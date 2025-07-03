import pdfplumber
import uuid
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from config import (
    PDF_PATHS, PINECONE_API_KEY, PINECONE_REGION, PINECONE_CLOUD,
    COLLECTION_NAME, EMBEDDING_MODEL_NAME
)
from config import get_env

class TarotPDFEmbedder:
    def __init__(self):
        # Init model
        self.embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)

        # Init Pinecone client
        # self.pinecone = Pinecone(api_key=PINECONE_API_KEY)
        # self.pinecone = Pinecone()  # Let it auto-read from env or secrets
          # add this import if not already present

        self.pinecone = Pinecone(api_key=get_env("PINECONE_API_KEY"))

        # Create index if it doesn't exist
        if COLLECTION_NAME not in self.pinecone.list_indexes().names():
            self.pinecone.create_index(
                name=COLLECTION_NAME,
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=PINECONE_CLOUD,
                    region=PINECONE_REGION
                )
            )
            print(f"✅ Created index: {COLLECTION_NAME}")
        else:
            print(f"ℹ️ Index '{COLLECTION_NAME}' already exists")

        self.index = self.pinecone.Index(COLLECTION_NAME)

    def extract_paragraphs(self):
        paragraphs = []
        for path in PDF_PATHS:
            print(f"\n📄 Reading file: {path}")
            with pdfplumber.open(path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        chunks = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 40]
                        paragraphs.extend(chunks)
        return paragraphs

    def build_vector_store(self):
        paragraphs = self.extract_paragraphs()
        print(f"🧠 Total chunks to embed: {len(paragraphs)}")

        batch = []
        for para in paragraphs:
            vector = self.embedder.encode(para).tolist()
            vector_id = str(uuid.uuid4())
            batch.append({
                "id": vector_id,
                "values": vector,
                "metadata": {"text": para}
            })

        # Upsert to Pinecone
        self.index.upsert(vectors=batch)
        print(f"✅ Upserted {len(batch)} chunks to Pinecone index '{COLLECTION_NAME}'.")

    def retrieve(self, query, top_k=3):
        query_vector = self.embedder.encode(query).tolist()
        response = self.index.query(vector=query_vector, top_k=top_k, include_metadata=True)

        if "matches" in response and response["matches"]:
            return [match["metadata"]["text"] for match in response["matches"]]
        return []
