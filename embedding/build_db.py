# # build_db.py

# from pdf_reader import TarotPDFEmbedder

# if __name__ == "__main__":
#     embedder = TarotPDFEmbedder()
#     embedder.build_vector_store()


# build_db.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from pdf_reader import TarotPDFEmbedder
from embedding.pdf_reader import TarotPDFEmbedder

from config import PDF_PATHS  

if __name__ == "__main__":
    embedder = TarotPDFEmbedder()
    embedder.build_vector_store()
