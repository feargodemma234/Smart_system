import streamlit as st
from ai_manager import get_ai_response
import datetime

st.set_page_config(page_title="Quantum AI", page_icon="⚛️", layout="wide")

st.title("⚛️ Quantum AI")
st.subheader("Text Intelligence - Powered by Groq")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model" not in st.session_state:
    st.session_state.model = "openai/gpt-oss-120b"

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # 1. MODEL SELECTOR
    st.session_state.model = st.selectbox(
        "Choose Model",
        ["openai/gpt-oss-120b"],
        index=0,
        help="gpt-oss-120b = best reasoning. 8b-instant = fastest"
    )
    
    # 2. FILE UPLOAD
    st.divider()
    st.header("📄 Upload File")
    uploaded_file = st.file_uploader("Upload PDF, TXT, or Image", type=["txt", "pdf", "png", "jpg", "jpeg"])
    
    if uploaded_file:
        file_content = uploaded_file.read().decode("utf-8", errors="ignore")
        st.success(f"Uploaded: {uploaded_file.name}")
        if st.button("Summarize File"):
            summary_prompt = f"Summarize this file content:\n\n{file_content[:8000]}" # limit to avoid token limit
            st.session_state.messages.append({"role": "user", "content": f"Summarize {uploaded_file.name}"})
            with st.spinner("Reading file..."):
                response = get_ai_response(summary_prompt, st.session_state.messages, st.session_state.model)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    st.divider()
    # 3. EXPORT + CLEAR
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    if st.session_state.messages:
        chat_export = "\n\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        st.download_button(
            "💾 Download Chat",
            data=chat_export,
            file_name=f"quantum_ai_chat_{datetime.date.today()}.txt",
            mime="text/plain"
        )

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Message Quantum AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        with st.spinner("Thinking..."):
            for chunk in get_ai_response(prompt, st.session_state.messages, st.session_state.model, stream=True):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})