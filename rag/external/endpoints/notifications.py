"""
Notification feed endpoints — /api/external/v1/notifications[/{id}].

Ship 4'.d — external consumers (SIEM/SOAR, monitoring dashboards,
compliance-platform integrations) can poll the tenant's inbox as
a JSON feed. Read-only in this arc; marking read/dismissed can
happen via a future `external:notifications:write` scope.

Design notes:

  * `since` param on GET /notifications takes an ISO8601 timestamp
    and returns only notifications with `fired_at >= since`. This
    is the primary incremental-polling contract — external clients
    remember the highest fired_at they saw and pass it back.
    Server-side check on the `idx_tenant_notification_tenant_fired`
    btree makes this cheap.
  * `kind[]` and `severity[]` are repeatable filters (any-of
    semantics), same shape as /posture's `finding[]`.
  * `unread_only` (default false) is the "poll the badge" mode —
    external clients that only care about actionable alerts pass
    `?unread_only=true`.
  * `include_dismissed` (default false) is a rarer option —
    dismissed notifications are usually filtered out by default,
    but auditors reviewing "what did the tenant ignore?" want
    them included.
  * Summary block carries total / unread / urgent (critical+high),
    matching the internal `/api/v1/tenant/notifications` badge
    contract so partners building alternative UIs see the same
    numbers as the built-in inbox.

Auth scope: `external:notifications:read`.
"""
from __future__ import annotations

import datetime as _dt
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from rag.external.auth import external_key_with_scope

logger = logging.getLogger(__name__)

router = APIRouter()


# The full set of kinds landed in Ship 3'.a-i — used to validate the
# `kind[]` filter param. Ship 3' arc close (13 kinds total).
_ALLOWED_KINDS = (
    "implication_overdue",
    "followup_overdue",
    "threshold_crossed",
    "cascade_blocked",
    "auto_resolved",
    "freshness_expiry",
    "nc_surfaced",
    "upload_processed",
    "stage2_proposal_ready",
    "upload_failed",
    "cite_verification_overdue",
    "posture_flip_to_comply",
    "api_key_expiring",
)

_ALLOWED_SEVERITIES = ("critical", "high", "medium", "low", "info")


# ── Response models ───────────────────────────────────────────────────

class Notification(BaseModel):
    id:                    str
    kind:                  str
    title:                 str
    body:                  Optional[str] = None
    severity:              str
    fired_at:              str
    read_at:               Optional[str] = None
    dismissed_at:          Optional[str] = None
    related_entity_kind:   Optional[str] = None
    related_entity_id:     Optional[str] = None
    related_control_ref:   Optional[str] = None
    related_event_type:    Optional[str] = None


class NotificationsSummary(BaseModel):
    total:  int = Field(..., description="Matching rows across the FILTERED set (not just the page).")
    unread: int = Field(..., description="Unread across the FILTERED set.")
    urgent: int = Field(..., description="Critical/high severity + unread + not-dismissed.")


class NotificationsResponse(BaseModel):
    tenant_id:               str
    generated_at:            str
    notifications:           list[Notification]
    summary:                 NotificationsSummary
    total_before_pagination: int


# ── Helpers ───────────────────────────────────────────────────────────

def _iso_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _row_to_notification(row) -> Notification:
    (nid, kind, title, body, severity, fired_at, read_at, dismissed_at,
     rel_kind, rel_id, rel_ref, rel_evt) = row
    return Notification(
        id                   = str(nid),
        kind                 = kind,
        title                = title,
        body                 = body,
        severity             = severity,
        fired_at             = fired_at.isoformat() if fired_at else "",
        read_at              = read_at.isoformat()  if read_at  else None,
        dismissed_at         = dismissed_at.isoformat() if dismissed_at else None,
        related_entity_kind  = rel_kind,
        related_entity_id    = str(rel_id) if rel_id else None,
        related_control_ref  = rel_ref,
        related_event_type   = rel_evt,
    )


# ── GET /notifications ────────────────────────────────────────────────

@router.get("/notifications",
            response_model = NotificationsResponse,
            summary        = "Notification feed for external polling")
async def list_notifications(
    request:            Request,
    key                 = Depends(external_key_with_scope("external:notifications:read")),
    since:              Optional[str]       = Query(None, description="ISO8601 — only return notifications with `fired_at >= since`."),
    kind:               Optional[list[str]] = Query(None, description="Repeatable — filter to one or more notification kinds."),
    severity:           Optional[list[str]] = Query(None, description="Repeatable — filter to one or more severities."),
    unread_only:        bool                = Query(False, description="Only return notifications with `read_at IS NULL AND dismissed_at IS NULL`."),
    include_dismissed:  bool                = Query(False, description="Include notifications with `dismissed_at IS NOT NULL` in the result."),
    limit:              int                 = Query(200, ge=1, le=1000),
    offset:             int                 = Query(0,   ge=0),
):
    """Return the tenant's notification inbox as a paginated JSON
    feed. Suitable for incremental polling by SIEM/SOAR consumers —
    pass the highest `fired_at` seen last time back as `since`.
    """
    # Validate filter values
    if kind:
        bad = [k for k in kind if k not in _ALLOWED_KINDS]
        if bad:
            raise HTTPException(
                status_code = 400,
                detail      = f"Unknown notification kind(s): {bad}. Allowed: {list(_ALLOWED_KINDS)}",
            )
    if severity:
        bad = [s for s in severity if s not in _ALLOWED_SEVERITIES]
        if bad:
            raise HTTPException(
                status_code = 400,
                detail      = f"Unknown severity value(s): {bad}. Allowed: {list(_ALLOWED_SEVERITIES)}",
            )

    since_dt = None
    if since:
        try:
            since_dt = _dt.datetime.fromisoformat(since.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(
                status_code = 400,
                detail      = f"`since` must be ISO8601 (e.g. `2026-07-18T12:00:00Z`); got: {since!r}",
            )

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (key.tenant_id,))

            where_parts = ["tenant_id = %s::uuid"]
            params: list = [key.tenant_id]

            if since_dt is not None:
                where_parts.append("fired_at >= %s")
                params.append(since_dt)

            if kind:
                placeholders = ",".join(["%s"] * len(kind))
                where_parts.append(f"kind IN ({placeholders})")
                params.extend(kind)

            if severity:
                placeholders = ",".join(["%s"] * len(severity))
                where_parts.append(f"severity IN ({placeholders})")
                params.extend(severity)

            if unread_only:
                where_parts.append("read_at IS NULL AND dismissed_at IS NULL")
            elif not include_dismissed:
                where_parts.append("dismissed_at IS NULL")

            where_sql = " AND ".join(where_parts)

            cur.execute(
                f"SELECT COUNT(*) FROM tenant_notification WHERE {where_sql}",
                params,
            )
            total = cur.fetchone()[0]

            cur.execute(
                f"""
                SELECT id, kind, title, body, severity,
                       fired_at, read_at, dismissed_at,
                       related_entity_kind, related_entity_id,
                       related_control_ref, related_event_type
                  FROM tenant_notification
                 WHERE {where_sql}
                 ORDER BY fired_at DESC
                 LIMIT %s OFFSET %s
                """,
                params + [limit, offset],
            )
            rows = cur.fetchall()

            # Summary counts across the FILTERED set — same design as
            # /posture: pagination-aware clients get whole-set numbers
            # without re-counting.
            cur.execute(
                f"""
                SELECT
                    COUNT(*)                                                           AS total_,
                    COUNT(*) FILTER (WHERE read_at IS NULL AND dismissed_at IS NULL)   AS unread_,
                    COUNT(*) FILTER (
                        WHERE severity IN ('critical','high')
                          AND read_at IS NULL
                          AND dismissed_at IS NULL
                    )                                                                  AS urgent_
                  FROM tenant_notification
                 WHERE {where_sql}
                """,
                params,
            )
            (_total_check, unread_ct, urgent_ct) = cur.fetchone()
    finally:
        pool.putconn(conn)

    return NotificationsResponse(
        tenant_id               = key.tenant_id,
        generated_at            = _iso_now(),
        notifications           = [_row_to_notification(r) for r in rows],
        summary                 = NotificationsSummary(
            total  = int(total),
            unread = int(unread_ct or 0),
            urgent = int(urgent_ct or 0),
        ),
        total_before_pagination = int(total),
    )


# ── GET /notifications/{id} ───────────────────────────────────────────

@router.get("/notifications/{notification_id}",
            response_model = Notification,
            summary        = "Fetch a single notification by id")
async def get_notification(
    notification_id: str,
    request:         Request,
    key              = Depends(external_key_with_scope("external:notifications:read")),
):
    """Fetch a single notification by its UUID. Returns 404 if the
    id doesn't exist for this tenant."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (key.tenant_id,))
            try:
                cur.execute(
                    """
                    SELECT id, kind, title, body, severity,
                           fired_at, read_at, dismissed_at,
                           related_entity_kind, related_entity_id,
                           related_control_ref, related_event_type
                      FROM tenant_notification
                     WHERE tenant_id = %s::uuid AND id = %s::uuid
                     LIMIT 1
                    """,
                    (key.tenant_id, notification_id),
                )
                row = cur.fetchone()
            except Exception as e:
                # Malformed UUID → invalid_input rather than 500
                logger.info("get_notification bad id %r: %s", notification_id, e)
                raise HTTPException(
                    status_code = 400,
                    detail      = f"notification_id must be a UUID; got: {notification_id!r}",
                )
    finally:
        pool.putconn(conn)

    if row is None:
        raise HTTPException(
            status_code = 404,
            detail      = f"No notification {notification_id!r} for this tenant.",
        )

    return _row_to_notification(row)
