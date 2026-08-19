import os
from groq import Groq
from gtts import gTTS
import io

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-120b"

def get_ai_response(prompt, chat_history, stream=False):
    messages = [{"role": "system", "content": "You are Quantum AI, a helpful assistant. Keep answers short for voice."}]
    messages.extend([{"role": m["role"], "content": m["content"]} for m in chat_history])

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=stream,
        max_tokens=512, # shorter for voice
        temperature=0.7
    )

    if stream:
        for chunk in response:
            yield chunk.choices[0].delta.content or ""
    else:
        return response.choices[0].message.content

def text_to_speech(text, lang="en"):
    tts = gTTS(text=text, lang=lang, slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp