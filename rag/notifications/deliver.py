"""
Outbound notification delivery worker — 2026-07-13.

Reads undelivered tenant_notification rows, iterates each tenant's
active tenant_notification_channel rows, delivers per channel kind,
records the attempt in notification_delivery_attempt.

Channel kinds implemented:
  email  — SMTP via smtplib (stdlib). Config keys:
             SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD,
             SMTP_FROM     (env). endpoint = comma-separated recipients.
  slack  — Webhook POST via urllib.request. endpoint = webhook URL.

Retry policy: a notification is considered delivered to a channel
when notification_delivery_attempt has a row with delivered_at set.
Failed attempts stay in the log and are retried on subsequent sweeps
UNTIL either (a) success lands, or (b) the notification is >7 days
old (give-up threshold). Backoff is implicit — the sweep cadence
controls retry frequency (default every 30 min per 3b deploy).

Severity gate: a channel with min_severity='high' only receives
notifications whose tenant_notification.severity is high or critical.
The severity_ordinal() helper compares severities as integers.
"""
from __future__ import annotations
import logging
import os
import smtplib
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger(__name__)

_SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
_GIVE_UP_DAYS   = 7   # notifications older than this stop retrying


def severity_ordinal(sev: str) -> int:
    return _SEVERITY_ORDER.get((sev or "info").lower(), 0)


@dataclass
class DeliverySummary:
    tenant_id:       str
    notification_id: str
    channel_id:      Optional[str] = None
    channel_kind:    Optional[str] = None
    endpoint:        Optional[str] = None
    delivered:       bool          = False
    error_type:      Optional[str] = None
    error_detail:    Optional[str] = None
    latency_ms:      int           = 0
    skipped_reason:  Optional[str] = None


# ── Channel implementations ─────────────────────────────────────────

def _deliver_email(endpoint: str, subject: str, body: str) -> None:
    """Send a plain-text email via SMTP.

    Env config:
      SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM

    Raises RuntimeError if SMTP is not configured — the caller
    records this as an error attempt (so we don't silently skip).
    """
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    pwd  = os.getenv("SMTP_PASSWORD")
    frm  = os.getenv("SMTP_FROM")
    if not (host and user and pwd and frm):
        raise RuntimeError("SMTP not configured (SMTP_HOST/USER/PASSWORD/FROM)")
    msg = MIMEText(body or "")
    msg["Subject"] = subject or "(no subject)"
    msg["From"]    = frm
    msg["To"]      = endpoint
    # Multiple recipients — split on comma
    to_addrs = [r.strip() for r in (endpoint or "").split(",") if r.strip()]
    with smtplib.SMTP(host, port, timeout=15) as s:
        s.starttls()
        s.login(user, pwd)
        s.sendmail(frm, to_addrs, msg.as_string())


def _deliver_slack(endpoint: str, subject: str, body: str, severity: str) -> None:
    """POST a message to a Slack incoming webhook.

    endpoint is the webhook URL (per-workspace). Formats title as
    bold header + severity emoji + body preview.
    """
    import json as _json
    emoji = {
        "critical": ":rotating_light:",
        "high":     ":warning:",
        "medium":   ":large_orange_diamond:",
        "low":      ":information_source:",
        "info":     ":page_facing_up:",
    }.get(severity, ":page_facing_up:")
    text = f"{emoji} *{subject}*\n\n{body[:1500] if body else ''}"
    req = urllib.request.Request(
        endpoint,
        data=_json.dumps({"text": text}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        if resp.status >= 300:
            raise RuntimeError(f"slack webhook returned {resp.status}")


# ── Worker ──────────────────────────────────────────────────────────

def _undelivered_notifications(pg_conn, limit: int = 200) -> list[dict]:
    """Return tenant_notification rows that haven't been fully
    delivered to all their tenant's active channels yet — i.e.
    notifications where at least one channel has no successful
    notification_delivery_attempt within _GIVE_UP_DAYS.

    Rough query — filters on fired_at recency. Actual dedup happens
    per (notification, channel) inside deliver_all().
    """
    with pg_conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, tenant_id, kind, title, body, severity,
                   related_control_ref, fired_at
              FROM tenant_notification
             WHERE fired_at > NOW() - INTERVAL '%s days'
               AND (dismissed_at IS NULL)
             ORDER BY fired_at DESC
             LIMIT %s
            """,
            (_GIVE_UP_DAYS, limit),
        )
        rows = cur.fetchall()
    return [
        {
            "id":                  str(r[0]),
            "tenant_id":           str(r[1]),
            "kind":                r[2],
            "title":               r[3],
            "body":                r[4],
            "severity":            r[5],
            "related_control_ref": r[6],
            "fired_at":            r[7],
        }
        for r in rows
    ]


def _tenant_channels(pg_conn, tenant_id: str) -> list[dict]:
    with pg_conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, channel_kind, endpoint, min_severity, config
              FROM tenant_notification_channel
             WHERE tenant_id = %s::uuid AND is_active = TRUE
             ORDER BY channel_kind
            """,
            (tenant_id,),
        )
        return [
            {"id": str(r[0]), "channel_kind": r[1], "endpoint": r[2],
             "min_severity": r[3], "config": r[4] or {}}
            for r in cur.fetchall()
        ]


def _already_delivered(pg_conn, notification_id: str, channel_id: str) -> bool:
    with pg_conn.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM notification_delivery_attempt
                 WHERE notification_id = %s::uuid
                   AND channel_id      = %s::uuid
                   AND delivered_at    IS NOT NULL
            )
            """,
            (notification_id, channel_id),
        )
        return bool(cur.fetchone()[0])


def _log_attempt(pg_conn, s: DeliverySummary) -> None:
    with pg_conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO notification_delivery_attempt (
                notification_id, tenant_id, channel_id, channel_kind, endpoint,
                delivered_at, error_type, error_detail, latency_ms
            ) VALUES (
                %s::uuid, %s::uuid, %s::uuid, %s, %s,
                CASE WHEN %s THEN NOW() ELSE NULL END,
                %s, %s, %s
            )
            """,
            (s.notification_id, s.tenant_id, s.channel_id, s.channel_kind,
             s.endpoint, s.delivered, s.error_type, s.error_detail, s.latency_ms),
        )
    pg_conn.commit()


def deliver_all(pg_conn, dry_run: bool = False) -> dict:
    """Iterate undelivered notifications × tenant channels, deliver
    when severity gate passes and no successful attempt exists yet.
    Records every attempt. Silent-fail per notification/channel.
    """
    notifications = _undelivered_notifications(pg_conn)
    scanned = 0
    delivered = 0
    skipped = 0
    errored = 0
    details: list[dict] = []

    for n in notifications:
        scanned += 1
        channels = _tenant_channels(pg_conn, n["tenant_id"])
        if not channels:
            skipped += 1
            continue
        for ch in channels:
            # Severity gate — skip if notification below channel's floor
            if severity_ordinal(n["severity"]) < severity_ordinal(ch["min_severity"]):
                continue
            # Dedup — don't re-deliver already-succeeded pair
            if _already_delivered(pg_conn, n["id"], ch["id"]):
                continue

            s = DeliverySummary(
                tenant_id       = n["tenant_id"],
                notification_id = n["id"],
                channel_id      = ch["id"],
                channel_kind    = ch["channel_kind"],
                endpoint        = ch["endpoint"],
            )
            if dry_run:
                s.skipped_reason = "dry_run"
                skipped += 1
                details.append(s.__dict__)
                continue

            t0 = time.time()
            try:
                if ch["channel_kind"] == "email":
                    _deliver_email(ch["endpoint"], n["title"], n["body"] or "")
                elif ch["channel_kind"] == "slack":
                    _deliver_slack(ch["endpoint"], n["title"], n["body"] or "",
                                    n["severity"])
                else:
                    raise RuntimeError(f"unsupported channel kind: {ch['channel_kind']}")
                s.delivered = True
                delivered += 1
            except Exception as e:
                s.error_type   = type(e).__name__
                s.error_detail = str(e)[:400]
                errored += 1

            s.latency_ms = int((time.time() - t0) * 1000)
            _log_attempt(pg_conn, s)
            details.append({
                "notification_id": s.notification_id,
                "channel_kind":    s.channel_kind,
                "delivered":       s.delivered,
                "latency_ms":      s.latency_ms,
                "error_type":      s.error_type,
            })

    return {
        "notifications_scanned": scanned,
        "delivered":             delivered,
        "skipped":               skipped,
        "errored":               errored,
        "attempts":              details,
        "dry_run":               dry_run,
    }
