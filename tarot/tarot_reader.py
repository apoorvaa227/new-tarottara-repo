
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


import random
from functools import lru_cache
from openai import OpenAI
from config import OPENROUTER_API_KEY
from tarot.deck import DATE_RANGES, FULL_DECK, NUMERIC_CARDS
from intent.intent import normalize
from tarot.rag import get_card_meaning

# OpenRouter client setup
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Query helper
def query_deepseek(question: str) -> str:
    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[
                {"role": "system", "content": "You are a wise tarot card reader."},
                {"role": "user", "content": question},
            ],
            extra_headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "TarotTara",
            },
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {e}"

# Core logic
def perform_reading(question: str, intent: str) -> dict:
    try:
        if intent == "factual":
            prompt = f"Answer the following factual question as accurately as possible:\n\n{question}"
            response = query_deepseek(prompt)
            return {"cards": [], "interpretation": response}

        elif intent == "timeline":
            card = random.choice(NUMERIC_CARDS)
            date_range = DATE_RANGES[card]
            card_meaning = get_card_meaning(card)

            prompt = f"""
            Tarot reader, intuitively answer this timeline question:
            '{question}'
            Card: {card}, Date: {date_range[0].strftime('%B %d')}–{date_range[1].strftime('%B %d')}
            Meaning: {card_meaning}
            """
            response = query_deepseek(prompt)
            return {"card": card, "date_range": date_range, "interpretation": response}

        else:
            cards = random.sample(FULL_DECK, k=3)
            meanings = [get_card_meaning(c, k=1) for c in cards]
            prompt = f"""
            Tarot reader, intuitively answer the user's question:
            '{question}'
            Cards drawn:
            1. {cards[0]}: {meanings[0]}
            2. {cards[1]}: {meanings[1]}
            3. {cards[2]}: {meanings[2]}
            """
            response = query_deepseek(prompt)
            return {"cards": cards, "interpretation": response}

    except Exception as e:
        return {"error": str(e)}

@lru_cache(maxsize=1000)
def cached_reading(question: str, intent: str) -> dict:
    """Cache the full tarot response per normalized question+intent"""
    question = normalize(question)
    intent = normalize(intent)
    return perform_reading(question, intent)
