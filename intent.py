from transformers import pipeline
from functools import lru_cache

# Load zero-shot classifier
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Updated intent labels
INTENT_LABELS = [
    "fact-based question",
    "yes or no question",
    "time-related question",
    "insightful question",
    "spiritual guidance",
    "general inquiry"
]

# Mapping verbose labels to internal labels
label_map = {
    "fact-based question": "factual",
    "yes or no question": "yes_no",
    "time-related question": "timeline",
    "insightful question": "insight",
    "spiritual guidance": "guidance",
    "general inquiry": "general"
}

def normalize(text: str) -> str:
    """Clean input: lowercase, strip, remove extra spaces."""
    return ' '.join(text.lower().strip().split())

@lru_cache(maxsize=1000)
def classify_intent_cached(question: str) -> str:
    question = normalize(question)
    result = classifier(question, INTENT_LABELS)

    print(f"[DEBUG] Intent Scores for '{question}':")
    for label, score in zip(result["labels"], result["scores"]):
        print(f"→ {label}: {score:.2f}")

    labels = result["labels"]
    scores = result["scores"]
    top_label = labels[0]
    top_score = scores[0]

    # ✅ Define this BEFORE usage
    factual_label = "fact-based question"

    # ✅ Add rule for WH-questions
    maybe_factual = question.startswith(("what", "how", "when", "where", "who"))

    # ✅ Rule-based override for factual
    if maybe_factual and top_label != factual_label and factual_label in labels:
        idx = labels.index(factual_label)
        if scores[idx] >= 0.2:  # relaxed threshold
            return label_map[factual_label]

    # Optional override: boost "factual" if it's close to the top
    if factual_label in labels:
        idx = labels.index(factual_label)
        if scores[idx] >= 0.6 and (top_score - scores[idx]) < 0.1:
            return label_map[factual_label]

    return label_map.get(top_label, "general")  # fallback to general
