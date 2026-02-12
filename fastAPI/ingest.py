"""
Ingestion script to load PDFs, split them, and create vector database.
Run this before starting the FastAPI server.

Usage:
    python ingest.py path/to/document.pdf
    python ingest.py path/to/folder/
"""

import sys
import logging
from pdf_loader import load_path
from text_splitter import split_documents
from vectordb import create_vector_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ingest(path: str):
    """
    Complete ingestion pipeline: load PDF(s) -> split -> create vector DB.

    Args:
        path: Path to PDF file or folder containing PDFs
    """
    try:
        logger.info(f"Starting ingestion for: {path}")
        documents = load_path(path)
        chunks = split_documents(documents)
        vectordb = create_vector_db(chunks)
        logger.info("Ingestion complete! You can now start the FastAPI server.")
        return vectordb
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest.py path/to/document.pdf")
        print("       python ingest.py path/to/folder/")
        sys.exit(1)

    ingest(sys.argv[1])
