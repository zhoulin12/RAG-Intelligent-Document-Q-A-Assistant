import streamlit as st
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.title("RAG智能文档问答助手")
st.write("这是一个测试页面，用于验证Streamlit是否正常运行。")

if st.button("测试"):
    st.write("测试成功！Streamlit正常运行。")