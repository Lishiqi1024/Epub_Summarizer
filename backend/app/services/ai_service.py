import requests
import json
from flask import current_app
import time

class AIService:
    def __init__(self):
        # 使用配置文件中的API配置
        self.api_key = current_app.config.get('DEEPSEEK_API_KEY')
        self.base_url = current_app.config.get('DEEPSEEK_BASE_URL')
        self.model = current_app.config.get('DEEPSEEK_MODEL')
    
    def summarize_text(self, text):
        """使用AI生成文本总结"""
        # 如果文本太长，截断它
        if len(text) > 10000:
            text = text[:10000] + "..."
        
        try:
            # 构建请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 构建提示
            prompt = f"""
            请对以下文本内容进行全面而简洁的总结。总结应该：
            1. 提取文本中的关键信息和主要观点
            2. 保留重要的事实、数据和引用
            3. 使用清晰的结构组织信息
            4. 突出作者的核心论点和结论
            
            文本内容：
            {text}
            """
            
            # 构建请求数据
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是一个专业的文本分析和总结助手，擅长提取文本的核心内容并生成结构化总结。"},
                    {"role": "user", "content": prompt}
                ]
            }
            
            # 发送请求
            response = requests.post(self.base_url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()
            
            # 提取总结内容
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                return "无法生成总结，API返回格式异常。"
        except Exception as e:
            print(f"AI总结生成错误: {str(e)}")
            return f"生成总结时出错: {str(e)}"
    
    def generate_summary(self, content):
        """
        使用DeepSeek R1 API生成内容总结
        """
        # 这个方法保持不变，与 summarize_text 方法功能相同
        # 为了保持兼容性，我们保留这个方法
        return self.summarize_text(content)
    
    def _process_long_content(self, content, headers):
        """处理长文本内容"""
        # 分割内容
        chunks = self._split_content(content)
        
        # 处理每个块并生成摘要
        summaries = []
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}")
            
            prompt = f"""
            请对以下文本片段进行简洁总结，这是长文本的第{i+1}/{len(chunks)}部分：
            
            {chunk}
            """
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是一个专业的文本分析和总结助手。"},
                    {"role": "user", "content": prompt}
                ]
            }
            
            try:
                response = requests.post(self.base_url, headers=headers, data=json.dumps(data))
                response.raise_for_status()
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    summaries.append(result['choices'][0]['message']['content'])
                else:
                    summaries.append(f"无法生成第{i+1}部分的总结。")
                
                # 避免API限流
                time.sleep(1)
            except Exception as e:
                print(f"处理第{i+1}部分时出错: {str(e)}")
                summaries.append(f"处理第{i+1}部分时出错: {str(e)}")
        
        # 合并所有摘要
        combined_summary = "\n\n".join(summaries)
        
        # 生成最终摘要
        final_prompt = f"""
        以下是一篇长文本的分段摘要，请将这些摘要整合成一个连贯、全面的最终摘要：
        
        {combined_summary}
        """
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个专业的文本分析和总结助手。"},
                {"role": "user", "content": final_prompt}
            ]
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                return "无法生成最终总结。"
        except Exception as e:
            print(f"生成最终总结时出错: {str(e)}")
            return f"生成最终总结时出错: {str(e)}"
    
    def _split_content(self, content, max_chunk_size=4000):
        """将内容分割成多个块"""
        words = content.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            if current_size + len(word) + 1 > max_chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
                current_size += len(word) + 1  # +1 for space
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks

    def translate_text(self, text):
        """使用 AI 生成通俗易懂的翻译"""
        # 如果文本太长，截断它
        if len(text) > 10000:
            text = text[:10000] + "..."
        
        try:
            # 构建请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 构建提示
            prompt = f"""
            请将以下文本内容翻译成通俗易懂的大白话，使用简单直接的语言，避免专业术语和复杂表达：
            
            文本内容：
            {text}
            """
            
            # 构建请求数据
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是一个专业的文本翻译助手，擅长将复杂文本转化为通俗易懂的大白话。"},
                    {"role": "user", "content": prompt}
                ]
            }
            
            # 发送请求
            response = requests.post(self.base_url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()
            
            # 提取翻译内容
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                return "无法生成翻译，API返回格式异常。"
        except Exception as e:
            print(f"AI翻译生成错误: {str(e)}")
            return f"生成翻译时出错: {str(e)}"

    def generate_mermaid_diagram(self, text):
        """使用 AI 生成 Mermaid 图表"""
        # 如果文本太长，截断它
        if len(text) > 10000:
            text = text[:10000] + "..."
        
        try:
            # 构建请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 构建提示
            prompt = f"""
            请根据以下文本内容，生成一个 Mermaid 图表代码，用于可视化文本中的关键概念、关系或流程。
            图表应该简洁明了，突出文本的主要结构或逻辑关系。
            
            可以使用流程图、思维导图、类图或其他适合的图表类型。
            请只返回有效的 Mermaid 代码，不要包含其他解释。
            
            文本内容：
            {text}
            """
            
            # 构建请求数据
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是一个专业的图表生成助手，擅长将文本内容转化为 Mermaid 图表代码。"},
                    {"role": "user", "content": prompt}
                ]
            }
            
            # 发送请求
            response = requests.post(self.base_url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()
            
            # 提取图表内容
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                
                # 提取 Mermaid 代码块
                import re
                mermaid_match = re.search(r'```mermaid\n([\s\S]*?)\n```', content)
                if mermaid_match:
                    return mermaid_match.group(1).strip()
                else:
                    return content.strip()
            else:
                return "无法生成图表，API返回格式异常。"
        except Exception as e:
            print(f"AI图表生成错误: {str(e)}")
            return f"生成图表时出错: {str(e)}" 