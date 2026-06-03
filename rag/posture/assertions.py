"""ArionComply — posture assertions writer (Phase 1a).

Helper for the new per-source truth table `posture_assertions`. Writers will
swap to this in Phase 1b; in Phase 1a the table is kept current by a
reverse-sync trigger on `posture_controls` (see schema_v29) and this module
is unused at runtime. Shipping it together with the schema so the writer
swap in 1b is a pure call-site change, not a new-code-+-call-site change.

Semantics:
  * Append-only with supersession. The prior active (or pending) row for
    (tenant_id, control_ref, standard_id, source) is marked status=
    'superseded' + superseded_at=NOW() + superseded_by_id=<new_id>. The
    new row is INSERTed at status='active' (or 'pending').
  * 'active' and 'pending' partition independently — a control can have
    both simultaneously (engine pending verdict awaiting Stage-2 + tenant
    active claim). set_assertion() supersedes only within the same
    status partition.
  * Caller manages tenant_id context via set_config('app.tenant_id', ...).
    arioncomply_app does NOT bypass RLS.
  * Caller owns commit/rollback. This helper does neither.

RLS: every cursor must first call SELECT set_config('app.tenant_id', %s, TRUE).
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


VALID_SOURCES  = frozenset({"tenant", "assessor", "engine"})
VALID_FINDINGS = frozenset({"NC", "OFI", "Comply", "N/A", "Not assessed"})
VALID_STATUSES = frozenset({"active", "pending"})


def set_assertion(
    cur,
    *,
    tenant_id:       str,
    control_ref:     str,
    standard_id:     str,
    source:          str,
    finding:         str,
    set_by:          str,
    gap_description: Optional[str]            = None,
    confidence:      Optional[str]            = None,
    status:          str                       = "active",
    metadata:        Optional[dict[str, Any]]  = None,
) -> int:
    """Supersede prior active/pending row + INSERT new row, return new id.

    Atomic within the caller's transaction. The partial unique indexes on
    posture_assertions guarantee at most one active and one pending row per
    (tenant_id, control_ref, standard_id, source); supersession + INSERT
    happen in the same transaction so neither side observes a duplicate.

    Args:
        cur: psycopg2 cursor (tenant context already set).
        tenant_id:       UUID string of the tenant.
        control_ref:     e.g. 'A.5.18', 'Art.32'.
        standard_id:     e.g. 'ISO27001:2022', 'GDPR:2016/679'.
        source:          one of 'tenant' | 'assessor' | 'engine'.
        finding:         one of 'NC' | 'OFI' | 'Comply' | 'N/A' | 'Not assessed'.
        set_by:          identifier of the writer ('engine', user_id, etc.).
        gap_description: free-text gap narrative (nullable).
        confidence:      'high' | 'medium' | 'low' (nullable; engine sets, tenant usually doesn't).
        status:          'active' (default) | 'pending' (engine proposal awaiting approval).
        metadata:        source-specific extras stored as JSONB. Caller's
                         responsibility to keep keys consistent across writes.

    Returns:
        The new assertion id (bigint).

    Raises:
        ValueError if source/finding/status fails enum check (cheaper than a DB roundtrip).
    """
    if source not in VALID_SOURCES:
        raise ValueError(f"invalid source: {source!r} (allowed: {sorted(VALID_SOURCES)})")
    if finding not in VALID_FINDINGS:
        raise ValueError(f"invalid finding: {finding!r} (allowed: {sorted(VALID_FINDINGS)})")
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status: {status!r} (allowed: {sorted(VALID_STATUSES)})")

    # Supersede the prior row of the same status partition.
    cur.execute(
        """
        UPDATE posture_assertions
           SET status        = 'superseded',
               superseded_at = NOW()
         WHERE tenant_id   = %s
           AND control_ref = %s
           AND standard_id = %s
           AND source      = %s
           AND status      = %s
         RETURNING id
        """,
        (tenant_id, control_ref, standard_id, source, status),
    )
    row = cur.fetchone()
    prior_id = row[0] if row else None

    cur.execute(
        """
        INSERT INTO posture_assertions (
            tenant_id, control_ref, standard_id, source,
            finding, gap_description, confidence,
            set_by, status, metadata
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
        RETURNING id
        """,
        (
            tenant_id, control_ref, standard_id, source,
            finding, gap_description, confidence,
            set_by, status,
            json.dumps(metadata or {}),
        ),
    )
    new_id = cur.fetchone()[0]

    if prior_id is not None:
        cur.execute(
            "UPDATE posture_assertions SET superseded_by_id = %s WHERE id = %s",
            (new_id, prior_id),
        )

    logger.debug(
        "posture_assertion %s: tenant=%s control=%s std=%s source=%s status=%s finding=%s (supersedes %s)",
        new_id, tenant_id, control_ref, standard_id, source, status, finding, prior_id,
    )
    return new_id


def get_active_assertions(
    cur,
    *,
    tenant_id:   str,
    control_ref: str,
    standard_id: str,
) -> dict[str, dict]:
    """Read the latest active assertion per source for one control.

    Returns a dict keyed by source ('tenant', 'assessor', 'engine') mapping
    to {finding, gap_description, confidence, set_by, set_at, metadata}.
    Missing sources are absent from the dict. Used by chat composition
    (Phase 1c) to surface divergence; included here so callers don't have
    to roll their own query.
    """
    cur.execute(
        """
        SELECT source, finding, gap_description, confidence,
               set_by, set_at, metadata
          FROM posture_assertions
         WHERE tenant_id   = %s
           AND control_ref = %s
           AND standard_id = %s
           AND status      = 'active'
        """,
        (tenant_id, control_ref, standard_id),
    )
    return {
        row[0]: {
            "finding":         row[1],
            "gap_description": row[2],
            "confidence":      row[3],
            "set_by":          row[4],
            "set_at":          row[5],
            "metadata":        row[6],
        }
        for row in cur.fetchall()
    }


def get_pending_proposal(
    cur,
    *,
    tenant_id:   str,
    control_ref: str,
    standard_id: str,
    source:      str = "engine",
) -> Optional[dict]:
    """Return the pending engine proposal (or None) for Stage-2 surfaces.

    Defaults to engine since tenant + assessor sources don't go through
    pending today, but the column is uniform so future paths can use it.
    """
    cur.execute(
        """
        SELECT id, finding, gap_description, confidence,
               set_by, set_at, metadata
          FROM posture_assertions
         WHERE tenant_id   = %s
           AND control_ref = %s
           AND standard_id = %s
           AND source      = %s
           AND status      = 'pending'
        """,
        (tenant_id, control_ref, standard_id, source),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return {
        "id":              row[0],
        "finding":         row[1],
        "gap_description": row[2],
        "confidence":      row[3],
        "set_by":          row[4],
        "set_at":          row[5],
        "metadata":        row[6],
    }
