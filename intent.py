# from transformers import pipeline
# from functools import lru_cache
# # Load zero-shot classifier
# classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# # Intent labels you want to classify
# INTENT_LABELS = ["yes_no", "timeline", "insight", "guidance", "general"]

# def classify_intent(question: str) -> str:
#     result = classifier(question, INTENT_LABELS)
#     return result["labels"][0]  # Top predicted intent


# @lru_cache(maxsize=100)
# def classify_intent_cached(question: str, intent: str):
#     return classify_intent(question)



# from transformers import pipeline
# from functools import lru_cache

# classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# INTENT_LABELS = ["yes_no", "timeline", "insight", "guidance", "general"]

# def normalize(text: str) -> str:
#     """Clean input: lowercase, strip, remove extra spaces."""
#     return ' '.join(text.lower().strip().split())

# @lru_cache(maxsize=1000)
# def classify_intent(question: str) -> str:
#     question = normalize(question)
#     result = classifier(question, INTENT_LABELS)
#     return result["labels"][0]



from transformers import pipeline
from functools import lru_cache

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

INTENT_LABELS = ["yes_no", "timeline", "insight", "guidance", "general"]

def normalize(text: str) -> str:
    """Clean input: lowercase, strip, remove extra spaces."""
    return ' '.join(text.lower().strip().split())

@lru_cache(maxsize=1000)
def classify_intent_cached(question: str) -> str:
    question = normalize(question)
    result = classifier(question, INTENT_LABELS)
    return result["labels"][0]
