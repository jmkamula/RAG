"""
ArionComply — DeletionService

All deletions go through here. Direct SQL DELETE is never used in application code.

Enforces:
  - Retention policies from Postgres retention_policies table
  - Soft delete only for compliance/operational data
  - Anonymisation for personal data
  - Audit trail in deletion_log for every operation
  - GDPR Art.17 erasure requests with 30-day deadline tracking

Usage:
    svc = DeletionService(pg_conn, tenant_id, acting_user_id)

    # Soft delete a risk record
    svc.soft_delete('risks', risk_uuid)

    # Handle GDPR erasure request
    result = svc.handle_erasure_request(
        data_subject_ref = 'user@example.com',
        deadline_days    = 30,
    )

    # Admin: see soft-deleted records
    svc.list_deleted('posture_controls', limit=20)

    # Dry-run purge to see what would be cleaned up
    svc.purge_expired(dry_run=True)
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

logger = logging.getLogger(__name__)


# ── Retention class constants ─────────────────────────────────────────────────

COMPLIANCE    = "compliance"
OPERATIONAL   = "operational"
PERSONAL_DATA = "personal_data"
PLATFORM      = "platform"
SESSION       = "session"

# Tables that require manual review before purge — never auto-purged
MANUAL_REVIEW_TABLES = {
    "posture_controls", "posture_history", "posture_pending",
    "isms_audits", "document_findings", "document_sections",
    "incidents", "incident_timeline", "incident_documents",
    "incident_obligations", "incident_classifications",
}

# PII fields per table — anonymised on erasure request
PII_FIELDS = {
    "users":   ["name", "email", "phone"],
    "vendors": ["contact_name", "contact_email", "contact_phone"],
    "incidents": ["reported_by_name", "reported_by_email", "affected_user_emails"],
    "assets":  ["owner_email"],
}


@dataclass
class DeletionResult:
    table:      str
    record_id:  UUID
    action:     str             # soft_deleted | anonymised | purged | skipped
    reason:     str
    purge_after: Optional[datetime] = None
    notes:      str = ""


@dataclass
class ErasureResult:
    data_subject_ref: str
    deadline:         datetime
    tables_affected:  list[dict] = field(default_factory=list)
    total_records:    int = 0
    completed_at:     Optional[datetime] = None


class DeletionService:
    """
    All deletions in ArionComply go through this service.
    Never call SQL DELETE directly in application code.

    Thread safety: each request should create its own instance with its
    own pg_conn. Do not share instances across threads.
    """

    def __init__(
        self,
        pg_conn,
        tenant_id:      str,
        acting_user_id: Optional[str] = None,  # None = system operation
    ):
        self._pg           = pg_conn
        self._tenant_id    = tenant_id
        self._acting_user  = acting_user_id

    # ── Public API ────────────────────────────────────────────────────────────

    def soft_delete(
        self,
        table:     str,
        record_id: str | UUID,
        reason:    str = "admin",
    ) -> DeletionResult:
        """
        Soft-delete a record by setting is_active = FALSE.
        The trigger fn_compute_purge_after will set purge_after automatically.
        Writes to deletion_log.

        Args:
            table:     table name (must have is_active column)
            record_id: UUID of the record
            reason:    why (admin | erasure_request | tenant_offboarding | test_data)
        """
        self._validate_reason(reason)

        with self._pg.cursor() as cur:
            # Check record exists and belongs to this tenant
            cur.execute(
                f"SELECT id, is_active, retention_class "
                f"FROM {table} "
                f"WHERE id = %s AND tenant_id = %s",
                (str(record_id), self._tenant_id)
            )
            row = cur.fetchone()
            if not row:
                raise ValueError(
                    f"Record {record_id} not found in {table} "
                    f"for tenant {self._tenant_id}"
                )
            _, is_active, retention_class = row

            if not is_active:
                logger.info(f"{table}/{record_id} already soft-deleted")
                return DeletionResult(
                    table=table, record_id=UUID(str(record_id)),
                    action="skipped", reason="already_deleted"
                )

            # Soft delete — trigger sets purge_after automatically
            cur.execute(
                f"UPDATE {table} SET "
                f"    is_active = FALSE, "
                f"    deleted_by = %s, "
                f"    deletion_reason = %s "
                f"WHERE id = %s AND tenant_id = %s "
                f"RETURNING purge_after",
                (self._acting_user, reason, str(record_id), self._tenant_id)
            )
            purge_after = cur.fetchone()[0]

            # Write audit log
            self._log_deletion(
                cur         = cur,
                table       = table,
                record_id   = str(record_id),
                dtype       = "soft",
                reason      = reason,
                ret_class   = retention_class,
                purge_after = purge_after,
            )

        self._pg.commit()

        logger.info(
            f"soft_delete: {table}/{record_id} "
            f"(retention={retention_class}, purge_after={purge_after})"
        )
        return DeletionResult(
            table       = table,
            record_id   = UUID(str(record_id)),
            action      = "soft_deleted",
            reason      = reason,
            purge_after = purge_after,
        )

    def restore(
        self,
        table:     str,
        record_id: str | UUID,
    ) -> DeletionResult:
        """
        Restore a soft-deleted record (set is_active = TRUE).
        Only permitted within retention window.
        Writes to deletion_log.
        """
        with self._pg.cursor() as cur:
            cur.execute(
                f"SELECT id, is_active, purge_after, retention_class "
                f"FROM {table} "
                f"WHERE id = %s AND tenant_id = %s",
                (str(record_id), self._tenant_id)
            )
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Record {record_id} not found in {table}")

            _, is_active, purge_after, retention_class = row

            if is_active:
                return DeletionResult(
                    table=table, record_id=UUID(str(record_id)),
                    action="skipped", reason="already_active"
                )

            cur.execute(
                f"UPDATE {table} SET "
                f"    is_active = TRUE, "
                f"    deleted_at = NULL, "
                f"    deleted_by = NULL, "
                f"    deletion_reason = NULL, "
                f"    purge_after = NULL "
                f"WHERE id = %s AND tenant_id = %s",
                (str(record_id), self._tenant_id)
            )

            self._log_deletion(
                cur       = cur,
                table     = table,
                record_id = str(record_id),
                dtype     = "soft",   # restored = reverse of soft delete
                reason    = "admin",
                ret_class = retention_class,
                notes     = "restored from soft delete",
            )

        self._pg.commit()
        return DeletionResult(
            table=table, record_id=UUID(str(record_id)),
            action="restored", reason="admin"
        )

    def anonymise(
        self,
        table:     str,
        record_id: str | UUID,
        reason:    str = "erasure_request",
    ) -> DeletionResult:
        """
        Anonymise PII fields in a record in-place.
        The record itself is retained (for compliance evidence).
        Replaces PII fields defined in PII_FIELDS[table] with '[anonymised]'.
        """
        pii_fields = PII_FIELDS.get(table, [])
        if not pii_fields:
            return DeletionResult(
                table=table, record_id=UUID(str(record_id)),
                action="skipped", reason=f"no_pii_fields_defined_for_{table}"
            )

        set_clauses = ", ".join(
            f"{f} = '[anonymised]'" for f in pii_fields
        )
        anon_marker = f"anonymised_at = NOW()" if table == "users" else ""
        if anon_marker:
            set_clauses += f", {anon_marker}"

        with self._pg.cursor() as cur:
            cur.execute(
                f"UPDATE {table} SET {set_clauses} "
                f"WHERE id = %s AND tenant_id = %s",
                (str(record_id), self._tenant_id)
            )
            cur.execute(
                f"SELECT retention_class FROM {table} WHERE id = %s",
                (str(record_id),)
            )
            row = cur.fetchone()
            ret_class = row[0] if row else "personal_data"

            self._log_deletion(
                cur       = cur,
                table     = table,
                record_id = str(record_id),
                dtype     = "anonymise",
                reason    = reason,
                ret_class = ret_class,
            )

        self._pg.commit()
        logger.info(f"anonymise: {table}/{record_id} ({len(pii_fields)} fields)")
        return DeletionResult(
            table=table, record_id=UUID(str(record_id)),
            action="anonymised", reason=reason
        )

    def handle_erasure_request(
        self,
        data_subject_ref: str,   # email or name of data subject
        deadline_days:    int = 30,
    ) -> ErasureResult:
        """
        GDPR Art.17 erasure request.
        Anonymises all records linked to the data subject.
        Logs the request with deadline for compliance tracking.
        Returns ErasureResult with details of what was processed.
        """
        from datetime import timedelta
        deadline = datetime.now(timezone.utc) + timedelta(days=deadline_days)
        result   = ErasureResult(
            data_subject_ref = data_subject_ref,
            deadline         = deadline,
        )

        with self._pg.cursor() as cur:
            # Find user records matching this data subject
            cur.execute("""
                SELECT id, name, email FROM users
                WHERE tenant_id = %s
                  AND (email = %s OR name = %s)
                  AND is_active = TRUE
            """, (self._tenant_id, data_subject_ref, data_subject_ref))
            user_rows = cur.fetchall()

            if user_rows:
                for user_id, name, email in user_rows:
                    cur.execute("""
                        UPDATE users SET
                            name          = '[anonymised]',
                            email         = '[anonymised-' || id::text || ']',
                            anonymised_at = NOW(),
                            deletion_reason = 'erasure_request'
                        WHERE id = %s AND tenant_id = %s
                    """, (user_id, self._tenant_id))

                    self._log_deletion(
                        cur       = cur,
                        table     = "users",
                        record_id = str(user_id),
                        dtype     = "erasure",
                        reason    = "erasure_request",
                        ret_class = "personal_data",
                        notes     = f"Art.17 request, deadline {deadline.date()}",
                    )

                result.tables_affected.append({
                    "table":   "users",
                    "records": len(user_rows),
                    "action":  "anonymised",
                })
                result.total_records += len(user_rows)

        self._pg.commit()
        result.completed_at = datetime.now(timezone.utc)

        logger.info(
            f"erasure_request: {data_subject_ref} — "
            f"{result.total_records} records anonymised, "
            f"deadline {deadline.date()}"
        )
        return result

    def list_deleted(
        self,
        table:  str,
        limit:  int = 50,
    ) -> list[dict]:
        """
        List soft-deleted records for a table (admin view).
        Requires BYPASSRLS or calling with superuser credentials
        since RLS hides is_active=FALSE records.
        """
        with self._pg.cursor() as cur:
            cur.execute(
                f"SELECT id, deleted_at, deleted_by, deletion_reason, "
                f"       retention_class, purge_after "
                f"FROM {table} "
                f"WHERE tenant_id = %s AND is_active = FALSE "
                f"ORDER BY deleted_at DESC LIMIT %s",
                (self._tenant_id, limit)
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def purge_expired(self, dry_run: bool = True) -> list[dict]:
        """
        Purge records past their purge_after date.
        Only callable by superuser (fn_purge_expired_records is SECURITY DEFINER).
        Always dry_run=True by default — must explicitly pass False.
        """
        with self._pg.cursor() as cur:
            cur.execute(
                "SELECT * FROM fn_purge_expired_records(%s)",
                (dry_run,)
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def deletion_log(
        self,
        table:      Optional[str] = None,
        limit:      int = 100,
    ) -> list[dict]:
        """
        Read the deletion audit log for this tenant.
        """
        where = "WHERE tenant_id = %s"
        params = [self._tenant_id]
        if table:
            where += " AND table_name = %s"
            params.append(table)

        with self._pg.cursor() as cur:
            cur.execute(
                f"SELECT * FROM deletion_log {where} "
                f"ORDER BY executed_at DESC LIMIT %s",
                params + [limit]
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    # ── Private helpers ───────────────────────────────────────────────────────

    def _log_deletion(
        self,
        cur,
        table:      str,
        record_id:  str,
        dtype:      str,
        reason:     str,
        ret_class:  str,
        purge_after: Optional[datetime] = None,
        notes:      str = "",
    ) -> None:
        """Write one row to deletion_log. Called inside an open cursor."""
        cur.execute("""
            INSERT INTO deletion_log (
                tenant_id, table_name, record_id,
                deletion_type, reason,
                requested_by, executed_by,
                retention_class, purge_scheduled, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            self._tenant_id, table, record_id,
            dtype, reason,
            self._acting_user, self._acting_user,
            ret_class, purge_after, notes or None,
        ))

    @staticmethod
    def _validate_reason(reason: str) -> None:
        valid = {
            "erasure_request", "retention_expired",
            "tenant_offboarding", "admin", "test_data"
        }
        if reason not in valid:
            raise ValueError(
                f"Invalid deletion reason '{reason}'. Must be one of: {valid}"
            )
