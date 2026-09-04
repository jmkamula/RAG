#!/usr/bin/env bash
#
# scripts/ops/ship-113-poc-update.sh
#
# On-VM deployment of Ship 113' (de-jargonized Profile scoping +
# region multi-select + sector controlled vocab + 3-bucket size).
# Runs directly on the customer box AS arionops (or whoever has
# passwordless sudo to postgres + systemd on that host).
#
# Invocation from operator's Mac:
#   ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
#     cd /data/arioncomply &&
#     git pull &&
#     bash scripts/ops/ship-113-poc-update.sh
#   '
#
# What this script does:
#   1. bash deploy/install.sh              — applies schema_v113
#   2. systemctl restart arioncomply-api   — pick up new code
#   3. Health probe + 5 verification queries specific to Ship 113'
#
# What this script does NOT do:
#   · git pull — the operator's SSH block does that before invoking
#     this script (it needs to happen BEFORE this script is available
#     the first time). Follows the Ship 111'.d "the script is in git"
#     principle: git pull fetches the script; the script does the
#     work.
#
# Per-arc script convention (see docs/deployments/README.md):
#   Each shipped arc that needs PoC deployment gets its own
#   scripts/ops/ship-N-poc-update.sh. Verification block is arc-
#   specific — Ship 113' checks region cols + size bucket + sector
#   vocab; the next arc's script checks whatever that arc introduces.

set -euo pipefail

# ── Guards ───────────────────────────────────────────────────────
ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
cd "$ARION_ROOT"

if [[ ! -f deploy/install.sh ]]; then
    echo "ERROR: deploy/install.sh missing — is this the arioncomply repo?" >&2
    exit 78
fi

# ── 1. install.sh (applies schema_v113 idempotently) ─────────────
# NO `sudo` prefix — install.sh line 108 explicitly rejects EUID=0
# and uses `sudo -u postgres` / `sudo systemctl` internally for what
# needs root. Ship 111'.a canonicalized this pattern.
echo "=== 1. install.sh (applies schema_v113 idempotently) ==="
bash deploy/install.sh 2>&1 | tail -25

# ── 2. Restart API ───────────────────────────────────────────────
echo
echo "=== 2. Restart arioncomply-api ==="
sudo systemctl restart arioncomply-api

# ── 3. Wait for API + probe ──────────────────────────────────────
echo
echo "=== 3. Wait for API + probe /docs ==="
for i in 1 2 3 4 5 6 7 8; do
    if curl -sf --max-time 3 http://127.0.0.1:8080/docs > /dev/null; then
        echo "API up after $((i*3))s"
        break
    fi
    sleep 3
    if [[ "$i" -eq 8 ]]; then
        echo "WARN: API did not respond within 24s"
        echo "  Check: journalctl -u arioncomply-api -n 100 --no-pager"
        exit 1
    fi
done

# ── 4. Verify schema_v113 applied ────────────────────────────────
echo
echo "=== 4. Verify schema_v113 applied ==="
sudo -u postgres psql -d arioncomply_compliance -tAc \
    "SELECT version FROM schema_migrations
      WHERE version = 'schema_v113_client_facts_regions_and_size_bucket'"

# ── 5. Verify new client_facts columns present ───────────────────
echo
echo "=== 5. Verify new client_facts columns present ==="
sudo -u postgres psql -d arioncomply_compliance -c \
    "SELECT column_name, data_type
       FROM information_schema.columns
      WHERE table_name = 'client_facts'
        AND column_name IN ('us_data_subjects','ca_data_subjects',
                            'apac_data_subjects','other_data_subjects',
                            'employee_size_bucket')
      ORDER BY column_name;"

# ── 6. Current tenant client_facts region state ──────────────────
echo
echo "=== 6. Current tenant client_facts region state ==="
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

# ── 7. Deployment log tail ───────────────────────────────────────
echo
echo "=== 7. Deployment log — last 3 entries ==="
if [[ -f .deployment_log.jsonl ]]; then
    jq -c . .deployment_log.jsonl | tail -3
else
    echo "(no deployment log yet — first Ship 111'.d deploy)"
fi

# ── 8. Ship 113' scoping_vocab shape check ───────────────────────
# Uses the admin API key if present in .env (Ship 111'.a stashed
# ARION_OWNER_PW but not necessarily ARION_DEV_API_KEY). Skip if
# no key is available; UI spot-check covers this anyway.
echo
echo "=== 8. GET /profile scoping_vocab shape ==="
API_KEY=""
if [[ -f .env ]]; then
    API_KEY=$(grep -E '^ARION_DEV_API_KEY=' .env 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"' || true)
fi
if [[ -n "$API_KEY" ]]; then
    curl -sf http://127.0.0.1:8080/api/v1/tenant/profile \
         -H "X-API-Key: $API_KEY" \
    | python3 -c "
import sys, json
d = json.load(sys.stdin)
v = d.get('scoping_vocab', {})
print(f'  regions[]:      {len(v.get(\"regions\", []))} entries (expected 6)')
print(f'  sectors[]:      {len(v.get(\"sectors\", []))} entries (expected 21)')
print(f'  size buckets:   {len(v.get(\"employee_size_buckets\", []))} entries (expected 3)')
" || echo "  (vocab probe failed — non-critical)"
else
    echo "  (skipped — no ARION_DEV_API_KEY in .env; spot-check via UI instead)"
fi

echo
echo "=== Ship 113' deployment complete ==="
echo
echo "Next steps:"
echo "  · Update docs/deployments/arionlabs-dr-01.md — flip Ship 113'.e row to GREEN"
echo "  · Open the UI via SSH tunnel (ssh -L 8080:127.0.0.1:8080 arionops@10.0.1.85)"
echo "    and verify Profile → About your organisation renders 12 questions"
echo "    in 4 groups with the new region multi-select + size radio + sector dropdown"
