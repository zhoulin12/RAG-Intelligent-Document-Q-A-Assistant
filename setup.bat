@echo off
echo 正在设置基于智普大模型的RAG智能文档问答助手环境...

REM 创建虚拟环境
if not exist ".venv" (
    echo 创建虚拟环境...
    python -m venv .venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call .venv\Scripts\activate.bat

REM 升级pip
echo 升级pip...
python -m pip install --upgrade pip

REM 安装依赖
echo 安装依赖包...
pip install -r requirements.txt

REM 创建数据目录
if not exist "data" (
    mkdir data
)

REM 复制环境配置文件
if not exist ".env" (
    echo 创建环境配置文件...
    copy .env.example .env
    echo.
    echo ⚠️  请编辑 .env 文件，设置您的智普AI API密钥:
    echo    ZHIPU_API_KEY=your_zhipu_api_key_here
    echo.
)

echo.
echo ✅ 环境设置完成！
echo.
echo 使用说明:
echo 1. 编辑 .env 文件，设置智普AI API密钥
echo 2. 运行: python main.py (命令行版本)
echo 3. 运行: streamlit run web_app.py (Web界面版本)
echo.
echo 注意: 系统将使用您提供的本地BGE嵌入模型:
echo   E:/kuakkkk/ai/models--BAAI--bge-large-zh-v1.5/snapshots/0cc67d9f159c4037e86efde28c42dadf6e3de7aa
echo.
pause