import random
from functools import lru_cache

from langchain_ollama import ChatOllama

from config import MODEL_NAME
from tarot.deck import DATE_RANGES, FULL_DECK, NUMERIC_CARDS
from intent.intent import normalize
from tarot.rag import get_card_meaning

llm = ChatOllama(model=MODEL_NAME)


def perform_reading(question: str, intent: str) -> dict:
    try:
        if intent == "factual":
            response = llm.invoke(
                f"Answer the following factual question as accurately as possible:\n\n{question}"
            ).content.strip()
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
