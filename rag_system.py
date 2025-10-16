import os
import time
from typing import List, Dict, Any, Optional
from document_processor import DocumentProcessor
from vector_db import VectorDBManager
from qa_engine import QAEngine
from config import system_config
from logger import get_logger

logger = get_logger(__name__)

class RAGSystem:
    """RAG智能问答系统主控制器"""
    
    def __init__(self):
        self.config = system_config
        self.document_processor = DocumentProcessor()
        self.vector_db = VectorDBManager()
        self.qa_engine = QAEngine(self.vector_db)
        
        # 系统状态
        self._initialized = False
        self._document_count = 0
    
    def initialize(self) -> bool:
        """初始化系统"""
        try:
            # 验证配置
            self.config.validate_config()
            
            # 初始化向量数据库
            if not self.vector_db.initialize():
                return False
            
            # 获取现有文档统计
            self._document_count = self.vector_db.get_document_count()
            
            self._initialized = True
            logger.info("RAG系统初始化完成")
            return True
            
        except Exception as e:
            error_msg = f"系统初始化失败: {e}"
            logger.error(error_msg)
            return False
    
    def add_document(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """添加文档到系统"""
        if not self._initialized:
            return {"success": False, "error": "系统未初始化"}
        
        try:
            # 处理文档
            document_data = self.document_processor.process_document(file_path, metadata)
            
            if not document_data["success"]:
                return document_data
            
            # 添加到向量数据库
            result = self.vector_db.add_documents(
                documents=document_data["chunks"],
                metadata=document_data.get("metadata", {})
            )
            
            if result["success"]:
                self._document_count += 1
                logger.info(f"文档添加成功: {os.path.basename(file_path)}")
            
            return result
            
        except Exception as e:
            error_msg = f"文档处理失败: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def batch_add_documents(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """批量添加文档"""
        results = []
        for file_path in file_paths:
            result = self.add_document(file_path)
            results.append({
                "file_path": file_path,
                "success": result["success"],
                "message": result.get("message", ""),
                "error": result.get("error", "")
            })
        return results
    
    def query(self, question: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        """查询问题"""
        if not self._initialized:
            return {
                "success": False, 
                "answer": "系统未初始化，请先添加文档",
                "sources": []
            }
        
        if self._document_count == 0:
            return {
                "success": False,
                "answer": "系统中暂无文档，请先添加文档后再提问",
                "sources": []
            }
        
        return self.qa_engine.answer_question(question, top_k)
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        db_status = self.vector_db.get_status()
        
        return {
            "initialized": self._initialized,
            "document_count": self._document_count,
            "vector_db": db_status,
            "config": {
                "embedding_model": self.config.EMBEDDING_MODEL_NAME,
                "llm_model": self.config.LLM_MODEL,
                "chunk_size": self.config.CHUNK_SIZE,
                "similarity_threshold": self.config.SIMILARITY_THRESHOLD
            }
        }
    
    def clear_documents(self) -> Dict[str, Any]:
        """清空所有文档"""
        try:
            result = self.vector_db.clear_collection()
            if result["success"]:
                self._document_count = 0
                logger.info("所有文档已清空")
            return result
        except Exception as e:
            error_msg = f"清空文档失败: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def get_document_sources(self) -> List[Dict[str, Any]]:
        """获取所有文档来源"""
        try:
            # 这里可以实现获取所有文档来源的逻辑
            # 由于ChromaDB的限制，可能需要维护一个单独的文档索引
            return []
        except Exception as e:
            logger.error(f"获取文档来源失败: {e}")
            return []

# 全局系统实例
rag_system = RAGSystem()