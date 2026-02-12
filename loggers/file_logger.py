"""
File logging entrypoint for RAG QA system.

This now uses UnifiedLogger and writes JSONL to one file:
- ./logs/unified_events.jsonl

API kept compatible:
- FileLogger.log_query
- FileLogger.log_document_ingestion
- FileLogger.log_error
- FileLogger.finish
"""

import time
from unified_logger import UnifiedLogger, wrap_qa_chain


class FileLogger(UnifiedLogger):
    def __init__(self, log_dir="logs", vendor=None, app=None, unified_filename="unified_events.jsonl", config_params=None):
        super().__init__(
            log_dir=log_dir,
            unified_filename=unified_filename,
            vendor=vendor,
            app=app,
            enable_wandb=False,
            enable_mlflow=False,
            config_params=config_params,
        )


def build_qa_chain_with_file_logging():
    """Build QA chain with unified file logging."""
    from qa_bot import build_qa_chain

    logger = FileLogger(log_dir="logs")
    qa = build_qa_chain()
    qa = wrap_qa_chain(qa, logger)
    return qa, logger
