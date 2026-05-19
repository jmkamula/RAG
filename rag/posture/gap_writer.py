"""ArionComply — persistent per-leaf gap writer.

Writes tenant_evidence_gaps rows from the engine's ControlVerdict output.

Lifecycle handled here:
  - Unsatisfied leaf seen by the engine → UPSERT a row by
    (tenant_id, control_id, leaf_id). Insert with status='open'; update
    refreshes gap_summary/gap_items/last_seen_at *without* touching the
    rationale or acknowledged_* columns (an existing acknowledgement
    survives the re-run, which is the whole point of persistence).
  - Leaf previously failing but no longer in the engine's unsatisfied set
    → mark status='resolved', resolved_at=NOW(). Rationale/acknowledged_*
    stay intact as audit trail.

Out of scope here: acknowledging a gap (status open → acknowledged) — that's
the chat surface's job (see chat_acknowledge.py / similar). This module
only handles the engine→Postgres writeback.

RLS: arioncomply_app role has no BYPASSRLS, so every cursor first calls
SELECT set_config('app.tenant_id', ..., TRUE).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from rag.posture.fulfilment_engine import ControlVerdict, LeafVerdict

logger = logging.getLogger(__name__)


@dataclass
class GapWriteStats:
    opened:   int = 0
    updated:  int = 0
    resolved: int = 0

    def as_dict(self) -> dict:
        return {"opened": self.opened, "updated": self.updated, "resolved": self.resolved}


def upsert_evidence_gaps(
    pg_conn,
    tenant_id:    str,
    verdicts:     dict[str, ControlVerdict],
) -> GapWriteStats:
    """For every verdict in `verdicts`, persist its unsatisfied leaves and
    resolve any prior gaps that are no longer reported.

    Errors during the write are logged but never raised: gap persistence is
    a side-effect; the engine's primary purpose (computing verdicts for the
    posture overlay) must not be blocked.
    """
    stats = GapWriteStats()
    if not verdicts:
        return stats

    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))

            for cid, verdict in verdicts.items():
                _upsert_one_control(cur, tenant_id, cid, verdict, stats)
        pg_conn.commit()
    except Exception as e:
        logger.warning("gap_writer: upsert_evidence_gaps failed: %s", e)
        try:
            pg_conn.rollback()
        except Exception:
            pass
    return stats


def _upsert_one_control(
    cur,
    tenant_id: str,
    control_id: str,
    verdict: ControlVerdict,
    stats: GapWriteStats,
) -> None:
    # Build the current unsatisfied-leaf set; if a verdict is Comply or
    # NotApplicable or UNKNOWN the unsatisfied set is empty and we just
    # resolve any prior leftovers.
    failing_leaves = [l for l in verdict.leaves if not l.counts_as_comply]
    failing_ids    = {l.leaf_id for l in failing_leaves}

    # 1. Upsert failing leaves
    for leaf in failing_leaves:
        gap_summary = _leaf_summary(leaf)
        gap_items   = list(leaf.items_unrecognised)
        cur.execute(
            """
            INSERT INTO tenant_evidence_gaps (
                tenant_id, control_id, control_ref, standard_id,
                leaf_id, role, evidence_type,
                gap_summary, gap_items
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (tenant_id, control_id, leaf_id) DO UPDATE
              SET gap_summary  = EXCLUDED.gap_summary,
                  gap_items    = EXCLUDED.gap_items,
                  role         = EXCLUDED.role,
                  evidence_type= EXCLUDED.evidence_type,
                  last_seen_at = now(),
                  updated_at   = now(),
                  -- If a previously resolved gap reappears, flip it back to
                  -- 'open' (engine says it's failing again). Don't touch a
                  -- row that's currently 'acknowledged'.
                  status       = CASE
                                   WHEN tenant_evidence_gaps.status = 'resolved'
                                     THEN 'open'
                                   ELSE tenant_evidence_gaps.status
                                 END,
                  resolved_at  = CASE
                                   WHEN tenant_evidence_gaps.status = 'resolved'
                                     THEN NULL
                                   ELSE tenant_evidence_gaps.resolved_at
                                 END
            RETURNING (xmax = 0) AS inserted
            """,
            (
                tenant_id, control_id,
                _ctrl_ref(control_id), _std_id(control_id),
                leaf.leaf_id, leaf.role or leaf.evidence_type, leaf.evidence_type,
                gap_summary, gap_items,
            ),
        )
        row = cur.fetchone()
        if row and row[0]:
            stats.opened += 1
        else:
            stats.updated += 1

    # 2. Resolve prior rows for this control whose leaf is no longer failing.
    #    We only touch open/acknowledged rows — already-resolved stay alone.
    if failing_ids:
        cur.execute(
            """
            UPDATE tenant_evidence_gaps
               SET status      = 'resolved',
                   resolved_at = now(),
                   updated_at  = now()
             WHERE tenant_id  = %s
               AND control_id = %s
               AND status     IN ('open', 'acknowledged')
               AND leaf_id    NOT IN %s
            """,
            (tenant_id, control_id, tuple(failing_ids)),
        )
    else:
        cur.execute(
            """
            UPDATE tenant_evidence_gaps
               SET status      = 'resolved',
                   resolved_at = now(),
                   updated_at  = now()
             WHERE tenant_id  = %s
               AND control_id = %s
               AND status     IN ('open', 'acknowledged')
            """,
            (tenant_id, control_id),
        )
    stats.resolved += cur.rowcount or 0


def _leaf_summary(leaf: LeafVerdict) -> str:
    """Short auditor-style line for the gap_summary column."""
    role = leaf.role or leaf.evidence_type
    if not leaf.fresh and leaf.satisfied:
        return f"[{role}] artifact present but stale — consider refreshing"
    if leaf.items_unrecognised:
        head = leaf.items_unrecognised[0]
        if len(leaf.items_unrecognised) == 1:
            tail = ""
        else:
            tail = f" (+{len(leaf.items_unrecognised) - 1} more)"
        return f"[{role}] auditors expect: {head} — we couldn't find it{tail}"
    return f"[{role}] no matching artifact uploaded"


def _ctrl_ref(control_id: str) -> str:
    """ISO27001:2022:A.5.1 → A.5.1; GDPR:2016/679:Art.32 → Art.32."""
    return control_id.rsplit(":", 1)[-1] if ":" in control_id else control_id


def _std_id(control_id: str) -> str:
    """ISO27001:2022:A.5.1 → ISO27001:2022."""
    return control_id.rsplit(":", 1)[0] if ":" in control_id else ""


# ── Read-side helper: which gaps are acknowledged for a given control? ─────────

def get_acknowledged_leaves(
    pg_conn,
    tenant_id: str,
    control_id: str,
) -> dict[str, dict]:
    """Returns {leaf_id: {rationale, acknowledged_by, acknowledged_at}} for
    currently acknowledged gaps of a single control. Read-only; used by
    posture_loader's headline-suppression layer."""
    out: dict[str, dict] = {}
    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            cur.execute(
                """
                SELECT leaf_id, rationale, acknowledged_by, acknowledged_at
                  FROM tenant_evidence_gaps
                 WHERE tenant_id  = %s
                   AND control_id = %s
                   AND status     = 'acknowledged'
                """,
                (tenant_id, control_id),
            )
            for leaf_id, rationale, ack_by, ack_at in cur.fetchall():
                out[leaf_id] = {
                    "rationale":       rationale or "",
                    "acknowledged_by": ack_by or "",
                    "acknowledged_at": ack_at,
                }
    except Exception as e:
        logger.warning("gap_writer: get_acknowledged_leaves failed: %s", e)
    return out
