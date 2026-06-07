import streamlit as st
from qdrant_client import QdrantClient
from openai import OpenAI

# 🏠 Page & UI Configurations
st.set_page_config(page_title="Enterprise LLMOps Platform", layout="wide")
st.title("🤖 Enterprise Cloud-Native RAG Platform Core")
st.markdown("---")

# 🔒 Production Secret Management
# Streamlit will pull these securely from your dashboard environment variables
QDRANT_URL = st.secrets["QDRANT_URL"]
QDRANT_API_KEY = st.secrets["QDRANT_API_KEY"]
XAI_API_KEY = st.secrets["XAI_API_KEY"]

# Initialize enterprise cloud clients
@st.cache_resource
def init_clients():
    q_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    # Grok uses the standard OpenAI client layout targeting xAI's endpoint
    grok_client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.xai.ai/v1")
    return q_client, grok_client

try:
    qdrant, grok = init_clients()
except Exception as e:
    st.error(f"Infrastructure initialization failed: {e}")
    st.stop()

query = st.text_input("Submit production system or architecture questions:", placeholder="e.g., How do I secure my vector store databases?")

if query:
    with st.spinner("Executing semantic database lookup and Grok model synthesis..."):
        try:
            # 1. Generate text embeddings locally on Streamlit's server
            from sentence_transformers import SentenceTransformer
            @st.cache_resource
            def load_embedder():
                return SentenceTransformer("all-MiniLM-L6-v2")
            
            embedder = load_embedder()
            query_vector = embedder.encode(query).tolist()
            
            # 2. Query your live Cloud Qdrant cluster
            search_result = qdrant.search(
                collection_name="system_architecture",
                query_vector=query_vector,
                limit=1
            )
            
            if search_result:
                matched_context = search_result[0].payload.get("text", "No text payload found.")
                similarity_score = search_result[0].score
            else:
                matched_context = "No direct documentation context matches found in the cluster."
                similarity_score = 0.0000

            # 3. Formulate prompt with strict production prompt guardrails
            system_prompt = (
                "You are an elite Enterprise Solutions Architect. Synthesize a concise, technical "
                "response using only the provided reference context. If the context does not contain "
                "the answer, rely on your core system design knowledge but explicitly state where "
                "the internal documentation falls short. Maintain an authoritative tone."
            )
            
            user_payload = f"Context:\n{matched_context}\n\nQuestion: {query}"

            # 4. Fire direct inference payload to xAI Grok Engine
            response = grok.chat.completions.create(
                model="grok-2-1212", # Accessing xAI's flagship reasoning model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_payload}
                ],
                temperature=0.2
            )
            answer = response.choices[0].message.content

            # 🎛️ Render production metrics and layout
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Grok Model Synthesis Output")
                st.success(answer)
                
            with col2:
                st.subheader("Cloud Tracking Metrics")
                st.metric(label="Retrieval Confidence Score", value=f"{similarity_score:.4f}")
                st.subheader("Retrieved Cloud Node Context")
                st.caption(f"Source Match: \n\"{matched_context}\"")
                
        except Exception as e:
            st.error(f"Pipeline Execution Error: {e}")