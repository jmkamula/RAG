#!/usr/bin/env bash
#
# scripts/dev/backfill_findings_count.sh
#
# Ship 128'.c one-shot fix for the current stuck upload's
# document_uploads.findings_count. Ship 128'.a wrote 656 findings
# to document_findings, but the counter still reads 0 because the
# aggregation-across-paths fix (Ship 128'.c) landed after the
# upload completed.
#
# This script:
#   1. Counts actual document_findings rows for each recent upload
#      via SHA join on client_documents
#   2. UPDATE document_uploads SET findings_count = <actual> where
#      the current value is 0 but there are real findings on disk
#
# Idempotent + safe: only touches rows where the counter is
# demonstrably wrong.

set -u

sudo -u postgres psql -d arioncomply_compliance <<'SQL'
\echo '=== Before ==='
SELECT LEFT(filename, 55) AS filename,
       findings_count AS ui_shows,
       (SELECT COUNT(*) FROM document_findings df
          JOIN client_documents cd ON cd.id = df.document_id
         WHERE cd.tenant_id = du.tenant_id
           AND cd.checksum_sha256 = du.sha256) AS actual_rows
  FROM document_uploads du
 WHERE filename ILIKE '%workbook%'
 ORDER BY uploaded_at DESC LIMIT 5;

BEGIN;
\echo ''
\echo '=== Updating rows where counter is wrong ==='
WITH actuals AS (
  SELECT du.id AS upload_id,
         COUNT(df.id) AS actual
    FROM document_uploads du
    JOIN client_documents cd
      ON cd.tenant_id = du.tenant_id
     AND cd.checksum_sha256 = du.sha256
    LEFT JOIN document_findings df
      ON df.document_id = cd.id
   WHERE du.findings_count = 0
     AND du.extraction_status = 'completed'
   GROUP BY du.id
  HAVING COUNT(df.id) > 0
)
UPDATE document_uploads du
   SET findings_count = a.actual,
       updated_at = NOW()
  FROM actuals a
 WHERE du.id = a.upload_id
 RETURNING LEFT(du.filename, 55), findings_count;
COMMIT;

\echo ''
\echo '=== After ==='
SELECT LEFT(filename, 55) AS filename,
       findings_count AS ui_shows,
       (SELECT COUNT(*) FROM document_findings df
          JOIN client_documents cd ON cd.id = df.document_id
         WHERE cd.tenant_id = du.tenant_id
           AND cd.checksum_sha256 = du.sha256) AS actual_rows
  FROM document_uploads du
 WHERE filename ILIKE '%workbook%'
 ORDER BY uploaded_at DESC LIMIT 5;
SQL
