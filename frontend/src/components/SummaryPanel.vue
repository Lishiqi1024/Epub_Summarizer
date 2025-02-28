<template>
  <el-card class="summary-card" style="height: 100%; display: flex; flex-direction: column;">
    <template #header>
      <div class="summary-header">
        <h3>AI 智能分析</h3>
        <p v-if="chapter">当前章节: {{ chapter.title }}</p>
      </div>
    </template>
    
    <div v-if="loading" class="summary-loading">
      <el-skeleton :rows="10" animated />
    </div>
    
    <div v-else-if="hasContent" class="summary-content">
      <tab-panel 
        :tabs="tabs" 
        :default-tab="0"
        @tab-change="handleTabChange"
      >
        <!-- 大纲标签页 -->
        <template #tab-0>
          <div v-if="summary" v-html="formattedSummary"></div>
          <div v-else class="tab-loading">
            <p>正在生成大纲...</p>
            <el-button size="small" @click="loadSummary">重试</el-button>
          </div>
        </template>
        
        <!-- 翻译标签页 -->
        <template #tab-1>
          <div v-if="translation" v-html="formattedTranslation"></div>
          <div v-else class="tab-loading">
            <p>正在生成翻译...</p>
            <el-button size="small" @click="loadTranslation">{{ translationLoading ? '加载中...' : '生成翻译' }}</el-button>
          </div>
        </template>
        
        <!-- 图表标签页 -->
        <template #tab-2>
          <div v-if="diagram" class="diagram-container">
            <div ref="mermaidContainer" class="mermaid-diagram"></div>
          </div>
          <div v-else class="tab-loading">
            <p>正在生成图表...</p>
            <el-button size="small" @click="loadDiagram">{{ diagramLoading ? '加载中...' : '生成图表' }}</el-button>
          </div>
        </template>
      </tab-panel>
    </div>
    
    <div v-else class="summary-empty">
      <p>无法加载章节分析，请重试</p>
      <el-button @click="$emit('refresh')">重新加载</el-button>
    </div>
  </el-card>
</template>

<script>
import TabPanel from './TabPanel.vue'
import apiService from '../services/api.service'
import mermaid from 'mermaid'
import { marked } from 'marked'

export default {
  name: 'SummaryPanel',
  components: {
    TabPanel
  },
  props: {
    chapter: Object,
    loading: Boolean,
    summary: String
  },
  data() {
    return {
      tabs: [
        { label: '大纲' },
        { label: '翻译' },
        { label: '图表' }
      ],
      activeTab: 0,
      translation: null,
      diagram: null,
      translationLoading: false,
      diagramLoading: false
    }
  },
  computed: {
    formattedSummary() {
      if (!this.summary) return '';
      return marked(this.summary);
    },
    formattedTranslation() {
      if (!this.translation) return '';
      return marked(this.translation);
    },
    hasContent() {
      return this.summary || this.translation || this.diagram;
    }
  },
  watch: {
    chapter() {
      // 当章节变化时，重置翻译和图表
      this.translation = null;
      this.diagram = null;
    }
  },
  methods: {
    handleTabChange(index) {
      this.activeTab = index;
      
      // 根据选中的标签页加载相应内容
      if (index === 1 && !this.translation && !this.translationLoading) {
        this.loadTranslation();
      } else if (index === 2 && !this.diagram && !this.diagramLoading) {
        this.loadDiagram();
      }
    },
    async loadSummary() {
      this.$emit('refresh');
    },
    async loadTranslation() {
      if (!this.chapter || this.translationLoading) return;
      
      this.translationLoading = true;
      
      try {
        const response = await apiService.translateChapter(this.chapter.id);
        this.translation = response.data.translation;
        
        // 如果翻译为空或太短，显示错误消息
        if (!this.translation || this.translation.length < 10) {
          this.$message.warning('翻译内容不足，可能是章节内容提取失败');
        }
      } catch (error) {
        console.error('Error loading translation:', error);
        this.$message.error('加载章节翻译失败: ' + (error.response?.data?.error || '未知错误'));
      } finally {
        this.translationLoading = false;
      }
    },
    async loadDiagram() {
      if (!this.chapter || this.diagramLoading) return;
      
      this.diagramLoading = true;
      
      try {
        const response = await apiService.getChapterDiagram(this.chapter.id);
        this.diagram = response.data.diagram;
        
        // 如果图表为空或太短，显示错误消息
        if (!this.diagram || this.diagram.length < 10) {
          this.$message.warning('图表内容不足，可能是章节内容提取失败');
        } else {
          // 渲染 Mermaid 图表
          this.$nextTick(() => {
            this.renderMermaid();
          });
        }
      } catch (error) {
        console.error('Error loading diagram:', error);
        this.$message.error('加载章节图表失败: ' + (error.response?.data?.error || '未知错误'));
      } finally {
        this.diagramLoading = false;
      }
    },
    renderMermaid() {
      if (!this.diagram || !this.$refs.mermaidContainer) return;
      
      try {
        // 初始化 Mermaid
        mermaid.initialize({
          startOnLoad: true,
          theme: 'default',
          securityLevel: 'loose'
        });
        
        // 清空容器
        this.$refs.mermaidContainer.innerHTML = '';
        
        // 创建一个新的 div 元素
        const div = document.createElement('div');
        div.className = 'mermaid';
        div.textContent = this.diagram;
        
        // 将 div 添加到容器中
        this.$refs.mermaidContainer.appendChild(div);
        
        // 渲染图表
        mermaid.init(undefined, '.mermaid');
      } catch (error) {
        console.error('Error rendering Mermaid diagram:', error);
        this.$refs.mermaidContainer.innerHTML = `
          <div class="diagram-error">
            <p>图表渲染失败</p>
            <pre>${this.diagram}</pre>
          </div>
        `;
      }
    }
  }
}
</script>

<style>
.summary-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.summary-header {
  text-align: center;
  margin-bottom: 10px;
}

.summary-header h3 {
  margin: 0;
  font-size: 18px;
  color: #409EFF;
}

.summary-header p {
  margin: 5px 0 0;
  font-size: 14px;
  color: #606266;
}

.summary-loading {
  padding: 20px;
}

.summary-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 15px;
  height: calc(100vh - 250px);
}

.summary-content :deep(h1),
.summary-content :deep(h2),
.summary-content :deep(h3),
.summary-content :deep(h4),
.summary-content :deep(h5),
.summary-content :deep(h6) {
  margin-top: 1em;
  margin-bottom: 0.5em;
  color: #303133;
}

.summary-content :deep(p) {
  margin: 0.5em 0;
  line-height: 1.6;
  color: #606266;
}

.summary-content :deep(ul),
.summary-content :deep(ol) {
  padding-left: 20px;
  margin: 0.5em 0;
}

.summary-content :deep(li) {
  margin: 0.3em 0;
  color: #606266;
}

.tab-loading {
  text-align: center;
  padding: 20px;
  color: #909399;
}

.diagram-container {
  padding: 15px;
  text-align: center;
}

@media (max-width: 768px) {
  .summary-content {
    height: auto;
    max-height: 50vh;
  }
}
</style>