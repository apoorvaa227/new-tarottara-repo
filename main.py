import os
import time
from fpdf import FPDF
from playsound import playsound
from intent import classify_intent_cached
from tarot_reader import cached_reading
from voice_utils import record_from_mic, synthesize_voice, transcribe_audio
from langdetect import detect
from deep_translator import GoogleTranslator

def collect_user_info():
    print("\U0001f52e Hi, how are you?")
    mood = input("> ")

    print("\U0001f31e How is your day going?")
    day_summary = input("> ")

    print("📝 Let me get some information for your reading.")

    name = input("→ Full Name: ")
    dob = input("→ Date of Birth (DD-MM-YYYY): ")
    birth_place = input("→ Place of Birth: ")
    birth_time = input("→ Time of Birth (e.g. 03:30 PM): ")
    gender = input("→ Gender (M/F/Other): ")

    user_info = {
        "name": name,
        "dob": dob,
        "birth_place": birth_place,
        "birth_time": birth_time,
        "gender": gender,
        "day_summary": day_summary,
        "mood": mood,
    }

    save_user_info_as_pdf(user_info)
    return user_info

def save_user_info_as_pdf(info: dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=" TarotTara User Log", ln=True, align="C")
    pdf.ln(10)

    for key, value in info.items():
        pdf.cell(200, 10, txt=f"{key.replace('_', ' ').title()}: {value}", ln=True)

    os.makedirs("user_logs", exist_ok=True)
    filename = f"user_logs/{info['name'].replace(' ', '_')}_log.pdf"
    pdf.output(filename)
    print(f"\n✅ User information saved as: {filename}")

def main():
    print("\U0001f52e Welcome to TarotTara – your magical tarot guide (type 'exit' to quit)\n")
    collect_user_info()

    # Ask user for their preferred language
    user_language = input("Please select your language (en, hi, es, fr): ").strip().lower()
    print("\n✨ Thank you! How can I help you today?\n")

    while True:
        print("\n🎧 You may (1) Speak into mic, (2) Upload audio, or (3) Type your question.")
        choice = input("Choose input method [1/2/3]: ").strip()

        question = None
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
        else:
            print("❌ Invalid choice. Please select 1, 2 or 3.")
            continue

        if question.lower() in {"exit", "quit"}:
            print("🌙 Farewell. Trust the journey ahead.")
            break

        total_start = time.time()

        # Detect language and translate question to English if needed
        from_lang = detect(question)
        translated_question = GoogleTranslator(source='auto', target='en').translate(question) if from_lang != "en" else question

        # Intent classification
        intent_start = time.time()
        intent = classify_intent_cached(translated_question)
        intent_duration = time.time() - intent_start
        print(f"\n✨ Intent detected: {intent} (in {intent_duration:.2f} sec)")

        print(" Drawing cards and interpreting...")
        prediction_start = time.time()
        result = cached_reading(translated_question, intent)
        prediction_duration = time.time() - prediction_start

        if "error" in result:
            print(f"⚠️ Error: {result['error']}")
            continue

        answer_en = result["interpretation"]

        print("\n🔍 TarotTara says:")

        if intent == "timeline":
            card = result["card"]
            date_range = result["date_range"]
            print(f"Card: {card}")
            print(f"Timeframe: {date_range[0].strftime('%B %#d')} – {date_range[1].strftime('%B %#d')}")
        elif intent == "factual":
            print("\nAnswer:")
        else:
            cards = result.get("cards", [])
            print(f"Cards Drawn: {', '.join(cards)}")

        # Translate back to user's preferred language
        final_answer = GoogleTranslator(source='en', target=user_language).translate(answer_en) if user_language != "en" else answer_en
        print(f"\n🕡 TarotTara ({user_language}):\n{final_answer}")

        # Voice generation
        try:
            print("\n🔊 Speaking the response...")
            audio_path = synthesize_voice(final_answer, user_input_lang=user_language)

            if audio_path and os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                playsound(audio_path)
                while True:
                    replay = input("🔁 Do you want to replay the voice response? (y/n): ").strip().lower()
                    if replay == "y":
                        playsound(audio_path)
                    else:
                        break
            else:
                print("⚠️ Audio file not generated properly.")
        except Exception as e:
            print(f"⚠️ Error playing voice response: {e}")

        total_duration = time.time() - total_start
        print("\n⏱️ Timing Summary:")
        print(f"• Intent classification: {intent_duration:.2f} sec")
        print(f"• Prediction (LLM + RAG): {prediction_duration:.2f} sec")
        print(f"• Total time: {total_duration:.2f} sec")

if __name__ == "__main__":
    main()