"""
Ingestion script to load PDFs, split them, and create vector database.
Run this before starting the Streamlit app.

Usage:
    python ingest.py path/to/document.pdf
"""

import sys
import logging
from pdf_loader import load_pdf
from text_splitter import split_documents
from vectordb import create_vector_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ingest_pdf(pdf_path: str):
    """
    Complete ingestion pipeline: load PDF -> split -> create vector DB.
    
    Args:
        pdf_path: Path to PDF file to ingest
    """
    try:
        # Load PDF
        logger.info(f"Starting ingestion for: {pdf_path}")
        documents = load_pdf(pdf_path)
        
        # Split documents
        chunks = split_documents(documents)
        
        # Create vector database
        vectordb = create_vector_db(chunks)
        
        logger.info("✓ Ingestion complete! You can now run the Streamlit app.")
        return vectordb
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest.py path/to/document.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    ingest_pdf(pdf_path)
