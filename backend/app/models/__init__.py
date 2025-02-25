import pymysql
from flask import g, current_app

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=current_app.config['DB_HOST'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            database=current_app.config['DB_NAME'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS,
            max_allowed_packet=67108864  # 64MB
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    app.teardown_appcontext(close_db)
    
    # 创建必要的表
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # 删除并重新创建books表
        cursor.execute('DROP TABLE IF EXISTS bookmarks')
        cursor.execute('DROP TABLE IF EXISTS chapters')
        cursor.execute('DROP TABLE IF EXISTS books')
        
        # 创建books表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            author VARCHAR(255),
            cover_path VARCHAR(255),
            file_path VARCHAR(255) NOT NULL,
            last_read DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建chapters表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chapters (
            id INT AUTO_INCREMENT PRIMARY KEY,
            book_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            href VARCHAR(255) NOT NULL,
            order_num INT NOT NULL,
            summary TEXT,
            translation TEXT,
            mermaid_diagram TEXT,
            html_content LONGTEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
        )
        ''')
        
        # 创建bookmarks表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            book_id INT NOT NULL,
            chapter_id INT NOT NULL,
            cfi VARCHAR(255) NOT NULL,
            text VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
            FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
        )
        ''')
        
        db.commit()