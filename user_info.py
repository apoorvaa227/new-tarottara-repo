
import os
from fpdf import FPDF
from constants import GREETING_EMOJI, SUN_EMOJI

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
