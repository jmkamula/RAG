"""
Ship 76'.b — tenant scope truth for callers without a CaseFile.

Mirror of `CaseFile.in_scope(ref)` (rag/casefile/types.py) for API,
dashboard, notification, and other paths that don't build a CaseFile.
Both predicates read the same SSoT column: Ship 66'.a's
`posture_controls.applicability_status`.

Rule (same as CaseFile.in_scope):
  - `applicability_status = 'na'`   → out of scope (returns False)
  - `applicability_status = 'applicable'` OR NULL OR row missing
                                    → in scope (returns True)

Rationale: missing rows aren't scoped-out. They're either unassessed
but applicable, or not curated. Only an explicit N/A marker drops.

Ship 76 arc closes the N/A-cascade gap surfaced by eval case #5.
See docs/memory/ship_76_prime_a_2026_08_17.md for the audit + design.
"""
from __future__ import annotations

from typing import Iterable, Optional


def row_in_scope(row: Optional[dict]) -> bool:
    """True iff a posture_controls row dict is in-scope.

    For callers that already have the row in hand (loader loop). Same
    rule as `is_ref_in_scope` — no re-query. Missing / None row treated
    as in-scope.
    """
    if not row:
        return True
    return status_in_scope(row.get("applicability_status"))


def status_in_scope(applicability_status: Optional[str]) -> bool:
    """True iff a raw applicability_status scalar is in-scope.

    For callers that unpacked the scalar from a row tuple (Stage-2
    approval flow's fetchone() unpack). The single string comparison
    that every scope check in the codebase reduces to.
    """
    return applicability_status != "na"


def is_ref_in_scope(pg_conn, tenant_id: str, ref: str) -> bool:
    """True iff `ref` is in-scope for `tenant_id`.

    Silent-fail: returns True on any DB error (fail-open matches the
    rule "missing rows are in-scope"). Callers that want stricter
    behavior should catch upstream and inspect the exception directly.
    """
    if not (tenant_id and ref):
        return True
    try:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)",
                (tenant_id,),
            )
            cur.execute(
                """
                SELECT applicability_status
                  FROM posture_controls
                 WHERE tenant_id = %s::uuid
                   AND control_ref = %s
                   AND is_active = TRUE
                 LIMIT 1
                """,
                (tenant_id, ref),
            )
            row = cur.fetchone()
    except Exception:
        return True
    if row is None:
        return True
    return row[0] != "na"


def refs_in_scope(pg_conn, tenant_id: str, refs: Iterable[str]) -> set[str]:
    """Batch variant — one query for many refs. Returns the set of refs
    that ARE in scope. Convenient for callers that want to filter a list.

    Missing rows are treated as in-scope (same rule as
    `is_ref_in_scope`); refs that never appear in posture_controls end
    up in the returned set.
    """
    refs = [r for r in refs if r]
    if not (tenant_id and refs):
        return set(refs)
    try:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)",
                (tenant_id,),
            )
            cur.execute(
                """
                SELECT control_ref
                  FROM posture_controls
                 WHERE tenant_id = %s::uuid
                   AND control_ref = ANY(%s)
                   AND is_active = TRUE
                   AND applicability_status = 'na'
                """,
                (tenant_id, list(refs)),
            )
            na_refs = {row[0] for row in cur.fetchall()}
    except Exception:
        return set(refs)
    return set(refs) - na_refs
