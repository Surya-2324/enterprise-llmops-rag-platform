from qdrant_client import QdrantClient
import requests

# 1. Connect to infrastructure
client = QdrantClient(url="http://localhost:6333")
GATEWAY_URL = "http://localhost:4000/v1"
COLLECTION_NAME = "tech_docs"

query = "What happens when an engineer pushes code changes to the main branch?"

print(f"User Query: '{query}'")
print("\n[1/3] Converting query to vector via LiteLLM...")

response = requests.post(
    f"{GATEWAY_URL}/embeddings",
    json={"model": "local-embeddings", "input": query}
)

if response.status_code == 200:
    query_vector = response.json()["data"][0]["embedding"]
else:
    raise Exception(f"Gateway Embedding Error: {response.text}")

print("[2/3] Searching Qdrant Vector database for matching context...")
search_response = client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_vector,
    limit=1
)

# Extract text payload from search results
matched_context = ""
for point in search_response.points:
    matched_context = point.payload['text']
    print(f" -> Found match (Score: {point.score:.4f}): '{matched_context}'")

# 2. Complete the loop: Construct our context-grounded prompt template
if matched_context:
    print("\n[3/3] Passing matched context down to Llama for grounded text synthesis...")
    
    prompt = f"""You are an expert AI MLOps Engineer. Answer the user question strictly using the provided documentation text block as your source context knowledge.

Context Material:
{matched_context}

User Question: {query}

Expert Answer:"""

    llm_response = requests.post(
        f"{GATEWAY_URL}/chat/completions",
        json={
            "model": "local-llama",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
    )
    
    print("\n================== SYNTHESIZED RAG GENERATION ==================")
    print(llm_response.json()['choices'][0]['message']['content'])
    print("================================================================")
else:
    print("No matching documentation context was recovered from the vector database index.")
