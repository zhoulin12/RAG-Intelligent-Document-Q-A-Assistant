# 项目变更日志

## [1.0.0] - 2024-06-01

### 新增
- 基于智普大模型的RAG智能文档问答助手初始版本
- 支持PDF、Word、文本和Markdown文档处理
- 集成本地BGE-large-zh-v1.5嵌入模型
- 使用ChromaDB向量数据库存储文档向量
- 提供Web界面和命令行界面两种交互方式
- 完整的测试套件和文档

### 技术栈
- Python 3.8+
- LangChain
- ChromaDB
- 智普AI API
- Sentence Transformers
- Streamlit (Web界面)

### 核心功能
- 文档上传与处理
- 向量化存储
- 智能问答
- 来源追踪
- 系统状态监控