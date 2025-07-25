# # MODEL_NAME = "llama3"
# # VECTOR_DB_DIR = "./tarot_vectordb"
# # PDF_PATHS = ["pdf_file/1.pdf", "pdf_file/2.pdf","pdf_file/3.pdf","pdf_file/4.pdf","pdf_file/7.pdf", "pdf_file/sample_hindi.pdf"]
# # COLLECTION_NAME = "tarot-index"
# # PINECONE_API_KEY="pcsk_3VGwGk_AdeQhYH5nG5McXF3PZoGaweBJTEhFYYoGkisN8Y7CnWjyWJZvLLvSBgVr3nshEk"
# # PINECONE_ENV="us-east-1-aws"
# # config.py
# # config.py
# import os
# from dotenv import load_dotenv
# import streamlit as st

# # Load environment variables from .env for local runs
# load_dotenv()

# # Universal getter for local + Streamlit Cloud
# def get_env(key: str, default=None):
#     return st.secrets.get(key, os.getenv(key, default))

# # PDF + Embedding Config
# EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# PDF_PATHS = ["pdf_file/tarot_guide.pdf"]
# # config.py
# import streamlit as st

# OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

# # OPENROUTER_API_KEY = get_env("OPENROUTER_API_KEY")
# GROQ_API_KEY = get_env("GROQ_API_KEY")
# if not GROQ_API_KEY:
#     raise ValueError("❌ GROQ_API_KEY not found in environment. Please set it in your .env file.")

# # LLM_MODEL_NAME = "llama3"

# # Pinecone Config
# PINECONE_API_KEY = get_env("PINECONE_API_KEY")
# PINECONE_REGION = get_env("PINECONE_REGION", "us-east-1")
# PINECONE_CLOUD = get_env("PINECONE_CLOUD", "aws")
# COLLECTION_NAME = get_env("PINECONE_INDEX_NAME", "tarottara-index")

# if not PINECONE_API_KEY:
#     raise ValueError("❌ PINECONE_API_KEY is missing. Check .env or .streamlit/secrets.toml.")
# # Others
# ASSEMBLYAI_API_KEY = get_env("ASSEMBLYAI_API_KEY")
# ELEVENLABS_API_KEY = get_env("ELEVENLABS_API_KEY")

import os
from dotenv import load_dotenv

# Load environment variables from .env (for local dev)
load_dotenv()

# Universal getter (works both locally and on Streamlit Cloud)
def get_env(key: str, default=None):
    return os.getenv(key, default)


# LLM / API Keys
# OPENROUTER_API_KEY = get_env("OPENROUTER_API_KEY")  # No longer needed, using Groq
GROQ_API_KEY = get_env("GROQ_API_KEY")

# if not OPENROUTER_API_KEY:
#     raise ValueError("❌ OPENROUTER_API_KEY not found. Check .env or secrets.toml.")
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found. Check .env or secrets.toml.")


# Pinecone Config
PINECONE_API_KEY = get_env("PINECONE_API_KEY")
PINECONE_REGION = get_env("PINECONE_REGION", "us-east-1")
PINECONE_CLOUD = get_env("PINECONE_CLOUD", "aws")
COLLECTION_NAME = get_env("PINECONE_INDEX_NAME", "tarottara-index")

if not PINECONE_API_KEY:
    raise ValueError("❌ PINECONE_API_KEY missing. Check .env or secrets.toml.")


# Embeddings + PDF
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
PDF_PATHS = ["pdf_file/tarot_guide.pdf"]


# Voice Services
ASSEMBLYAI_API_KEY = get_env("ASSEMBLYAI_API_KEY")
ELEVENLABS_API_KEY = get_env("ELEVENLABS_API_KEY")
ELEVENLABS_API_KEY = get_env("ELEVENLABS_API_KEY")
