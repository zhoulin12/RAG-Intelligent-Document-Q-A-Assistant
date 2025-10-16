import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from document_processor import DocumentProcessor
from config import system_config

class TestDocumentProcessor(unittest.TestCase):
    """文档处理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.processor = DocumentProcessor()
        self.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        
        # 确保测试数据目录存在
        os.makedirs(self.test_data_dir, exist_ok=True)
        
        # 创建测试文本文件
        self.test_txt_path = os.path.join(self.test_data_dir, 'test.txt')
        with open(self.test_txt_path, 'w', encoding='utf-8') as f:
            f.write("这是一个测试文档。\n包含多行内容。\n用于测试文档处理功能。")
    
    def tearDown(self):
        """测试后清理"""
        # 删除测试文件
        if os.path.exists(self.test_txt_path):
            os.remove(self.test_txt_path)
    
    def test_load_text_file(self):
        """测试加载文本文件"""
        text = self.processor.load_document(self.test_txt_path)
        self.assertIn("这是一个测试文档", text)
        self.assertIn("包含多行内容", text)
    
    def test_chunk_document(self):
        """测试文档分块"""
        text = "这是一个测试文档。用于测试文档分块功能。分块应该按照指定大小进行。"
        chunks = self.processor.chunk_document(text)
        
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)
        
        for chunk in chunks:
            self.assertIn("content", chunk)
            self.assertIn("id", chunk)
    
    def test_process_document(self):
        """测试完整文档处理流程"""
        result = self.processor.process_document(self.test_txt_path)
        
        self.assertTrue(result["success"])
        self.assertIn("chunks", result)
        self.assertIn("metadata", result)
        self.assertGreater(len(result["chunks"]), 0)

if __name__ == '__main__':
    unittest.main()