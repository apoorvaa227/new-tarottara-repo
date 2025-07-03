# MODEL_NAME = "llama3"
# VECTOR_DB_DIR = "./tarot_vectordb"
# PDF_PATHS = ["pdf_file/1.pdf", "pdf_file/2.pdf","pdf_file/3.pdf","pdf_file/4.pdf","pdf_file/7.pdf", "pdf_file/sample_hindi.pdf"]
# COLLECTION_NAME = "tarot-index"
# PINECONE_API_KEY="pcsk_3VGwGk_AdeQhYH5nG5McXF3PZoGaweBJTEhFYYoGkisN8Y7CnWjyWJZvLLvSBgVr3nshEk"
# PINECONE_ENV="us-east-1-aws"
# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# PDF + Embedding Config
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
PDF_PATHS = ["pdf_file/tarot_guide.pdf"]
LLM_MODEL_NAME = "llama3" 
# // earlier in chroma db
# VECTOR_DB_DIR = "./tarot_vectordb"

# Pinecone Config
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
# Others (if needed)
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
COLLECTION_NAME = os.getenv("PINECONE_INDEX_NAME", "tarottara-index")
