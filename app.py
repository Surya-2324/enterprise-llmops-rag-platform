import streamlit as st
from openai import OpenAI
from qdrant_client import QdrantClient

# --- Configuration & Initialization ---
st.set_page_config(page_title="Enterprise AI Platform", layout="wide")

# Initialize Qdrant Client
qdrant_client = QdrantClient(
    url=st.secrets["QDRANT_URL"],
    api_key=st.secrets["QDRANT_API_KEY"]
)

# --- Unified Helper Function ---
def get_llm_response(prompt, context=None):
    client = OpenAI(
        api_key=st.secrets["GEMINI_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai"
    )
    
    system_instruction = "You are a helpful, brilliant Enterprise AI assistant."
    if context:
        system_instruction = f"Use this retrieved enterprise context to answer the user: {context}"
        
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# --- UI Layout ---
st.title("🏢 Enterprise LLMOps Platform")
st.sidebar.title("🤖 Platform Settings")
app_mode = st.sidebar.radio(
    "Choose System Intelligence Mode:",
    ["Open-Source (General Knowledge)", "Knowledge Base Retrieval (RAG)"]
)

user_query = st.text_input("Submit system or architecture questions:")

# --- Core Logic ---
if user_query:
    with st.chat_message("user"):
        st.write(user_query)

    try:
        # MODE 1: General Knowledge
        if app_mode == "Open-Source (General Knowledge)":
            with st.spinner("🧠 Generating general response..."):
                answer = get_llm_response(user_query)
                with st.chat_message("assistant"):
                    st.write(answer)

        # MODE 2: RAG Pipeline
        elif app_mode == "Knowledge Base Retrieval (RAG)":
            with st.spinner("🔍 Retrieving from Vector DB..."):
                # Updated to use 'query_points' instead of 'search'
                search_results = qdrant_client.query_points(
                    collection_name="enterprise_knowledge",
                    query=[0.0] * 1536, # Ensure this size matches your embedding dimensions
                    limit=3
                ).points
                
                # Extract text from payloads
                retrieved_context = "\n".join([hit.payload.get("text", "") for hit in search_results if hit.payload])
                
                if not retrieved_context:
                    retrieved_context = "No specific enterprise documentation found."
                
                answer = get_llm_response(user_query, context=retrieved_context)
                
                with st.chat_message("assistant"):
                    st.write(answer)
                    with st.expander("🛠️ View RAG Context & Metadata"):
                        st.json([hit.payload for hit in search_results])

    except Exception as e:
        st.error(f"Pipeline Error: {e}")
