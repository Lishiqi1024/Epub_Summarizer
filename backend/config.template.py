import os

class Config:
    # 基本配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    
    # 数据库配置
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_USER = os.environ.get('DB_USER') or 'your_username'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'your_password'
    DB_NAME = os.environ.get('DB_NAME') or 'your_database'
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    COVER_FOLDER = os.path.join(UPLOAD_FOLDER, 'covers')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    
    # AI API配置
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY') or 'your-api-key'
    DEEPSEEK_BASE_URL = os.environ.get('DEEPSEEK_BASE_URL') or 'https://api.example.com/v1/chat/completions'
    DEEPSEEK_MODEL = os.environ.get('DEEPSEEK_MODEL') or 'model-name'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}