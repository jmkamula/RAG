"""
Integration tests for the notification delivery worker (Ship 3'.j).

Exercises `rag.notifications.deliver.deliver_all` end-to-end
against a real Postgres DB with:
  - a throwaway test tenant (auto-cleaned on teardown)
  - real channels + notifications + delivery_attempt rows
  - monkey-patched smtplib.SMTP + urllib.request.urlopen so no
    actual network calls happen

What we cover:
  - email + slack happy paths
  - severity gate (medium notification skipped by a `high` channel)
  - dedup (successful delivery, re-run, no new attempt)
  - retry-on-failure (SMTP raises, error logged, then fix + rerun
    → success)
  - dry_run (no attempts written)
  - give-up boundary (notifications older than _GIVE_UP_DAYS are
    filtered by _undelivered_notifications and never re-attempted)

Run:
    PYTHONPATH=/data/arioncomply python3 tests/test_notification_delivery.py
"""
from __future__ import annotations

import os
import sys
import uuid
from contextlib import contextmanager
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

import psycopg2  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

load_dotenv(_ROOT / ".env")


# ── Test fixture (throwaway tenant + channels + notifications) ────────

TEST_TENANT_ID  = "99999999-9999-9999-9999-999999999999"
TEST_USER_ID    = "99999999-9999-9999-9999-999999999988"
TEST_TENANT_NAME = "ArionComply Delivery-Test Tenant"


def _db_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL not set — needed for delivery integration test")
    return url


def _connect():
    return psycopg2.connect(_db_url())


@contextmanager
def _test_state():
    """Seed a throwaway tenant + one email channel + one slack channel
    + one notification. Yields the connection + a dict of the seeded
    ids. Cleans up all seeded rows on exit."""
    conn = _connect()
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            # Tenant (idempotent — reused if a prior run leaked)
            cur.execute("""
                INSERT INTO tenants (id, name, slug, is_active)
                VALUES (%s::uuid, %s, %s, TRUE)
                ON CONFLICT (id) DO NOTHING
            """, (TEST_TENANT_ID, TEST_TENANT_NAME,
                  "delivery-test-tenant"))

            # Channels: one email (min medium), one slack (min high)
            cur.execute("""
                INSERT INTO tenant_notification_channel
                    (tenant_id, channel_kind, endpoint, min_severity, is_active)
                VALUES
                    (%s::uuid, 'email', 'ops@example.test',       'medium', TRUE),
                    (%s::uuid, 'slack', 'https://slack.test/hook','high',   TRUE)
                RETURNING id::text, channel_kind
            """, (TEST_TENANT_ID, TEST_TENANT_ID))
            channels = {r[1]: r[0] for r in cur.fetchall()}

            # One medium-severity notification (should reach email,
            # skip slack via severity gate)
            cur.execute("""
                INSERT INTO tenant_notification
                    (tenant_id, kind, title, body, severity)
                VALUES (%s::uuid, 'freshness_expiry',
                        'Delivery-test notification',
                        'body of the test notification',
                        'medium')
                RETURNING id::text
            """, (TEST_TENANT_ID,))
            notif_id = cur.fetchone()[0]

        conn.commit()
        yield conn, {"notif_id": notif_id, "channels": channels}
    finally:
        # Cleanup — cascade-delete attempts + notifications + channels
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                            (TEST_TENANT_ID,))
                cur.execute("DELETE FROM notification_delivery_attempt "
                            "WHERE tenant_id=%s::uuid", (TEST_TENANT_ID,))
                cur.execute("DELETE FROM tenant_notification "
                            "WHERE tenant_id=%s::uuid", (TEST_TENANT_ID,))
                cur.execute("DELETE FROM tenant_notification_channel "
                            "WHERE tenant_id=%s::uuid", (TEST_TENANT_ID,))
                cur.execute("DELETE FROM tenants "
                            "WHERE id=%s::uuid", (TEST_TENANT_ID,))
            conn.commit()
        except Exception:
            conn.rollback()
        finally:
            conn.close()


# ── Monkey-patch harness ──────────────────────────────────────────────

class _SmtpCapture:
    """Stand-in for smtplib.SMTP — records sendmail() calls, no I/O."""
    sent: list[dict] = []
    should_raise: Exception | None = None

    def __init__(self, host, port, timeout=15):
        self.host = host
    def __enter__(self):     return self
    def __exit__(self, *a):  return False
    def starttls(self):      pass
    def login(self, u, p):   pass
    def sendmail(self, frm, to, msg):
        if _SmtpCapture.should_raise is not None:
            raise _SmtpCapture.should_raise
        _SmtpCapture.sent.append({"from": frm, "to": to, "size": len(msg)})


class _SlackResponse:
    def __init__(self, status): self.status = status
    def __enter__(self):        return self
    def __exit__(self, *a):     return False


class _SlackCapture:
    """Stand-in for urllib.request.urlopen — records POST bodies."""
    posted: list[dict] = []
    should_raise: Exception | None = None
    status: int = 200

    @classmethod
    def urlopen(cls, req, timeout=15):
        if cls.should_raise is not None:
            raise cls.should_raise
        cls.posted.append({
            "url":  req.full_url,
            "data": req.data.decode("utf-8") if req.data else "",
        })
        return _SlackResponse(cls.status)


@contextmanager
def _patched_deliver():
    """Patch smtplib + urllib inside rag.notifications.deliver."""
    import rag.notifications.deliver as _dm
    import smtplib as _smtp
    import urllib.request as _ur
    orig_smtp = _smtp.SMTP
    orig_urlopen = _ur.urlopen
    _smtp.SMTP = _SmtpCapture
    _ur.urlopen = _SlackCapture.urlopen
    # deliver.py imports at module scope — patch its bindings too
    _dm.smtplib.SMTP = _SmtpCapture
    _dm.urllib.request.urlopen = _SlackCapture.urlopen
    _SmtpCapture.sent.clear()
    _SmtpCapture.should_raise = None
    _SlackCapture.posted.clear()
    _SlackCapture.should_raise = None
    _SlackCapture.status = 200
    try:
        yield _dm
    finally:
        _smtp.SMTP = orig_smtp
        _ur.urlopen = orig_urlopen
        _dm.smtplib.SMTP = orig_smtp
        _dm.urllib.request.urlopen = orig_urlopen


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


# ── Environment prep ──────────────────────────────────────────────────
# _deliver_email raises RuntimeError if SMTP_* env vars are missing.
# Set stubs so the code reaches the sendmail() call (which is our
# _SmtpCapture).
os.environ.setdefault("SMTP_HOST",     "smtp.example.test")
os.environ.setdefault("SMTP_PORT",     "587")
os.environ.setdefault("SMTP_USER",     "test-user")
os.environ.setdefault("SMTP_PASSWORD", "test-pass")
os.environ.setdefault("SMTP_FROM",     "arion@example.test")


# ── Tests ─────────────────────────────────────────────────────────────

def test_email_happy_path():
    from rag.notifications.deliver import deliver_all
    with _test_state() as (conn, seeds):
        with _patched_deliver():
            r = deliver_all(conn)
        # Email delivered, slack skipped by severity gate
        return _ok(
            r["delivered"] == 1
            and len(_SmtpCapture.sent) == 1
            and _SmtpCapture.sent[0]["to"] == ["ops@example.test"]
            and len(_SlackCapture.posted) == 0,
            f"result={r} smtp={_SmtpCapture.sent} slack={_SlackCapture.posted}",
        )


def test_slack_happy_path_with_high_severity():
    from rag.notifications.deliver import deliver_all
    with _test_state() as (conn, seeds):
        # Upgrade the notification to 'critical' so it clears both channels
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            cur.execute("UPDATE tenant_notification SET severity='critical' "
                        "WHERE id=%s::uuid", (seeds["notif_id"],))
        conn.commit()
        with _patched_deliver():
            r = deliver_all(conn)
        return _ok(
            r["delivered"] == 2
            and len(_SmtpCapture.sent) == 1
            and len(_SlackCapture.posted) == 1
            and "slack.test" in _SlackCapture.posted[0]["url"],
            f"result={r}",
        )


def test_severity_gate_skips_below_channel_floor():
    """Slack channel has min_severity='high'. Default notification is
    'medium'. Slack should get 0 attempts recorded (not even a failure)."""
    from rag.notifications.deliver import deliver_all
    with _test_state() as (conn, seeds):
        with _patched_deliver():
            r = deliver_all(conn)
        # Check DB: only 1 attempt row (email), not 2
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            cur.execute("SELECT count(*) FROM notification_delivery_attempt "
                        "WHERE notification_id=%s::uuid", (seeds["notif_id"],))
            attempts = cur.fetchone()[0]
        return _ok(
            attempts == 1 and len(_SlackCapture.posted) == 0,
            f"attempts={attempts} slack={_SlackCapture.posted}",
        )


def test_dedup_no_reattempt_after_success():
    """After a successful delivery, re-running deliver_all shouldn't
    re-send + shouldn't write a second attempt row."""
    from rag.notifications.deliver import deliver_all
    with _test_state() as (conn, seeds):
        with _patched_deliver():
            deliver_all(conn)
            # First run: 1 send + 1 attempt row
            _SmtpCapture.sent.clear()
            # Second run should short-circuit on _already_delivered
            r2 = deliver_all(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            cur.execute("SELECT count(*) FROM notification_delivery_attempt "
                        "WHERE notification_id=%s::uuid", (seeds["notif_id"],))
            attempts = cur.fetchone()[0]
        return _ok(
            r2["delivered"] == 0
            and len(_SmtpCapture.sent) == 0
            and attempts == 1,
            f"r2={r2} sent={_SmtpCapture.sent} attempts={attempts}",
        )


def test_retry_after_failure_lands_success():
    """First run: SMTP raises → error logged, 0 delivered.
    Second run (SMTP recovered): 1 delivered."""
    from rag.notifications.deliver import deliver_all
    with _test_state() as (conn, seeds):
        with _patched_deliver():
            _SmtpCapture.should_raise = RuntimeError("test SMTP outage")
            r1 = deliver_all(conn)
            _SmtpCapture.should_raise = None
            r2 = deliver_all(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            cur.execute("""
                SELECT count(*) FILTER (WHERE delivered_at IS NOT NULL) AS ok,
                       count(*) FILTER (WHERE error_type IS NOT NULL) AS err
                  FROM notification_delivery_attempt
                 WHERE notification_id=%s::uuid
            """, (seeds["notif_id"],))
            ok_ct, err_ct = cur.fetchone()
        return _ok(
            r1["errored"] == 1 and r2["delivered"] == 1
            and ok_ct == 1 and err_ct == 1,
            f"r1={r1} r2={r2} ok={ok_ct} err={err_ct}",
        )


def test_dry_run_writes_no_attempts():
    from rag.notifications.deliver import deliver_all
    with _test_state() as (conn, seeds):
        with _patched_deliver():
            r = deliver_all(conn, dry_run=True)
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            cur.execute("SELECT count(*) FROM notification_delivery_attempt "
                        "WHERE notification_id=%s::uuid", (seeds["notif_id"],))
            attempts = cur.fetchone()[0]
        return _ok(
            attempts == 0
            and len(_SmtpCapture.sent) == 0
            and len(_SlackCapture.posted) == 0
            and r.get("dry_run") is True,
            f"attempts={attempts} r={r}",
        )


def test_give_up_boundary_filters_old_notifications():
    """Notifications older than _GIVE_UP_DAYS are excluded by the
    initial SELECT — no attempt is even considered."""
    from rag.notifications.deliver import deliver_all, _GIVE_UP_DAYS
    with _test_state() as (conn, seeds):
        # Backdate the notification past the give-up window
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            cur.execute("""
                UPDATE tenant_notification
                   SET fired_at = NOW() - make_interval(days => %s + 1)
                 WHERE id=%s::uuid
            """, (_GIVE_UP_DAYS, seeds["notif_id"]))
        conn.commit()
        with _patched_deliver():
            r = deliver_all(conn)
        return _ok(
            r["notifications_scanned"] == 0
            and r["delivered"] == 0,
            f"r={r}",
        )


TESTS = [
    test_email_happy_path,
    test_slack_happy_path_with_high_severity,
    test_severity_gate_skips_below_channel_floor,
    test_dedup_no_reattempt_after_success,
    test_retry_after_failure_lands_success,
    test_dry_run_writes_no_attempts,
    test_give_up_boundary_filters_old_notifications,
]


def main():
    print("─" * 70)
    print("  Notification delivery integration tests (Ship 3'.j)")
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
