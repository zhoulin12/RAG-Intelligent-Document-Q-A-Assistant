import os
import logging
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

@dataclass
class SystemConfig:
    """系统配置类"""
    
    # 数据目录
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")
    VECTOR_DB_DIR: str = os.path.join(DATA_DIR, "vector_db")
    DOCUMENT_DIR: str = os.path.join(DATA_DIR, "documents")
    CACHE_DIR: str = os.path.join(DATA_DIR, "cache")
    
    # 智普AI配置
    ZHIPU_API_KEY: str = os.getenv("ZHIPU_API_KEY", "")
    ZHIPU_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"
    
    # 模型配置
    EMBEDDING_MODEL_PATH: str = os.getenv(
        "EMBEDDING_MODEL_PATH", 
        "E:/kuakkkk/ai/models--BAAI--bge-large-zh-v1.5/snapshots/0cc67d9f159c4037e86efde28c42dadf6e3de7aa"
    )
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-large-zh-v1.5")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "glm-4")
    
    # 文档处理配置
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # 检索配置
    TOP_K: int = int(os.getenv("TOP_K", "3"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    
    # 性能配置
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
    TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG")
    LOG_FILE: str = os.path.join(DATA_DIR, "app.log")
    
    def __post_init__(self):
        """初始化后处理"""
        # 确保目录存在
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(self.VECTOR_DB_DIR, exist_ok=True)
        os.makedirs(self.DOCUMENT_DIR, exist_ok=True)
        os.makedirs(self.CACHE_DIR, exist_ok=True)
    
    @classmethod
    def validate_config(cls) -> bool:
        """验证配置是否有效"""
        if not cls.ZHIPU_API_KEY:
            raise ValueError("智普AI API密钥未设置，请在.env文件中设置ZHIPU_API_KEY")
        return True

# 全局配置实例
system_config = SystemConfig()