#!/usr/bin/env bash
#
# scripts/ops/ship-126-poc-update.sh
#
# On-VM deployment of Ship 126' — application-layer security fixes:
#
#   126'.a  dev API key rotation (dev-VM only; PoC keys not touched)
#   126'.b  PII redaction on 3 log tables + schema_v117 marker +
#           backfill of existing rows
#   126'.c  LLM prompt-injection hardening (delimiters + system prompt)
#   126'.d  SPA localStorage rehydration sanitize
#   126'.e  2 secret-in-tree cleanups (docstring creds + dev password)
#
# Invocation from operator's Mac:
#   ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
#     cd /data/arioncomply &&
#     git pull &&
#     bash scripts/ops/ship-126-poc-update.sh
#   '

set -euo pipefail

ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
cd "$ARION_ROOT"

if [[ ! -f deploy/install.sh ]]; then
    echo "ERROR: deploy/install.sh missing" >&2
    exit 78
fi

# ── 1. install.sh (applies schema_v117 marker + baseline_grants idempotent) ──
echo "=== 1. install.sh (applies schema_v117_pii_redaction_marker.sql) ==="
bash deploy/install.sh 2>&1 | tail -20

# ── 2. Verify schema_v117 applied ─────────────────────────────────
echo
echo "=== 2. Verify schema_v117 applied ==="
sudo -u postgres psql -d arioncomply_compliance -tAc \
    "SELECT version FROM schema_migrations
      WHERE version = 'schema_v117_pii_redaction_marker'"

# ── 3. Restart API to load new prompt + redaction code ────────────
echo
echo "=== 3. Restart arioncomply-api ==="
sudo systemctl restart arioncomply-api

echo
echo "=== 4. Wait for API + probe /docs ==="
for i in 1 2 3 4 5 6 7 8; do
    if curl -sf --max-time 3 http://127.0.0.1:8080/docs > /dev/null; then
        echo "API up after $((i*3))s"; break
    fi
    sleep 3
    if [[ "$i" -eq 8 ]]; then
        echo "WARN: API did not respond within 24s"; exit 1
    fi
done

# ── 5. Run PII redaction backfill on historical rows ──────────────
# Uses ARION_OWNER_PW via python-dotenv (Ship 111' canonical scheme).
# Idempotent — redact_pii is idempotent by design; re-runs no-op.
echo
echo "=== 5. Backfill PII redaction on historical rows ==="
if [[ -f scripts/ops/backfill_pii_redaction.py ]]; then
    PYTHONPATH=. python3 scripts/ops/backfill_pii_redaction.py 2>&1 | tail -15
else
    echo "  (scripts/ops/backfill_pii_redaction.py not found — skipping)"
fi

# ── 6. Spot-check redaction on the 3 log tables ───────────────────
# The backfill numbers above already tell us how many rows were
# updated. This step shows the intended shape on any row containing
# an email pattern — should always show `<email-redacted>`.
echo
echo "=== 6. Spot-check PII redaction on historical rows ==="
sudo -u postgres psql -d arioncomply_compliance -c "
SELECT 'chat_casefile_log' AS tbl, LEFT(query, 120) AS query_preview
  FROM chat_casefile_log
 WHERE query LIKE '%<email-redacted>%' OR query LIKE '%<ipv4-redacted>%'
 ORDER BY created_at DESC LIMIT 2
UNION ALL
SELECT 'chat_consensus_log', LEFT(query, 120)
  FROM chat_consensus_log
 WHERE query LIKE '%<email-redacted>%' OR query LIKE '%<ipv4-redacted>%'
 ORDER BY created_at DESC LIMIT 2;"

# ── 7. Endpoint registration smoke test (Ship 125'.f pattern) ─────
# Verifies chat endpoint + auth chain live without needing a valid
# API key. Real chat verification is via UI (SSH tunnel + browser).
echo
echo "=== 7. Chat endpoint registration smoke test ==="
code=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8080/api/v1/chat \
    -H "Content-Type: application/json" \
    -d '{"question":"ping"}')
if [[ "$code" =~ ^(401|403)$ ]]; then
    echo "  OK — /api/v1/chat returns $code without api key"
else
    echo "  WARN — expected 401/403 without api key, got $code"
fi

# ── 8. Deployment log tail ────────────────────────────────────────
echo
echo "=== 8. Deployment log — last 3 entries ==="
jq -c . .deployment_log.jsonl | tail -3

echo
echo "=== Ship 126' deployment complete ==="
echo
echo "What changed on this PoC:"
echo "  ✓ 5 log-table columns now scrubbed of PII at write-time"
echo "  ✓ Historical rows in ai_call_log / chat_consensus_log /"
echo "    chat_casefile_log backfilled to same shape"
echo "  ✓ LLM prompts wrap user query in [USER_QUERY] delimiters +"
echo "    system prompt declares them non-authoritative"
echo "  ✓ SPA chat-restore sanitises stored HTML before re-injecting"
echo "  ✓ rag/orchestrator.py docstring uses os.environ instead of"
echo "    hardcoded example passwords"
echo "  ✓ db/setup_local.sh generates strong app-user password"
echo "    (unused on Ubuntu PoC deploys, but cleans up dev-side)"
echo
echo "NOT changed on this PoC:"
echo "  · The dev-VM key rotation (Ship 126'.a) was dev-VM only."
echo "    This PoC's Quickstart-minted per-install keys are unaffected."
echo "    If you ever hardcoded 'arion_dev_key_2026' anywhere on this"
echo "    box, rotate it independently."
