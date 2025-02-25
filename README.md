# EPUB阅读器和摘要生成器

## 项目配置说明

### 环境配置
1. 复制 `backend/config.template.py` 文件并重命名为 `config.py`
2. 根据实际情况修改配置文件中的环境变量

### 环境变量说明
项目支持通过环境变量配置以下参数，也可以直接在 `config.py` 中设置默认值：

#### 基本配置
- `SECRET_KEY`: Flask应用密钥

#### 数据库配置
- `DB_HOST`: MySQL数据库地址（默认：localhost）
- `DB_USER`: 数据库用户名
- `DB_PASSWORD`: 数据库密码
- `DB_NAME`: 数据库名称（默认：epub_summarizer）

#### AI API配置
- `DEEPSEEK_API_KEY`: DeepSeek API密钥
- `DEEPSEEK_BASE_URL`: DeepSeek API基础URL
- `DEEPSEEK_MODEL`: 使用的AI模型名称

### 文件上传配置
- 上传文件存储在 `backend/uploads` 目录下
- 封面图片存储在 `backend/uploads/covers` 目录下
- 最大上传文件大小限制为50MB

## 开发环境配置
1. 安装Python依赖：
```bash
cd backend
pip install -r requirements.txt
```

2. 配置MySQL数据库：
- 确保MySQL服务已启动
- 创建数据库：epub_summarizer
- 配置数据库连接信息（用户名、密码等）

3. 启动后端服务：
```bash
cd backend
python run.py
```

4. 安装前端依赖并启动：
```bash
cd frontend
npm install
npm run dev
```