import os
from groq import Groq
from elevenlabs import Voice, VoiceSettings, generate, voices, clone
from elevenlabs.client import ElevenLabs
import io, base64

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
eleven_client = ElevenLabs(api_key=os.environ.get("ELEVEN_API_KEY"))
MODEL = "openai/gpt-oss-120b"

def get_ai_response(prompt, chat_history, stream=False):
    messages = [{"role": "system", "content": "You are Quantum AI. Be helpful, friendly, and concise."}]
    messages.extend([{"role": m["role"], "content": m["content"]} for m in chat_history])
    response = groq_client.chat.completions.create(model=MODEL, messages=messages, stream=stream, max_tokens=1024)
    if stream:
        for chunk in response: yield chunk.choices[0].delta.content or ""
    else: return response.choices[0].message.content

def text_to_speech(text, voice_id="21m00Tcm4TlvDq8ikWAM"):
    audio = generate(text=text, voice=Voice(voice_id=voice_id, settings=VoiceSettings(stability=0.4, similarity_boost=0.8)), api_key=ELEVEN_API_KEY, model="eleven_multilingual_v2")
    return io.BytesIO(audio)

def voice_changer(audio_bytes, target_voice_id):
    """Turn your voice into target voice"""
    audio = eleven_client.speech_to_speech.convert(
        voice_id=target_voice_id,
        audio=audio_bytes,
        model_id="eleven_english_v1"
    )
    return io.BytesIO(audio)

def generate_sound_effect(prompt):
    """Generate sound effects from text"""
    audio = eleven_client.sound_generation.generate(text=prompt, duration_seconds=5)
    return io.BytesIO(audio)

def isolate_voice(audio_bytes):
    """Remove background noise"""
    audio = eleven_client.audio_isolation.isolate(audio_bytes)
    return io.BytesIO(audio)

def verify_payment_screenshot(image_bytes, expected_amount, user_email):
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    prompt = f"Analyze this bank transfer screenshot. Check if amount is ₦{expected_amount} and narration has {user_email}. Reply ONLY JSON: {{\"status\": \"approved\" or \"rejected\", \"reason\": \"why\", \"amount_found\": 2000}}"
    chat_completion = groq_client.chat.completions.create(model="llama-3.2-90b-vision-preview", messages=[{"role": "user","content": [{"type": "text", "text": prompt},{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}], temperature=0.1)
    return chat_completion.choices[0].message.content