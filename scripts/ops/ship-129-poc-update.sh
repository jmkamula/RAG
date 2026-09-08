#!/usr/bin/env bash
#
# scripts/ops/ship-129-poc-update.sh
#
# On-VM deployment of Ship 129' — discovery-vs-surfacing separation.
#
#   129'.a  Stage-1 queue subscription filter — list_queue +
#           list_pending_for_control INNER JOIN tenant_standards. Out-
#           of-scope findings stay in document_findings but no longer
#           surface in the worklist. Instant-flip on enrolment: adding
#           a tenant_standards row immediately unblocks the join.
#
#   129'.b  Stage-2 queue subscription filter — same shape on
#           list_pending_proposals + get_proposal_for_control.
#
#   129'.c  Chat xfw bridge footer respects subscription — case-file
#           digest (_render_xfw_bridges) + preservation
#           (_build_bridge_footer) drop bridges to non-enrolled
#           frameworks. Together with framework_scope_guard (already
#           enrolment-aware) closes the last surface where a non-
#           enrolled framework ref could leak into chat output.
#
#   129'.d  Enrolment-nudge notification kind
#           `unenrolled_framework_applicable`. New sweep work_type
#           `enrolment_nudge` fires when jurisdiction facts
#           (client_facts) indicate a framework is applicable but not
#           enrolled. Discovery-count enriches body; jurisdiction is
#           the trigger. Ships 2 rules today (GDPR + ISO 27701).
#
# Schema: v119 — adds allowlist entry for new notification kind + new
# sweep work_type (+ fixes pre-existing CHECK drift on posture_refresh
# + cite_attestation_retention that had never made it into the CHECK).
#
# Invocation from operator's Mac:
#   ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
#     cd /data/arioncomply &&
#     git pull &&
#     bash scripts/ops/ship-129-poc-update.sh
#   '

set -euo pipefail

ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
cd "$ARION_ROOT"

# Load .env so PGPASSWORD / DATABASE_URL / etc. are available to the
# sweep + regression tests run below. install.sh's environment doesn't
# propagate to a fresh bash invocation via SSH.
if [[ -f .env ]]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

if [[ ! -f deploy/install.sh ]]; then
    echo "ERROR: deploy/install.sh missing" >&2
    exit 78
fi

# ── 1. install.sh runs schema_v119 automatically via migration loop ──
echo "=== 1. install.sh (applies schema_v119 + refreshes code) ==="
bash deploy/install.sh 2>&1 | tail -20

# ── 2. Restart API to load Stage-1/Stage-2/casefile fixes ────────
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

# ── 4. Verify schema_v119 landed — CHECK constraints ─────────────
echo
echo "=== 4. Verify tenant_notification_kind_check has the new value ==="
sudo -u postgres psql -d arioncomply_compliance -c \
"SELECT conname FROM pg_constraint
  WHERE conname = 'tenant_notification_kind_check';" 2>&1
sudo -u postgres psql -d arioncomply_compliance -c \
"SELECT 'unenrolled_framework_applicable=' ||
   CASE WHEN pg_get_constraintdef(oid)
             LIKE '%unenrolled_framework_applicable%'
        THEN 'PRESENT' ELSE 'MISSING' END AS check_status
   FROM pg_constraint
  WHERE conname = 'tenant_notification_kind_check';" 2>&1

echo
echo "=== 5. Dry-run the enrolment_nudge sweep to confirm wiring ==="
PYTHONPATH="$ARION_ROOT" python3 -m rag.scheduler.tick \
    --work enrolment_nudge --dry-run --json 2>&1 | tail -5

# ── 6. Regression tests (Stage-1 filter + xfw enrolment + nudge) ─
echo
echo "=== 6. Run Ship 129' regression tests ==="
PYTHONPATH="$ARION_ROOT" python3 tests/test_stage_queue_subscription_filter.py \
    2>&1 | tail -8
echo
PYTHONPATH="$ARION_ROOT" python3 tests/test_casefile_enrolment_filter.py \
    2>&1 | tail -8
echo
PYTHONPATH="$ARION_ROOT" python3 tests/test_enrolment_nudge.py \
    2>&1 | tail -8

# ── 7. Show live current-tenant queue counts ────────────────────
echo
echo "=== 7. Live Stage-1 queue per tenant (post-filter) ==="
sudo -u postgres psql -d arioncomply_compliance -c \
"WITH filtered AS (
   SELECT df.tenant_id, df.standard_id,
          count(DISTINCT COALESCE(df.evidence_group_id, df.id::text)) AS n
     FROM document_findings df
     JOIN tenant_standards  ts
       ON ts.tenant_id   = df.tenant_id
      AND ts.standard_id = df.standard_id
      AND ts.status     <> 'lapsed'
    WHERE df.review_status = 'pending'
      AND df.is_active     = TRUE
    GROUP BY df.tenant_id, df.standard_id
 )
 SELECT LEFT(tenant_id::text, 8) AS tenant,
        standard_id, n AS pending_visible
   FROM filtered
   ORDER BY tenant, standard_id;" 2>&1

# ── 8. Show which frameworks the sweep would nudge (live) ───────
echo
echo "=== 8. Enrolment-nudge candidates (live, dry-run) ==="
PYTHONPATH="$ARION_ROOT" python3 -m rag.scheduler.tick \
    --work enrolment_nudge --dry-run --json 2>&1 | \
    python3 -c "
import sys, json
data = json.loads(sys.stdin.read().splitlines()[-1])
for r in data.get('results', []):
    for tid, stats in (r.get('per_tenant') or {}).items():
        print(f'  tenant {tid[:8]}: {stats}')
"

# ── 9. Deployment log ────────────────────────────────────────────
LOG_FILE="$ARION_ROOT/.deployment_log.jsonl"
echo
echo "=== 9. Deployment log tail ==="
tail -3 "$LOG_FILE" 2>/dev/null || echo "(no log yet)"

echo
echo "=== DONE — Ship 129' deployed ==="
echo "See docs/memory/ship-129-prime-arc-retrospective-2026-09-08.md"
