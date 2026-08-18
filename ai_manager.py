import os
from groq import Groq

# Use the latest stable Groq model
MODEL = "llama-3.3-70b-versatile" # This one won't get decommissioned soon

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in secrets")
    return Groq(api_key=api_key)

def get_ai_response(user_message, history=[]):
    client = get_groq_client()
    
    messages = [{"role": "system", "content": "You are Quantum AI, a helpful and smart assistant."}]
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