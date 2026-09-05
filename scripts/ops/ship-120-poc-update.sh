#!/usr/bin/env bash
#
# scripts/ops/ship-120-poc-update.sh
#
# On-VM deployment of Ship 120' — audit-table DELETE-drift diagnostic + fix.
# One-sub-arc surface (no schema_v* needed — pure baseline_grants.sql
# fix + regression test):
#   120'.c  deploy/baseline_grants.sql extended with post-blanket-grant
#           REVOKE block enforcing intended shape for the 9 audit tables
#           (3 append-only compliance + 1 counter-audit + 5 diagnostic).
#   120'.d  tests/test_audit_table_grants.py locks the shape.
#
# Invocation from operator's Mac:
#   ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
#     cd /data/arioncomply &&
#     git pull &&
#     bash scripts/ops/ship-120-poc-update.sh
#   '

set -euo pipefail

ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
cd "$ARION_ROOT"

if [[ ! -f deploy/install.sh ]]; then
    echo "ERROR: deploy/install.sh missing" >&2
    exit 78
fi

# ── 1. install.sh (re-applies baseline_grants.sql with 120' fix) ──
# baseline_grants.sql runs at install.sh step 4.9 — post-migration
# reconciliation. Re-running it is idempotent. The fix's new DO block
# revokes the errantly-granted UPDATE/DELETE on the 9 audit tables.
echo "=== 1. install.sh (re-applies baseline_grants.sql idempotently) ==="
bash deploy/install.sh 2>&1 | tail -20

# ── 2. Restart API (no code change, but proves nothing wedged) ────
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

# ── 4. Verify grants match intended shape ─────────────────────────
# Direct query against Postgres info schema — proves the fix took.
# Before Ship 120': all 9 tables have DELETE (and 8 have UPDATE too).
# After Ship 120':
#   append-only compliance:   INSERT + SELECT only
#   audit_ledger_download_token: INSERT + SELECT + UPDATE
#   diagnostic:                INSERT + SELECT + DELETE
echo
echo "=== 4. Verify grant shape post-fix ==="
sudo -u postgres psql -d arioncomply_compliance -c "
SELECT table_name, string_agg(privilege_type, ',' ORDER BY privilege_type) AS grants
  FROM information_schema.role_table_grants
 WHERE grantee = 'arioncomply_app'
   AND table_name IN (
     'posture_status_log', 'applicability_status_log', 'client_facts_log',
     'audit_ledger_download_token',
     'ai_call_log', 'chat_casefile_log', 'chat_consensus_log',
     'fact_recompute_log', 'intake_trace_log'
   )
 GROUP BY table_name
 ORDER BY table_name;
"

# ── 5. Run the audit-table-grants regression test ─────────────────
# The test uses ARION_OWNER_PW from .env via python-dotenv.
echo
echo "=== 5. Run tests/test_audit_table_grants.py ==="
PYTHONPATH=. python3 tests/test_audit_table_grants.py

# ── 6. Deployment log tail ────────────────────────────────────────
echo
echo "=== 6. Deployment log — last 3 entries ==="
jq -c . .deployment_log.jsonl | tail -3

echo
echo "=== Ship 120' deployment complete ==="
echo
echo "Expected grant shape after fix:"
echo "  ai_call_log                 : DELETE,INSERT,SELECT"
echo "  applicability_status_log    : INSERT,SELECT"
echo "  audit_ledger_download_token : INSERT,SELECT,UPDATE"
echo "  chat_casefile_log           : DELETE,INSERT,SELECT"
echo "  chat_consensus_log          : DELETE,INSERT,SELECT"
echo "  client_facts_log            : INSERT,SELECT"
echo "  fact_recompute_log          : DELETE,INSERT,SELECT"
echo "  intake_trace_log            : DELETE,INSERT,SELECT"
echo "  posture_status_log          : INSERT,SELECT"
