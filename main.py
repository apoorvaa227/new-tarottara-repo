import os
import time
import base64
import traceback
from fpdf import FPDF
from playsound import playsound
from intent.intent import classify_intent_cached
from tarot.tarot_reader import cached_reading
from voice.input import record_from_mic, transcribe_audio
from voice.output import synthesize_voice, play_voice_response
from utils.language_detection import detect_language_with_groq, get_language_name, normalize_language_for_translation
from deep_translator import GoogleTranslator
from user_info.user_info import collect_user_info  
from utils.decorators import log_timing

# Add the new multimodal import
from utils.llm_chat import process_image_with_question

def debug_log_error(context: str, error: Exception):
    print(f"❌ [{context}] Exception: {error}")
    print(traceback.format_exc())
    if hasattr(error, 'response') and error.response is not None:
        try:
            print("🔎 Response content:", error.response.text)
        except Exception as parse_error:
            print("⚠️ Could not parse error response:", parse_error)

def main():
    print("\U0001f52e Welcome to TarotTara – your magical tarot guide (type 'exit' to quit)\n")
    
    # Collect mandatory user info
    user_info = collect_user_info()
    user_name = user_info["name"]
    user_gender = user_info["gender"]
    user_language = user_info["language"]

    print(f"\n✨ Thank you {user_name}! How can I help you today?\n")

    while True:
        print("\n🎧 You may (1) Speak into mic, (2) Upload audio, (3) Type your question, or (4) Upload image with question.")
        choice = input("Choose input method [1/2/3/4]: ").strip()

        question = None
        image_path = None
        
        if choice == "1":
            question = record_from_mic()
            if not question:
                continue
        elif choice == "2":
            file_path = input("Enter path to audio file (.wav or .mp3): ").strip()
            if not os.path.exists(file_path):
                print("❌ File not found. Please try again.")
                continue
            print("🔁 Transcribing your audio...")
            try:
                with open(file_path, "rb") as f:
                    question = transcribe_audio(f)
                    print(f"✅ You said: {question}")
            except Exception as e:
                print(f"⚠️ Error transcribing audio: {e}")
                continue
        elif choice == "3":
            question = input("\n🧘 Ask your question:\n> ")
        elif choice == "4":
            image_path = input("Enter path to image file (.jpg, .jpeg, .png): ").strip()
            if not os.path.exists(image_path):
                print("❌ Image file not found. Please try again.")
                continue
            question = input("💭 Ask a question about this image: ").strip()
            if not question:
                print("❌ Please enter a question about the image.")
                continue
        else:
            print("❌ Invalid choice. Please select 1, 2, 3, or 4.")
            continue

        if question and question.lower() in {"exit", "quit"}:
            print("🌙 Farewell. Trust the journey ahead.")
            break

        total_start = time.time()

        # Handle image + question with multimodal AI
        if image_path:
            try:
                print("🔍 Analyzing your image and question with AI vision...")
                with open(image_path, "rb") as img_file:
                    image_data = base64.b64encode(img_file.read()).decode('utf-8')
                
                final_answer = process_image_with_question(image_data, question, user_info)
                
                # Translate response to user's language if needed
                if user_language != "en":
                    try:
                        final_answer = GoogleTranslator(source='en', target=user_language).translate(final_answer)
                    except Exception as e:
                        print(f"⚠️ Translation failed: {e}")
                
                print(f"\n🔮 TarotTara's vision for {user_name}:")
                print(final_answer)
                
                total_duration = time.time() - total_start
                print(f"\n⏱️ Total time: {total_duration:.2f} sec")
                continue
                
            except Exception as e:
                debug_log_error("Image Processing", e)
                print(f"⚠️ Error processing image: {e}")
                continue

        # Advanced language detection using Groq
        detected_lang, confidence = detect_language_with_groq(question)
        print(f"🌍 Detected language: {get_language_name(detected_lang)} (confidence: {confidence:.2f})")
        
        # Normalize language for translation
        translation_lang = normalize_language_for_translation(detected_lang)
        translated_question = GoogleTranslator(source=translation_lang, target='en').translate(question) if translation_lang != "en" else question

        # Intent classification
        intent_start = time.time()
        intent = classify_intent_cached(translated_question)
        print(f"\n✨ Intent detected: {intent}")
        intent_duration = time.time() - intent_start
        print(f"\n✨ Intent detected: {intent} (in {intent_duration:.2f} sec)")

        timed_cached_reading = log_timing("🔮 Tarot reading")(cached_reading)
        result, prediction_duration = timed_cached_reading(translated_question, intent, user_name, user_gender, detected_lang)

        if "error" in result:
            debug_log_error("Tarot Reading", e)
            print(f"⚠️ Error: {result['error']}")
            continue

        answer_en = result["interpretation"]

        print(f"\n🔍 TarotTara's reading for {user_name}:")
        if intent == "timeline":
            card = result["card"]
            date_range = result["date_range"]
            print(f"Card: {card}")
            print(f"Timeframe: {date_range[0].strftime('%B %#d')} – {date_range[1].strftime('%B %#d')}")
        elif intent == "factual":
            print(f"\nAnswer for {user_name}:")
        else:
            cards = result.get("cards", [])
            if len(cards) == 1:
                print(f"Card Drawn for {user_name}: {cards[0]}")
            else:
                print(f"Cards Drawn for {user_name}: {', '.join(cards)}")
    
        # Translate back to user's preferred language
        final_answer = GoogleTranslator(source='en', target=user_language).translate(answer_en) if user_language != "en" else answer_en
        print(f"\n🕡 TarotTara to {user_name} ({user_language}):\n{final_answer}")

        total_duration = time.time() - total_start
        print("\n⏱️ Timing Summary:")
        print(f"• Intent classification: {intent_duration:.2f} sec")
        print(f"• Prediction (LLM + RAG): {prediction_duration:.2f} sec")
        print(f"• Total time: {total_duration:.2f} sec")

if __name__ == "__main__":
    main()


