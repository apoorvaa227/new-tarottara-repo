import requests
import json
import time
import uuid
import os

# ✅ Update this to your actual deployed endpoint
LAMBDA_URL = "https://call-astro.com/api/ai-tool-analysis"

def send_chat_log(question: str, answer: str, intent_type: str = "general", duration: float = 0.0) -> None:
    """Send chat log (question, answer, intent, etc.) to the logging API."""
    try:
        payload = {
            "session_number": str(uuid.uuid4())[:8],  # or pull from session_id
            "time_duration": str(round(duration * 1000)),  # in milliseconds
            "intent_type": intent_type,
            "question": question,
            "answer": answer,
        }

        response = requests.post(LAMBDA_URL, params=payload, timeout=10)

        if response.status_code == 200:
            print("✅ Log sent to analytics endpoint.")
        else:
            print(f"❌ Failed to send log. Status code: {response.status_code}")

    except Exception as e:
        print(f"❌ Exception while sending log: {e}")

# 🔧 Manual test (can be removed in prod)
if __name__ == "__main__":
    send_chat_log(
        question="Who is the Prime Minister of India?",
        answer="Narendra Damodardas Modi",
        intent_type="factual",
        duration=0.4321
    )
#         print("✅ SUCCESS! Lambda function responded correctly")
#         print("-" * 40)
            
            


# if __name__ == "__main__":
#     test_numerologyAIApp_request()
        
        
   
import requests
import json
import time
import uuid
import os

# ✅ Update this to your actual deployed endpoint
LAMBDA_URL = "https://call-astro.com/api/ai-tool-analysis"

def send_chat_log(question: str, answer: str, intent_type: str = "general", duration: float = 0.0) -> None:
    """Send chat log (question, answer, intent, etc.) to the logging API."""
    try:
        payload = {
            "session_number": str(uuid.uuid4())[:8],  # or pull from session_id
            "time_duration": str(round(duration * 1000)),  # in milliseconds
            "intent_type": intent_type,
            "question": question,
            "answer": answer,
        }

        response = requests.post(LAMBDA_URL, params=payload, timeout=10)

        if response.status_code == 200:
            print("✅ Log sent to analytics endpoint.")
        else:
            print(f"❌ Failed to send log. Status code: {response.status_code}")

    except Exception as e:
        print(f"❌ Exception while sending log: {e}")

# 🔧 Manual test (can be removed in prod)
if __name__ == "__main__":
    send_chat_log(
        question="Who is the Prime Minister of India?",
        answer="Narendra Damodardas Modi",
        intent_type="factual",
        duration=0.4321
    )
    
