import os
import time
import PyPDF2
from docx import Document
import markdown
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import system_config
from logger import get_logger

logger = get_logger(__name__)

class DocumentProcessor:
    """文档处理器 - 负责文档加载和分块"""
    
    def __init__(self):
        self.config = system_config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            length_function=len,
        )
    
    def process_document(self, file_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理文档并返回分块数据"""
        try:
            # 加载文档
            text = self.load_document(file_path)
            
            if not text.strip():
                return {
                    "success": False,
                    "error": "文档内容为空"
                }
            
            # 分块处理
            chunks = self.chunk_document(text)
            
            # 添加元数据
            file_metadata = {
                "source": os.path.basename(file_path),
                "file_path": file_path,
                "file_type": os.path.splitext(file_path)[1].lower(),
                "total_chunks": len(chunks)
            }
            
            # 合并用户提供的元数据
            if metadata:
                file_metadata.update(metadata)
            
            # 为每个块添加元数据
            for i, chunk in enumerate(chunks):
                chunk["metadata"] = {
                    **file_metadata,
                    "chunk_index": i,
                    "chunk_size": len(chunk["content"])
                }
            
            return {
                "success": True,
                "chunks": chunks,
                "metadata": file_metadata,
                "total_chunks": len(chunks)
            }
            
        except Exception as e:
            error_msg = f"文档处理失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def load_document(self, file_path: str) -> str:
        """加载文档并提取文本"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self._load_pdf(file_path)
        elif file_extension == '.docx':
            return self._load_docx(file_path)
        elif file_extension in ['.txt', '.md']:
            return self._load_text(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")
    
    def _load_pdf(self, file_path: str) -> str:
        """加载PDF文件"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"PDF加载失败: {e}")
            raise
        return text
    
    def _load_docx(self, file_path: str) -> str:
        """加载Word文档"""
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            logger.error(f"Word文档加载失败: {e}")
            raise
        return text
    
    def _load_text(self, file_path: str) -> str:
        """加载文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # 如果是Markdown文件，转换为纯文本
            if file_path.endswith('.md'):
                content = markdown.markdown(content)
                # 简单去除HTML标签
                import re
                content = re.sub(r'<[^>]+>', '', content)
                
            return content
        except Exception as e:
            logger.error(f"文本文件加载失败: {e}")
            raise
    
    def chunk_document(self, text: str) -> List[Dict[str, Any]]:
        """将文档分块"""
        chunks = self.text_splitter.split_text(text)
        
        chunk_data = []
        for i, chunk in enumerate(chunks):
            chunk_data.append({
                "id": f"chunk_{i}_{int(time.time())}",
                "content": chunk
            })
        
        return chunk_data
    
    def batch_process_documents(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """批量处理文档"""
        results = []
        for file_path in file_paths:
            result = self.process_document(file_path)
            results.append({
                "file_path": file_path,
                "success": result["success"],
                "message": result.get("message", ""),
                "error": result.get("error", ""),
                "chunks": result.get("chunks", [])
            })
        return results