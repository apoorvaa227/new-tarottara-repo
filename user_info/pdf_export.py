# user_info/pdf_export.py

import os
from fpdf import FPDF

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
