#!/usr/bin/env bash
#
# scripts/ops/ship-113-poc-update.sh
#
# One-command deployment of Ship 113' (de-jargonized Profile scoping
# + region multi-select + sector controlled vocab + 3-bucket size)
# to the arionlabs-dr-01 PoC. Runs from the operator's Mac.
#
# Usage:
#   bash scripts/ops/ship-113-poc-update.sh
#
# Env overrides:
#   ARION_POC_SSH_TARGET  — SSH target (default: arionops@10.0.1.85)
#   ARION_POC_SSH_KEY     — Path to SSH key (default: ~/.ssh/arion_operator_ed25519)
#
# What runs on the customer VM:
#   1. git pull                     — fetch latest code
#   2. bash deploy/install.sh       — applies schema_v113 idempotently
#   3. systemctl restart arioncomply-api  — pick up new code
#   4. Health probe + verification queries for Ship 113' columns
#
# Why per-arc script (not a generic update.sh):
#   · Each arc's verification block is different (new columns, new
#     rows, new endpoints to spot-check). Baking arc-specific
#     checks into a generic runner makes it hard to reason about.
#   · The script IS the documentation for what this arc changes at
#     deploy time. Reads as a runbook.
#   · Failure mode is obvious: if THIS arc's script fails, next arc's
#     script picks up where this one left off.

set -euo pipefail

# ── SSH config ───────────────────────────────────────────────────
: "${ARION_POC_SSH_TARGET:=arionops@10.0.1.85}"
: "${ARION_POC_SSH_KEY:=$HOME/.ssh/arion_operator_ed25519}"

# Sanity: warn if the SSH key file doesn't exist.
if [[ ! -f "$ARION_POC_SSH_KEY" ]]; then
    echo "ERROR: SSH key not found: $ARION_POC_SSH_KEY" >&2
    echo "  Set ARION_POC_SSH_KEY to the correct path if different." >&2
    exit 1
fi

echo "=== Ship 113' PoC update ==="
echo "  target: $ARION_POC_SSH_TARGET"
echo "  key:    $ARION_POC_SSH_KEY"
echo

# Everything below runs on the customer VM in a single SSH session.
# `set -e` inside the remote block halts on any step failure.
ssh -i "$ARION_POC_SSH_KEY" "$ARION_POC_SSH_TARGET" bash -s <<'REMOTE'
set -euo pipefail
cd /data/arioncomply

echo "=== 1. git pull ==="
git pull --ff-only 2>&1 | tail -5

echo
echo "=== 2. install.sh (applies schema_v113 idempotently) ==="
# NOTE: no `sudo` prefix — install.sh line 108 rejects EUID=0 and
# uses `sudo -u postgres` / `sudo systemctl` internally for what
# needs root. Ship 111'.a canonicalized this pattern.
bash deploy/install.sh 2>&1 | tail -25

echo
echo "=== 3. Restart API to pick up new code ==="
sudo systemctl restart arioncomply-api

echo
echo "=== 4. Wait for API + probe /docs ==="
for i in 1 2 3 4 5 6 7 8; do
  if curl -sf --max-time 3 http://127.0.0.1:8080/docs > /dev/null; then
    echo "API up after $((i*3))s"; break
  fi
  sleep 3
  if [[ "$i" -eq 8 ]]; then
    echo "WARN: API did not respond within 24s — check journalctl -u arioncomply-api -n 100"
    exit 1
  fi
done

echo
echo "=== 5. Verify schema_v113 applied ==="
sudo -u postgres psql -d arioncomply_compliance -tAc \
    "SELECT version FROM schema_migrations
      WHERE version = 'schema_v113_client_facts_regions_and_size_bucket'"

echo
echo "=== 6. Verify new client_facts columns present ==="
sudo -u postgres psql -d arioncomply_compliance -c \
    "SELECT column_name, data_type
       FROM information_schema.columns
      WHERE table_name = 'client_facts'
        AND column_name IN ('us_data_subjects','ca_data_subjects',
                            'apac_data_subjects','other_data_subjects',
                            'employee_size_bucket')
      ORDER BY column_name;"

echo
echo "=== 7. Verify current tenant client_facts region state ==="
sudo -u postgres psql -d arioncomply_compliance -c \
    "SELECT t.name,
            cf.eu_data_subjects   AS eu,
            cf.uk_data_subjects   AS uk,
            cf.us_data_subjects   AS us,
            cf.ca_data_subjects   AS ca,
            cf.apac_data_subjects AS apac,
            cf.other_data_subjects AS other,
            cf.employee_size_bucket AS size,
            cf.sector
       FROM client_facts cf JOIN tenants t ON t.id = cf.tenant_id
      WHERE t.is_active;"

echo
echo "=== 8. Deployment log — last 3 entries ==="
if [[ -f .deployment_log.jsonl ]]; then
    jq -c . .deployment_log.jsonl | tail -3
else
    echo "(no deployment log yet — first Ship 111'.d deploy)"
fi

echo
echo "=== 9. GET /profile scoping_vocab check ==="
# Requires the admin API key. Read from .env silently — no output.
API_KEY=""
if [[ -f .env ]]; then
    # Look for any api key in .env. If none, skip the vocab probe.
    API_KEY=$(grep -E '^ARION_DEV_API_KEY=' .env 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"' || true)
fi
if [[ -n "$API_KEY" ]]; then
    curl -sf http://127.0.0.1:8080/api/v1/tenant/profile \
         -H "X-API-Key: $API_KEY" \
    | python3 -c "
import sys, json
d = json.load(sys.stdin)
v = d.get('scoping_vocab', {})
print(f'  regions[]: {len(v.get(\"regions\", []))} entries (expected 6)')
print(f'  sectors[]: {len(v.get(\"sectors\", []))} entries (expected 21)')
print(f'  size buckets: {len(v.get(\"employee_size_buckets\", []))} entries (expected 3)')
" || echo "  (vocab probe failed — non-critical)"
else
    echo "  (skipped — no ARION_DEV_API_KEY in .env; use UI or /admin/derive-applicability to spot-check)"
fi

echo
echo "=== Ship 113' deployment complete ==="
REMOTE

echo
echo "=== Next steps ==="
echo "  · Update docs/deployments/arionlabs-dr-01.md — flip the Ship 113'.e row to GREEN"
echo "  · Open the UI (SSH tunnel: ssh -L 8080:127.0.0.1:8080 $ARION_POC_SSH_TARGET) and verify:"
echo "      - Profile → About your organisation has 12 questions in 4 groups"
echo "      - Q2 is a 6-checkbox region multi-select"
echo "      - Q11 (size) is a 3-option radio"
echo "      - Q12 (sector) is a grouped dropdown"
echo "      - Quickstart has no sector field (open a fresh tenant to see this)"
