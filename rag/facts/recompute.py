"""
UPDATES_FACT — client_facts recompute worker.

Reads `fact_source_config` for each fact_key with an active source
definition, runs the source query in the current tenant's scope,
compares the result to the stored value on `client_facts`, and updates
the fact + logs the outcome.

Source types (MVP):
  posture   — check posture_controls for a (control_ref, standard_id)
              with an optional exclude_findings filter. Fact is TRUE
              when a row exists whose finding is NOT in exclude_findings.
  evidence  — check document_findings for approved bindings on a
              control (or any of a list). Fact is TRUE when count of
              approved+active findings on the target control(s) is
              >= min_count (default 1).
  sql       — reserved (safe-list of query templates, tenant_id-
              parameterised). Not implemented in MVP.
  external  — reserved (HTTP connectors: Odoo, Okta, ServiceNow).
  llm       — reserved (LLM-derived fact from doc content).

All source types return Optional[bool]:
  True/False  — computed value
  None        — could not compute (missing config, DB error) — the
                fact is NOT updated in this case; existing value stays.

The worker writes to `fact_recompute_log` on every run (success or
failure) so the audit trail captures both the deltas and the no-op
"we checked and it was already right" cases. `client_facts` is only
mutated when the computed value differs from prior.

Silent-fail contract at the recompute level: exceptions inside a
single fact's compute never poison the batch — the worker logs and
moves on to the next fact.
"""
from __future__ import annotations
import logging
import time
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class RecomputeResult:
    fact_key:       str
    computed_value: Optional[bool]
    prior_value:    Optional[bool]
    changed:        bool
    source_type:    str
    error_type:     Optional[str]  = None
    error_detail:   Optional[str]  = None
    latency_ms:     int            = 0


def _current_fact_value(pg_conn, tenant_id: str, fact_key: str) -> Optional[bool]:
    """Read the tenant's current client_facts.<fact_key> value.
    Returns None when the row doesn't exist yet (first-ever recompute)."""
    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            # Use format() for the column name only — validated against
            # information_schema before use to prevent SQL injection.
            cur.execute(
                """
                SELECT column_name FROM information_schema.columns
                 WHERE table_name = 'client_facts' AND column_name = %s
                """,
                (fact_key,),
            )
            if not cur.fetchone():
                logger.debug("fact_key %s not a client_facts column — skipping", fact_key)
                return None
            cur.execute(
                f'SELECT "{fact_key}" FROM client_facts WHERE tenant_id = %s::uuid',
                (tenant_id,),
            )
            row = cur.fetchone()
            return row[0] if row else None
    except Exception as e:
        logger.warning("_current_fact_value(%s): %s", fact_key, e)
        return None


def _write_fact_value(pg_conn, tenant_id: str, fact_key: str, value: bool) -> None:
    """Write the fact value to client_facts, upserting the tenant row.
    Only called after a validated fact_key check."""
    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        # UPSERT — ensures the row exists for tenants without a
        # client_facts row yet
        cur.execute(
            f"""
            INSERT INTO client_facts (tenant_id, "{fact_key}")
                 VALUES (%s::uuid, %s)
                    ON CONFLICT (tenant_id) DO UPDATE
                       SET "{fact_key}" = EXCLUDED."{fact_key}"
            """,
            (tenant_id, value),
        )


def _write_recompute_log(pg_conn, tenant_id: str, r: RecomputeResult) -> None:
    """Append a row to fact_recompute_log — success or failure."""
    try:
        with pg_conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO fact_recompute_log (
                    tenant_id, fact_key, computed_value, prior_value,
                    changed, source_type, error_type, error_detail, latency_ms
                ) VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (tenant_id, r.fact_key, r.computed_value, r.prior_value,
                 r.changed, r.source_type, r.error_type, r.error_detail,
                 r.latency_ms),
            )
    except Exception as e:
        logger.warning("_write_recompute_log: %s", e)


# ── Source-type implementations ─────────────────────────────────────

def _compute_posture(pg_conn, tenant_id: str, cfg: dict) -> Optional[bool]:
    """`posture` source: fact is TRUE if a posture_controls row exists
    for (control_ref, standard_id) whose `finding` is NOT in
    exclude_findings (default ['N/A'])."""
    control_ref = cfg.get("control_ref")
    standard_id = cfg.get("standard_id")
    excludes    = cfg.get("exclude_findings") or ["N/A"]
    if not control_ref or not standard_id:
        return None
    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM posture_controls
                 WHERE tenant_id  = %s::uuid
                   AND control_ref = %s
                   AND standard_id = %s
                   AND is_active   = TRUE
                   AND (finding IS NULL OR NOT (finding = ANY(%s)))
            )
            """,
            (tenant_id, control_ref, standard_id, excludes),
        )
        return bool(cur.fetchone()[0])


def _compute_evidence(pg_conn, tenant_id: str, cfg: dict) -> Optional[bool]:
    """`evidence` source: fact is TRUE if count of approved+active
    document_findings on the target control(s) >= min_count (default 1)."""
    control_refs = cfg.get("any_of_control_refs")
    if not control_refs:
        cr = cfg.get("control_ref")
        control_refs = [cr] if cr else []
    if not control_refs:
        return None
    standard_id = cfg.get("standard_id")
    min_count   = int(cfg.get("min_count") or 1)
    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        where_std = "AND standard_id = %s" if standard_id else ""
        params: list = [tenant_id, control_refs]
        if standard_id:
            params.append(standard_id)
        cur.execute(
            f"""
            SELECT count(*) FROM document_findings
             WHERE tenant_id     = %s::uuid
               AND control_ref  = ANY(%s)
               {where_std}
               AND review_status = 'approved'
               AND is_active     = TRUE
            """,
            params,
        )
        n = cur.fetchone()[0] or 0
        return bool(n >= min_count)


def _compute_sql(pg_conn, tenant_id: str, cfg: dict, sql_template: str) -> Optional[bool]:
    """`sql` source: parameterised query with {{tenant_id}} placeholder.
    NOT IMPLEMENTED in MVP — deferred until we settle on a safe query
    template mechanism (needs allowlist-style validation to prevent SQL
    injection via config)."""
    logger.warning("sql source_type not implemented — skip")
    return None


# ── Public API ──────────────────────────────────────────────────────

def recompute_client_fact(
    pg_conn,
    tenant_id: str,
    fact_key:  str,
) -> RecomputeResult:
    """Recompute one fact for one tenant. Returns a RecomputeResult;
    also writes to fact_recompute_log and (on delta) client_facts.
    Never raises — errors are captured in the result.
    """
    t0 = time.time()
    r = RecomputeResult(
        fact_key       = fact_key,
        computed_value = None,
        prior_value    = None,
        changed        = False,
        source_type    = "unknown",
    )
    try:
        with pg_conn.cursor() as cur:
            cur.execute(
                """
                SELECT source_type, source_query, source_config
                  FROM fact_source_config
                 WHERE fact_key = %s AND is_active = TRUE
                """,
                (fact_key,),
            )
            row = cur.fetchone()
        if not row:
            r.error_type   = "no_config"
            r.error_detail = f"no active source config for fact_key={fact_key}"
            _write_recompute_log(pg_conn, tenant_id, r)
            pg_conn.commit()
            return r
        source_type, source_query, source_config = row
        r.source_type = source_type

        # Compute
        if source_type == "posture":
            r.computed_value = _compute_posture(pg_conn, tenant_id, source_config or {})
        elif source_type == "evidence":
            r.computed_value = _compute_evidence(pg_conn, tenant_id, source_config or {})
        elif source_type == "sql":
            r.computed_value = _compute_sql(pg_conn, tenant_id, source_config or {}, source_query or "")
        else:
            r.error_type   = "not_implemented"
            r.error_detail = f"source_type={source_type} not implemented"

        # Prior value + delta
        r.prior_value = _current_fact_value(pg_conn, tenant_id, fact_key)
        if r.computed_value is not None and r.computed_value != r.prior_value:
            _write_fact_value(pg_conn, tenant_id, fact_key, r.computed_value)
            r.changed = True

    except Exception as e:
        r.error_type   = type(e).__name__
        r.error_detail = str(e)[:400]
        logger.warning("recompute_client_fact(%s, %s): %s", fact_key, tenant_id, e)

    r.latency_ms = int((time.time() - t0) * 1000)
    _write_recompute_log(pg_conn, tenant_id, r)
    pg_conn.commit()
    return r


def recompute_all_for_tenant(pg_conn, tenant_id: str) -> list[RecomputeResult]:
    """Recompute every active fact for one tenant. Returns per-fact
    results in the order they were computed."""
    with pg_conn.cursor() as cur:
        cur.execute(
            "SELECT fact_key FROM fact_source_config WHERE is_active = TRUE ORDER BY fact_key"
        )
        fact_keys = [row[0] for row in cur.fetchall()]
    results: list[RecomputeResult] = []
    for fk in fact_keys:
        results.append(recompute_client_fact(pg_conn, tenant_id, fk))
    return results
