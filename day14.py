import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

# 设置网页标题和布局（顶格写）
st.set_page_config(page_title="企业智能客服", page_icon="💬", layout="wide")

# 1. 配置 API 客户端（顶格写）
client = OpenAI(
    aipa_key=st.secrets["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)

# 2. 把工具放到侧边栏（顶格写）
with st.sidebar:
    st.header("⚙️ 控制面板")  # 按1次Tab
    uploaded_file = st.file_uploader("上传企业介绍文件", type=["txt", "pdf"])  # 按1次Tab
    
    # 清空聊天记录的按钮（按1次Tab）
    if st.button("清空对话记忆"):
        st.session_state.messages = []
        st.rerun()

# 3. 主界面标题（顶格写）
st.title("💬 企业智能客服中心")

# 4. 初始化记忆盒子（顶格写）
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. 读取文件内容并显示（顶格写）
if uploaded_file is not None:
    file_content = ""
    if uploaded_file.name.endswith(".txt"):
        file_content = uploaded_file.read().decode("utf-8")
    elif uploaded_file.name.endswith(".pdf"):
        pdf_reader = PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            file_content += page.extract_text()
    
    st.success(f"✅ 文件已加载！共读取 {len(file_content)} 个字符。")

    # 6. 显示历史聊天记录
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 7. 用户输入框（放在页面底部）
    user_input = st.chat_input("请输入你想问的问题...")
    
    # 8. 核心逻辑
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
    # 如果没有上传文件，给个提示
    st.info("👈 请先在左侧“控制面板”上传您的企业介绍文件(TXT或PDF)。")