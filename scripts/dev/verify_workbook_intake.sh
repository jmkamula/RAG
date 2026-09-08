#!/usr/bin/env bash
#
# scripts/dev/verify_workbook_intake.sh — v2
#
# Post-upload verification for Ship 128' fix. Uses upload_id (not
# filename) to correlate — filename collides across old/new uploads
# after the Ship 128'.b cleanup deleted document_uploads but left
# intake_trace_log historical rows in place.

set -u

sudo -u postgres psql -d arioncomply_compliance <<'SQL'
\echo '=== 1. Latest workbook upload (correlation key = upload_id) ==='
SELECT id AS upload_id,
       LEFT(filename, 55) AS filename,
       findings_count,
       extraction_status,
       LEFT(sha256, 16) AS sha_prefix,
       uploaded_at::time(0) AS uploaded
  FROM document_uploads
 WHERE filename ILIKE '%workbook%'
 ORDER BY uploaded_at DESC LIMIT 3;

\echo ''
\echo '=== 2. intake_trace_log for the LATEST upload_id ONLY ==='
WITH latest AS (
  SELECT id::text AS upload_id
    FROM document_uploads
   WHERE filename ILIKE '%workbook%'
   ORDER BY uploaded_at DESC LIMIT 1
)
SELECT stage,
       stage_status,
       stage_ms,
       findings_raw,
       findings_kept,
       findings_written,
       LEFT(error_detail, 80) AS err
  FROM intake_trace_log
 WHERE upload_id = (SELECT upload_id FROM latest)
 ORDER BY traced_at;

\echo ''
\echo '=== 3. client_documents that matches latest upload (SHA lookup workbook_discovery uses) ==='
WITH latest AS (
  SELECT sha256, tenant_id
    FROM document_uploads
   WHERE filename ILIKE '%workbook%'
   ORDER BY uploaded_at DESC LIMIT 1
)
SELECT LEFT(filename, 40) AS filename,
       LEFT(id::text, 8) AS cd_id,
       LEFT(checksum_sha256, 16) AS sha,
       document_status,
       is_active,
       tenant_id::text = (SELECT tenant_id::text FROM latest) AS tenant_match,
       uploaded_at::time(0) AS uploaded
  FROM client_documents
 WHERE checksum_sha256 = (SELECT sha256 FROM latest);

\echo ''
\echo '=== 4. What the workbook_discovery SHA lookup actually returns (simulated) ==='
-- The lookup runs as arioncomply_app with app.tenant_id set. Simulate
-- as owner (RLS bypassed) to see the raw truth first.
WITH latest AS (
  SELECT sha256, tenant_id::text AS tenant_id
    FROM document_uploads
   WHERE filename ILIKE '%workbook%'
   ORDER BY uploaded_at DESC LIMIT 1
)
SELECT COUNT(*) AS rows_visible_to_owner,
       (SELECT sha256 FROM latest) AS sha_being_looked_up,
       (SELECT tenant_id FROM latest) AS tenant_being_looked_up
  FROM client_documents cd, latest
 WHERE cd.tenant_id = latest.tenant_id::uuid
   AND cd.checksum_sha256 = latest.sha256
   AND cd.is_active = TRUE;
SQL
