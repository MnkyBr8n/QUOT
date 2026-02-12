import logging

import streamlit as st
from qa_bot_multi import build_qa_chain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.title("RAG QA Assistant (Multi-Provider)")


@st.cache_resource
def get_qa_chain():
    """Build and cache the QA chain"""
    try:
        return build_qa_chain()
    except Exception as e:
        logger.error(f"Failed to build QA chain: {e}")
        st.error("Failed to initialize QA system. Check your .env configuration.")
        return None


qa = get_qa_chain()

if qa is None:
    st.stop()

query = st.text_input("Ask a question about the document")

if query and query.strip():
    with st.spinner("Searching for answer..."):
        try:
            result = qa({"query": query})
            st.write("**Answer:**")
            st.write(result["result"])

            if "source_documents" in result and result["source_documents"]:
                with st.expander("View Sources"):
                    for i, doc in enumerate(result["source_documents"], 1):
                        st.write(f"**Source {i}:**")
                        st.write(doc.page_content[:300] + "...")
        except Exception as e:
            logger.error(f"Query failed: {e}")
            st.error("Failed to process question. Please try again.")
elif query:
    st.warning("Please enter a valid question.")
