import streamlit as st
import sqlite3
import os
from groq import Groq
from pypdf import PdfReader
import requests
from io import BytesIO
from PIL import Image

DB_FILE = "users.db"

# --- DB SETUP THAT NEVER BREAKS ---
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

# 1. Create base table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (email TEXT PRIMARY KEY, password TEXT, is_pro INTEGER, chat_history TEXT)''')

# 2. Add new columns if they don't exist. This fixes the error
try:
    c.execute("ALTER TABLE users ADD COLUMN img_trials INTEGER DEFAULT 3")
except sqlite3.OperationalError:
    pass # Column already exists

try:
    c.execute("ALTER TABLE users ADD COLUMN pdf_trials INTEGER DEFAULT 3")
except sqlite3.OperationalError:
    pass # Column already exists

conn.commit()

def get_user(email): 
    return c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

def create_user(email, password): 
    # Use column names so order doesn't matter
    c.execute("INSERT INTO users (email, password, is_pro, chat_history, img_trials, pdf_trials) VALUES (?,?,?,?,?,?)", 
              (email, password, 0, '', 3, 3))
    conn.commit()

def update_user(email, history, img, pdf, is_pro):
    c.execute("UPDATE users SET chat_history=?, img_trials=?, pdf_trials=?, is_pro=? WHERE email=?", 
              (history, img, pdf, is_pro, email))
    conn.commit()

# --- GROQ + IMAGE ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
def get_ai_response(messages):
    resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages)
    return resp.choices[0].message.content

def generate_image(prompt):
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

# --- LOGIN ---
if 'logged_in' not in st.session_state:
    st.title("Quantum AI")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login / Sign Up"):
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
    st.sidebar.title("Quantum AI Pro")
    if st.session_state.is_pro == 0:
        st.sidebar.write(f"Image: {st.session_state.img_trials} | PDF: {st.session_state.pdf_trials}")
    else:
        st.sidebar.success("PRO USER")
    page = st.sidebar.radio("Go to", ["Chat", "Image Gen", "PDF Chat", "Billing"])
    
    if st.sidebar.button("Logout"):
        update_user(st.session_state.email, "|||".join(st.session_state.history), 
                    st.session_state.img_trials, st.session_state.pdf_trials, st.session_state.is_pro)
        st.session_state.clear()
        st.rerun()

    # 1. CHAT - FREE UNLIMITED
    if page == "Chat":
        st.title("💬 Chat")
        for msg in st.session_state.history:
            st.write(msg)
        prompt = st.chat_input("Ask me anything...")
        if prompt:
            st.session_state.history.append(f"You: {prompt}")
            messages = [{"role":"user","content":prompt}]
            response = get_ai_response(messages)
            st.session_state.history.append(f"AI: {response}")
            st.rerun()

    # 2. IMAGE GEN - 3 FREE TRIALS
    elif page == "Image Gen":
        st.title("🎨 Image Generation")
        if st.session_state.is_pro == 0 and st.session_state.img_trials <= 0:
            st.error("You used all 3 free trials. Upgrade to Pro for unlimited.")
            st.link_button("Upgrade to Pro", "https://opay.ng/s/36QEa", type="primary")
        else:
            if st.session_state.is_pro == 0:
                st.info(f"You have {st.session_state.img_trials} free image generations left")
            prompt = st.text_input("Describe the image you want")
            if st.button("Generate"):
                with st.spinner("Generating..."):
                    img = generate_image(prompt)
                    st.image(img)
                    if st.session_state.is_pro == 0:
                        st.session_state.img_trials -= 1
                        st.rerun()

    # 3. PDF CHAT - 3 FREE TRIALS
    elif page == "PDF Chat":
        st.title("📄 Chat with PDF")
        if st.session_state.is_pro == 0 and st.session_state.pdf_trials <= 0:
            st.error("You used all 3 free trials. Upgrade to Pro for unlimited.")
            st.link_button("Upgrade to Pro", "https://opay.ng/s/36QEa", type="primary")
        else:
            if st.session_state.is_pro == 0:
                st.info(f"You have {st.session_state.pdf_trials} free PDF chats left")
            pdf = st.file_uploader("Upload PDF", type="pdf")
            if pdf:
                reader = PdfReader(pdf)
                text = "".join([p.extract_text() for p in reader.pages])
                q = st.text_input("Ask about this PDF")
                if q and st.button("Ask"):
                    messages = [{"role":"user","content":f"Context: {text[:4000]}\n\nQuestion: {q}"}]
                    st.write(get_ai_response(messages))
                    if st.session_state.is_pro == 0:
                        st.session_state.pdf_trials -= 1
                        st.rerun()

    # 4. BILLING
    elif page == "Billing":
        st.title("💳 Billing")
        if st.session_state.is_pro:
            st.success("You are Pro! Unlimited Images + PDFs")
        else:
            st.write("Get Unlimited Access")
            st.link_button("Upgrade to Pro - ₦5000/month", "https://opay.ng/s/36QEa", type="primary")