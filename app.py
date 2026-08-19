import streamlit as st
from ai_manager import *
from streamlit_mic_recorder import mic_recorder

st.set_page_config(page_title="Quantum AI Pro", page_icon="⚛️", layout="wide")
st.title("⚛️ Quantum AI Pro")
st.caption("The All-in-One AI Studio: Chat, Voice, Music, Images")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 Chat", "🎤 Voice Studio", "🎵 Sound & Music", "🖼️ Generate", "💳 Billing"])

# TAB 1: NORMAL CHAT
with tab1:
    st.header("Chat with Quantum AI")
    #... normal chat code from before...

# TAB 2: VOICE STUDIO
with tab2:
    st.header("Voice Studio")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Text to Speech")
        text = st.text_area("Enter text")
        voice = st.selectbox("Voice", ["Rachel", "Adam", "Domi"])
        if st.button("Generate Voice"):
            audio = text_to_speech(text)
            st.audio(audio)
    
    with col2:
        st.subheader("2. Voice Changer")
        audio_in = mic_recorder("🎤 Record Your Voice")
        target_voice = st.selectbox("Change to Voice", ["Rachel", "Adam"])
        if audio_in and st.button("Change Voice"):
            new_audio = voice_changer(audio_in["bytes"], "21m00Tcm4TlvDq8ikWAM")
            st.audio(new_audio)

    st.subheader("3. Voice Isolator")
    noisy_audio = st.file_uploader("Upload audio with noise")
    if noisy_audio and st.button("Remove Noise"):
        clean = isolate_voice(noisy_audio.read())
        st.audio(clean)

# TAB 3: SOUND & MUSIC
with tab3:
    st.header("Sound Effects + Music")
    prompt = st.text_input("Describe sound: 'rain on roof', 'afrobeat drums'")
    if st.button("Generate Sound"):
        sound = generate_sound_effect(prompt)
        st.audio(sound)

# TAB 4: GENERATE
with tab4:
    st.header("Image & Video Generation")
    img_prompt = st.text_input("Describe image: 'Quantum AI robot mascot'")
    if st.button("Generate Image"):
        st.info("Connecting to Stable Diffusion... Coming next")

# TAB 5: BILLING
with tab5:
    st.header("Buy Credits")
    #... bank transfer + auto verify code from before...