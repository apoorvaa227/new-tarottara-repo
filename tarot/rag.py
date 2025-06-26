# import os
# from langchain.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.vectorstores import Chroma
# from config import PDF_PATHS, VECTOR_DB_DIR

# ##

# ##

# def init_vectorstore():
#     if not os.path.exists(VECTOR_DB_DIR):
#         docs = []
#         for path in PDF_PATHS:
#             loader = PyPDFLoader(path)
#             docs.extend(loader.load())

#         splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#         chunks = splitter.split_documents(docs)

#         embeddings = HuggingFaceEmbeddings()
#         vectordb = Chroma.from_documents(chunks, embeddings, persist_directory=VECTOR_DB_DIR)
#         vectordb.persist()
#     else:
#         embeddings = HuggingFaceEmbeddings()
#         vectordb = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)
    
#     return vectordb


# vectordb = init_vectorstore()
# all_docs = vectordb._collection.get()
# for i, doc in enumerate(all_docs['documents']):
#     print(f"\n--- Doc {i+1} ---")
#     print(doc[:200], "...") 

# # Number of documents
# print("Number of documents:", vectordb._collection.count())

# # List all document IDs
# print("Document IDs:", vectordb._collection.get()['ids'])

# # Print all metadata
# all_docs = vectordb._collection.get()
# for i, doc_id in enumerate(all_docs['ids']):
#     print(f"\nDocument #{i+1}")
#     print("ID:", doc_id)
#     print("Metadata:", all_docs['metadatas'][i])
#     print("Content:", all_docs['documents'][i][:200], "...")  # Print first 200 chars only


# print(vectordb)
# def get_card_meaning(card_name: str, k=2):
#     # Search vector DB for most similar chunks
#     docs = vectordb.similarity_search(card_name, k=k)
    
#     if not docs:
#         print(f"[DEBUG] No results for query: '{card_name}'")
#         return "No meaning found for this card."
    
#     print(f"[DEBUG] Top {k} results for '{card_name}':")
#     for i, doc in enumerate(docs):
#         print(f"\n--- Document {i+1} ---")
#         print("Content:", doc.page_content[:200], "...")
#         print("Metadata:", doc.metadata)
    
#     # Join and return the result
#     return "\n\n".join(doc.page_content for doc in docs)

# # import os
# # from langchain.document_loaders import PyPDFLoader
# # from langchain.text_splitter import RecursiveCharacterTextSplitter
# # from langchain.embeddings import HuggingFaceEmbeddings
# # from langchain.vectorstores import Chroma
# # from config import PDF_PATHS, VECTOR_DB_DIR

# # def init_vectorstore():
# #     if not os.path.exists(VECTOR_DB_DIR):
# #         docs = []
# #         for path in PDF_PATHS:
# #             docs.extend(PyPDFLoader(path).load())
# #         chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)
# #         embeddings = HuggingFaceEmbeddings()
# #         db = Chroma.from_documents(chunks, embeddings, VECTOR_DB_DIR)
# #         db.persist()
# #     else:
# #         embeddings = HuggingFaceEmbeddings()
# #         db = Chroma(VECTOR_DB_DIR, embeddings)
# #     return db

# # vectordb = init_vectorstore()

# # def get_card_meaning(card: str, k=2):
# #     docs = vectordb.similarity_search(card, k)
# #     return "\n\n".join(doc.page_content for doc in docs)

# rag.py

from embedding.pdf_reader import TarotPDFEmbedder
from config import VECTOR_DB_DIR, MODEL_NAME

_embedder = TarotPDFEmbedder(model_name="all-MiniLM-L6-v2", collection_name="tarot_cards")

def get_card_meaning(card_name: str, k: int = 3) -> str:
    results = _embedder.retrieve(card_name, top_k=k)
    return "\n\n".join(results)
