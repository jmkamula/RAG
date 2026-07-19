"""
Persistence helper for chat_casefile_log (schema_v68).

Called by rank_and_answer once the digest is built + repair pass
completes. Silent-fail — a log write must never break the chat
pipeline. Mirrors the rag/consensus/log.py pattern.
"""
from __future__ import annotations

import json
import logging
from typing import Optional

from rag.casefile.claim_scan import claims_to_json, scan_claims
from rag.casefile.repair import RepairEvent, RepairResult
from rag.casefile.types import CaseFile


logger = logging.getLogger("rag.casefile.log")

# Ship 6'.d: cap the stored answer body. 8000 chars covers >99% of
# realistic chat answers (typical: 800–2000). Anything longer is
# either a rare long-form implementation guide or a defect worth
# investigating separately.
_ANSWER_TEXT_CAP = 8000


def _repair_events_to_json(events: list[RepairEvent]) -> list[dict]:
    """Compact JSON view of the repair events list."""
    return [
        {"kind": e.kind, "ref": e.ref, "detail": e.detail}
        for e in events
    ]


def log_casefile(
    pg_conn,
    tenant_id:            str,
    case_file:            CaseFile,
    system_prompt_tokens: Optional[int],
    user_digest_tokens:   Optional[int],
    repair_result:        RepairResult,
    answer_text:          Optional[str] = None,
    session_id:           Optional[str] = None,
    request_id:           Optional[str] = None,
    casefile_enabled:     bool = False,
    shadow_mode:          bool = False,
    digest_latency_ms:    Optional[int] = None,
    repair_latency_ms:    Optional[int] = None,
    total_latency_ms:     Optional[int] = None,
    error_type:           Optional[str] = None,
    error_detail:         Optional[str] = None,
    retention_days:       int = 90,
) -> Optional[str]:
    """Persist one Ship 2' trace to chat_casefile_log.

    Returns the inserted row id on success, None on any failure.
    Silent-fail: exceptions caught + logged, never raised.

    Args:
        pg_conn:               psycopg2 connection (tenant context set).
        tenant_id:             Tenant UUID matching app.tenant_id GUC.
        case_file:             The CaseFile whose digest was built.
        system_prompt_tokens:  approx_tokens(system_prompt).
        user_digest_tokens:    approx_tokens(digest).
        repair_result:         Full RepairResult (events + footers).
        session_id / request_id: Trace ids.
        casefile_enabled:      Was Ship 2' active this turn? (Feature flag.)
        shadow_mode:           TRUE if both paths ran; only one served.
        *_latency_ms:          Optional performance breakdown.
        error_type / detail:   Only set when the pipeline errored.
        retention_days:        Purge-after horizon.
    """
    try:
        summary  = case_file.summary()
        qtype    = case_file.question_type
        query    = case_file.query
        events_json = _repair_events_to_json(repair_result.events)
        events_count = len(repair_result.events)
        footers = list(repair_result.footers_added)
        total_tokens = None
        if system_prompt_tokens is not None and user_digest_tokens is not None:
            total_tokens = system_prompt_tokens + user_digest_tokens

        # Ship 6'.d: passive claim scan. NEVER blocks or rewrites —
        # only records what normative claims the LLM made.
        answer_body = (answer_text or "")[:_ANSWER_TEXT_CAP]
        claim_events = claims_to_json(scan_claims(answer_body, case_file))
        claim_events_count = len(claim_events)

        with pg_conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chat_casefile_log (
                    tenant_id, request_id, session_id,
                    query, question_type,
                    case_file_summary,
                    system_prompt_tokens, user_digest_tokens, total_prompt_tokens,
                    repair_events, repair_events_count, footers_added,
                    casefile_enabled, shadow_mode,
                    digest_latency_ms, repair_latency_ms, total_latency_ms,
                    error_type, error_detail,
                    answer_text, claim_events, claim_events_count,
                    purge_after
                ) VALUES (
                    %s::uuid, %s, %s,
                    %s, %s,
                    %s::jsonb,
                    %s, %s, %s,
                    %s::jsonb, %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s, %s,
                    %s, %s::jsonb, %s,
                    NOW() + (%s || ' days')::interval
                )
                RETURNING id
                """,
                (
                    tenant_id, request_id, session_id,
                    query, qtype,
                    json.dumps(summary),
                    system_prompt_tokens, user_digest_tokens, total_tokens,
                    json.dumps(events_json), events_count, footers,
                    casefile_enabled, shadow_mode,
                    digest_latency_ms, repair_latency_ms, total_latency_ms,
                    error_type, error_detail,
                    answer_body or None, json.dumps(claim_events), claim_events_count,
                    str(retention_days),
                ),
            )
            row_id = cur.fetchone()[0]
        pg_conn.commit()
        return str(row_id)
    except Exception as e:
        logger.warning("chat_casefile_log write failed (silent): %s", e)
        try:
            pg_conn.rollback()
        except Exception:
            pass
        return None
