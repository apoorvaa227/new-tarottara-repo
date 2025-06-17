# import random
# from langchain_ollama import ChatOllama
# from config import MODEL_NAME
# from deck import NUMERIC_CARDS, DATE_RANGES
# from rag import get_card_meaning

# llm = ChatOllama(model=MODEL_NAME)

# def predict_timing(question: str) -> str:
#     # Draw a numeric Minor Arcana card
#     card = random.choice(NUMERIC_CARDS)
#     date_range = DATE_RANGES[card]
#     card_meaning = get_card_meaning(card)

#     # Build a clear, detailed prompt
#     prompt = f"""
#     You're TarotTara, an intuitive and empathetic tarot reader.

#     User Question: "{question}"
    
#     Card Drawn for Timing Prediction: "{card}"
#     Associated Date Range: {date_range[0].strftime('%B %d')}–{date_range[1].strftime('%B %d')}

#     Symbolic Card Meaning (from Tarot references):
#     {card_meaning}

#     Now, interpret the timing intuitively and clearly. Tell the user explicitly during which date range they can expect events related to their question. Be warm, supportive, and clear in your prediction.
#     """

#     # Invoke the LLM with the prepared prompt
#     response = llm.invoke(prompt)
    
#     # Safely extract response content
#     if hasattr(response, 'content'):
#         return response.content.strip()
#     else:
#         # Fallback if response is malformed
#         return f"I drew the {card}, which suggests your timeframe is {date_range[0].strftime('%B %d')}–{date_range[1].strftime('%B %d')}."

# import random
# from langchain_ollama import ChatOllama
# from config import MODEL_NAME
# from functools import lru_cache
# from intent import normalize
# from deck import FULL_DECK, NUMERIC_CARDS, DATE_RANGES
# from rag import get_card_meaning

# llm = ChatOllama(model=MODEL_NAME)

# def perform_reading(question: str, intent: str):
#     try:
#         #print(question, intent,"is called perform reading")
#         if intent == "timeline":
#            # print("came in timline")
#             card = random.choice(NUMERIC_CARDS)
#            # print("came in card")
#             date_range = DATE_RANGES[card]
#            # print("came in date_range")
#             card_meaning = get_card_meaning(card)
#            # print("came in card_meaning")
#             prompt = f"""
#             Tarot reader, intuitively answer this timeline question:
#             '{question}'
#             Card: {card}, Date: {date_range[0].strftime('%B %d')}–{date_range[1].strftime('%B %d')}
#             Meaning: {card_meaning}
#             """
#            # print(prompt)
#             response = llm.invoke(prompt).content.strip()
#            # print(response)
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
#             #wheprint(prompt)
#             response = llm.invoke(prompt).content.strip()
#            # print(response)
#             return {"cards": cards, "interpretation": response}
#     except Exception as e:
#         #print(e)
#         return {"error": str(e)}
    
# @lru_cache(maxsize=1000)
# def cached_reading(question: str, intent: str) -> dict:
#     """Cache the full tarot response per normalized question+intent"""
#     question = normalize(question)
#     intent = normalize(intent)
#     return perform_reading(question, intent)



import random
from langchain_ollama import ChatOllama
from config import MODEL_NAME
from functools import lru_cache
from intent import normalize
from deck import FULL_DECK, NUMERIC_CARDS, DATE_RANGES
from rag import get_card_meaning

llm = ChatOllama(model=MODEL_NAME)

def perform_reading(question: str, intent: str) -> dict:
    try:
        if intent == "timeline":
            card = random.choice(NUMERIC_CARDS)
            date_range = DATE_RANGES[card]
            card_meaning = get_card_meaning(card)

            prompt = f"""
            Tarot reader, intuitively answer this timeline question:
            '{question}'
            Card: {card}, Date: {date_range[0].strftime('%B %d')}–{date_range[1].strftime('%B %d')}
            Meaning: {card_meaning}
            """
            response = llm.invoke(prompt).content.strip()
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
            response = llm.invoke(prompt).content.strip()
            return {"cards": cards, "interpretation": response}
    except Exception as e:
        return {"error": str(e)}

@lru_cache(maxsize=1000)
def cached_reading(question: str, intent: str) -> dict:
    """Cache the full tarot response per normalized question+intent"""
    question = normalize(question)
    intent = normalize(intent)
    return perform_reading(question, intent)
