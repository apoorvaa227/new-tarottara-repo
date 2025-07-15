import time
from transformers import pipeline

# Sample questions with expected intent (for testing accuracy)
TEST_QUESTIONS = [
    ("Will I be rich?", "yes_no"),
    ("What does the future hold?", "insight"),
    ("Tell me something about my career.", "guidance"),
    ("How many planets are there?", "factual"),
    ("When will I get married?", "timeline"),
    ("Tell me a tarot reading.", "general"),
    ("who is the prime minister of India?", "factual"),
]

# The intent labels you want to classify
INTENT_LABELS = [
    "fact-based question",
    "yes or no question",
    "time-related question",
    "insightful question",
    "spiritual guidance",
    "general inquiry"
]

# Mapping to match internal intent types
label_map = {
    "fact-based question": "factual",
    "yes or no question": "yes_no",
    "time-related question": "timeline",
    "insightful question": "insight",
    "spiritual guidance": "guidance",
    "general inquiry": "general"
}

# Models to benchmark
models = [
    "facebook/bart-large-mnli",
    "microsoft/deberta-v3-large-mnli",
    "cross-encoder/nli-roberta-large"
]

def main():
    print("🧪 Benchmarking Models...\n")

    for model_name in models:
        print(f"\n🔍 Model: {model_name}")
        pipe = pipeline("zero-shot-classification", model=model_name)

        correct = 0
        total_time = 0

        for question, expected_intent in TEST_QUESTIONS:
            start = time.time()
            result = pipe(question, INTENT_LABELS)
            duration = time.time() - start

            top_label = result["labels"][0]
            predicted_intent = label_map[top_label]
            is_correct = (predicted_intent == expected_intent)

            if is_correct:
                correct += 1
            total_time += duration

            print(f"Q: {question}")
            print(f"→ Predicted: {predicted_intent}, Expected: {expected_intent}, ✅: {is_correct}, ⏱️: {duration:.2f}s\n")

        avg_latency = total_time / len(TEST_QUESTIONS)
        accuracy = correct / len(TEST_QUESTIONS) * 100

        print(f"✅ Accuracy: {accuracy:.2f}%")
        print(f"⏱️ Average Latency: {avg_latency:.2f} seconds")

# 👇 This ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    main()
