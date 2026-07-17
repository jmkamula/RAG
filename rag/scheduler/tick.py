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

Work types (MVP):

  fact_recompute — for each fact in fact_source_config, for each tenant
    whose last recompute is older than refresh_days, call
    rag.facts.recompute.recompute_client_fact. Batched per fact —
    all tenants for one fact in one loop, so a slow config doesn't
    stall the batch.

  overdue_followups (stub) — placeholder for cascade events past
    followup_due_at. Currently logs the count; delivery hooks land
    when the notification arc ships.

  freshness_expiry (stub) — placeholder for posture rows past
    freshness_days. Currently logs the count.

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
    """Stub — count cascade events past followup_due_at, log for now.
    Actual notification delivery hooks land with the notification arc."""
    row_id = _log_start(pg_conn, tick_id, "overdue_followups")
    scanned = acted = errored = 0
    detail: dict = {"note": "stub — counting only, no delivery yet"}
    error_type = error_detail = None
    try:
        # Only count if the table exists (defensive for envs without cascade)
        with pg_conn.cursor() as cur:
            cur.execute("""
                SELECT to_regclass('cascade_events') IS NOT NULL
            """)
            if cur.fetchone()[0]:
                cur.execute("""
                    SELECT count(*) FROM cascade_events
                     WHERE followup_due_at IS NOT NULL
                       AND followup_due_at < NOW()
                       AND (acknowledged_at IS NULL OR acknowledged_at = 'epoch'::timestamptz)
                """)
                scanned = int(cur.fetchone()[0] or 0)
                detail["overdue_count"] = scanned
    except Exception as e:
        error_type = type(e).__name__
        error_detail = str(e)[:400]
    status = "completed" if error_type is None else "failed"
    _log_complete(pg_conn, row_id, scanned, acted, errored, detail,
                  status=status, error_type=error_type, error_detail=error_detail)
    return {"work_type": "overdue_followups", "scanned": scanned,
            "acted_on": acted, "errored": errored, "detail": detail}


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
    "fact_recompute":         sweep_fact_recompute,
    "overdue_followups":      sweep_overdue_followups,
    "freshness_expiry":       sweep_freshness_expiry,
    "notification_delivery":  sweep_notification_delivery,
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
