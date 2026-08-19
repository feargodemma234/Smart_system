import streamlit as st
import os
import sqlite3
import uuid
from ai_manager import get_ai_response, text_to_speech

# --- DATABASE SETUP ---
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (email TEXT PRIMARY KEY, is_pro INTEGER, opay_ref TEXT)''')
conn.commit()

def check_pro(email):
    c.execute("SELECT is_pro FROM users WHERE email=?", (email,))
    result = c.fetchone()
    return result[0] == 1 if result else False

def upgrade_user(email, ref):
    c.execute("INSERT OR REPLACE INTO users (email, is_pro, opay_ref) VALUES (?, 1,?)", (email, ref))
    conn.commit()

# --- PAGE CONFIG ---
st.set_page_config(page_title="Quantum AI Pro", page_icon="⚡", layout="wide")

# --- LOGIN ---
if "email" not in st.session_state:
    st.session_state.email = ""

if not st.session_state.email:
    st.title("⚡ Login to Quantum AI Pro")
    email = st.text_input("Enter your email to continue")
    if st.button("Continue"):
        if "@" in email:
            st.session_state.email = email
            st.rerun()
        else:
            st.error("Enter a valid email")
    st.stop()

is_pro = check_pro(st.session_state.email)

# --- SIDEBAR ---
st.sidebar.title("⚡ Quantum AI Pro")
st.sidebar.write(f"Logged in as: {st.session_state.email}")
if is_pro:
    st.sidebar.success("PRO MEMBER")
else:
    st.sidebar.warning("FREE PLAN")
page = st.sidebar.radio("Menu", ["Chat", "Voice Studio", "Billing"])

# --- CHAT LIMITS ---
if "msg_count" not in st.session_state:
    st.session_state.msg_count = 0

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am Quantum AI Pro. How can I help?"}]

# --- PAGE 1: CHAT ---
if page == "Chat":
    st.title("💬 Quantum AI Chat")
    
    if not is_pro and st.session_state.msg_count >= 50:
        st.error("Free limit reached. Upgrade to Pro for unlimited messages.")
        st.stop()
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Ask Quantum anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Quantum is thinking..."):
                response = get_ai_response(st.session_state.messages)
                st.write(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.msg_count += 1
        st.rerun()

# --- PAGE 2: VOICE STUDIO ---
elif page == "Voice Studio":
    st.title("🔊 Voice Studio")
    text_input = st.text_area("Enter text to speak:", height=200)
    accent = st.selectbox("Voice Accent", ["en-US - American", "en-GB - British", "en-NG - Nigerian"])
    
    if st.button("Generate Voice", type="primary"):
        lang = "en-ng" if "Nigerian" in accent else "en"
        audio = text_to_speech(text_input, lang)
        st.audio(audio)

# --- PAGE 3: BILLING + AUTO UPGRADE ---
elif page == "Billing":
    st.title("💳 Billing & Upgrade")
    
    if is_pro:
        st.success("You are already a Pro Member!")
    else:
        st.write("Unlock Pro Features")
        # Generate unique reference for this user
        payment_ref = f"quantum_{st.session_state.email}_{uuid.uuid4()}"
        
        # YOUR OPAY PAYMENT LINK WITH CALLBACK
        # IMPORTANT: Replace MERCHANT_ID and CALLBACK_URL
        opay_link = f"https://pay.opaycheckout.com/link/quantum-ai-pro?reference={payment_ref}&email={st.session_state.email}"
        
        st.link_button("Upgrade to Pro - ₦5,000/month with OPay", opay_link, type="primary")
        
        st.info("After payment, OPay will redirect you back here and you will be upgraded automatically.")
        
        # --- CHECK FOR PAYMENT CALLBACK ---
        query_params = st.query_params
        if "reference" in query_params and "status" in query_params:
            if query_params["status"] == "success":
                upgrade_user(st.session_state.email, query_params["reference"])
                st.success("Payment Successful! You are now PRO.")
                st.balloons()
                st.rerun()