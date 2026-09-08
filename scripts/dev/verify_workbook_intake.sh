#!/usr/bin/env bash
#
# scripts/dev/verify_workbook_intake.sh — v4
#
# Correct column names for document_findings: document_id (not
# client_document_id), checklist_item_id (not must_id).

set -u

sudo -u postgres psql -d arioncomply_compliance <<'SQL'
\echo '=== 1. Latest workbook upload ==='
SELECT LEFT(filename, 55) AS filename,
       LEFT(id::text, 8) AS upload_id,
       findings_count AS reported_count,
       extraction_status,
       uploaded_at::time(0) AS uploaded
  FROM document_uploads
 WHERE filename ILIKE '%workbook%'
 ORDER BY uploaded_at DESC LIMIT 3;

\echo ''
\echo '=== 2. ACTUAL findings landed (document_findings.document_id joined via SHA) ==='
WITH latest AS (
  SELECT sha256, tenant_id
    FROM document_uploads
   WHERE filename ILIKE '%workbook%'
   ORDER BY uploaded_at DESC LIMIT 1
),
cd_match AS (
  SELECT cd.id AS cd_id
    FROM client_documents cd, latest
   WHERE cd.tenant_id = latest.tenant_id
     AND cd.checksum_sha256 = latest.sha256
)
SELECT COUNT(*) AS total_findings,
       COUNT(DISTINCT control_ref) AS distinct_controls,
       COUNT(DISTINCT checklist_item_id) FILTER (WHERE checklist_item_id IS NOT NULL) AS distinct_musts,
       status,
       confidence
  FROM document_findings
 WHERE document_id IN (SELECT cd_id FROM cd_match)
 GROUP BY status, confidence
 ORDER BY total_findings DESC;

\echo ''
\echo '=== 3. Sample findings (first 15) ==='
WITH latest AS (
  SELECT sha256, tenant_id FROM document_uploads
   WHERE filename ILIKE '%workbook%'
   ORDER BY uploaded_at DESC LIMIT 1
),
cd_match AS (
  SELECT cd.id AS cd_id FROM client_documents cd, latest
   WHERE cd.tenant_id = latest.tenant_id AND cd.checksum_sha256 = latest.sha256
)
SELECT LEFT(control_ref, 15) AS control_ref,
       LEFT(checklist_item_id, 40) AS must,
       status,
       confidence,
       LEFT(excerpt, 40) AS excerpt
  FROM document_findings
 WHERE document_id IN (SELECT cd_id FROM cd_match)
 ORDER BY control_ref, checklist_item_id LIMIT 15;

\echo ''
\echo '=== 4. Discrepancy: what UI shows vs what actually landed ==='
WITH latest AS (
  SELECT id AS upload_id, sha256, tenant_id, findings_count AS ui_shows
    FROM document_uploads
   WHERE filename ILIKE '%workbook%'
   ORDER BY uploaded_at DESC LIMIT 1
),
cd_match AS (
  SELECT cd.id AS cd_id FROM client_documents cd, latest
   WHERE cd.tenant_id = latest.tenant_id AND cd.checksum_sha256 = latest.sha256
)
SELECT (SELECT ui_shows FROM latest) AS ui_shows_findings_count,
       (SELECT COUNT(*) FROM document_findings
         WHERE document_id IN (SELECT cd_id FROM cd_match)) AS actual_rows_in_document_findings;
SQL
