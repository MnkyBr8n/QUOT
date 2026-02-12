import streamlit as st
from qa_bot import build_qa_chain

st.title("RAG QA Assistant")

qa = build_qa_chain()

query = st.text_input("Ask a question about the document")

if query:
    result = qa(query)
    st.write("Answer:")
    st.write(result["result"])