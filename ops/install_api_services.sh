#!/usr/bin/env bash
# ArionComply API + Chroma systemd installer.
# Requires sudo. Idempotent: safe to re-run.
#
# Installs:
#   /etc/systemd/system/arioncomply-chroma.service
#   /etc/systemd/system/arioncomply-api.service
#
# ── Companion units already installed (Ship 44 / Ship 3'.a) ──
#   /etc/systemd/system/arioncomply-jaeger.service
#   /etc/systemd/system/arioncomply-phoenix.service
#   /etc/systemd/system/arioncomply-sweep.{service,timer}
#
# The API service Requires= chroma + postgresql, so systemd starts them
# in the right order on boot and restarts the API if chroma drops.
#
# Verify after install:
#   systemctl status arioncomply-chroma arioncomply-api
#   journalctl -u arioncomply-api -n 30
#   curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/docs

set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
    echo "This installer needs root — run with: sudo $0" >&2
    exit 1
fi

SRC=/data/arioncomply/ops/systemd
DST=/etc/systemd/system

echo "==> Installing systemd units..."
install -m 0644 "$SRC/arioncomply-chroma.service" "$DST/arioncomply-chroma.service"
install -m 0644 "$SRC/arioncomply-api.service"    "$DST/arioncomply-api.service"

echo "==> Reloading systemd..."
systemctl daemon-reload

# Always enable so systemd starts these on boot. Only START when the
# port is free — starting would collide with any existing nohup
# process bound to the port and confuse the operator mid-session.
echo "==> Enabling for boot auto-start..."
systemctl enable arioncomply-chroma arioncomply-api

if lsof -i :8000 -sTCP:LISTEN >/dev/null 2>&1; then
    echo "  ⚠  Something is already listening on port 8000 — NOT starting"
    echo "     arioncomply-chroma.service now. Kill the existing process"
    echo "     first (probably a nohup Chroma from earlier), then run:"
    echo "         sudo systemctl start arioncomply-chroma"
    echo "     (Enabled for auto-start on next boot regardless.)"
    CHROMA_STARTED=0
else
    echo "==> Starting arioncomply-chroma..."
    systemctl start arioncomply-chroma
    CHROMA_STARTED=1
    sleep 3
fi

if lsof -i :8080 -sTCP:LISTEN >/dev/null 2>&1; then
    echo "  ⚠  Something is already listening on port 8080 — NOT starting"
    echo "     arioncomply-api.service now. Kill the existing process first:"
    echo "         kill \$(lsof -ti:8080)"
    echo "     then run:"
    echo "         sudo systemctl start arioncomply-api"
    echo "     (Enabled for auto-start on next boot regardless.)"
    API_STARTED=0
else
    echo "==> Starting arioncomply-api..."
    systemctl start arioncomply-api
    API_STARTED=1
fi

echo
echo "==> Status check:"
systemctl --no-pager status arioncomply-chroma arioncomply-api 2>&1 | \
    grep -E "Loaded:|Active:" | head -10 || true

echo
echo "==> Health probe:"
sleep 5
if curl -sf http://localhost:8000/api/v2/heartbeat > /dev/null; then
    echo "  ✓ Chroma responding on :8000"
else
    echo "  ✗ Chroma NOT responding on :8000"
fi
if curl -sf http://localhost:8080/docs > /dev/null; then
    echo "  ✓ API responding on :8080"
else
    echo "  ✗ API NOT responding on :8080 (may still be starting; wait ~20s)"
fi

cat <<EOF

Both units are now enabled — will start automatically on boot.

Commands:
  systemctl status arioncomply-{chroma,api}
  systemctl restart arioncomply-api
  journalctl -u arioncomply-api -f
  tail -f /tmp/arioncomply-api.log

To disable auto-start:
  sudo systemctl disable arioncomply-api arioncomply-chroma
EOF
