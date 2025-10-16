#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试RAG系统问答功能
"""

import os
import sys
from rag_system import rag_system

def main():
    print("=== RAG系统问答测试 ===")
    
    # 初始化系统
    print("正在初始化RAG系统...")
    if not rag_system.initialize():
        print("系统初始化失败！")
        return 1
    
    print("系统初始化成功！")
    
    # 获取系统状态
    status = rag_system.get_system_status()
    print(f"当前文档数量: {status['document_count']}")
    
    if status['document_count'] == 0:
        print("系统中没有文档，请先添加文档！")
        return 1
    
    # 测试问答
    test_questions = [
        "什么是RAG？",
        "RAG系统的工作原理是什么？",
        "RAG系统有哪些优势？",
        "RAG系统可以应用在哪些场景？"
    ]
    
    for question in test_questions:
        print(f"\n问题: {question}")
        print("正在思考...")
        
        result = rag_system.query(question)
        
        if result.get("success", False):
            print(f"答案: {result['answer']}")
            if result.get("confidence", 0) > 0:
                print(f"置信度: {result['confidence']:.2%}")
            
            if result.get("sources"):
                print(f"参考来源数量: {len(result['sources'])}")
        else:
            print(f"回答失败: {result.get('answer', '未知错误')}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())