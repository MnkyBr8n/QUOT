"""
Log reader utility for unified logging dashboard.

Reads unified_events.jsonl and provides query functions for the API.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from collections import defaultdict


def _parse_timestamp(ts: str) -> datetime:
    """Parse ISO timestamp string to datetime."""
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


class LogReader:
    """Read and query unified log events."""

    def __init__(self, log_path: str = "logs/unified_events.jsonl"):
        self.log_path = Path(log_path)

    def _read_all_events(self) -> List[Dict[str, Any]]:
        """Read all events from JSONL file."""
        if not self.log_path.exists():
            return []

        events = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return events

    def get_events(
        self,
        event_type: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get events with optional filters.

        Args:
            event_type: Filter by event type (query, error, ingestion, etc.)
            session_id: Filter by session ID
            limit: Max events to return
            offset: Skip first N events
        """
        events = self._read_all_events()

        # Apply filters
        if event_type:
            events = [e for e in events if e.get("event_type") == event_type]
        if session_id:
            events = [e for e in events if e.get("session_id") == session_id]

        # Sort by timestamp descending (newest first)
        events.sort(key=lambda e: e.get("timestamp", ""), reverse=True)

        # Apply pagination
        return events[offset : offset + limit]

    def get_sessions(self) -> List[Dict[str, Any]]:
        """
        Get all sessions with summary stats.

        Returns list of session summaries with:
        - session_id
        - start_time
        - end_time
        - query_count
        - total_response_time
        - avg_response_time
        - error_count
        - vendor
        - app
        """
        events = self._read_all_events()

        # Group by session
        sessions: Dict[str, Dict[str, Any]] = {}

        for event in events:
            sid = event.get("session_id")
            if not sid:
                continue

            if sid not in sessions:
                sessions[sid] = {
                    "session_id": sid,
                    "start_time": None,
                    "end_time": None,
                    "query_count": 0,
                    "total_response_time": 0.0,
                    "error_count": 0,
                    "vendor": event.get("vendor"),
                    "app": event.get("app"),
                    "tokens_used": 0,
                }

            s = sessions[sid]
            ts = event.get("timestamp")
            etype = event.get("event_type")

            if etype == "session_start":
                s["start_time"] = ts
            elif etype == "session_end":
                s["end_time"] = ts
                if event.get("extra"):
                    s["query_count"] = event["extra"].get("total_queries", s["query_count"])
                    s["total_response_time"] = event["extra"].get("total_time_s", s["total_response_time"])
            elif etype == "query":
                s["query_count"] += 1
                s["total_response_time"] += event.get("response_time_s", 0)
                s["tokens_used"] += event.get("tokens_used", 0) or 0
            elif etype == "error":
                s["error_count"] += 1

        # Calculate averages and convert to list
        result = []
        for s in sessions.values():
            if s["query_count"] > 0:
                s["avg_response_time"] = round(s["total_response_time"] / s["query_count"], 4)
            else:
                s["avg_response_time"] = 0.0
            s["total_response_time"] = round(s["total_response_time"], 4)
            result.append(s)

        # Sort by start time descending
        result.sort(key=lambda x: x.get("start_time") or "", reverse=True)
        return result

    def get_session_detail(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed info for a specific session including all its events."""
        events = self._read_all_events()
        session_events = [e for e in events if e.get("session_id") == session_id]

        if not session_events:
            return None

        # Build summary
        summary = {
            "session_id": session_id,
            "events": session_events,
            "query_count": 0,
            "error_count": 0,
            "total_response_time": 0.0,
            "tokens_used": 0,
            "start_time": None,
            "end_time": None,
            "vendor": None,
            "app": None,
        }

        for event in session_events:
            etype = event.get("event_type")
            if etype == "session_start":
                summary["start_time"] = event.get("timestamp")
                summary["vendor"] = event.get("vendor")
                summary["app"] = event.get("app")
            elif etype == "session_end":
                summary["end_time"] = event.get("timestamp")
            elif etype == "query":
                summary["query_count"] += 1
                summary["total_response_time"] += event.get("response_time_s", 0)
                summary["tokens_used"] += event.get("tokens_used", 0) or 0
            elif etype == "error":
                summary["error_count"] += 1

        if summary["query_count"] > 0:
            summary["avg_response_time"] = round(summary["total_response_time"] / summary["query_count"], 4)
        else:
            summary["avg_response_time"] = 0.0

        return summary

    def get_stats(self) -> Dict[str, Any]:
        """
        Get aggregated statistics.

        Returns:
            - total_queries
            - total_sessions
            - total_errors
            - avg_response_time
            - total_tokens
            - total_docs_ingested
            - total_chunks_created
            - queries_today
            - error_rate
        """
        events = self._read_all_events()

        stats = {
            "total_queries": 0,
            "total_sessions": 0,
            "total_errors": 0,
            "total_response_time": 0.0,
            "avg_response_time": 0.0,
            "total_tokens": 0,
            "total_docs_ingested": 0,
            "total_chunks_created": 0,
            "queries_today": 0,
            "error_rate": 0.0,
        }

        session_ids = set()
        today = datetime.now(timezone.utc).date()

        for event in events:
            etype = event.get("event_type")
            sid = event.get("session_id")

            if sid:
                session_ids.add(sid)

            if etype == "query":
                stats["total_queries"] += 1
                stats["total_response_time"] += event.get("response_time_s", 0)
                stats["total_tokens"] += event.get("tokens_used", 0) or 0

                # Check if today
                ts = event.get("timestamp")
                if ts:
                    try:
                        event_date = _parse_timestamp(ts).date()
                        if event_date == today:
                            stats["queries_today"] += 1
                    except Exception:
                        pass

            elif etype == "error":
                stats["total_errors"] += 1

            elif etype == "ingestion":
                stats["total_docs_ingested"] += event.get("num_docs", 0) or 0
                stats["total_chunks_created"] += event.get("num_chunks", 0) or 0

        stats["total_sessions"] = len(session_ids)

        if stats["total_queries"] > 0:
            stats["avg_response_time"] = round(stats["total_response_time"] / stats["total_queries"], 4)
            stats["error_rate"] = round(stats["total_errors"] / stats["total_queries"] * 100, 2)

        stats["total_response_time"] = round(stats["total_response_time"], 4)

        return stats

    def get_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent errors."""
        return self.get_events(event_type="error", limit=limit)

    def get_queries(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get query events."""
        return self.get_events(event_type="query", limit=limit, offset=offset)

    def get_response_time_series(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get response time data for charting.

        Returns list of {timestamp, response_time_s, query_id}
        """
        queries = self.get_queries(limit=limit)
        return [
            {
                "timestamp": q.get("timestamp"),
                "response_time_s": q.get("response_time_s"),
                "query_id": q.get("query_id"),
                "session_id": q.get("session_id"),
            }
            for q in queries
        ]


# Singleton instance for easy import
_reader: Optional[LogReader] = None


def get_reader(log_path: str = "logs/unified_events.jsonl") -> LogReader:
    """Get or create log reader instance."""
    global _reader
    if _reader is None or str(_reader.log_path) != log_path:
        _reader = LogReader(log_path)
    return _reader
