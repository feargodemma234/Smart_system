import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_ai_response(prompt, chat_history, model="openai/gpt-oss-120b", stream=False):
    # Build full message history for Groq
    messages = [{"role": "system", "content": "You are Quantum AI, a helpful, intelligent, and friendly assistant. Answer clearly and concisely."}]
    messages.extend([{"role": m["role"], "content": m["content"]} for m in chat_history])

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=stream,
        max_tokens=2048,
        temperature=0.7
    )
    
    if stream:
        for chunk in response:
            yield chunk.choices[0].delta.content or ""
    else:
        return response.choices[0].message.content