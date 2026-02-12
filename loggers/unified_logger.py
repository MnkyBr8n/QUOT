"""
Unified logging for RAG QA system.

Always writes a single JSONL file (dashboard ready).
Optionally forwards the same events to Weights & Biases and MLflow.

One JSON object per line, stable schema.
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_int(x: Any, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _doc_preview(doc: Any, limit: int = 200) -> Dict[str, Any]:
    content = getattr(doc, "page_content", None)
    meta = getattr(doc, "metadata", None)
    return {
        "content": (content or "")[:limit],
        "metadata": meta if isinstance(meta, dict) else {},
    }


@dataclass
class UnifiedEvent:
    event_id: str
    event_type: str          # session_start | query | ingestion | error | session_end
    timestamp: str
    session_id: str

    vendor: Optional[str] = None
    app: Optional[str] = None

    query_id: Optional[int] = None
    query: Optional[str] = None
    answer: Optional[str] = None
    response_time_s: Optional[float] = None
    tokens_used: Optional[int] = None
    num_sources: Optional[int] = None
    sources: Optional[List[Dict[str, Any]]] = None

    num_docs: Optional[int] = None
    num_chunks: Optional[int] = None
    ingestion_time_s: Optional[float] = None

    error_type: Optional[str] = None
    error_message: Optional[str] = None

    extra: Optional[Dict[str, Any]] = None


class _JsonlFileSink:
    def __init__(self, log_dir: str, filename: str) -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.log_dir / filename
        self._lock = threading.Lock()

    def write(self, event: UnifiedEvent) -> None:
        line = json.dumps(asdict(event), ensure_ascii=False)
        with self._lock:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line + "\n")


class _WandbSink:
    def __init__(self, project_name: str, config: Optional[Dict[str, Any]] = None) -> None:
        import wandb  # type: ignore

        self._wandb = wandb
        self._wandb.init(project=project_name, config=(config or {}))

    def write(self, event: UnifiedEvent) -> None:
        payload = asdict(event)
        metrics: Dict[str, Any] = {"event_type": event.event_type, "timestamp": event.timestamp}

        if event.response_time_s is not None:
            metrics["response_time_s"] = event.response_time_s
        if event.tokens_used is not None:
            metrics["tokens_used"] = event.tokens_used
        if event.num_sources is not None:
            metrics["num_sources"] = event.num_sources

        self._wandb.log({**metrics, "event": payload})

    def finish(self) -> None:
        self._wandb.finish()


class _MLflowSink:
    def __init__(self, experiment_name: str, params: Optional[Dict[str, Any]] = None) -> None:
        import mlflow  # type: ignore

        self._mlflow = mlflow
        self._mlflow.set_experiment(experiment_name)
        self._mlflow.start_run()
        self._step = 0

        if params:
            safe_params: Dict[str, Any] = {}
            for k, v in params.items():
                try:
                    json.dumps(v)
                    safe_params[k] = v
                except Exception:
                    safe_params[k] = str(v)
            self._mlflow.log_params(safe_params)

    def write(self, event: UnifiedEvent) -> None:
        self._step += 1
        metrics: Dict[str, float] = {}

        if event.response_time_s is not None:
            metrics["response_time_s"] = _safe_float(event.response_time_s)
        if event.tokens_used is not None:
            metrics["tokens_used"] = float(_safe_int(event.tokens_used))
        if event.num_sources is not None:
            metrics["num_sources"] = float(_safe_int(event.num_sources))

        if event.event_type == "ingestion":
            if event.num_docs is not None:
                metrics["ingestion_num_docs"] = float(_safe_int(event.num_docs))
            if event.num_chunks is not None:
                metrics["ingestion_num_chunks"] = float(_safe_int(event.num_chunks))
            if event.ingestion_time_s is not None:
                metrics["ingestion_time_s"] = _safe_float(event.ingestion_time_s)

        if metrics:
            self._mlflow.log_metrics(metrics, step=self._step)

        tmp_dir = Path("logs") / "mlflow_events"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        p = tmp_dir / f"{event.event_type}_{event.event_id}.json"
        with open(p, "w", encoding="utf-8") as f:
            json.dump(asdict(event), f, ensure_ascii=False, indent=2)
        self._mlflow.log_artifact(str(p), artifact_path="events")

    def finish(self) -> None:
        self._mlflow.end_run()


class UnifiedLogger:
    """
    Unified logger.
    Always writes JSONL to disk.
    Optionally forwards events to W&B and MLflow.
    """

    def __init__(
        self,
        log_dir: str = "logs",
        unified_filename: str = "unified_events.jsonl",
        vendor: Optional[str] = None,
        app: Optional[str] = None,
        enable_wandb: bool = False,
        wandb_project: str = "rag-qa-system",
        enable_mlflow: bool = False,
        mlflow_experiment: str = "rag-qa-system",
        config_params: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.session_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
        self.vendor = vendor
        self.app = app

        self._query_count = 0
        self._total_time = 0.0

        self._file = _JsonlFileSink(log_dir=log_dir, filename=unified_filename)
        self._wandb = None
        self._mlflow = None

        config_params = config_params or {}

        if enable_wandb:
            try:
                self._wandb = _WandbSink(project_name=wandb_project, config=config_params)
            except Exception:
                self._wandb = None

        if enable_mlflow:
            try:
                self._mlflow = _MLflowSink(experiment_name=mlflow_experiment, params=config_params)
            except Exception:
                self._mlflow = None

        self._write(
            UnifiedEvent(
                event_id=uuid.uuid4().hex,
                event_type="session_start",
                timestamp=_utc_iso(),
                session_id=self.session_id,
                vendor=self.vendor,
                app=self.app,
                extra={"config": config_params},
            )
        )

    @property
    def unified_path(self) -> str:
        return str(self._file.path)

    def _write(self, event: UnifiedEvent) -> None:
        self._file.write(event)
        if self._wandb:
            self._wandb.write(event)
        if self._mlflow:
            self._mlflow.write(event)

    def log_query(
        self,
        query: str,
        answer: str,
        sources: Optional[List[Any]],
        response_time: float,
        tokens_used: Optional[int] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._query_count += 1
        self._total_time += float(response_time)

        src_list = sources or []
        self._write(
            UnifiedEvent(
                event_id=uuid.uuid4().hex,
                event_type="query",
                timestamp=_utc_iso(),
                session_id=self.session_id,
                vendor=self.vendor,
                app=self.app,
                query_id=self._query_count,
                query=str(query),
                answer=str(answer),
                response_time_s=round(float(response_time), 4),
                tokens_used=_safe_int(tokens_used, 0) if tokens_used is not None else None,
                num_sources=len(src_list),
                sources=[_doc_preview(d) for d in src_list[:3]],
                extra=extra,
            )
        )

    def log_document_ingestion(
        self,
        num_docs: int,
        num_chunks: int,
        ingestion_time: float,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._write(
            UnifiedEvent(
                event_id=uuid.uuid4().hex,
                event_type="ingestion",
                timestamp=_utc_iso(),
                session_id=self.session_id,
                vendor=self.vendor,
                app=self.app,
                num_docs=_safe_int(num_docs),
                num_chunks=_safe_int(num_chunks),
                ingestion_time_s=round(float(ingestion_time), 4),
                extra=extra,
            )
        )

    def log_error(
        self,
        error_type: str,
        error_message: str,
        query: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._write(
            UnifiedEvent(
                event_id=uuid.uuid4().hex,
                event_type="error",
                timestamp=_utc_iso(),
                session_id=self.session_id,
                vendor=self.vendor,
                app=self.app,
                query=query,
                error_type=error_type,
                error_message=error_message,
                extra=extra,
            )
        )

    def finish(self, extra: Optional[Dict[str, Any]] = None) -> None:
        avg = (self._total_time / self._query_count) if self._query_count else 0.0
        self._write(
            UnifiedEvent(
                event_id=uuid.uuid4().hex,
                event_type="session_end",
                timestamp=_utc_iso(),
                session_id=self.session_id,
                vendor=self.vendor,
                app=self.app,
                extra={
                    "total_queries": self._query_count,
                    "total_time_s": round(self._total_time, 4),
                    "avg_response_time_s": round(avg, 4),
                    **(extra or {}),
                },
            )
        )

        if self._wandb:
            try:
                self._wandb.finish()
            except Exception:
                pass
        if self._mlflow:
            try:
                self._mlflow.finish()
            except Exception:
                pass


def wrap_qa_chain(
    qa: Any,
    logger: UnifiedLogger,
    query_key: str = "query",
    answer_key: str = "result",
    sources_key: str = "source_documents",
    token_extractor: Optional[Callable[[Dict[str, Any]], Optional[int]]] = None,
) -> Any:
    """
    Wrap qa.__call__ so every query logs to the unified file, and optionally W&B or MLflow.

    If a vendor uses different result keys, override answer_key or sources_key.
    """
    original_call = qa.__call__

    def logged_call(inputs: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        query = inputs.get(query_key, "")

        try:
            result = original_call(inputs)
            response_time = time.time() - start_time

            tokens_used = None
            if token_extractor:
                try:
                    tokens_used = token_extractor(result)
                except Exception:
                    tokens_used = None

            logger.log_query(
                query=str(query),
                answer=str(result.get(answer_key, "")),
                sources=result.get(sources_key, []),
                response_time=response_time,
                tokens_used=tokens_used,
            )
            return result
        except Exception as e:
            logger.log_error("query_execution", str(e), query=str(query))
            raise

    qa.__call__ = logged_call
    return qa
