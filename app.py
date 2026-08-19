import streamlit as st
from ai_manager import get_ai_response, text_to_speech
from streamlit_mic_recorder import mic_recorder
import datetime

st.set_page_config(page_title="Quantum AI Voice", page_icon="⚛️", layout="wide")
st.title("⚛️ Quantum AI Voice Changer")
st.caption("Talk to it, and it talks back in AI voice")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("⚙️ Voice Settings")
    voice_lang = st.selectbox("AI Voice Language", ["en", "en-us", "en-uk", "yo", "ig", "ha"]) # Yoruba, Igbo, Hausa
    speak_reply = st.toggle("AI Talks Back", value=True)

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Display chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# MIC INPUT
st.write("### Press to Talk")
audio = mic_recorder(start_prompt="🎤 Hold to Talk", stop_prompt="Stop", key="recorder")

if audio:
    st.audio(audio["bytes"])

    # 1. Transcribe audio with Groq Whisper
    with st.spinner("Transcribing..."):
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio["bytes"]),
            model="whisper-large-v3",
            response_format="text"
        )
    prompt = transcription

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Get AI Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in get_ai_response(prompt, st.session_state.messages, stream=True):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 3. SPEAK BACK IN AI VOICE
    if speak_reply:
        with st.spinner("Generating voice..."):
            audio_fp = text_to_speech(full_response, lang=voice_lang)
            st.audio(audio_fp, format="audio/mp3", autoplay=True)