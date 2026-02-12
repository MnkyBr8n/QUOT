from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

def get_embeddings():
    """
    Get OpenAI embeddings.

    Requires .env file with:
    - OPENAI_API_KEY

    Returns:
        OpenAIEmbeddings instance

    Raises:
        ValueError: If API key is missing
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY in .env file")

    model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    return OpenAIEmbeddings(
        api_key=api_key,
        model=model
    )
