"""
ArionComply — Cascade → posture overlay (S3e)

Wires cascade output (triggered_implication rows) back into the
posture surface. Two functions:

  compute_cascade_pressure(pg_conn, tenant_id)
    Returns per-control aggregation of pending + overdue implication
    counts. Pure read; no side effects. Used by the dashboard
    endpoint to surface cascade pressure alongside live posture.

  propose_from_cascade(pg_conn, tenant_id, pressure)
    Writes posture_assertions (source='engine', set_by='cascade:...')
    for controls where cascade pressure crosses thresholds. Calls
    set_assertion which supersedes any prior cascade assertion for
    the same control. Conservative thresholds (see _proposal_for):
      overdue >= 1 on Comply control  -> propose OFI
      overdue >= 3                     -> propose NC
      overdue == 0 + pending only      -> no proposal (tenant has time)

The overlay writes PAs at status='pending' so they enter the existing
Stage-2 review queue; tenant can approve/reject as with any engine
proposal. This intentionally piggy-backs on the engine PA path
rather than introducing a new source value — avoids invasive
CHECK-constraint changes and gets Stage-2 lifecycle for free.

Why thresholds aren't aggressive:
  Cascade output reflects evidence freshness/timeliness, not
  underlying control failure. A single overdue training-row
  implication doesn't justify flipping a well-evidenced control to
  NC immediately; ramping to OFI signals attention is needed,
  multiple overdue signals genuine erosion.
"""
from __future__ import annotations
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ── Public surface ────────────────────────────────────────────────────────

def compute_cascade_pressure(pg_conn, tenant_id: str) -> dict[str, dict]:
    """Aggregate triggered_implication rows per control.

    Returns dict keyed by target_requirement_id (e.g.
    'ISO27001:2022:A.6.3'), each value:
      {
        "pending_count":   int,   # status='pending' AND due_date >= now() or NULL
        "overdue_count":   int,   # status='pending' AND due_date < now()
        "satisfied_count": int,   # status='satisfied' (lifetime)
        "dismissed_count": int,   # status='dismissed' (lifetime)
        "most_recent":     iso str,  # max(fired_at)
      }

    Caller is responsible for the tenant context GUC. Read-only.
    """
    with pg_conn.cursor() as cur:
        cur.execute(
            """
            SELECT target_requirement_id,
                   sum(CASE WHEN status = 'pending'
                              AND (due_date IS NULL OR due_date >= now())
                            THEN 1 ELSE 0 END) AS pending_count,
                   sum(CASE WHEN status = 'pending'
                              AND due_date IS NOT NULL
                              AND due_date < now()
                            THEN 1 ELSE 0 END) AS overdue_count,
                   sum(CASE WHEN status = 'satisfied' THEN 1 ELSE 0 END) AS satisfied_count,
                   sum(CASE WHEN status = 'dismissed' THEN 1 ELSE 0 END) AS dismissed_count,
                   max(fired_at) AS most_recent
              FROM triggered_implication
             WHERE tenant_id = %s::uuid
             GROUP BY target_requirement_id
            """,
            (tenant_id,),
        )
        rows = cur.fetchall()

    out: dict[str, dict] = {}
    for r in rows:
        out[r[0]] = {
            "pending_count":   int(r[1] or 0),
            "overdue_count":   int(r[2] or 0),
            "satisfied_count": int(r[3] or 0),
            "dismissed_count": int(r[4] or 0),
            "most_recent":     r[5].isoformat() if r[5] else None,
        }
    return out


def _proposal_for(live_posture: Optional[str],
                  pending: int, overdue: int) -> Optional[str]:
    """Decide whether to propose a cascade-driven posture change.

    Returns the proposed finding ('OFI' / 'NC') or None for "no proposal".
    Skips when live_posture is N/A or Not assessed (cascade pressure on
    N/A controls is noise — tenant said it doesn't apply).
    """
    if live_posture in ("N/A", "Not assessed"):
        return None
    if overdue >= 3:
        return "NC"
    if overdue >= 1 and live_posture == "Comply":
        return "OFI"
    if overdue >= 1 and live_posture == "OFI":
        # Stay at OFI; no further cascade flip until threshold crossed.
        return None
    return None


def propose_from_cascade(pg_conn, tenant_id: str,
                         pressure: dict[str, dict],
                         live_postures: dict[str, str]) -> int:
    """Write cascade-derived posture assertions where threshold crossed.

    Args:
      pg_conn:        active connection; tenant GUC already set by caller.
      tenant_id:      uuid string.
      pressure:       output of compute_cascade_pressure.
      live_postures:  dict[control_id, posture_finding] — the current
                      tenant-attested posture per control (e.g. 'Comply').
                      Used to gate proposals (cascade only flips Comply
                      and OFI, never raises NC).

    Returns count of proposals written. Idempotency-aware via supersession:
    repeated calls write a new pending row only when the proposed finding
    changes.
    """
    from rag.posture.assertions import set_assertion

    written = 0
    with pg_conn.cursor() as cur:
        cur.execute(
            "SELECT set_config('app.tenant_id', %s, TRUE)",
            (tenant_id,),
        )
        for req_id, p in pressure.items():
            overdue = p.get("overdue_count", 0)
            pending = p.get("pending_count", 0)
            live = live_postures.get(req_id)
            proposed = _proposal_for(live, pending, overdue)
            if not proposed:
                continue

            if ":" not in req_id:
                continue
            standard_id, control_ref = req_id.rsplit(":", 1)

            # Idempotency: check current cascade-sourced PA for this control;
            # skip if same finding already pending or active.
            cur.execute(
                """
                SELECT finding, status
                  FROM posture_assertions
                 WHERE tenant_id   = %s::uuid
                   AND control_ref = %s
                   AND standard_id = %s
                   AND source      = 'engine'
                   AND set_by LIKE 'cascade:%%'
                   AND status      IN ('active', 'pending')
                 ORDER BY set_at DESC
                 LIMIT 1
                """,
                (tenant_id, control_ref, standard_id),
            )
            row = cur.fetchone()
            if row and row[0] == proposed:
                # Already proposing this exact finding — no-op
                continue

            try:
                set_assertion(
                    cur,
                    tenant_id   = tenant_id,
                    control_ref = control_ref,
                    standard_id = standard_id,
                    source      = "engine",
                    finding     = proposed,
                    set_by      = f"cascade:overdue:{overdue}",
                    gap_description = (
                        f"Cascade pressure: {overdue} overdue and {pending} pending "
                        f"triggered implication(s) on this control"
                    ),
                    confidence  = "medium",
                    status      = "pending",
                    metadata    = {
                        "kind":            "cascade_overlay",
                        "overdue_count":   overdue,
                        "pending_count":   pending,
                        "satisfied_count": p.get("satisfied_count", 0),
                        "live_posture":    live,
                    },
                )
                written += 1
                # S3t: notify on overdue cascade pressure
                if overdue >= 1:
                    try:
                        from rag.cascade.notify import notify
                        sev = "critical" if proposed == "NC" else "high"
                        notify(
                            cur,
                            tenant_id           = tenant_id,
                            kind                = "implication_overdue",
                            title               = (f"Cascade pressure on {control_ref}: "
                                                   f"{overdue} overdue implication(s)"),
                            body                = (f"Cascade overlay proposing {proposed} on "
                                                   f"{control_ref} (was {live or 'unassessed'}). "
                                                   f"{overdue} overdue + {pending} pending "
                                                   f"triggered_implication rows."),
                            severity            = sev,
                            related_entity_kind = "triggered_implication",
                            related_control_ref = control_ref,
                        )
                    except Exception:
                        pass
            except Exception as ex:
                logger.warning("cascade overlay PA write failed for %s: %s",
                               req_id, ex)
                continue
    return written
