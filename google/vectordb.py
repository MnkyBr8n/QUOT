from langchain_chroma import Chroma
from embeddings import get_embeddings
import os
import logging

logger = logging.getLogger(__name__)


def create_vector_db(chunks, persist_dir=None):
    """
    Create a vector database from document chunks.

    Args:
        chunks: List of document chunks to embed
        persist_dir: Directory to save the database (default from env)

    Returns:
        Chroma vector database instance

    Raises:
        Exception: If database creation fails
    """
    if persist_dir is None:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")

    try:
        embeddings = get_embeddings()
        logger.info(f"Creating vector database with {len(chunks)} chunks")

        vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_dir
        )

        # Note: persist() is deprecated, Chroma auto-persists with persist_directory
        logger.info(f"Vector database created at {persist_dir}")
        return vectordb

    except Exception as e:
        logger.error(f"Failed to create vector database: {e}")
        raise
