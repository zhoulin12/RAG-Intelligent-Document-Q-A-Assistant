# 贡献指南

感谢您对基于智普大模型的RAG智能文档问答助手项目的关注！

## 开发环境设置

1. 克隆项目
```bash
git clone <repository-url>
cd RagDocument
```

2. 创建虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，设置您的智普AI API密钥
```

## 代码规范

- 遵循PEP 8代码风格
- 使用类型提示
- 编写单元测试
- 添加适当的注释和文档字符串

## 提交流程

1. 创建功能分支
```bash
git checkout -b feature/your-feature-name
```

2. 提交更改
```bash
git commit -m "feat: 添加新功能描述"
```

3. 推送分支
```bash
git push origin feature/your-feature-name
```

4. 创建Pull Request

## 测试

运行测试套件：
```bash
python -m pytest tests/
```

## 问题报告

如果您发现bug或有功能建议，请创建issue并详细描述问题或需求。

## 许可证

本项目采用MIT许可证。