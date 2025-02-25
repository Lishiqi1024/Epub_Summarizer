<template>
  <el-card class="summary-card">
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
      return this.summary.replace(/\n/g, '<br>');
    },
    formattedTranslation() {
      if (!this.translation) return '';
      return this.translation.replace(/\n/g, '<br>');
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

<style scoped>
.summary-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-header h3 {
  margin: 0;
}

.summary-header p {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.summary-loading {
  padding: 20px;
}

.summary-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 10px;
}

.summary-empty {
  text-align: center;
  padding: 20px;
  color: #909399;
}

.tab-loading {
  text-align: center;
  padding: 20px;
  color: #909399;
}

.diagram-container {
  padding: 10px;
}

.mermaid-diagram {
  width: 100%;
  overflow-x: auto;
}

.diagram-error {
  padding: 10px;
  background-color: #fef0f0;
  border-radius: 4px;
  color: #f56c6c;
}

.diagram-error pre {
  margin-top: 10px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
}
</style> 