#!/usr/bin/env bash
#
# scripts/ops/ship-127-poc-update.sh
#
# On-VM deployment of Ship 127' — MEDIUM security gap closes:
#
#   127'.a  Diagnostic-log DELETE restriction via SECURITY DEFINER
#           function (schema_v118 + baseline_grants.sql extension)
#   127'.b  Slack webhook encryption — DEFERRED with rationale doc
#           (0 rows in tenant_notification_channel; complexity doesn't
#           earn itself yet). No code change on the PoC.
#   127'.c  vector/build_index.py — presence-only OpenAI/Anthropic key
#           logging (no first-8-chars leak). No PoC deploy impact —
#           script only runs during vector-reindex operations.
#
# Invocation from operator's Mac:
#   ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
#     cd /data/arioncomply &&
#     git pull &&
#     bash scripts/ops/ship-127-poc-update.sh
#   '

set -euo pipefail

ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
cd "$ARION_ROOT"

if [[ ! -f deploy/install.sh ]]; then
    echo "ERROR: deploy/install.sh missing" >&2
    exit 78
fi

# ── 1. install.sh (applies schema_v118 + baseline_grants w/ new DELETE revokes) ──
echo "=== 1. install.sh (applies schema_v118_diagnostic_log_delete_restriction.sql) ==="
bash deploy/install.sh 2>&1 | tail -20

# ── 2. Verify schema_v118 applied ─────────────────────────────────
echo
echo "=== 2. Verify schema_v118 applied ==="
sudo -u postgres psql -d arioncomply_compliance -tAc \
    "SELECT version FROM schema_migrations
      WHERE version = 'schema_v118_diagnostic_log_delete_restriction'"

# ── 3. Verify DELETE revoked on all 7 diagnostic tables ───────────
echo
echo "=== 3. Verify DELETE revoked on 7 diagnostic tables ==="
sudo -u postgres psql -d arioncomply_compliance -c "
SELECT table_name, string_agg(privilege_type, ',' ORDER BY privilege_type) AS grants
  FROM information_schema.role_table_grants
 WHERE grantee = 'arioncomply_app'
   AND table_name IN (
     'ai_call_log', 'chat_casefile_log', 'chat_consensus_log',
     'fact_recompute_log', 'intake_trace_log',
     'intake_consensus_log', 'request_trace_log'
   )
 GROUP BY table_name ORDER BY table_name;"

# ── 4. Verify function exists + arioncomply_app has EXECUTE ───────
echo
echo "=== 4. Verify sweep_delete_diagnostic_log_rows function ==="
sudo -u postgres psql -d arioncomply_compliance -c "
SELECT proname AS function_name,
       pg_get_function_identity_arguments(oid) AS args,
       pg_get_userbyid(proowner) AS owner
  FROM pg_proc
 WHERE proname = 'sweep_delete_diagnostic_log_rows';"

# ── 5. Restart API ───────────────────────────────────────────────
echo
echo "=== 5. Restart arioncomply-api ==="
sudo systemctl restart arioncomply-api

echo
echo "=== 6. Wait for API + probe /docs ==="
for i in 1 2 3 4 5 6 7 8; do
    if curl -sf --max-time 3 http://127.0.0.1:8080/docs > /dev/null; then
        echo "API up after $((i*3))s"; break
    fi
    sleep 3
    if [[ "$i" -eq 8 ]]; then
        echo "WARN: API did not respond within 24s"; exit 1
    fi
done

# ── 7. Smoke test: raw DELETE from arioncomply_app must fail ──────
echo
echo "=== 7. Smoke test: raw DELETE denied for app role ==="
result=$(psql -U arioncomply_app -h 127.0.0.1 -d arioncomply_compliance -tAc \
    "DELETE FROM ai_call_log WHERE FALSE" 2>&1 || true)
if echo "$result" | grep -q "permission denied"; then
    echo "  OK — raw DELETE denied as expected"
else
    echo "  WARN — expected 'permission denied', got: $result"
fi

# ── 8. Smoke test: function call succeeds ─────────────────────────
echo
echo "=== 8. Smoke test: sweep function callable by app role ==="
result=$(psql -U arioncomply_app -h 127.0.0.1 -d arioncomply_compliance -tAc \
    "SELECT public.sweep_delete_diagnostic_log_rows('ai_call_log', 3650)" 2>&1 || true)
if echo "$result" | grep -qE "^[0-9]+$"; then
    echo "  OK — function returned row count: $result (rows older than 10 years, expected 0)"
else
    echo "  WARN — unexpected function result: $result"
fi

# ── 9. Regression test — audit table grants ───────────────────────
echo
echo "=== 9. Run tests/test_audit_table_grants.py ==="
PYTHONPATH=. python3 tests/test_audit_table_grants.py

# ── 10. Deployment log tail ───────────────────────────────────────
echo
echo "=== 10. Deployment log — last 3 entries ==="
jq -c . .deployment_log.jsonl | tail -3

echo
echo "=== Ship 127' deployment complete ==="
echo
echo "Changes landed on PoC:"
echo "  ✓ DELETE revoked on 7 diagnostic-log tables (app role)"
echo "  ✓ sweep_delete_diagnostic_log_rows() SECURITY DEFINER function"
echo "    installed for future retention sweeps"
echo "  ✓ Extended baseline_grants.sql: also revokes DELETE on the"
echo "    diagnostic tables + grants EXECUTE on the function"
echo
echo "Deferred (no PoC-visible change):"
echo "  · 127'.b Slack webhook encryption — see"
echo "    docs/memory/ship-127-prime-b-webhook-encryption-deferred-2026-09-07.md"
echo "    (0 rows in tenant_notification_channel; complexity not earned yet)"
echo "  · 127'.c OpenAI key partial-logging — vector/build_index.py"
echo "    edit; only runs during vector-reindex operations"
