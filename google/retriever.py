from langchain_chroma import Chroma
from embeddings import get_embeddings
import os
import logging

logger = logging.getLogger(__name__)


def get_retriever(persist_dir=None):
    """
    Load the vector database and return a retriever.

    Args:
        persist_dir: Directory where Chroma DB is stored (default from env)

    Returns:
        Retriever instance

    Raises:
        FileNotFoundError: If vector database doesn't exist
        Exception: If retriever creation fails
    """
    if persist_dir is None:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")

    if not os.path.exists(persist_dir):
        raise FileNotFoundError(
            f"Vector database not found at {persist_dir}. "
            "Please run the ingestion script first to create the database."
        )

    try:
        embeddings = get_embeddings()
        vectordb = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings
        )

        k = int(os.getenv("RETRIEVAL_K", "3"))

        retriever = vectordb.as_retriever(search_kwargs={"k": k})
        logger.info(f"Retriever initialized with k={k}")
        return retriever

    except Exception as e:
        logger.error(f"Failed to create retriever: {e}")
        raise
