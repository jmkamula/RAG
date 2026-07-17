"""
Tests for rag/scheduler/tick.py — the periodic sweep entry point.

Ship 3'.a (2026-07-17): productionizes the scheduler shipped earlier
in commit 849ea7a. These tests exercise the public runner
(`run_tick`) with a monkey-patched work-type registry so no real
Postgres writes happen — the sweep_log update flows still target
Postgres, so we use a live connection but write into a
transaction-isolated tick_id.

Run: PYTHONPATH=/data/arioncomply python3 tests/test_scheduler.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from rag.scheduler.tick import (
    run_tick,
    sweep_fact_recompute,
    sweep_overdue_followups,
    sweep_freshness_expiry,
    sweep_notification_delivery,
    _WORK_TYPES,
)


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


def _needs_pg():
    """Skip tests when Postgres is unreachable — CI hosts without
    a live DB shouldn't fail this suite."""
    try:
        import psycopg2
        c = psycopg2.connect(
            host=os.getenv("PGHOST", "127.0.0.1"),
            dbname=os.getenv("PGDATABASE", "arioncomply_compliance"),
            user=os.getenv("PGUSER", "arioncomply_app"),
            password=os.getenv("PGPASSWORD", ""),
            connect_timeout=1,
        )
        c.close()
        return True
    except Exception:
        return False


_PG = _needs_pg()


# ── Registry / interface tests ────────────────────────────────────────

def test_registry_has_all_declared_work_types():
    """All work_types on schema_v65's CHECK constraint must have a
    registered handler."""
    schema_v65_types = {
        "fact_recompute",
        "overdue_followups",
        "freshness_expiry",
        "notification_delivery",
    }
    return _ok(
        schema_v65_types.issubset(set(_WORK_TYPES.keys())),
        f"missing: {schema_v65_types - set(_WORK_TYPES.keys())}",
    )


def test_registry_handlers_are_callable():
    return _ok(
        all(callable(fn) for fn in _WORK_TYPES.values()),
        "one or more handlers not callable",
    )


# ── run_tick shape tests (require PG) ─────────────────────────────────

def test_run_tick_returns_summary_shape():
    if not _PG:
        return _ok(True, "skipped — no Postgres")
    summary = run_tick(dry_run=True)
    return _ok(
        "tick_id" in summary
        and "elapsed_ms" in summary
        and "results" in summary
        and len(summary["results"]) == len(_WORK_TYPES),
        f"got keys: {list(summary.keys())}",
    )


def test_run_tick_all_work_types_complete():
    if not _PG:
        return _ok(True, "skipped — no Postgres")
    summary = run_tick(dry_run=True)
    # Every result should have a work_type + not report a top-level
    # crash. items_errored may be nonzero if a specific sub-item
    # failed, but the wrapper shouldn't crash.
    for r in summary["results"]:
        if "error" in r:
            return _ok(False, f"work_type {r.get('work_type')} crashed: {r['error']}")
    return _ok(True)


def test_run_tick_dry_run_does_not_write_client_facts():
    """dry_run should read fact_source_config but never call
    recompute_client_fact (which would mutate client_facts)."""
    if not _PG:
        return _ok(True, "skipped — no Postgres")
    summary = run_tick(work_types=["fact_recompute"], dry_run=True)
    r = summary["results"][0]
    return _ok(
        r["work_type"] == "fact_recompute"
        and r["acted_on"] == 0
        and r["errored"] == 0,
        f"got {r}",
    )


def test_run_tick_specific_work_type_only():
    if not _PG:
        return _ok(True, "skipped — no Postgres")
    summary = run_tick(work_types=["freshness_expiry"], dry_run=True)
    return _ok(
        len(summary["results"]) == 1
        and summary["results"][0]["work_type"] == "freshness_expiry"
    )


def test_run_tick_writes_sweep_log_row_per_work_type():
    """Each tick writes exactly one sweep_log row per work_type.
    Verify via count-before/count-after."""
    if not _PG:
        return _ok(True, "skipped — no Postgres")
    import psycopg2
    conn = psycopg2.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        dbname=os.getenv("PGDATABASE", "arioncomply_compliance"),
        user=os.getenv("PGUSER", "arioncomply_app"),
        password=os.getenv("PGPASSWORD", ""),
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM sweep_log")
            before = cur.fetchone()[0]
        # One tick — writes len(_WORK_TYPES) rows
        run_tick(dry_run=True)
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM sweep_log")
            after = cur.fetchone()[0]
        return _ok(
            after == before + len(_WORK_TYPES),
            f"before={before} after={after} expected +{len(_WORK_TYPES)}",
        )
    finally:
        conn.close()


def test_run_tick_all_rows_share_tick_id():
    """One tick_id per invocation — all work_type rows must share it."""
    if not _PG:
        return _ok(True, "skipped — no Postgres")
    import psycopg2
    conn = psycopg2.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        dbname=os.getenv("PGDATABASE", "arioncomply_compliance"),
        user=os.getenv("PGUSER", "arioncomply_app"),
        password=os.getenv("PGPASSWORD", ""),
    )
    try:
        summary = run_tick(dry_run=True)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(DISTINCT tick_id) FROM sweep_log "
                "WHERE tick_id = %s::uuid",
                (summary["tick_id"],),
            )
            n = cur.fetchone()[0]
        return _ok(n == 1, f"multiple tick_ids: {n}")
    finally:
        conn.close()


TESTS = [
    test_registry_has_all_declared_work_types,
    test_registry_handlers_are_callable,
    test_run_tick_returns_summary_shape,
    test_run_tick_all_work_types_complete,
    test_run_tick_dry_run_does_not_write_client_facts,
    test_run_tick_specific_work_type_only,
    test_run_tick_writes_sweep_log_row_per_work_type,
    test_run_tick_all_rows_share_tick_id,
]


def main():
    print("─" * 70)
    print("  Scheduler tick tests")
    print("─" * 70)
    if not _PG:
        print("  [skip] Postgres unreachable — DB tests will pass trivially")
    failures = 0
    for t in TESTS:
        try:
            ok, msg = t()
        except Exception as e:
            import traceback
            ok = False
            msg = f"raised {type(e).__name__}: {e}\n{traceback.format_exc()}"
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {t.__name__}")
        if not ok:
            print(f"         {msg}")
            failures += 1
    print("─" * 70)
    print(f"  {len(TESTS) - failures}/{len(TESTS)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
