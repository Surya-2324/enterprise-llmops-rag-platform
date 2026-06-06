from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
import requests

app = FastAPI(title="Production LLMOps Platform API", version="1.0.0")

# Internal Connections
client = QdrantClient(url="http://localhost:6333")
GATEWAY_URL = "http://localhost:4000/v1"
COLLECTION_NAME = "tech_docs"

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    query: str
    matched_context: str
    similarity_score: float
    answer: str

def get_embedding(text: str):
    response = requests.post(
        f"{GATEWAY_URL}/embeddings",
        json={"model": "local-embeddings", "input": text}
    )
    if response.status_code == 200:
        return response.json()["data"][0]["embedding"]
    raise HTTPException(status_code=500, detail="Gateway embedding error.")

@app.post("/api/rag", response_model=QueryResponse)
async def run_rag_pipeline(request: QueryRequest):
    # 1. Fetch search vector
    query_vector = get_embedding(request.question)
    
    # 2. Qdrant Search
    search_response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=1
    )
    
    if not search_response.points:
        return QueryResponse(
            query=request.question,
            matched_context="N/A",
            similarity_score=0.0,
            answer="No reference documentation available."
        )
        
    point = search_response.points[0]
    context = point.payload.get("text", "")
    score = point.score

    # 3. Grounded Generation (Sharpened to prevent model hesitation)
    prompt = f"""You are an advanced, objective AI MLOps Engineer. Answer the user question accurately and concisely by analyzing the provided documentation context. 

If the exact phrasing isn't present but the answer is clearly implied (such as matching operational intervals, snapshot cadences, or system guidelines), synthesize the answer directly without stating that the context is missing or that you are providing general guidance.

Context Material:
\"\"\"
{context}
\"\"\"

User Question: {request.question}

Expert Answer:"""

    llm_response = requests.post(
        f"{GATEWAY_URL}/chat/completions",
        json={
            "model": "local-llama",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
    )
    
    if llm_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Gateway generation error.")
        
    answer = llm_response.json()['choices'][0]['message']['content']
    
    return QueryResponse(
        query=request.question,
        matched_context=context,
        similarity_score=score,
        answer=answer
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # <-- Change this to 8001
