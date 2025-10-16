#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
调试向量数据库内容
"""

import os
import sys
from rag_system import rag_system
from zhipu_service import zhipu_service

def main():
    print("=== 向量数据库调试 ===")
    
    # 清空向量数据库
    print("清空向量数据库...")
    rag_system.vector_db.clear_collection()
    
    # 初始化系统
    print("正在初始化RAG系统...")
    if not rag_system.initialize():
        print("系统初始化失败！")
        return 1
    
    print("系统初始化成功！")
    
    # 添加测试文档
    print("\n添加测试文档...")
    test_file = "e:\\RagDocument\\test_document.md"
    result = rag_system.add_document(test_file)
    if result["success"]:
        print(f"成功添加文档: {result['message']}")
    else:
        print(f"添加文档失败: {result['error']}")
        return 1
    
    # 获取系统状态
    status = rag_system.get_system_status()
    print(f"当前文档数量: {status['document_count']}")
    
    # 获取向量数据库状态
    vector_db_status = status['vector_db']
    print(f"向量数据库状态: {vector_db_status}")
    
    # 尝试直接查询向量数据库
    print("\n尝试直接查询向量数据库...")
    try:
        # 获取所有文档
        all_docs = rag_system.vector_db.collection.get()
        print(f"数据库中文档数量: {len(all_docs['ids'])}")
        
        if all_docs['ids']:
            print("\n文档ID列表:")
            for i, doc_id in enumerate(all_docs['ids'][:5]):  # 只显示前5个
                print(f"  {i+1}. {doc_id}")
            
            print("\n文档内容示例:")
            for i, (doc_id, content, metadata) in enumerate(zip(
                all_docs['ids'][:3],  # 只显示前3个
                all_docs['documents'][:3],
                all_docs['metadatas'][:3]
            )):
                print(f"\n文档 {i+1}:")
                print(f"  ID: {doc_id}")
                print(f"  内容: {content[:100]}...")
                print(f"  元数据: {metadata}")
        
        # 尝试搜索
        print("\n尝试搜索测试...")
        
        # 先测试嵌入向量生成
        print("生成查询嵌入向量...")
        query_embedding = zhipu_service.get_embeddings(["RAG"])
        print(f"查询嵌入向量维度: {len(query_embedding[0]) if query_embedding else 0}")
        
        # 获取一个文档的嵌入向量进行比较
        if all_docs['ids']:
            doc_content = all_docs['documents'][0]
            print(f"文档内容: {doc_content[:50]}...")
            doc_embedding = zhipu_service.get_embeddings([doc_content])
            print(f"文档嵌入向量维度: {len(doc_embedding[0]) if doc_embedding else 0}")
            
            # 计算相似度
            if query_embedding and doc_embedding:
                import numpy as np
                query_vec = np.array(query_embedding[0])
                doc_vec = np.array(doc_embedding[0])
                
                # 计算余弦相似度
                dot_product = np.dot(query_vec, doc_vec)
                norm_query = np.linalg.norm(query_vec)
                norm_doc = np.linalg.norm(doc_vec)
                cosine_sim = dot_product / (norm_query * norm_doc)
                print(f"直接计算的余弦相似度: {cosine_sim}")
        
        search_results = rag_system.vector_db.search("RAG", top_k=3)
        print(f"搜索结果数量: {len(search_results)}")
        
        # 直接查询ChromaDB
        print("\n直接查询ChromaDB...")
        query_embedding = zhipu_service.get_embeddings(["RAG"])
        chroma_results = rag_system.vector_db.collection.query(
            query_embeddings=query_embedding,
            n_results=3
        )
        
        print(f"ChromaDB查询结果:")
        print(f"  文档数量: {len(chroma_results['documents'][0]) if chroma_results['documents'] else 0}")
        
        if chroma_results['documents'] and chroma_results['documents'][0]:
            for i, (doc, metadata, distance) in enumerate(zip(
                chroma_results['documents'][0],
                chroma_results['metadatas'][0],
                chroma_results['distances'][0]
            )):
                similarity = 1 - distance  # 转换为相似度分数
                print(f"\nChromaDB结果 {i+1}:")
                print(f"  距离: {distance}")
                print(f"  相似度: {similarity}")
                print(f"  是否超过阈值: {similarity >= rag_system.vector_db.config.SIMILARITY_THRESHOLD}")
                print(f"  内容: {doc[:50]}...")
        
        for i, result in enumerate(search_results):
            print(f"\n搜索结果 {i+1}:")
            print(f"  相似度: {result['similarity']}")
            print(f"  内容: {result['content'][:100]}...")
            print(f"  元数据: {result['metadata']}")
            
    except Exception as e:
        print(f"查询向量数据库失败: {e}")
        import traceback
        traceback.print_exc()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())