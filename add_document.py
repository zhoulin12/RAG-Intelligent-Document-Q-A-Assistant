#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
直接添加文档到RAG系统的脚本
"""

import os
import sys
from rag_system import rag_system

def main():
    print("=== RAG系统文档添加脚本 ===")
    
    # 初始化系统
    print("正在初始化RAG系统...")
    if not rag_system.initialize():
        print("系统初始化失败！")
        return 1
    
    print("系统初始化成功！")
    
    # 获取系统状态
    status = rag_system.get_system_status()
    print(f"当前文档数量: {status['document_count']}")
    
    # 添加测试文档
    test_doc_path = os.path.join(os.path.dirname(__file__), "test_document.md")
    if os.path.exists(test_doc_path):
        print(f"正在添加文档: {test_doc_path}")
        result = rag_system.add_document(test_doc_path)
        
        if result["success"]:
            print("文档添加成功！")
            # 再次获取系统状态
            status = rag_system.get_system_status()
            print(f"更新后文档数量: {status['document_count']}")
        else:
            print(f"文档添加失败: {result['error']}")
    else:
        print(f"测试文档不存在: {test_doc_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())