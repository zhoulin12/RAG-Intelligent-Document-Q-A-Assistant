from ZhipuLLM import ZhipuLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma, FAISS
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from operator import itemgetter



# RAG问答简单示例。
# llm = ZhipuLLM()
# outputParser = StrOutputParser()
# # 使用模型路径
# embeddings_path = "E:/kuakkkk/ai/models--BAAI--bge-large-zh-v1.5/snapshots/0cc67d9f159c4037e86efde28c42dadf6e3de7aa"
# embeddings = HuggingFaceEmbeddings(model_name=embeddings_path)

# vectorstores = FAISS.from_texts(["王泽在成都工作","周豪喜欢打篮球","王利喜欢看电影"], embedding=embeddings)
# retriever = vectorstores.as_retriever()

# template = """
# 已知以下信息:
# {context}

# 请根据以上信息，简要回答用户的问题。如果无法从中获取答案，请回复"无法从已知信息中获取答案"。

# 问题: {question}
# 回答问题请加上称呼: {name}
# """
# prompt = ChatPromptTemplate.from_template(template)

# # retriever = RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
# # chain = retriever | prompt | llm | outputParser
# # a = chain.invoke( "王泽在哪里工作？")
# # print(a)

# # # 完整链式
# # chain = (
# #     {"context": retriever, "question": RunnablePassthrough()}
# #     | prompt
# #     | llm
# #     | outputParser
# # )
# # a = chain.invoke( "王泽在哪里工作？")
# # print(a)

# # 加入额外变量
# chain = (
#     {"context": itemgetter("question") | retriever, 
#      "question": itemgetter("question"),
#      "name": itemgetter("name")}
#     | prompt
#     | llm
#     | outputParser
# )
# a = chain.invoke( {"question": "王泽在哪里工作？", "name":"主人"})
# print(a)










# 使用文档的RAG问答示例
from langchain_community.document_loaders import (
    PyPDFLoader,      # PDF文档
    Docx2txtLoader,        # Word文档
    UnstructuredHTMLLoader, # HTML网页
    WebBaseLoader,         # 网页内容
    CSVLoader,             # CSV文件
    TextLoader             # 纯文本文件
    # ... 更多加载器
)

llm = ZhipuLLM()
outputParser = StrOutputParser()

# # 定位文件
# loader = TextLoader("E:\kuakkkk\syy\sy.txt", encoding="utf-8")
# doc = loader.load()
# loader2 = TextLoader("E:\kuakkkk\syy\sy2.txt", encoding="utf-8")
# doc2 = loader2.load()

# # 加载并分割PDF文件
# loader3 = PyPDFLoader("E:/kuakkkk/syy/jy.pdf")
# doc3 = loader3.load_and_split()
# print(doc3)

# 批量加载文件夹中的所有文件
from langchain_community.document_loaders import DirectoryLoader

loader = DirectoryLoader("E:/kuakkkk/syy")
docs = loader.load()

# 使用模型路径
embeddings_path = "E:/kuakkkk/ai/models--BAAI--bge-large-zh-v1.5/snapshots/0cc67d9f159c4037e86efde28c42dadf6e3de7aa"
embeddings = HuggingFaceEmbeddings(model_name=embeddings_path)

# vectorstores = FAISS.from_documents(doc, doc2, embedding=embeddings)
vectorstores = FAISS.from_documents(docs, embedding=embeddings)

template = """
只根据以下已知信息，简要回答用户的问题。如果无法从中获取答案，请回复"无法从已知信息中获取答案"。
已知信息:
{context}
问题: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

# MMR（最大边际相关性）检索 。 #多样化结果
# retriever = vectorstores.as_retriever(
#     search_type="mmr", search_kwargs={"k": 1}
# )
# docs = retriever.get_relevant_documents("银行培训的内容主要是哪些？")

# 使用向量数据库作为检索器 # 严格过滤
# retriever = vectorstores.as_retriever(
#     search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.3}
# )
# docs = retriever.get_relevant_documents("安装CentOS过程是怎样的？")

# 创建检索器 - 使用简单的相似度搜索 # 常规使用
retriever = vectorstores.as_retriever(search_kwargs={"k": 5})
docs = retriever.get_relevant_documents("王泽是谁？")

setup_and_retrieval = RunnableParallel({
    "context": retriever,
    "question": RunnablePassthrough()
})


chain = (
    setup_and_retrieval
    | prompt
    | llm
    | outputParser
)
a = chain.invoke("王泽是谁？")
print(a)







