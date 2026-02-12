"""
Unified logging for RAG QA system.

Usage:
    from loggers import UnifiedLogger, FileLogger, WandbLogger, MLflowLogger

All loggers write to the same JSONL format for dashboard compatibility.
"""

from .unified_logger import UnifiedLogger, wrap_qa_chain

# File-only logger
class FileLogger(UnifiedLogger):
    """File-only logger - writes JSONL without external services."""

    def __init__(
        self,
        log_dir: str = "logs",
        unified_filename: str = "unified_events.jsonl",
        vendor: str = None,
        app: str = None,
        config_params: dict = None,
    ):
        super().__init__(
            log_dir=log_dir,
            unified_filename=unified_filename,
            vendor=vendor,
            app=app,
            enable_wandb=False,
            enable_mlflow=False,
            config_params=config_params,
        )


# W&B logger
class WandbLogger(UnifiedLogger):
    """Logger with Weights & Biases integration."""

    def __init__(
        self,
        project_name: str = "rag-qa-system",
        log_dir: str = "logs",
        unified_filename: str = "unified_events.jsonl",
        vendor: str = None,
        app: str = None,
        config_params: dict = None,
    ):
        import os
        from dotenv import load_dotenv
        load_dotenv()

        config = config_params or {
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
            enable_wandb=True,
            wandb_project=project_name,
            enable_mlflow=False,
            config_params=config,
        )


# MLflow logger
class MLflowLogger(UnifiedLogger):
    """Logger with MLflow integration."""

    def __init__(
        self,
        experiment_name: str = "rag-qa-system",
        log_dir: str = "logs",
        unified_filename: str = "unified_events.jsonl",
        vendor: str = None,
        app: str = None,
        config_params: dict = None,
    ):
        import os
        from dotenv import load_dotenv
        load_dotenv()

        config = config_params or {
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


__all__ = [
    "UnifiedLogger",
    "FileLogger",
    "WandbLogger",
    "MLflowLogger",
    "wrap_qa_chain",
]
