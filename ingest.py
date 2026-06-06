from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import requests
import uuid

# Connect to Qdrant and LiteLLM Gateway
client = QdrantClient(url="http://localhost:6333")
GATEWAY_EMBED_URL = "http://localhost:4000/v1/embeddings"
COLLECTION_NAME = "tech_docs"

# Nomic-embed-text produces high-quality 768-dimensional vectors
VECTOR_DIMENSION = 768 

if not client.collection_exists(collection_name=COLLECTION_NAME):
    print(f"Creating collection: {COLLECTION_NAME}...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_DIMENSION, distance=Distance.COSINE)
    )

def get_embedding(text: str):
    response = requests.post(
        GATEWAY_EMBED_URL,
        json={"model": "local-embeddings", "input": text}
    )
    if response.status_code == 200:
        return response.json()["data"][0]["embedding"]
    else:
        raise Exception(f"Gateway Embedding Error: {response.text}")

# Sample chunk processing execution
sample_text = "MLOps pipelines automate model monitoring, data drift tracking, and container retraining tasks."
print("Requesting embedding from LiteLLM Gateway...")
vector = get_embedding(sample_text)

print("Upserting vector point into Qdrant index...")
client.upsert(
    collection_name=COLLECTION_NAME,
    points=[
        PointStruct(id=str(uuid.uuid4()), vector=vector, payload={"text": sample_text})
    ]
)
print("? Ingestion successful!")
