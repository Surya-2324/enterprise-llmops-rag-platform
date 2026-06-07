import streamlit as st
from openai import OpenAI
from qdrant_client import QdrantClient

# --- INITIALIZATION ---
# Initialize at the top level so it's available everywhere
try:
    qdrant_client = QdrantClient(
        url=st.secrets["QDRANT_URL"],
        api_key=st.secrets["QDRANT_API_KEY"]
    )
except Exception as e:
    st.error(f"Failed to initialize Qdrant: {e}")
    st.stop()

# --- Helper Functions ---
def get_llm_response(prompt, context=None):
    client = OpenAI(
        api_key=st.secrets["GEMINI_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai"
    )
    system_instruction = "You are a helpful, brilliant Enterprise AI assistant."
    if context:
        system_instruction = f"Use this retrieved enterprise context to answer: {context}"
        
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# --- UI Layout ---
st.set_page_config(page_title="Enterprise AI Platform", layout="wide")
st.title("🏢 Enterprise LLMOps Platform")
app_mode = st.sidebar.radio("Choose Mode:", ["Open-Source (General Knowledge)", "Knowledge Base Retrieval (RAG)"])

user_query = st.text_input("Submit your question:")

# --- Core Logic ---
if user_query:
    with st.chat_message("user"):
        st.write(user_query)

    try:
        if app_mode == "Open-Source (General Knowledge)":
            with st.spinner("🧠 Generating response..."):
                answer = get_llm_response(user_query)
                with st.chat_message("assistant"):
                    st.write(answer)

        elif app_mode == "Knowledge Base Retrieval (RAG)":
            with st.spinner("🔍 Retrieving from Vector DB..."):
                # Fixed: Correct collection name and dimension (384)
                results = qdrant_client.query_points(
                    collection_name="system_architecture", 
                    query=[0.0] * 384, 
                    limit=3
                ).points
                
                context = "\n".join([hit.payload.get("text", "") for hit in results if hit.payload])
                
                if not context:
                    context = "No specific enterprise documentation found."
                
                answer = get_llm_response(user_query, context=context)
                
                with st.chat_message("assistant"):
                    st.write(answer)
                    with st.expander("🛠️ View Context"):
                        st.json([hit.payload for hit in results])

    except Exception as e:
        st.error(f"Pipeline Error: {e}")
