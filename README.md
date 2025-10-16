# 基于智普大模型的RAG智能文档问答助手

## 📋 项目简介

本项目是一个基于**检索增强生成（RAG）**技术的智能文档问答助手，专门集成**智普AI大模型**作为核心语言模型，并使用**本地BGE-large-zh-v1.5中文嵌入模型**进行文档向量化。系统能够处理多种格式的文档，通过智能检索和语义理解，为用户提供准确、有依据的问答服务。

## 🌟 核心特性

- 🔗 **智普AI集成**：深度集成智普GLM系列大模型
- 🧠 **本地嵌入模型**：使用BGE-large-zh-v1.5中文嵌入模型，提高中文理解能力
- 📄 **多格式支持**：PDF、Word、TXT、Markdown等文档格式
- 🔍 **智能检索**：基于语义相似度的文档检索
- 💬 **上下文感知**：基于文档上下文的智能问答
- 📊 **可追溯性**：答案来源和置信度展示
- 🌐 **多界面支持**：Web界面和命令行两种使用方式

## 🏗️ 技术架构

```
用户界面层 (UI Layer)
    ├── Web界面 (Streamlit)
    └── 命令行界面 (CLI)
        ↓
应用服务层 (Application Layer)
    ├── RAG系统主控制器
    ├── 文档处理引擎
    ├── 向量数据库管理器
    └── 问答引擎
        ↓
数据存储层 (Data Layer)
    ├── 向量数据库 (ChromaDB)
    └── 本地文件存储
        ↓
AI服务层 (AI Service Layer)
    ├── 智普AI大模型 API
    └── 本地BGE嵌入模型
```

## 📁 项目文件结构

```
RagDocument/
├── 📄 config.py                    # 系统配置
├── 📄 logger.py                    # 日志工具
├── 📄 zhipu_service.py             # 智普AI服务封装
├── 📄 document_processor.py        # 文档处理器
├── 📄 vector_db.py                 # 向量数据库管理
├── 📄 qa_engine.py                 # 问答引擎
├── 📄 rag_system.py                # RAG系统主控制器
├── 📄 main.py                      # 命令行主程序
├── 📄 web_app.py                   # Streamlit Web应用
├── 📄 requirements.txt             # Python依赖
├── 📄 setup.bat                    # 环境设置脚本
├── 📄 .env.example                 # 环境变量示例
└── 📄 README.md                    # 项目说明
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 运行设置脚本
.\setup.bat

# 或手动设置
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置环境变量

1. 复制环境变量示例文件：
   ```bash
   copy .env.example .env
   ```

2. 编辑 `.env` 文件，设置智普AI API密钥：
   ```
   ZHIPU_API_KEY=your_zhipu_api_key_here
   ```

3. 确认嵌入模型路径（已预设为您提供的路径）：
   ```
   EMBEDDING_MODEL_PATH=E:/kuakkkk/ai/models--BAAI--bge-large-zh-v1.5/snapshots/0cc67d9f159c4037e86efde28c42dadf6e3de7aa
   ```

### 3. 获取智普AI API密钥

1. 访问[智普AI开放平台](https://open.bigmodel.cn/)
2. 注册账号并完成实名认证
3. 在控制台创建API密钥
4. 将API密钥配置到 `.env` 文件中

### 4. 启动系统

**方式一：Web界面（推荐）**
```bash
streamlit run web_app.py
```

**方式二：命令行界面**
```bash
python main.py
```

## 💻 使用指南

### Web界面使用

1. 启动Web界面后，在浏览器中打开显示的URL（通常是 http://localhost:8501）
2. 在左侧边栏上传您的文档（支持PDF、Word、TXT、Markdown）
3. 在主界面输入您的问题
4. 查看答案和参考来源

### 命令行界面使用

命令行界面支持以下命令：

```
add <文件路径>     - 添加文档到系统
query <问题>       - 提问
status             - 查看系统状态
clear              - 清空所有文档
help               - 显示帮助信息
quit/exit          - 退出程序
```

示例：
```
> add ./documents/sample.pdf
> query 这个文档的主要内容是什么？
> status
> clear
> quit
```

## 🔧 技术细节

### 智普AI集成

系统使用智普AI的GLM系列大模型作为语言模型，支持：
- GLM-4：最新一代大模型，性能优异
- GLM-3-turbo：高速响应版本
- 自定义参数：温度、最大令牌数、top_p等

### 本地BGE嵌入模型

系统使用BGE-large-zh-v1.5中文嵌入模型进行文档向量化：
- 模型路径：`E:/kuakkkk/ai/models--BAAI--bge-large-zh-v1.5/snapshots/0cc67d9f159c4037e86efde28c42dadf6e3de7aa`
- 优势：本地部署，无需API调用，中文理解能力强

### 向量数据库

使用ChromaDB作为向量数据库：
- 支持余弦相似度计算
- 本地存储，数据安全
- 高效的相似度搜索

### 文档处理

支持多种文档格式：
- PDF：使用PyPDF2库
- Word：使用python-docx库
- 文本/Markdown：原生支持

## 📊 性能优化

### 1. 向量检索优化
- 使用分层导航小世界图（HNSW）索引
- 实现近似最近邻搜索（ANN）
- 添加查询缓存机制

### 2. 大模型调用优化
- 实现请求批处理
- 添加重试机制和熔断器
- 使用流式响应减少等待时间

### 3. 内存管理优化
- 实现文档分块缓存
- 添加内存使用监控
- 支持增量更新向量数据库

## 🔍 扩展功能规划

### 短期扩展（1-2周）
- [ ] 支持更多文档格式（PPT、Excel等）
- [ ] 添加用户会话管理
- [ ] 实现文档预览功能

### 中期扩展（1-2月）
- [ ] 支持多轮对话上下文
- [ ] 添加文档摘要生成
- [ ] 实现知识图谱集成

### 长期扩展（3-6月）
- [ ] 支持多模态文档（图片、音频）
- [ ] 添加自定义模型微调
- [ ] 实现分布式部署

## ❓ 常见问题

### Q: 如何更换嵌入模型？
A: 修改 `.env` 文件中的 `EMBEDDING_MODEL_PATH` 和 `EMBEDDING_MODEL_NAME` 配置。

### Q: 如何调整文档分块大小？
A: 修改 `.env` 文件中的 `CHUNK_SIZE` 和 `CHUNK_OVERLAP` 配置。

### Q: 如何调整相似度阈值？
A: 修改 `.env` 文件中的 `SIMILARITY_THRESHOLD` 配置（0-1之间的值）。

### Q: 系统支持哪些智普AI模型？
A: 目前支持GLM-4、GLM-3-turbo等模型，可在 `.env` 文件中的 `LLM_MODEL` 配置。

## 📝 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 集成智普AI大模型
- 支持本地BGE嵌入模型
- 实现基本文档问答功能

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进本项目！

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🙏 致谢

- [智普AI](https://open.bigmodel.cn/) - 提供强大的大语言模型API
- [BGE](https://github.com/FlagOpen/FlagEmbedding) - 优秀的中文嵌入模型
- [LangChain](https://github.com/langchain-ai/langchain) - LLM应用开发框架
- [ChromaDB](https://github.com/chroma-core/chroma) - 开源向量数据库