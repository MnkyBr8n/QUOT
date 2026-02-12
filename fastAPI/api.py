from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from qa_bot import build_qa_chain
from pdf_loader import load_pdf
from text_splitter import split_documents
from vectordb import create_vector_db
import logging
import tempfile
import shutil
import os
import sys
import time

# Resolve sibling directories relative to this file so the server can be
# started from any working directory (e.g. repo root or fastAPI/).
_here = os.path.dirname(os.path.abspath(__file__))
_loggers_dir = os.path.join(_here, "..", "loggers")
_logs_dir = os.path.join(_here, "..", "logs")
sys.path.insert(0, _loggers_dir)
from unified_logger import UnifiedLogger
from log_reader import LogReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global QA chain and logger (mutated by lifespan)
qa_chain = None
rag_logger: Optional[UnifiedLogger] = None
log_reader: Optional[LogReader] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup; clean up on shutdown."""
    global qa_chain, rag_logger, log_reader

    log_reader = LogReader(
        log_path=os.path.join(_logs_dir, "unified_events.jsonl")
    )

    try:
        rag_logger = UnifiedLogger(
            log_dir=_logs_dir,
            unified_filename="unified_events.jsonl",
            vendor="fastapi",
            app="rag-qa-api",
            enable_wandb=False,
            enable_mlflow=False,
        )
        logger.info("Unified logger initialized")
    except Exception as e:
        logger.error(f"Failed to initialize unified logger: {e}")

    try:
        qa_chain = build_qa_chain()
        logger.info("QA chain initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize QA chain: {e}")

    yield

    if rag_logger:
        try:
            rag_logger.finish()
        except Exception:
            pass


app = FastAPI(title="RAG QA API", version="2.0.0", lifespan=lifespan)

# Enable CORS for web clients.
# Origins are read from ALLOWED_ORIGINS env var (comma-separated).
# Default covers the Vite dev server and common local ports.
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
_allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    answer: str
    sources: list = []
    response_time: Optional[float] = None


# Dashboard response models
class StatsResponse(BaseModel):
    total_queries: int
    total_sessions: int
    total_errors: int
    avg_response_time: float
    total_tokens: int
    total_docs_ingested: int
    total_chunks_created: int
    queries_today: int
    error_rate: float


class SessionSummary(BaseModel):
    session_id: str
    start_time: Optional[str]
    end_time: Optional[str]
    query_count: int
    total_response_time: float
    avg_response_time: float
    error_count: int
    tokens_used: int
    vendor: Optional[str]
    app: Optional[str]


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "RAG QA API is running",
        "qa_ready": qa_chain is not None,
        "logging_enabled": rag_logger is not None,
    }


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question and get an answer from the QA system.

    Example:
        POST /ask
        {"question": "What is the main topic of the document?"}
    """
    if qa_chain is None:
        raise HTTPException(status_code=503, detail="QA system not initialized")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    start_time = time.time()

    try:
        result = qa_chain.invoke({"query": request.question})
        response_time = time.time() - start_time

        sources = []
        source_docs = result.get("source_documents", [])
        if source_docs:
            sources = [
                {"content": doc.page_content[:200], "metadata": doc.metadata}
                for doc in source_docs
            ]

        # Log the query
        if rag_logger:
            rag_logger.log_query(
                query=request.question,
                answer=result["result"],
                sources=source_docs,
                response_time=response_time,
            )

        return QuestionResponse(
            answer=result["result"], sources=sources, response_time=round(response_time, 4)
        )
    except Exception as e:
        # Log the error
        if rag_logger:
            rag_logger.log_error("query_execution", str(e), query=request.question)

        logger.error(f"Query failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process question: {str(e)}"
        ) from e


@app.post("/ingest")
async def ingest_pdf(file: UploadFile = File(...)):
    """
    Upload and ingest a PDF document.
    This will replace the existing vector database.
    """
    global qa_chain

    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    tmp_path = None
    start_time = time.time()

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Process PDF
        logger.info(f"Processing PDF: {file.filename}")
        documents = load_pdf(tmp_path)
        chunks = split_documents(documents)

        # Remove existing vector DB so re-ingesting the same file doesn't
        # accumulate duplicate chunks (Chroma.from_documents appends by default).
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir)

        create_vector_db(chunks)

        ingestion_time = time.time() - start_time

        # Log ingestion
        if rag_logger:
            rag_logger.log_document_ingestion(
                num_docs=len(documents),
                num_chunks=len(chunks),
                ingestion_time=ingestion_time,
                extra={"filename": file.filename},
            )

        # Reinitialize QA chain with new database
        qa_chain = build_qa_chain()

        # Cleanup — isolated so a delete failure doesn't mask ingestion success
        try:
            os.unlink(tmp_path)
        except OSError:
            logger.warning("Could not delete temp file: %s", tmp_path)

        return {
            "status": "success",
            "message": f"Successfully ingested {file.filename}",
            "pages": len(documents),
            "chunks": len(chunks),
            "ingestion_time": round(ingestion_time, 2),
        }
    except Exception as e:
        # Log error
        if rag_logger:
            rag_logger.log_error(
                "ingestion_failed", str(e), extra={"filename": file.filename}
            )

        logger.error(f"Ingestion failed: {e}")
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(
            status_code=500, detail=f"Failed to ingest PDF: {str(e)}"
        ) from e


@app.get("/status")
async def get_status():
    """Get system status"""
    return {
        "qa_initialized": qa_chain is not None,
        "logging_enabled": rag_logger is not None,
        "vector_db_exists": os.path.exists(os.getenv("CHROMA_PERSIST_DIR", "chroma_db")),
    }


# ============================================================================
# Dashboard API Endpoints
# ============================================================================


@app.get("/logs/stats", response_model=StatsResponse)
async def get_log_stats():
    """Get aggregated logging statistics for dashboard."""
    if log_reader is None:
        raise HTTPException(status_code=503, detail="Log reader not initialized")

    stats = log_reader.get_stats()
    return StatsResponse(**stats)


@app.get("/logs/sessions", response_model=List[SessionSummary])
async def get_sessions():
    """Get all sessions with summary stats."""
    if log_reader is None:
        raise HTTPException(status_code=503, detail="Log reader not initialized")

    sessions = log_reader.get_sessions()
    return [SessionSummary(**s) for s in sessions]


@app.get("/logs/sessions/{session_id}")
async def get_session_detail(session_id: str):
    """Get detailed info for a specific session."""
    if log_reader is None:
        raise HTTPException(status_code=503, detail="Log reader not initialized")

    detail = log_reader.get_session_detail(session_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return detail


@app.get("/logs/events")
async def get_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Get log events with optional filters."""
    if log_reader is None:
        raise HTTPException(status_code=503, detail="Log reader not initialized")

    events = log_reader.get_events(
        event_type=event_type, session_id=session_id, limit=limit, offset=offset
    )
    return {"events": events, "count": len(events)}


@app.get("/logs/queries")
async def get_queries(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Get query events."""
    if log_reader is None:
        raise HTTPException(status_code=503, detail="Log reader not initialized")

    queries = log_reader.get_queries(limit=limit, offset=offset)
    return {"queries": queries, "count": len(queries)}


@app.get("/logs/errors")
async def get_errors(limit: int = Query(50, ge=1, le=500)):
    """Get recent errors."""
    if log_reader is None:
        raise HTTPException(status_code=503, detail="Log reader not initialized")

    errors = log_reader.get_errors(limit=limit)
    return {"errors": errors, "count": len(errors)}


@app.get("/logs/response-times")
async def get_response_times(limit: int = Query(100, ge=1, le=500)):
    """Get response time series data for charting."""
    if log_reader is None:
        raise HTTPException(status_code=503, detail="Log reader not initialized")

    data = log_reader.get_response_time_series(limit=limit)
    return {"data": data, "count": len(data)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
