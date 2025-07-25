from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from intent.intent import classify_intent_cached
from tarot.tarot_reader import cached_reading
from utils.language_detection import detect_language_with_groq, get_language_name, normalize_language_for_translation
from deep_translator import GoogleTranslator
import os

app = FastAPI()

# Models for request and response
class QuestionRequest(BaseModel):
    question: str
    user_name: str
    user_gender: str
    user_language: str

class ReadingResponse(BaseModel):
    cards: list
    interpretation: str

# Update the get_env function to use os.getenv directly
def get_env(key: str, default: Optional[str] = None) -> str:
    return os.getenv(key, default)

# Replace the usage of st.secrets with os.getenv
GROQ_API_KEY = get_env("GROQ_API_KEY")

# @app.post("/classify-intent/")
# def classify_intent_endpoint(request: QuestionRequest):
#     try:
#         intent = classify_intent_cached(request.question)
#         return {"intent": intent}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/tarot-reading/", response_model=ReadingResponse)
# def tarot_reading_endpoint(request: QuestionRequest):
#     try:
#         detected_lang, _ = detect_language_with_groq(request.question)
#         translated_question = GoogleTranslator(source=detected_lang, target="en").translate(request.question) if detected_lang != "en" else request.question
#         result = cached_reading(translated_question, classify_intent_cached(translated_question), request.user_name, request.user_gender, detected_lang)
#         if "error" in result:
#             raise HTTPException(status_code=500, detail=result["error"])
#         return {
#             "cards": result.get("cards", []),
#             "interpretation": GoogleTranslator(source="en", target=request.user_language).translate(result["interpretation"]) if request.user_language != "en" else result["interpretation"]
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/detect-language/")
# def detect_language_endpoint(text: str):
#     try:
#         detected_lang, confidence = detect_language_with_groq(text)
#         return {"language": detected_lang, "confidence": confidence, "language_name": get_language_name(detected_lang)}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@app.get("/tarot-reading/")
def get_tarot_reading(
    question: str = Query(..., description="The user's question"),
    user_name: str = Query(..., description="The user's name"),
    user_gender: str = Query(..., description="The user's gender"),
    user_language: str = Query("en", description="The user's preferred language")
):
    """
    GET API to provide generated_cards, interpretation, language, and intent in one request.
    """
    try:
        # Detect language
        detected_lang, _ = detect_language_with_groq(question)
        user_language = normalize_language_for_translation(user_language)
        detected_lang = normalize_language_for_translation(detected_lang)

        # Fallback to English for unsupported languages
        if user_language not in ['en', 'hi', 'es', 'fr', 'ta', 'te', 'bn', 'gu', 'mr', 'kn', 'ml', 'pa']:
            user_language = 'en'

        translated_question = GoogleTranslator(source=detected_lang, target="en").translate(question) if detected_lang != "en" else question

        # Classify intent
        intent = classify_intent_cached(translated_question)

        # Perform tarot reading
        result = cached_reading(translated_question, intent, user_name, user_gender, detected_lang)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        # Translate interpretation if needed
        interpretation = GoogleTranslator(source="en", target=user_language).translate(result["interpretation"]) if user_language != "en" else result["interpretation"]

        # Format response
        cards = result.get("cards", [])
        card_details = [{"name": card} for card in cards]  # Format cards as a list of dictionaries

        response = {
            "cards": card_details,
            "interpretation": interpretation,
            "intent": intent,
            "language": user_language
        }

        # Add additional formatting for timeline intent
        if intent == "timeline":
            response["timeline"] = {
                "present": cards[0] if len(cards) > 0 else None,
                "future": cards[1] if len(cards) > 1 else None,
                "past": cards[2] if len(cards) > 2 else None
            }

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.get("/tarot-reading-query/")
# def get_tarot_reading_query(
#     generated_cards: str = Query(..., description="Comma-separated list of generated cards"),
#     interpretation: str = Query(..., description="Interpretation of the reading"),
#     language: str = Query(..., description="Language of the response"),
#     intent: str = Query(..., description="Intent of the user's query")
# ):
#     """
#     GET API to accept query parameters and return the tarot reading data.
#     """
#     try:
#         # Parse the generated cards
#         cards = generated_cards.split(",")

#         # Return the response
#         return {
#             "generated_cards": cards,
#             "interpretation": interpretation,
#             "language": language,
#             "intent": intent
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
