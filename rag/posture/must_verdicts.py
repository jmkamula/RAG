"""
Canonical reader for `posture_must_verdicts` (per-MUST fulfillment SSoT).

Every consumer that needs per-MUST truth reads through this module — no
consumer runs its own SQL against posture_must_verdicts, and no consumer
runs the engine directly to compute per-MUST recognition (that's what the
SSoT is for).

Ship 58' (2026-08-10) established the writer + refresh cycle;
Ship 58'.s-u hardened the wiring; this module is the read-side canonical
API introduced 2026-08-11 to unify the ~9 consumer sites (template
renderer + journey wizard + chat answer_footer + api_server per-leaf
state chip; more migrate later).

Scope selectors (combinable):
    must_ids       — specific list of MUST ids (template renderer path)
    control_ref +  — all MUSTs under one control (advisory / Dashboard /
    standard_id      SPA leaf-detail / chat markdown)
    (neither)      — all MUSTs for the tenant (journey wizard coverage)

Filters:
    only_satisfied — restrict to satisfied=TRUE rows

Return shape: `dict[must_id, MustVerdict]`. Missing rows (N/A-excluded
MUSTs, tenants not yet populated) simply don't appear in the dict.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class MustVerdict:
    """One row of posture_must_verdicts as a Python object."""
    must_id:     str
    control_ref: str
    standard_id: str
    satisfied:   bool
    stale:       bool
    partial:     bool
    reason:      str

    @property
    def state(self) -> str:
        """Convenience one-word category:
          'present'  — satisfied and fresh
          'stale'    — satisfied but past freshness_days
          'partial'  — partial-status finding, no present
          'missing'  — no evidence recognised
        """
        if self.satisfied:
            return "stale" if self.stale else "present"
        if self.partial:
            return "partial"
        return "missing"


def read_must_verdicts(
    pg_conn,
    tenant_id: str,
    *,
    must_ids:       Optional[Iterable[str]] = None,
    control_ref:    Optional[str] = None,
    standard_id:    Optional[str] = None,
    only_satisfied: bool = False,
) -> dict[str, MustVerdict]:
    """Read per-MUST verdicts from posture_must_verdicts.

    Scope selectors combine with AND. Passing no scope returns all rows
    for the tenant. RLS-scoped via `set_config('app.tenant_id', ...)` on
    the caller's connection — mandatory even though we also filter on
    tenant_id explicitly (arioncomply_app has no BYPASSRLS).

    Returns {must_id: MustVerdict}. Empty dict when scope has no matches
    or SSoT isn't populated yet (silent fallback — caller handles missing
    rows however it sees fit).
    """
    where_parts = ["tenant_id = %s::uuid"]
    params: list = [tenant_id]

    if must_ids is not None:
        ids_list = list(must_ids)
        if not ids_list:
            return {}
        where_parts.append("must_id = ANY(%s)")
        params.append(ids_list)
    if control_ref is not None:
        where_parts.append("control_ref = %s")
        params.append(control_ref)
    if standard_id is not None:
        where_parts.append("standard_id = %s")
        params.append(standard_id)
    if only_satisfied:
        where_parts.append("satisfied = TRUE")

    q = f"""
        SELECT must_id, control_ref, standard_id,
               satisfied, stale, partial, COALESCE(reason, '')
          FROM posture_must_verdicts
         WHERE {' AND '.join(where_parts)}
    """
    try:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,),
            )
            cur.execute(q, params)
            return {
                r[0]: MustVerdict(
                    must_id     = r[0],
                    control_ref = r[1],
                    standard_id = r[2],
                    satisfied   = r[3],
                    stale       = r[4],
                    partial     = r[5],
                    reason      = r[6],
                )
                for r in cur.fetchall()
            }
    except Exception:
        # Silent fallback — schema not applied, or transient issue.
        # Consumers treat empty dict as "no signal", which is safe.
        return {}


def read_satisfied_must_ids(pg_conn, tenant_id: str) -> set[str]:
    """Convenience: set of must_ids satisfied for this tenant.

    Fast-path for membership checks (journey wizard coverage progress,
    chat footer template-suggestion logic). Uses only_satisfied=TRUE
    filter so the query stays cheap on tenants with mostly-unmet posture.
    """
    verdicts = read_must_verdicts(pg_conn, tenant_id, only_satisfied=True)
    return set(verdicts.keys())


def read_must_verdicts_by_control(
    pg_conn,
    tenant_id:   str,
    control_ref: str,
    standard_id: str,
) -> dict[str, MustVerdict]:
    """Convenience wrapper — all MUSTs under one control."""
    return read_must_verdicts(
        pg_conn, tenant_id,
        control_ref=control_ref, standard_id=standard_id,
    )
