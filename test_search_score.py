from qdrant_client import QdrantClient
import requests

# Connect to infrastructure
client = QdrantClient(url="http://localhost:6333")
GATEWAY_URL = "http://localhost:4000/v1"
COLLECTION_NAME = "tech_docs"

# Test with the exact query from your screenshot
query = "how often do i check the database"

print(f"User Query: '{query}'")
print("\n[1/2] Converting query to vector via LiteLLM...")

response = requests.post(
    f"{GATEWAY_URL}/embeddings",
    json={"model": "local-embeddings", "input": query}
)

if response.status_code == 200:
    query_vector = response.json()["data"][0]["embedding"]
else:
    raise Exception(f"Gateway Embedding Error: {response.text}")

print("[2/2] Searching Qdrant Vector database for matching context...")
search_response = client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_vector,
    limit=3
)

# Extract results
print(f"\n📊 TOP 3 RESULTS:\n")
for i, point in enumerate(search_response.points, 1):
    matched_context = point.payload['text']
    score = point.score
    print(f"Result #{i}")
    print(f"  Score: {score:.4f} ⭐")
    print(f"  Context: {matched_context[:100]}...\n")
