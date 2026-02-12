from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
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
    Build a RetrievalQA chain with Google Gemini.

    Requires .env file with:
    - GOOGLE_API_KEY

    Returns:
        RetrievalQA chain

    Raises:
        ValueError: If API key is missing
        RuntimeError: If chain building fails
    """
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY in .env file")

        # Get configuration
        model = os.getenv("LLM_MODEL", "gemini-1.5-flash")
        temperature = float(os.getenv("TEMPERATURE", "0.0"))
        max_tokens = int(os.getenv("MAX_NEW_TOKENS", "512"))

        # Initialize Google LLM
        llm = ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model=model,
            temperature=temperature,
            max_output_tokens=max_tokens
        )

        logger.info(f"Initialized Google Gemini: {model}")

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
