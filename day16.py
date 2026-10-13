import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
from docx import Document  # 新增：读取Word文档的工具

st.set_page_config(page_title="企业智能客服", page_icon="💬", layout="wide")

client = OpenAI(
    api_key=st.secrets["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)

with st.sidebar:
    st.header("⚙️ 控制面板")
    uploaded_file = st.file_uploader("上传企业介绍文件", type=["txt", "pdf", "docx"])  # 这里加了docx
    
    if st.button("清空对话记忆"):
        st.session_state.messages = []
        st.rerun()

st.title("💬 企业智能客服中心")

if "messages" not in st.session_state:
    st.session_state.messages = []

if uploaded_file is not None:
    file_content = ""
    # 1. 读取 TXT 文件
    if uploaded_file.name.endswith(".txt"):
        file_content = uploaded_file.read().decode("utf-8")
    # 2. 读取 PDF 文件
    elif uploaded_file.name.endswith(".pdf"):
        pdf_reader = PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            file_content += page.extract_text()
    # 3. 新增：读取 Word (docx) 文件
    elif uploaded_file.name.endswith(".docx"):
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            file_content += para.text + "\n"
    
    st.success(f"✅ 文件已加载！共读取 {len(file_content)} 个字符。")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    user_input = st.chat_input("请输入你想问的问题...")
    
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("assistant"):
            with st.spinner("AI 正在翻阅文件思考中..."):
                messages_to_send = [
                    {"role": "system", "content": f"你是一个企业客服，请严格根据以下资料回答用户问题：\n{file_content}"},
                    *st.session_state.messages
                ]
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages_to_send
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
else:
    st.info("👈 请先在左侧“控制面板”上传您的企业介绍文件(TXT、PDF或Word)。")