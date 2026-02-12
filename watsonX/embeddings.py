from langchain_huggingface import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

def get_embeddings():
    """
    Get HuggingFace embeddings using sentence-transformers.
    
    Runs locally on your machine - no API key required!
    
    Available models (set via EMBEDDING_MODEL in .env):
    - all-MiniLM-L6-v2: Fast, lightweight (default)
    - all-mpnet-base-v2: Higher quality, slower
    - all-MiniLM-L12-v2: Balance of speed and quality
    
    Returns:
        HuggingFaceEmbeddings instance
    
    Notes:
        - First run downloads the model (~80-400MB depending on model)
        - Models are cached locally for future use
        - No API calls, runs entirely on your machine
        - Free and unlimited usage
    """
    # Get model name from environment or use default
    model_name = os.getenv(
        "EMBEDDING_MODEL", 
        "sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Optional: Use GPU if available (much faster)
    device = os.getenv("DEVICE", "cpu")  # Set to "cuda" for GPU
    
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': device},
        encode_kwargs={'normalize_embeddings': True}
    )

# Model recommendations for different use cases
RECOMMENDED_MODELS = {
    "fast": "sentence-transformers/all-MiniLM-L6-v2",  # 80MB, good quality
    "balanced": "sentence-transformers/all-MiniLM-L12-v2",  # 120MB, better quality
    "quality": "sentence-transformers/all-mpnet-base-v2",  # 420MB, best quality
    "multilingual": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",  # 470MB
}

def get_recommended_model(use_case: str = "fast"):
    """
    Get recommended model name for a specific use case.
    
    Args:
        use_case: One of 'fast', 'balanced', 'quality', 'multilingual'
    
    Returns:
        Model name string
    """
    return RECOMMENDED_MODELS.get(use_case, RECOMMENDED_MODELS["fast"])
