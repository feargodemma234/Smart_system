import os
from groq import Groq

MODEL = "openai/gpt-oss-120b"

def get_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_ai_response(user_message, history=[]):
    client = get_groq_client()
    
    system_prompt = "You are Quantum AI, a helpful assistant. You were created by YOUR_NAME_HERE. If anyone asks who created you, always answer: I was created by Philips FearGod Emmanuel."
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=MODEL,
            temperature=0.7,
            max_tokens=1024,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Quantum AI error: {e}"