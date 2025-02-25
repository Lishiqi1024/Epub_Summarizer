import { Book } from 'epubjs'

class EpubService {
  constructor() {
    this.book = null
    this.rendition = null
    this.displayed = null
  }
  
  // 打开EPUB文件
  open(url) {
    console.log('Opening EPUB file:', url);
    
    // 确保关闭之前的书籍
    if (this.book) {
      this.close();
    }
    
    // 创建新的Book实例
    console.log('Creating new Book instance');
    
    // 尝试不同的配置选项
    const options = {
      openAs: 'binary',
      encoding: 'binary'
    };
    
    this.book = new Book(url, options);
    
    // 添加事件监听器
    this.book.on('openFailed', (error) => {
      console.error('EPUB open failed:', error);
    });
    
    return this.book.ready.then(() => {
      console.log('EPUB book loaded successfully');
      // 打印一些书籍信息
      if (this.book.spine && this.book.spine.items) {
        console.log('Book spine items:', this.book.spine.items.length);
      }
      console.log('Book navigation:', this.book.navigation);
      return this.book;
    }).catch(err => {
      console.error('Error loading EPUB book:', err);
      throw err;
    });
  }
  
  // 渲染到指定元素
  renderTo(element, options = {}) {
    if (!this.book) {
      console.error('Book not loaded yet');
      throw new Error('电子书尚未加载');
    }
    
    const defaultOptions = {
      width: '100%',
      height: '100%',
      spread: 'none',
      flow: 'paginated',
      manager: 'default'
    };
    
    try {
      console.log('Rendering book to element:', element);
      this.rendition = this.book.renderTo(element, {
        ...defaultOptions,
        ...options
      });
      
      // 添加基本样式
      this.rendition.themes.register('default', {
        'body': {
          'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
          'font-size': '1em',
          'line-height': '1.5',
          'padding': '0 !important',
          'margin': '0 !important'
        },
        'p': {
          'font-family': 'inherit',
          'margin': '1em 0 !important'
        },
        'h1, h2, h3, h4, h5, h6': {
          'font-family': 'inherit',
          'margin': '1em 0 0.5em 0 !important'
        },
        'img': {
          'max-width': '100% !important'
        }
      });
      
      // 应用默认主题
      this.rendition.themes.select('default');
      
      console.log('Book rendered successfully');
      return this.rendition;
    } catch (error) {
      console.error('Error rendering book:', error);
      throw new Error('渲染电子书失败：' + (error.message || '未知错误'));
    }
  }
  
  // 显示指定章节
  async display(target) {
    if (!this.book) {
      console.error('Book not loaded yet');
      throw new Error('电子书尚未加载');
    }
    
    if (!this.rendition) {
      console.error('Book not rendered yet');
      throw new Error('阅读器尚未初始化');
    }
    
    try {
      console.log('Displaying target:', target);
      
      // 确保book已经准备好
      await this.book.ready;
      
      // 尝试查找章节
      let href = target;
      
      // 如果target是章节href，确保它是相对路径
      if (typeof target === 'string' && !target.startsWith('epubcfi')) {
        // 移除开头的斜杠（如果有）
        href = target.startsWith('/') ? target.substring(1) : target;
        console.log('Normalized href:', href);
        
        // 尝试在spine中查找章节
        const spineItem = this.book.spine.get(href);
        if (!spineItem) {
          console.warn('Spine item not found for href:', href);
          // 尝试查找最接近的匹配
          const items = this.book.spine.items;
          if (items && items.length > 0) {
            for (let i = 0; i < items.length; i++) {
              const item = items[i];
              if (item.href && (item.href.includes(href) || href.includes(item.href))) {
                href = item.href;
                console.log('Found closest match:', href);
                break;
              }
            }
          } else {
            console.warn('No spine items found');
          }
        }
      }
      
      // 显示章节
      console.log('Final display target:', href);
      this.displayed = await this.rendition.display(href);
      
      // 确保内容可见
      this.rendition.views().forEach(view => {
        if (view && view.element) {
          view.element.style.visibility = 'visible';
        }
      });
      
      return this.displayed;
    } catch (error) {
      console.error('Error displaying chapter:', error);
      throw new Error('加载章节失败：' + (error.message || '未知错误'));
    }
  }
  
  // 获取当前位置
  getCurrentLocation() {
    if (!this.rendition) {
      return null;
    }
    
    return this.rendition.currentLocation();
  }
  
  // 获取当前章节信息
  async getCurrentChapter() {
    if (!this.rendition) {
      return null;
    }
    
    try {
      const location = await this.getCurrentLocation();
      if (!location || !location.start) {
        return null;
      }
      
      const cfi = location.start.cfi;
      const href = await this.book.spine.getHref(cfi);
      
      return {
        href: href,
        cfi: cfi
      };
    } catch (error) {
      console.error('Error getting current chapter:', error);
      return null;
    }
  }
  
  // 下一页
  next() {
    if (!this.rendition) {
      return;
    }
    
    return this.rendition.next();
  }
  
  // 上一页
  prev() {
    if (!this.rendition) {
      return;
    }
    
    return this.rendition.prev();
  }
  
  // 设置字体大小
  setFontSize(size) {
    if (!this.rendition) {
      return;
    }
    
    this.rendition.themes.fontSize(size);
    
    // 保存设置到localStorage
    localStorage.setItem('epub_font_size', size);
  }
  
  // 设置主题
  setTheme(theme) {
    if (!this.rendition) {
      return;
    }
    
    // 定义主题
    const themes = {
      light: {
        body: {
          color: '#000',
          background: '#fff'
        }
      },
      dark: {
        body: {
          color: '#fff',
          background: '#333'
        }
      },
      sepia: {
        body: {
          color: '#5b4636',
          background: '#f4ecd8'
        }
      }
    };
    
    // 注册主题
    if (!this._themesRegistered) {
      Object.keys(themes).forEach(key => {
        this.rendition.themes.register(key, themes[key]);
      });
      this._themesRegistered = true;
    }
    
    // 应用主题
    this.rendition.themes.select(theme);
    
    // 保存设置到localStorage
    localStorage.setItem('epub_theme', theme);
  }
  
  // 保存阅读进度
  saveProgress(bookId) {
    if (!this.rendition) {
      return;
    }
    
    const location = this.rendition.currentLocation();
    if (location && location.start) {
      localStorage.setItem(`book_progress_${bookId}`, location.start.cfi);
      console.log('Progress saved:', location.start.cfi);
    }
  }
  
  // 恢复阅读进度
  restoreProgress(bookId) {
    const cfi = localStorage.getItem(`book_progress_${bookId}`);
    console.log('Restoring progress:', cfi);
    return cfi;
  }
  
  // 应用保存的设置
  applySettings() {
    if (!this.rendition) {
      return;
    }
    
    // 应用字体大小
    const fontSize = localStorage.getItem('epub_font_size');
    if (fontSize) {
      this.setFontSize(fontSize);
    }
    
    // 应用主题
    const theme = localStorage.getItem('epub_theme');
    if (theme) {
      this.setTheme(theme);
    }
  }
  
  // 关闭书籍
  close() {
    if (this.book) {
      this.book.destroy();
      this.book = null;
      this.rendition = null;
      this.displayed = null;
      console.log('Book closed');
    }
  }
}

export default new EpubService();