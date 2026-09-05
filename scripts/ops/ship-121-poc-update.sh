#!/usr/bin/env bash
#
# scripts/ops/ship-121-poc-update.sh
#
# On-VM deployment of Ship 121' — audit-table classification completion.
# Extends Ship 120' from 9 tables to 17. Pure `deploy/baseline_grants.sql`
# extension + regression-test extension. No new schema.
#
#   121'.a  Classified the 8 previously-unclassified _log tables:
#            6 append-only compliance (audit_log, confirmation_log,
#            deletion_log, cascade_suppression_log, client_fact_change_log,
#            external_evidence_verification_log)
#            2 diagnostic (request_trace_log, intake_consensus_log)
#   121'.b  Extended baseline_grants.sql + regression test to lock all 17.
#   121'.c  Pre-commit blanket-grant guard against future
#            `GRANT ... ON ALL TABLES ... TO arioncomply_app`.
#   121'.d  Pre-commit schema_v* over-grant guard against
#            `GRANT ... UPDATE|DELETE ON <*_log|*_audit> TO arioncomply_app`.
#
# Invocation from operator's Mac:
#   ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
#     cd /data/arioncomply &&
#     git pull &&
#     bash scripts/ops/ship-121-poc-update.sh
#   '

set -euo pipefail

ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
cd "$ARION_ROOT"

if [[ ! -f deploy/install.sh ]]; then
    echo "ERROR: deploy/install.sh missing" >&2
    exit 78
fi

# ── 1. install.sh (re-applies baseline_grants.sql with 121' additions) ──
echo "=== 1. install.sh (re-applies baseline_grants.sql idempotently) ==="
bash deploy/install.sh 2>&1 | tail -20

# ── 2. Restart API ────────────────────────────────────────────────
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

# ── 4. Verify grant shape on ALL 17 audit tables ──────────────────
echo
echo "=== 4. Verify grant shape post-fix (17 tables) ==="
sudo -u postgres psql -d arioncomply_compliance -c "
SELECT table_name, string_agg(privilege_type, ',' ORDER BY privilege_type) AS grants
  FROM information_schema.role_table_grants
 WHERE grantee = 'arioncomply_app'
   AND table_name IN (
     -- Append-only compliance (should be INSERT+SELECT only)
     'posture_status_log', 'applicability_status_log', 'client_facts_log',
     'audit_log', 'confirmation_log', 'deletion_log',
     'cascade_suppression_log', 'client_fact_change_log',
     'external_evidence_verification_log',
     -- Counter-audit (INSERT+SELECT+UPDATE, no DELETE)
     'audit_ledger_download_token',
     -- Diagnostic (INSERT+SELECT+DELETE, no UPDATE)
     'ai_call_log', 'chat_casefile_log', 'chat_consensus_log',
     'fact_recompute_log', 'intake_trace_log',
     'intake_consensus_log', 'request_trace_log'
   )
 GROUP BY table_name ORDER BY table_name;
"

# ── 5. Run regression test (now covers all 17 tables) ─────────────
echo
echo "=== 5. Run tests/test_audit_table_grants.py ==="
PYTHONPATH=. python3 tests/test_audit_table_grants.py

# ── 6. Deployment log tail ────────────────────────────────────────
echo
echo "=== 6. Deployment log — last 3 entries ==="
jq -c . .deployment_log.jsonl | tail -3

echo
echo "=== Ship 121' deployment complete ==="
echo
echo "Coverage: 17 audit tables classified + locked (9 from Ship 120' + 8 from Ship 121')."
echo "Pre-commit guards added on this repo (not deployed to PoC — dev-side only):"
echo "  · blanket GRANT ... ON ALL TABLES ... TO arioncomply_app"
echo "  · schema_v* GRANT UPDATE/DELETE on _log|_audit tables"
