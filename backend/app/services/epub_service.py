import os
import zipfile
import xml.etree.ElementTree as ET
import tempfile
import shutil
from bs4 import BeautifulSoup
import uuid
from flask import current_app

class EpubService:
    def __init__(self, file_path):
        self.file_path = file_path
        self.temp_dir = tempfile.mkdtemp()
        self.content_path = None
        self.opf_path = None
        self.cover_path = None
    
    def __enter__(self):
        with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
        
        # 查找container.xml
        container_path = os.path.join(self.temp_dir, 'META-INF', 'container.xml')
        if not os.path.exists(container_path):
            raise Exception("Invalid EPUB: container.xml not found")
        
        # 解析container.xml找到OPF文件
        tree = ET.parse(container_path)
        root = tree.getroot()
        ns = {'ns': 'urn:oasis:names:tc:opendocument:xmlns:container'}
        opf_path_rel = root.find('.//ns:rootfile', ns).get('full-path')
        
        self.opf_path = os.path.join(self.temp_dir, opf_path_rel)
        self.content_path = os.path.dirname(self.opf_path)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def get_metadata(self):
        """获取电子书元数据"""
        if not self.opf_path:
            raise Exception("OPF file not found")
        
        tree = ET.parse(self.opf_path)
        root = tree.getroot()
        
        # 定义命名空间
        ns = {
            'opf': 'http://www.idpf.org/2007/opf',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }
        
        # 提取元数据
        metadata = {}
        
        # 标题
        title_elem = root.find('.//dc:title', ns)
        metadata['title'] = title_elem.text if title_elem is not None else "Unknown Title"
        
        # 作者
        creator_elem = root.find('.//dc:creator', ns)
        metadata['author'] = creator_elem.text if creator_elem is not None else "Unknown Author"
        
        # 封面图片
        metadata['cover_path'] = self._get_cover_path(root, ns)
        
        # 保存封面路径
        self.cover_path = metadata['cover_path']
        
        return metadata
    
    def _get_cover_path(self, root, ns):
        """获取封面图片路径"""
        # 方法1: 通过meta标签查找
        meta_cover = root.find('.//opf:meta[@name="cover"]', ns)
        if meta_cover is not None:
            cover_id = meta_cover.get('content')
            cover_item = root.find(f'.//opf:item[@id="{cover_id}"]', ns)
            if cover_item is not None:
                return os.path.join(self.content_path, cover_item.get('href'))
        
        # 方法2: 查找带有"cover"属性的item
        cover_item = root.find('.//opf:item[@properties="cover-image"]', ns)
        if cover_item is not None:
            return os.path.join(self.content_path, cover_item.get('href'))
        
        # 方法3: 查找id或href包含"cover"的图片
        for item in root.findall('.//opf:item', ns):
            item_id = item.get('id', '').lower()
            item_href = item.get('href', '').lower()
            item_media = item.get('media-type', '')
            
            if (('cover' in item_id or 'cover' in item_href) and 
                item_media.startswith('image/')):
                return os.path.join(self.content_path, item.get('href'))
        
        return None
    
    def get_chapters(self):
        """获取章节列表"""
        if not self.opf_path:
            raise Exception("OPF file not found")
        
        tree = ET.parse(self.opf_path)
        root = tree.getroot()
        
        # 定义命名空间
        ns = {
            'opf': 'http://www.idpf.org/2007/opf',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }
        
        # 查找spine元素，它定义了阅读顺序
        spine = root.find('.//opf:spine', ns)
        if spine is None:
            return []
        
        # 获取manifest中的所有item
        manifest_items = {}
        for item in root.findall('.//opf:manifest/opf:item', ns):
            item_id = item.get('id')
            item_href = item.get('href')
            item_media = item.get('media-type')
            
            if item_id and item_href and item_media == 'application/xhtml+xml':
                manifest_items[item_id] = item_href
        
        # 查找目录文件
        toc_id = spine.get('toc')
        if toc_id:
            toc_item = root.find(f'.//opf:manifest/opf:item[@id="{toc_id}"]', ns)
            if toc_item is not None:
                toc_path = os.path.join(self.content_path, toc_item.get('href'))
                if os.path.exists(toc_path):
                    # 尝试从NCX文件中提取章节
                    ncx_chapters = self._extract_chapters_from_ncx(toc_path)
                    if ncx_chapters:
                        return ncx_chapters
        
        # 如果没有找到NCX文件或NCX文件中没有章节，则从spine中提取
        chapters = []
        order_num = 1
        
        for itemref in spine.findall('.//opf:itemref', ns):
            idref = itemref.get('idref')
            if idref in manifest_items:
                href = manifest_items[idref]
                file_path = os.path.join(self.content_path, href)
                
                # 尝试从文件中提取标题
                title = self._extract_title_from_file(file_path)
                if not title:
                    title = f"Chapter {order_num}"
                
                chapters.append({
                    'title': title,
                    'href': href,
                    'order_num': order_num
                })
                
                order_num += 1
        
        return chapters
    
    def _extract_title_from_file(self, file_path):
        """从HTML文件中提取标题"""
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # 尝试从标题标签中提取
            for tag in ['h1', 'h2', 'h3', 'h4', 'title']:
                title_tag = soup.find(tag)
                if title_tag and title_tag.text.strip():
                    return title_tag.text.strip()
            
            # 尝试从class或id包含'title'的元素中提取
            title_elem = soup.find(class_=lambda x: x and 'title' in x.lower())
            if title_elem and title_elem.text.strip():
                return title_elem.text.strip()
            
            title_elem = soup.find(id=lambda x: x and 'title' in x.lower())
            if title_elem and title_elem.text.strip():
                return title_elem.text.strip()
            
            return None
        except Exception as e:
            print(f"Error extracting title from {file_path}: {str(e)}")
            return None
    
    def _extract_chapters_from_ncx(self, ncx_path):
        """从NCX文件中提取章节信息"""
        if not os.path.exists(ncx_path):
            return []
        
        try:
            tree = ET.parse(ncx_path)
            root = tree.getroot()
            
            # 定义命名空间
            ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
            
            # 提取navPoints
            chapters = []
            order_num = 1
            
            for navPoint in root.findall('.//ncx:navPoint', ns):
                # 获取标题
                navLabel = navPoint.find('.//ncx:navLabel/ncx:text', ns)
                if navLabel is None or not navLabel.text:
                    continue
                
                title = navLabel.text
                
                # 获取链接
                content = navPoint.find('.//ncx:content', ns)
                if content is None:
                    continue
                
                src = content.get('src')
                if not src:
                    continue
                
                # 处理锚点
                href = src.split('#')[0]
                
                chapters.append({
                    'title': title,
                    'href': href,
                    'order_num': order_num
                })
                
                order_num += 1
            
            return chapters
        except Exception as e:
            print(f"Error extracting chapters from NCX: {str(e)}")
            return []
    
    def get_chapter_content(self, href):
        """获取指定章节的内容"""
        try:
            file_path = os.path.join(self.content_path, href)
            
            if not os.path.exists(file_path):
                print(f"Chapter file not found: {file_path}")
                return "章节内容不可用"
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # 尝试其他编码
                try:
                    with open(file_path, 'r', encoding='gbk') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            content = f.read()
                    except Exception as e:
                        print(f"Failed to read file with multiple encodings: {str(e)}")
                        return f"无法读取章节内容: {str(e)}"
            
            # 使用BeautifulSoup提取文本
            soup = BeautifulSoup(content, 'html.parser')
            
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
                
                return '\n\n'.join(paragraphs)
            else:
                # 尝试直接从HTML中提取文本
                text = soup.get_text(separator='\n').strip()
                paragraphs = [line.strip() for line in text.split('\n') if line.strip()]
                
                if paragraphs:
                    return '\n\n'.join(paragraphs)
                else:
                    return "无法提取章节内容"
        except Exception as e:
            print(f"Error getting chapter content: {str(e)}")
            return f"获取章节内容时出错: {str(e)}"
    
    def save_cover_image(self, cover_folder):
        """保存封面图片到指定文件夹"""
        # 确保已经调用了 get_metadata 方法
        if not hasattr(self, 'cover_path') or not self.cover_path:
            # 尝试获取元数据
            self.get_metadata()
        
        if not self.cover_path or not os.path.exists(self.cover_path):
            return None
        
        try:
            # 确保目标文件夹存在
            os.makedirs(cover_folder, exist_ok=True)
            
            # 生成唯一文件名
            cover_filename = f"{uuid.uuid4()}.jpg"
            cover_file_path = os.path.join(cover_folder, cover_filename)
            
            # 复制封面图片
            shutil.copy2(self.cover_path, cover_file_path)
            
            return cover_filename
        except Exception as e:
            print(f"Error saving cover image: {str(e)}")
            return None
    
    def get_chapter_html(self, href):
        """获取指定章节的HTML内容"""
        try:
            file_path = os.path.join(self.content_path, href)
            
            if not os.path.exists(file_path):
                print(f"Chapter file not found: {file_path}")
                return "<h1>章节内容不可用</h1><p>找不到章节文件</p>"
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # 尝试其他编码
                try:
                    with open(file_path, 'r', encoding='gbk') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            content = f.read()
                    except Exception as e:
                        print(f"Failed to read file with multiple encodings: {str(e)}")
                        return f"<h1>无法读取章节内容</h1><p>编码错误: {str(e)}</p>"
            
            # 修复相对路径
            try:
                soup = BeautifulSoup(content, 'html.parser')
                
                # 修复图片路径
                for img in soup.find_all('img'):
                    if img.get('src') and not img['src'].startswith(('http://', 'https://', 'data:')):
                        img_path = os.path.join(os.path.dirname(href), img['src'])
                        img['src'] = f"/api/books/resource/{img_path}"
                
                # 修复CSS路径
                for link in soup.find_all('link', rel='stylesheet'):
                    if link.get('href') and not link['href'].startswith(('http://', 'https://', 'data:')):
                        css_path = os.path.join(os.path.dirname(href), link['href'])
                        link['href'] = f"/api/books/resource/{css_path}"
                
                # 添加基本样式
                style = soup.new_tag('style')
                style.string = """
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 100%;
                    margin: 0 auto;
                    padding: 20px;
                }
                img {
                    max-width: 100%;
                    height: auto;
                }
                h1, h2, h3, h4, h5, h6 {
                    margin-top: 1em;
                    margin-bottom: 0.5em;
                }
                p {
                    margin-bottom: 1em;
                }
                """
                if soup.head:
                    soup.head.append(style)
                else:
                    # 如果没有head标签，创建一个
                    head = soup.new_tag('head')
                    head.append(style)
                    if soup.html:
                        soup.head.insert(0, head)
                    else:
                        # 如果没有html标签，创建完整的文档结构
                        html = soup.new_tag('html')
                        html.append(head)
                        body = soup.new_tag('body')
                        for tag in list(soup.contents):
                            body.append(tag.extract())
                        html.append(body)
                        soup = BeautifulSoup(str(html), 'html.parser')
                
                return str(soup)
            except Exception as e:
                print(f"Error processing HTML: {str(e)}")
                return f"<h1>处理HTML内容时出错</h1><p>{str(e)}</p>"
        except Exception as e:
            print(f"Error getting chapter HTML: {str(e)}")
            return f"<h1>获取章节内容时出错</h1><p>{str(e)}</p>" 