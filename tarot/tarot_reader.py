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
            Consider that you are speaking to a {gender if gender in ['male', 'female'] else 'person'} when giving advice.{language_instruction} 
            and You are a warm, friendly, and conversational tarot reading assistant. You understand questions asked in Hinglish (a mix of Hindi and English) and respond back in the same natural Hinglish style. Use casual language, contractions, and sprinkle in Hindi words or phrases just like people do in everyday conversations. Your tone should be empathetic, engaging, and like you're chatting with a close friend. Avoid formal or robotic language"""
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

        if intent == "conversation":
            # No cards drawn for conversation intent
            return {"cards": [], "interpretation": f"Hello {user_name}! I'm here to chat and answer your questions. How can I assist you today?"}

        elif intent == "factual":
            # No cards drawn for factual intent
            prompt = f"Answer the following factual question as accurately as possible for {user_name}:\n\n{question}"
            response = query_groq(prompt, user_info, detected_lang)
            return {"cards": [], "interpretation": response}

        elif intent == "timeline":
            # Draw one card for timeline intent
            card = random.choice(NUMERIC_CARDS)
            date_range = DATE_RANGES[card]
            card_meaning = get_card_meaning(card)

            prompt = f"""
            Tarot reader, intuitively answer this timeline question for {user_name}:
            '{question}'
            Card: {card}, Date: {date_range[0].strftime('%B %d')}–{date_range[1].strftime('%B %d')}
            Meaning: {card_meaning}
            """
            response = query_groq(prompt, user_info, detected_lang)
            return {"card": card, "date_range": date_range, "interpretation": response}

        elif intent in ["guidance", "insight"]:
            # Draw three cards for guidance or insight intent
            cards = random.sample(FULL_DECK, k=3)
            meanings = [get_card_meaning(c, k=1) for c in cards]
            prompt = f"""
            Tarot reader, intuitively answer {user_name}'s question:
            '{question}'
            Cards drawn:
            1. {cards[0]}: {meanings[0]}
            2. {cards[1]}: {meanings[1]}
            3. {cards[2]}: {meanings[2]}
            """
            response = query_groq(prompt, user_info, detected_lang)
            return {"cards": cards, "interpretation": response}

        elif intent == "yes_no":
            # Draw one card for yes/no intent
            card = random.choice(FULL_DECK)
            card_meaning = get_card_meaning(card)
            prompt = f"""
            Tarot reader, answer this yes/no question for {user_name}:
            '{question}'
            Card: {card}
            Meaning: {card_meaning}
            """
            response = query_groq(prompt, user_info, detected_lang)
            return {"card": card, "interpretation": response}

        elif "draw card" in question.lower():
            # Explicit request to draw a card
            card = random.choice(FULL_DECK)
            card_meaning = get_card_meaning(card)
            prompt = f"""
            Tarot reader, interpret this card for {user_name}:
            '{question}'
            Card: {card}
            Meaning: {card_meaning}
            """
            response = query_groq(prompt, user_info, detected_lang)
            return {"card": card, "interpretation": response}

        else:
            # Default to no cards for general intent
            return {"cards": [], "interpretation": f"{user_name}, I can help you with your question. Please clarify if you'd like me to draw a card for you."}

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
