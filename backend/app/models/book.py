from app.models import get_db

class Book:
    @staticmethod
    def create(title, author, cover_path, file_path):
        db = get_db()
        cursor = db.cursor()
        
        sql = '''
        INSERT INTO books (title, author, cover_path, file_path)
        VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(sql, (title, author, cover_path, file_path))
        book_id = cursor.lastrowid
        db.commit()
        
        return book_id
    
    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor()
        
        sql = '''
        SELECT * FROM books ORDER BY last_read DESC
        '''
        cursor.execute(sql)
        
        return cursor.fetchall()
    
    @staticmethod
    def get_by_id(book_id):
        db = get_db()
        cursor = db.cursor()
        
        sql = '''
        SELECT * FROM books WHERE id = %s
        '''
        cursor.execute(sql, (book_id,))
        
        return cursor.fetchone()
    
    @staticmethod
    def update_last_read(book_id):
        db = get_db()
        cursor = db.cursor()
        
        sql = '''
        UPDATE books SET last_read = NOW() WHERE id = %s
        '''
        cursor.execute(sql, (book_id,))
        db.commit()
    
    @staticmethod
    def delete(book_id):
        db = get_db()
        cursor = db.cursor()
        
        sql = '''
        DELETE FROM books WHERE id = %s
        '''
        cursor.execute(sql, (book_id,))
        db.commit()
        
        return cursor.rowcount > 0

class Chapter:
    @staticmethod
    def create_many(book_id, chapters):
        """批量创建章节"""
        db = get_db()
        cursor = db.cursor()
        
        chapter_ids = []
        
        for i, chapter in enumerate(chapters):
            sql = '''
            INSERT INTO chapters (book_id, title, href, order_num)
            VALUES (%s, %s, %s, %s)
            '''
            cursor.execute(sql, (book_id, chapter['title'], chapter['href'], i))
            chapter_ids.append(cursor.lastrowid)
        
        db.commit()
        
        return chapter_ids
    
    @staticmethod
    def get_by_book_id(book_id):
        db = get_db()
        cursor = db.cursor()
        
        sql = '''
        SELECT * FROM chapters WHERE book_id = %s ORDER BY order_num
        '''
        cursor.execute(sql, (book_id,))
        
        return cursor.fetchall()
    
    @staticmethod
    def get_by_id(chapter_id):
        db = get_db()
        cursor = db.cursor()
        
        sql = '''
        SELECT * FROM chapters WHERE id = %s
        '''
        cursor.execute(sql, (chapter_id,))
        
        return cursor.fetchone()
    
    @staticmethod
    def update_summary(chapter_id, summary):
        """更新章节摘要"""
        db = get_db()
        cursor = db.cursor()
        
        sql = '''
        UPDATE chapters
        SET summary = %s
        WHERE id = %s
        '''
        cursor.execute(sql, (summary, chapter_id))
        db.commit()
        
        return cursor.rowcount > 0

    @staticmethod
    def update_translation(chapter_id, translation):
        """更新章节翻译"""
        db = get_db()
        cursor = db.cursor()
        
        sql = '''
        UPDATE chapters
        SET translation = %s
        WHERE id = %s
        '''
        cursor.execute(sql, (translation, chapter_id))
        db.commit()
        
        return cursor.rowcount > 0

    @staticmethod
    def update_mermaid_diagram(chapter_id, mermaid_diagram):
        """更新章节 Mermaid 图表"""
        db = get_db()
        cursor = db.cursor()
        
        sql = '''
        UPDATE chapters
        SET mermaid_diagram = %s
        WHERE id = %s
        '''
        cursor.execute(sql, (mermaid_diagram, chapter_id))
        db.commit()
        
        return cursor.rowcount > 0

    @staticmethod
    def update_html_content(chapter_id, html_content):
        """更新章节的HTML内容"""
        db = get_db()
        cursor = db.cursor()
        
        try:
            sql = '''
            UPDATE chapters SET html_content = %s WHERE id = %s
            '''
            cursor.execute(sql, (html_content, chapter_id))
            db.commit()
            
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating HTML content: {str(e)}")
            # 如果内容太大，尝试截断
            if len(html_content) > 65535:  # MySQL TEXT类型的最大长度
                truncated_content = html_content[:65000] + "... (内容已截断)"
                try:
                    cursor.execute(sql, (truncated_content, chapter_id))
                    db.commit()
                    return True
                except Exception as e2:
                    print(f"Error updating truncated HTML content: {str(e2)}")
                    return False
            return False

class Bookmark:
    @staticmethod
    def create(book_id, chapter_id, cfi, text):
        db = get_db()
        cursor = db.cursor()
        
        sql = '''
        INSERT INTO bookmarks (book_id, chapter_id, cfi, text)
        VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(sql, (book_id, chapter_id, cfi, text))
        db.commit()
        
        return cursor.lastrowid
    
    @staticmethod
    def get_by_book_id(book_id):
        db = get_db()
        cursor = db.cursor()
        
        sql = '''
        SELECT * FROM bookmarks WHERE book_id = %s ORDER BY created_at DESC
        '''
        cursor.execute(sql, (book_id,))
        
        return cursor.fetchall()
    
    @staticmethod
    def delete(bookmark_id):
        db = get_db()
        cursor = db.cursor()
        
        sql = '''
        DELETE FROM bookmarks WHERE id = %s
        '''
        cursor.execute(sql, (bookmark_id,))
        db.commit()
        
        return cursor.rowcount > 0 