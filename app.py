import streamlit as st
import requests

st.set_page_config(page_title="Enterprise LLMOps Platform", layout="wide")
st.title("🤖 Enterprise RAG Platform Engineering Core")
st.markdown("---")

query = st.text_input("Submit production system or architecture questions:", placeholder="e.g., How do I secure my vector store databases?")

if query:
    with st.spinner("Executing semantic database lookup and model synthesis..."):
        try:
            res = requests.post("http://localhost:8001/api/rag", json={"question": query})
            if res.status_code == 200:
                data = res.json()
                
                # Layout columns
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("Model Synthesis Output")
                    st.info(data["answer"])
                    
                with col2:
                    st.subheader("Infrastructure Tracking Metrics")
                    st.metric(label="Retrieval Confidence Score", value=f"{data['similarity_score']:.4f}")
                    st.subheader("Retrieved Reference Node Context")
                    st.caption(f"Source String Match: \n\"{data['matched_context']}\"")
            else:
                st.error("API Gateway returned an evaluation error code.")
        except Exception as e:
            st.error(f"Could not connect to the FastAPI backend service: {e}")