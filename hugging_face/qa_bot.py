"""
HuggingFace QA bot module.
Supports both HuggingFace Inference API and local models.

Great for learning, research, and portfolio projects.
"""

from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import HuggingFaceHub, HuggingFacePipeline
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
    Build a RetrievalQA chain with HuggingFace models.

    Two modes (set via USE_LOCAL_MODEL in .env):

    1. API Mode (USE_LOCAL_MODEL=false, default):
       - Uses HuggingFace Inference API
       - Requires HUGGINGFACE_API_KEY
       - Free tier available (rate limited)
       - Models run on HuggingFace servers

    2. Local Mode (USE_LOCAL_MODEL=true):
       - Downloads and runs model on your machine
       - No API key needed
       - Completely free and unlimited
       - Requires good CPU/GPU and RAM

    Returns:
        RetrievalQA chain

    Raises:
        ValueError: If configuration is invalid
        RuntimeError: If chain building fails
    """
    use_local = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"

    try:
        if use_local:
            llm = _get_local_llm()
        else:
            llm = _get_api_llm()

        logger.info(f"Initialized HuggingFace LLM (local={use_local})")

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

def _get_api_llm():
    """
    Get HuggingFace LLM via Inference API.

    Uses HuggingFace's hosted inference - no local resources needed.
    Free tier available with rate limits.
    """
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing HUGGINGFACE_API_KEY in .env file. "
            "Get free API key at: https://huggingface.co/settings/tokens"
        )

    model = os.getenv("LLM_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
    temperature = float(os.getenv("TEMPERATURE", "0.1"))
    max_tokens = int(os.getenv("MAX_NEW_TOKENS", "512"))

    return HuggingFaceHub(
        repo_id=model,
        huggingfacehub_api_token=api_key,
        model_kwargs={
            "temperature": temperature,
            "max_new_tokens": max_tokens,
            "top_p": 0.95,
            "repetition_penalty": 1.15
        }
    )

def _get_local_llm():
    """
    Get HuggingFace LLM running locally.

    Downloads model to your machine (first run only).
    Runs entirely locally - no API calls, completely free.

    Note: Requires significant RAM/VRAM depending on model size.
    """
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        import torch
    except ImportError:
        raise ImportError(
            "Local model support requires transformers. "
            "Install with: pip install transformers torch"
        )

    model_name = os.getenv("LLM_MODEL", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    temperature = float(os.getenv("TEMPERATURE", "0.1"))
    max_tokens = int(os.getenv("MAX_NEW_TOKENS", "512"))

    logger.info(f"Loading local model: {model_name} (first run may take time to download)")

    # Load model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype=torch.float16,  # Use half precision for efficiency
        low_cpu_mem_usage=True
    )

    # Create pipeline
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=max_tokens,
        temperature=temperature,
        top_p=0.95,
        repetition_penalty=1.15
    )

    # Wrap in LangChain
    return HuggingFacePipeline(pipeline=pipe)

# Recommended models for different setups
RECOMMENDED_MODELS = {
    # API Models (use with HuggingFace Inference API)
    "api": {
        "small": "google/flan-t5-base",  # Fast, good for learning
        "medium": "mistralai/Mistral-7B-Instruct-v0.2",  # Recommended
        "large": "meta-llama/Llama-2-13b-chat-hf"  # Best quality (slower)
    },

    # Local Models (run on your machine)
    "local": {
        "tiny": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # 1.1B params, runs on laptop
        "small": "microsoft/phi-2",  # 2.7B params, good quality
        "medium": "mistralai/Mistral-7B-Instruct-v0.2",  # 7B params, needs good GPU
        "large": "meta-llama/Llama-2-7b-chat-hf"  # 7B params, needs GPU
    }
}

def list_recommended_models(mode: str = "api", size: str = "medium"):
    """
    Get recommended model for a specific mode and size.

    Args:
        mode: 'api' or 'local'
        size: 'tiny', 'small', 'medium', or 'large'

    Returns:
        Model name string
    """
    return RECOMMENDED_MODELS.get(mode, {}).get(size, "")
