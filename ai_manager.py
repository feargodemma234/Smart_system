import os
from groq import Groq

# THESE ARE THE CURRENT NAMES
MODELS = [
    "llama-3.3-70b-versatile", # Best quality
    "llama-3.1-8b-instant" # Fastest
]

def get_ai_response(user_message, history=[]):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    messages = [{"role": "system", "content": "You are Quantum AI."}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    for model in MODELS:
        try:
            res = client.chat.completions.create(model=model, messages=messages)
            return res.choices[0].message.content
        except Exception:
            pass # try next model
    
    return "Quantum AI error: Could not connect to Groq. Check model names in Playground."