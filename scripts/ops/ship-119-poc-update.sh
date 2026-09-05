#!/usr/bin/env bash
#
# scripts/ops/ship-119-poc-update.sh
#
# On-VM deployment of Ship 119' — the Auditor's Ledger.
# Four sub-arcs:
#   119'.a  PII redactor + user pseudonymisation
#   119'.b  Aggregate ledger compiler + admin HTML endpoint
#   119'.c  One-time-download URL delivery (schema_v116 + public endpoint)
#   119'.d  UI (Profile → Auditor packages) + audit scope acknowledgement
#
# Invocation from operator's Mac:
#   ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
#     cd /data/arioncomply &&
#     git pull &&
#     bash scripts/ops/ship-119-poc-update.sh
#   '

set -euo pipefail

ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
cd "$ARION_ROOT"

if [[ ! -f deploy/install.sh ]]; then
    echo "ERROR: deploy/install.sh missing" >&2
    exit 78
fi

# ── 1. install.sh (applies schema_v116) ──────────────────────────
echo "=== 1. install.sh (applies schema_v116 idempotently) ==="
bash deploy/install.sh 2>&1 | tail -25

# ── 2. Restart API ───────────────────────────────────────────────
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
        echo "WARN: API did not respond within 24s"
        exit 1
    fi
done

# ── 4. Verify schema_v116 applied ────────────────────────────────
echo
echo "=== 4. Verify schema_v116 applied ==="
sudo -u postgres psql -d arioncomply_compliance -tAc \
    "SELECT version FROM schema_migrations
      WHERE version = 'schema_v116_audit_ledger_download_tokens'"

echo
echo "=== 5. Verify token table exists + grants correct ==="
sudo -u postgres psql -d arioncomply_compliance -c \
    "SELECT table_name FROM information_schema.tables
      WHERE table_name = 'audit_ledger_download_token';"

sudo -u postgres psql -d arioncomply_compliance -c \
    "SELECT grantee, privilege_type
       FROM information_schema.role_table_grants
      WHERE table_name = 'audit_ledger_download_token'
        AND grantee = 'arioncomply_app'
      ORDER BY privilege_type;"

# ── 6. PII redactor tests (offline, deterministic) ───────────────
echo
echo "=== 6. Run PII redactor test suite ==="
PYTHONPATH=. python3 tests/test_pii_redactor.py

# ── 7. Endpoint smoke test — new token endpoints resolve ─────────
# We probe with a nonexistent-prefix revoke that MUST 404 or 400,
# not 500 or "not-found handler". Confirms the route is live.
echo
echo "=== 7. Endpoint smoke test — token routes registered ==="
if curl -s -o /dev/null -w "%{http_code}\n" \
     "http://127.0.0.1:8080/api/v1/admin/audit-ledger/tokens" | grep -qE '401|403'; then
    echo "  GET /admin/audit-ledger/tokens: registered (401/403 without key = expected)"
else
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
                  "http://127.0.0.1:8080/api/v1/admin/audit-ledger/tokens")
    echo "  WARN: expected 401/403 without key, got $STATUS"
fi

# ── 8. Deployment log tail ───────────────────────────────────────
echo
echo "=== 8. Deployment log — last 3 entries ==="
jq -c . .deployment_log.jsonl | tail -3

echo
echo "=== Ship 119' deployment complete ==="
echo
echo "Try in browser via SSH tunnel:"
echo "  ssh -L 8080:127.0.0.1:8080 arionops@10.0.1.85"
echo "  http://localhost:8080/  → sign in → Profile → 'Auditor packages'"
echo "  → 'Generate audit package' → tick acknowledgement → Generate URL"
echo "  → copy the one-time URL → open in a private window (no key needed)"
