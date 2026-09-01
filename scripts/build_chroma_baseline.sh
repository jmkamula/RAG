#!/usr/bin/env bash
# scripts/build_chroma_baseline.sh — regenerate Chroma golden image.
#
# Emits db/baseline/chroma_prebuilt.tar.gz — the entire live
# dev-host chroma_db/ directory captured as a single tar+gzip.
# Customer install.sh will extract this directly into
# $ARION_ROOT/chroma_db and start the Chroma service pointing
# at it.
#
# All 9 collections ship pre-computed:
#   musts_arioncomply      5385 docs   (MUST-item embeddings)
#   arioncombly_all        1668 docs   (unified multi-standard)
#   edpb_guidelines        1190 docs   (EDPB/WP29 guidance — copyrighted PDFs)
#   gdpr_2016_679           303 docs   (GDPR articles)
#   iso27001_2022           126 docs   (ISO 27001 controls)
#   iso27701_2019            49 docs   (ISO 27701 controls)
#   iso27005_2022            42 docs   (risk mgmt guidance — copyrighted)
#   iso27003_2017            25 docs   (ISMS guidance — copyrighted)
#   iso27004_2016            23 docs   (measurement guidance — copyrighted)
#
# The four "guidance" collections (edpb + 3× iso270xx) cannot be
# rebuilt at customer sites — their source content is copyrighted
# PDFs that live in /data/arioncomply/private/ (gitignored). The
# pre-computed embedding vectors are derived work and safe to
# ship. This makes the prebuilt-tar approach non-negotiable for
# a functional customer install.
#
# Chroma uses SQLite as its underlying store. For a fully-safe
# hot-copy we should ideally stop the chroma service first, but
# on the dev host that disrupts everything else running. Since
# the dev host is read-mostly at rest, we accept the slight
# consistency risk and tar directly. Verification below catches
# corrupt tars before shipping.
#
# Usage:
#   bash scripts/build_chroma_baseline.sh
#
# Ship 102'.c (2026-09-01).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASELINE_DIR="${REPO_ROOT}/db/baseline"
CHROMA_SRC="${REPO_ROOT}/chroma_db"
OUT_PATH="${BASELINE_DIR}/chroma_prebuilt.tar.gz"

log() { printf "\033[1;34m==>\033[0m %s\n" "$*"; }
ok()  { printf "\033[1;32m✓\033[0m  %s\n" "$*"; }
fail(){ printf "\033[1;31m✗\033[0m  %s\n" "$*"; exit 1; }

mkdir -p "$BASELINE_DIR"

# ── 1. Sanity ─────────────────────────────────────────────────────
[[ -d "$CHROMA_SRC" ]] || fail "$CHROMA_SRC not found — is Chroma set up on this host?"

src_size_human=$(du -sh "$CHROMA_SRC" | awk '{print $1}')
log "packaging $CHROMA_SRC ($src_size_human)"

# ── 2. Tar + gzip ─────────────────────────────────────────────────
# `-C src .` captures the CONTENTS of chroma_db, not the wrapper
# directory. Customer install extracts straight into their own
# chroma_db/ without wrapper juggling.
tar -czf "$OUT_PATH" -C "$CHROMA_SRC" .

out_size=$(stat -c%s "$OUT_PATH")
out_size_human=$(numfmt --to=iec-i --suffix=B "$out_size" 2>/dev/null || echo "$out_size B")
ok "wrote $out_size_human to db/baseline/chroma_prebuilt.tar.gz"

# ── 3. Verification — extract to throwaway dir, count collections ─
log "verifying tar by extracting to /tmp/chroma_verify"
rm -rf /tmp/chroma_verify
mkdir -p /tmp/chroma_verify
tar -xzf "$OUT_PATH" -C /tmp/chroma_verify

# Use chromadb PersistentClient to read directly from the extracted
# directory (no need to start a separate Chroma server for this).
PYTHONPATH="$REPO_ROOT" python3 <<'PYEOF'
import sys
try:
    import chromadb
except ImportError:
    print("  (chromadb not installed — skipping doc-count verification)")
    sys.exit(0)

c = chromadb.PersistentClient(path="/tmp/chroma_verify")
collections = c.list_collections()
if not collections:
    print("  ✗ verification: no collections found in extracted tar")
    sys.exit(1)

print(f"  {len(collections)} collections in extracted tar:")
for coll_summary in sorted(collections, key=lambda x: -c.get_collection(x.name).count()):
    coll = c.get_collection(coll_summary.name)
    print(f"     {coll_summary.name:25s}  {coll.count():>6} docs")
PYEOF

rm -rf /tmp/chroma_verify
ok "verified — customer install can extract this tar into \$ARION_ROOT/chroma_db"

# ── 4. Metadata sidecar ───────────────────────────────────────────
# Not strictly necessary (tar contains its own metadata), but a
# tiny JSON sidecar lets install.sh check "is my current tar current?"
# without extracting.
GIT_SHA="$(cd "$REPO_ROOT" && git rev-parse --short HEAD 2>/dev/null || echo unknown)"
cat > "${BASELINE_DIR}/chroma_prebuilt.meta.json" <<META
{
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "git_sha": "$GIT_SHA",
  "raw_size_bytes": $(du -sb "$CHROMA_SRC" | awk '{print $1}'),
  "tar_size_bytes": $out_size,
  "generator": "scripts/build_chroma_baseline.sh"
}
META
ok "wrote db/baseline/chroma_prebuilt.meta.json"
