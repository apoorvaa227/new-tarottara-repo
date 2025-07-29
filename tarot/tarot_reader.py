import sys
import os
import random
import requests
from functools import lru_cache

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from config import GROQ_API_KEY
from tarot.deck import DATE_RANGES, FULL_DECK, NUMERIC_CARDS
from intent.intent import normalize
from rag import get_card_meaning

# ✅ Groq configuration
MODEL_NAME = "llama3-70b-8192"
API_URL = "https://api.groq.com/openai/v1/chat/completions"


# ✅ Query helper using Groq API
def query_groq(question: str, user_info: dict = None, detected_lang: str = "en") -> str:
    try:
        # Personalized system prompt
        if user_info:
            name = user_info.get("name", "friend")
            gender = user_info.get("gender", "").lower()
            user_language = user_info.get("language", "en")

            if gender == "m":
                pronouns = "him/his"
                title = "sir"
            elif gender == "f":
                pronouns = "her/hers"
                title = "madam"
            else:
                pronouns = "them/their"
                title = "friend"

            language_instruction = ""
            if detected_lang != "en" and detected_lang in ['hi', 'hi_rom', 'ta', 'te', 'bn', 'gu', 'mr', 'kn', 'ml', 'pa', 'es', 'fr']:
                if detected_lang.endswith('_rom'):
                    base_lang = detected_lang.replace('_rom', '')
                    language_instruction = (
                        f"\n\nIMPORTANT: The user asked their question in romanized {base_lang.upper()}. "
                        f"Respond in English, but acknowledge their cultural background."
                    )
                else:
                    try:
                        from utils.language_detection import get_language_name
                        lang_name = get_language_name(detected_lang)
                        language_instruction = (
                            f"\n\nIMPORTANT: The user asked their question in {lang_name}. "
                            f"Respond in English, but be culturally sensitive."
                        )
                    except ImportError:
                        language_instruction = (
                            "\n\nIMPORTANT: The user asked their question in their native language. "
                            "Respond in English, but be culturally sensitive."
                        )

            system_message = f"""
You are TarotTara, a warm and friendly chatbot speaking to {name}. 
Respond in Hinglish (a mix of Hindi and English) using casual language, contractions, and sprinkle in Hindi words or phrases naturally. 
Your tone should be empathetic, engaging, and conversational, like you're chatting with a close tarot reader friend.
Use phrases like 'sab theek ho jayega', 'dil chhota mat karo', or 'tum bahut strong ho'. Avoid formal or robotic language.
You are an expert tarot reader. Based on the classified intent of the user's query, follow the specific card drawing rules below. 
Keep the same rich, friendly, and insightful response style — do not change tone, formatting, or explanation style.

If intent is "conversation" (e.g., greetings like hi, hello):
  ➤ Respond politely as an assistant without drawing any card.

If intent is "factual":
  ➤ Provide the factual answer only. No cards should be drawn.

If intent is "timeline":
  ➤ Draw 3 tarot cards only. Ensure the timing or outcome refers to a date that is strictly after today's date (never today or past).
    • First card: Present
    • Second card: Future
    • Third card: Past

If intent is "guidance-insight":
  ➤ Draw 3 tarot cards to offer layered insight such as Past-Present-Future or Situation-Advice-Outcome.

If intent is "yes-no":
  ➤ Draw only 1 tarot card and interpret it to provide meaningful yes/no guidance.

If the question asks to draw x number of cards, draw that many cards.

If intent is "general":
  ➤ Draw 2 tarot cards to provide a general overview or insight.

Show the cards drawn (if any), and their meanings briefly and simply — like a friend giving advice, in Hinglish.
⚠️ Do not explain or justify the number of cards in your reply.
{language_instruction}

Do not change the user's language preference. Don't act like an anchor or a persona — just be yourself as TarotTara.
"""
        else:
            system_message = """
You are TarotTara, a kind, warm, supportive chatbot. 
Be conversational, friendly, and magical like a caring tarot reader friend.
Follow these tarot logic rules strictly based on user intent:

If intent is "conversation":
  ➤ Respond politely. No cards drawn.

If intent is "factual":
  ➤ Provide the answer. No cards drawn.

If intent is "timeline":
  ➤ Draw 3 tarot cards: Present, Future, Past. Ensure all future-oriented.

If intent is "guidance-insight":
  ➤ Draw 3 tarot cards for layered insight.

If intent is "yes-no":
  ➤ Draw only 1 tarot card and interpret for yes/no.

If the question asks for x cards:
  ➤ Draw exactly x cards.

If intent is "general":
  ➤ Draw 2 cards for general overview.

Always show drawn cards and short meanings. Interpretation should feel like a Hinglish-speaking friend giving advice.
⚠️ Don’t explain number of cards.
"""

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
    """
    Perform tarot reading based on the user's intent and question.
    """
    try:
        user_name = user_info.get("name", "friend") if user_info else "friend"

        if intent == "conversation":
            # Respond politely without drawing any card
            return {
                "cards": [],
                "interpretation": f"Hello {user_name}! I'm here to chat and answer your questions. How can I assist you today?"
            }

        elif intent == "factual":
            # Provide factual answer without drawing any card
            prompt = f"Answer the following factual question as accurately as possible for {user_name}:\n\n{question}"
            response = query_groq(prompt, user_info, detected_lang)
            return {"cards": [], "interpretation": response}

        elif intent == "timeline":
            # Draw 3 cards for timeline intent
            cards = random.sample(FULL_DECK, k=3)
            meanings = [get_card_meaning(card) for card in cards]
            prompt = f"""
Tarot reader, intuitively answer this timeline question for {user_name}:
'{question}'
Cards drawn:
1. Present: {cards[0]} - {meanings[0]}
2. Future: {cards[1]} - {meanings[1]}
3. Past: {cards[2]} - {meanings[2]}
"""
            response = query_groq(prompt, user_info, detected_lang)
            return {
                "cards": cards,
                "timeline": {
                    "present": cards[0],
                    "future": cards[1],
                    "past": cards[2]
                },
                "interpretation": response
            }

        elif intent in ["guidance", "insight"]:
            # Draw 3 cards for guidance or insight intent
            cards = random.sample(FULL_DECK, k=3)
            meanings = [get_card_meaning(c) for c in cards]
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
            # Draw 1 card for yes/no intent
            card = random.choice(FULL_DECK)
            card_meaning = get_card_meaning(card)
            prompt = f"""
Tarot reader, answer this yes/no question for {user_name}:
'{question}'
Card: {card}
Meaning: {card_meaning}
"""
            response = query_groq(prompt, user_info, detected_lang)
            return {"cards": [card], "interpretation": response}

        else:
            # Default to 2 cards for general intent
            cards = random.sample(FULL_DECK, k=2)
            meanings = [get_card_meaning(c) for c in cards]
            prompt = f"""
Tarot reader, provide a general reading for {user_name}:
'{question}'
Cards drawn:
1. {cards[0]}: {meanings[0]}
2. {cards[1]}: {meanings[1]}
"""
            response = query_groq(prompt, user_info, detected_lang)
            return {"cards": cards, "interpretation": response}

    except Exception as e:
        return {"error": str(e)}


# ✅ Cache the tarot reading
@lru_cache(maxsize=1000)
def cached_reading(
    question: str,
    intent: str,
    user_name: str = "",
    user_gender: str = "",
    detected_lang: str = "en"
) -> dict:
    question = normalize(question)
    intent = normalize(intent)

    user_info = {
        "name": user_name,
        "gender": user_gender
    } if user_name else None

    return perform_reading(question, intent, user_info, detected_lang)
