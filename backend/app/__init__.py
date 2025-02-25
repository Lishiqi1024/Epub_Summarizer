from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import pymysql
import traceback
from config import config
import os

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 启用CORS以解决跨域问题，允许所有头部
    CORS(app, resources={r"/api/*": {"origins": "*", "supports_credentials": True, "expose_headers": "*"}})
    
    # 初始化数据库连接
    from app.models import init_db
    init_db(app)
    
    # 注册路由
    from app.routes.book_routes import book_bp
    from app.routes.ai_routes import ai_bp
    
    app.register_blueprint(book_bp, url_prefix='/api/books')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    
    # 添加根路由
    @app.route('/')
    def index():
        # 检查是否存在静态文件
        static_index = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(static_index):
            return send_from_directory(app.static_folder, 'index.html')
        else:
            return jsonify({
                "status": "ok",
                "message": "EPUB Analyzer API is running",
                "endpoints": {
                    "books": "/api/books/",
                    "upload": "/api/books/upload",
                    "ai": "/api/ai/"
                }
            })
    
    # 静态文件服务
    @app.route('/static/<path:path>')
    def serve_static(path):
        return send_from_directory('static', path)
    
    # 处理CORS预检请求
    @app.route('/', methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def options_handler(path=None):
        return '', 200
    
    # 添加404错误处理
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "error": "Not Found",
            "message": "The requested URL was not found on the server.",
            "available_endpoints": {
                "books": "/api/books/",
                "upload": "/api/books/upload",
                "ai": "/api/ai/"
            }
        }), 404
    
    # 添加全局错误处理
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled exception: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            "error": "服务器内部错误",
            "message": str(e)
        }), 500
    
    return app 