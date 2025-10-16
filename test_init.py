#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试系统初始化脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_system import rag_system

def test_system_initialization():
    """测试系统初始化"""
    print("开始测试系统初始化...")
    
    # 尝试初始化系统
    result = rag_system.initialize()
    
    if result:
        print("✅ 系统初始化成功")
        
        # 获取系统状态
        status = rag_system.get_system_status()
        print("\n系统状态:")
        print(f"- 初始化状态: {status.get('initialized', False)}")
        print(f"- 文档数量: {status.get('document_count', 0)}")
        print(f"- 嵌入模型: {status['config']['embedding_model']}")
        print(f"- 语言模型: {status['config']['llm_model']}")
        
        # 检查向量数据库状态
        vector_db_status = status.get('vector_db', {})
        print(f"- 向量数据库初始化: {vector_db_status.get('initialized', False)}")
        
        return True
    else:
        print("❌ 系统初始化失败")
        return False

def test_embedding_service():
    """测试嵌入服务"""
    print("\n开始测试嵌入服务...")
    
    try:
        from zhipu_service import zhipu_service
        
        # 测试获取嵌入向量
        test_text = "这是一个测试文本"
        embeddings = zhipu_service.get_embeddings([test_text])
        
        if embeddings and len(embeddings) > 0:
            print(f"✅ 嵌入服务正常工作，向量维度: {len(embeddings[0])}")
            return True
        else:
            print("❌ 嵌入服务返回空向量")
            return False
            
    except Exception as e:
        print(f"❌ 嵌入服务测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("RAG系统初始化测试")
    print("=" * 50)
    
    # 测试系统初始化
    init_success = test_system_initialization()
    
    # 测试嵌入服务
    embedding_success = test_embedding_service()
    
    print("\n" + "=" * 50)
    if init_success and embedding_success:
        print("✅ 所有测试通过，系统应该可以正常工作")
    else:
        print("❌ 部分测试失败，请检查错误信息")
    print("=" * 50)