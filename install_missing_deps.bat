@echo off
echo 正在安装缺失的依赖...

cd /d e:\RagDocument
call .venv\Scripts\activate

echo 安装markdown...
pip install markdown

echo 安装chromadb...
pip install chromadb

echo 安装sentence-transformers...
pip install sentence-transformers

echo 安装其他可能缺失的依赖...
pip install unstructured

echo 依赖安装完成！
echo 现在您可以运行以下命令启动应用：
echo python -m streamlit run web_app.py --server.port 8501

pause