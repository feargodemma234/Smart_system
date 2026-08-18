import os
from groq import Groq

# USE THIS MODEL - It's what works in your Playground
MODEL = "openai/gpt-oss-120b"

def get_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_ai_response(user_message, history=[]):
    client = get_groq_client()
    
    messages = [{"role": "system", "content": "You are Quantum AI, a helpful and smart assistant."}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=MODEL, # <-- This is the key fix
            temperature=0.7,
            max_tokens=1024,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Quantum AI error: {e}"