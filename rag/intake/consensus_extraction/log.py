"""
Writer for `intake_consensus_log` (schema_v89, Ship 34'.b).

One row per doc processed through the extraction consensus module.
Silent-fail — logging never blocks extraction. Callers pass a
psycopg2 connection + tenant/upload ids + the aggregator result +
the raw signals (for signals_summary + optional sample).

Usage:
    from rag.intake.consensus_extraction.log import log_consensus_result

    result = run_extraction_consensus(doc, scoped_leaf_ids, cfg)
    log_consensus_result(
        pg_conn         = conn,
        tenant_id       = tenant_id,
        upload_id       = upload_id,
        result          = result,
        signals_summary = result.signal_fire_counts,
        candidates_sample = _build_sample(result),   # optional
        cost_usd        = 0.05,                       # optional
    )
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

from rag.intake.consensus_extraction.types import (
    ExtractionConsensusResult,
    CandidateVerdict,
)


logger = logging.getLogger(__name__)


def log_consensus_result(
    pg_conn:            Any,
    tenant_id:          str,
    upload_id:          str,
    result:             ExtractionConsensusResult,
    n_arbiter_llm_accept:   int  = 0,
    n_arbiter_llm_reject:   int  = 0,
    candidates_sample:  Optional[list[dict]] = None,
    cost_usd:           Optional[float]      = None,
) -> Optional[str]:
    """Insert one row into intake_consensus_log. Returns the row id
    on success, None on any error.

    Silent-fail: logging never blocks the caller. Any exception is
    caught, logged as a warning, and returns None.

    `n_arbiter_llm_accept` / `n_arbiter_llm_reject` are the LLM
    arbiter's movement counts (how many arbiter-zone candidates the
    LLM decided which way). Sum + residual n_arbiter should equal
    the original arbiter count from the aggregator.
    """
    try:
        with pg_conn.cursor() as cur:
            # Ensure RLS sees the tenant_id — arioncomply_app requires it
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (str(tenant_id),))
            cur.execute(
                """
                INSERT INTO intake_consensus_log (
                    tenant_id, upload_id, total_candidates,
                    n_accept, n_arbiter, n_drop,
                    n_arbiter_llm_accept, n_arbiter_llm_reject,
                    signals_summary, candidates_sample,
                    latency_ms, cost_usd
                ) VALUES (
                    %s::uuid, %s::uuid, %s,
                    %s, %s, %s,
                    %s, %s,
                    %s::jsonb, %s::jsonb,
                    %s, %s
                )
                RETURNING id::text
                """,
                (
                    str(tenant_id), str(upload_id), result.total_candidates,
                    result.n_accept, result.n_arbiter, result.n_drop,
                    n_arbiter_llm_accept, n_arbiter_llm_reject,
                    json.dumps(result.signal_fire_counts or {}),
                    json.dumps(candidates_sample) if candidates_sample else None,
                    result.latency_ms, cost_usd,
                ),
            )
            row_id = cur.fetchone()[0]
        pg_conn.commit()
        return row_id
    except Exception as e:
        logger.warning("intake_consensus_log write failed: %s", e)
        try:
            pg_conn.rollback()
        except Exception:
            pass
        return None


def build_candidates_sample(
    result:            ExtractionConsensusResult,
    include_arbiter:   bool = True,
    top_k_by_score:    int  = 20,
) -> list[dict]:
    """Build a bounded sample of candidates for the
    `candidates_sample` JSONB column.

    Includes:
    - All candidates that went through the LLM arbiter (verdict
      changed from 'arbiter' to 'accept'/'drop' or stayed 'arbiter')
    - Top-K by score across all verdicts, for tuning-view

    Bounded so the log row doesn't bloat unboundedly on
    Processor-Ops-sized docs (400+ candidates).
    """
    sampled: list[dict] = []
    seen_keys: set[tuple[str, str]] = set()

    # Sort by score descending, take top K
    ordered = sorted(result.verdicts, key=lambda v: v.score, reverse=True)
    for v in ordered[:top_k_by_score]:
        sampled.append(_verdict_to_dict(v))
        seen_keys.add(v.candidate)

    if include_arbiter:
        # Also include any arbiter-zone or LLM-moved candidates not
        # already in the top-K sample
        for v in result.verdicts:
            if v.candidate in seen_keys:
                continue
            if v.verdict == "arbiter" or "arbiter" in (v.signals or []):
                sampled.append(_verdict_to_dict(v))
                seen_keys.add(v.candidate)

    return sampled


def _verdict_to_dict(v: CandidateVerdict) -> dict:
    """Serialize one CandidateVerdict for the sample JSONB."""
    leaf_id, must_id = v.candidate
    return {
        "leaf_id":     leaf_id,
        "must_id":     must_id,
        "control_ref": v.control_ref,
        "standard_id": v.standard_id,
        "score":       v.score,
        "corroborators": v.corroborators,
        "signals":     v.signals,
        "verdict":     v.verdict,
        "excerpt":     (v.fingerprint_excerpt or "")[:400] if v.fingerprint_excerpt else None,
    }
