# # create_index.py
# import os
# from dotenv import load_dotenv
# import pinecone
# load_dotenv()

# api_key = os.getenv("PINECONE_API_KEY")
# env = os.getenv("PINECONE_ENV")
# index_name = os.getenv("PINECONE_INDEX_NAME")


# pinecone.init(api_key=api_key, environment=env)

# # Create index
# if index_name not in pinecone.list_indexes():
#     pinecone.create_index(name=index_name, dimension=384, metric="cosine")
#     print(f"✅ Created new index: {index_name}")
# else:
#     print(f"⚠️ Index {index_name} already exists")

import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key and other configs
api_key = os.getenv("PINECONE_API_KEY")
env_region = os.getenv("PINECONE_REGION", "us-east-1")  # default region if not in .env
index_name = "tarot-index"  # your desired index name

# Initialize Pinecone client
pc = Pinecone(api_key=api_key)

# Check if index exists
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,  # use correct embedding dimension (e.g., 384 for Sentence Transformers)
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region=env_region
        )
    )
    print(f"Index '{index_name}' created.")
else:
    print(f"Index '{index_name}' already exists.")
