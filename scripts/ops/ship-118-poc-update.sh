#!/usr/bin/env bash
#
# scripts/ops/ship-118-poc-update.sh
#
# On-VM deployment of Ship 118' — point-in-time posture reconstruction.
# Three sub-arcs:
#   118'.a  snapshot function + admin endpoint (JSON + CSV)
#   118'.b  schema_v115 audit tables (applicability_status_log +
#           client_facts_log) + writers wired
#   118'.c  print-optimised HTML render (browser Save-as-PDF workflow)
#
# Invocation from operator's Mac:
#   ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
#     cd /data/arioncomply &&
#     git pull &&
#     bash scripts/ops/ship-118-poc-update.sh
#   '

set -euo pipefail

ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
cd "$ARION_ROOT"

if [[ ! -f deploy/install.sh ]]; then
    echo "ERROR: deploy/install.sh missing" >&2
    exit 78
fi

# ── 1. install.sh (applies schema_v115) ──────────────────────────
echo "=== 1. install.sh (applies schema_v115 idempotently) ==="
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

# ── 4. Verify schema_v115 applied + tables present ───────────────
echo
echo "=== 4. Verify schema_v115 applied ==="
sudo -u postgres psql -d arioncomply_compliance -tAc \
    "SELECT version FROM schema_migrations
      WHERE version = 'schema_v115_applicability_and_scoping_history'"

echo
echo "=== 5. Verify audit tables exist ==="
sudo -u postgres psql -d arioncomply_compliance -c \
    "SELECT table_name FROM information_schema.tables
      WHERE table_name IN ('applicability_status_log', 'client_facts_log')
      ORDER BY table_name;"

# ── 6. Trigger derive-applicability so the log gets its first rows ──
# Without doing this, applicability_status_log would be empty and the
# snapshot's HTML would report "no history" for controls that flipped
# yesterday. Idempotent — re-firing a rule with same result no-ops.
echo
echo "=== 6. Trigger derive-applicability sweep (populates log) ==="
# Use an api key if one exists in .env; otherwise skip and note.
API_KEY=""
if [[ -f .env ]]; then
    API_KEY=$(grep -E '^ARION_DEV_API_KEY=' .env 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"' || true)
fi
if [[ -n "$API_KEY" ]]; then
    curl -sf -X POST http://127.0.0.1:8080/api/v1/admin/derive-applicability \
        -H "X-API-Key: $API_KEY" \
    | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"  rules_fired: {d['rules_fired']}\")
print(f\"  controls_cleared: {d['controls_cleared']}, controls_na_set: {d['controls_na_set']}\")
" || echo "  (derive call failed — non-critical, next fact PUT will populate the log)"
else
    echo "  (skipped — no ARION_DEV_API_KEY in .env; log populates on next fact PUT)"
fi

# ── 7. Row counts in the new tables ──────────────────────────────
echo
echo "=== 7. Audit table row counts ==="
sudo -u postgres psql -d arioncomply_compliance -c \
    "SELECT 'applicability_status_log' AS tbl, COUNT(*) FROM applicability_status_log
     UNION ALL
     SELECT 'client_facts_log', COUNT(*) FROM client_facts_log;"

# ── 8. Snapshot smoke test ───────────────────────────────────────
echo
echo "=== 8. Snapshot smoke test (JSON, current) ==="
if [[ -n "$API_KEY" ]]; then
    curl -sf "http://127.0.0.1:8080/api/v1/admin/posture-snapshot" \
        -H "X-API-Key: $API_KEY" \
    | python3 -c "
import sys, json
d = json.load(sys.stdin)
from collections import Counter
by_f = Counter(c['finding'] for c in d['controls'])
print(f\"  as_of: {d['as_of']}  controls: {d['control_count']}\")
print(f\"  findings: {dict(by_f)}\")
cov = d['coverage_notes']
print(f\"  applicability coverage: {cov['applicability_status']['coverage']}\")
print(f\"  scoping       coverage: {cov['scoping_facts']['coverage']}\")
"
else
    echo "  (skipped — no admin key available; spot-check via UI)"
fi

# ── 9. Deployment log tail ───────────────────────────────────────
echo
echo "=== 9. Deployment log — last 3 entries ==="
jq -c . .deployment_log.jsonl | tail -3

echo
echo "=== Ship 118' deployment complete ==="
echo
echo "Try in browser via SSH tunnel:"
echo "  ssh -L 8080:127.0.0.1:8080 arionops@10.0.1.85"
echo "  http://localhost:8080/api/v1/admin/posture-snapshot?fmt=html  (needs X-API-Key header)"
echo "  http://localhost:8080/api/v1/admin/posture-snapshot?fmt=html&as_of=2026-05-01"
echo
echo "  Browser 'Save as PDF' produces the auditor-ready artifact."
