from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import requests
import uuid
import os

client = QdrantClient(url="http://localhost:6333")
GATEWAY_EMBED_URL = "http://localhost:4000/v1/embeddings"
COLLECTION_NAME = "tech_docs"
VECTOR_DIMENSION = 768

# Create raw data source directory if missing
DATA_DIR = "./knowledge_base"
os.makedirs(DATA_DIR, exist_ok=True)

if not client.collection_exists(collection_name=COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_DIMENSION, distance=Distance.COSINE)
    )

def chunk_text(text: str, max_chars: int = 500) -> list:
    """Splits raw unstructured logs or text documents cleanly by sentences/paragraphs."""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chars:
            current_chunk += para + "\n\n"
        else:
            if current_chunk: chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    return [c for c in chunks if c]

def get_embedding(text: str):
    response = requests.post(GATEWAY_EMBED_URL, json={"model": "local-embeddings", "input": text})
    return response.json()["data"][0]["embedding"] if response.status_code == 200 else None

def ingest_all_files():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.txt')]
    if not files:
        print(f"No source files detected inside '{DATA_DIR}/'. Creating a sample reference file now...")
        with open(os.path.join(DATA_DIR, "mlops_guide.txt"), "w") as f:
            f.write("Model serving monitoring systems track operational latencies and error anomaly spikes.\n\nDatabase automatic snapshots should run every 24 hours to secure vector stores against unexpected service host crashes.")
        files = os.listdir(DATA_DIR)

    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)
        print(f"\nProcessing file: {filename}...")
        with open(filepath, "r", encoding="utf-8") as f:
            raw_content = f.read()
            
        chunks = chunk_text(raw_content)
        print(f"Generated {len(chunks)} contextual chunks for indexing.")
        
        points = []
        for chunk in chunks:
            vector = get_embedding(chunk)
            if vector:
                points.append(PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={"text": chunk, "source": filename}
                ))
        
        if points:
            client.upsert(collection_name=COLLECTION_NAME, points=points)
            print(f"✓ Indexed {len(points)} nodes from '{filename}' into Qdrant.")

if __name__ == "__main__":
    ingest_all_files()