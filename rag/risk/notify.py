"""
Ship 14'.f (2026-07-22) — risk-register notification producers.

Two entry points:

1. `emit_risk_added(pg_conn, tenant_id, ext_ref, threat)` —
   write-path producer. Called from the workbook importer
   (RowMappers.risks) or a future POST /risks endpoint when a
   new risks row is inserted. Fires immediately with severity
   `low` — a heads-up for the tenant that a new risk landed,
   not an alarm.

2. `sweep_risk_register_notify(pg_conn, tick_id, dry_run)` —
   periodic scan wired to the `risk_register_notify` work_type
   in `rag/scheduler/tick.py`. Emits three time-triggered
   notification kinds:
     * risk_treatment_overdue    — implementation_date past,
                                    status != implemented
     * residual_above_threshold  — residual_risk_level >= 15
     * risk_review_due           — review_date within 30d or past

All producers respect the standard 7-day dedup window per
(tenant, risk_id, kind) — matches the freshness_expiry pattern.

Framework role model discipline (Ship 14'.a addendum): none of
these notifications reference specific control refs — the risk
row's `control_refs TEXT[]` remains the linkage back to
program/extension/obligation controls, and the dashboard
drill-in surfaces those side-by-side. No role split here.
"""
from __future__ import annotations

import logging
from typing import Optional


logger = logging.getLogger(__name__)


# Standard dedup window in days (mirrors freshness_expiry).
_RISK_DEDUP_DAYS = 7

# Residual threshold — top quintile of the 1-25 scale.
_RESIDUAL_THRESHOLD = 15

# Review-due window — start warning this many days before review_date.
_REVIEW_DUE_WINDOW_DAYS = 30


# ── Write-path producer ──────────────────────────────────────


def emit_risk_added(
    pg_conn,
    tenant_id: str,
    external_ref: str,
    threat: Optional[str] = None,
) -> bool:
    """Fire a `risk_added` notification when a new risk row is
    inserted. Returns True on insert, False on dedup or missing
    input. Silent-fail on DB errors (never blocks the caller)."""
    if not tenant_id or not external_ref:
        return False
    try:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,)
            )
            # Dedup: same (tenant, external_ref, kind) within window?
            cur.execute(
                "SELECT 1 FROM tenant_notification "
                " WHERE tenant_id = %s::uuid "
                "   AND kind = 'risk_added' "
                "   AND related_entity_kind = 'risk' "
                "   AND title LIKE %s "
                "   AND fired_at > NOW() - make_interval(days => %s) "
                " LIMIT 1",
                (tenant_id, f"%{external_ref}%", _RISK_DEDUP_DAYS),
            )
            if cur.fetchone() is not None:
                return False
            title = f"New risk {external_ref} added to the register"
            body = (
                f"A new risk row (`{external_ref}`) was added. "
                f"{'Threat: ' + threat[:180] + '. ' if threat else ''}"
                f"Review the treatment plan and residual level to "
                f"confirm the row is complete per ISO 27005:2022 §8.6.1."
            )
            cur.execute(
                "INSERT INTO tenant_notification ("
                "  tenant_id, kind, title, body, severity, "
                "  related_entity_kind "
                ") VALUES (%s::uuid, 'risk_added', %s, %s, 'low', 'risk')",
                (tenant_id, title, body),
            )
        return True
    except Exception as e:
        logger.warning("emit_risk_added: swallowed error: %s", e)
        try: pg_conn.rollback()
        except Exception: pass
        return False


# ── Sweep — periodic scan ────────────────────────────────────


def sweep_risk_register_notify(pg_conn, tick_id: str, dry_run: bool = False) -> dict:
    """Per-tenant scan of the risks table. Emits three time-
    triggered notification kinds. Returns a summary dict per the
    tick.py sweep convention.

    Kinds:
      * risk_treatment_overdue    — implementation_date < CURRENT_DATE
                                     AND treatment_status <> 'implemented'
      * residual_above_threshold  — residual_risk_level >= 15
      * risk_review_due           — review_date < CURRENT_DATE + 30 days
                                     AND treatment_status <> 'implemented'

    Dedup per (tenant, risk_id, kind) within _RISK_DEDUP_DAYS.
    """
    # Import _log_start/_log_complete lazily to avoid circular deps.
    from rag.scheduler.tick import _log_start, _log_complete

    row_id = _log_start(pg_conn, tick_id, "risk_register_notify")

    scanned = 0
    acted   = 0
    errored = 0
    per_tenant: dict[str, dict] = {}
    error_type = error_detail = None

    try:
        # Fetch candidate risks across tenants.
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT id::text, tenant_id::text, external_ref, "
                "       threat, implementation_date, treatment_status, "
                "       residual_risk_level, review_date "
                "  FROM risks "
                " WHERE is_active = TRUE "
                "   AND (treatment_status IS NULL "
                "        OR treatment_status <> 'implemented') "
                "   AND ( "
                "        (implementation_date IS NOT NULL "
                "         AND implementation_date < CURRENT_DATE) "
                "     OR (residual_risk_level IS NOT NULL "
                "         AND residual_risk_level >= %s) "
                "     OR (review_date IS NOT NULL "
                "         AND review_date < CURRENT_DATE + INTERVAL '30 days') "
                "   )",
                (_RESIDUAL_THRESHOLD,),
            )
            rows = cur.fetchall()

        scanned = len(rows)

        # Group by tenant for tenant-scoped INSERTs.
        from collections import defaultdict
        by_tenant: dict[str, list] = defaultdict(list)
        for row in rows:
            by_tenant[row[1]].append(row)

        import datetime as _dt
        today = _dt.date.today()

        for tenant_id, tenant_rows in by_tenant.items():
            tenant_stats = {"overdue": 0, "above_threshold": 0, "review_due": 0, "deduped": 0}

            with pg_conn.cursor() as cur:
                cur.execute(
                    "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,)
                )
                for (
                    risk_id, _tid, ext_ref, threat, impl_date,
                    status, residual, review_date,
                ) in tenant_rows:

                    # Kind 1 — overdue treatment
                    if impl_date is not None and impl_date < today:
                        acted_here = _maybe_emit(
                            cur, tenant_id, risk_id, ext_ref,
                            kind      = "risk_treatment_overdue",
                            severity  = _overdue_severity(today, impl_date),
                            title     = f"Risk {ext_ref} treatment overdue",
                            body      = _overdue_body(ext_ref, threat, impl_date, today),
                            dry_run   = dry_run,
                        )
                        if acted_here is True:
                            tenant_stats["overdue"] += 1
                        elif acted_here is False:
                            tenant_stats["deduped"] += 1

                    # Kind 2 — residual above threshold
                    if residual is not None and residual >= _RESIDUAL_THRESHOLD:
                        acted_here = _maybe_emit(
                            cur, tenant_id, risk_id, ext_ref,
                            kind      = "residual_above_threshold",
                            severity  = "critical" if residual >= 20 else "high",
                            title     = f"Risk {ext_ref} residual level {residual}/25 above threshold",
                            body      = _residual_body(ext_ref, threat, residual),
                            dry_run   = dry_run,
                        )
                        if acted_here is True:
                            tenant_stats["above_threshold"] += 1
                        elif acted_here is False:
                            tenant_stats["deduped"] += 1

                    # Kind 3 — review due
                    if (review_date is not None
                            and review_date < today + _dt.timedelta(days=_REVIEW_DUE_WINDOW_DAYS)):
                        acted_here = _maybe_emit(
                            cur, tenant_id, risk_id, ext_ref,
                            kind      = "risk_review_due",
                            severity  = _review_severity(today, review_date),
                            title     = f"Risk {ext_ref} review due" + (" (past due)" if review_date < today else ""),
                            body      = _review_body(ext_ref, threat, review_date, today),
                            dry_run   = dry_run,
                        )
                        if acted_here is True:
                            tenant_stats["review_due"] += 1
                        elif acted_here is False:
                            tenant_stats["deduped"] += 1

            per_tenant[tenant_id[:8]] = tenant_stats
            acted += (tenant_stats["overdue"]
                      + tenant_stats["above_threshold"]
                      + tenant_stats["review_due"])

        if not dry_run:
            pg_conn.commit()

    except Exception as e:
        error_type = type(e).__name__
        error_detail = str(e)[:400]
        errored += 1
        try: pg_conn.rollback()
        except Exception: pass

    status = "completed" if error_type is None else "failed"
    detail = {
        "per_tenant":       per_tenant,
        "dedup_days":       _RISK_DEDUP_DAYS,
        "residual_thresh":  _RESIDUAL_THRESHOLD,
        "review_window_d":  _REVIEW_DUE_WINDOW_DAYS,
        "dry_run":          dry_run,
    }
    _log_complete(pg_conn, row_id, scanned, acted, errored, detail,
                  status=status, error_type=error_type, error_detail=error_detail)
    return {"work_type": "risk_register_notify", "scanned": scanned,
            "acted_on": acted, "errored": errored, "detail": detail}


# ── Helpers ──────────────────────────────────────────────────


def _maybe_emit(
    cur, tenant_id: str, risk_id: str, external_ref: str,
    kind: str, severity: str, title: str, body: str,
    dry_run: bool,
) -> Optional[bool]:
    """Dedup + insert. Returns:
      True  — inserted
      False — deduped (existing notification within window)
      None  — dry-run (no insert, no dedup check)

    Dedup uses `related_entity_id = risk_id` — matches the
    tenant_notification_active_unique partial unique index shape.
    """
    if dry_run:
        return None
    cur.execute(
        "SELECT 1 FROM tenant_notification "
        " WHERE tenant_id = %s::uuid "
        "   AND kind = %s "
        "   AND related_entity_id = %s::uuid "
        "   AND read_at IS NULL AND dismissed_at IS NULL "
        "   AND fired_at > NOW() - make_interval(days => %s) "
        " LIMIT 1",
        (tenant_id, kind, risk_id, _RISK_DEDUP_DAYS),
    )
    if cur.fetchone() is not None:
        return False
    cur.execute(
        "INSERT INTO tenant_notification ("
        "  tenant_id, kind, title, body, severity, "
        "  related_entity_kind, related_entity_id "
        ") VALUES (%s::uuid, %s, %s, %s, %s, 'risk', %s::uuid)",
        (tenant_id, kind, title, body, severity, risk_id),
    )
    return True


def _overdue_severity(today, impl_date) -> str:
    days = (today - impl_date).days
    if days > 90:  return "critical"
    if days > 30:  return "high"
    return "medium"


def _overdue_body(ext_ref, threat, impl_date, today) -> str:
    days = (today - impl_date).days
    threat_bit = f" ({threat[:120]})" if threat else ""
    return (
        f"Risk `{ext_ref}`{threat_bit} — the treatment "
        f"implementation date was {impl_date.isoformat()} "
        f"({days} days ago) but the row is not yet marked as "
        f"`implemented`. Per ISO 27005:2022 §9.2 you should either "
        f"update the status or revise the treatment plan."
    )


def _residual_body(ext_ref, threat, residual) -> str:
    threat_bit = f" ({threat[:120]})" if threat else ""
    return (
        f"Risk `{ext_ref}`{threat_bit} has a residual level of "
        f"{residual}/25 — at or above the top-quintile threshold "
        f"({_RESIDUAL_THRESHOLD}). Per ISO 27005:2022 §8.6.3 the "
        f"risk owner should explicitly accept the residual risk in "
        f"writing, or extend the treatment to bring it below the "
        f"threshold."
    )


def _review_severity(today, review_date) -> str:
    days = (review_date - today).days
    if days < 0:   return "high"     # past due
    if days < 7:   return "medium"
    return "low"


def _review_body(ext_ref, threat, review_date, today) -> str:
    threat_bit = f" ({threat[:120]})" if threat else ""
    days = (review_date - today).days
    if days < 0:
        when = f"{-days} days ago"
    elif days == 0:
        when = "today"
    else:
        when = f"in {days} days"
    return (
        f"Risk `{ext_ref}`{threat_bit} — review is due {when} "
        f"({review_date.isoformat()}). Per ISO 27005:2022 §10 "
        f"the risk should be re-assessed and the treatment plan "
        f"updated as needed."
    )
