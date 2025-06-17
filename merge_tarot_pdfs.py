from PyPDF2 import PdfMerger
import os

# Folder containing individual card PDFs
PDF_DIR = "data/tarot_cards"
OUTPUT_FILE = "data/tarot_guide.pdf"

merger = PdfMerger()

for filename in sorted(os.listdir(PDF_DIR)):
    if filename.endswith(".pdf"):
        merger.append(os.path.join(PDF_DIR, filename))

merger.write(OUTPUT_FILE)
merger.close()

print(f"✅ Merged tarot guide created at: {OUTPUT_FILE}")
