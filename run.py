#!/usr/bin/env python3
"""
基于智普大模型的RAG智能文档问答助手 - 启动脚本
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        sys.exit(1)

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import streamlit
        import langchain
        import chromadb
        import sentence_transformers
        import requests
        return True
    except ImportError as e:
        print(f"缺少依赖: {e}")
        print("请运行 'pip install -r requirements.txt' 安装依赖")
        return False

def check_env_file():
    """检查环境配置文件"""
    env_file = Path(".env")
    if not env_file.exists():
        print("警告: .env文件不存在，将从.env.example复制")
        if Path(".env.example").exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("已创建.env文件，请编辑并设置ZHIPU_API_KEY")
        else:
            print("错误: .env.example文件不存在")
            return False
    
    # 检查API密钥是否设置
    with open(".env", "r") as f:
        content = f.read()
        if "your_zhipu_api_key_here" in content:
            print("警告: 请在.env文件中设置您的智普AI API密钥")
            return False
    
    return True

def run_web_app():
    """运行Web应用"""
    print("启动Web应用...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "web_app.py"])

def run_cli_app():
    """运行命令行应用"""
    print("启动命令行应用...")
    subprocess.run([sys.executable, "main.py"])

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="基于智普大模型的RAG智能文档问答助手启动脚本")
    parser.add_argument("--mode", choices=["web", "cli"], default="web", help="选择运行模式 (默认: web)")
    parser.add_argument("--skip-checks", action="store_true", help="跳过环境检查")
    
    args = parser.parse_args()
    
    # 检查Python版本
    check_python_version()
    
    # 检查依赖和环境
    if not args.skip_checks:
        if not check_dependencies():
            sys.exit(1)
        
        if not check_env_file():
            sys.exit(1)
    
    # 根据模式启动应用
    if args.mode == "web":
        run_web_app()
    else:
        run_cli_app()

if __name__ == "__main__":
    main()