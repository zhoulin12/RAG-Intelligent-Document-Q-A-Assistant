#!/usr/bin/env python3
"""
快速安装脚本 - 只安装必要的依赖以运行基本功能
"""

import subprocess
import sys
import os

def run_command(command):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def install_basic_deps():
    """安装基础依赖"""
    print("正在安装基础依赖...")
    
    # 基础依赖列表
    basic_deps = [
        "streamlit",
        "python-dotenv",
        "requests",
        "PyPDF2",
        "sentence-transformers",
        "chromadb",
        "langchain"
    ]
    
    for dep in basic_deps:
        print(f"安装 {dep}...")
        success, output = run_command(f"{sys.executable} -m pip install {dep}")
        if not success:
            print(f"安装 {dep} 失败: {output}")
        else:
            print(f"成功安装 {dep}")

if __name__ == "__main__":
    # 检查是否在虚拟环境中
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("警告: 没有在虚拟环境中运行")
    
    install_basic_deps()
    print("基础依赖安装完成!")