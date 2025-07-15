import base64
import requests
from typing import Optional, Union
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_env(key: str, default=None):
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except:
        return os.getenv(key, default)

API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = get_env("GROQ_API_KEY")

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

def process_image_with_question(image_data: Union[str, bytes], question: str, user_info: dict = None) -> str:
    """
    Process image with text question using Llama 4 Maverick multimodal model
    """
    user_name = user_info.get("name", "friend") if user_info else "friend"
    user_gender = user_info.get("gender", "") if user_info else ""
    user_language = user_info.get("language", "en") if user_info else "en"
    
    # Convert image to base64 if it's bytes
    if isinstance(image_data, bytes):
        image_base64 = base64.b64encode(image_data).decode('utf-8')
    else:
        image_base64 = image_data
    
    # Gender-specific pronouns
    if user_gender.lower() == "m":
        pronouns = "him/his"
        title = "sir"
    elif user_gender.lower() == "f":
        pronouns = "her/hers"
        title = "madam"
    else:
        pronouns = "them/their"
        title = "friend"
    
    system_message = f"""You are TarotTara, a wise and mystical tarot reader with the gift of sight speaking to {user_name}. 
    You can see and interpret both images and spiritual energy. When {user_name} shares an image with a question:

    1. Carefully observe all visual elements in the image
    2. Connect the visual symbolism to tarot wisdom and spiritual insights  
    3. Provide guidance that addresses their specific question
    4. Be warm, personal, and address {user_name} directly using appropriate pronouns ({pronouns})
    5. If you see tarot cards in the image, interpret them in detail
    6. If it's a life situation photo, offer spiritual guidance about what you perceive
    7. If you see symbols, objects, or scenes, relate them to {user_name}'s spiritual journey
    8. Keep responses mystical yet grounded in wisdom

    Always start your response by addressing {user_name} by name and acknowledge what you see in their image."""
    
    # Construct message with both text and image
    messages = [
        {"role": "system", "content": system_message},
        {
            "role": "user", 
            "content": [
                {"type": "text", "text": f"{user_name} asks: {question}"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        }
    ]
    
    payload = {
        "model": "meta-llama/llama-4-maverick-17b-128e-instruct",
        "messages": messages,
        "max_tokens": 2000,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"I'm having trouble seeing the mystical energies in your image right now, {user_name}. The cosmic connection seems clouded. Could you try uploading it again? ✨"

def encode_image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')