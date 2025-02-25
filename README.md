# EPUB 在线总结分析工具

一个基于Vue.js和Flask的在线EPUB电子书阅读和AI智能总结工具。本工具能够帮助用户快速理解电子书内容，通过火山方舟DeepSeek R1 API将文章内容转换为易于理解的总结。

## 功能特点

- 支持EPUB格式电子书上传和解析
- 自动提取电子书章节内容和元数据
- 基于火山方舟DeepSeek R1 API的智能内容总结
- 清晰的三栏布局设计，左侧章节列表，中间阅读，右侧总结
- 实时章节内容预览和总结生成
- 个性化书架管理功能
- 优雅的UI设计和流畅的用户体验
- 支持大文本分块处理和流式输出
- 阅读进度保存和恢复
- 书签功能
- 主题切换和字体大小调整

## 技术栈

### 前端
- Vue.js 3
- Element Plus UI库
- epub.js (EPUB渲染)
- Axios (HTTP请求)
- Vue Router

### 后端
- Flask (Python Web框架)
- MySQL数据库
- Beautiful Soup (HTML解析)
- 火山方舟DeepSeek R1 API (AI内容总结)

## 项目结构

```
├── backend/                # 后端Flask应用
│   ├── app/                # 应用代码
│   │   ├── models/         # 数据库模型
│   │   ├── routes/         # API路由
│   │   ├── services/       # 业务逻辑服务
│   │   └── utils/          # 工具函数
│   ├── uploads/            # 上传文件存储
│   │   ├── books/          # EPUB文件
│   │   └── covers/         # 封面图片
│   ├── config.py           # 配置文件
│   └── run.py              # 应用入口
│
└── frontend/               # 前端Vue应用
    ├── public/             # 静态资源
    └── src/                # 源代码
        ├── assets/         # 资源文件
        ├── components/     # Vue组件
        ├── services/       # API服务
        ├── views/          # 页面视图
        ├── App.vue         # 根组件
        └── main.js         # 入口文件
```

## 使用指南

### 安装和运行

#### 后端

1. 安装Python依赖：
```bash
cd backend
pip install -r requirements.txt
```

2. 配置数据库：
   - 确保MySQL服务已启动
   - 创建数据库：`CREATE DATABASE epub_summarizer;`
   - 修改`config.py`中的数据库连接信息

3. 运行后端服务：
```bash
python run.py
```

#### 前端

1. 安装Node.js依赖：
```bash
cd frontend
npm install
```

2. 运行开发服务器：
```bash
npm run dev
```

3. 构建生产版本：
```bash
npm run build
```

### 使用流程

1. 访问应用首页（默认为 http://localhost:5173）
2. 点击"上传新书籍"按钮上传EPUB文件，或点击"我的书架"查看已上传书籍
3. 在阅读界面，左侧显示章节列表，中间是阅读区域，右侧是AI总结
4. 点击章节可以切换阅读内容，右侧会自动生成对应章节的AI总结
5. 使用阅读控制按钮调整字体大小、主题，添加书签等

## 优化计划

### 已实现优化
- 阅读进度保存功能：使用localStorage存储每本书的阅读位置
- 书签功能：支持添加、查看和删除书签
- 主题切换：支持浅色、深色和护眼模式
- 字体大小调整：提供多种字体大小选项

### 待实现优化
- 离线阅读功能
- 用户账户系统和数据同步
- 批注和高亮功能
- 搜索功能
- 性能优化：预加载机制和内存管理

## 贡献指南

欢迎贡献代码或提出建议！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件 