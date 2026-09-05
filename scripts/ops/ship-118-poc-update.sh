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
# Without doing this, applicability_status_log would be empty until
# the next fact PUT + snapshot would report "no history" for controls
# that flipped previously. Idempotent — re-firing a rule with same
# result no-ops (Ship 118'.b Lesson 215).
#
# Ship 118'.d: prefer the direct-DB utility (uses ARION_OWNER_PW,
# always present since Ship 111'.a) over the HTTP endpoint (which
# needs an ARION_DEV_API_KEY that may not be stashed on every box).
echo
echo "=== 6. Trigger derive-applicability sweep (populates log) ==="
# Ship 118'.d fix: check -f (exists), not -x (executable). Python
# files pulled via git don't get the executable bit — they're
# invoked as `python3 script.py` not `./script.py`.
if [[ -f scripts/dev/trigger_applicability_sweep.py ]]; then
    set -a; source .env; set +a
    PYTHONPATH=. python3 scripts/dev/trigger_applicability_sweep.py \
    || echo "  (sweep utility failed — non-critical, next fact PUT will populate the log)"
else
    echo "  (scripts/dev/trigger_applicability_sweep.py not present — skipping;"
    echo "   log will populate on next fact PUT)"
fi

# ── 7. Row counts in the new tables ──────────────────────────────
echo
echo "=== 7. Audit table row counts ==="
sudo -u postgres psql -d arioncomply_compliance -c \
    "SELECT 'applicability_status_log' AS tbl, COUNT(*) FROM applicability_status_log
     UNION ALL
     SELECT 'client_facts_log', COUNT(*) FROM client_facts_log;"

# ── 8. Snapshot smoke test (direct-DB, no API key needed) ────────
# Ship 118'.d — use the direct-DB path here too, matching the step 6
# pattern. Calls snapshot_posture() from a small inline Python block,
# same code as the HTTP endpoint. No ARION_DEV_API_KEY required.
echo
echo "=== 8. Snapshot smoke test (current, all active tenants) ==="
set -a; source .env; set +a
PYTHONPATH=. python3 <<'PYEOF' || echo "  (snapshot smoke test failed — non-critical)"
import os, sys
from urllib.parse import unquote, urlparse
from collections import Counter
import psycopg2
from rag.posture.snapshot import snapshot_posture

u = urlparse(os.environ["DATABASE_URL"])
conn = psycopg2.connect(
    host=u.hostname, port=u.port or 5432, user="arioncomply",
    password=os.getenv("ARION_OWNER_PW") or unquote(u.password or ""),
    dbname=(u.path or "/arioncomply_compliance").lstrip("/"),
)
with conn.cursor() as cur:
    cur.execute("SELECT id::text, name FROM tenants WHERE is_active ORDER BY created_at")
    tenants = cur.fetchall()

for tid, name in tenants:
    snap = snapshot_posture(conn, tid)
    by_f = Counter(c.finding for c in snap.controls)
    cov_app  = snap.coverage_notes["applicability_status"]["coverage"]
    cov_scop = snap.coverage_notes["scoping_facts"]["coverage"]
    print(f"  {name!r}: {snap.control_count} controls  findings={dict(by_f)}")
    print(f"    coverage: applicability={cov_app}  scoping={cov_scop}")
conn.close()
PYEOF

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
