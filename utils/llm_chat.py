# utils/llm_chat.py (new file)
import os
import requests
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Universal getter for local + Streamlit Cloud
def get_env(key: str, default=None):
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except:
        return os.getenv(key, default)

GROQ_API_KEY = get_env("GROQ_API_KEY")

MODEL_NAME =  "llama3-70b-8192"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

def generate_conversational_response(message: str, user_info: dict = None, detected_lang: str = "en", context: list = None) -> str:
    user_name = user_info.get("name", "friend") if user_info else "friend"
    user_language = user_info.get("language", "en") if user_info else "en"

    # Check if Hinglish is requested
    if user_language == "hinglish":
        system_message = f"""You are TarotTara, a warm and friendly chatbot speaking to {user_name}. 
        Respond in Hinglish (a mix of Hindi and English) using casual language, contractions, and sprinkle in Hindi words or phrases naturally. 
        Your tone should be empathetic, engaging, and conversational, like you're chatting with a close friend. 
        For example, use phrases like 'sab theek ho jayega', 'dil chhota mat karo', or 'tum bahut strong ho'. Avoid formal or robotic language."""
    else:
        system_message = f"""You are TarotTara, a kind, warm, supportive chatbot speaking to {user_name}. 
        Address {user_name} directly by name in your responses. Be conversational, friendly, and magical like a caring tarot reader friend."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # Include context memory in the payload
    messages = [{"role": "system", "content": system_message}]
    if context:
        messages.extend(context)
    messages.append({"role": "user", "content": message})

    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": 500,  # Increased token limit for longer responses
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        # Ensure only one response is returned
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("❌ Error generating conversational response:", e)
        return f"Hmm {user_name}, kuch galat ho gaya lagta hai. Please try again, dost!"
