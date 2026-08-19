import streamlit as st
st.login() # if using Streamlit 1.37+
# or build simple login with Supabase/Firebase
import streamlit as st
from ai_manager import get_ai_response

st.set_page_config(page_title="Quantum AI", page_icon="⚛️", layout="wide")

st.title("⚛️ Quantum AI")
st.subheader("Text Intelligence")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Message Quantum AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_ai_response(prompt, st.session_state.messages[:-1])
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})