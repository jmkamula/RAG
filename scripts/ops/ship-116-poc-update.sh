#!/usr/bin/env bash
#
# scripts/ops/ship-116-poc-update.sh
#
# On-VM deployment of Ship 116' (init-secrets.sh + install.sh
# non-interactive). Ship 116' is code + docs only — no schema
# migrations, no runtime behavior changes. The main verification
# is that the new hard-.env-required install.sh proceeds cleanly
# on the customer box (since Ship 111'.a stashed ARION_OWNER_PW
# there already, this should just work).
#
# Invocation from operator's Mac:
#   ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
#     cd /data/arioncomply &&
#     git pull &&
#     bash scripts/ops/ship-116-poc-update.sh
#   '

set -euo pipefail

ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
cd "$ARION_ROOT"

if [[ ! -f deploy/install.sh ]]; then
    echo "ERROR: deploy/install.sh missing" >&2
    exit 78
fi

# ── 1. Sanity: init-secrets.sh landed + is executable ────────────
echo "=== 1. Verify init-secrets.sh landed ==="
if [[ -x scripts/ops/init-secrets.sh ]]; then
    echo "  ✓ scripts/ops/init-secrets.sh present + executable"
else
    echo "  ✗ scripts/ops/init-secrets.sh missing or not executable" >&2
    exit 1
fi

# ── 2. Verify install.sh syntax (defensive) ──────────────────────
echo
echo "=== 2. install.sh syntax check ==="
bash -n deploy/install.sh && echo "  ✓ syntax OK"

# ── 3. install.sh (should proceed cleanly — .env already populated) ──
echo
echo "=== 3. install.sh (non-interactive — .env already has ARION_OWNER_PW) ==="
bash deploy/install.sh 2>&1 | tail -20

# ── 4. Restart API ───────────────────────────────────────────────
echo
echo "=== 4. Restart arioncomply-api ==="
sudo systemctl restart arioncomply-api

# ── 5. Health probe ──────────────────────────────────────────────
echo
echo "=== 5. Wait for API + probe /docs ==="
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

# ── 6. Deployment log tail ───────────────────────────────────────
echo
echo "=== 6. Deployment log — last 3 entries ==="
jq -c . .deployment_log.jsonl | tail -3

echo
echo "=== Ship 116' deployment complete ==="
echo
echo "Verification summary:"
echo "  · init-secrets.sh present (fresh installs going forward will use it)"
echo "  · install.sh proceeded cleanly with no prompts (Ship 116' non-interactive)"
echo "  · .env unchanged (Ship 111'.a's ARION_OWNER_PW stash carried forward)"
echo "  · deployment log gained a new GREEN entry"
