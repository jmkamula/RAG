#!/usr/bin/env bash
#
# scripts/dev/verify_workbook_intake.sh — v3
#
# Post-Ship-128' verification. Log analysis on 2026-09-08 showed
# workbook_discovery wrote 207 findings + arbiter wrote 449 = 656
# total, but document_uploads.findings_count reported 0. Confirm the
# real count by counting document_findings rows for the upload's
# client_document_id.

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
\echo '=== 2. ACTUAL findings landed (via client_document_id join on SHA) ==='
WITH latest AS (
  SELECT id AS upload_id, sha256, tenant_id
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
       COUNT(*) FILTER (WHERE inference_source = 'workbook') AS from_workbook_discovery,
       COUNT(*) FILTER (WHERE inference_source = 'workbook_arbiter') AS from_llm_arbiter,
       COUNT(*) FILTER (WHERE inference_source NOT IN ('workbook', 'workbook_arbiter')) AS other_source,
       COUNT(DISTINCT control_ref) AS distinct_controls_covered
  FROM document_findings
 WHERE client_document_id IN (SELECT cd_id FROM cd_match);

\echo ''
\echo '=== 3. Sample findings (first 10) ==='
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
       LEFT(must_id, 40) AS must,
       inference_source,
       finding
  FROM document_findings
 WHERE client_document_id IN (SELECT cd_id FROM cd_match)
 ORDER BY control_ref, must_id LIMIT 10;

\echo ''
\echo '=== 4. Stage 4.6 + 4.7 log summary from api log tail ==='
\echo '(Log excerpt for correlation — the actual data is in Section 2)'
\! grep -E "Stage 4\.6|Stage 4\.7|workbook_arbiter|Complete:.*workbook" /tmp/arioncomply-api.log | tail -20
SQL
