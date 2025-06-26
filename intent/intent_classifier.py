# intent_classifier.py
from transformers import pipeline
from functools import lru_cache
# Load a small, fast zero-shot classifier model
classifier = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")

# Define the same intent labels as in your current setup
CANDIDATE_LABELS = ["yes_no", "timeline", "insight", "guidance", "general"]

def classify_intent(question: str) -> str:
    result = classifier(question, CANDIDATE_LABELS)
    intent = result["labels"][0].lower()
    
    # Just in case, sanitize to known intents
    if intent not in CANDIDATE_LABELS:
        return "general"
    return intent
