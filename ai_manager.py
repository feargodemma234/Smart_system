import os
from groq import Groq
from gtts import gTTS
import io

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

def get_ai_response(messages):
    system_prompt = {"role": "system", "content": "You are Quantum AI Pro, a smart helpful assistant from Nigeria. Be friendly and brief."}
    chat = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[system_prompt] + messages,
        max_tokens=1000
    )
    return chat.choices[0].message.content

def text_to_speech(text, lang="en"):
    tts = gTTS(text=text, lang=lang, slow=False)
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return audio_bytes