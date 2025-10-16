import os
import uuid
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from config import system_config
from zhipu_service import zhipu_service
from logger import get_logger

logger = get_logger(__name__)

class VectorDBManager:
    """向量数据库管理器"""
    
    def __init__(self):
        self.config = system_config
        self.client = None
        self.collection = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """初始化向量数据库"""
        try:
            # 创建数据目录
            os.makedirs(self.config.VECTOR_DB_DIR, exist_ok=True)
            
            # 初始化ChromaDB客户端
            self.client = chromadb.PersistentClient(
                path=self.config.VECTOR_DB_DIR,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # 获取或创建集合
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
            )
            
            self._initialized = True
            logger.info("向量数据库初始化完成")
            return True
            
        except Exception as e:
            error_msg = f"向量数据库初始化失败: {str(e)}"
            logger.error(error_msg)
            return False
    
    def add_documents(self, documents: List[Dict[str, Any]], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """添加文档到向量数据库"""
        if not self._initialized:
            return {"success": False, "error": "向量数据库未初始化"}
        
        try:
            # 准备数据
            doc_contents = [doc["content"] for doc in documents]
            doc_ids = [doc["id"] for doc in documents]
            doc_metadatas = [doc.get("metadata", {}) for doc in documents]
            
            # 如果提供了额外的元数据，合并到每个文档的元数据中
            if metadata:
                for doc_meta in doc_metadatas:
                    doc_meta.update(metadata)
            
            # 生成嵌入向量
            embeddings = zhipu_service.get_embeddings(doc_contents)
            
            # 添加到集合
            self.collection.add(
                embeddings=embeddings,
                documents=doc_contents,
                metadatas=doc_metadatas,
                ids=doc_ids
            )
            
            return {
                "success": True,
                "message": f"成功添加 {len(documents)} 个文档块",
                "count": len(documents)
            }
            
        except Exception as e:
            error_msg = f"添加文档失败: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def search(self, query: str, top_k: int = None, filter_dict: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """搜索相似文档"""
        if not self._initialized:
            return []
        
        if top_k is None:
            top_k = self.config.TOP_K
        
        try:
            # 生成查询嵌入
            query_embedding = zhipu_service.get_embeddings([query])
            
            # 执行搜索
            search_kwargs = {
                "query_embeddings": query_embedding,
                "n_results": top_k
            }
            
            # 如果提供了过滤条件，添加到搜索参数中
            if filter_dict:
                search_kwargs["where"] = filter_dict
            
            results = self.collection.query(**search_kwargs)
            
            # 格式化结果
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    similarity = 1 - distance  # 转换为相似度分数
                    
                    # 应用相似度阈值过滤
                    if similarity >= self.config.SIMILARITY_THRESHOLD:
                        search_results.append({
                            "content": doc,
                            "metadata": metadata,
                            "similarity": similarity,
                            "rank": i + 1
                        })
            
            return search_results
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def get_document_count(self) -> int:
        """获取文档数量"""
        if not self._initialized:
            return 0
        
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"获取文档数量失败: {e}")
            return 0
    
    def get_status(self) -> Dict[str, Any]:
        """获取向量数据库状态"""
        if not self._initialized:
            return {"initialized": False}
        
        try:
            return {
                "initialized": True,
                "document_count": self.get_document_count(),
                "collection_name": self.collection.name,
                "embedding_model": self.config.EMBEDDING_MODEL_NAME
            }
        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            return {"initialized": False, "error": str(e)}
    
    def clear_collection(self) -> Dict[str, Any]:
        """清空集合"""
        if not self._initialized:
            return {"success": False, "error": "向量数据库未初始化"}
        
        try:
            # 删除集合
            self.client.delete_collection(name=self.collection.name)
            
            # 重新创建集合
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            
            return {
                "success": True,
                "message": "集合已清空"
            }
            
        except Exception as e:
            error_msg = f"清空集合失败: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def delete_documents(self, ids: List[str]) -> Dict[str, Any]:
        """删除指定ID的文档"""
        if not self._initialized:
            return {"success": False, "error": "向量数据库未初始化"}
        
        try:
            self.collection.delete(ids=ids)
            return {
                "success": True,
                "message": f"成功删除 {len(ids)} 个文档"
            }
        except Exception as e:
            error_msg = f"删除文档失败: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}