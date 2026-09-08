#!/usr/bin/env bash
#
# scripts/dev/diagnose_workbook_jk.sh — v3
#
# The missing-link diagnostic. Check whether client_documents has rows
# for the failing uploads, which is the SHA-256 lookup workbook_discovery
# depends on before running persist_proposals.

set -u
ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
cd "$ARION_ROOT"

echo "=== 1. document_uploads (all workbooks) ==="
sudo -u postgres psql -d arioncomply_compliance -c "
SELECT LEFT(filename, 55) AS filename,
       LEFT(id::text, 8) AS upload_id,
       LEFT(sha256, 16) AS sha_prefix,
       findings_count, extraction_status, uploaded_at::date
  FROM document_uploads
 WHERE filename ILIKE '%workbook%'
 ORDER BY uploaded_at DESC LIMIT 5;"

echo
echo "=== 2. client_documents (all — is the table empty for this tenant?) ==="
sudo -u postgres psql -d arioncomply_compliance -c "
SELECT LEFT(filename, 55) AS filename,
       LEFT(id::text, 8) AS cd_id,
       LEFT(checksum_sha256, 16) AS sha_prefix,
       document_status,
       tenant_id::text = '2b6db5af-a607-4b57-9664-320b7de86772' AS is_arion,
       uploaded_at::date
  FROM client_documents
 ORDER BY uploaded_at DESC NULLS LAST LIMIT 10;"

echo
echo "=== 3. Count uploads vs client_documents for Arion tenant ==="
sudo -u postgres psql -d arioncomply_compliance -c "
SELECT
  (SELECT COUNT(*) FROM document_uploads WHERE tenant_id = '2b6db5af-a607-4b57-9664-320b7de86772'::uuid) AS uploads,
  (SELECT COUNT(*) FROM client_documents WHERE tenant_id = '2b6db5af-a607-4b57-9664-320b7de86772'::uuid) AS client_docs,
  (SELECT COUNT(*) FROM client_documents WHERE tenant_id = '2b6db5af-a607-4b57-9664-320b7de86772'::uuid AND checksum_sha256 IS NOT NULL) AS client_docs_with_sha;"

echo
echo "=== 4. Do the SHAs match? (uploads sha256 vs client_documents checksum_sha256) ==="
sudo -u postgres psql -d arioncomply_compliance -c "
WITH u AS (
  SELECT sha256 FROM document_uploads
   WHERE tenant_id = '2b6db5af-a607-4b57-9664-320b7de86772'::uuid
     AND filename ILIKE '%workbook%'
),
c AS (
  SELECT checksum_sha256 FROM client_documents
   WHERE tenant_id = '2b6db5af-a607-4b57-9664-320b7de86772'::uuid
)
SELECT 'uploads_sha_missing_from_client_docs' AS check,
       COUNT(*) FILTER (WHERE u.sha256 NOT IN (SELECT checksum_sha256 FROM c)) AS n
  FROM u;"
