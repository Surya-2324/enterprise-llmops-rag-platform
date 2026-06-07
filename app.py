import streamlit as st
from openai import OpenAI
from qdrant_client import QdrantClient

# ... (Keep your existing Qdrant and OpenAI client initializations here) ...

# 🌐 Sidebar Configuration for App Modes
st.sidebar.title("🤖 Platform Settings")
app_mode = st.sidebar.radio(
    "Choose System Intelligence Mode:",
    ["Open-Source (General Knowledge)", "Enterprise RAG (Knowledge Base)"]
)

# ... (Keep your layout title code) ...

# User Input
user_query = st.text_input("Submit system or architecture questions:")

if user_query:
    with st.spinner("Processing request..."):
        
        # 🚀 MODE 1: General Knowledge Mode (Bypass RAG)
       # 🚀 MODE 1: General Knowledge Mode (Bypass RAG)
       # 🚀 MODE 1: General Knowledge Mode (Bypass RAG)
        if app_mode == "Open-Source (General Knowledge)":
            try:
                # Self-contained client initialization
                general_client = OpenAI(
                    api_key=st.secrets["XAI_API_KEY"],
                    base_url="https://api.x.ai/v1"
                )
                
                response = general_client.chat.completions.create(
                    model="grok-2-1212",  # Standard stable production text model identifier
                    messages=[
                        {"role": "system", "content": "You are a helpful, brilliant open-source AI assistant."},
                        {"role": "user", "content": user_query}
                    ]
                )
                st.write(response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"Error calling LLM: {e}")
        # 🔒 MODE 2: Enterprise RAG Mode (Your Original Logic)
        else:
            # Put your existing embedding generation, Qdrant payload search, 
            # and context-augmented LLM prompt logic right here.
            pass
