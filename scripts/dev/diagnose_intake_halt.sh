#!/usr/bin/env bash
#
# scripts/dev/diagnose_intake_halt.sh
#
# Pipeline halted after `xfw` on the latest workbook upload — no
# workbook_discovery / write / complete stages logged. This means an
# exception is being raised (and probably not silently caught) between
# the xfw stage and workbook_discovery. Dumps the info needed to
# identify where.
#
# Sections:
#   1. OTel status — services + config + whether traces are being exported
#   2. arioncomply-api journal since the latest upload (looking for
#      Traceback / ERROR / _upsert_client_document / workbook_discovery)
#   3. /tmp/arioncomply-api.log tail (same purpose, different sink)
#   4. Jaeger UI URL (for browser-side trace exploration)

set -u
ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
cd "$ARION_ROOT"

echo "=== 1. OTel status ==="
echo ""
echo "--- 1a. Env config ---"
grep -E "^OTEL_" .env 2>/dev/null || echo "(no OTEL_ vars in .env)"
echo ""
echo "--- 1b. systemd services ---"
for svc in arioncomply-jaeger arioncomply-phoenix; do
    status=$(systemctl is-active "$svc" 2>&1)
    echo "  $svc: $status"
done
echo ""
echo "--- 1c. Listening ports (OTLP gRPC 4317, Jaeger UI 16686, Phoenix 6006/6317) ---"
ss -tlnp 2>/dev/null | grep -E ":(4317|16686|6006|6317)\s" || echo "(none listening)"
echo ""
echo "--- 1d. API's OTel init log line ---"
sudo journalctl -u arioncomply-api --since "1 hour ago" --no-pager 2>&1 | \
    grep -E "telemetry:|OTel|Jaeger|Phoenix" | head -5 || echo "(no OTel init lines)"

echo ""
echo "=== 2. arioncomply-api journal since 30 min ago — errors + workbook signals ==="
sudo journalctl -u arioncomply-api --since "30 min ago" --no-pager 2>&1 | \
    grep -E "Traceback|ERROR|WARNING|workbook_discovery|_upsert_client_document|Stage 4.6|Stage 4.7|persist_proposals|client_documents" | \
    tail -50 || echo "(no matching lines)"

echo ""
echo "=== 3. /tmp/arioncomply-api.log — last 200 lines ==="
if [[ -f /tmp/arioncomply-api.log ]]; then
    tail -200 /tmp/arioncomply-api.log | grep -iE "Traceback|ERROR|workbook|client_doc|Stage" | tail -40 \
        || echo "(no matching lines in tmp log)"
else
    echo "(no /tmp/arioncomply-api.log)"
fi

echo ""
echo "=== 4. Jaeger trace pointer (for browser-side exploration) ==="
if systemctl is-active arioncomply-jaeger > /dev/null 2>&1; then
    echo "  SSH tunnel:  ssh -L 16686:127.0.0.1:16686 arionops@10.0.1.85"
    echo "  Then open:   http://localhost:16686/"
    echo "  Service:     arioncomply-api"
    echo "  Operation:   filter on 'workbook_discovery' or 'doc_pipeline'"
    echo "  Time range:  last 30 minutes"
else
    echo "  Jaeger not running — sudo bash /data/arioncomply/ops/install_jaeger.sh"
    echo "  (or debug via journal/log tail above)"
fi

echo ""
echo "=== 5. Latest intake_trace_log rows for the failing upload ==="
sudo -u postgres psql -d arioncomply_compliance -c "
WITH latest AS (
  SELECT id::text AS upload_id, filename
    FROM document_uploads
   WHERE filename ILIKE '%workbook%'
   ORDER BY uploaded_at DESC LIMIT 1
)
SELECT stage, stage_status, stage_ms, error_type,
       LEFT(error_detail, 200) AS error_detail
  FROM intake_trace_log
 WHERE upload_id = (SELECT upload_id FROM latest)
 ORDER BY traced_at;"
