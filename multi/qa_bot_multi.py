"""
Multi-provider QA bot module.
Supports: Watsonx, OpenAI, Anthropic, Google Gemini
"""

from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from retriever import get_retriever
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Load .env from this module's directory
load_dotenv(Path(__file__).parent / ".env", override=True)

logger = logging.getLogger(__name__)

_DOCUMENT_PROMPT = PromptTemplate(
    input_variables=["page_content"],
    template="<document>\n{page_content}\n</document>",
)
_QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "Answer the question using only the context below.\n"
        "If the answer is not in the context, say you don't know.\n\n"
        "<context>\n{context}\n</context>\n\n"
        "Question: {question}\n\n"
        "Answer:"
    ),
)


def build_qa_chain():
    """
    Build a RetrievalQA chain with the configured LLM provider.

    Supported providers (set via PROVIDER env var):
    - watsonx: IBM Watsonx
    - openai: OpenAI GPT models
    - anthropic: Anthropic Claude models
    - google: Google Gemini models

    Returns:
        RetrievalQA chain

    Raises:
        ValueError: If provider not supported or credentials missing
        RuntimeError: If chain building fails
    """
    provider = os.getenv("PROVIDER", "watsonx").lower()

    try:
        if provider == "watsonx":
            llm = _get_watsonx_llm()
        elif provider == "openai":
            llm = _get_openai_llm()
        elif provider == "anthropic":
            llm = _get_anthropic_llm()
        elif provider == "google":
            llm = _get_google_llm()
        else:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                "Supported: watsonx, openai, anthropic, google"
            )

        logger.info(f"Initialized LLM: {provider}")

        # Get retriever
        retriever = get_retriever()
        logger.info("Retriever loaded successfully")

        # Build QA chain
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={
                "prompt": _QA_PROMPT,
                "document_prompt": _DOCUMENT_PROMPT,
                "document_variable_name": "context",
            },
        )

        logger.info("QA chain built successfully")
        return qa

    except Exception as e:
        logger.error(f"Failed to build QA chain: {e}")
        raise RuntimeError(f"QA chain initialization failed: {e}")

def _get_watsonx_llm():
    """Get Watsonx LLM"""
    from langchain_community.llms import WatsonxLLM

    url = os.getenv("WATSONX_URL")
    apikey = os.getenv("WATSONX_APIKEY")
    project_id = os.getenv("WATSONX_PROJECT_ID")

    if not all([url, apikey, project_id]):
        raise ValueError(
            "Missing Watsonx credentials. Set WATSONX_URL, "
            "WATSONX_APIKEY, and WATSONX_PROJECT_ID"
        )

    model_id = os.getenv("LLM_MODEL", "mistralai/mixtral-8x7b-instruct-v01")
    temperature = float(os.getenv("TEMPERATURE", "0.0"))
    max_new_tokens = int(os.getenv("MAX_NEW_TOKENS", "512"))

    return WatsonxLLM(
        model_id=model_id,
        url=url,
        apikey=apikey,
        project_id=project_id,
        params={
            "temperature": temperature,
            "max_new_tokens": max_new_tokens
        }
    )

def _get_openai_llm():
    """Get OpenAI LLM"""
    from langchain_openai import ChatOpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY in .env file")

    model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    temperature = float(os.getenv("TEMPERATURE", "0.0"))
    max_tokens = int(os.getenv("MAX_NEW_TOKENS", "512"))

    return ChatOpenAI(
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )

def _get_anthropic_llm():
    """Get Anthropic Claude LLM"""
    from langchain_anthropic import ChatAnthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("Missing ANTHROPIC_API_KEY in .env file")

    model = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")
    temperature = float(os.getenv("TEMPERATURE", "0.0"))
    max_tokens = int(os.getenv("MAX_NEW_TOKENS", "512"))

    return ChatAnthropic(
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )

def _get_google_llm():
    """Get Google Gemini LLM"""
    from langchain_google_genai import ChatGoogleGenerativeAI

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY in .env file")

    model = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    temperature = float(os.getenv("TEMPERATURE", "0.0"))
    max_tokens = int(os.getenv("MAX_NEW_TOKENS", "512"))

    return ChatGoogleGenerativeAI(
        google_api_key=api_key,
        model=model,
        temperature=temperature,
        max_output_tokens=max_tokens
    )

# Provider-specific model recommendations
LLM_MODELS = {
    "watsonx": [
        "mistralai/mixtral-8x7b-instruct-v01",  # Recommended
        "meta-llama/llama-3-70b-instruct",
        "ibm/granite-13b-chat-v2"
    ],
    "openai": [
        "gpt-4-turbo",           # Best quality
        "gpt-4o",                # Fast & quality
        "gpt-3.5-turbo",         # Cheap & fast
    ],
    "anthropic": [
        "claude-3-5-sonnet-20241022",  # Recommended
        "claude-3-opus-20240229",      # Most capable
        "claude-3-haiku-20240307",     # Fastest
    ],
    "google": [
        "gemini-1.5-pro",        # Best quality
        "gemini-1.5-flash",      # Recommended (fast)
        "gemini-1.0-pro"         # Cheaper
    ]
}

def list_llm_models(provider: str = None):
    """List available LLM models for a provider"""
    if provider:
        return LLM_MODELS.get(provider.lower(), [])
    return LLM_MODELS
