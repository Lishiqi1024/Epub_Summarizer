import os
import traceback
from flask import Blueprint, request, jsonify, current_app, send_from_directory, send_file
from werkzeug.utils import secure_filename
import uuid
from app.models.book import Book, Chapter, Bookmark
from app.services.epub_service import EpubService
import zipfile

book_bp = Blueprint('book', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'epub'

@book_bp.route('/upload', methods=['POST'])
def upload_book():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # 创建唯一文件名
        filename = f"{uuid.uuid4()}.epub"
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        # 确保上传文件夹存在
        os.makedirs(upload_folder, exist_ok=True)
        os.makedirs(current_app.config['COVER_FOLDER'], exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        try:
            # 解析EPUB文件
            with EpubService(file_path) as epub:
                metadata = epub.get_metadata()  # 先获取元数据，这会设置 cover_path
                chapters = epub.get_chapters()
                
                # 打印完整的EPUB解析结果
                current_app.logger.info("=== EPUB文件解析结果 ===")
                current_app.logger.info(f"标题: {metadata.get('title', 'Unknown Title')}")
                current_app.logger.info(f"作者: {metadata.get('author', 'Unknown Author')}")
                current_app.logger.info(f"封面图片: {'已找到' if metadata.get('cover_path') else '未找到'}")
                current_app.logger.info(f"\n总章节数: {len(chapters)}")
                current_app.logger.info("章节列表:")
                for i, chapter in enumerate(chapters):
                    current_app.logger.info(f"第{i+1}章: {chapter['title']}")
                    current_app.logger.info(f"  链接: {chapter['href']}")
                current_app.logger.info("=== 解析结果结束 ===")
                
                # 保存封面图片
                cover_filename = epub.save_cover_image(current_app.config['COVER_FOLDER'])
                cover_path = cover_filename if cover_filename else None
                
                # 保存书籍信息到数据库
                book_id = Book.create(
                    title=metadata.get('title', 'Unknown Title'),
                    author=metadata.get('author', 'Unknown Author'),
                    cover_path=cover_path,
                    file_path=filename
                )
                
                # 保存章节信息
                chapter_ids = Chapter.create_many(book_id, chapters)
                
                # 保存章节HTML内容
                try:
                    for i, chapter_id in enumerate(chapter_ids):
                        try:
                            html_content = epub.get_chapter_html(chapters[i]['href'])
                            Chapter.update_html_content(chapter_id, html_content)
                        except Exception as e:
                            current_app.logger.error(f"Error saving HTML content for chapter {i+1}: {str(e)}")
                except Exception as e:
                    current_app.logger.error(f"Error in HTML content saving loop: {str(e)}")
                
                return jsonify({
                    'id': book_id,
                    'title': metadata.get('title'),
                    'author': metadata.get('author'),
                    'cover': cover_path,
                    'chapters': len(chapters)
                }), 201
                
        except Exception as e:
            # 如果处理失败，删除上传的文件
            if os.path.exists(file_path):
                os.remove(file_path)
            current_app.logger.error(f"Error processing EPUB file: {str(e)}")
            current_app.logger.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file format. Only EPUB files are allowed.'}), 400

@book_bp.route('/', methods=['GET'])
def get_books():
    books = Book.get_all()
    
    # 添加封面URL
    for book in books:
        if book['cover_path']:
            book['cover_url'] = f"/api/books/covers/{book['cover_path']}"
        else:
            book['cover_url'] = None
    
    return jsonify(books)

@book_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.get_by_id(book_id)
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    # 更新最后阅读时间
    Book.update_last_read(book_id)
    
    # 获取章节信息
    chapters = Chapter.get_by_book_id(book_id)
    
    # 添加封面URL
    if book['cover_path']:
        book['cover_url'] = f"/api/books/covers/{book['cover_path']}"
    else:
        book['cover_url'] = None
    
    book['chapters'] = chapters
    
    return jsonify(book)

@book_bp.route('/<int:book_id>/last-read', methods=['PUT'])
def update_last_read(book_id):
    # 验证书籍存在
    book = Book.get_by_id(book_id)
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    # 更新最后阅读时间
    Book.update_last_read(book_id)
    
    return jsonify({'message': 'Last read time updated successfully'})

@book_bp.route('/<int:book_id>/chapters/<int:chapter_id>', methods=['GET'])
def get_chapter(book_id, chapter_id):
    # 验证书籍存在
    book = Book.get_by_id(book_id)
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    # 验证章节存在
    chapter = Chapter.get_by_id(chapter_id)
    
    if not chapter or chapter['book_id'] != book_id:
        return jsonify({'error': 'Chapter not found'}), 404
    
    # 返回章节信息
    return jsonify({
        'id': chapter['id'],
        'title': chapter['title'],
        'href': chapter['href'],
        'summary': chapter['summary']
    })

@book_bp.route('/temp/<filename>', methods=['GET'])
def get_temp_file(filename):
    temp_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp')
    return send_from_directory(temp_dir, filename)

@book_bp.route('/covers/<path:filename>')
def get_cover(filename):
    return send_from_directory(current_app.config['COVER_FOLDER'], filename)

@book_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.get_by_id(book_id)
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    # 删除文件
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], book['file_path'])
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 删除封面
    if book['cover_path']:
        cover_path = os.path.join(current_app.config['COVER_FOLDER'], book['cover_path'])
        if os.path.exists(cover_path):
            os.remove(cover_path)
    
    # 从数据库中删除
    success = Book.delete(book_id)
    
    if success:
        return jsonify({'message': 'Book deleted successfully'})
    else:
        return jsonify({'error': 'Failed to delete book'}), 500

# 书签相关路由
@book_bp.route('/<int:book_id>/bookmarks', methods=['POST'])
def create_bookmark(book_id):
    data = request.json
    
    if not data or 'chapter_id' not in data or 'cfi' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    chapter_id = data['chapter_id']
    cfi = data['cfi']
    text = data.get('text', '')
    
    # 验证书籍和章节存在
    book = Book.get_by_id(book_id)
    chapter = Chapter.get_by_id(chapter_id)
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    if not chapter or chapter['book_id'] != book_id:
        return jsonify({'error': 'Chapter not found'}), 404
    
    # 创建书签
    bookmark_id = Bookmark.create(book_id, chapter_id, cfi, text)
    
    return jsonify({
        'id': bookmark_id,
        'book_id': book_id,
        'chapter_id': chapter_id,
        'cfi': cfi,
        'text': text
    }), 201

@book_bp.route('/<int:book_id>/bookmarks', methods=['GET'])
def get_bookmarks(book_id):
    # 验证书籍存在
    book = Book.get_by_id(book_id)
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    # 获取书签
    bookmarks = Bookmark.get_by_book_id(book_id)
    
    return jsonify(bookmarks)

@book_bp.route('/<int:book_id>/bookmarks/<int:bookmark_id>', methods=['DELETE'])
def delete_bookmark(book_id, bookmark_id):
    # 删除书签
    success = Bookmark.delete(bookmark_id)
    
    if success:
        return jsonify({'message': 'Bookmark deleted successfully'})
    else:
        return jsonify({'error': 'Failed to delete bookmark'}), 500

@book_bp.route('/<int:book_id>/content', methods=['GET'])
def get_book_content(book_id):
    # 验证书籍存在
    book = Book.get_by_id(book_id)
    
    if not book:
        current_app.logger.error(f"Book with ID {book_id} not found")
        return jsonify({'error': 'Book not found'}), 404
    
    # 返回EPUB文件
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], book['file_path'])
    
    if not os.path.exists(file_path):
        current_app.logger.error(f"EPUB file not found at path: {file_path}")
        return jsonify({'error': 'Book file not found'}), 404
    
    # 获取文件名
    filename = os.path.basename(book['file_path'])
    
    # 添加调试日志
    current_app.logger.info(f"Serving EPUB file: {file_path}, filename: {filename}, size: {os.path.getsize(file_path)} bytes")
    
    # 确保设置正确的MIME类型
    return send_from_directory(
        os.path.dirname(file_path),
        filename,
        as_attachment=False,
        mimetype='application/epub+zip'
    )

@book_bp.route('/<int:book_id>/chapters/<int:chapter_id>/content', methods=['GET'])
def get_chapter_content(book_id, chapter_id):
    # 验证书籍存在
    book = Book.get_by_id(book_id)
    
    if not book:
        current_app.logger.error(f"Book with ID {book_id} not found")
        return jsonify({'error': 'Book not found'}), 404
    
    # 验证章节存在
    chapter = Chapter.get_by_id(chapter_id)
    
    if not chapter or chapter['book_id'] != book_id:
        current_app.logger.error(f"Chapter with ID {chapter_id} not found for book {book_id}")
        return jsonify({'error': 'Chapter not found'}), 404
    
    # 如果数据库中已有HTML内容，直接返回
    if chapter.get('html_content'):
        return chapter['html_content'], 200, {'Content-Type': 'text/html; charset=utf-8'}
    
    # 否则从EPUB文件中获取
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], book['file_path'])
    
    if not os.path.exists(file_path):
        current_app.logger.error(f"EPUB file not found at path: {file_path}")
        return jsonify({'error': 'Book file not found'}), 404
    
    try:
        # 使用EpubService获取章节内容
        with EpubService(file_path) as epub:
            content_html = epub.get_chapter_html(chapter['href'])
            
            # 保存到数据库以便下次快速访问
            Chapter.update_html_content(chapter_id, content_html)
            
            # 返回HTML内容
            return content_html, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        current_app.logger.error(f"Error getting chapter content: {str(e)}")
        return jsonify({'error': str(e)}), 500

@book_bp.route('/resource/<path:resource_path>', methods=['GET'])
def get_resource(resource_path):
    """获取EPUB资源文件（图片、CSS等）"""
    # 安全检查，防止路径遍历攻击
    if '..' in resource_path:
        return jsonify({'error': 'Invalid resource path'}), 400
    
    # 尝试在所有上传的EPUB中查找资源
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    # 遍历所有EPUB文件
    for root, dirs, files in os.walk(upload_folder):
        for file in files:
            if file.endswith('.epub'):
                epub_path = os.path.join(root, file)
                
                # 尝试从EPUB中提取资源
                try:
                    with zipfile.ZipFile(epub_path, 'r') as zip_ref:
                        # 查找匹配的文件
                        for info in zip_ref.infolist():
                            if info.filename.endswith(resource_path):
                                # 提取文件到临时目录
                                temp_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp')
                                os.makedirs(temp_dir, exist_ok=True)
                                
                                extracted_path = zip_ref.extract(info, temp_dir)
                                
                                # 确定MIME类型
                                mime_type = 'application/octet-stream'
                                if resource_path.endswith('.css'):
                                    mime_type = 'text/css'
                                elif resource_path.endswith(('.jpg', '.jpeg')):
                                    mime_type = 'image/jpeg'
                                elif resource_path.endswith('.png'):
                                    mime_type = 'image/png'
                                elif resource_path.endswith('.gif'):
                                    mime_type = 'image/gif'
                                
                                return send_file(extracted_path, mimetype=mime_type)
                except Exception as e:
                    current_app.logger.error(f"Error extracting resource: {str(e)}")
                    continue
    
    return jsonify({'error': 'Resource not found'}), 404