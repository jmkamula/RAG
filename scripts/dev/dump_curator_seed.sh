#!/usr/bin/env bash
# Dump the curator-authored (portable across tenants) reference data.
# Excludes anything tenant-scoped or per-VM-runtime.
#
# Output: db/baseline/seed_curator_data.sql — pg_dump --data-only for
# the specific tables that carry framework curation, retention rules,
# ref-prefix reservations, and RBAC role catalog.
#
# Run: bash scripts/dev/dump_curator_seed.sh
set -euo pipefail

OUT=/data/arioncomply/db/baseline/seed_curator_data.sql

# Curator tables — non-tenant-scoped reference data every install needs.
# Verified 2026-07-27 against Ship 47'.a memo:
#   standards               (9 rows)  — framework catalog
#   standard_relationships  (5 rows)  — SQL-layer role-model edges
#   retention_policies     (16 rows)  — data class → days
#   ref_prefixes            (8 rows)  — external_ref prefix reservations
#   ref_sequences           (7 rows)  — per-prefix current numbers
#   roles                   (7 rows)  — RBAC role catalog
CURATOR_TABLES=(
    standards
    standard_relationships
    retention_policies
    ref_prefixes
    ref_sequences
    roles
)

# pg_dump one table at a time so we can concatenate + inspect
: > "$OUT"
{
    echo "-- Curator seed data — Ship 47'.b"
    echo "-- Generated: $(date -Iseconds)"
    echo "-- Apply after schema_baseline.sql on a fresh install."
    echo "-- All tables here are portable across tenants and non-runtime."
    echo
    echo "BEGIN;"
    echo
} >> "$OUT"

for tbl in "${CURATOR_TABLES[@]}"; do
    echo "-- ── ${tbl} ──" >> "$OUT"
    sudo -u postgres pg_dump --data-only --no-owner --no-privileges \
        --disable-triggers \
        --column-inserts \
        -t "public.${tbl}" \
        -d arioncomply_compliance \
    >> "$OUT" 2>/dev/null
    echo >> "$OUT"
done

echo "COMMIT;" >> "$OUT"

echo "wrote $OUT"
echo "  lines: $(wc -l < "$OUT")"
echo "  INSERTs: $(grep -c '^INSERT' "$OUT")"
