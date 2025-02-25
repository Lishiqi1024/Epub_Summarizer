<template>
  <div class="tab-panel">
    <div class="tab-header">
      <div 
        v-for="(tab, index) in tabs" 
        :key="index"
        :class="['tab-item', { active: activeTab === index }]"
        @click="setActiveTab(index)"
      >
        {{ tab.label }}
      </div>
    </div>
    
    <div class="tab-content">
      <slot :name="'tab-' + activeTab"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TabPanel',
  props: {
    tabs: {
      type: Array,
      required: true
    },
    defaultTab: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      activeTab: this.defaultTab
    }
  },
  methods: {
    setActiveTab(index) {
      this.activeTab = index
      this.$emit('tab-change', index)
    }
  }
}
</script>

<style scoped>
.tab-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.tab-header {
  display: flex;
  border-bottom: 1px solid #dcdfe6;
  margin-bottom: 15px;
}

.tab-item {
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.tab-item:hover {
  color: #409eff;
}

.tab-item.active {
  color: #409eff;
  border-bottom-color: #409eff;
}

.tab-content {
  flex: 1;
  overflow-y: auto;
}
</style> 