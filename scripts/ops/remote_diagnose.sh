#!/usr/bin/env bash
#
# scripts/ops/remote_diagnose.sh
#
# Run from an operator laptop: SSH into the customer VM, produce a
# diagnostic bundle via scripts/ops/diagnose.sh, retrieve it, extract
# it locally. Prints the local extraction path to stdout — Claude can
# then read files inside without another SSH round trip.
#
# Usage:
#   bash scripts/ops/remote_diagnose.sh <ssh-target> [local-scratch-dir]
#
# Examples:
#   bash scripts/ops/remote_diagnose.sh arionops@40.68.12.34
#   bash scripts/ops/remote_diagnose.sh arionops@vm.example.com ~/arion-ops/acme/
#
# ssh-target: passed straight to ssh/scp; anything ssh accepts is fine
#   (bare IP, hostname, user@host, ssh config alias with jumphost).
#
# local-scratch-dir: where to store the tarball + extracted bundle.
#   Defaults to $(pwd)/arion-diag-$(date -u +%Y%m%d-%H%M%S)/.
#   Directory is created if it doesn't exist.
#
# Never modifies anything on the customer VM beyond producing the
# /tmp/arion-diag-*.tar.gz that diagnose.sh writes. Idempotent from
# the operator's side; safe to re-run.
#
# See CLAUDE_OPERATOR.md §Phase 3 + CLAUDE_DEPLOY_GUIDE.md §2.6.

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
    echo "Usage: $0 <ssh-target> [local-scratch-dir]" >&2
    echo "Example: $0 arionops@40.68.12.34 ~/arion-ops/acme/" >&2
    exit 64  # EX_USAGE
fi

readonly SSH_TARGET="$1"
readonly SCRATCH_DIR="${2:-$(pwd)/arion-diag-$(date -u +%Y%m%d-%H%M%S)}"

# Sanity: refuse to write to $HOME or / directly — always inside a
# named subdirectory so nothing accidentally clobbers.
if [[ "$SCRATCH_DIR" == "$HOME" || "$SCRATCH_DIR" == "/" || -z "$SCRATCH_DIR" ]]; then
    echo "ERROR: scratch dir must be a named subdirectory, not $HOME or /" >&2
    exit 78  # EX_CONFIG
fi

mkdir -p "$SCRATCH_DIR"

# Verify SSH works before doing anything else.
if ! ssh -o BatchMode=yes -o ConnectTimeout=10 "$SSH_TARGET" 'true' 2>/dev/null; then
    echo "ERROR: cannot SSH to $SSH_TARGET (BatchMode, 10s timeout)" >&2
    echo "  Fix: ensure key is loaded (ssh-add) + NSG allows your IP" >&2
    exit 77  # EX_NOPERM
fi

# Step 1: run diagnose.sh on the VM.
# diagnose.sh writes to /tmp/arion-diag-<host>-<ts>.tar.gz and prints
# the path on the last line (per its own convention). We capture the
# whole output so any inline warnings surface to the operator.
echo "── producing bundle on $SSH_TARGET ──" >&2
REMOTE_OUTPUT="$(ssh "$SSH_TARGET" 'bash /data/arioncomply/scripts/ops/diagnose.sh' 2>&1)"
echo "$REMOTE_OUTPUT" >&2

# Extract the tarball path from diagnose.sh's output. It emits
# something like:
#   arion-diag: bundle written to /tmp/arion-diag-vmname-20260828-104521.tar.gz
REMOTE_TARBALL="$(echo "$REMOTE_OUTPUT" \
    | grep -oE '/tmp/arion-diag-[^ ]+\.tar\.gz' \
    | tail -1)"

if [[ -z "$REMOTE_TARBALL" ]]; then
    # Fallback: look for the newest tarball in /tmp.
    REMOTE_TARBALL="$(ssh "$SSH_TARGET" \
        'ls -1t /tmp/arion-diag-*.tar.gz 2>/dev/null | head -1')"
fi

if [[ -z "$REMOTE_TARBALL" ]]; then
    echo "ERROR: could not identify the tarball on the VM" >&2
    echo "  Look at diagnose.sh output above for clues" >&2
    exit 70  # EX_SOFTWARE
fi

echo "── remote tarball: $REMOTE_TARBALL ──" >&2

# Step 2: pull the tarball to the scratch dir.
echo "── copying to $SCRATCH_DIR ──" >&2
scp -q "$SSH_TARGET:$REMOTE_TARBALL" "$SCRATCH_DIR/"

# Local filename is the basename.
LOCAL_TARBALL="$SCRATCH_DIR/$(basename "$REMOTE_TARBALL")"
if [[ ! -f "$LOCAL_TARBALL" ]]; then
    echo "ERROR: scp completed but $LOCAL_TARBALL not found" >&2
    exit 74  # EX_IOERR
fi

# Step 3: extract into a named subdirectory so extraction+tarball
# live side-by-side for easy cleanup + re-extraction.
EXTRACT_DIR="$SCRATCH_DIR/$(basename "$LOCAL_TARBALL" .tar.gz)"
mkdir -p "$EXTRACT_DIR"
tar xzf "$LOCAL_TARBALL" -C "$EXTRACT_DIR" --strip-components=1

# Print the final path to stdout — this is what the caller (Claude
# reading + reasoning) picks up.
echo ""
echo "$EXTRACT_DIR"
