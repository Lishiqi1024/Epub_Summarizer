import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

const apiService = {
  // 书籍相关API
  getBooks() {
    return axios.get(`${API_URL}/books/`)
  },
  
  getBook(bookId) {
    return axios.get(`${API_URL}/books/${bookId}`)
  },
  
  uploadBook(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    return axios.post(`${API_URL}/books/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  deleteBook(bookId) {
    return axios.delete(`${API_URL}/books/${bookId}`)
  },
  
  getChapter(bookId, chapterId) {
    return axios.get(`${API_URL}/books/${bookId}/chapters/${chapterId}`)
      .catch(error => {
        console.error('Error fetching chapter:', error);
        throw error;
      });
  },
  
  // 书签相关API
  getBookmarks(bookId) {
    return axios.get(`${API_URL}/books/${bookId}/bookmarks`)
  },
  
  createBookmark(bookId, chapterId, cfi, text) {
    return axios.post(`${API_URL}/books/${bookId}/bookmarks`, {
      chapter_id: chapterId,
      cfi: cfi,
      text: text
    })
  },
  
  deleteBookmark(bookId, bookmarkId) {
    return axios.delete(`${API_URL}/books/${bookId}/bookmarks/${bookmarkId}`)
  },
  
  // AI总结相关API
  summarizeChapter(chapterId) {
    return axios.get(`${API_URL}/ai/summarize/chapter/${chapterId}`)
  },
  
  summarizeText(text) {
    return axios.post(`${API_URL}/ai/summarize/text`, {
      text: text
    })
  },
  
  // 添加更新最后阅读时间的方法
  updateLastRead(bookId) {
    return axios.put(`${API_URL}/books/${bookId}/last-read`)
      .catch(error => {
        console.error('Error updating last read:', error);
        throw error;
      });
  },
  
  // 添加获取完整EPUB文件的方法
  getBookContent(bookId) {
    console.log(`Fetching book content for book ID: ${bookId}`);
    return axios.get(`${API_URL}/books/${bookId}/content`, {
      responseType: 'blob'
    }).then(response => {
      console.log('Book content fetched successfully, content type:', response.headers['content-type']);
      return response;
    }).catch(error => {
      console.error('Error fetching book content:', error);
      throw error;
    });
  },
  
  // 获取章节内容
  getChapterContent(bookId, chapterId) {
    return axios.get(`${API_URL}/books/${bookId}/chapters/${chapterId}/content`, {
      responseType: 'text'
    }).catch(error => {
      console.error('Error fetching chapter content:', error);
      throw error;
    });
  },
  
  // 获取章节翻译
  translateChapter(chapterId) {
    return axios.get(`${API_URL}/ai/translate/chapter/${chapterId}`)
  },
  
  // 获取章节图表
  getChapterDiagram(chapterId) {
    return axios.get(`${API_URL}/ai/diagram/chapter/${chapterId}`)
  }
}

export default apiService 