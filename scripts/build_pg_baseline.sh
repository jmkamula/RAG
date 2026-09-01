#!/usr/bin/env bash
# scripts/build_pg_baseline.sh — regenerate Postgres golden images.
#
# Emits three files, all under db/baseline/:
#
#   1. schema_baseline.sql           — DDL for arioncomply_compliance
#                                       (--schema-only --no-owner --no-privileges,
#                                        excludes schema_migrations tracker)
#   2. schema_sessions_baseline.sql  — DDL for arioncomply_sessions
#                                       (LangGraph checkpointer schema)
#   3. seed_curator_data.sql         — catalog data (INSERT statements).
#                                       Covers 9 pure-catalog tables + the
#                                       tenant_id IS NULL rows on
#                                       retention_policies (cross-tenant
#                                       defaults).
#
# Runs against the LIVE dev-host Postgres (arioncomply_compliance +
# arioncomply_sessions) — the assumption is the dev host is the
# working reference for what "current" means. Tenant data is not
# included; --schema-only excludes all data, and the catalog data
# dump is scoped to specific tables.
#
# Idempotent: re-running produces the same output modulo the
# generation timestamp header. Safe to invoke from the pre-commit
# hook.
#
# Requires: postgres running locally, arioncomply role has SELECT on
# the catalog tables, python3 available.
#
# Usage:
#   bash scripts/build_pg_baseline.sh
#
# Ship 102'.a (2026-09-01).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASELINE_DIR="${REPO_ROOT}/db/baseline"
GENERATED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
GIT_SHA="$(cd "$REPO_ROOT" && git rev-parse --short HEAD 2>/dev/null || echo unknown)"

log() { printf "\033[1;34m==>\033[0m %s\n" "$*"; }
ok()  { printf "\033[1;32m✓\033[0m  %s\n" "$*"; }

mkdir -p "$BASELINE_DIR"

# ── 1. Schema DDL for arioncomply_compliance ─────────────────────────
log "dumping schema DDL from arioncomply_compliance"
{
    printf -- "-- ArionComply — Postgres schema baseline (arioncomply_compliance)\n"
    printf -- "-- Generated: %s from HEAD %s by scripts/build_pg_baseline.sh\n" \
        "$GENERATED_AT" "$GIT_SHA"
    printf -- "-- Includes: all public-schema DDL (tables / views / functions /\n"
    printf -- "--          indexes / constraints / policies). Excludes: OWNER +\n"
    printf -- "--          GRANT (applied post-hoc by baseline_grants.sql) and\n"
    printf -- "--          the schema_migrations tracker (created by install.sh).\n"
    printf -- "--          Zero tenant data — this is DDL-only.\n"
    printf -- "-- Apply order: schema_baseline.sql → baseline_grants.sql → seed_curator_data.sql\n"
    printf -- "\n"
    sudo -u postgres pg_dump \
        --schema-only \
        --no-owner \
        --no-privileges \
        --exclude-table=schema_migrations \
        arioncomply_compliance
} > "${BASELINE_DIR}/schema_baseline.sql"
ok "wrote $(wc -l < "${BASELINE_DIR}/schema_baseline.sql") lines to db/baseline/schema_baseline.sql"

# ── 2. Schema DDL for arioncomply_sessions ───────────────────────────
log "dumping schema DDL from arioncomply_sessions"
{
    printf -- "-- ArionComply — Postgres schema baseline (arioncomply_sessions)\n"
    printf -- "-- Generated: %s from HEAD %s by scripts/build_pg_baseline.sh\n" \
        "$GENERATED_AT" "$GIT_SHA"
    printf -- "-- LangGraph checkpointer schema. Zero session data.\n"
    printf -- "\n"
    sudo -u postgres pg_dump \
        --schema-only \
        --no-owner \
        --no-privileges \
        arioncomply_sessions
} > "${BASELINE_DIR}/schema_sessions_baseline.sql"
ok "wrote $(wc -l < "${BASELINE_DIR}/schema_sessions_baseline.sql") lines to db/baseline/schema_sessions_baseline.sql"

# ── 3. Catalog data ──────────────────────────────────────────────────
# 9 pure-catalog tables (no tenant_id column, safe to dump fully) +
# retention_policies (has tenant_id column, but the tenant_id IS NULL
# rows are cross-tenant defaults that ship as catalog).
log "dumping catalog data"

# NOTE ON ref_sequences: not included. It has a tenant_id column
# populated with per-tenant next-sequence counters (assets, incidents,
# risks, etc). Dev host uses a sentinel tenant_id for its counters —
# shipping that data would leak the dev tenant's ref state. DDL ships;
# each customer's tenant starts with an empty ref_sequences table and
# fills it via runtime writes.
CATALOG_TABLES=(
    standards
    standard_relationships
    ref_prefixes
    roles
    topics
    topic_leaves
    templates
    enricher_cache
    fact_source_config
)

{
    printf -- "-- ArionComply — curator seed data\n"
    printf -- "-- Generated: %s from HEAD %s by scripts/build_pg_baseline.sh\n" \
        "$GENERATED_AT" "$GIT_SHA"
    printf -- "-- Apply AFTER schema_baseline.sql + baseline_grants.sql.\n"
    printf -- "-- Contains catalog data only — zero tenant rows.\n"
    printf -- "--\n"
    printf -- "-- Pure catalog tables (no tenant_id column, dumped fully):\n"
    for t in "${CATALOG_TABLES[@]}"; do
        printf -- "--   %s\n" "$t"
    done
    printf -- "-- Cross-tenant defaults (tenant_id IS NULL rows only):\n"
    printf -- "--   retention_policies\n"
    printf -- "\n"
    printf "BEGIN;\n\n"

    # 3a. Pure catalog tables via pg_dump --data-only.
    TABLE_ARGS=()
    for t in "${CATALOG_TABLES[@]}"; do
        TABLE_ARGS+=(--table="public.${t}")
    done
    sudo -u postgres pg_dump \
        --data-only \
        --column-inserts \
        --no-owner \
        --no-privileges \
        "${TABLE_ARGS[@]}" \
        arioncomply_compliance \
        | grep -Ev '^(--|SET |SELECT pg_catalog|\\restrict|\\unrestrict)' \
        | grep -v '^$'

    printf "\n"

    # 3b. retention_policies cross-tenant defaults (tenant_id IS NULL only).
    printf -- "-- retention_policies: cross-tenant defaults (tenant_id IS NULL) --\n"
    sudo -u postgres psql -d arioncomply_compliance -tA <<'PSQL_EOF'
SELECT format(
    'INSERT INTO public.retention_policies VALUES (%s);',
    concat_ws(', ',
        quote_nullable(id::text),
        quote_nullable(tenant_id::text),
        quote_nullable(retention_class),
        quote_nullable(table_name),
        quote_nullable(retain_years::text),
        quote_nullable(retain_days::text),
        quote_nullable(anonymise_after_years::text),
        quote_nullable(auto_purge::text),
        quote_nullable(legal_basis),
        quote_nullable(notes),
        quote_nullable(created_at::text)
    )
)
FROM public.retention_policies
WHERE tenant_id IS NULL
ORDER BY created_at;
PSQL_EOF

    printf "\nCOMMIT;\n"
} > "${BASELINE_DIR}/seed_curator_data.sql"

ok "wrote $(wc -l < "${BASELINE_DIR}/seed_curator_data.sql") lines to db/baseline/seed_curator_data.sql"

# ── 4. Report per-table row counts ───────────────────────────────────
log "catalog data row counts:"
for t in "${CATALOG_TABLES[@]}"; do
    cnt=$(sudo -u postgres psql -d arioncomply_compliance -tAc "SELECT COUNT(*) FROM public.${t}")
    printf "     %-30s %6s\n" "$t" "$cnt"
done
ret_null=$(sudo -u postgres psql -d arioncomply_compliance -tAc \
    "SELECT COUNT(*) FROM public.retention_policies WHERE tenant_id IS NULL")
printf "     %-30s %6s\n" "retention_policies (tenant NULL)" "$ret_null"

log "done — 3 files regenerated in db/baseline/"
