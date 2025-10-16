import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vector_db import VectorDBManager
from config import system_config

class TestVectorDBManager(unittest.TestCase):
    """向量数据库管理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 使用临时目录进行测试
        self.test_db_dir = os.path.join(os.path.dirname(__file__), 'test_vector_db')
        os.makedirs(self.test_db_dir, exist_ok=True)
        
        # 修改配置使用测试目录
        self.original_vector_db_dir = system_config.VECTOR_DB_DIR
        system_config.VECTOR_DB_DIR = self.test_db_dir
        
        self.vector_db = VectorDBManager()
    
    def tearDown(self):
        """测试后清理"""
        # 恢复原始配置
        system_config.VECTOR_DB_DIR = self.original_vector_db_dir
        
        # 删除测试目录
        import shutil
        if os.path.exists(self.test_db_dir):
            shutil.rmtree(self.test_db_dir)
    
    def test_initialize(self):
        """测试初始化"""
        result = self.vector_db.initialize()
        self.assertTrue(result)
        self.assertTrue(self.vector_db._initialized)
    
    @patch('vector_db.zhipu_service')
    def test_add_documents(self, mock_zhipu_service):
        """测试添加文档"""
        # 模拟嵌入向量
        mock_zhipu_service.get_embeddings.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        
        # 初始化向量数据库
        self.vector_db.initialize()
        
        # 准备测试数据
        documents = [
            {"id": "doc1", "content": "这是第一个文档", "metadata": {"source": "test1.txt"}},
            {"id": "doc2", "content": "这是第二个文档", "metadata": {"source": "test2.txt"}}
        ]
        
        # 添加文档
        result = self.vector_db.add_documents(documents)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 2)
    
    @patch('vector_db.zhipu_service')
    def test_search(self, mock_zhipu_service):
        """测试搜索"""
        # 模拟嵌入向量
        mock_zhipu_service.get_embeddings.return_value = [[0.1, 0.2, 0.3]]
        
        # 初始化向量数据库
        self.vector_db.initialize()
        
        # 添加测试文档
        documents = [
            {"id": "doc1", "content": "这是关于人工智能的文档", "metadata": {"source": "ai.txt"}}
        ]
        self.vector_db.add_documents(documents)
        
        # 搜索
        results = self.vector_db.search("人工智能")
        
        self.assertIsInstance(results, list)

if __name__ == '__main__':
    unittest.main()