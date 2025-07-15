# intent/classifier.py

from transformers import pipeline

# Load Hugging Face pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

INTENT_LABELS = [
    "fact-based question",
    "yes or no question",
    "time-related question",
    "insightful question",
    "spiritual guidance",
    "general inquiry"
]

label_map = {
    "fact-based question": "factual",
    "yes or no question": "yes_no",
    "time-related question": "timeline",
    "insightful question": "insight",
    "spiritual guidance": "guidance",
    "general inquiry": "general"
}
