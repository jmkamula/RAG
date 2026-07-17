#!/usr/bin/env bash
# ArionComply sweep-timer installer.
# Requires sudo. Idempotent: safe to re-run.
#
# Installs:
#   /etc/systemd/system/arioncomply-sweep.service
#   /etc/systemd/system/arioncomply-sweep.timer
# Enables + starts the timer.
#
# Verify after install:
#   systemctl list-timers arioncomply-sweep.timer
#   systemctl status arioncomply-sweep.timer
#   journalctl -u arioncomply-sweep.service --since '30 min ago'
#
# To disable:
#   sudo systemctl disable --now arioncomply-sweep.timer
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
    echo "This installer needs root — run with: sudo $0" >&2
    exit 1
fi

REPO=/data/arioncomply
SRC="${REPO}/ops/systemd"
DEST=/etc/systemd/system

# Sanity check: repo present, tick module importable.
if [[ ! -f "${REPO}/rag/scheduler/tick.py" ]]; then
    echo "rag/scheduler/tick.py not found under ${REPO}" >&2
    exit 1
fi

# Copy unit files.
install -m 0644 "${SRC}/arioncomply-sweep.service" "${DEST}/arioncomply-sweep.service"
install -m 0644 "${SRC}/arioncomply-sweep.timer"   "${DEST}/arioncomply-sweep.timer"

# Reload systemd + enable + start the timer (not the service — the timer
# handles firing).
systemctl daemon-reload
systemctl enable  arioncomply-sweep.timer
systemctl start   arioncomply-sweep.timer

# Show status so the operator can eyeball success.
echo "── Timer status ──────────────────────────────────────────────"
systemctl list-timers arioncomply-sweep.timer --no-pager || true
echo
echo "── Next scheduled run ────────────────────────────────────────"
systemctl status arioncomply-sweep.timer --no-pager 2>/dev/null | head -20 || true
echo
echo "OK — sweep tick will fire every 30 minutes."
echo "Verify a real tick after ~2 minutes:"
echo "    journalctl -u arioncomply-sweep.service --since '5 min ago'"
echo "    psql -U arioncomply -d arioncomply_compliance -c '"
echo "        SELECT tick_id, work_type, status, started_at"
echo "          FROM sweep_log ORDER BY started_at DESC LIMIT 8;'"
