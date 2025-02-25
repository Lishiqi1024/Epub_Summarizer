<template>
  <div class="upload-container">
    <el-upload
      class="upload-dragger"
      drag
      action="#"
      :auto-upload="false"
      :on-change="handleFileChange"
      :file-list="fileList"
      accept=".epub"
    >
      <i class="el-icon-upload"></i>
      <div class="el-upload__text">
        拖拽EPUB文件到此处，或 <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          只支持EPUB格式的电子书文件
        </div>
      </template>
    </el-upload>
    
    <div class="upload-actions">
      <el-button type="primary" @click="uploadFile" :loading="uploading" :disabled="!file">
        上传
      </el-button>
    </div>
    
    <div v-if="uploadProgress > 0 && uploadProgress < 100" class="upload-progress">
      <el-progress :percentage="uploadProgress" />
    </div>
  </div>
</template>

<script>
import apiService from '../services/api.service'

export default {
  name: 'UploadBook',
  emits: ['upload-success'],
  data() {
    return {
      file: null,
      fileList: [],
      uploading: false,
      uploadProgress: 0
    }
  },
  methods: {
    handleFileChange(file) {
      this.fileList = [file]
      this.file = file.raw
    },
    async uploadFile() {
      if (!this.file) {
        this.$message.warning('请先选择文件')
        return
      }
      
      if (!this.file.name.toLowerCase().endsWith('.epub')) {
        this.$message.error('只支持EPUB格式的电子书文件')
        return
      }
      
      this.uploading = true
      this.uploadProgress = 0
      
      try {
        const response = await apiService.uploadBook(this.file)
        
        this.$emit('upload-success', response.data)
        
        // 清空文件
        this.file = null
        this.fileList = []
        this.uploadProgress = 100
        
        setTimeout(() => {
          this.uploadProgress = 0
        }, 1000)
      } catch (error) {
        console.error('Error uploading book:', error)
        this.$message.error('上传失败，请重试')
      } finally {
        this.uploading = false
      }
    }
  }
}
</script>

<style scoped>
.upload-container {
  padding: 20px 0;
}

.upload-dragger {
  width: 100%;
}

.upload-actions {
  margin-top: 20px;
  text-align: center;
}

.upload-progress {
  margin-top: 20px;
}
</style> 