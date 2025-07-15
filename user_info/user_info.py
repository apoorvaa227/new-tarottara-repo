
import os
from fpdf import FPDF
from constants import GREETING_EMOJI, SUN_EMOJI
from user_info.pdf_export import save_user_info_as_pdf

def collect_user_info():
    print(f"{GREETING_EMOJI} Welcome to TarotTara! I'm your personal tarot guide.")
    print("📝 Before we begin, I need some information to personalize your reading.\n")
    
    # Make name mandatory
    while True:
        name = input("→ Full Name (required): ").strip()
        if name:
            break
        print("❌ Name is required. Please enter your name.")
    
    # Make gender mandatory for personalized responses
    while True:
        gender = input("→ Gender (M/F/Other) (required): ").strip().upper()
        if gender in ['M', 'F', 'OTHER']:
            break
        print("❌ Please enter M, F, or Other.")
    
    # Optional but recommended fields
    dob = input("→ Date of Birth (DD-MM-YYYY) (optional): ").strip()
    birth_place = input("→ Place of Birth (optional): ").strip()
    birth_time = input("→ Time of Birth (e.g. 03:30 PM) (optional): ").strip()
    
    print(f"\n{GREETING_EMOJI} Hi {name}! How are you feeling today?")
    mood = input("> ").strip()

    print(f"{SUN_EMOJI} How is your day going?")
    day_summary = input("> ").strip()

    # Ask user for their preferred language with more options
    print("\n🌍 Language Selection:")
    print("Choose your preferred language:")
    print("1. English (en)")
    print("2. Hindi (hi)")  
    print("3. Spanish (es)")
    print("4. French (fr)")
    print("5. Tamil (ta)")
    print("6. Telugu (te)")
    print("7. Bengali (bn)")
    print("8. Gujarati (gu)")
    print("9. Marathi (mr)")
    print("10. Kannada (kn)")
    print("11. Malayalam (ml)")
    print("12. Punjabi (pa)")
    
    language_map = {
        "1": "en", "2": "hi", "3": "es", "4": "fr", "5": "ta", 
        "6": "te", "7": "bn", "8": "gu", "9": "mr", "10": "kn",
        "11": "ml", "12": "pa"
    }
    
    while True:
        choice = input("Enter your choice (1-12): ").strip()
        if choice in language_map:
            user_language = language_map[choice]
            break
        print("❌ Invalid choice. Please enter a number between 1-12.")

    user_info = {
        "name": name,
        "gender": gender,
        "dob": dob or "Not provided",
        "birth_place": birth_place or "Not provided", 
        "birth_time": birth_time or "Not provided",
        "mood": mood or "Good",
        "day_summary": day_summary or "Going well",
        "language": user_language
    }

    save_user_info_as_pdf(user_info)
    print(f"\n✨ Thank you {name}! Your information has been saved. Let's begin your tarot journey!")
    return user_info
