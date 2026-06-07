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
      # 🚀 MODE 1: General Knowledge Mode (Bypass RAG)
        # 🚀 MODE 1: General Knowledge Mode (Bypass RAG)
   # 🚀 MODE 1: General Knowledge Mode (Bypass RAG)
        # 🚀 MODE 1: General Knowledge Mode (Bypass RAG)
      # 🚀 MODE 1: General Knowledge Mode (Bypass RAG)
      # 🚀 MODE 1: General Knowledge Mode (Bypass RAG)
    # 🚀 MODE 1: General Knowledge Mode (Bypass RAG)
      # 🚀 MODE 1: General Knowledge Mode (Bypass RAG)
      # --- Unified Helper Function ---
def get_llm_response(prompt, context=None):
    client = OpenAI(
        api_key=st.secrets["GEMINI_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai"
    )
    
    # If context is provided, we are in RAG mode; otherwise, General mode.
    system_instruction = "You are a helpful Enterprise AI assistant."
    if context:
        system_instruction = f"Use this retrieved context to answer: {context}"
        
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# --- Main App Logic ---
if user_query:
    with st.chat_message("user"):
        st.write(user_query)

    try:
        # MODE 1: General Knowledge
        if app_mode == "Open-Source (General Knowledge)":
            with st.spinner("🧠 Thinking..."):
                answer = get_llm_response(user_query)
                with st.chat_message("assistant"):
                    st.write(answer)

        # MODE 2: RAG Pipeline
        elif app_mode == "Knowledge Base Retrieval (RAG)":
            with st.spinner("🔍 Retrieving from Vector DB..."):
                # Search Qdrant
                search_results = qdrant_client.search(
                    collection_name="enterprise_knowledge",
                    query_vector=[0.1] * 1536, # Ensure this matches your embedding size
                    limit=3
                )
                retrieved_context = "\n".join([hit.payload.get("text", "") for hit in search_results if hit.payload])
                
                # Get RAG Answer
                answer = get_llm_response(user_query, context=retrieved_context)
                
                with st.chat_message("assistant"):
                    st.write(answer)
                    with st.expander("🛠️ View RAG Context"):
                        st.json([hit.payload for hit in search_results])

    except Exception as e:
        st.error(f"Error: {e}")
            except Exception as e:
                st.error(f"Error calling LLM: {e}")
        # 🔒 MODE 2: Enterprise RAG Mode (Your Original Logic)
        else:
            # Put your existing embedding generation, Qdrant payload search, 
            # and context-augmented LLM prompt logic right here.
            pass
