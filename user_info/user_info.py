
import os
from fpdf import FPDF
from constants import GREETING_EMOJI, SUN_EMOJI
from user_info.pdf_export import save_user_info_as_pdf
def collect_user_info():
    print(f"{GREETING_EMOJI} Hi, how are you?")
    mood = input("> ")

    print(f"{SUN_EMOJI} How is your day going?")
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
