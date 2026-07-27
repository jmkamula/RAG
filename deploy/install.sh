#!/usr/bin/env bash
# ArionComply — POC installer for a fresh Ubuntu 22.04+ VM.
# Idempotent: safe to re-run. Skips steps that are already complete.
#
# Prereqs:
#   - Ubuntu 22.04 or 24.04
#   - sudo access
#   - /data/arioncomply is the code root (this repo checked out)
#   - An OpenAI (or Anthropic) API key
#
# Usage:
#   bash deploy/install.sh
#
# Non-interactive / CI mode (all passwords via env):
#   ARION_OWNER_PW=... ARION_APP_PW=... NEO4J_PW=... OPENAI_KEY=... \
#     bash deploy/install.sh --yes
#
# What this does:
#   1. apt install postgresql-16, python3-pip, curl, lsof, git
#   2. Install Neo4j 5 from Neo4j apt repo
#   3. Bootstrap Postgres roles + databases + extensions
#   4. Apply schema_baseline.sql + seed_curator_data.sql +
#      schema_sessions_baseline.sql
#   5. pip install -r deploy/requirements.txt
#   6. Load Neo4j graph (framework role model + all curated content)
#   7. Provision Chroma data directory
#   8. Copy systemd units + enable + start
#   9. Write /data/arioncomply/.env from template
#  10. Print next steps

set -euo pipefail

ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
YES_MODE=0
for arg in "$@"; do
    case "$arg" in
        --yes|-y) YES_MODE=1 ;;
        *) echo "unknown arg: $arg"; exit 1 ;;
    esac
done

log()   { printf "\033[1;34m==>\033[0m %s\n" "$*"; }
warn()  { printf "\033[1;33m⚠\033[0m  %s\n" "$*"; }
ok()    { printf "\033[1;32m✓\033[0m  %s\n" "$*"; }
fail()  { printf "\033[1;31m✗\033[0m  %s\n" "$*"; exit 1; }
step()  { printf "\n\033[1;36m── %s ──\033[0m\n" "$*"; }

# Only prompt for a password if not already in env.
prompt_pw() {
    local var_name="$1"; local prompt_msg="$2"
    if [[ -n "${!var_name:-}" ]]; then return; fi
    if [[ "$YES_MODE" -eq 1 ]]; then
        fail "$var_name must be set in env when running with --yes"
    fi
    read -r -s -p "$prompt_msg: " value
    echo
    export "$var_name=$value"
}

step "0. Sanity checks"
[[ -d "$ARION_ROOT" ]] || fail "$ARION_ROOT does not exist — check out the repo there first"
[[ -f "$ARION_ROOT/db/baseline/schema_baseline.sql" ]] || \
    fail "schema_baseline.sql not found — is this the arioncomply repo?"
[[ -f "$ARION_ROOT/deploy/postgres_preamble.sql" ]] || \
    fail "postgres_preamble.sql not found"
[[ "$EUID" -eq 0 ]] && fail "run as a regular user with sudo, not as root"
ok "code root: $ARION_ROOT"

prompt_pw ARION_OWNER_PW  "Choose a password for the arioncomply Postgres role"
prompt_pw ARION_APP_PW    "Choose a password for the arioncomply_app Postgres role"
prompt_pw NEO4J_PW        "Choose a password for the neo4j user"
prompt_pw OPENAI_KEY      "OpenAI API key (leave blank if using another provider)"

# ── 1. System deps ───────────────────────────────────────────────────
step "1. System packages"
if ! dpkg -l postgresql-16 >/dev/null 2>&1; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq postgresql-16 python3 python3-pip curl lsof git
    ok "apt packages installed"
else
    ok "postgresql-16 already installed"
fi

# ── 2. Neo4j ────────────────────────────────────────────────────────
step "2. Neo4j"
if ! command -v neo4j >/dev/null 2>&1; then
    curl -fsSL https://debian.neo4j.com/neotechnology.gpg.key | \
        sudo gpg --dearmor -o /etc/apt/keyrings/neo4j.gpg
    echo "deb [signed-by=/etc/apt/keyrings/neo4j.gpg] https://debian.neo4j.com stable 5" | \
        sudo tee /etc/apt/sources.list.d/neo4j.list >/dev/null
    sudo apt-get update -qq
    sudo apt-get install -y -qq neo4j
    # Initial password bootstrap
    sudo systemctl stop neo4j || true
    sudo neo4j-admin dbms set-initial-password "$NEO4J_PW" 2>&1 | tail -1
    sudo systemctl enable --now neo4j
    ok "neo4j installed + running"
else
    ok "neo4j already installed"
fi

# Wait for Neo4j to be reachable
for i in {1..30}; do
    if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:7474/ | grep -q 200; then
        break
    fi
    sleep 2
done

# ── 3. Postgres bootstrap ────────────────────────────────────────────
step "3. Postgres roles + databases + extensions"
sudo systemctl enable --now postgresql
sudo -u postgres psql \
    -v arion_owner_pass="$ARION_OWNER_PW" \
    -v arion_app_pass="$ARION_APP_PW" \
    -f "$ARION_ROOT/deploy/postgres_preamble.sql" 2>&1 | tail -5
ok "roles + databases + extensions in place"

# ── 4. Schema + seed ─────────────────────────────────────────────────
step "4. Schema baseline + curator seed"
if sudo -u postgres psql -d arioncomply_compliance -tAc \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'" \
    | grep -q "^0$"; then
    sudo -u postgres psql -d arioncomply_compliance \
        -f "$ARION_ROOT/db/baseline/schema_baseline.sql" >/dev/null
    sudo -u postgres psql -d arioncomply_compliance \
        -f "$ARION_ROOT/db/baseline/seed_curator_data.sql" >/dev/null
    ok "compliance schema + curator seed applied"
else
    ok "compliance schema already exists — skipping"
fi

if sudo -u postgres psql -d arioncomply_sessions -tAc \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'" \
    | grep -q "^0$"; then
    sudo -u postgres psql -d arioncomply_sessions \
        -f "$ARION_ROOT/db/baseline/schema_sessions_baseline.sql" >/dev/null
    ok "sessions schema applied"
else
    ok "sessions schema already exists — skipping"
fi

# ── 5. Python dependencies ───────────────────────────────────────────
step "5. Python dependencies"
pip install --break-system-packages -q -r "$ARION_ROOT/deploy/requirements.txt"
ok "pip install complete"

# ── 6. .env from template ────────────────────────────────────────────
step "6. Environment file"
if [[ ! -f "$ARION_ROOT/.env" ]]; then
    cp "$ARION_ROOT/deploy/.env.example" "$ARION_ROOT/.env"
    # Substitute the values we have
    sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql://arioncomply_app:${ARION_APP_PW}@127.0.0.1/arioncomply_compliance|" \
        "$ARION_ROOT/.env"
    sed -i "s|SESSIONS_DATABASE_URL=.*|SESSIONS_DATABASE_URL=postgresql://arioncomply_app:${ARION_APP_PW}@127.0.0.1/arioncomply_sessions|" \
        "$ARION_ROOT/.env"
    sed -i "s|PGPASSWORD=.*|PGPASSWORD=${ARION_APP_PW}|" "$ARION_ROOT/.env"
    sed -i "s|NEO4J_PASSWORD=.*|NEO4J_PASSWORD=${NEO4J_PW}|" "$ARION_ROOT/.env"
    [[ -n "${OPENAI_KEY}" ]] && \
        sed -i "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=${OPENAI_KEY}|" "$ARION_ROOT/.env"
    chmod 600 "$ARION_ROOT/.env"
    ok ".env written with secrets"
else
    ok ".env already exists — not overwriting (review manually if needed)"
fi

# ── 7. Chroma data dir + systemd units ───────────────────────────────
step "7. Chroma dir + systemd units"
mkdir -p "$ARION_ROOT/chroma_db"

for unit in arioncomply-chroma.service arioncomply-api.service; do
    sudo install -m 0644 "$ARION_ROOT/ops/systemd/$unit" "/etc/systemd/system/$unit"
done
sudo systemctl daemon-reload
sudo systemctl enable arioncomply-chroma arioncomply-api

# Start Chroma first, then wait for its port, then API
if ! lsof -i :8000 -sTCP:LISTEN >/dev/null 2>&1; then
    sudo systemctl start arioncomply-chroma
    for i in {1..15}; do
        if curl -sf http://127.0.0.1:8000/api/v2/heartbeat >/dev/null; then
            break
        fi
        sleep 2
    done
    ok "Chroma running on :8000"
else
    warn "port 8000 already in use — leaving existing Chroma alone"
fi

# ── 8. Neo4j graph load ──────────────────────────────────────────────
step "8. Neo4j graph load (framework role model + all curated content)"
cd "$ARION_ROOT"
PYTHONPATH="$ARION_ROOT" python3 enrichment/documents/load_to_neo4j.py 2>&1 | tail -5
ok "graph loaded"

# ── 9. Start the API ─────────────────────────────────────────────────
step "9. ArionComply API"
if ! lsof -i :8080 -sTCP:LISTEN >/dev/null 2>&1; then
    sudo systemctl start arioncomply-api
    for i in {1..30}; do
        if curl -sf http://127.0.0.1:8080/docs >/dev/null; then
            break
        fi
        sleep 2
    done
    if curl -sf http://127.0.0.1:8080/docs >/dev/null; then
        ok "API up on :8080"
    else
        warn "API didn't come up in 60s — check: journalctl -u arioncomply-api -n 50"
    fi
else
    warn "port 8080 already in use — leaving existing API alone"
fi

# ── Summary ──────────────────────────────────────────────────────────
step "Install complete"
cat <<EOF

ArionComply is running. Next steps:

  1. Create your first tenant:
       cd $ARION_ROOT
       PYTHONPATH=. python3 scripts/dev/create_tenant.py --name "Your Corp"

  2. Rebuild Chroma indexes (first install, ~5-10 min):
       PYTHONPATH=. python3 scripts/reindex_all.py

  3. Verify health:
       curl -s http://127.0.0.1:8080/docs > /dev/null && echo OK

  4. Access the UI (SSH tunnel from your workstation):
       ssh -L 8080:127.0.0.1:8080 <user>@<this-vm>
       Then open http://localhost:8080/ in a browser.

  5. Optional — observability stack (Jaeger + Phoenix):
       sudo bash $ARION_ROOT/ops/install_jaeger.sh
       Then flip OTEL_ENABLED=1 in $ARION_ROOT/.env and:
       sudo systemctl restart arioncomply-api

Logs:
       sudo systemctl status arioncomply-{api,chroma}
       journalctl -u arioncomply-api -f
       tail -f /tmp/arioncomply-api.log

Environment file:
       $ARION_ROOT/.env   (chmod 600)

EOF
