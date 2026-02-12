from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import WatsonxLLM
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
    Build a RetrievalQA chain with Watsonx LLM.

    Requires .env file with:
    - WATSONX_URL
    - WATSONX_APIKEY
    - WATSONX_PROJECT_ID

    Returns:
        RetrievalQA chain

    Raises:
        ValueError: If credentials are missing
        RuntimeError: If chain building fails
    """
    try:
        # Get credentials from environment
        url = os.getenv("WATSONX_URL")
        apikey = os.getenv("WATSONX_APIKEY")
        project_id = os.getenv("WATSONX_PROJECT_ID")

        if not all([url, apikey, project_id]):
            raise ValueError(
                "Missing Watsonx credentials. Set WATSONX_URL, "
                "WATSONX_APIKEY, and WATSONX_PROJECT_ID in .env file"
            )

        # Get configuration
        model_id = os.getenv("LLM_MODEL", "mistralai/mixtral-8x7b-instruct-v01")
        temperature = float(os.getenv("TEMPERATURE", "0.0"))
        max_new_tokens = int(os.getenv("MAX_NEW_TOKENS", "512"))

        # Initialize LLM
        llm = WatsonxLLM(
            model_id=model_id,
            url=url,
            apikey=apikey,
            project_id=project_id,
            params={
                "temperature": temperature,
                "max_new_tokens": max_new_tokens
            }
        )

        logger.info(f"Initialized LLM: {model_id}")

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
