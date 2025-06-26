# intent/intent.py

from functools import lru_cache
from intent.classifier import classifier, INTENT_LABELS, label_map

def normalize(text: str) -> str:
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

    factual_label = "fact-based question"
    maybe_factual = question.startswith(("what", "how", "when", "where", "who"))

    if maybe_factual and top_label != factual_label and factual_label in labels:
        idx = labels.index(factual_label)
        if scores[idx] >= 0.2:
            return label_map[factual_label]

    if factual_label in labels:
        idx = labels.index(factual_label)
        if scores[idx] >= 0.6 and (top_score - scores[idx]) < 0.1:
            return label_map[factual_label]

    return label_map.get(top_label, "general")
