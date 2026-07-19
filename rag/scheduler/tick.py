"""
Periodic sweep tick — Wave 3b (2026-07-13).

Stateless entry point invoked by cron / systemd timer:

    python -m rag.scheduler.tick                   # runs all work types
    python -m rag.scheduler.tick --work fact_recompute
    python -m rag.scheduler.tick --dry-run

Each invocation:
  1. Generates a `tick_id` (UUID) that groups all work-type rows
     from this tick in `sweep_log`
  2. For each configured work type, runs the sweep function
  3. Logs one `sweep_log` row per work_type (running → completed/failed)
  4. Exits with code 0 (all completed) or 1 (any failed)

Work types (registered in _WORK_TYPES at the bottom):

  fact_recompute — for each fact in fact_source_config, for each tenant
    whose last recompute is older than refresh_days, call
    rag.facts.recompute.recompute_client_fact. Batched per fact —
    all tenants for one fact in one loop, so a slow config doesn't
    stall the batch.

  overdue_followups — backstop for cascade write-path (engine.py:1085
    + posture_overlay.py:205). Marks expected_followup_event rows
    'overdue' when expires_at has passed; fires followup_overdue +
    implication_overdue notifications. Severity by cascade_depth.
    See Ship 3'.f.

  freshness_expiry — Comply postures past their leaf's freshness_days
    fire a freshness_expiry notification. Severity ladder by
    staleness_ratio (medium / high / critical). 7-day dedup window.
    See Ship 3'.b.

  cite_verification_overdue — active external_evidence_source rows
    past next_review_due. Auditor-critical: severity skews harder
    than freshness (never-verified → critical, past-due → critical
    / high). 7-day dedup window. See Ship 3'.g.

  api_key_expiring — api_keys.expires_at approaching. Three
    escalating buckets (30d medium / 7d high / 1d critical) using
    the bucket label in related_control_ref for per-bucket dedup.
    See Ship 3'.i.

  notification_delivery — SMTP + Slack workers (rag.notifications.
    deliver.deliver_all). Severity gate, dedup on already-delivered,
    retry until >7 days old. See Ship 3'.a.

  notification_retention — hard-delete stale tenant_notification +
    notification_delivery_attempt rows. Three delete rules
    (dismissed 30d / read 90d / max_age 365d) + attempt aging (90d).
    See Ship 3'.k.

Zero external dependencies beyond psycopg2 + the app code. Safe to
run multiple invocations concurrently — each writes its own tick_id
rows (no shared state). If two invocations happen to recompute the
same fact at the same instant, the last write wins on client_facts;
both attempts land in fact_recompute_log.
"""
from __future__ import annotations
import argparse
import json
import logging
import os
import sys
import time
import uuid
from typing import Optional

logger = logging.getLogger(__name__)


# ── DB connection helper ─────────────────────────────────────────────

def _connect():
    import psycopg2
    return psycopg2.connect(
        host    = os.getenv("PGHOST", "127.0.0.1"),
        dbname  = os.getenv("PGDATABASE", "arioncomply_compliance"),
        user    = os.getenv("PGUSER", "arioncomply_app"),
        password= os.getenv("PGPASSWORD", ""),
    )


# ── sweep_log helpers ────────────────────────────────────────────────

def _log_start(pg_conn, tick_id: str, work_type: str) -> str:
    """Insert a 'running' sweep_log row. Returns the row id so caller
    can update it on completion."""
    with pg_conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO sweep_log (tick_id, work_type, started_at, status)
                 VALUES (%s::uuid, %s, NOW(), 'running')
              RETURNING id
            """,
            (tick_id, work_type),
        )
        row_id = cur.fetchone()[0]
    pg_conn.commit()
    return str(row_id)


def _log_complete(
    pg_conn,
    row_id:         str,
    items_scanned:  int,
    items_acted_on: int,
    items_error:    int,
    detail:         dict,
    status:         str = "completed",
    error_type:     Optional[str] = None,
    error_detail:   Optional[str] = None,
) -> None:
    with pg_conn.cursor() as cur:
        cur.execute(
            """
            UPDATE sweep_log
               SET completed_at   = NOW(),
                   status         = %s,
                   items_scanned  = %s,
                   items_acted_on = %s,
                   items_error    = %s,
                   detail         = %s::jsonb,
                   error_type     = %s,
                   error_detail   = %s
             WHERE id = %s::uuid
            """,
            (status, items_scanned, items_acted_on, items_error,
             json.dumps(detail or {}), error_type, error_detail, row_id),
        )
    pg_conn.commit()


# ── Work-type implementations ────────────────────────────────────────

def sweep_fact_recompute(pg_conn, tick_id: str, dry_run: bool = False) -> dict:
    """For each active fact in fact_source_config, find tenants whose
    last recompute is older than refresh_days (or never happened),
    and call recompute_client_fact for each.

    Returns a summary dict written into sweep_log.detail.
    """
    row_id = _log_start(pg_conn, tick_id, "fact_recompute")
    scanned = acted = errored = 0
    per_fact: dict[str, dict] = {}
    error_type = None
    error_detail = None

    try:
        # Load active facts + refresh_days
        with pg_conn.cursor() as cur:
            cur.execute(
                """
                SELECT fact_key, refresh_days
                  FROM fact_source_config
                 WHERE is_active = TRUE
                """
            )
            facts = cur.fetchall()

        from rag.facts.recompute import recompute_client_fact
        for fact_key, refresh_days in facts:
            # Find tenants whose last recompute of this fact is older
            # than refresh_days (or never recomputed at all).
            with pg_conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT t.id
                      FROM tenants t
                     WHERE t.is_active = TRUE
                       AND NOT EXISTS (
                             SELECT 1 FROM fact_recompute_log frl
                              WHERE frl.tenant_id = t.id
                                AND frl.fact_key  = %s
                                AND frl.computed_at > NOW() - make_interval(days => %s)
                           )
                    """,
                    (fact_key, refresh_days),
                )
                tenants_due = [r[0] for r in cur.fetchall()]

            fact_summary = {
                "refresh_days":   refresh_days,
                "tenants_due":    len(tenants_due),
                "tenants_updated": 0,
                "tenants_errored": 0,
            }
            for tenant_id in tenants_due:
                scanned += 1
                if dry_run:
                    continue
                try:
                    r = recompute_client_fact(pg_conn, str(tenant_id), fact_key)
                    if r.changed:
                        fact_summary["tenants_updated"] += 1
                        acted += 1
                    if r.error_type:
                        fact_summary["tenants_errored"] += 1
                        errored += 1
                except Exception as e:
                    logger.warning(
                        "fact_recompute failed for %s / %s: %s",
                        fact_key, tenant_id, e,
                    )
                    fact_summary["tenants_errored"] += 1
                    errored += 1
            per_fact[fact_key] = fact_summary
    except Exception as e:
        error_type   = type(e).__name__
        error_detail = str(e)[:400]
        logger.error("sweep_fact_recompute failed: %s", e)

    status = "completed" if error_type is None else "failed"
    detail = {"per_fact": per_fact, "dry_run": dry_run}
    _log_complete(pg_conn, row_id, scanned, acted, errored, detail,
                  status=status, error_type=error_type, error_detail=error_detail)
    return {"work_type": "fact_recompute", "scanned": scanned,
            "acted_on": acted, "errored": errored, "detail": detail}


def sweep_overdue_followups(pg_conn, tick_id: str, dry_run: bool = False) -> dict:
    """Backstop sweep for cascade follow-ups that missed the write-path notify.

    The cascade engine (`rag/cascade/engine.py`) and posture overlay
    (`rag/cascade/posture_overlay.py`) fire `followup_overdue` +
    `implication_overdue` notifications INLINE when they see a
    pending expected_followup_event past `expires_at` or a
    triggered_implication past `due_date`. That path only runs when
    another verification write triggers cascade reprocessing — if
    no write happens after the deadline, nothing fires.

    This sweep is the safety net. It runs across all tenants every
    tick, marks expired expected_followup_event rows as 'overdue'
    (mirror of engine.py:1085), notifies for both classes, and
    lets the partial unique index on tenant_notification dedup
    against write-path notifications that already fired.

    Structure per-tenant so RLS + app.tenant_id GUC work correctly.
    """
    row_id = _log_start(pg_conn, tick_id, "overdue_followups")
    scanned    = 0
    acted      = 0
    errored    = 0
    per_tenant: dict[str, dict] = {}
    error_type = error_detail = None

    try:
        from collections import defaultdict

        # ── Step 1: gather pending overdue rows across all tenants ──
        # Uses arioncomply_app's permissive `app_*_all` policies via
        # `USING (true)` grants added in Ship 3'.d — same pattern as
        # sweep_freshness_expiry. Table-owner-set RLS on the individual
        # cascade tables still needs the per-tenant GUC on WRITES.
        expected_by_tenant:  dict[str, list] = defaultdict(list)
        implication_by_tenant: dict[str, list] = defaultdict(list)

        with pg_conn.cursor() as cur:
            if _table_exists(cur, "expected_followup_event"):
                cur.execute("""
                    SELECT tenant_id::text,
                           id::text,
                           source_event_type,
                           expected_event_type,
                           window_days,
                           expires_at
                      FROM expected_followup_event
                     WHERE status     = 'pending'
                       AND expires_at < NOW()
                     ORDER BY tenant_id, expires_at
                """)
                for row in cur.fetchall():
                    expected_by_tenant[row[0]].append(row[1:])

            if _table_exists(cur, "triggered_implication"):
                cur.execute("""
                    SELECT tenant_id::text,
                           id::text,
                           target_control_ref,
                           target_standard_id,
                           expected_action,
                           due_date,
                           cascade_depth
                      FROM triggered_implication
                     WHERE status   = 'pending'
                       AND due_date IS NOT NULL
                       AND due_date < NOW()
                     ORDER BY tenant_id, due_date
                """)
                for row in cur.fetchall():
                    implication_by_tenant[row[0]].append(row[1:])

        all_tenants = set(expected_by_tenant.keys()) | set(implication_by_tenant.keys())
        scanned = sum(len(v) for v in expected_by_tenant.values()) + \
                  sum(len(v) for v in implication_by_tenant.values())

        if dry_run or not all_tenants:
            _log_complete(
                pg_conn, row_id, scanned, acted, errored,
                {"per_tenant": {}, "dry_run": dry_run},
                status="completed",
            )
            return {"work_type": "overdue_followups", "scanned": scanned,
                    "acted_on": 0, "errored": 0,
                    "detail": {"per_tenant": {}, "dry_run": dry_run}}

        # ── Step 2: per-tenant mark + notify ────────────────────────
        from rag.cascade.notify import notify as _notify

        for tenant_id in all_tenants:
            tenant_acted = 0
            expected_rows = expected_by_tenant.get(tenant_id, [])
            impl_rows     = implication_by_tenant.get(tenant_id, [])

            with pg_conn.cursor() as cur:
                cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                            (tenant_id,))

                # expected_followup_event: mark 'overdue' + notify.
                # Mirror of engine.py:1085 but scoped to still-pending
                # rows we already fetched (no re-race).
                for (fid, src_event, exp_event, window_d, expires_at) in expected_rows:
                    cur.execute("""
                        UPDATE expected_followup_event
                           SET status      = 'overdue',
                               resolved_at = NOW()
                         WHERE id     = %s::uuid
                           AND status = 'pending'
                        RETURNING id
                    """, (fid,))
                    if cur.fetchone() is None:
                        # Another writer got there first — skip notify.
                        continue

                    # Ship 7'.b — humanise event slugs through the
                    # output gateway so downstream frameworks (SOC 2,
                    # NIS2, etc.) get consistent tenant-facing display
                    # without editing this producer.
                    from rag.output import humanize as _humanize
                    src_h = _humanize(src_event, surface="notification_title")
                    exp_h = _humanize(exp_event, surface="notification_title")
                    _title = (f"Follow-up overdue: "
                              f"'{src_h}' expected '{exp_h}'")
                    _body  = _humanize(
                        f"It's been {window_d} day"
                        f"{'s' if window_d != 1 else ''} since "
                        f"'{src_event}' fired and we still don't have "
                        f"the expected '{exp_event}' follow-up on file.",
                        surface="notification_body",
                    )
                    result = _notify(
                        cur,
                        tenant_id           = tenant_id,
                        kind                = "followup_overdue",
                        title               = _title,
                        body                = _body,
                        severity            = "high",
                        related_entity_kind = "expected_followup_event",
                        related_entity_id   = fid,
                        related_event_type  = src_event,
                    )
                    if result is not None:
                        tenant_acted += 1

                # triggered_implication: notify only. The table has no
                # 'overdue' status in its CHECK — pending is expected
                # while the tenant works remediation. Dedup via the
                # partial unique index (kind + implication_id).
                for (impl_id, ctrl_ref, std_id, exp_action, due_date, depth) in impl_rows:
                    # Ship 7'.b — same gateway pass; action slugs
                    # ('access_review_required') render as prose.
                    from rag.output import humanize as _humanize
                    _title = _humanize(
                        f"Overdue: {ctrl_ref} requires {exp_action}",
                        surface="notification_title",
                    )
                    _body  = _humanize(
                        f"A cascade follow-up on {ctrl_ref} is past due. "
                        f"Expected action: {exp_action}. Depth "
                        f"{depth} in the cascade path.",
                        surface="notification_body",
                    )
                    # Severity by cascade depth — deeper implications
                    # tend to be secondary/derivative and can be lower
                    # priority; direct (depth 0-1) implications rank
                    # critical because the parent event's SLA is
                    # actively slipping.
                    severity = "critical" if depth <= 1 else "high"
                    result = _notify(
                        cur,
                        tenant_id           = tenant_id,
                        kind                = "implication_overdue",
                        title               = _title,
                        body                = _body,
                        severity            = severity,
                        related_entity_kind = "triggered_implication",
                        related_entity_id   = impl_id,
                        related_control_ref = ctrl_ref,
                        related_event_type  = exp_action,
                    )
                    if result is not None:
                        tenant_acted += 1

            if tenant_acted or expected_rows or impl_rows:
                per_tenant[tenant_id[:8]] = {
                    "expected_overdue":     len(expected_rows),
                    "implications_overdue": len(impl_rows),
                    "notified":             tenant_acted,
                }
            acted += tenant_acted

        pg_conn.commit()
    except Exception as e:
        error_type = type(e).__name__
        error_detail = str(e)[:400]
        errored += 1
        try: pg_conn.rollback()
        except Exception: pass

    status = "completed" if error_type is None else "failed"
    detail = {"per_tenant": per_tenant, "dry_run": dry_run}
    _log_complete(pg_conn, row_id, scanned, acted, errored, detail,
                  status=status, error_type=error_type, error_detail=error_detail)
    return {"work_type": "overdue_followups", "scanned": scanned,
            "acted_on": acted, "errored": errored, "detail": detail}


def _table_exists(cur, name: str) -> bool:
    cur.execute("SELECT to_regclass(%s) IS NOT NULL", (name,))
    return bool(cur.fetchone()[0])


# Dedup window: don't fire another freshness_expiry notification for
# the same (tenant, control) if one is already unread/undismissed
# within this many days. Prevents the sweep from spamming the
# tenant every 30 minutes for the same stale evidence.
_FRESHNESS_DEDUP_DAYS = 7


def _get_freshness_days_per_control(neo_driver, control_ids: list[str]) -> dict[str, int]:
    """Return {control_id: min freshness_days across its leaves}.

    Traverses SATISFIED_BY → REQUIRES_EVIDENCE to reach the leaf
    EvidenceRequirement nodes and picks the tightest (smallest)
    freshness_days across all leaves of the control. Controls whose
    leaves don't carry `freshness_days` are absent from the result.
    """
    if not control_ids:
        return {}
    with neo_driver.session() as s:
        result = s.run("""
            UNWIND $ids AS cid
            MATCH (rn:RequirementNode {id: cid})-[:SATISFIED_BY]->(fs:FulfilmentSpec)
            OPTIONAL MATCH (fs)-[:REQUIRES_EVIDENCE]->(er:EvidenceRequirement)
            WHERE er.freshness_days IS NOT NULL
            WITH cid, min(er.freshness_days) AS tightest
            WHERE tightest IS NOT NULL
            RETURN cid, tightest
        """, ids=control_ids)
        return {r["cid"]: int(r["tightest"]) for r in result}


def sweep_freshness_expiry(pg_conn, tick_id: str, dry_run: bool = False) -> dict:
    """Per-tenant sweep: find Comply postures past their leaves'
    freshness_days window and emit a tenant_notification per stale
    control.

    Dedup: skip if an unread/undismissed freshness_expiry notification
    for the same (tenant, control_ref) exists within the last
    _FRESHNESS_DEDUP_DAYS.

    Severity ladder:
      staleness_ratio = (now - last_updated) / freshness_days
      1.0 - 1.5x  →  medium
      1.5 - 2.0x  →  high
      > 2.0x      →  critical
    """
    row_id = _log_start(pg_conn, tick_id, "freshness_expiry")
    scanned    = 0
    acted      = 0
    errored    = 0
    per_tenant: dict[str, dict] = {}
    error_type = error_detail = None

    try:
        # Fetch Comply postures across all tenants.
        # NOTE: we don't JOIN tenants here — under arioncomply_app RLS
        # the tenants table is tenant-scoped (0 rows visible without
        # `app.tenant_id` set) so a JOIN would filter every row.
        # posture_controls has a permissive `app_posture_all` policy
        # that lets arioncomply_app see all rows for maintenance work.
        with pg_conn.cursor() as cur:
            cur.execute("""
                SELECT pc.tenant_id::text,
                       pc.node_id,
                       pc.control_ref,
                       pc.standard_id,
                       pc.last_updated
                  FROM posture_controls pc
                 WHERE pc.is_active = TRUE
                   AND pc.finding = 'Comply'
                   AND pc.last_updated IS NOT NULL
                ORDER BY pc.tenant_id, pc.node_id
            """)
            rows = cur.fetchall()

        # Group by tenant so Neo4j lookups can batch.
        from collections import defaultdict
        by_tenant: dict[str, list] = defaultdict(list)
        for tid, nid, cref, std, lu in rows:
            by_tenant[tid].append((nid, cref, std, lu))
        scanned = len(rows)

        # Connect to Neo4j once for the whole sweep.
        from neo4j import GraphDatabase as _GD
        neo = _GD.driver(
            os.getenv("NEO4J_URI",       "bolt://localhost:7687"),
            auth=(os.getenv("NEO4J_USER",     "neo4j"),
                  os.getenv("NEO4J_PASSWORD", "")),
        )
        try:
            import datetime as _dt
            now = _dt.datetime.now(_dt.timezone.utc)

            for tenant_id, tenant_rows in by_tenant.items():
                control_ids  = [r[0] for r in tenant_rows]
                freshness    = _get_freshness_days_per_control(neo, control_ids)
                tenant_acted = 0
                tenant_dedup = 0
                tenant_stale = 0

                # Set tenant scope for INSERTs (RLS).
                with pg_conn.cursor() as cur:
                    cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                                (tenant_id,))
                    for nid, cref, std, lu in tenant_rows:
                        fdays = freshness.get(nid)
                        if fdays is None:
                            continue
                        # Robustness: last_updated might be naive.
                        lu_aware = lu if lu.tzinfo else lu.replace(tzinfo=_dt.timezone.utc)
                        stale_days = (now - lu_aware).total_seconds() / 86400.0
                        if stale_days <= fdays:
                            continue
                        tenant_stale += 1

                        if dry_run:
                            continue

                        # Dedup: existing unread notification for this
                        # (tenant, control) within the window?
                        cur.execute("""
                            SELECT 1 FROM tenant_notification
                             WHERE tenant_id           = %s::uuid
                               AND kind                = 'freshness_expiry'
                               AND related_control_ref = %s
                               AND read_at IS NULL AND dismissed_at IS NULL
                               AND fired_at > NOW() - make_interval(days => %s)
                             LIMIT 1
                        """, (tenant_id, cref, _FRESHNESS_DEDUP_DAYS))
                        if cur.fetchone() is not None:
                            tenant_dedup += 1
                            continue

                        # Severity ladder.
                        ratio = stale_days / fdays
                        if ratio > 2.0:
                            severity = "critical"
                        elif ratio > 1.5:
                            severity = "high"
                        else:
                            severity = "medium"

                        title = (
                            f"Evidence for {cref} has passed its "
                            f"{fdays}-day freshness window"
                        )
                        body = (
                            f"Your latest Comply evidence for {cref} is "
                            f"{int(stale_days)} days old — {int(stale_days - fdays)} "
                            f"days past the {fdays}-day freshness window "
                            f"defined for this control. Refresh the evidence "
                            f"to keep the posture auditor-ready."
                        )

                        cur.execute("""
                            INSERT INTO tenant_notification (
                                tenant_id, kind, title, body, severity,
                                related_control_ref, related_event_type
                            ) VALUES (
                                %s::uuid, 'freshness_expiry', %s, %s, %s,
                                %s, 'evidence_stale'
                            )
                        """, (tenant_id, title, body, severity, cref))
                        tenant_acted += 1

                if tenant_stale or tenant_acted or tenant_dedup:
                    per_tenant[tenant_id[:8]] = {
                        "stale":     tenant_stale,
                        "notified":  tenant_acted,
                        "deduped":   tenant_dedup,
                    }
                acted += tenant_acted
            # Commit tenant-scoped writes.
            pg_conn.commit()
        finally:
            try: neo.close()
            except Exception: pass
    except Exception as e:
        error_type = type(e).__name__
        error_detail = str(e)[:400]
        errored += 1
        try: pg_conn.rollback()
        except Exception: pass

    status = "completed" if error_type is None else "failed"
    detail = {
        "per_tenant":  per_tenant,
        "dedup_days":  _FRESHNESS_DEDUP_DAYS,
        "dry_run":     dry_run,
    }
    _log_complete(pg_conn, row_id, scanned, acted, errored, detail,
                  status=status, error_type=error_type, error_detail=error_detail)
    return {"work_type": "freshness_expiry", "scanned": scanned,
            "acted_on": acted, "errored": errored, "detail": detail}


# Dedup window for cite verification — mirror of _FRESHNESS_DEDUP_DAYS.
# Once we've told the tenant a cite is overdue, don't spam them every
# 30 min for the same source. Explicit re-verification bumps
# next_review_due forward + the row falls out of the SELECT anyway.
_CITE_VERIFICATION_DEDUP_DAYS = 7


def sweep_cite_verification_overdue(pg_conn, tick_id: str, dry_run: bool = False) -> dict:
    """Per-tenant sweep: active external_evidence_source rows whose
    next_review_due has passed without a fresh verification bumping
    last_verified_at forward.

    Auditor-critical: a cited system as evidence *without* a recent
    verification log entry is worse than stale in-product evidence.
    The tenant is claiming "Okta manages access" but hasn't confirmed
    that claim is still true.

    Severity ladder — cite verification skews harder than
    freshness_expiry because there's no artefact in-product at all
    for the sample review to fall back on:
      staleness_ratio = (now - next_review_due) / cadence_days
      never_verified (last_verified_at IS NULL AND past due)   → critical
      staleness_ratio > 1.0                                     → critical
      staleness_ratio in (0, 1.0]                              → high

    (staleness_ratio ≤ 0 means past due but by less than one cadence
    period — still auditor-critical because the promise-of-freshness
    contract is broken. High rather than critical only because there's
    time to remediate before the next audit window.)

    Dedup: skip if an unread/undismissed cite_verification_overdue
    notification for the same (tenant, source_id) exists within the
    last _CITE_VERIFICATION_DEDUP_DAYS. The partial unique index
    already handles per-source dedup; the time window is belt-and-
    braces so re-verification just outside the window still surfaces
    without re-notify.
    """
    row_id = _log_start(pg_conn, tick_id, "cite_verification_overdue")
    scanned    = 0
    acted      = 0
    errored    = 0
    per_tenant: dict[str, dict] = {}
    error_type = error_detail = None

    try:
        from collections import defaultdict

        # Cross-tenant read via arioncomply_app's permissive
        # `app_external_evidence_source_all` policy (schema_v73).
        with pg_conn.cursor() as cur:
            cur.execute("""
                SELECT tenant_id::text,
                       id::text,
                       must_id,
                       leaf_id,
                       cadence_days,
                       last_verified_at,
                       next_review_due
                  FROM external_evidence_source
                 WHERE is_active       = TRUE
                   AND next_review_due IS NOT NULL
                   AND next_review_due < NOW()
                 ORDER BY tenant_id, next_review_due
            """)
            rows = cur.fetchall()

        by_tenant: dict[str, list] = defaultdict(list)
        for r in rows:
            by_tenant[r[0]].append(r[1:])
        scanned = len(rows)

        if dry_run or not by_tenant:
            _log_complete(
                pg_conn, row_id, scanned, acted, errored,
                {"per_tenant": {}, "dry_run": dry_run,
                 "dedup_days": _CITE_VERIFICATION_DEDUP_DAYS},
                status="completed",
            )
            return {"work_type": "cite_verification_overdue",
                    "scanned": scanned, "acted_on": 0, "errored": 0,
                    "detail": {"per_tenant": {}, "dry_run": dry_run}}

        import datetime as _dt
        now = _dt.datetime.now(_dt.timezone.utc)

        for tenant_id, tenant_rows in by_tenant.items():
            tenant_acted = 0
            tenant_dedup = 0

            with pg_conn.cursor() as cur:
                cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                            (tenant_id,))
                for (src_id, must_id, leaf_id, cadence_days,
                     last_verified_at, next_review_due) in tenant_rows:

                    # Skip dedup window check.
                    cur.execute("""
                        SELECT 1 FROM tenant_notification
                         WHERE tenant_id         = %s::uuid
                           AND kind              = 'cite_verification_overdue'
                           AND related_entity_id = %s::uuid
                           AND read_at IS NULL AND dismissed_at IS NULL
                           AND fired_at > NOW() - make_interval(days => %s)
                         LIMIT 1
                    """, (tenant_id, src_id, _CITE_VERIFICATION_DEDUP_DAYS))
                    if cur.fetchone() is not None:
                        tenant_dedup += 1
                        continue

                    # Severity ladder.
                    nrd_aware = (next_review_due if next_review_due.tzinfo
                                 else next_review_due.replace(tzinfo=_dt.timezone.utc))
                    days_over = (now - nrd_aware).total_seconds() / 86400.0
                    ratio = days_over / max(cadence_days, 1)

                    if last_verified_at is None:
                        severity = "critical"
                    elif ratio > 1.0:
                        severity = "critical"
                    else:
                        severity = "high"

                    # Extract control ref from leaf_id ('req:A.5.15:policy'
                    # → 'A.5.15') for display + related_control_ref.
                    parts = leaf_id.split(":", 2)
                    control_ref = parts[1] if len(parts) >= 2 else leaf_id

                    if last_verified_at is None:
                        _hist = "never been verified"
                    else:
                        lva = (last_verified_at if last_verified_at.tzinfo
                               else last_verified_at.replace(tzinfo=_dt.timezone.utc))
                        days_since = int((now - lva).total_seconds() / 86400.0)
                        _hist = f"last verified {days_since} days ago"

                    title = (
                        f"Cited source for {control_ref} is overdue "
                        f"for verification"
                    )
                    body = (
                        f"The cited external system covering "
                        f"{must_id} ({_hist}) has passed its "
                        f"{cadence_days}-day verification cadence by "
                        f"{int(days_over)} day{'s' if int(days_over) != 1 else ''}. "
                        f"Auditors expect a fresh verification log "
                        f"entry — re-verify the cite or downgrade the "
                        f"claim."
                    )

                    from rag.cascade.notify import notify as _notify
                    result = _notify(
                        cur,
                        tenant_id           = tenant_id,
                        kind                = "cite_verification_overdue",
                        title               = title,
                        body                = body,
                        severity            = severity,
                        related_entity_kind = "external_evidence_source",
                        related_entity_id   = src_id,
                        related_control_ref = control_ref,
                        related_event_type  = "cite_verification_overdue",
                    )
                    if result is not None:
                        tenant_acted += 1

            if tenant_acted or tenant_rows or tenant_dedup:
                per_tenant[tenant_id[:8]] = {
                    "overdue":  len(tenant_rows),
                    "notified": tenant_acted,
                    "deduped":  tenant_dedup,
                }
            acted += tenant_acted

        pg_conn.commit()
    except Exception as e:
        error_type = type(e).__name__
        error_detail = str(e)[:400]
        errored += 1
        try: pg_conn.rollback()
        except Exception: pass

    status = "completed" if error_type is None else "failed"
    detail = {"per_tenant": per_tenant,
              "dedup_days": _CITE_VERIFICATION_DEDUP_DAYS,
              "dry_run":    dry_run}
    _log_complete(pg_conn, row_id, scanned, acted, errored, detail,
                  status=status, error_type=error_type, error_detail=error_detail)
    return {"work_type": "cite_verification_overdue",
            "scanned": scanned, "acted_on": acted,
            "errored": errored, "detail": detail}


# Ship 3'.i: three escalating warning windows before an API key expires.
# Buckets ranked oldest-first so the SELECT can pick the tightest one
# (a key at 3d out lands in the 7d bucket, not 30d). Bucket label goes
# into related_event_type so the partial unique index dedupes per bucket:
# tenant gets three heads-up over a key's final month, not a daily nag.
_API_KEY_WARN_BUCKETS = [
    ("1d",  1,  "critical"),
    ("7d",  7,  "high"),
    ("30d", 30, "medium"),
]


def sweep_api_key_expiring(pg_conn, tick_id: str, dry_run: bool = False) -> dict:
    """Per-tenant sweep: active API keys approaching their expires_at.

    Fires up to three escalating notifications per key:
      * 30 days out — medium severity — plan the rotation
      * 7 days out  — high severity    — schedule the rotation
      * 1 day out   — critical         — do the rotation NOW

    Each bucket dedups against the partial unique index on the
    (kind, related_entity_id, related_control_ref) tuple.
    related_control_ref carries the bucket label ('30d'/'7d'/'1d') so
    the same key can produce all three notifications in sequence
    without dedup collision, but a second sweep in the same bucket
    hits the index and is a no-op.

    Keys with `expires_at IS NULL` (never expiring) are skipped;
    keys past expiry are also skipped (post-expiry pain isn't a
    warning — the key is dead).

    Uses api_keys' existing `app_all_api_keys` permissive policy for
    cross-tenant read.
    """
    row_id = _log_start(pg_conn, tick_id, "api_key_expiring")
    scanned    = 0
    acted      = 0
    errored    = 0
    per_tenant: dict[str, dict] = {}
    error_type = error_detail = None

    try:
        from collections import defaultdict

        # Bucket the key by TIGHTEST window it falls into. Postgres
        # calculates the days remaining once; we CASE-WHEN pick the
        # bucket label. Excludes already-expired keys.
        with pg_conn.cursor() as cur:
            cur.execute("""
                SELECT tenant_id::text,
                       id::text,
                       name,
                       key_prefix,
                       expires_at,
                       EXTRACT(EPOCH FROM (expires_at - NOW())) / 86400.0 AS days_remaining,
                       CASE
                         WHEN expires_at <= NOW() + interval '1 day'   THEN '1d'
                         WHEN expires_at <= NOW() + interval '7 days'  THEN '7d'
                         WHEN expires_at <= NOW() + interval '30 days' THEN '30d'
                         ELSE NULL
                       END AS bucket
                  FROM api_keys
                 WHERE is_active  = TRUE
                   AND expires_at IS NOT NULL
                   AND expires_at > NOW()
                   AND expires_at <= NOW() + interval '30 days'
                 ORDER BY tenant_id, expires_at
            """)
            rows = cur.fetchall()

        by_tenant: dict[str, list] = defaultdict(list)
        for r in rows:
            by_tenant[r[0]].append(r[1:])
        scanned = len(rows)

        # Severity map for lookup by bucket label
        _sev_by_bucket = {b: s for (b, _, s) in _API_KEY_WARN_BUCKETS}

        if dry_run or not by_tenant:
            _log_complete(
                pg_conn, row_id, scanned, acted, errored,
                {"per_tenant": {}, "dry_run": dry_run,
                 "buckets": [b for (b, _, _) in _API_KEY_WARN_BUCKETS]},
                status="completed",
            )
            return {"work_type": "api_key_expiring",
                    "scanned": scanned, "acted_on": 0, "errored": 0,
                    "detail": {"per_tenant": {}, "dry_run": dry_run}}

        from rag.cascade.notify import notify as _notify

        for tenant_id, tenant_rows in by_tenant.items():
            tenant_acted = 0
            with pg_conn.cursor() as cur:
                cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                            (tenant_id,))
                for (key_id, name, key_prefix, expires_at,
                     days_remaining, bucket) in tenant_rows:
                    if bucket is None:
                        continue
                    days_left = max(int(days_remaining or 0), 0)
                    severity  = _sev_by_bucket.get(bucket, "medium")

                    title = (
                        f"API key '{name}' expires in {days_left} "
                        f"day{'s' if days_left != 1 else ''}"
                    )
                    body = (
                        f"API key '{name}' (prefix {key_prefix}...) "
                        f"is set to expire on "
                        f"{expires_at.strftime('%Y-%m-%d')}. "
                        f"Rotate it in the Profile page — any client "
                        f"still using the old key will start failing "
                        f"once it expires."
                    )
                    result = _notify(
                        cur,
                        tenant_id           = tenant_id,
                        kind                = "api_key_expiring",
                        title               = title,
                        body                = body,
                        severity            = severity,
                        related_entity_kind = "api_key",
                        related_entity_id   = key_id,
                        related_control_ref = bucket,
                        related_event_type  = "api_key_expiring",
                    )
                    if result is not None:
                        tenant_acted += 1

            if tenant_acted or tenant_rows:
                per_tenant[tenant_id[:8]] = {
                    "at_risk":  len(tenant_rows),
                    "notified": tenant_acted,
                }
            acted += tenant_acted

        pg_conn.commit()
    except Exception as e:
        error_type = type(e).__name__
        error_detail = str(e)[:400]
        errored += 1
        try: pg_conn.rollback()
        except Exception: pass

    status = "completed" if error_type is None else "failed"
    detail = {"per_tenant": per_tenant,
              "buckets":    [b for (b, _, _) in _API_KEY_WARN_BUCKETS],
              "dry_run":    dry_run}
    _log_complete(pg_conn, row_id, scanned, acted, errored, detail,
                  status=status, error_type=error_type, error_detail=error_detail)
    return {"work_type": "api_key_expiring",
            "scanned": scanned, "acted_on": acted,
            "errored": errored, "detail": detail}


# Ship 3'.k: notification retention thresholds. Fired-agnostic
# (measured against tenant_notification.fired_at). Conservative
# defaults — favour keeping data over deleting it.
_RETENTION_DISMISSED_DAYS = 30    # tenant explicitly said "go away"
_RETENTION_READ_DAYS      = 90    # tenant saw + acknowledged
_RETENTION_MAX_AGE_DAYS   = 365   # hard ceiling — even unread
_RETENTION_ATTEMPT_DAYS   = 90    # delivery-attempt log age


def sweep_notification_retention(pg_conn, tick_id: str, dry_run: bool = False) -> dict:
    """Hard-delete stale tenant_notification + notification_delivery_
    attempt rows per the retention rules above.

    Deletion rules (union):
      (a) dismissed_at IS NOT NULL AND fired_at < NOW - _RETENTION_DISMISSED_DAYS
      (b) read_at      IS NOT NULL AND fired_at < NOW - _RETENTION_READ_DAYS
      (c) fired_at < NOW - _RETENTION_MAX_AGE_DAYS
                                 (regardless of read/dismissed state)

    Rule (a) uses a shorter window because the tenant explicitly
    said "get rid of this" via dismissal. Rule (b) keeps read-but-not-
    dismissed notifications around longer as an in-app history until
    the 90-day mark. Rule (c) is the hard ceiling: after a year,
    everything ages out regardless of whether it was ever read.

    Attempts (notification_delivery_attempt) age out on their own
    schedule via _RETENTION_ATTEMPT_DAYS keyed on attempted_at.
    Attempts pointing at now-deleted notifications become orphan
    rows (no FK enforcement) — they age out on the same
    _RETENTION_ATTEMPT_DAYS clock, so orphans self-clean.

    No FK cascade from tenant_notification → notification_delivery_
    attempt: attempts hold notification_id but no FK constraint, by
    design (delivery is a separate audit stream). Cleanup is
    orthogonal.

    Cross-tenant SELECT via arioncomply_app's app_notification_all +
    app_delivery_attempt_all policies (schema_v70). DELETE uses the
    grants added in schema_v75.
    """
    row_id = _log_start(pg_conn, tick_id, "notification_retention")
    scanned    = 0
    acted      = 0
    errored    = 0
    per_tenant: dict[str, dict] = {}
    error_type = error_detail = None

    try:
        if dry_run:
            # Just count what WOULD be deleted, don't touch anything.
            with pg_conn.cursor() as cur:
                cur.execute("""
                    SELECT count(*) FROM tenant_notification
                     WHERE (dismissed_at IS NOT NULL
                            AND fired_at < NOW() - make_interval(days => %s))
                        OR (read_at      IS NOT NULL
                            AND fired_at < NOW() - make_interval(days => %s))
                        OR fired_at < NOW() - make_interval(days => %s)
                """, (_RETENTION_DISMISSED_DAYS,
                      _RETENTION_READ_DAYS,
                      _RETENTION_MAX_AGE_DAYS))
                notif_would_delete = cur.fetchone()[0] or 0
                cur.execute("""
                    SELECT count(*) FROM notification_delivery_attempt
                     WHERE attempted_at < NOW() - make_interval(days => %s)
                """, (_RETENTION_ATTEMPT_DAYS,))
                attempt_would_delete = cur.fetchone()[0] or 0
            scanned = notif_would_delete + attempt_would_delete
            _log_complete(
                pg_conn, row_id, scanned, acted, errored,
                {"would_delete_notifications": notif_would_delete,
                 "would_delete_attempts":      attempt_would_delete,
                 "dry_run":                    True,
                 "thresholds": {
                     "dismissed_days": _RETENTION_DISMISSED_DAYS,
                     "read_days":      _RETENTION_READ_DAYS,
                     "max_age_days":   _RETENTION_MAX_AGE_DAYS,
                     "attempt_days":   _RETENTION_ATTEMPT_DAYS,
                 }},
                status="completed",
            )
            return {"work_type": "notification_retention",
                    "scanned": scanned, "acted_on": 0, "errored": 0,
                    "detail": {"would_delete_notifications": notif_would_delete,
                               "would_delete_attempts":      attempt_would_delete,
                               "dry_run": True}}

        # Real run — DELETE with RETURNING so we can bucket per-tenant.
        # Attempts first because a notification-side DELETE might
        # deprive an attempt row of context (though there's no FK
        # enforcement, keeping the order clean helps auditors read
        # the sweep_log entry chronologically).
        with pg_conn.cursor() as cur:
            cur.execute("""
                DELETE FROM notification_delivery_attempt
                 WHERE attempted_at < NOW() - make_interval(days => %s)
                RETURNING tenant_id::text
            """, (_RETENTION_ATTEMPT_DAYS,))
            attempt_deleted = cur.fetchall()

            cur.execute("""
                DELETE FROM tenant_notification
                 WHERE (dismissed_at IS NOT NULL
                        AND fired_at < NOW() - make_interval(days => %s))
                    OR (read_at      IS NOT NULL
                        AND fired_at < NOW() - make_interval(days => %s))
                    OR fired_at < NOW() - make_interval(days => %s)
                RETURNING tenant_id::text
            """, (_RETENTION_DISMISSED_DAYS,
                  _RETENTION_READ_DAYS,
                  _RETENTION_MAX_AGE_DAYS))
            notif_deleted = cur.fetchall()

        # Bucket by tenant
        from collections import defaultdict
        counts: dict[str, dict[str, int]] = defaultdict(lambda: {"n": 0, "a": 0})
        for (tid,) in notif_deleted:
            counts[tid]["n"] += 1
        for (tid,) in attempt_deleted:
            counts[tid]["a"] += 1
        for tid, c in counts.items():
            per_tenant[tid[:8]] = {
                "notifications_deleted": c["n"],
                "attempts_deleted":      c["a"],
            }

        scanned = len(notif_deleted) + len(attempt_deleted)
        acted   = scanned
        pg_conn.commit()
    except Exception as e:
        error_type = type(e).__name__
        error_detail = str(e)[:400]
        errored += 1
        try: pg_conn.rollback()
        except Exception: pass

    status = "completed" if error_type is None else "failed"
    detail = {"per_tenant": per_tenant,
              "thresholds": {
                  "dismissed_days": _RETENTION_DISMISSED_DAYS,
                  "read_days":      _RETENTION_READ_DAYS,
                  "max_age_days":   _RETENTION_MAX_AGE_DAYS,
                  "attempt_days":   _RETENTION_ATTEMPT_DAYS,
              },
              "dry_run": dry_run}
    _log_complete(pg_conn, row_id, scanned, acted, errored, detail,
                  status=status, error_type=error_type, error_detail=error_detail)
    return {"work_type": "notification_retention",
            "scanned": scanned, "acted_on": acted,
            "errored": errored, "detail": detail}


# ── Public tick runner ───────────────────────────────────────────────

def sweep_notification_delivery(pg_conn, tick_id: str, dry_run: bool = False) -> dict:
    """Outbound notification delivery. Reads undelivered
    tenant_notification × tenant_notification_channel rows,
    delivers per channel_kind, records attempts. Silent-fail per
    (notification, channel).

    Config: SMTP env vars for email channel; Slack webhook URLs
    live in tenant_notification_channel.endpoint. Channels with
    min_severity gate low-severity notifications out.
    """
    row_id = _log_start(pg_conn, tick_id, "notification_delivery")
    scanned = 0
    acted   = 0
    errored = 0
    detail: dict = {}
    error_type = error_detail = None
    try:
        from rag.notifications.deliver import deliver_all
        result = deliver_all(pg_conn, dry_run=dry_run)
        scanned = result.get("notifications_scanned", 0)
        acted   = result.get("delivered", 0)
        errored = result.get("errored", 0)
        detail  = {
            "notifications_scanned": scanned,
            "delivered":             acted,
            "skipped":               result.get("skipped", 0),
            "errored":               errored,
            "dry_run":               dry_run,
        }
    except Exception as e:
        error_type   = type(e).__name__
        error_detail = str(e)[:400]
        try:
            pg_conn.rollback()
        except Exception:
            pass
    status = "completed" if error_type is None else "failed"
    _log_complete(pg_conn, row_id, scanned, acted, errored, detail,
                  status=status, error_type=error_type, error_detail=error_detail)
    return {"work_type": "notification_delivery", "scanned": scanned,
            "acted_on": acted, "errored": errored, "detail": detail}


_WORK_TYPES = {
    "fact_recompute":              sweep_fact_recompute,
    "overdue_followups":           sweep_overdue_followups,
    "freshness_expiry":            sweep_freshness_expiry,
    "cite_verification_overdue":   sweep_cite_verification_overdue,
    "api_key_expiring":            sweep_api_key_expiring,
    "notification_delivery":       sweep_notification_delivery,
    "notification_retention":      sweep_notification_retention,
}


def run_tick(work_types: Optional[list[str]] = None, dry_run: bool = False) -> dict:
    """Run one tick — one or more work types.

    Returns a summary dict for stdout logging.
    """
    tick_id   = str(uuid.uuid4())
    started   = time.time()
    to_run    = work_types or list(_WORK_TYPES.keys())
    results: list[dict] = []
    pg_conn = _connect()
    try:
        for w in to_run:
            fn = _WORK_TYPES.get(w)
            if fn is None:
                logger.warning("Unknown work_type: %s", w)
                continue
            try:
                results.append(fn(pg_conn, tick_id, dry_run=dry_run))
            except Exception as e:
                logger.error("work_type %s crashed: %s", w, e)
                results.append({"work_type": w, "error": str(e)[:400]})
    finally:
        pg_conn.close()

    elapsed = int((time.time() - started) * 1000)
    return {
        "tick_id":     tick_id,
        "elapsed_ms":  elapsed,
        "dry_run":     dry_run,
        "results":     results,
    }


def _main():
    parser = argparse.ArgumentParser(description="ArionComply sweep tick")
    parser.add_argument("--work",  action="append",
                        choices=list(_WORK_TYPES.keys()),
                        help="Specific work types (default: all)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Log intent but do not write client_facts")
    parser.add_argument("--json", action="store_true",
                        help="Emit machine-readable JSON summary to stdout")
    args = parser.parse_args()

    logging.basicConfig(
        level  = logging.INFO,
        format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    summary = run_tick(args.work, args.dry_run)
    if args.json:
        print(json.dumps(summary, default=str))
    else:
        print(f"tick {summary['tick_id']} completed in {summary['elapsed_ms']}ms")
        for r in summary["results"]:
            print(f"  {r.get('work_type','?')}: "
                  f"scanned={r.get('scanned','?')} "
                  f"acted={r.get('acted_on','?')} "
                  f"errored={r.get('errored','?')}")
    # Exit code — non-zero if any work type failed
    any_err = any(r.get("errored", 0) or r.get("error") for r in summary["results"])
    sys.exit(1 if any_err else 0)


if __name__ == "__main__":
    _main()
