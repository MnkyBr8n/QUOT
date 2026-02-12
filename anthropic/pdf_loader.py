import os
import logging
from langchain_community.document_loaders import PyPDFLoader

logger = logging.getLogger(__name__)

def load_pdf(path: str):
    """
    Load a PDF document and return its content as documents.
    
    Args:
        path: Path to the PDF file
        
    Returns:
        List of Document objects
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        Exception: If PDF loading fails
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"PDF file not found: {path}")
    
    if not path.lower().endswith('.pdf'):
        raise ValueError(f"File must be a PDF: {path}")
    
    try:
        logger.info(f"Loading PDF: {path}")
        loader = PyPDFLoader(path)
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} pages from PDF")
        return documents
    except Exception as e:
        logger.error(f"Failed to load PDF: {e}")
        raise


def load_pdfs_from_folder(folder_path: str):
    """
    Load all PDF documents from a folder and return their content.

    Args:
        folder_path: Path to the folder containing PDF files

    Returns:
        List of Document objects from all PDFs
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    if not os.path.isdir(folder_path):
        raise ValueError(f"Path is not a folder: {folder_path}")

    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

    if not pdf_files:
        raise ValueError(f"No PDF files found in folder: {folder_path}")

    logger.info(f"Found {len(pdf_files)} PDF files in {folder_path}")

    all_documents = []
    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        try:
            documents = load_pdf(pdf_path)
            all_documents.extend(documents)
        except Exception as e:
            logger.warning(f"Failed to load {pdf_file}: {e}")
            continue

    logger.info(f"Total loaded: {len(all_documents)} pages from {len(pdf_files)} PDFs")
    return all_documents


def load_path(path: str):
    """
    Load PDFs from a file or folder path.

    Args:
        path: Path to a PDF file or folder containing PDFs

    Returns:
        List of Document objects
    """
    if os.path.isdir(path):
        return load_pdfs_from_folder(path)
    else:
        return load_pdf(path)