import os
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

def split_documents(documents):
    """
    Split documents into chunks for embedding.

    Args:
        documents: List of Document objects to split

    Returns:
        List of split Document chunks
    """
    # Get configuration from environment
    chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "150"))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = splitter.split_documents(documents)
    logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
    return chunks
