#!/usr/bin/env bash
#
# scripts/ops/update.sh — ArionComply in-place update on a customer VM.
#
# Runs on a customer VM (as arionops or any user with passwordless sudo).
# Fetches the latest code from GitHub, applies any new schema_v*.sql
# migrations via install.sh, restarts the API service, and prints a
# post-update verification block.
#
# Idempotent — safe to re-run. If nothing has changed, all steps are
# no-ops except the API restart (which stays cheap).
#
# Usage:
#   sudo bash scripts/ops/update.sh              # normal update
#   sudo bash scripts/ops/update.sh --no-restart # skip API restart
#   sudo bash scripts/ops/update.sh --dry-run    # show what would change
#
# See CLAUDE_OPERATOR.md for the operator-side workflow +
# scripts/ops/remote_update.sh for the laptop-driven wrapper.

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────
ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"

DRY_RUN=0
NO_RESTART=0
for arg in "$@"; do
    case "$arg" in
        --dry-run)    DRY_RUN=1 ;;
        --no-restart) NO_RESTART=1 ;;
        -h|--help)
            sed -n '3,/^set -euo/p' "$0" | sed 's/^#//' | sed '$d'
            exit 0 ;;
        *) echo "unknown arg: $arg" >&2; exit 64 ;;
    esac
done

# ── Guards ────────────────────────────────────────────────────────
[[ -d "$ARION_ROOT/.git" ]] || {
    echo "ERROR: $ARION_ROOT is not a git repo — is this the right box?" >&2
    exit 78
}
[[ -f "$ARION_ROOT/deploy/install.sh" ]] || {
    echo "ERROR: deploy/install.sh missing — repo layout unexpected" >&2
    exit 78
}
cd "$ARION_ROOT"

# ── Pretty printers ──────────────────────────────────────────────
if [[ -t 1 ]]; then
    _bold() { printf '\033[1m%s\033[0m\n' "$*"; }
    _step() { printf '\n\033[1;36m=== %s ===\033[0m\n' "$*"; }
    _ok()   { printf '\033[32m✓ %s\033[0m\n' "$*"; }
    _warn() { printf '\033[33m! %s\033[0m\n' "$*"; }
else
    _bold() { printf '=== %s ===\n' "$*"; }
    _step() { printf '\n=== %s ===\n' "$*"; }
    _ok()   { printf 'OK: %s\n' "$*"; }
    _warn() { printf 'WARN: %s\n' "$*"; }
fi

# ── Snapshot BEFORE ──────────────────────────────────────────────
_step "BEFORE snapshot"
BEFORE_SHA=$(git rev-parse --short HEAD)
BEFORE_SUBJECT=$(git log -1 --format='%s')
echo "git head:    $BEFORE_SHA — $BEFORE_SUBJECT"

BEFORE_SCHEMA=$(sudo -u postgres psql -d arioncomply_compliance -tAc \
    "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1" 2>/dev/null || echo "")
echo "highest schema: ${BEFORE_SCHEMA:-(no tracker table yet)}"

# ── Fetch ────────────────────────────────────────────────────────
_step "1. git fetch"
git fetch --all --tags 2>&1 | tail -3

# Show what's incoming
INCOMING=$(git log --oneline HEAD..origin/main 2>/dev/null | head -20 || true)
if [[ -z "$INCOMING" ]]; then
    _ok "Already at latest — no code updates to apply"
    NO_CODE_CHANGE=1
else
    NO_CODE_CHANGE=0
    echo "Incoming commits:"
    echo "$INCOMING" | sed 's/^/  /'
fi

# Show pending migrations (files present but not yet in schema_migrations).
# The tracker table itself is a Ship 102' customer-install pattern; older
# hand-provisioned dev boxes don't have it. Skip the pending report there
# and let install.sh's bootstrap logic populate the tracker on first run.
TRACKER_EXISTS=$(sudo -u postgres psql -d arioncomply_compliance -tAc \
    "SELECT to_regclass('public.schema_migrations') IS NOT NULL" 2>/dev/null || echo "?")
if [[ "$TRACKER_EXISTS" == "t" ]]; then
    PENDING_MIGRATIONS=""
    UPCOMING_MIGRATION_FILES=$(git ls-tree -r --name-only origin/main -- db/ 2>/dev/null \
        | grep -E '^db/schema_v[0-9]+.*\.sql$' | sort -V || true)
    for f in $UPCOMING_MIGRATION_FILES; do
        v=$(basename "$f" .sql)
        already=$(sudo -u postgres psql -d arioncomply_compliance -tAc \
            "SELECT 1 FROM schema_migrations WHERE version = '$v'" 2>/dev/null || echo "")
        if [[ "$already" != "1" ]]; then
            PENDING_MIGRATIONS+="  $v"$'\n'
        fi
    done
    if [[ -n "$PENDING_MIGRATIONS" ]]; then
        echo "Pending schema migrations:"
        echo "$PENDING_MIGRATIONS"
    else
        echo "Pending schema migrations: none"
    fi
else
    _warn "schema_migrations tracker not present — install.sh will bootstrap it on first run"
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
    _warn "--dry-run: not applying anything. Rerun without --dry-run to apply."
    exit 0
fi

# ── Apply code updates ───────────────────────────────────────────
if [[ "$NO_CODE_CHANGE" -eq 0 ]]; then
    _step "2. git pull"
    git pull --ff-only 2>&1 | tail -5

    _step "3. git lfs pull (goldens)"
    if command -v git-lfs >/dev/null 2>&1; then
        git lfs pull 2>&1 | tail -3
    else
        _warn "git-lfs not installed — skipping (only matters if Chroma golden changed)"
    fi
else
    _step "2-3. (skipped — code already current)"
fi

# ── Apply schema migrations via install.sh ───────────────────────
# install.sh is idempotent — safe to re-run. It'll skip everything
# already applied and only run the new schema_v*.sql files.
_step "4. install.sh (applies new schema_v*.sql migrations idempotently)"
sudo bash deploy/install.sh 2>&1 | tail -20 || {
    echo "ERROR: install.sh failed — inspect above output. Nothing partially restarted." >&2
    exit 1
}

# ── Restart API ──────────────────────────────────────────────────
if [[ "$NO_RESTART" -eq 1 ]]; then
    _step "5. API restart SKIPPED (--no-restart)"
    _warn "New code is on disk but not running. Restart later with: sudo systemctl restart arioncomply-api"
else
    _step "5. Restart arioncomply-api"
    sudo systemctl restart arioncomply-api
    echo "waiting for API to come back up..."
    for i in 1 2 3 4 5 6 7 8 9 10 11 12; do
        if curl -sf --max-time 3 http://127.0.0.1:8080/docs > /dev/null; then
            _ok "API up after $((i*5))s"
            break
        fi
        sleep 5
        if [[ "$i" -eq 12 ]]; then
            _warn "API did not respond within 60s — check: journalctl -u arioncomply-api -n 100 --no-pager"
        fi
    done
fi

# ── Snapshot AFTER ───────────────────────────────────────────────
_step "AFTER snapshot"
AFTER_SHA=$(git rev-parse --short HEAD)
AFTER_SUBJECT=$(git log -1 --format='%s')
echo "git head:      $AFTER_SHA — $AFTER_SUBJECT"

AFTER_SCHEMA=$(sudo -u postgres psql -d arioncomply_compliance -tAc \
    "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1" 2>/dev/null || echo "")
echo "highest schema: ${AFTER_SCHEMA:-(no tracker table)}"

if [[ "$NO_RESTART" -eq 0 ]]; then
    echo
    echo "API health:"
    sudo systemctl is-active arioncomply-api | sed 's/^/  systemd status: /'
    if curl -sf --max-time 3 http://127.0.0.1:8080/docs > /dev/null; then
        echo "  http probe:    OK (/docs)"
    else
        _warn "http probe:    FAILED"
    fi
fi

echo
if [[ "$BEFORE_SHA" == "$AFTER_SHA" && "$BEFORE_SCHEMA" == "$AFTER_SCHEMA" ]]; then
    _ok "No-op update — nothing changed"
else
    _ok "Update complete"
    echo "  code:   $BEFORE_SHA → $AFTER_SHA"
    echo "  schema: $BEFORE_SCHEMA → $AFTER_SCHEMA"
fi
