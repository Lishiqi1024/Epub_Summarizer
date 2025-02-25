<template>
  <div class="reader-container">
    <el-row :gutter="20" class="reader-layout">
      <!-- 左侧面板：章节列表 -->
      <el-col :span="6" class="toc-panel">
        <el-card class="toc-card">
          <template #header>
            <div class="toc-header">
              <h3>{{ book.title }}</h3>
              <p v-if="book.author">作者: {{ book.author }}</p>
            </div>
          </template>
          
          <el-menu
            :default-active="activeChapter ? activeChapter.id.toString() : ''"
            class="chapter-list"
          >
            <el-menu-item
              v-for="chapter in book.chapters"
              :key="chapter.id"
              :index="chapter.id.toString()"
              @click="loadChapter(chapter)"
            >
              {{ chapter.title }}
            </el-menu-item>
          </el-menu>
          
          <div class="reader-controls">
            <el-button-group>
              <el-button @click="prevChapter">上一章</el-button>
              <el-button @click="nextChapter">下一章</el-button>
            </el-button-group>
            
            <div class="reader-settings">
              <el-dropdown @command="setFontSize">
                <el-button>
                  字体大小<i class="el-icon-arrow-down el-icon--right"></i>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="small">小</el-dropdown-item>
                    <el-dropdown-item command="medium">中</el-dropdown-item>
                    <el-dropdown-item command="large">大</el-dropdown-item>
                    <el-dropdown-item command="xlarge">超大</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              
              <el-dropdown @command="setTheme">
                <el-button>
                  主题<i class="el-icon-arrow-down el-icon--right"></i>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="light">浅色</el-dropdown-item>
                    <el-dropdown-item command="dark">深色</el-dropdown-item>
                    <el-dropdown-item command="sepia">护眼</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 中间面板：阅读器 -->
      <el-col :span="10" class="reader-panel">
        <el-card class="reader-card">
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="15" animated />
          </div>
          <div v-else class="chapter-content" :class="currentTheme">
            <div v-html="chapterHtml" class="content-html"></div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧面板：AI总结 -->
      <el-col :span="8" class="summary-panel">
        <SummaryPanel
          :chapter="activeChapter"
          :loading="summaryLoading"
          :summary="summary"
        />
      </el-col>
    </el-row>
  </div>
</template>

<script>
import apiService from '../services/api.service'
import SummaryPanel from '../components/SummaryPanel.vue'

export default {
  name: 'ReaderView',
  components: {
    SummaryPanel
  },
  props: {
    bookId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      book: {
        id: null,
        title: '加载中...',
        author: '',
        chapters: []
      },
      activeChapter: null,
      chapterHtml: '',
      summary: '',
      summaryLoading: false,
      loading: false,
      currentFontSize: localStorage.getItem('reader_font_size') || 'medium',
      currentTheme: localStorage.getItem('reader_theme') || 'light'
    }
  },
  mounted() {
    this.loadBook()
  },
  methods: {
    async loadBook() {
      try {
        this.loading = true
        const response = await apiService.getBook(this.bookId)
        this.book = response.data
        
        // 更新最后阅读时间
        apiService.updateLastRead(this.book.id)
        
        // 如果有章节，加载第一章
        if (this.book.chapters && this.book.chapters.length > 0) {
          // 获取上次阅读的章节
          const lastChapterId = localStorage.getItem(`book_${this.book.id}_last_chapter`)
          
          if (lastChapterId) {
            const chapter = this.book.chapters.find(c => c.id.toString() === lastChapterId)
            if (chapter) {
              this.loadChapter(chapter)
              return
            }
          }
          
          // 如果没有上次阅读记录，加载第一章
          this.loadChapter(this.book.chapters[0])
        }
      } catch (error) {
        console.error('Error loading book:', error)
        this.$message.error('加载书籍失败，请重试')
      } finally {
        this.loading = false
      }
    },
    
    async loadChapter(chapter) {
      try {
        this.loading = true
        console.log('Loading chapter:', chapter)
        this.activeChapter = chapter
        
        // 保存当前阅读章节
        localStorage.setItem(`book_${this.book.id}_last_chapter`, chapter.id)
        
        // 获取章节内容
        const response = await apiService.getChapterContent(this.book.id, chapter.id)
        this.chapterHtml = response.data
        
        // 更新最后阅读时间
        apiService.updateLastRead(this.book.id)
        
        // 加载章节总结
        this.loadSummary()
        
        // 滚动到顶部
        setTimeout(() => {
          const contentElement = document.querySelector('.chapter-content')
          if (contentElement) {
            contentElement.scrollTop = 0
          }
        }, 100)
      } catch (error) {
        console.error('Error loading chapter:', error)
        this.$message.error('加载章节失败: ' + (error.message || '未知错误'))
      } finally {
        this.loading = false
      }
    },
    
    async loadSummary() {
      if (!this.activeChapter) return;
      
      this.summaryLoading = true;
      
      try {
        const response = await apiService.summarizeChapter(this.activeChapter.id);
        this.summary = response.data.summary;
        
        // 如果总结为空或太短，显示错误消息
        if (!this.summary || this.summary.length < 10) {
          console.warn('Summary is empty or too short:', this.summary);
          this.$message.warning('章节总结内容不足，可能是章节内容提取失败');
        }
      } catch (error) {
        console.error('Error loading summary:', error);
        this.$message.error('加载章节总结失败: ' + (error.response?.data?.error || '未知错误'));
        this.summary = null;
      } finally {
        this.summaryLoading = false;
      }
    },
    
    prevChapter() {
      if (!this.activeChapter) return
      
      const currentIndex = this.book.chapters.findIndex(c => c.id === this.activeChapter.id)
      if (currentIndex > 0) {
        this.loadChapter(this.book.chapters[currentIndex - 1])
      } else {
        this.$message.info('已经是第一章')
      }
    },
    
    nextChapter() {
      if (!this.activeChapter) return
      
      const currentIndex = this.book.chapters.findIndex(c => c.id === this.activeChapter.id)
      if (currentIndex < this.book.chapters.length - 1) {
        this.loadChapter(this.book.chapters[currentIndex + 1])
      } else {
        this.$message.info('已经是最后一章')
      }
    },
    
    setFontSize(size) {
      this.currentFontSize = size
      localStorage.setItem('reader_font_size', size)
    },
    
    setTheme(theme) {
      this.currentTheme = theme
      localStorage.setItem('reader_theme', theme)
    }
  }
}
</script>

<style>
.reader-container {
  max-width: 1600px;
  margin: 0 auto;
}

.reader-layout {
  display: flex;
  min-height: calc(100vh - 180px);
}

.toc-panel {
  height: 100%;
}

.toc-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.toc-header {
  text-align: center;
}

.toc-header h3 {
  margin-bottom: 5px;
}

.chapter-list {
  flex: 1;
  overflow-y: auto;
  max-height: 300px;
}

.reader-controls {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.reader-settings {
  display: flex;
  gap: 10px;
  margin: 10px 0;
}

.reader-panel {
  height: 100%;
}

.reader-card {
  height: 100%;
}

.chapter-content {
  width: 100%;
  height: 600px;
  overflow-y: auto;
  padding: 20px;
}

.content-html {
  max-width: 800px;
  margin: 0 auto;
}

/* 字体大小 */
.chapter-content.small {
  font-size: 14px;
}

.chapter-content.medium {
  font-size: 16px;
}

.chapter-content.large {
  font-size: 18px;
}

.chapter-content.xlarge {
  font-size: 20px;
}

/* 主题 */
.chapter-content.light {
  background-color: #fff;
  color: #333;
}

.chapter-content.dark {
  background-color: #333;
  color: #eee;
}

.chapter-content.dark a {
  color: #58a6ff;
}

.chapter-content.sepia {
  background-color: #f8f1e3;
  color: #5b4636;
}

.loading-container {
  padding: 20px;
}

@media (max-width: 768px) {
  .reader-layout {
    flex-direction: column;
  }
  
  .toc-panel, .reader-panel, .summary-panel {
    width: 100%;
    margin-bottom: 20px;
  }
  
  .chapter-content {
    height: 400px;
  }
}
</style>