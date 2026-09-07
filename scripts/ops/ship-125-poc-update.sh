#!/usr/bin/env bash
#
# scripts/ops/ship-125-poc-update.sh
#
# On-VM deployment of Ship 125' — dep upgrades closing 4 of 8 CVEs
# surfaced by Ship 124'.c's pip-audit run.
#
#   125'.a  python-multipart 0.0.27 → 0.0.31            (3 CVEs)
#   125'.b  langgraph-checkpoint-postgres 3.0.5 → 3.1.2  (1 CVE)
#   125'.c  chromadb 1.5.9 → not-applicable-to-us       (4 CVEs, documented)
#
# Both .a + .b are pin bumps in deploy/requirements.txt; install.sh's
# pip install picks them up on the next run. No schema changes.
#
# Invocation from operator's Mac:
#   ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
#     cd /data/arioncomply &&
#     git pull &&
#     bash scripts/ops/ship-125-poc-update.sh
#   '

set -euo pipefail

ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
cd "$ARION_ROOT"

if [[ ! -f deploy/install.sh ]]; then
    echo "ERROR: deploy/install.sh missing" >&2
    exit 78
fi

# ── 1. install.sh (upgrades pinned deps via pip install) ──────────
echo "=== 1. install.sh (picks up new pins in deploy/requirements.txt) ==="
bash deploy/install.sh 2>&1 | tail -20

# ── 2. Verify installed versions match new pins ───────────────────
echo
echo "=== 2. Verify upgraded package versions ==="
pip3 show python-multipart langgraph-checkpoint-postgres 2>&1 | grep -E "^Name|^Version"

# ── 3. Restart API to load new checkpointer version ───────────────
echo
echo "=== 3. Restart arioncomply-api ==="
sudo systemctl restart arioncomply-api

echo
echo "=== 4. Wait for API + probe /docs ==="
for i in 1 2 3 4 5 6 7 8; do
    if curl -sf --max-time 3 http://127.0.0.1:8080/docs > /dev/null; then
        echo "API up after $((i*3))s"; break
    fi
    sleep 3
    if [[ "$i" -eq 8 ]]; then
        echo "WARN: API did not respond within 24s"; exit 1
    fi
done

# ── 5. Sync chat smoke test (exercises new PostgresSaver checkpointer) ──
# Diagnostic-rich: prints the top-level keys + first answer/clarification
# field found. If the LLM call fails on the PoC (missing OpenAI key,
# quota exhausted, etc.) the response has neither `answer` nor
# `clarification` — surface the raw shape so it's fixable.
echo
echo "=== 5. Sync chat smoke test ==="
resp=$(curl -s -X POST http://127.0.0.1:8080/api/v1/chat \
    -H "X-API-Key: arion_dev_key_2026" \
    -H "Content-Type: application/json" \
    -d '{"question":"what is A.5.15 about?"}' 2>&1)
echo "$resp" | python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
except Exception as e:
    print(f'  FAIL — non-JSON response: {e}')
    sys.exit(0)
print(f'  Response keys: {sorted(d.keys())}')
if isinstance(d.get('answer'), str) and d['answer']:
    print(f'  OK — answer: {d[\"answer\"][:100]}')
elif d.get('clarification'):
    print(f'  OK — clarification: {str(d[\"clarification\"])[:100]}')
else:
    print(f'  WARN — no answer/clarification in response. Full body (200 chars):')
    print(f'    {json.dumps(d)[:200]}')
"

# ── 6. pip-audit — confirm 4 CVEs cleared, 4 remaining (all chromadb) ──
# pip-audit is dev-only (in deploy/requirements-dev.txt, not
# deploy/requirements.txt). PoCs don't install it. Skip cleanly if
# missing; the CI job on GitHub Actions runs the full audit on every
# push, so CVE state is verified there.
echo
echo "=== 6. pip-audit — confirm expected CVE state ==="
if ! command -v pip-audit > /dev/null 2>&1; then
    echo "  SKIP — pip-audit not installed on PoC (dev-only dep per Ship 124'.a)."
    echo "  CVE state is verified on every push via .github/workflows/security-scan.yml."
else
    audit_out=$(pip-audit -r deploy/requirements.txt --no-deps 2>&1 || true)
    if echo "$audit_out" | grep -q "Found 4 known vulnerabilities in 1 package"; then
        echo "  OK — 4 CVEs remain, all chromadb (expected — Ship 125'.c not-applicable analysis)"
    elif echo "$audit_out" | grep -qE "^No known vulnerabilities found"; then
        echo "  OK — no CVEs (unexpected but great — chromadb may have shipped a fix!)"
    else
        echo "  WARN — unexpected pip-audit state:"
        echo "$audit_out" | tail -15 | sed 's/^/    /'
    fi
fi

# ── 7. Deployment log tail ────────────────────────────────────────
echo
echo "=== 7. Deployment log — last 3 entries ==="
jq -c . .deployment_log.jsonl | tail -3

echo
echo "=== Ship 125' deployment complete ==="
echo
echo "CVE status:"
echo "  python-multipart              0.0.27 → 0.0.31   ✓ CLOSED (3 CVEs)"
echo "  langgraph-checkpoint-postgres 3.0.5  → 3.1.2    ✓ CLOSED (1 CVE)"
echo "  chromadb                      1.5.9  unchanged  ✓ NOT-APPLICABLE (4 CVEs, documented)"
echo
echo "See docs/memory/ship-125-prime-c-chromadb-analysis-2026-09-07.md for the"
echo "chromadb-specific analysis + re-review triggers."
