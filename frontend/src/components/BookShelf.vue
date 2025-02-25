<template>
  <div class="bookshelf-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="bookshelf-header">
          <h2>我的书架</h2>
          <el-button type="primary" @click="$emit('upload-book')">上传新书</el-button>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="book-list">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="book in books" :key="book.id" class="book-item">
        <el-card :body-style="{ padding: '0px' }" shadow="hover">
          <div class="book-cover" @click="selectBook(book.id)">
            <img v-if="book.cover_url" :src="book.cover_url" :alt="book.title" />
            <div v-else class="no-cover">
              <span>{{ book.title }}</span>
            </div>
          </div>
          <div class="book-info">
            <h3 class="book-title" :title="book.title">{{ book.title }}</h3>
            <p class="book-author" v-if="book.author">{{ book.author }}</p>
            
            <div class="book-actions">
              <el-button type="primary" size="small" @click="selectBook(book.id)">阅读</el-button>
              <el-button type="danger" size="small" @click="confirmDelete(book)">删除</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 空状态 -->
      <el-col :span="24" v-if="books.length === 0 && !loading">
        <el-empty description="您的书架还没有书籍" />
      </el-col>
      
      <!-- 加载状态 -->
      <el-col :span="24" v-if="loading">
        <div class="loading-container">
          <el-skeleton :rows="3" animated />
        </div>
      </el-col>
    </el-row>
    
    <!-- 删除确认对话框 -->
    <el-dialog
      title="确认删除"
      v-model="deleteDialogVisible"
      width="30%"
    >
      <p>确定要删除《{{ bookToDelete?.title }}》吗？此操作不可恢复。</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="deleteBook">确定删除</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import apiService from '../services/api.service'

export default {
  name: 'BookShelf',
  emits: ['book-selected', 'upload-book'],
  data() {
    return {
      books: [],
      loading: true,
      deleteDialogVisible: false,
      bookToDelete: null
    }
  },
  mounted() {
    this.loadBooks()
  },
  methods: {
    async loadBooks() {
      this.loading = true
      
      try {
        const response = await apiService.getBooks()
        this.books = response.data
      } catch (error) {
        console.error('Error loading books:', error)
        this.$message.error('加载书籍失败，请重试')
      } finally {
        this.loading = false
      }
    },
    selectBook(bookId) {
      this.$emit('book-selected', bookId)
    },
    confirmDelete(book) {
      this.bookToDelete = book
      this.deleteDialogVisible = true
    },
    async deleteBook() {
      if (!this.bookToDelete) return
      
      try {
        await apiService.deleteBook(this.bookToDelete.id)
        
        // 从列表中移除
        this.books = this.books.filter(book => book.id !== this.bookToDelete.id)
        
        this.$message.success(`《${this.bookToDelete.title}》已删除`)
      } catch (error) {
        console.error('Error deleting book:', error)
        this.$message.error('删除书籍失败，请重试')
      } finally {
        this.deleteDialogVisible = false
        this.bookToDelete = null
      }
    }
  }
}
</script>

<style scoped>
.bookshelf-container {
  margin-top: 30px;
}

.bookshelf-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.bookshelf-header h2 {
  margin: 0;
}

.book-list {
  margin-top: 20px;
}

.book-item {
  margin-bottom: 20px;
}

.book-cover {
  height: 200px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background-color: #f5f7fa;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-cover {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e6e8eb;
  color: #606266;
  text-align: center;
  padding: 10px;
}

.book-info {
  padding: 14px;
}

.book-title {
  margin: 0;
  font-size: 16px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-author {
  color: #909399;
  font-size: 14px;
  margin: 5px 0 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.loading-container {
  padding: 20px;
}
</style> 