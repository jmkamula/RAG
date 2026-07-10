"""
Signal-precision feedback loop — Wave 4a (2026-07-09).

Computes rolling per-signal precision from Stage-1 review outcomes.
Feeds back into the auto-approve gate: signals that consistently
predict tenant decisions gain weight; signals that consistently
predict wrong decisions lose weight or fall below the auto-approve
threshold.

Precision definition per signal S:
  Numerator   — count of auto-approved fingerprint_match rows where
                S was in `corroborating_signals` AND review_status
                stayed 'approved' (tenant didn't later reject).
  Denominator — count of auto-approved fingerprint_match rows where
                S was in `corroborating_signals` AND the tenant took
                any Stage-1 action on them (approved-then-approved,
                approved-then-rejected).

Practically:
  precision(S) = approved(S) / (approved(S) + rejected(S))

Where:
  approved(S)  — corroborating_signals @> [S] AND review_status='approved' AND rejection_reason IS NULL
  rejected(S)  — corroborating_signals @> [S] AND (review_status='rejected' OR rejection_reason IS NOT NULL)

At Arion's current volumes, direct aggregation over `document_findings`
is fast (<10ms per lookup). A materialized rollup view can be added
later if the read path becomes hot.

Cold-start: with no history, precision defaults to a neutral 1.0 —
signals stay at their theoretical weight until data accumulates.

Gate integration: the Wave 3 rule `agreeing >= 2` becomes weighted:
  weighted_agreement = sum(precision(S) for S in agreeing_signals)
  if signal_available >= 2: auto_approve = weighted_agreement >= 2.0
  if signal_available == 1: auto_approve = weighted_agreement >= 1.0

A signal at 0.5 precision half-counts. A signal at 1.0 counts fully.
This ties the auto-approve threshold to empirical evidence quality.
"""
from __future__ import annotations
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Signals whose precision we track. Matches the writer's
# corroborating_signals[] values verbatim.
TRACKED_SIGNALS = (
    "target_controls",
    "semantic_controls",
    "explicit_refs",
    "llm_extracted",
)

# Cold-start neutral precision — used when a signal has no history
# (or fewer than MIN_DECISIONS samples).
_COLD_START_PRECISION = 1.0
_MIN_DECISIONS        = 5

# In-process cache — precision changes slowly and re-computing per
# finding is wasteful. Refresh every 5 minutes.
_CACHE: dict[tuple, tuple[dict[str, float], float]] = {}
_CACHE_TTL_S = 300.0


def _cache_key(tenant_id: str, standard_id: Optional[str], window_days: int) -> tuple:
    return (tenant_id, standard_id or "*", window_days)


def compute_signal_precision(
    pg_conn,
    tenant_id:   str,
    standard_id: Optional[str] = None,
    window_days: int = 90,
) -> dict[str, float]:
    """Return {signal_name → precision} for the tracked signals over
    the last `window_days` on this tenant. `standard_id` narrows to a
    single framework when supplied (matches the fingerprint's own
    standard so the feedback loop respects per-framework accuracy
    differences — e.g. 27701 fingerprints may be less precise than
    27001 while catalog maturity is uneven).

    Signals with < _MIN_DECISIONS Stage-1 outcomes fall back to the
    cold-start neutral. Silent fallback on DB failure returns the
    cold-start dict — never blocks the gate.

    Caches per (tenant, standard, window) for _CACHE_TTL_S seconds.
    """
    import time
    key = _cache_key(tenant_id, standard_id, window_days)
    now = time.time()
    cached = _CACHE.get(key)
    if cached and (now - cached[1]) < _CACHE_TTL_S:
        return cached[0]

    result = {s: _COLD_START_PRECISION for s in TRACKED_SIGNALS}
    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            std_clause = "AND standard_id = %s" if standard_id else ""
            params: list = [tenant_id]
            if standard_id:
                params.append(standard_id)
            # For each signal, count approved vs rejected within the window
            for signal in TRACKED_SIGNALS:
                q = f"""
                    SELECT
                      count(*) FILTER (WHERE review_status = 'approved'
                                         AND (rejection_reason IS NULL
                                              OR rejection_reason NOT LIKE 'superseded_%%')
                                        )                                            AS approved_n,
                      count(*) FILTER (WHERE review_status = 'rejected')             AS rejected_n
                      FROM document_findings
                     WHERE tenant_id = %s::uuid
                       {std_clause}
                       AND inference_source = 'fingerprint_match'
                       AND is_active = TRUE
                       AND extracted_at > NOW() - INTERVAL '{int(window_days)} days'
                       AND %s = ANY(corroborating_signals)
                """
                cur.execute(q, params + [signal])
                row = cur.fetchone() or (0, 0)
                approved_n = int(row[0] or 0)
                rejected_n = int(row[1] or 0)
                total = approved_n + rejected_n
                if total >= _MIN_DECISIONS:
                    result[signal] = round(approved_n / total, 3)
    except Exception as e:
        logger.warning("signal precision compute failed: %s", e)

    _CACHE[key] = (result, now)
    return result


def invalidate_cache(tenant_id: Optional[str] = None) -> None:
    """Drop the precision cache — call after Stage-1 approve/reject
    events so the next auto-approve decision reads fresh stats.
    Scoped to one tenant when supplied, else global."""
    global _CACHE
    if tenant_id is None:
        _CACHE = {}
        return
    _CACHE = {k: v for k, v in _CACHE.items() if k[0] != tenant_id}
