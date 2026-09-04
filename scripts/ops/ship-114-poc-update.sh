#!/usr/bin/env bash
#
# scripts/ops/ship-114-poc-update.sh
#
# On-VM deployment of Ship 114' (region backfill for pre-Ship-113'
# tenants + sector CHECK constraint + strict API sector validation).
#
# Invocation from operator's Mac:
#   ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
#     cd /data/arioncomply &&
#     git pull &&
#     bash scripts/ops/ship-114-poc-update.sh
#   '
#
# Order matters:
#   1. install.sh applies schema_v114 (backfills legacy sector free-
#      text values to canonical codes THEN adds CHECK constraint).
#   2. Restart API to pick up strict sector validation code.
#   3. Run backfill_region_facts script to fix Arion Networks s.r.o.
#      (country="Czechia" → "CZ" + eu_data_subjects=TRUE derived).
#   4. Verification queries.

set -euo pipefail

ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
cd "$ARION_ROOT"

if [[ ! -f deploy/install.sh ]]; then
    echo "ERROR: deploy/install.sh missing" >&2
    exit 78
fi

# ── 1. install.sh (applies schema_v114 idempotently) ─────────────
# schema_v114:
#   · Backfills known legacy sector free-text values → canonical
#   · Residual unknown values → NULL (tenant re-picks via dropdown)
#   · Adds CHECK constraint on client_facts.sector
echo "=== 1. install.sh (applies schema_v114 idempotently) ==="
bash deploy/install.sh 2>&1 | tail -25

# ── 2. Restart API to pick up strict sector validation ───────────
echo
echo "=== 2. Restart arioncomply-api ==="
sudo systemctl restart arioncomply-api

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
        exit 1
    fi
done

# ── 4. Region backfill for pre-Ship-113' tenants ─────────────────
# Idempotent — only touches tenants whose region cols are all at
# default. On arionlabs-dr-01 this will fix Arion Networks s.r.o.'s
# country="Czechia" → "CZ" + eu_data_subjects=TRUE. On boxes where
# every tenant already has region facts declared, it's a no-op.
echo
echo "=== 4. Region backfill (fixes country + region for pre-113 tenants) ==="
PYTHONPATH=. python3 scripts/dev/backfill_region_facts_for_existing_tenants.py

# ── 5. Verify schema_v114 applied + CHECK constraint present ─────
echo
echo "=== 5. Verify schema_v114 applied ==="
sudo -u postgres psql -d arioncomply_compliance -tAc \
    "SELECT version FROM schema_migrations
      WHERE version = 'schema_v114_sector_backfill_and_check'"

echo
echo "=== 6. Verify CHECK constraint on client_facts.sector ==="
sudo -u postgres psql -d arioncomply_compliance -tAc \
    "SELECT conname FROM pg_constraint
      WHERE conname = 'client_facts_sector_check'"

# ── 7. Current tenant client_facts state ─────────────────────────
echo
echo "=== 7. Current tenant client_facts state ==="
sudo -u postgres psql -d arioncomply_compliance -c \
    "SELECT t.name,
            cf.country,
            cf.eu_data_subjects   AS eu,
            cf.uk_data_subjects   AS uk,
            cf.us_data_subjects   AS us,
            cf.ca_data_subjects   AS ca,
            cf.apac_data_subjects AS apac,
            cf.other_data_subjects AS other,
            cf.sector,
            cf.fact_source ? 'sector'           AS sector_declared,
            cf.fact_source ? 'eu_data_subjects' AS eu_declared
       FROM client_facts cf JOIN tenants t ON t.id = cf.tenant_id
      WHERE t.is_active;"

# ── 8. Deployment log tail ───────────────────────────────────────
echo
echo "=== 8. Deployment log — last 3 entries ==="
if [[ -f .deployment_log.jsonl ]]; then
    jq -c . .deployment_log.jsonl | tail -3
else
    echo "(no deployment log yet)"
fi

echo
echo "=== Ship 114' deployment complete ==="
echo
echo "Next steps:"
echo "  · Update docs/deployments/arionlabs-dr-01.md — flip Ship 114'.d row to GREEN"
echo "  · Optional UI check: Profile → sector dropdown should show tenant's canonical value pre-selected"
echo "                       (e.g. Arion's IT Consulting → 'ICT services' in the dropdown)"
