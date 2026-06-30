"""
ArionComply — Cascade notification writer (S3t)

Tiny helper that inserts tenant_notification rows from cascade
write sites. De-dups against the active-row partial unique index
(unread+undismissed for same kind+entity), so repeated triggers
don't spam the inbox.

Severity convention:
  critical  — Art.33-style hard deadline missed
  high      — SLA breach detected, cascade-blocked under live conditions
  medium    — followup overdue, threshold crossed (single tenant impact)
  low       — auto-resolved confirmation (FYI)
  info      — informational
"""
from __future__ import annotations
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def notify(
    pg_cursor,
    *,
    tenant_id:           str,
    kind:                str,
    title:               str,
    body:                Optional[str] = None,
    severity:            str = "info",
    related_entity_kind: Optional[str] = None,
    related_entity_id:   Optional[str] = None,
    related_control_ref: Optional[str] = None,
    related_event_type:  Optional[str] = None,
) -> Optional[str]:
    """Insert a notification row, de-duping against active duplicates.

    Returns the new row id when written, or None when the partial
    unique index suppressed it as a duplicate. Best-effort: never
    raises — failure is logged and ignored to avoid cascading into
    the cascade engine's own error paths.

    Caller is responsible for the surrounding transaction and the
    app.tenant_id GUC.
    """
    try:
        pg_cursor.execute(
            """
            INSERT INTO tenant_notification
                (tenant_id, kind, title, body, severity,
                 related_entity_kind, related_entity_id,
                 related_control_ref, related_event_type)
            VALUES (%s::uuid, %s, %s, %s, %s,
                    %s, %s::uuid, %s, %s)
            ON CONFLICT DO NOTHING
            RETURNING id::text
            """,
            (tenant_id, kind, title, body, severity,
             related_entity_kind, related_entity_id,
             related_control_ref, related_event_type),
        )
        row = pg_cursor.fetchone()
        return row[0] if row else None
    except Exception as e:
        logger.warning("notify() failed (%s): %s", kind, e)
        return None
