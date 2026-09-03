#!/usr/bin/env bash
#
# scripts/ops/remote_update.sh
#
# Run from an operator laptop: SSH into the customer VM, git-pull the
# latest ArionComply code, invoke scripts/ops/update.sh which applies
# any new schema migrations + restarts the API.
#
# Usage:
#   bash scripts/ops/remote_update.sh <ssh-target> [--dry-run|--no-restart]
#
# Examples:
#   bash scripts/ops/remote_update.sh arionops@10.0.1.85
#   bash scripts/ops/remote_update.sh arionops@10.0.1.85 --dry-run
#   bash scripts/ops/remote_update.sh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85
#
# ssh-target: passed straight to ssh; anything ssh accepts is fine
#   (bare IP, hostname, user@host, ssh config alias with jumphost).
#
# Chicken-and-egg note: the FIRST time this arc's scripts/ops/update.sh
# reaches a customer box, the box doesn't have it yet. This wrapper
# runs `git pull` on the remote first, THEN invokes update.sh — so
# a bare `git pull && sudo bash scripts/ops/update.sh` works even
# when update.sh was introduced by the same pull. Subsequent updates
# use the on-box update.sh which also does its own `git pull`.
#
# Never runs destructive commands. If the operator wants to preview
# the change without applying it, pass `--dry-run` (relayed to
# update.sh which shows pending commits + migrations without touching
# anything).
#
# See CLAUDE_OPERATOR.md §Phase 3 for the operator handbook +
# scripts/ops/update.sh for the on-VM worker.

set -euo pipefail

# Split args: pass through -i / -p / -o / -F to ssh; keep --dry-run
# and --no-restart for update.sh.
SSH_OPTS=()
UPDATE_ARGS=()
SSH_TARGET=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -i|-p|-o|-F|-J)
            SSH_OPTS+=("$1" "$2")
            shift 2
            ;;
        --dry-run|--no-restart)
            UPDATE_ARGS+=("$1")
            shift
            ;;
        -h|--help)
            sed -n '3,/^set -euo/p' "$0" | sed 's/^#//' | sed '$d'
            exit 0
            ;;
        -*)
            echo "unknown option: $1" >&2
            exit 64
            ;;
        *)
            if [[ -n "$SSH_TARGET" ]]; then
                echo "extra positional arg: $1 (already have target $SSH_TARGET)" >&2
                exit 64
            fi
            SSH_TARGET="$1"
            shift
            ;;
    esac
done

if [[ -z "$SSH_TARGET" ]]; then
    echo "Usage: $0 [-i keyfile] <ssh-target> [--dry-run|--no-restart]" >&2
    echo "Example: $0 -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85" >&2
    exit 64
fi

# Verify SSH works before doing anything else.
if ! ssh -o BatchMode=yes -o ConnectTimeout=10 "${SSH_OPTS[@]}" \
        "$SSH_TARGET" 'true' 2>/dev/null; then
    echo "ERROR: cannot SSH to $SSH_TARGET (BatchMode, 10s timeout)" >&2
    echo "  Fix: ensure key is loaded (ssh-add) + NSG allows your IP" >&2
    exit 77
fi

# Bootstrap-friendly: run git pull first on the remote, THEN invoke
# update.sh (which will do its own pull too — harmless). This means
# update.sh is fetched via the git pull even on the very first run
# after this arc lands.
#
# Pass UPDATE_ARGS through as separate quoted words. Bash on the
# remote sees them as distinct argv[] entries because we let ssh
# reassemble them via printf %q.
REMOTE_UPDATE_ARGS=""
for a in "${UPDATE_ARGS[@]-}"; do
    REMOTE_UPDATE_ARGS+=" $(printf '%q' "$a")"
done

# Single-quoted heredoc so nothing local-expands; the printf %q above
# handles the args safely.
ssh "${SSH_OPTS[@]}" "$SSH_TARGET" bash -s <<REMOTE_SCRIPT
set -euo pipefail
cd /data/arioncomply

echo "=== bootstrap: git pull to fetch update.sh + latest code ==="
git pull --ff-only 2>&1 | tail -5

if [[ ! -x scripts/ops/update.sh ]]; then
    echo "ERROR: scripts/ops/update.sh missing on remote after pull" >&2
    exit 78
fi

echo
echo "=== invoking scripts/ops/update.sh$REMOTE_UPDATE_ARGS ==="
sudo bash scripts/ops/update.sh$REMOTE_UPDATE_ARGS
REMOTE_SCRIPT
