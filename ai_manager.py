import os
from groq import Groq

# List of models to try in order
MODELS = [
    "llama-3.3-70b-versatile", # newest
    "llama-3.1-70b-versatile", # backup 1
    "llama-3.1-8b-instant" # backup 2 - always works
]

def get_ai_response(user_message, history=[]):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    messages = [{"role": "system", "content": "You are Quantum AI, a helpful assistant."}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    last_error = None
    # Try each model until one works
    for model in MODELS:
        try:
            chat_completion = client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=0.7,
                max_tokens=1024,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            last_error = e
            continue # try next model
    
    return f"Quantum AI error: All models failed. Last error: {last_error}"