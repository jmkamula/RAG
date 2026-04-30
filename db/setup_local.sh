#!/usr/bin/env zsh
# ArionComply — Local Postgres Setup (Mac)
# Usage: bash db/setup_local.sh [--reset]

set -e
RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'
DIM='\033[2m'; RESET='\033[0m'
RESET_MODE=false
[[ "$1" == "--reset" ]] && RESET_MODE=true

echo ""
echo "${CYAN}╔═══════════════════════════════════════════╗${RESET}"
echo "${CYAN}║  ArionComply — Local Postgres Setup       ║${RESET}"
echo "${CYAN}╚═══════════════════════════════════════════╝${RESET}"
echo ""

# ── Add postgres to PATH (Homebrew M1/M2) ────────────────────────────────────
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"

# ── Install Postgres if needed ────────────────────────────────────────────────
if ! command -v psql &>/dev/null; then
    echo "${DIM}Installing PostgreSQL 16 via Homebrew...${RESET}"
    brew install postgresql@16
    echo "${GREEN}✓ PostgreSQL installed${RESET}"
else
    echo "${GREEN}✓ PostgreSQL $(psql --version | grep -oE '[0-9]+\.[0-9]+' | head -1) found${RESET}"
fi

brew services start postgresql@16 2>/dev/null || true
sleep 2

# ── Reset if requested ────────────────────────────────────────────────────────
if $RESET_MODE; then
    echo "${DIM}Dropping existing databases...${RESET}"
    dropdb --if-exists arioncomply_compliance
    dropdb --if-exists arioncomply_sessions
    echo "  ${GREEN}✓ Databases dropped${RESET}"
fi

# ── Create databases ──────────────────────────────────────────────────────────
echo "${DIM}Creating databases...${RESET}"
for DB in arioncomply_compliance arioncomply_sessions; do
    if psql -lqt | cut -d\| -f1 | grep -qw "$DB"; then
        echo "  ${DIM}△ $DB already exists${RESET}"
    else
        createdb "$DB"
        echo "  ${GREEN}✓ $DB created${RESET}"
    fi
done

# ── Apply schema ──────────────────────────────────────────────────────────────
echo "${DIM}Applying compliance schema...${RESET}"
psql arioncomply_compliance < db/schema.sql > /tmp/schema_output.txt 2>&1

# Check for unexpected errors (ignore NOTICE and expected skips)
ERRORS=$(grep "^ERROR" /tmp/schema_output.txt || true)
if [[ -n "$ERRORS" ]]; then
    echo "  ${RED}⚠ Schema errors:${RESET}"
    echo "$ERRORS" | while read line; do echo "    $line"; done
else
    echo "  ${GREEN}✓ Schema applied cleanly${RESET}"
fi

# ── Create app user ───────────────────────────────────────────────────────────
echo "${DIM}Creating app user...${RESET}"
psql arioncomply_compliance << 'PSQL' > /dev/null 2>&1
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'arioncomply_app') THEN
        CREATE ROLE arioncomply_app WITH LOGIN PASSWORD 'arionlocal2026';
    END IF;
END $$;
GRANT CONNECT ON DATABASE arioncomply_compliance TO arioncomply_app;
GRANT USAGE ON SCHEMA public TO arioncomply_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO arioncomply_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO arioncomply_app;
ALTER ROLE arioncomply_app BYPASSRLS;
PSQL
echo "  ${GREEN}✓ App user ready${RESET}"

# ── Seed test tenant ──────────────────────────────────────────────────────────
echo "${DIM}Seeding Arion Networks test data...${RESET}"
psql arioncomply_compliance << 'PSQL' > /dev/null 2>&1
INSERT INTO tenants (id, name, slug, sector, subscription)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Arion Networks', 'arion-networks', 'technology', 'professional'
) ON CONFLICT (slug) DO NOTHING;

INSERT INTO applicable_standards (tenant_id, standard_id) VALUES
    ('00000000-0000-0000-0000-000000000001', 'ISO27001:2022'),
    ('00000000-0000-0000-0000-000000000001', 'GDPR:2016/679')
ON CONFLICT DO NOTHING;

INSERT INTO client_facts (tenant_id,
    processes_personal_data, eu_data_subjects, uk_data_subjects,
    role_controller, role_processor,
    uses_processors, uses_cloud_services,
    develops_software, has_remote_workers, has_physical_premises,
    sector)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    TRUE, TRUE, TRUE, TRUE, TRUE,
    TRUE, TRUE, TRUE, TRUE, TRUE, 'technology'
) ON CONFLICT (tenant_id) DO NOTHING;
PSQL
echo "  ${GREEN}✓ Test data seeded${RESET}"

# ── Update .env ───────────────────────────────────────────────────────────────
echo "${DIM}Updating .env...${RESET}"
COMP_URL="postgresql://arioncomply_app:arionlocal2026@localhost/arioncomply_compliance"
SESS_URL="postgresql://arioncomply_app:arionlocal2026@localhost/arioncomply_sessions"

# Find the .env file (script runs from $INGESTION)
ENV_FILE=".env"
if [[ ! -f "$ENV_FILE" ]]; then ENV_FILE="$(dirname $0)/../.env"; fi

if [[ -f "$ENV_FILE" ]]; then
    if grep -q "^DATABASE_URL=" "$ENV_FILE"; then
        sed -i '' "s|^DATABASE_URL=.*|DATABASE_URL=${COMP_URL}|" "$ENV_FILE"
    else
        printf "\n# Postgres\nDATABASE_URL=${COMP_URL}\n" >> "$ENV_FILE"
    fi
    if grep -q "^SESSIONS_DB_URL=" "$ENV_FILE"; then
        sed -i '' "s|^SESSIONS_DB_URL=.*|SESSIONS_DB_URL=${SESS_URL}|" "$ENV_FILE"
    else
        printf "SESSIONS_DB_URL=${SESS_URL}\n" >> "$ENV_FILE"
    fi
    echo "  ${GREEN}✓ .env updated${RESET}"
else
    echo "  ${DIM}△ .env not found — add these manually:${RESET}"
    echo "  DATABASE_URL=${COMP_URL}"
    echo "  SESSIONS_DB_URL=${SESS_URL}"
fi

# ── Verify ────────────────────────────────────────────────────────────────────
echo ""
TABLE_COUNT=$(psql arioncomply_compliance -tAc \
    "SELECT count(*) FROM information_schema.tables \
     WHERE table_schema='public' AND table_type='BASE TABLE'" 2>/dev/null || echo "?")
VIEW_COUNT=$(psql arioncomply_compliance -tAc \
    "SELECT count(*) FROM information_schema.views \
     WHERE table_schema='public'" 2>/dev/null || echo "?")
TENANT=$(psql arioncomply_compliance -tAc \
    "SELECT name FROM tenants LIMIT 1" 2>/dev/null || echo "?")

echo "${GREEN}✓ Postgres ready${RESET}"
echo "  Tables: ${TABLE_COUNT}   Views: ${VIEW_COUNT}"
echo "  Tenant: ${TENANT}"
echo ""
echo "${DIM}Connections:${RESET}"
echo "  psql arioncomply_compliance"
echo "  DATABASE_URL=${COMP_URL}"
echo ""
echo "${DIM}Useful commands:${RESET}"
echo "  psql arioncomply_compliance -c '\\dt'           # list tables"
echo "  psql arioncomply_compliance -c '\\dv'           # list views"
echo "  psql arioncomply_compliance -c 'SELECT * FROM retention_policies;'"
echo "  bash db/setup_local.sh --reset                 # drop and recreate"
echo ""
