#!/usr/bin/env bash
#
# scripts/ops/ship-123-poc-update.sh
#
# On-VM deployment of Ship 123' — audit-view entry points in the SPA.
# Pure static/arioncomply.html changes; no schema, no code, no data.
#
#   123'.a  "Preview ledger" button in the Auditor packages modal
#           (wires GET /api/v1/admin/audit-ledger — no token minted).
#   123'.b  "Compliance history" Profile section with date picker +
#           "View snapshot" button (wires GET /api/v1/admin/posture-snapshot).
#
# Invocation from operator's Mac:
#   ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
#     cd /data/arioncomply &&
#     git pull &&
#     bash scripts/ops/ship-123-poc-update.sh
#   '

set -euo pipefail

ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
cd "$ARION_ROOT"

# ── 1. install.sh (no schema; will re-apply baseline_grants idempotently) ──
echo "=== 1. install.sh (no schema changes; idempotent re-run) ==="
bash deploy/install.sh 2>&1 | tail -20

# ── 2. Restart API (static/ is served by the same API process) ────
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

# ── 4. Verify JS version marker is the Ship 123' one ──────────────
echo
echo "=== 4. Verify JS version stamp ==="
if curl -sf http://127.0.0.1:8080/ | grep -oE "ARION_JS_VERSION = '[^']+'" | head -1; then
    :
else
    echo "  WARN: version stamp not found in served HTML"
fi

# ── 5. Verify the two new endpoints reach admin-scoped auth ───────
# Both should return 401/403 without api-key (proving they're registered).
echo
echo "=== 5. Endpoint reachability ==="
for path in "/api/v1/admin/audit-ledger" "/api/v1/admin/posture-snapshot?fmt=html"; do
    code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8080$path")
    if [[ "$code" =~ ^(401|403)$ ]]; then
        echo "  $path: $code (registered — expected without api key)"
    else
        echo "  WARN $path: got $code"
    fi
done

# ── 6. Deployment log tail ────────────────────────────────────────
echo
echo "=== 6. Deployment log — last 3 entries ==="
jq -c . .deployment_log.jsonl | tail -3

echo
echo "=== Ship 123' deployment complete ==="
echo
echo "Try in browser via SSH tunnel:"
echo "  ssh -L 8080:127.0.0.1:8080 arionops@10.0.1.85"
echo "  → sign in → Profile"
echo "  → 'Compliance history' section: pick a date + 'View snapshot' → new tab opens"
echo "  → 'Auditor packages' → 'Generate audit package' modal:"
echo "     · fill form → 'Preview ledger' → new tab (no token minted)"
echo "     · fill form → tick acknowledgement → 'Generate URL' → mints token"
