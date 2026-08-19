import streamlit as st
import sqlite3
import os
from groq import Groq
from pypdf import PdfReader
import requests
from io import BytesIO
from PIL import Image
import urllib.parse

DB_FILE = "users.db"

# --- DB SETUP ---
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (email TEXT PRIMARY KEY, password TEXT, is_pro INTEGER, chat_history TEXT)''')
for col in ["img_trials INTEGER DEFAULT 3", "pdf_trials INTEGER DEFAULT 3"]:
    try: c.execute(f"ALTER TABLE users ADD COLUMN {col}")
    except: pass
conn.commit()

def get_user(email): 
    return c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

def create_user(email, password): 
    c.execute("INSERT INTO users (email, password, is_pro, chat_history, img_trials, pdf_trials) VALUES (?,?,?,?,?,?)", 
              (email, password, 0, '', 3, 3))
    conn.commit()

def update_user(email, history, img, pdf, is_pro):
    c.execute("UPDATE users SET chat_history=?, img_trials=?, pdf_trials=?, is_pro=? WHERE email=?", 
              (history, img, pdf, is_pro, email))
    conn.commit()

# --- GROQ CLIENT ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def get_ai_response(messages):
    try:
        resp = client.chat.completions.create(
            model="openai/gpt-oss-120b", # CHATGPT MODEL FROM GROQ
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"AI Error: {e}. Check your GROQ_API_KEY in Secrets"

def generate_image(prompt):
    st.info("Generating image... 10-15s")
    try:
        # WORKING API FOR STREAMLIT CLOUD
        safe_prompt = urllib.parse.quote(prompt)
        url = f"https://api.a0.dev/assets/image?text={safe_prompt}&aspect=1:1&seed=42"
        response = requests.get(url, timeout=90)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except Exception as e:
        st.error(f"Image generation failed: {e}")
        st.write("Tip: Try a simpler prompt like 'a dog in space'")
        return None

# --- LOGIN PAGE ---
if 'logged_in' not in st.session_state:
    st.set_page_config(page_title="Quantum AI", layout="wide")
    st.title("⚡ Quantum AI")
    st.write("Free Chat + 3 Free Image + 3 Free PDF Trials")
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login / Sign Up", type="primary"):
        user = get_user(email)
        if user and user[1] == password:
            st.session_state.logged_in = True
            st.session_state.email = email
            st.session_state.is_pro = user[2]
            st.session_state.history = user[3].split("|||") if user[3] else []
            st.session_state.img_trials = user[4]
            st.session_state.pdf_trials = user[5]
            st.rerun()
        else:
            create_user(email, password)
            st.session_state.logged_in = True
            st.session_state.email = email
            st.session_state.is_pro = 0
            st.session_state.history = []
            st.session_state.img_trials = 3
            st.session_state.pdf_trials = 3
            st.rerun()

# --- MAIN APP ---
else:
    st.set_page_config(page_title="Quantum AI Pro", layout="wide")
    st.sidebar.title("⚡ Quantum AI Pro")
    
    if st.session_state.is_pro == 0:
        st.sidebar.metric("Image Trials Left", st.session_state.img_trials)
        st.sidebar.metric("PDF Trials Left", st.session_state.pdf_trials)
    else:
        st.sidebar.success("PRO USER - UNLIMITED")
    
    page = st.sidebar.radio("Navigation", ["💬 Chat", "🎨 Image Gen", "📄 PDF Chat", "💳 Billing"])
    
    if st.sidebar.button("Logout"):
        update_user(st.session_state.email, "|||".join(st.session_state.history), 
                    st.session_state.img_trials, st.session_state.pdf_trials, st.session_state.is_pro)
        st.session_state.clear()
        st.rerun()

    # 1. CHAT - FREE UNLIMITED
    if page == "💬 Chat":
        st.title("💬 Chat with AI")
        for msg in st.session_state.history:
            if msg.startswith("You:"): st.chat_message("user").write(msg[4:])
            else: st.chat_message("assistant").write(msg[3:])
        
        prompt = st.chat_input("Ask me anything...")
        if prompt:
            st.session_state.history.append(f"You: {prompt}")
            st.chat_message("user").write(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = get_ai_response([{"role":"user","content":prompt}])
                    st.write(response)
            st.session_state.history.append(f"AI: {response}")

    # 2. IMAGE GEN - 3 FREE TRIALS - FIXED
    elif page == "🎨 Image Gen":
        st.title("🎨 AI Image Generation")
        if st.session_state.is_pro == 0 and st.session_state.img_trials <= 0:
            st.error("You used all 3 free trials. Upgrade to Pro for unlimited.")
            st.link_button("Upgrade to Pro - ₦5000/month", "https://opay.ng/s/36QEa", type="primary")
        else:
            if st.session_state.is_pro == 0:
                st.warning(f"You have {st.session_state.img_trials} free generations left")
            prompt = st.text_input("Describe the image you want", placeholder="A futuristic city at night, 4k")
            if st.button("Generate Image", type="primary"):
                with st.spinner("Generating..."):
                    img = generate_image(prompt)
                    if img:
                        st.image(img, caption=prompt, use_column_width=True)
                        if st.session_state.is_pro == 0:
                            st.session_state.img_trials -= 1
                            st.rerun()

    # 3. PDF CHAT - 3 FREE TRIALS
    elif page == "📄 PDF Chat":
        st.title("📄 Chat with your PDF")
        if st.session_state.is_pro == 0 and st.session_state.pdf_trials <= 0:
            st.error("You used all 3 free trials. Upgrade to Pro for unlimited.")
            st.link_button("Upgrade to Pro - ₦5000/month", "https://opay.ng/s/36QEa", type="primary")
        else:
            if st.session_state.is_pro == 0:
                st.warning(f"You have {st.session_state.pdf_trials} free PDF chats left")
            pdf = st.file_uploader("Upload PDF", type="pdf")
            if pdf:
                with st.spinner("Reading PDF..."):
                    reader = PdfReader(pdf)
                    text = "".join([p.extract_text() for p in reader.pages])
                st.success(f"Loaded {len(reader.pages)} pages")
                q = st.text_input("Ask anything about this PDF")
                if q and st.button("Ask AI"):
                    with st.spinner("Thinking..."):
                        messages = [{"role":"user","content":f"Use this context to answer:\n{text[:8000]}\n\nQuestion: {q}"}]
                        st.write(get_ai_response(messages))
                    if st.session_state.is_pro == 0:
                        st.session_state.pdf_trials -= 1
                        st.rerun()

    # 4. BILLING
    elif page == "💳 Billing":
        st.title("💳 Upgrade to Pro")
        if st.session_state.is_pro:
            st.success("You are Pro! Unlimited Images + PDFs + Priority")
        else:
            st.info("Get Unlimited Access")
            st.write("**₦5000 / month**")
            st.link_button("Upgrade with OPay", "https://opay.ng/s/36QEa", type="primary")