# MODEL_NAME = "llama3"
# VECTOR_DB_DIR = "./tarot_vectordb"
# PDF_PATHS = ["pdf_file/1.pdf", "pdf_file/2.pdf","pdf_file/3.pdf","pdf_file/4.pdf","pdf_file/7.pdf", "pdf_file/sample_hindi.pdf"]
# COLLECTION_NAME = "tarot-index"
# PINECONE_API_KEY="pcsk_3VGwGk_AdeQhYH5nG5McXF3PZoGaweBJTEhFYYoGkisN8Y7CnWjyWJZvLLvSBgVr3nshEk"
# PINECONE_ENV="us-east-1-aws"
# config.py
# config.py
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env for local runs
load_dotenv()

# Universal getter for local + Streamlit Cloud
def get_env(key: str, default=None):
    return st.secrets.get(key, os.getenv(key, default))

# PDF + Embedding Config
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
PDF_PATHS = ["pdf_file/tarot_guide.pdf"]
# config.py
OPENROUTER_API_KEY = get_env("OPENROUTER_API_KEY")


# LLM_MODEL_NAME = "llama3"

# Pinecone Config
PINECONE_API_KEY = get_env("PINECONE_API_KEY")
PINECONE_REGION = get_env("PINECONE_REGION", "us-east-1")
PINECONE_CLOUD = get_env("PINECONE_CLOUD", "aws")
COLLECTION_NAME = get_env("PINECONE_INDEX_NAME", "tarottara-index")

if not PINECONE_API_KEY:
    raise ValueError("❌ PINECONE_API_KEY is missing. Check .env or .streamlit/secrets.toml.")
# Others
ASSEMBLYAI_API_KEY = get_env("ASSEMBLYAI_API_KEY")
ELEVENLABS_API_KEY = get_env("ELEVENLABS_API_KEY")
