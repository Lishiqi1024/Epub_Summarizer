from flask import Blueprint, request, jsonify, current_app
from app.services.ai_service import AIService
from app.models.book import Chapter, Book
from app.services.epub_service import EpubService
import os
from bs4 import BeautifulSoup
import traceback

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/summarize/chapter/<int:chapter_id>', methods=['GET'])
def summarize_chapter(chapter_id):
    # 获取章节信息
    chapter = Chapter.get_by_id(chapter_id)
    
    if not chapter:
        return jsonify({'error': 'Chapter not found'}), 404
    
    # 检查是否已有总结
    if chapter.get('summary'):
        return jsonify({'summary': chapter['summary']})
    
    # 获取书籍信息
    book = Book.get_by_id(chapter['book_id'])
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    try:
        # 尝试从HTML内容中提取文本
        if chapter.get('html_content'):
            soup = BeautifulSoup(chapter['html_content'], 'html.parser')
            
            # 提取正文内容
            body = soup.find('body')
            if body:
                # 移除脚本和样式
                for script in body.find_all(['script', 'style']):
                    script.decompose()
                
                # 获取所有文本，保留段落结构
                paragraphs = []
                for p in body.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    text = p.get_text().strip()
                    if text:
                        paragraphs.append(text)
                
                # 如果没有找到段落，尝试获取所有文本
                if not paragraphs:
                    text = body.get_text(separator='\n').strip()
                    paragraphs = [line.strip() for line in text.split('\n') if line.strip()]
                
                content = '\n\n'.join(paragraphs)
            else:
                # 尝试直接从HTML中提取文本
                text = soup.get_text(separator='\n').strip()
                paragraphs = [line.strip() for line in text.split('\n') if line.strip()]
                
                if paragraphs:
                    content = '\n\n'.join(paragraphs)
                else:
                    # 如果无法从HTML中提取文本，则从EPUB文件中获取
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], book['file_path'])
                    
                    if not os.path.exists(file_path):
                        return jsonify({'error': 'Book file not found'}), 404
                    
                    with EpubService(file_path) as epub:
                        content = epub.get_chapter_content(chapter['href'])
        else:
            # 如果没有HTML内容，则从EPUB文件中获取
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], book['file_path'])
            
            if not os.path.exists(file_path):
                return jsonify({'error': 'Book file not found'}), 404
            
            with EpubService(file_path) as epub:
                content = epub.get_chapter_content(chapter['href'])
        
        # 记录提取的内容长度
        current_app.logger.info(f"Extracted content length: {len(content)}")
        
        # 使用AI服务生成总结
        ai_service = AIService()
        summary = ai_service.summarize_text(content)
        
        # 保存总结到数据库
        Chapter.update_summary(chapter_id, summary)
        
        return jsonify({'summary': summary})
    except Exception as e:
        current_app.logger.error(f"Error summarizing chapter: {str(e)}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/summarize/text', methods=['POST'])
def summarize_text():
    data = request.json
    
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text field'}), 400
    
    text = data['text']
    
    if not text or len(text) < 100:
        return jsonify({'error': 'Text is too short to summarize'}), 400
    
    try:
        # 生成总结
        ai_service = AIService()
        summary = ai_service.generate_summary(text)
        
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/translate/chapter/<int:chapter_id>', methods=['GET'])
def translate_chapter(chapter_id):
    # 获取章节信息
    chapter = Chapter.get_by_id(chapter_id)
    
    if not chapter:
        return jsonify({'error': 'Chapter not found'}), 404
    
    # 检查是否已有翻译
    if chapter.get('translation'):
        return jsonify({'translation': chapter['translation']})
    
    # 获取书籍信息
    book = Book.get_by_id(chapter['book_id'])
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    # 获取EPUB文件路径
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], book['file_path'])
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'Book file not found'}), 404
    
    try:
        # 使用EpubService获取章节内容
        with EpubService(file_path) as epub:
            content = epub.get_chapter_content(chapter['href'])
            
            # 使用AI服务生成翻译
            ai_service = AIService()
            translation = ai_service.translate_text(content)
            
            # 保存翻译到数据库
            Chapter.update_translation(chapter_id, translation)
            
            return jsonify({'translation': translation})
    except Exception as e:
        current_app.logger.error(f"Error translating chapter: {str(e)}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/diagram/chapter/<int:chapter_id>', methods=['GET'])
def generate_chapter_diagram(chapter_id):
    # 获取章节信息
    chapter = Chapter.get_by_id(chapter_id)
    
    if not chapter:
        return jsonify({'error': 'Chapter not found'}), 404
    
    # 检查是否已有图表
    if chapter.get('mermaid_diagram'):
        return jsonify({'diagram': chapter['mermaid_diagram']})
    
    # 获取书籍信息
    book = Book.get_by_id(chapter['book_id'])
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    # 获取EPUB文件路径
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], book['file_path'])
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'Book file not found'}), 404
    
    try:
        # 使用EpubService获取章节内容
        with EpubService(file_path) as epub:
            content = epub.get_chapter_content(chapter['href'])
            
            # 使用AI服务生成图表
            ai_service = AIService()
            diagram = ai_service.generate_mermaid_diagram(content)
            
            # 保存图表到数据库
            Chapter.update_mermaid_diagram(chapter_id, diagram)
            
            return jsonify({'diagram': diagram})
    except Exception as e:
        current_app.logger.error(f"Error generating chapter diagram: {str(e)}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500 