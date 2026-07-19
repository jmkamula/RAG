"""
Persistence helper for chat_consensus_log (schema_v67).

Called by the classify graph node after run_consensus returns.
Silent-fail — a log write must never break the chat pipeline.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Optional
from dataclasses import asdict, is_dataclass

from rag.ai_trace import current_request_id, current_session_id
from rag.consensus.types import ConsensusResult, SignalOutput


logger = logging.getLogger("rag.consensus.log")


def _signal_to_json(sig: SignalOutput) -> dict:
    """Compact JSON view of one signal."""
    return {
        "name":          sig.name,
        # Refs as [[ref, weight], ...] arrays — smaller than dicts
        "refs":          [[r, round(w, 4)] for r, w in sig.refs],
        "question_type": sig.question_type,
        "framework":     sig.framework,
        "fired":         sig.fired,
        "metadata":      _sanitize_metadata(sig.metadata),
    }


def _sanitize_metadata(md: dict) -> dict:
    """Ensure metadata is JSON-serialisable — cast anything exotic."""
    out = {}
    for k, v in md.items():
        try:
            json.dumps(v)
            out[k] = v
        except (TypeError, ValueError):
            out[k] = str(v)[:200]
    return out


def _clarification_to_json(clarification) -> Optional[dict]:
    if clarification is None:
        return None
    return {
        "kind":     clarification.kind,
        "question": clarification.question,
        "options":  [
            {"ref": o.ref, "title": o.title, "framework": o.framework}
            for o in clarification.options
        ],
    }


def log_consensus(
    pg_conn,
    tenant_id:         str,
    query:             str,
    result:            ConsensusResult,
    session_id:        Optional[str] = None,
    request_id:        Optional[str] = None,
    llm_fallback_used: bool = False,
    retention_days:    int = 90,
) -> Optional[str]:
    """Persist one ConsensusResult to chat_consensus_log.

    Returns the inserted row id on success, None on any failure.
    Silent-fail: exceptions caught + logged, never raised.

    Args:
        pg_conn:           A psycopg2 connection (already inside a
                            tenant context via set_config).
        tenant_id:         Tenant UUID (must match app.tenant_id GUC).
        query:             Raw user query text.
        result:            ConsensusResult from run_consensus.
        session_id:        LangGraph session id (per-turn thread).
        request_id:        Per-request trace id (matches ai_call_log).
        llm_fallback_used: TRUE when the classify node fell through to
                            the legacy LLM classifier.
        retention_days:    Purge-after horizon (default 90 days).
    """
    try:
        # Ship 6'.e: fall back to ai_trace ContextVars if the caller
        # didn't pass ids explicitly. set_trace_context() runs at API
        # request entry (api_server.py:513) so every internal write
        # picks them up transparently.
        if session_id is None:
            session_id = current_session_id()
        if request_id is None:
            request_id = current_request_id()

        signals_json = [_signal_to_json(s) for s in (result.signals or [])]
        clarification_json = _clarification_to_json(result.clarification)

        with pg_conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chat_consensus_log (
                    tenant_id, request_id, session_id, query,
                    verdict, top_refs, top_ref_confidence, corroborators,
                    question_type, framework,
                    signals_json, disagreement_notes, clarification,
                    llm_fallback_used, latency_ms,
                    purge_after
                ) VALUES (
                    %s::uuid, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s,
                    %s::jsonb, %s, %s::jsonb,
                    %s, %s,
                    NOW() + INTERVAL '%s days'
                )
                RETURNING id
                """,
                (
                    tenant_id, request_id, session_id, query,
                    result.verdict,
                    list(result.refs) if result.refs else None,
                    result.top_ref_confidence,
                    result.corroborators,
                    result.question_type,
                    result.framework,
                    json.dumps(signals_json),
                    list(result.disagreement_notes) if result.disagreement_notes else None,
                    json.dumps(clarification_json) if clarification_json else None,
                    llm_fallback_used,
                    result.latency_ms,
                    retention_days,
                ),
            )
            row_id = cur.fetchone()[0]
        pg_conn.commit()
        return str(row_id)
    except Exception as e:
        logger.warning("chat_consensus_log write failed (silent): %s", e)
        try:
            pg_conn.rollback()
        except Exception:
            pass
        return None
