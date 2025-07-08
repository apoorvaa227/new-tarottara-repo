# intent/intent.py
import os
import re
import requests
from functools import lru_cache
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Universal getter for local + Streamlit Cloud
def get_env(key: str, default=None):
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except:
        return os.getenv(key, default)

GROQ_API_KEY = get_env("GROQ_API_KEY")

def normalize(text: str) -> str:
    return ' '.join(text.lower().strip().split())

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME =  "llama3-70b-8192"

API_URL = "https://api.groq.com/openai/v1/chat/completions"

def classify_intent(question: str) -> str:
    # Direct pattern check for conversation
    conversational_keywords = r"\b(who are you|hi|hello|hey|good morning|good evening|how are you|how's it going|bye|goodbye|see you|what's up|good night|namaste|happy diwali|happy holi)\b"
    if re.search(conversational_keywords, question.lower()):
        return "conversation"
    print("🔑 Key loaded:", bool(GROQ_API_KEY))
    prompt = (
        "You are an intent classifier. Your job is to read a user's question and classify it into ONLY ONE of these categories:\n"
        "- conversation: greetings or casual\n"
        "- yes_no: yes/no questions\n"
        "- factual: verifiable facts\n"
        "- timeline: questions about time\n"
        "- insight: reasons, explanations\n"
        "- guidance: advice or next steps\n"
        "\nRespond with ONLY one of these words (no explanation):\n"
        f"Q: {question}\nA:"
    )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 10,
        "temperature": 0
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        intent = response.json()["choices"][0]["message"]["content"].strip().lower()
        valid_intents = {"yes_no", "timeline", "insight", "guidance", "factual", "conversation"}
        print(response.json())
        return intent if intent in valid_intents else "general"
    except Exception as e:
       print("❌ Error in intent classification:", e)
       if hasattr(e, 'response') and e.response is not None:
           try:
            print("🔎 Response content:", e.response.text)
           except Exception as parse_error:
            print("⚠️ Could not parse error response:", parse_error)
       return "general"

# ✅ Cached version of classify_intent
@lru_cache(maxsize=1000)
def classify_intent_cached(question: str) -> str:
    """Cache the intent classification result per normalized question"""
    question = normalize(question)
    return classify_intent(question)

