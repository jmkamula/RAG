#!/usr/bin/env bash
#
# scripts/ops/ship-128-poc-update.sh
#
# On-VM deployment of Ship 128' — workbook 0-findings root-cause fix.
#
#   128'.a  api_server.py POST /documents/upload now inserts a
#           companion client_documents row in the same txn as the
#           document_uploads insert. Fixes silent-skip bug where any
#           upload that doesn't produce LLM findings (workbooks, PDFs
#           with 0 extractable findings, failed extractions) had no
#           client_documents row → workbook_discovery's SHA-256 lookup
#           returned 0 → whole workbook block silently skipped.
#
#   128'.b  Clears the 2 stuck workbook uploads on this PoC (jk +
#           `(1)` workbooks that failed with 0 findings pre-Ship-128).
#           Operator re-uploads via UI to verify the fix.
#
# Invocation from operator's Mac:
#   ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
#     cd /data/arioncomply &&
#     git pull &&
#     bash scripts/ops/ship-128-poc-update.sh
#   '

set -euo pipefail

ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
cd "$ARION_ROOT"

if [[ ! -f deploy/install.sh ]]; then
    echo "ERROR: deploy/install.sh missing" >&2
    exit 78
fi

# ── 1. install.sh (no schema; picks up code fix + baseline_grants idempotent) ──
echo "=== 1. install.sh (code fix only; no schema changes) ==="
bash deploy/install.sh 2>&1 | tail -15

# ── 2. Restart API to load api_server.py fix ─────────────────────
echo
echo "=== 2. Restart arioncomply-api ==="
sudo systemctl restart arioncomply-api

echo
echo "=== 3. Wait for API + probe /docs ==="
for i in 1 2 3 4 5 6 7 8; do
    if curl -sf --max-time 3 http://127.0.0.1:8080/docs > /dev/null; then
        echo "API up after $((i*3))s"; break
    fi
    sleep 3
    if [[ "$i" -eq 8 ]]; then
        echo "WARN: API did not respond within 24s"; exit 1
    fi
done

# ── 4. Clean up the 2 stuck workbook uploads ─────────────────────
# Both uploaded 2026-09-08 pre-fix; landed in document_uploads with
# extraction_status='completed' but findings_count=0 because the
# workbook_discovery block silently skipped (no client_documents row).
# Hard-delete both DB rows + storage files so the operator can re-upload
# via the UI without hitting the 409 duplicate check.
echo
echo "=== 4. Clean up stuck workbook uploads ==="
sudo -u postgres psql -d arioncomply_compliance <<'SQL'
BEGIN;
-- Show what we're about to delete for transparency
\echo 'Stuck workbook uploads to be cleared:'
SELECT LEFT(filename, 55) AS filename,
       LEFT(id::text, 8) AS upload_id,
       storage_path,
       findings_count,
       uploaded_at::date
  FROM document_uploads
 WHERE filename ILIKE '%workbook%'
   AND findings_count = 0
   AND extraction_status = 'completed';

-- Store paths so we can rm files after DELETE commits
CREATE TEMP TABLE _to_purge AS
SELECT id, storage_path
  FROM document_uploads
 WHERE filename ILIKE '%workbook%'
   AND findings_count = 0
   AND extraction_status = 'completed';

-- Delete document_uploads rows
DELETE FROM document_uploads
 WHERE id IN (SELECT id FROM _to_purge);

\echo ''
\echo 'Storage paths to remove after commit:'
SELECT storage_path FROM _to_purge;

COMMIT;

\echo ''
\echo 'DB cleanup complete.'
SQL

# Now remove the actual files. Extract paths + remove.
sudo -u postgres psql -d arioncomply_compliance -tAc "
-- Re-derive paths from expected uploads/<tenant>/<id>.xlsm pattern
-- since the temp table is dropped on commit. Both files are known:
--   c69a6d00-f3a8-4587-b31d-8a18c3d8c3dd.xlsm (was: '(1).xlsm')
--   c7439179-14d6-475c-bba4-4c211ea5d909.xlsm (was: jk.xlsm)
SELECT 'File cleanup: manual step (both under uploads/2b6db5af-*/*)';"

# Best-effort file cleanup (safe: only .xlsm under the Arion tenant dir
# for the two specific upload_id prefixes)
for f in \
    /data/arioncomply/uploads/2b6db5af-a607-4b57-9664-320b7de86772/c69a6d00-f3a8-4587-b31d-8a18c3d8c3dd.xlsm \
    /data/arioncomply/uploads/2b6db5af-a607-4b57-9664-320b7de86772/c7439179-14d6-475c-bba4-4c211ea5d909.xlsm ; do
    if [[ -f "$f" ]]; then
        rm -f "$f" && echo "  removed: $f"
    else
        echo "  (already gone): $f"
    fi
done

# ── 5. Verify slate is clean ─────────────────────────────────────
echo
echo "=== 5. Verify: no stuck workbook uploads remain ==="
sudo -u postgres psql -d arioncomply_compliance -c "
SELECT LEFT(filename, 55) AS filename, findings_count, extraction_status
  FROM document_uploads
 WHERE filename ILIKE '%workbook%'
 ORDER BY uploaded_at DESC LIMIT 5;"

# ── 6. Deployment log tail ───────────────────────────────────────
echo
echo "=== 6. Deployment log — last 3 entries ==="
jq -c . .deployment_log.jsonl | tail -3

echo
echo "=== Ship 128' deployment complete ==="
echo
echo "Next step (manual):"
echo "  1. Open the UI (SSH tunnel + browser at http://localhost:8080/)"
echo "  2. Re-upload the ISO 27001 workbook via the Documents section"
echo "  3. Watch the intake events — you should see workbook_discovery"
echo "     complete with findings_written > 0 (dev VM historical baseline"
echo "     was 210 findings on the same file shape)"
echo "  4. Verify findings landed:"
echo "     sudo -u postgres psql -d arioncomply_compliance -c \\"
echo "       \"SELECT findings_count FROM document_uploads WHERE filename ILIKE '%workbook%' ORDER BY uploaded_at DESC LIMIT 1;\""
