# utils/llm_chat.py (new file)
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

def generate_conversational_response(message: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are TarotTara, a kind, warm, supportive chatbot. Respond conversationally to the user, like a magical friendly assistant."},
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
        return "Hmm, something went wrong while I was trying to respond to you. Please try again."
