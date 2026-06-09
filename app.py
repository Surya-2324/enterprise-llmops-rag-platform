import streamlit as st
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from openai import OpenAI
import uuid

# --- 1. CONFIG & INITIALIZATION ---
st.set_page_config(page_title="PDF Q&A RAG Platform", layout="wide")
model = SentenceTransformer('all-MiniLM-L6-v2') # 384-dim model
qdrant_client = QdrantClient(url=st.secrets["QDRANT_URL"], api_key=st.secrets["QDRANT_API_KEY"])

# --- 2. CORE FUNCTIONS ---
def get_llm_response(prompt, context):
    client = OpenAI(api_key=st.secrets["GEMINI_API_KEY"], base_url="https://generativelanguage.googleapis.com/v1beta/openai")
    messages = [
        {"role": "system", "content": f"Answer based on this context: {context}"},
        {"role": "user", "content": prompt}
    ]
    return client.chat.completions.create(model="gemini-2.5-flash", messages=messages).choices[0].message.content

# --- 3. UI & LOGIC ---
st.title("📄 PDF Intelligent Q&A")

# Mode Selection
mode = st.sidebar.radio("Mode", ["Upload PDF", "Ask Questions"])

if mode == "Upload PDF":
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")
    if uploaded_file and st.button("Process Document"):
        with st.spinner("Processing..."):
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            text = "".join([page.get_text() for page in doc])
            chunks = [text[i:i+800] for i in range(0, len(text), 800)] # 800 char chunks
            
            points = []
            for chunk in chunks:
                points.append({
                    "id": str(uuid.uuid4()),
                    "vector": model.encode(chunk).tolist(),
                    "payload": {"text": chunk}
                })
            qdrant_client.upsert(collection_name="system_architecture", points=points)
            st.success("PDF knowledge added to Qdrant!")

elif mode == "Ask Questions":
    query = st.text_input("Ask a question about your PDF:")
    if query:
        # Search Qdrant
        search_results = qdrant_client.query_points(
            collection_name="system_architecture",
            query=model.encode(query).tolist(),
            limit=3
        ).points
        
        # --- Confidence Score Logic ---
        st.write("### Retrieved Context & Confidence:")
        context = ""
        for hit in search_results:
            confidence = round(hit.score * 100, 2)
            context += hit.payload.get("text", "") + "\n"
            st.write(f"- **Confidence: {confidence}%** | Snippet: {hit.payload.get('text', '')[:100]}...")
        
        # Generate Answer
        with st.spinner("Generating AI response..."):
            answer = get_llm_response(query, context)
            st.write("### AI Answer:")
            st.write(answer)
