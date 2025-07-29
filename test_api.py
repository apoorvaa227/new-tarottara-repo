import os
from dotenv import load_dotenv
import requests

load_dotenv()

def test_groq_api():
    """Test if GROQ API is working"""
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        print("❌ GROQ_API_KEY not found in environment variables!")
        print("Please create a .env file with your GROQ_API_KEY")
        return False
    
    print(f"✅ Found GROQ_API_KEY: {groq_api_key[:10]}...")
    
    # Test API call
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": "Hello, how are you?"}],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        print("✅ API call successful!")
        print(f"Response: {result['choices'][0]['message']['content']}")
        return True
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False

if __name__ == "__main__":
    test_groq_api() 