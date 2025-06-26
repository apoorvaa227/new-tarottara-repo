from embedding.pdf_reader import TarotPDFEmbedder

embedder = TarotPDFEmbedder()

query = "प्यार में सफलता कैसे मिले?"  # Hindi query
results = embedder.retrieve(query)

print("\n🔍 Top Matching Chunks:")
for i, chunk in enumerate(results):
    print(f"{i+1}. {chunk}")
