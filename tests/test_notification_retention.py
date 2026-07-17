"""
Integration tests for the notification retention sweep (Ship 3'.k).

Exercises `rag.scheduler.tick.sweep_notification_retention` against
a real Postgres DB. Uses a throwaway test tenant so the eval-covered
Arion tenant is never touched.

Test coverage:
  - Rule (a): dismissed_at IS NOT NULL AND fired_at < NOW - _RETENTION_DISMISSED_DAYS → delete
  - Rule (b): read_at      IS NOT NULL AND fired_at < NOW - _RETENTION_READ_DAYS → delete
  - Rule (c): fired_at < NOW - _RETENTION_MAX_AGE_DAYS → delete (regardless of state)
  - Keep: unread + not-dismissed + within max_age → survive
  - Attempts: attempted_at < NOW - _RETENTION_ATTEMPT_DAYS → delete
  - dry_run: no rows deleted, count-only report

Run:
    PYTHONPATH=/data/arioncomply python3 tests/test_notification_retention.py
"""
from __future__ import annotations

import os
import sys
import uuid
from contextlib import contextmanager
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

import psycopg2
from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")


TEST_TENANT_ID   = "88888888-8888-8888-8888-888888888888"
TEST_TENANT_NAME = "ArionComply Retention-Test Tenant"


def _db_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL not set")
    return url


def _connect():
    return psycopg2.connect(_db_url())


@contextmanager
def _test_state():
    """Seed a throwaway tenant + one channel (for attempt rows) +
    various-aged notifications. Cleans up on exit."""
    conn = _connect()
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            cur.execute("""
                INSERT INTO tenants (id, name, slug, is_active)
                VALUES (%s::uuid, %s, %s, TRUE)
                ON CONFLICT (id) DO NOTHING
            """, (TEST_TENANT_ID, TEST_TENANT_NAME, "retention-test-tenant"))

            cur.execute("""
                INSERT INTO tenant_notification_channel
                    (tenant_id, channel_kind, endpoint, min_severity, is_active)
                VALUES (%s::uuid, 'email', 'ops@example.test', 'medium', TRUE)
                RETURNING id::text
            """, (TEST_TENANT_ID,))
            channel_id = cur.fetchone()[0]

            # Insert 5 notifications spanning the rules:
            #  (a) dismissed 35d ago
            #  (b) read 95d ago (not dismissed)
            #  (c) unread 400d ago (max_age ceiling)
            #   -  unread 200d ago (should KEEP — below ceiling, not read/dismissed)
            #   -  read 5d ago (should KEEP — read but well within read window)
            cur.execute("""
                INSERT INTO tenant_notification (tenant_id, kind, title, body, severity,
                                                 fired_at, read_at, dismissed_at)
                VALUES
                  (%s::uuid,'freshness_expiry','a dismissed 35d','','medium',
                     NOW()-interval '35 days', NOW()-interval '32 days', NOW()-interval '32 days'),
                  (%s::uuid,'nc_surfaced',     'b read 95d',     '','high',
                     NOW()-interval '95 days', NOW()-interval '90 days', NULL),
                  (%s::uuid,'upload_failed',   'c unread 400d',  '','low',
                     NOW()-interval '400 days', NULL, NULL),
                  (%s::uuid,'upload_processed','keep unread 200d','','info',
                     NOW()-interval '200 days', NULL, NULL),
                  (%s::uuid,'stage2_proposal_ready','keep read 5d','','medium',
                     NOW()-interval '5 days', NOW()-interval '3 days', NULL)
                RETURNING id::text, title
            """, tuple([TEST_TENANT_ID] * 5))
            notifs = {row[1]: row[0] for row in cur.fetchall()}

            # 2 delivery attempts: one 100d (age out), one 10d (keep)
            cur.execute("""
                INSERT INTO notification_delivery_attempt
                    (notification_id, tenant_id, channel_id, channel_kind, endpoint,
                     attempted_at, delivered_at, latency_ms)
                VALUES
                  (%s::uuid, %s::uuid, %s::uuid, 'email', 'ops@example.test',
                     NOW()-interval '100 days', NOW()-interval '100 days', 42),
                  (%s::uuid, %s::uuid, %s::uuid, 'email', 'ops@example.test',
                     NOW()-interval '10 days',  NOW()-interval '10 days', 33)
                RETURNING id::text
            """, (notifs["keep unread 200d"], TEST_TENANT_ID, channel_id,
                  notifs["keep read 5d"],    TEST_TENANT_ID, channel_id))
            attempts = [r[0] for r in cur.fetchall()]

        conn.commit()
        yield conn, {"channel_id": channel_id, "notifs": notifs, "attempts": attempts}
    finally:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                            (TEST_TENANT_ID,))
                cur.execute("DELETE FROM notification_delivery_attempt WHERE tenant_id=%s::uuid",
                            (TEST_TENANT_ID,))
                cur.execute("DELETE FROM tenant_notification WHERE tenant_id=%s::uuid",
                            (TEST_TENANT_ID,))
                cur.execute("DELETE FROM tenant_notification_channel WHERE tenant_id=%s::uuid",
                            (TEST_TENANT_ID,))
                cur.execute("DELETE FROM tenants WHERE id=%s::uuid",
                            (TEST_TENANT_ID,))
            conn.commit()
        except Exception:
            conn.rollback()
        finally:
            conn.close()


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


def _remaining_notif_titles(conn) -> set[str]:
    with conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                    (TEST_TENANT_ID,))
        cur.execute("SELECT title FROM tenant_notification WHERE tenant_id=%s::uuid",
                    (TEST_TENANT_ID,))
        return {r[0] for r in cur.fetchall()}


def _remaining_attempt_ids(conn) -> set[str]:
    with conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                    (TEST_TENANT_ID,))
        cur.execute("SELECT id::text FROM notification_delivery_attempt WHERE tenant_id=%s::uuid",
                    (TEST_TENANT_ID,))
        return {r[0] for r in cur.fetchall()}


# ── Tests ─────────────────────────────────────────────────────────────

def test_all_three_rules_delete_correct_notifications():
    """Exercise all three delete rules + verify the two 'keep' rows
    survive."""
    from rag.scheduler.tick import sweep_notification_retention
    with _test_state() as (conn, seeds):
        r = sweep_notification_retention(conn, tick_id=str(uuid.uuid4()))
        remaining = _remaining_notif_titles(conn)
        # 3 deleted + 2 kept
        return _ok(
            r["scanned"] >= 3
            and "keep unread 200d" in remaining
            and "keep read 5d" in remaining
            and "a dismissed 35d" not in remaining
            and "b read 95d" not in remaining
            and "c unread 400d" not in remaining,
            f"result={r} remaining={remaining}",
        )


def test_dismissed_rule_uses_shorter_window():
    """A notification dismissed 20 days ago should NOT be deleted (rule
    (a) threshold is 30d). Only aged-past-30d dismissed rows delete."""
    from rag.scheduler.tick import sweep_notification_retention
    with _test_state() as (conn, seeds):
        # Add a 20-day-dismissed row (should survive)
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            cur.execute("""
                INSERT INTO tenant_notification (tenant_id, kind, title, severity,
                                                 fired_at, read_at, dismissed_at)
                VALUES (%s::uuid,'freshness_expiry','dismissed 20d','medium',
                        NOW()-interval '20 days', NOW()-interval '15 days',
                        NOW()-interval '15 days')
            """, (TEST_TENANT_ID,))
        conn.commit()
        sweep_notification_retention(conn, tick_id=str(uuid.uuid4()))
        remaining = _remaining_notif_titles(conn)
        return _ok(
            "dismissed 20d" in remaining,
            f"remaining={remaining}",
        )


def test_read_but_not_dismissed_uses_90d_window():
    """A notification read but NOT dismissed 60 days ago should
    survive (rule (b) threshold is 90d)."""
    from rag.scheduler.tick import sweep_notification_retention
    with _test_state() as (conn, seeds):
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            cur.execute("""
                INSERT INTO tenant_notification (tenant_id, kind, title, severity,
                                                 fired_at, read_at)
                VALUES (%s::uuid,'nc_surfaced','read 60d','high',
                        NOW()-interval '60 days', NOW()-interval '50 days')
            """, (TEST_TENANT_ID,))
        conn.commit()
        sweep_notification_retention(conn, tick_id=str(uuid.uuid4()))
        remaining = _remaining_notif_titles(conn)
        return _ok(
            "read 60d" in remaining,
            f"remaining={remaining}",
        )


def test_max_age_ceiling_applies_regardless_of_state():
    """A read+dismissed 400-day-old row hits BOTH (a) and (c). But
    also an UNREAD 400d row hits only (c) — the ceiling. Both must be
    deleted. The unread-400d fixture row covers this."""
    from rag.scheduler.tick import sweep_notification_retention
    with _test_state() as (conn, seeds):
        sweep_notification_retention(conn, tick_id=str(uuid.uuid4()))
        remaining = _remaining_notif_titles(conn)
        return _ok(
            "c unread 400d" not in remaining,
            f"remaining={remaining}",
        )


def test_attempt_ages_out_independently():
    """The 100d attempt row should be deleted; the 10d one should
    survive. Both attempts point at notifications the sweep KEEPS."""
    from rag.scheduler.tick import sweep_notification_retention
    with _test_state() as (conn, seeds):
        r = sweep_notification_retention(conn, tick_id=str(uuid.uuid4()))
        remaining_attempts = _remaining_attempt_ids(conn)
        # Only the 10d attempt survives (100d aged out)
        return _ok(
            len(remaining_attempts) == 1
            and r["detail"]["per_tenant"].get(TEST_TENANT_ID[:8], {}).get("attempts_deleted", 0) == 1,
            f"attempts_remaining={remaining_attempts} r={r}",
        )


def test_dry_run_deletes_nothing():
    from rag.scheduler.tick import sweep_notification_retention
    with _test_state() as (conn, seeds):
        before = _remaining_notif_titles(conn)
        r = sweep_notification_retention(conn, tick_id=str(uuid.uuid4()), dry_run=True)
        after = _remaining_notif_titles(conn)
        return _ok(
            before == after
            and r["acted_on"] == 0
            and r["detail"].get("dry_run") is True
            and r["detail"].get("would_delete_notifications", 0) >= 3,
            f"before={before} after={after} r={r}",
        )


def test_sweep_log_row_written():
    """The sweep should write a sweep_log row for the tick."""
    from rag.scheduler.tick import sweep_notification_retention
    tid = str(uuid.uuid4())
    with _test_state() as (conn, seeds):
        sweep_notification_retention(conn, tick_id=tid)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT status, items_scanned, items_acted_on
                  FROM sweep_log
                 WHERE tick_id=%s::uuid AND work_type='notification_retention'
            """, (tid,))
            row = cur.fetchone()
        return _ok(
            row is not None
            and row[0] == "completed"
            and row[1] >= 3
            and row[2] >= 3,
            f"sweep_log row={row}",
        )


TESTS = [
    test_all_three_rules_delete_correct_notifications,
    test_dismissed_rule_uses_shorter_window,
    test_read_but_not_dismissed_uses_90d_window,
    test_max_age_ceiling_applies_regardless_of_state,
    test_attempt_ages_out_independently,
    test_dry_run_deletes_nothing,
    test_sweep_log_row_written,
]


def main():
    print("─" * 70)
    print("  Notification retention integration tests (Ship 3'.k)")
    print("─" * 70)
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
