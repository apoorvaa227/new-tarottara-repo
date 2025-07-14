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
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import requests

import random
from functools import lru_cache
import traceback

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
    """
    Generate a tarot reading based on the question and intent.
    """
    # Check if user specifically requested one card
    question_lower = question.lower()
    single_card_keywords = ['one card', 'single card', 'draw one', 'pull one', 'just one card', 'only one card']
    
    if any(keyword in question_lower for keyword in single_card_keywords):
        # Draw only one card
        card = random.choice(FULL_DECK)
        cards = [card]
        num_cards = 1
    else:
        # Default behavior - draw 3 cards
        if intent == "timeline":
            card = random.choice(NUMERIC_CARDS)
            date_range = random.choice(DATE_RANGES)
            return {
                "card": card,
                "date_range": date_range,
                "interpretation": generate_reading(
                    question=question,
                    cards=[card],
                    card_meanings=[f"{card}: {get_card_meaning(card)}"],
                    intent=intent,
                    user_name=user_name,
                    user_gender=user_gender,
                    detected_lang=detected_lang
                )
            }
        else:
            cards = random.sample(FULL_DECK, 3)
            num_cards = 3
    
    # Get card meanings
    card_meanings = []
    for card in cards:
        try:
            meaning = get_card_meaning(card)
            card_meanings.append(f"{card}: {meaning}")
        except Exception as e:
            card_meanings.append(f"{card}: Traditional tarot meaning")
    
    # Generate interpretation
    interpretation = generate_reading(
        question=question,
        cards=cards,
        card_meanings=card_meanings,
        intent=intent,
        user_name=user_name,
        user_gender=user_gender,
        detected_lang=detected_lang
    )
    
    return {
        "cards": cards,
        "card_meanings": card_meanings,
        "interpretation": interpretation
    }

# Update the generate_reading function to handle single vs multiple cards

def generate_reading(question: str, cards: list, card_meanings: list, intent: str, user_name: str, user_gender: str, detected_lang: str) -> str:
    """Generate a tarot reading using the LLM."""
    
    # Determine if this is a single card or multiple card reading
    is_single_card = len(cards) == 1
    
    if is_single_card:
        card_context = f"You have drawn one card for {user_name}: {cards[0]}"
        card_instruction = f"Focus deeply on this single card's meaning and how it relates to {user_name}'s question. Provide a comprehensive interpretation of this one card."
    else:
        card_context = f"You have drawn three cards for {user_name}: {', '.join(cards)}"
        card_instruction = f"Interpret these three cards together as a cohesive reading for {user_name}."
    
    # Gender-specific language
    if user_gender.lower() == "m":
        pronouns = "he/him/his"
    elif user_gender.lower() == "f":
        pronouns = "she/her/hers"  
    else:
        pronouns = "they/them/their"
    
    system_prompt = f"""You are TarotTara, a wise tarot reader speaking to {user_name}.
    
    {card_context}
    
    Card meanings:
    {chr(10).join(card_meanings)}
    
    {card_instruction}
    
    Guidelines:
    1. Address {user_name} directly and warmly
    2. Use {pronouns} pronouns when referring to {user_name}
    3. Connect the card meaning(s) to their specific question
    4. Provide actionable guidance and insights
    5. Keep the tone mystical but practical
    6. Make sure to complete your thoughts fully - don't cut off mid-sentence
    
    Question: {question}
    Intent: {intent}
    """

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(API_URL, headers=headers, json={
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please provide a complete tarot reading for {user_name}'s question."}
            ],
            "max_tokens": 1000,  # Increased token limit
            "temperature": 0.7
        })
        
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
        
    except Exception as e:
        return f"I'm having trouble connecting with the spiritual realm right now, {user_name}. Please try again. Error: {str(e)}"

def debug_log_error(context: str, error: Exception):
    print(f"❌ [{context}] Exception: {error}")
    print(traceback.format_exc())
    if hasattr(error, 'response') and error.response is not None:
        try:
            print("🔎 Response content:", error.response.text)
        except Exception as parse_error:
            print("⚠️ Could not parse error response:", parse_error)

# Make sure DATE_RANGES is defined like this:
DATE_RANGES = [
    (datetime(2025, 7, 1), datetime(2025, 7, 31)),
    (datetime(2025, 8, 1), datetime(2025, 8, 31)),
    # ...add more ranges as needed...
]

# When using:
date_range = random.choice(DATE_RANGES)
