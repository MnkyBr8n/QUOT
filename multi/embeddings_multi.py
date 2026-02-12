"""
Multi-provider embeddings module.
Supports: Watsonx, OpenAI, Google Gemini

Set EMBEDDING_PROVIDER to override the LLM provider for embeddings.
This is required when PROVIDER=anthropic (no Anthropic embedding API).
Falls back to PROVIDER if EMBEDDING_PROVIDER is not set.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_embeddings():
    """
    Get embeddings based on EMBEDDING_PROVIDER (or PROVIDER) env var.

    Supported embedding providers:
    - watsonx: IBM Watsonx
    - openai: OpenAI
    - google: Google Gemini

    When PROVIDER=anthropic, set EMBEDDING_PROVIDER=openai or
    EMBEDDING_PROVIDER=google and supply the corresponding API key.

    Returns:
        Embeddings instance for the configured provider

    Raises:
        ValueError: If provider is not supported or credentials missing
    """
    provider = os.getenv("EMBEDDING_PROVIDER", os.getenv("PROVIDER", "watsonx")).lower()

    if provider == "watsonx":
        return _get_watsonx_embeddings()
    if provider == "openai":
        return _get_openai_embeddings()
    if provider == "google":
        return _get_google_embeddings()
    raise ValueError(
        f"Unsupported provider: {provider}. "
        "Supported: watsonx, openai, google"
    )


def _get_watsonx_embeddings():
    """Get Watsonx embeddings"""
    from langchain_ibm import WatsonxEmbeddings  # noqa: PLC0415

    model_id = os.getenv("EMBEDDING_MODEL", "ibm/slate-125m-english-rtrvr")
    url = os.getenv("WATSONX_URL")
    apikey = os.getenv("WATSONX_APIKEY")
    project_id = os.getenv("WATSONX_PROJECT_ID")

    if not all([url, apikey, project_id]):
        raise ValueError(
            "Missing Watsonx credentials. Set WATSONX_URL, "
            "WATSONX_APIKEY, and WATSONX_PROJECT_ID"
        )

    return WatsonxEmbeddings(
        model_id=model_id,
        url=url,
        apikey=apikey,
        project_id=project_id
    )


def _get_openai_embeddings():
    """Get OpenAI embeddings"""
    from langchain_openai import OpenAIEmbeddings  # noqa: PLC0415

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY in .env file")

    model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    return OpenAIEmbeddings(
        api_key=api_key,
        model=model
    )


def _get_google_embeddings():
    """Get Google Gemini embeddings"""
    from langchain_google_genai import GoogleGenerativeAIEmbeddings  # noqa: PLC0415

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY in .env file")

    model = os.getenv("EMBEDDING_MODEL", "models/embedding-001")

    return GoogleGenerativeAIEmbeddings(
        google_api_key=api_key,
        model=model
    )


# Provider-specific model recommendations
EMBEDDING_MODELS = {
    "watsonx": [
        "ibm/slate-125m-english-rtrvr",
        "ibm/slate-30m-english-rtrvr"
    ],
    "openai": [
        "text-embedding-3-small",  # Recommended
        "text-embedding-3-large",
        "text-embedding-ada-002"
    ],
    "google": [
        "models/embedding-001",    # Recommended
        "models/text-embedding-004"
    ]
}


def list_embedding_models(provider: str = None):
    """List available embedding models for a provider"""
    if provider:
        return EMBEDDING_MODELS.get(provider.lower(), [])
    return EMBEDDING_MODELS
