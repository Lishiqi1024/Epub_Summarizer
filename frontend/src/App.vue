<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="logo">
        <router-link to="/">EPUB 在线总结分析工具</router-link>
      </div>
      <div class="nav-links">
        <router-link to="/">首页</router-link>
      </div>
    </el-header>
    
    <el-main class="app-main">
      <router-view />
    </el-main>
    
    <el-footer class="app-footer">
      <p>EPUB 在线总结分析工具 &copy; 2023</p>
    </el-footer>
  </el-container>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background-color: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.logo a {
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
  text-decoration: none;
}

.nav-links a {
  color: white;
  margin-left: 20px;
  text-decoration: none;
}

.app-main {
  flex: 1;
  padding: 20px;
}

.app-footer {
  background-color: #f5f7fa;
  text-align: center;
  color: #606266;
  padding: 10px 0;
}
</style> 