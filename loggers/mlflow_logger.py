"""
MLflow logging for RAG QA system.

Unified behavior:
- Always writes JSONL to ./logs/unified_events.jsonl
- Also forwards the same events to MLflow
"""

import os
from dotenv import load_dotenv
from unified_logger import UnifiedLogger, wrap_qa_chain

load_dotenv()


class MLflowRAGLogger(UnifiedLogger):
    def __init__(self, experiment_name="rag-qa-system", log_dir="logs", vendor=None, app=None, unified_filename="unified_events.jsonl"):
        config = {
            "llm_model": os.getenv("LLM_MODEL"),
            "embedding_model": os.getenv("EMBEDDING_MODEL"),
            "chunk_size": os.getenv("CHUNK_SIZE"),
            "chunk_overlap": os.getenv("CHUNK_OVERLAP"),
            "retrieval_k": os.getenv("RETRIEVAL_K"),
            "temperature": os.getenv("TEMPERATURE"),
            "use_local": os.getenv("USE_LOCAL_MODEL", "false"),
        }
        super().__init__(
            log_dir=log_dir,
            unified_filename=unified_filename,
            vendor=vendor,
            app=app,
            enable_wandb=False,
            enable_mlflow=True,
            mlflow_experiment=experiment_name,
            config_params=config,
        )


def build_qa_chain_with_mlflow_logging():
    """Build QA chain with unified file logging + MLflow forwarding."""
    from qa_bot import build_qa_chain

    logger = MLflowRAGLogger(experiment_name="my-rag-system", log_dir="logs")
    qa = build_qa_chain()
    qa = wrap_qa_chain(qa, logger)
    return qa, logger
