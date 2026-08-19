import streamlit as st
import os
from ai_manager import get_ai_response, text_to_speech

st.set_page_config(page_title="Quantum AI Pro", page_icon="⚡", layout="wide")

st.title("⚡ Quantum AI Pro")
st.caption("Your Free AI Voice Assistant")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Chat with Quantum")
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask Quantum anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_ai_response(prompt)
                st.write(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

with col2:
    st.subheader("🔊 Voice Generator")
    
    text_input = st.text_area("Enter text to speak:", height=150, placeholder="Type what you want Quantum to say...")
    
    if st.button("Generate Voice", type="primary", use_container_width=True):
        if text_input:
            with st.spinner("Generating voice..."):
                audio = text_to_speech(text_input)
                st.audio(audio)
                st.success("Voice generated!")
        else:
            st.warning("Please enter some text first")
    
    st.divider()
    st.info("**Note:** Using free Google TTS. No API limits.")

st.divider()
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()