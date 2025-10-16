import os
import requests
import json
import time
from typing import List, Dict, Any, Optional
from config import system_config
from logger import get_logger

logger = get_logger(__name__)

class ZhipuAIService:
    """智普AI服务封装类"""
    
    def __init__(self):
        self.config = system_config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.config.ZHIPU_API_KEY}",
            "Content-Type": "application/json"
        })
        
        # 初始化本地BGE模型
        self.tokenizer = None
        self.model = None
        self._init_local_model()
    
    def _init_local_model(self):
        """初始化本地BGE模型"""
        try:
            # 首先尝试使用SentenceTransformers
            try:
                from sentence_transformers import SentenceTransformer
                self.sentence_model = SentenceTransformer(self.config.EMBEDDING_MODEL_PATH)
                logger.info(f"成功加载本地BGE模型(SentenceTransformers): {self.config.EMBEDDING_MODEL_PATH}")
                return
            except ImportError:
                logger.warning("SentenceTransformers库未安装，尝试使用transformers库")
            
            # 如果SentenceTransformers不可用，使用transformers
            from transformers import AutoTokenizer, AutoModel
            import torch
            
            # 加载tokenizer和模型
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.EMBEDDING_MODEL_PATH)
            self.model = AutoModel.from_pretrained(self.config.EMBEDDING_MODEL_PATH)
            self.model.eval()  # 设置为评估模式
            
            logger.info(f"成功加载本地BGE模型(Transformers): {self.config.EMBEDDING_MODEL_PATH}")
        except Exception as e:
            logger.error(f"加载本地BGE模型失败: {e}")
            self.tokenizer = None
            self.model = None
            self.sentence_model = None
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """聊天补全接口"""
        url = f"{self.config.ZHIPU_BASE_URL}/chat/completions"
        
        payload = {
            "model": kwargs.get("model", self.config.LLM_MODEL),
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
            "top_p": kwargs.get("top_p", 0.9),
            "stream": False
        }
        
        try:
            response = self.session.post(
                url, 
                json=payload, 
                timeout=self.config.TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                "success": True,
                "content": result["choices"][0]["message"]["content"],
                "usage": result.get("usage", {}),
                "model": result["model"]
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"智普AI请求失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": "抱歉，AI服务暂时不可用"
            }
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """获取文本嵌入向量 - 使用本地BGE模型"""
        # 如果本地模型未初始化，尝试初始化
        if not hasattr(self, 'sentence_model') or self.sentence_model is None:
            if self.tokenizer is None or self.model is None:
                self._init_local_model()
        
        # 优先使用SentenceTransformers
        if hasattr(self, 'sentence_model') and self.sentence_model is not None:
            try:
                embeddings = self.sentence_model.encode(texts, normalize_embeddings=True)
                return embeddings.tolist()
            except Exception as e:
                logger.error(f"SentenceTransformers嵌入向量获取失败: {e}")
        
        # 如果SentenceTransformers不可用，尝试使用transformers
        if self.tokenizer is not None and self.model is not None:
            try:
                import torch
                import torch.nn.functional as F
                
                # 编码文本
                encoded_input = self.tokenizer(texts, padding=True, truncation=True, max_length=512, return_tensors='pt')
                
                # 生成嵌入向量
                with torch.no_grad():
                    model_output = self.model(**encoded_input)
                    
                    # 对于BGE模型，使用平均池化而不是CLS token
                    attention_mask = encoded_input['attention_mask']
                    token_embeddings = model_output.last_hidden_state
                    
                    # 执行平均池化 - 使用BGE官方推荐的方式
                    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
                    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
                    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                    sentence_embeddings = sum_embeddings / sum_mask
                    
                    # 确保嵌入向量是2D张量
                    if sentence_embeddings.dim() == 1:
                        sentence_embeddings = sentence_embeddings.unsqueeze(0)
                    
                    # BGE模型推荐的归一化方式
                    sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
                    embeddings = sentence_embeddings.cpu().numpy()
                
                return embeddings.tolist()
                
            except Exception as e:
                logger.error(f"Transformers嵌入向量获取失败: {e}")
        
        # 如果本地模型都失败，使用智普AI API
        logger.warning("本地BGE模型不可用，使用智普AI API")
        return self._get_zhipu_embeddings(texts)
    
    def _get_zhipu_embeddings(self, texts: List[str]) -> List[List[float]]:
        """获取智普AI嵌入向量（备用方案）"""
        url = f"{self.config.ZHIPU_BASE_URL}/embeddings"
        
        payload = {
            "model": "embedding-2",
            "input": texts
        }
        
        try:
            response = self.session.post(
                url, 
                json=payload, 
                timeout=self.config.TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            embeddings = [item["embedding"] for item in result["data"]]
            return embeddings
            
        except Exception as e:
            logger.error(f"智普AI嵌入向量获取失败: {e}")
            raise
    
    def batch_chat_completion(self, queries: List[str], system_prompt: str = "") -> List[Dict[str, Any]]:
        """批量聊天补全（用于并行处理）"""
        results = []
        for query in queries:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": query})
            
            result = self.chat_completion(messages)
            results.append(result)
        
        return results

# 全局服务实例
zhipu_service = ZhipuAIService()