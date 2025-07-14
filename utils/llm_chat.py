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

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

def generate_conversational_response(message: str, user_info: dict = None, detected_lang: str = "en") -> str:
    """
    Generate conversational response with backward compatibility.
    Can be called with 1, 2, or 3 arguments.
    """
    # Handle backward compatibility - if user_info is a string, it's the old calling pattern
    if isinstance(user_info, str):
        # Old calling pattern: generate_conversational_response(message)
        # In this case, user_info is actually None and detected_lang is the user_info
        detected_lang = "en"
        user_info = None
    
    user_name = user_info.get("name", "friend") if user_info else "friend"
    user_gender = user_info.get("gender", "").lower() if user_info else ""
    
    # Gender-specific pronouns
    if user_gender == "m":
        pronouns = "him/his"
    elif user_gender == "f":
        pronouns = "her/hers"
    else:
        pronouns = "them/their"
    
    # Language-specific cultural context
    language_context = ""
    if detected_lang != "en" and detected_lang in ['hi', 'hi_rom', 'ta', 'te', 'bn', 'gu', 'mr', 'kn', 'ml', 'pa', 'es', 'fr']:
        if detected_lang.endswith('_rom'):
            base_lang = detected_lang.replace('_rom', '')
            language_context = f"\n\nNote: {user_name} is speaking in romanized {base_lang.upper()}. Be culturally respectful and warm."
        else:
            # Import here to avoid circular imports
            try:
                from utils.language_detection import get_language_name
                lang_name = get_language_name(detected_lang)
                language_context = f"\n\nNote: {user_name} is speaking in {lang_name}. Be culturally respectful and acknowledge their heritage warmly."
            except ImportError:
                language_context = f"\n\nNote: {user_name} is speaking in their native language. Be culturally respectful and warm."
    
    system_message = f"""You are TarotTara, a kind, warm, supportive chatbot speaking to {user_name}. 
    Address {user_name} directly by name in your responses. Use appropriate pronouns ({pronouns}) when referring to {user_name}.
    Be conversational, friendly, and magical like a caring tarot reader friend.{language_context}"""
    
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": message}
        ],
        "max_tokens": 200,
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("❌ Error generating conversational response:", e)
        return f"Hmm {user_name}, something went wrong while I was trying to respond to you. Please try again."
