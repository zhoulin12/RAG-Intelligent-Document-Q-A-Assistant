import streamlit as st
import os
import tempfile
from rag_system import rag_system
from config import system_config

# 页面配置
st.set_page_config(
    page_title="基于智普大模型的RAG智能文档问答助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .source-card {
        background-color: #f9f9f9;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 初始化系统
@st.cache_resource
def init_rag_system():
    """初始化RAG系统"""
    if rag_system.initialize():
        return rag_system
    else:
        st.error("系统初始化失败，请检查配置")
        return None

# 在应用启动时初始化系统
if "system_initialized" not in st.session_state:
    st.session_state.system_initialized = False
    st.session_state.rag_system = None

if not st.session_state.system_initialized:
    with st.spinner("正在初始化RAG系统..."):
        st.session_state.rag_system = init_rag_system()
        if st.session_state.rag_system:
            st.session_state.system_initialized = True
            st.success("RAG系统初始化成功！")
        else:
            st.error("RAG系统初始化失败，请检查配置")

# 使用已初始化的系统
if st.session_state.system_initialized:
    rag_system = st.session_state.rag_system

# 侧边栏
with st.sidebar:
    st.markdown('<div class="main-header">🤖 RAG助手</div>', unsafe_allow_html=True)
    
    # 文档上传区域
    st.markdown("### 📄 文档管理")
    uploaded_file = st.file_uploader(
        "上传文档",
        type=['pdf', 'docx', 'txt', 'md'],
        help="支持PDF、Word、文本文件"
    )
    
    if uploaded_file is not None:
        # 保存上传的文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        st.info(f"文件 '{uploaded_file.name}' 已上传，请点击下方按钮确认添加到系统")
        
        # 添加确认按钮
        if st.button(f"确认添加文档: {uploaded_file.name}", type="primary"):
            # 处理文档
            with st.spinner("正在处理文档..."):
                result = rag_system.add_document(tmp_file_path)
                
                if result["success"]:
                    st.success(result["message"])
                    # 刷新系统状态
                    st.rerun()
                else:
                    st.error(result["error"])
            
            # 清理临时文件
            os.unlink(tmp_file_path)
    
    # 系统状态
    st.markdown("---")
    st.markdown("### ℹ️ 系统状态")
    if st.button("刷新系统状态"):
        system_status = rag_system.get_system_status()
        st.json(system_status)
    
    # 显示文档列表
    system_status = rag_system.get_system_status()
    if system_status.get("document_count", 0) > 0:
        st.markdown(f"**已添加文档数量**: {system_status.get('document_count', 0)}")
        
        # 获取文档来源
        try:
            # 尝试获取向量数据库中的文档信息
            vector_db_status = system_status.get("vector_db", {})
            if vector_db_status.get("collection_exists", False):
                st.success("✅ 向量数据库中有文档")
            else:
                st.warning("⚠️ 向量数据库中无文档")
        except Exception as e:
            st.error(f"获取文档信息失败: {e}")
    else:
        st.warning("⚠️ 系统中暂无文档，请上传文档后点击确认添加")
    
    # 清空文档
    st.markdown("---")
    if st.button("清空所有文档", type="secondary"):
        if st.session_state.get('confirm_clear', False):
            result = rag_system.clear_documents()
            if result["success"]:
                st.success("所有文档已清空")
            else:
                st.error(f"清空失败: {result['error']}")
            st.session_state.confirm_clear = False
        else:
            st.session_state.confirm_clear = True
            st.warning("再次点击确认清空所有文档")

# 主界面
st.markdown('<div class="main-header">基于智普大模型的RAG智能文档问答助手</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">基于检索增强生成技术的智能问答系统</div>', unsafe_allow_html=True)

# 只有在系统初始化后才显示系统概览
if st.session_state.get("system_initialized", False):
    # 获取系统状态
    system_status = rag_system.get_system_status()

    # 显示系统概览
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("文档数量", system_status.get("document_count", 0))
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("嵌入模型", system_status["config"]["embedding_model"].split("/")[-1])
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("语言模型", system_status["config"]["llm_model"])
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("系统正在初始化中，请稍候...")

# 问答区域
st.markdown("## 💬 智能问答")

# 只有在系统初始化且有文档时才允许提问
if st.session_state.get("system_initialized", False):
    system_status = rag_system.get_system_status()
    
    if system_status.get("document_count", 0) > 0:
        question = st.text_input(
            "请输入您的问题:",
            placeholder="例如：这个文档的主要内容是什么？",
            key="question_input"
        )

        if question:
            with st.spinner("正在思考..."):
                answer_data = rag_system.query(question)
            
            # 显示答案
            st.markdown("### 💡 答案")
            st.write(answer_data["answer"])
            
            # 显示置信度
            if answer_data.get("confidence", 0) > 0:
                st.metric("回答置信度", f"{answer_data['confidence']:.2%}")
            
            # 显示来源信息
            if answer_data.get("sources"):
                st.markdown("### 📚 参考来源")
                
                for i, source in enumerate(answer_data["sources"]):
                    with st.expander(f"来源 {i+1} (相似度: {source['similarity']:.2f})"):
                        st.markdown(f"**文件名:** {source['metadata'].get('source', '未知')}")
                        st.markdown(f"**文件类型:** {source['metadata'].get('file_type', '未知')}")
                        st.markdown(f"**块大小:** {source['metadata'].get('chunk_size', 0)} 字符")
                        st.markdown("**内容:**")
                        st.write(source["content"])
    else:
        st.warning("系统中暂无文档，请先在左侧上传文档后再提问")
else:
    st.warning("系统正在初始化中，请稍候...")

# 使用说明
with st.expander("📖 使用说明"):
    st.markdown("""
    ## 如何使用RAG问答助手
    
    ### 1. 上传文档
    - 在左侧边栏上传您的PDF、Word或文本文件
    - 系统会自动处理文档并提取内容
    
    ### 2. 提问
    - 在上方输入框中输入您的问题
    - 系统会基于文档内容生成智能答案
    
    ### 3. 查看答案和来源
    - 答案会显示在主界面
    - 可以查看答案的置信度和参考来源
    
    ## 技术特点
    
    - **智普AI集成**: 使用智普GLM系列大模型
    - **本地嵌入模型**: 使用BGE-large-zh-v1.5中文嵌入模型
    - **智能检索**: 基于语义相似度的文档检索
    - **上下文感知**: 基于文档上下文的智能问答
    - **可追溯性**: 提供答案来源和置信度
    
    ## 支持的文件格式
    
    - PDF文档 (.pdf)
    - Word文档 (.docx)
    - 文本文件 (.txt)
    - Markdown文件 (.md)
    
    ## 系统配置
    
    当前系统配置:
    - **嵌入模型**: BAAI/bge-large-zh-v1.5
    - **语言模型**: GLM-4
    - **文本块大小**: 1000 字符
    - **相似度阈值**: 0.7
    """)

# 页脚
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #888;">基于智普大模型的RAG智能文档问答助手 © 2024</div>',
    unsafe_allow_html=True
)