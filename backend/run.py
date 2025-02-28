from app import create_app
import os

app = create_app('development')

# 确保上传文件夹存在
with app.app_context():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['COVER_FOLDER'], exist_ok=True)
    temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp')
    os.makedirs(temp_dir, exist_ok=True)

if __name__ == '__main__':
    print(f"Starting Flask app on http://localhost:5002")
    app.run(host='0.0.0.0', port=5002)