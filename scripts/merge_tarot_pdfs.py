from PyPDF2 import PdfMerger
import os

# Folder containing the PDF files listed in config.py
PDF_DIR = "pdf_file"
OUTPUT_FILE = "pdf_file/tarot_guide.pdf"

# Define the filenames you want to merge, in order
pdf_filenames = ["1.pdf", "2.pdf", "3.pdf", "4.pdf", "7.pdf", "sample_hindi.pdf"]

merger = PdfMerger()

for filename in pdf_filenames:
    file_path = os.path.join(PDF_DIR, filename)
    if os.path.exists(file_path):
        merger.append(file_path)
    else:
        print(f"⚠️ File not found: {file_path}")

merger.write(OUTPUT_FILE)
merger.close()
print(f"✅ Merged tarot guide created at: {os.path.abspath(OUTPUT_FILE)}")
print(f"✅ Merged tarot guide created at: {OUTPUT_FILE}")
