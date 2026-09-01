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
    while :; do
        read -r -s -p "$prompt_msg: " value
        echo
        if [[ -n "$value" ]]; then break; fi
        warn "password cannot be empty — try again"
    done
    export "$var_name=$value"
}

# ── Neo4j helpers (used by step 2) ───────────────────────────────────
# Auth probe: returns 0 iff the given password authenticates against
# the running Neo4j Bolt endpoint. cypher-shell exits non-zero on
# either connection failure or auth failure.
neo4j_auth_ok() {
    local pw="$1"
    command -v cypher-shell >/dev/null 2>&1 || return 1
    printf "RETURN 1;" | \
        cypher-shell -u neo4j -p "$pw" --format plain >/dev/null 2>&1
}

# Password reset for Neo4j 5+. `set-initial-password` is bootstrap-
# only — it silently no-ops once the system database has been
# initialized. To make it bite again we wipe the entire data dir
# (databases + transactions + dbms bootstrap flag), then rerun
# set-initial-password before the first start. Graph content is
# lost by design here; step 8 rebuilds it from the catalog.
neo4j_reset_password() {
    local pw="$1"
    warn "Neo4j auth doesn't match NEO4J_PW — resetting"
    warn "  · wiping /var/lib/neo4j/data/{databases,transactions,dbms}"
    warn "  · graph content will be reloaded from catalog in step 8"
    sudo systemctl stop neo4j
    sudo rm -rf /var/lib/neo4j/data/databases \
                /var/lib/neo4j/data/transactions \
                /var/lib/neo4j/data/dbms
    sudo neo4j-admin dbms set-initial-password "$pw" 2>&1 | tail -1
    sudo systemctl start neo4j
    # Wait for Bolt (7687) — cypher-shell uses Bolt, not HTTP.
    for i in {1..30}; do
        if (timeout 1 bash -c 'cat < /dev/tcp/127.0.0.1/7687' >/dev/null 2>&1); then
            return 0
        fi
        sleep 2
    done
    return 1
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
    # Initial password bootstrap (fresh install path)
    sudo systemctl stop neo4j || true
    sudo neo4j-admin dbms set-initial-password "$NEO4J_PW" 2>&1 | tail -1
    sudo systemctl enable --now neo4j
    ok "neo4j installed + running"
else
    sudo systemctl enable --now neo4j
    ok "neo4j already installed"
fi

# Wait for Neo4j to be reachable (HTTP is a proxy — Bolt comes up around the same time)
for i in {1..30}; do
    if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:7474/ | grep -q 200; then
        break
    fi
    sleep 2
done

# Verify auth matches NEO4J_PW. Handles the case where Neo4j is
# already installed but with a different password (e.g. a prior
# install attempt with a different handoff.env, or a manual reset).
# `set-initial-password` is one-shot pre-bootstrap; if it's already
# bit and the current password is wrong, we have to nuke the system
# DB to redo bootstrap. Safe here because step 8 rebuilds the graph.
if neo4j_auth_ok "$NEO4J_PW"; then
    ok "Neo4j auth verified against NEO4J_PW"
else
    neo4j_reset_password "$NEO4J_PW" || fail "Neo4j password reset failed"
    if neo4j_auth_ok "$NEO4J_PW"; then
        ok "Neo4j auth reset — verified"
    else
        fail "Neo4j still not accepting NEO4J_PW after reset — check journalctl -u neo4j -n 50"
    fi
fi

# ── 3. Postgres bootstrap ────────────────────────────────────────────
step "3. Postgres roles + databases + extensions"
sudo systemctl enable --now postgresql
sudo -u postgres psql \
    -v arion_owner_pass="$ARION_OWNER_PW" \
    -v arion_app_pass="$ARION_APP_PW" \
    -f "$ARION_ROOT/deploy/postgres_preamble.sql" 2>&1 | tail -5
ok "roles + databases + extensions in place"

# ── 4. Schema + seed ─────────────────────────────────────────────────
# Detection uses a canonical LATE-created table (posture_controls,
# line ~1379 of schema_baseline.sql) rather than "any table in
# public" — the latter falsely-skips baseline on rerun after a
# partial crash where only a few early tables were created.
step "4. Schema baseline + curator seed"
if ! sudo -u postgres psql -d arioncomply_compliance -tAc \
        "SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='posture_controls'" \
        | grep -q "^1$"; then
    sudo -u postgres psql -d arioncomply_compliance \
        -f "$ARION_ROOT/db/baseline/schema_baseline.sql" >/dev/null
    sudo -u postgres psql -d arioncomply_compliance \
        -f "$ARION_ROOT/db/baseline/seed_curator_data.sql" >/dev/null
    ok "compliance schema + curator seed applied"
else
    ok "compliance schema already exists — skipping"
fi

# Sessions DB — LangGraph checkpointer creates `checkpoints` on
# its own if we don't; we still bootstrap it here so RLS grants
# etc land. Marker: the schema_sessions_baseline.sql seeds
# `checkpoints` (also late-created).
if ! sudo -u postgres psql -d arioncomply_sessions -tAc \
        "SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='checkpoints'" \
        | grep -q "^1$"; then
    sudo -u postgres psql -d arioncomply_sessions \
        -f "$ARION_ROOT/db/baseline/schema_sessions_baseline.sql" >/dev/null
    ok "sessions schema applied"
else
    ok "sessions schema already exists — skipping"
fi

# ── Post-baseline schema_v*.sql migrations ──
# schema_baseline.sql is a pg_dump snapshot of the fully-migrated
# dev DB — it already contains the effects of every schema_v*.sql
# file existing at the time the dump was taken. Track applied-
# migration state in a `schema_migrations` tracker so reruns skip
# already-applied files (CREATE POLICY has no IF NOT EXISTS guard,
# so unconditional replay is not safe).
#
# Bootstrap logic (Ship 102'.e): if the baseline was just applied
# but the tracker is empty, mark every schema_v*.sql file as
# already-applied. The baseline is understood to include their
# effects (that's what "regenerate baseline" means — it captures
# the current fully-migrated state).
#
# For customer boxes that got here via the OLD baseline (pre
# Ship 102'.a) + the incremental migration loop, the tracker
# either already has entries or the marker-based bootstrap in
# Ship 101' already fired. Fresh installs from the new baseline
# take this path.
sudo -u postgres psql -d arioncomply_compliance -v ON_ERROR_STOP=1 -c \
    "CREATE TABLE IF NOT EXISTS schema_migrations (
        version TEXT PRIMARY KEY,
        applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );" > /dev/null

# Auto-bootstrap on pre-existing installs (baseline applied, no
# tracker entries yet). Any staged schema_v*.sql files are
# considered baked into the baseline.
tracker_empty=$(sudo -u postgres psql -d arioncomply_compliance -tAc \
    "SELECT COUNT(*) FROM schema_migrations")
baseline_applied=$(sudo -u postgres psql -d arioncomply_compliance -tAc \
    "SELECT COUNT(*) FROM information_schema.tables
      WHERE table_schema='public' AND table_name='posture_controls'")
if [[ "$tracker_empty" == "0" && "$baseline_applied" == "1" ]]; then
    for f in "$ARION_ROOT"/db/schema_v*.sql; do
        v=$(basename "$f" .sql)
        sudo -u postgres psql -d arioncomply_compliance -c \
            "INSERT INTO schema_migrations (version) VALUES ('$v') ON CONFLICT DO NOTHING" >/dev/null
    done
    ok "schema_migrations bootstrapped from baseline snapshot ($(ls "$ARION_ROOT"/db/schema_v*.sql 2>/dev/null | wc -l) files marked applied)"
fi

# Apply un-applied migrations in numeric order. Fail loud on error.
applied_count=0
if compgen -G "$ARION_ROOT/db/schema_v*.sql" > /dev/null; then
    for f in $(ls "$ARION_ROOT"/db/schema_v*.sql | sort -V); do
        v=$(basename "$f" .sql)
        already=$(sudo -u postgres psql -d arioncomply_compliance -tAc \
            "SELECT 1 FROM schema_migrations WHERE version = '$v'")
        if [[ "$already" != "1" ]]; then
            sudo -u postgres psql -d arioncomply_compliance -v ON_ERROR_STOP=1 \
                -f "$f" > /dev/null 2>&1 \
                || fail "migration $v failed — inspect: sudo -u postgres psql -d arioncomply_compliance -f $f"
            sudo -u postgres psql -d arioncomply_compliance -c \
                "INSERT INTO schema_migrations (version) VALUES ('$v')" > /dev/null
            applied_count=$((applied_count + 1))
        fi
    done
    if [[ "$applied_count" -gt 0 ]]; then
        ok "applied $applied_count new schema_v*.sql migrations"
    else
        ok "schema_v*.sql migrations all up-to-date"
    fi
fi

# ── Ownership + grants reconciliation ──
# baseline SQL is a pg_dump snapshot with --no-owner --no-privileges,
# so tables end up owned by `postgres` (whoever runs the SQL) with
# no privileges to either app role. baseline_grants.sql reassigns
# ownership to `arioncomply` and grants the app role runtime privs.
# Run AFTER migrations so any migrations that create new tables get
# their ownership + grants set too. Idempotent: no-op when already correct.
sudo -u postgres psql -d arioncomply_compliance \
    -f "$ARION_ROOT/deploy/baseline_grants.sql" >/dev/null
sudo -u postgres psql -d arioncomply_sessions \
    -f "$ARION_ROOT/deploy/baseline_grants.sql" >/dev/null
ok "ownership + grants reconciled on both databases"

# ── 5. Python dependencies ───────────────────────────────────────────
step "5. Python dependencies"
pip install --break-system-packages -q -r "$ARION_ROOT/deploy/requirements.txt"
ok "pip install complete"

# ── 6. .env from template ────────────────────────────────────────────
# Secret substitution done in Python — sed would interpret pipe /
# ampersand / backslash / dollar in passwords, and won't URL-encode
# passwords that appear inside the postgresql:// connection strings.
step "6. Environment file"
if [[ ! -f "$ARION_ROOT/.env" ]]; then
    cp "$ARION_ROOT/deploy/.env.example" "$ARION_ROOT/.env"
    ARION_APP_PW="$ARION_APP_PW" NEO4J_PW="$NEO4J_PW" OPENAI_KEY="${OPENAI_KEY:-}" \
        ARION_ENV_PATH="$ARION_ROOT/.env" python3 - <<'PYEOF'
import os, re, urllib.parse
path      = os.environ["ARION_ENV_PATH"]
app_pw    = os.environ["ARION_APP_PW"]
neo4j_pw  = os.environ["NEO4J_PW"]
openai    = os.environ.get("OPENAI_KEY", "")
enc       = urllib.parse.quote_plus  # URL-encodes @ : / etc

subs = {
    "DATABASE_URL":         f"postgresql://arioncomply_app:{enc(app_pw)}@127.0.0.1/arioncomply_compliance",
    "SESSIONS_DATABASE_URL": f"postgresql://arioncomply_app:{enc(app_pw)}@127.0.0.1/arioncomply_sessions",
    "PGPASSWORD":           app_pw,
    "NEO4J_PASSWORD":       neo4j_pw,
}
if openai:
    subs["OPENAI_API_KEY"] = openai

with open(path) as f:
    text = f.read()
for k, v in subs.items():
    text = re.sub(rf"^{re.escape(k)}=.*$", f"{k}={v}", text, count=1, flags=re.M)
with open(path, "w") as f:
    f.write(text)
PYEOF
    chmod 600 "$ARION_ROOT/.env"
    ok ".env written with secrets"
else
    ok ".env already exists — not overwriting (review manually if needed)"
fi

# ── 7. Chroma data dir + systemd units ───────────────────────────────
# Units carry __ARION_USER__ placeholders — the invoking user (whoever
# ran install.sh) owns /data/arioncomply and has chroma at
# ~/.local/bin/chroma. Substitute at copy time so the unit files
# stay dev-host-agnostic.
step "7. Chroma dir + systemd units"
mkdir -p "$ARION_ROOT/chroma_db" "$ARION_ROOT/uploads"

# Ship 102'.e — extract prebuilt Chroma golden tar if present.
# Skips the expensive reindex_all step for the 5 rebuildable
# collections AND provides the 4 copyrighted collections that
# can't be rebuilt at customer sites (private/ PDFs are gitignored).
#
# The tar is >100 MB so it's not tracked in git — customer receives
# it out-of-band (secure file transfer) until Ship 103' ships the
# image repo. If the tar is missing, fall through to reindex_all
# which will build the 5 rebuildable collections + warn about
# the 4 missing.
CHROMA_TAR="$ARION_ROOT/db/baseline/chroma_prebuilt.tar.gz"
if [[ -f "$CHROMA_TAR" ]]; then
    if [[ -z "$(ls -A "$ARION_ROOT/chroma_db" 2>/dev/null)" ]]; then
        log "  · extracting chroma_prebuilt.tar.gz ($(du -h "$CHROMA_TAR" | cut -f1)) into $ARION_ROOT/chroma_db"
        tar -xzf "$CHROMA_TAR" -C "$ARION_ROOT/chroma_db"
        ok "  · Chroma prebuilt extracted"
    else
        ok "  · Chroma prebuilt available but chroma_db is non-empty — leaving alone"
    fi
else
    warn "  · Chroma prebuilt tar not found at $CHROMA_TAR"
    warn "    Customer install requires this file for the 4 copyrighted"
    warn "    collections (edpb_guidelines, iso27003/4/5). Copy it in place"
    warn "    before running install.sh, OR run reindex_all.py post-install"
    warn "    for the 5 rebuildable collections + accept the guidance gap."
fi

ARION_RUNTIME_USER="$(id -un)"
if [[ ! -x "/home/$ARION_RUNTIME_USER/.local/bin/chroma" ]]; then
    fail "chroma binary not found at /home/$ARION_RUNTIME_USER/.local/bin/chroma — did step 5 pip install run as this user?"
fi

for unit in arioncomply-chroma.service arioncomply-api.service \
            arioncomply-sweep.service arioncomply-sweep.timer; do
    sed -e "s|__ARION_USER__|$ARION_RUNTIME_USER|g" \
        "$ARION_ROOT/ops/systemd/$unit" \
    | sudo tee "/etc/systemd/system/$unit" >/dev/null
    sudo chmod 0644 "/etc/systemd/system/$unit"
done
sudo systemctl daemon-reload
# Clear any prior failed state before re-enabling (a prior install
# attempt with the wrong user hits "Start request repeated too quickly"
# and refuses to try again without reset-failed).
sudo systemctl reset-failed arioncomply-chroma arioncomply-api arioncomply-sweep.timer 2>/dev/null || true
# Enable services (arioncomply-sweep.service is oneshot, started by
# its timer — enable the timer, not the service itself).
sudo systemctl enable arioncomply-chroma arioncomply-api arioncomply-sweep.timer

# Start Chroma first, then wait for its port, then API
if ! lsof -i :8000 -sTCP:LISTEN >/dev/null 2>&1; then
    sudo systemctl start arioncomply-chroma
    chroma_up=0
    for i in {1..15}; do
        if curl -sf http://127.0.0.1:8000/api/v2/heartbeat >/dev/null; then
            chroma_up=1
            break
        fi
        sleep 2
    done
    if [[ "$chroma_up" -eq 1 ]]; then
        ok "Chroma running on :8000"
    else
        fail "Chroma didn't come up on :8000 in 30s — check: sudo journalctl -u arioncomply-chroma -n 30"
    fi
else
    warn "port 8000 already in use — leaving existing Chroma alone"
fi

# Start the sweep timer (fires the service every 30 min per its OnUnitActiveSec).
# The service itself is oneshot — no long-running process to health-check here.
sudo systemctl start arioncomply-sweep.timer
ok "arioncomply-sweep.timer enabled (fires every 30 min)"

# ── 8. Neo4j graph load ──────────────────────────────────────────────
# Ship 102'.e — prefer the consolidated golden loader (single JSON
# snapshot + single MERGE loader) when present. Falls back to the
# original 5-loader chain if the JSON baseline is missing.
#
# The consolidated path is verified byte-identical to the 5-loader
# output (Ship 102'.b: empty-DB load reproduces exact source state,
# 8148 nodes / 14378 rels, zero property drift).
#
# All loaders read NEO4J_PASSWORD via os.getenv. Bash keeps the
# value in $NEO4J_PW; export at the boundary.
step "8. Neo4j graph load (framework role model + all curated content)"
cd "$ARION_ROOT"

NEO4J_JSON="$ARION_ROOT/db/baseline/neo4j_baseline.json"
if [[ -f "$NEO4J_JSON" ]]; then
    log "  · loading via consolidated golden ($(du -h "$NEO4J_JSON" | cut -f1) JSON snapshot)"
    NEO4J_PASSWORD="$NEO4J_PW" PYTHONPATH="$ARION_ROOT" \
        python3 db/baseline/load_neo4j_baseline.py 2>&1 | tail -8
    ok "graph loaded from golden"
else
    warn "  · $NEO4J_JSON missing — falling back to 5-loader chain"
    warn "    (this path retires in Ship 103'; see db/AUTHORING.md)"

    log "  · loading RequirementNodes (iso + gdpr JSON)"
    NEO4J_PASSWORD="$NEO4J_PW" PYTHONPATH="$ARION_ROOT" \
        python3 load_neo4j.py 2>&1 | tail -3

    log "  · seeding ISO 27701 RequirementNodes"
    NEO4J_PASSWORD="$NEO4J_PW" PYTHONPATH="$ARION_ROOT" \
        python3 scripts/seed_27701_requirement_nodes.py 2>&1 | tail -3

    log "  · loading cross-framework relationship catalog"
    NEO4J_PASSWORD="$NEO4J_PW" PYTHONPATH="$ARION_ROOT" \
        python3 enrichment/relationships/load_to_neo4j.py 2>&1 | tail -3

    log "  · loading PART_OF hierarchy + control edges"
    NEO4J_PASSWORD="$NEO4J_PW" PYTHONPATH="$ARION_ROOT" \
        python3 load_graph_relationships.py 2>&1 | tail -3

    log "  · loading evidence layer (FulfilmentSpec + EvidenceRequirement + ChecklistItem)"
    NEO4J_PASSWORD="$NEO4J_PW" PYTHONPATH="$ARION_ROOT" \
        python3 enrichment/documents/load_to_neo4j.py 2>&1 | tail -3

    ok "graph loaded via legacy 5-loader chain"
fi

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

  2. Chroma indexes (Ship 102'.e):
     * If the golden tar was extracted in step 7, embeddings are
       already in place — no action needed.
     * Otherwise (missing db/baseline/chroma_prebuilt.tar.gz):
         PYTHONPATH=. python3 scripts/reindex_all.py
       Rebuilds 5 of 9 collections from Neo4j (~90s + ~\$2 OpenAI).
       The 4 copyrighted-source collections (edpb_guidelines +
       iso27003/4/5) will remain empty; chat over those standards
       loses advisory grounding until the tar is provided.

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
