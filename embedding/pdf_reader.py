import pdfplumber
import chromadb
from config import PDF_PATHS, VECTOR_DB_DIR
from chromadb.utils import embedding_functions

class TarotPDFEmbedder:
    def __init__(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", collection_name="tarot_knowledge"):
        self.chroma_client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embed_fn
        )

    def extract_paragraphs(self):
        paragraphs = []
        for path in PDF_PATHS:
            print(f"\n📄 Reading file: {path}")
            with pdfplumber.open(path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        # Split text by double newlines, Hindi-safe
                        chunks = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 40]
                        # print(f"✅ Page {i+1} → {len(chunks)} chunks found")
                        paragraphs.extend(chunks)
        return paragraphs

    def build_vector_store(self):
        paragraphs = self.extract_paragraphs()
        ids = [f"chunk_{i}" for i in range(len(paragraphs))]

        # 🧪 Print embeddings for Hindi & English
        # print("\n🧪 Sample embeddings:")

        for i, para in enumerate(paragraphs[:10]):
            if 'भारत' in para or 'है' in para:
                # print(f"\n🈳 Hindi sample text:\n{para}")
                emb = self.embed_fn([para])[0]
                # print(f"➡️ Embedding: {emb[:5]}...")  # show first 5 dimensions
                break

        for i, para in enumerate(paragraphs[:10]):
            if 'the' in para or 'is' in para:
                # print(f"\n🇬🇧 English sample text:\n{para}")
                emb = self.embed_fn([para])[0]
                # print(f"➡️ Embedding: {emb[:5]}...")  # show first 5 dimensions
                break

        # ✅ Now index to vector DB if not already
        if self.collection.count() == 0:
            self.collection.add(documents=paragraphs, ids=ids)
            print(f"🔗 Indexed {len(paragraphs)} chunks from {len(PDF_PATHS)} PDFs.")
        else:
            print(f"ℹ️ Collection already contains {self.collection.count()} chunks.")

    def retrieve(self, query, top_k=3):
        result = self.collection.query(query_texts=[query], n_results=top_k)
        return result["documents"][0] if result["documents"] else []
    


     # def build_vector_store(self):
    #     paragraphs = self.extract_paragraphs()
    #     ids = [f"chunk_{i}" for i in range(len(paragraphs))]

    #     if self.collection.count() == 0:
    #         self.collection.add(documents=paragraphs, ids=ids)
    #         print(f"🔗 Indexed {len(paragraphs)} chunks from {len(PDF_PATHS)} PDFs.")
    #     else:
    #         print(f"ℹ️ Collection already contains {self.collection.count()} chunks.")
    