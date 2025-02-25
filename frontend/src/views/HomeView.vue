<template>
  <div class="home-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <h1>欢迎使用 EPUB 在线总结分析工具</h1>
          <p>上传您的EPUB电子书，使用AI智能技术快速获取内容总结</p>
          
          <div class="action-buttons">
            <el-button type="primary" size="large" @click="showUploadDialog">
              上传新书籍
            </el-button>
            <el-button type="success" size="large" @click="showBookshelf">
              我的书架
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <BookShelf ref="bookshelf" v-if="showShelf" @book-selected="openBook" />
    
    <el-dialog
      title="上传EPUB电子书"
      v-model="uploadDialogVisible"
      width="30%"
    >
      <UploadBook @upload-success="handleUploadSuccess" />
    </el-dialog>
  </div>
</template>

<script>
import BookShelf from '../components/BookShelf.vue'
import UploadBook from '../components/UploadBook.vue'

export default {
  name: 'HomeView',
  components: {
    BookShelf,
    UploadBook
  },
  data() {
    return {
      uploadDialogVisible: false,
      showShelf: false
    }
  },
  methods: {
    showUploadDialog() {
      this.uploadDialogVisible = true
    },
    showBookshelf() {
      this.showShelf = true
      // 如果书架组件已加载，则刷新数据
      if (this.$refs.bookshelf) {
        this.$refs.bookshelf.loadBooks()
      }
    },
    handleUploadSuccess(book) {
      this.uploadDialogVisible = false
      this.showShelf = true
      
      // 如果书架组件已加载，则刷新数据
      if (this.$refs.bookshelf) {
        this.$refs.bookshelf.loadBooks()
      }
      
      // 显示成功消息
      this.$message({
        message: `《${book.title}》上传成功！`,
        type: 'success'
      })
    },
    openBook(bookId) {
      this.$router.push({ name: 'reader', params: { bookId } })
    }
  }
}
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  text-align: center;
  padding: 40px 20px;
  margin-bottom: 30px;
}

.welcome-card h1 {
  font-size: 2rem;
  margin-bottom: 20px;
  color: #303133;
}

.welcome-card p {
  font-size: 1.2rem;
  color: #606266;
  margin-bottom: 30px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
}
</style> 