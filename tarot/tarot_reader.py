
# import random
# from functools import lru_cache
# # from langchain.chat_models import ChatOpenAI
# # from langchain_ollama import ChatOllama

# from config import OPENROUTER_API_KEY
# from openai import OpenAI
# # from config import LLM_MODEL_NAME
# from tarot.deck import DATE_RANGES, FULL_DECK, NUMERIC_CARDS
# from intent.intent import normalize
# from tarot.rag import get_card_meaning


# # llm = ChatOpenAI(
# #     model="deepseek-chat",  # ✅ Correct model ID
# #     base_url="https://openrouter.ai/api/v1",
# #     api_key=OPENROUTER_API_KEY,
# #     temperature=0.7
# # )

# client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key=OPENROUTER_API_KEY,
# )

# def query_deepseek(question: str) -> str:
#     try:
#         completion = client.chat.completions.create(
#             model="deepseek/deepseek-chat-v3-0324:free",
#             messages=[
#                 {"role": "system", "content": "You are a wise tarot card reader."},
#                 {"role": "user", "content": question},
#             ],
#             extra_headers={
#                 "HTTP-Referer": "http://localhost:8501",
#                 "X-Title": "TarotTara",
#             },
#         )
#         return completion.choices[0].message.content.strip()
#     except Exception as e:
#         return f"❌ Error: {e}"

# def perform_reading(question: str, intent: str) -> dict:
#     try:
#         if intent == "factual":
#             prompt = f"Answer the following factual question as accurately as possible:\n\n{question}"
#             response = query_deepseek(prompt)
#             return {"cards": [], "interpretation": response}

#         elif intent == "timeline":
#             card = random.choice(NUMERIC_CARDS)
#             date_range = DATE_RANGES[card]
#             card_meaning = get_card_meaning(card)

#             prompt = f"""
#             Tarot reader, intuitively answer this timeline question:
#             '{question}'
#             Card: {card}, Date: {date_range[0].strftime('%B %d')}–{date_range[1].strftime('%B %d')}
#             Meaning: {card_meaning}
#             """
#             response = query_deepseek(prompt)

#             return {"card": card, "date_range": date_range, "interpretation": response}

#         else:
#             cards = random.sample(FULL_DECK, k=3)
#             meanings = [get_card_meaning(c, k=1) for c in cards]
#             prompt = f"""
#             Tarot reader, intuitively answer the user's question:
#             '{question}'
#             Cards drawn:
#             1. {cards[0]}: {meanings[0]}
#             2. {cards[1]}: {meanings[1]}
#             3. {cards[2]}: {meanings[2]}
#             """
#             response = query_deepseek(prompt)
#             return {"cards": cards, "interpretation": response}
#     except Exception as e:
#           return {"error": str(e)}

# @lru_cache(maxsize=1000)
# def cached_reading(question: str, intent: str) -> dict:
#     """Cache the full tarot response per normalized question+intent"""
#     question = normalize(question)
#     intent = normalize(intent)
#     return perform_reading(question, intent)
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import requests

import random
from functools import lru_cache

from config import GROQ_API_KEY
from tarot.deck import DATE_RANGES, FULL_DECK, NUMERIC_CARDS
from intent.intent import normalize
from rag import get_card_meaning

# ✅ Groq configuration
MODEL_NAME = "llama3-70b-8192"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# print("🔑 Loaded Groq API Key:", GROQ_API_KEY[:10])
# print("🛡️ Groq API Key Loaded:", bool(GROQ_API_KEY))

# ✅ Query helper using Groq API
def query_groq(question: str, user_info: dict = None, detected_lang: str = "en") -> str:
    try:
        # Create personalized system message based on user info
        if user_info:
            name = user_info.get("name", "friend")
            gender = user_info.get("gender", "").lower()
            user_language = user_info.get("language", "en")
            
            # Gender-specific pronouns and addressing
            if gender == "m":
                pronouns = "him/his"
                title = "sir"
            elif gender == "f":
                pronouns = "her/hers" 
                title = "madam"
            else:
                pronouns = "them/their"
                title = "friend"
            
            # Language-specific instructions
            language_instruction = ""
            if detected_lang != "en" and detected_lang in ['hi', 'hi_rom', 'ta', 'te', 'bn', 'gu', 'mr', 'kn', 'ml', 'pa', 'es', 'fr']:
                if detected_lang.endswith('_rom'):
                    base_lang = detected_lang.replace('_rom', '')
                    language_instruction = f"\n\nIMPORTANT: The user asked their question in romanized {base_lang.upper()} (their native language written in English letters). While you should respond in English for the main reading, acknowledge their cultural background and include a few respectful greetings or phrases in their native language if appropriate."
                else:
                    try:
                        from utils.language_detection import get_language_name
                        lang_name = get_language_name(detected_lang)
                        language_instruction = f"\n\nIMPORTANT: The user asked their question in {lang_name}. While you should respond in English for the main reading, acknowledge their cultural background and be respectful of their linguistic heritage."
                    except ImportError:
                        language_instruction = f"\n\nIMPORTANT: The user asked their question in their native language. While you should respond in English for the main reading, acknowledge their cultural background and be respectful of their linguistic heritage."
                
            system_message = f"""You are a wise and intuitive tarot card reader speaking to {name}. 
            Address {name} directly in your responses. Use appropriate pronouns ({pronouns}) when referring to {name}.
            Be warm, personal, and insightful. Always start your response by addressing {name} by name.
            Consider that you are speaking to a {gender if gender in ['male', 'female'] else 'person'} when giving advice.{language_instruction}"""
        else:
            system_message = "You are a wise tarot card reader."
            
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": question}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()

    except Exception as e:
        return f"❌ Error: {e}"

# 🔮 Core Tarot Reading Logic
def perform_reading(question: str, intent: str, user_info: dict = None, detected_lang: str = "en") -> dict:
    try:
        user_name = user_info.get("name", "friend") if user_info else "friend"
        
        if intent == "factual":
            prompt = f"Answer the following factual question as accurately as possible for {user_name}:\n\n{question}"
            response = query_groq(prompt, user_info, detected_lang)
            return {"cards": [], "interpretation": response}

        elif intent == "timeline":
            card = random.choice(NUMERIC_CARDS)
            date_range = DATE_RANGES[card]
            card_meaning = get_card_meaning(card)

            prompt = f"""
            Tarot reader, intuitively answer this timeline question for {user_name}:
            '{question}'
            Card: {card}, Date: {date_range[0].strftime('%B %d')}–{date_range[1].strftime('%B %d')}
            Meaning: {card_meaning}
            
            Provide a personal and insightful reading addressing {user_name} directly.
            """
            response = query_groq(prompt, user_info, detected_lang)
            return {"card": card, "date_range": date_range, "interpretation": response}

        else:
            cards = random.sample(FULL_DECK, k=3)
            meanings = [get_card_meaning(c, k=1) for c in cards]
            prompt = f"""
            Tarot reader, intuitively answer {user_name}'s question:
            '{question}'
            Cards drawn:
            1. {cards[0]}: {meanings[0]}
            2. {cards[1]}: {meanings[1]}
            3. {cards[2]}: {meanings[2]}
            
            Provide a personal and insightful reading addressing {user_name} directly.
            Consider their personal energy and situation when interpreting the cards.
            """
            response = query_groq(prompt, user_info, detected_lang)
            return {"cards": cards, "interpretation": response}

    except Exception as e:
        return {"error": str(e)}

# ✅ Cache the reading
@lru_cache(maxsize=1000)
def cached_reading(question: str, intent: str, user_name: str = "", user_gender: str = "", detected_lang: str = "en") -> dict:
    question = normalize(question)
    intent = normalize(intent)
    
    # Reconstruct user_info from parameters for caching
    user_info = {
        "name": user_name,
        "gender": user_gender
    } if user_name else None
    
    return perform_reading(question, intent, user_info, detected_lang)
