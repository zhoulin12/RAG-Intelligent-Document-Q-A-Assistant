#!/usr/bin/env python3
"""
基于智普大模型的RAG智能文档问答助手 - 命令行版本
"""

import os
import sys
import argparse
from rag_system import rag_system
from config import system_config
from logger import get_logger

logger = get_logger(__name__)

def print_banner():
    """打印横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║          基于智普大模型的RAG智能文档问答助手               ║
    ║                                                              ║
    ║  技术特点:                                                   ║
    ║  - 智普AI集成: 使用智普GLM系列大模型                         ║
    ║  - 本地嵌入模型: 使用BGE-large-zh-v1.5中文嵌入模型           ║
    ║  - 智能检索: 基于语义相似度的文档检索                        ║
    ║  - 上下文感知: 基于文档上下文的智能问答                      ║
    ║  - 可追溯性: 提供答案来源和置信度                            ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_help():
    """打印帮助信息"""
    help_text = """
    命令帮助:
    
    add <文件路径>     - 添加文档到系统
    query <问题>       - 提问
    status             - 查看系统状态
    clear              - 清空所有文档
    help               - 显示帮助信息
    quit/exit          - 退出程序
    
    示例:
    > add ./documents/sample.pdf
    > query 这个文档的主要内容是什么？
    > status
    > clear
    > quit
    """
    print(help_text)

def handle_add_command(file_path):
    """处理添加文档命令"""
    if not file_path:
        print("❌ 错误: 请提供文件路径")
        return
    
    if not os.path.exists(file_path):
        print(f"❌ 错误: 文件不存在: {file_path}")
        return
    
    print(f"📄 正在处理文档: {os.path.basename(file_path)}")
    result = rag_system.add_document(file_path)
    
    if result["success"]:
        print(f"✅ {result['message']}")
    else:
        print(f"❌ 添加失败: {result['error']}")

def handle_query_command(question):
    """处理查询命令"""
    if not question:
        print("❌ 错误: 请提供问题")
        return
    
    print(f"🤔 正在思考: {question}")
    answer_data = rag_system.query(question)
    
    if answer_data.get("success", False):
        print(f"\n💡 答案: {answer_data['answer']}")
        
        if answer_data.get("confidence", 0) > 0:
            print(f"📊 置信度: {answer_data['confidence']:.2%}")
        
        if answer_data.get("sources"):
            print(f"\n📚 参考来源 ({len(answer_data['sources'])} 个):")
            for i, source in enumerate(answer_data["sources"]):
                print(f"  来源 {i+1} (相似度: {source['similarity']:.2f}): {source['metadata'].get('source', '未知')}")
    else:
        print(f"❌ 查询失败: {answer_data.get('error', '未知错误')}")

def handle_status_command():
    """处理状态命令"""
    status = rag_system.get_system_status()
    
    print("\n📊 系统状态:")
    print(f"  初始化状态: {'✅ 已初始化' if status['initialized'] else '❌ 未初始化'}")
    print(f"  文档数量: {status['document_count']}")
    
    if status.get("vector_db", {}).get("initialized"):
        print(f"  向量数据库: ✅ 已初始化")
        print(f"  集合名称: {status['vector_db']['collection_name']}")
    else:
        print(f"  向量数据库: ❌ 未初始化")
    
    print(f"\n⚙️ 配置信息:")
    print(f"  嵌入模型: {status['config']['embedding_model']}")
    print(f"  语言模型: {status['config']['llm_model']}")
    print(f"  文本块大小: {status['config']['chunk_size']} 字符")
    print(f"  相似度阈值: {status['config']['similarity_threshold']}")

def handle_clear_command():
    """处理清空命令"""
    print("⚠️ 确认清空所有文档? (y/N): ", end="")
    confirm = input().strip().lower()
    
    if confirm == 'y' or confirm == 'yes':
        result = rag_system.clear_documents()
        if result["success"]:
            print("✅ 所有文档已清空")
        else:
            print(f"❌ 清空失败: {result['error']}")
    else:
        print("操作已取消")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="基于智普大模型的RAG智能文档问答助手")
    parser.add_argument("--dev", action="store_true", help="开发模式")
    args = parser.parse_args()
    
    # 打印横幅
    print_banner()
    
    # 初始化系统
    print("🚀 正在初始化系统...")
    if not rag_system.initialize():
        print("❌ 系统初始化失败，请检查配置")
        sys.exit(1)
    
    print("✅ 系统初始化完成")
    
    # 显示系统状态
    handle_status_command()
    
    # 交互式循环
    print("\n💬 请输入命令 (输入 'help' 查看帮助):")
    
    while True:
        try:
            command = input("\n> ").strip()
            
            if not command:
                continue
            
            # 解析命令
            parts = command.split(maxsplit=1)
            cmd = parts[0].lower()
            args_part = parts[1] if len(parts) > 1 else ""
            
            # 处理命令
            if cmd in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
            elif cmd == 'help':
                print_help()
            elif cmd == 'add':
                handle_add_command(args_part)
            elif cmd == 'query':
                handle_query_command(args_part)
            elif cmd == 'status':
                handle_status_command()
            elif cmd == 'clear':
                handle_clear_command()
            else:
                print(f"❌ 未知命令: {cmd} (输入 'help' 查看帮助)")
        
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 错误: {str(e)}")

if __name__ == "__main__":
    main()