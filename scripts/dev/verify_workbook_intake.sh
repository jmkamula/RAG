#!/usr/bin/env bash
#
# scripts/dev/verify_workbook_intake.sh
#
# Post-upload verification for the Ship 128' fix. Prints:
#   1. Latest workbook uploads with findings_count + extraction_status
#   2. workbook_discovery trace row (findings_written should be > 0)
#   3. Sample of what actually landed in document_findings
#   4. client_documents row for the upload (confirms Ship 128'.a wired)

set -u

sudo -u postgres psql -d arioncomply_compliance <<'SQL'
\echo '=== 1. Recent workbook uploads ==='
SELECT LEFT(filename, 55) AS filename,
       LEFT(id::text, 8) AS upload_id,
       findings_count,
       extraction_status,
       uploaded_at::time(0) AS uploaded
  FROM document_uploads
 WHERE filename ILIKE '%workbook%'
 ORDER BY uploaded_at DESC LIMIT 5;

\echo ''
\echo '=== 2. workbook_discovery trace (findings_written should be > 0) ==='
SELECT LEFT(filename, 45) AS filename,
       stage,
       stage_status,
       stage_ms,
       findings_written
  FROM intake_trace_log
 WHERE filename ILIKE '%workbook%'
   AND stage IN ('workbook_discovery', 'write', 'complete')
 ORDER BY traced_at DESC LIMIT 10;

\echo ''
\echo '=== 3. Sample findings from the latest workbook ==='
WITH latest AS (
  SELECT id FROM document_uploads
   WHERE filename ILIKE '%workbook%'
   ORDER BY uploaded_at DESC LIMIT 1
)
SELECT LEFT(control_ref, 15) AS control_ref,
       LEFT(must_item_id, 40) AS must,
       inference_source,
       finding
  FROM document_findings
 WHERE document_id = (SELECT id FROM latest)
    OR client_document_id IN (
        SELECT id FROM client_documents
         WHERE checksum_sha256 = (SELECT sha256 FROM latest LIMIT 1)
    )
 ORDER BY control_ref LIMIT 15;

\echo ''
\echo '=== 4. client_documents row (Ship 128a upload-time insert) ==='
SELECT LEFT(filename, 45) AS filename,
       LEFT(id::text, 8) AS cd_id,
       LEFT(checksum_sha256, 16) AS sha_prefix,
       document_status,
       uploaded_at::time(0) AS uploaded
  FROM client_documents
 WHERE filename ILIKE '%workbook%'
 ORDER BY uploaded_at DESC LIMIT 5;
SQL
