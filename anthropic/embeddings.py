from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

def get_embeddings():
    """
    Get Google Gemini embeddings for Claude RAG.

    Anthropic doesn't provide embeddings, so we use Google's.

    Requires .env file with:
    - GOOGLE_API_KEY

    Returns:
        GoogleGenerativeAIEmbeddings instance

    Raises:
        ValueError: If API key is missing
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY in .env file")

    model = os.getenv("EMBEDDING_MODEL", "models/embedding-001")

    return GoogleGenerativeAIEmbeddings(
        google_api_key=api_key,
        model=model
    )
