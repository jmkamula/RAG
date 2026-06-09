---
name: upload-failed-row-lifecycle
description: "SHIPPED 2026-06-09 (404afe0 + cf5a08c, schema_v33 + v34): 'failed' document_uploads rows no longer block SHA-dedup, cascade-delete on successful retry, sweep after 30d."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

A crashed pipeline used to leave `document_uploads` rows wedged at
`extraction_status='failed'` and block all re-upload attempts of the
same file. The dedup unique index `uniq_document_uploads_tenant_sha256`
excluded only `'duplicate'` rows; failed rows kept their slot, so even
after fixing the pipeline bug the user couldn't retry without manual
DB cleanup.

Surfaced 2026-06-09 by `Information Security and Data Management
Process.docx` failing via `ModuleNotFoundError: No module named
'intake'` in `_merge_small_sections` (a stale `from intake.readers`
import that should have been `from rag.intake.readers` — fixed in
commit 6a564a7). The retry was then rejected as a duplicate.

## Three-layer fix

**Layer 1 — dedup excludes 'failed' (schema_v33 + api_server.py).**
Both the unique index `uniq_document_uploads_tenant_sha256` and the
application's pre-insert dedup query now use the predicate
`extraction_status NOT IN ('duplicate', 'failed')`. A failed row no
longer blocks fresh upload of the same SHA.

**Layer 2 — cascade-on-success (api_server.upload_document).** In
the same transaction that inserts the new row, we first
`DELETE FROM document_uploads WHERE sha256=… AND extraction_status
IN ('failed','duplicate')`. If the insert fails (e.g. disk write
issue), the prior failed row stays intact for forensics. If it
succeeds, the audit-log noise from the crashed pipeline disappears
the moment a successful upload of the same bytes lands.

**Layer 3 — time-based sweep (schema_v34 + scripts/purge_failed_uploads.py).**
`fn_purge_failed_uploads(p_older_than_days INT DEFAULT 30,
p_dry_run BOOLEAN DEFAULT TRUE)` hard-deletes failed rows older
than the threshold. Catches the long-tail case where the user never
retried — Layer 2 only fires on retry. Wrapper script defaults to
dry-run for safety.

## Cron (not yet wired)

Recommended nightly entry documented in the script docstring:
```
30 3 * * * cd /data/arioncomply && PYTHONPATH=. \
    python3 scripts/purge_failed_uploads.py --apply >> \
    /var/log/arioncomply/purge_failed_uploads.log 2>&1
```
The function uses `SECURITY DEFINER` so it can be invoked by
`arioncomply_app` without superuser DELETE privileges.

## Why document_uploads stays outside the standard retention model

`document_uploads` is an intake audit log — not a soft-deletable
business record. It deliberately lacks `is_active` / `purge_after` /
`retention_class` columns and is not enrolled in the nightly
`fn_purge_expired_records` table list. We use a purpose-built
function tied to `extraction_status='failed'` instead of fitting it
into the generic retention machinery.

## Related

- [[engine-to-posture-controls-wiring-fix]] — earlier upload pipeline
  scar.
- [[doc-curation-engine-v1]] — the broader upload/extraction flow this
  fits into.
