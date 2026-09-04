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
#   ARION_OWNER_PW=... ARION_APP_PW=... NEO4J_PASSWORD=... OPENAI_API_KEY=... \
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
    warn "Neo4j auth doesn't match NEO4J_PASSWORD — resetting"
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

# ── Update-friendly secret loader (Ship 111'.a) ──────────────────
# If .env exists (i.e. a prior install has already run), read its
# secrets so prompt_pw skips them. Only genuinely-missing values
# trigger interactive prompts — critical for SSH one-liner updates
# where stdin is not a TTY.
#
# Ship 111'.a canonicalizes install-time + runtime variable names
# so this loader is a straight read (not a translation table):
#
#   ARION_OWNER_PW  — owner Postgres role password
#   OPENAI_API_KEY  — OpenAI API key
#   NEO4J_PASSWORD  — Neo4j password
#   ARION_APP_PW    — app Postgres role password (install-time only;
#                     runtime code reads app pw from DATABASE_URL)
#
# ARION_APP_PW isn't stored in .env directly — it's embedded in
# DATABASE_URL. For update-mode we parse it back out here.
if [[ -f "$ARION_ROOT/.env" ]]; then
    _read_env_var() {
        # Read a KEY=value from .env safely without executing shell
        # substitutions. Handles bare, single-, and double-quoted values.
        local key="$1"
        grep -E "^${key}=" "$ARION_ROOT/.env" | head -1 | \
            sed -E "s/^${key}=//; s/^\"(.*)\"\$/\1/; s/^'(.*)'\$/\1/"
    }
    _url_decode() {
        # POSIX %XX decoder for DATABASE_URL password field.
        printf '%b' "$(printf '%s' "$1" | \
            sed 's/+/ /g; s/%\([0-9A-Fa-f][0-9A-Fa-f]\)/\\x\1/g')"
    }

    : "${ARION_OWNER_PW:=$(_read_env_var ARION_OWNER_PW)}"
    : "${OPENAI_API_KEY:=$(_read_env_var OPENAI_API_KEY)}"
    : "${NEO4J_PASSWORD:=$(_read_env_var NEO4J_PASSWORD)}"

    # DATABASE_URL shape: postgresql://arioncomply_app:PASSWORD@host/db
    if [[ -z "${ARION_APP_PW:-}" ]]; then
        _db_url=$(_read_env_var DATABASE_URL)
        if [[ "$_db_url" =~ ^postgresql://[^:]+:([^@]+)@ ]]; then
            ARION_APP_PW=$(_url_decode "${BASH_REMATCH[1]}")
            export ARION_APP_PW
        fi
    fi

    if [[ -n "${OPENAI_API_KEY:-}${NEO4J_PASSWORD:-}${ARION_APP_PW:-}${ARION_OWNER_PW:-}" ]]; then
        ok "loaded existing secrets from .env (update mode — missing values will be prompted)"
    fi
fi

prompt_pw ARION_OWNER_PW  "Choose a password for the arioncomply Postgres role"
prompt_pw ARION_APP_PW    "Choose a password for the arioncomply_app Postgres role"
prompt_pw NEO4J_PASSWORD  "Choose a password for the neo4j user"
prompt_pw OPENAI_API_KEY  "OpenAI API key (leave blank if using another provider)"

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
    sudo neo4j-admin dbms set-initial-password "$NEO4J_PASSWORD" 2>&1 | tail -1
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

# Verify auth matches NEO4J_PASSWORD. Handles the case where Neo4j is
# already installed but with a different password (e.g. a prior
# install attempt with a different handoff.env, or a manual reset).
# `set-initial-password` is one-shot pre-bootstrap; if it's already
# bit and the current password is wrong, we have to nuke the system
# DB to redo bootstrap. Safe here because step 8 rebuilds the graph.
if neo4j_auth_ok "$NEO4J_PASSWORD"; then
    ok "Neo4j auth verified against NEO4J_PASSWORD"
else
    neo4j_reset_password "$NEO4J_PASSWORD" || fail "Neo4j password reset failed"
    if neo4j_auth_ok "$NEO4J_PASSWORD"; then
        ok "Neo4j auth reset — verified"
    else
        fail "Neo4j still not accepting NEO4J_PASSWORD after reset — check journalctl -u neo4j -n 50"
    fi
fi

# ── 3. Postgres bootstrap ────────────────────────────────────────────
# Ship 104'.b addendum: verify BOTH role passwords work after the
# preamble. Earlier customer install had the arioncomply owner role
# with a stale password (root cause never fully pinned down —
# possibly a psql-variable pass-through issue or a rerun with a
# different ARION_OWNER_PW). The Quickstart flow needs the owner
# connection to bypass RLS on tenants; a broken owner password fails
# silently and looks like "bootstrap unavailable" from the UI.
step "3. Postgres roles + databases + extensions"
sudo systemctl enable --now postgresql
sudo -u postgres psql \
    -v arion_owner_pass="$ARION_OWNER_PW" \
    -v arion_app_pass="$ARION_APP_PW" \
    -f "$ARION_ROOT/deploy/postgres_preamble.sql" 2>&1 | tail -5

# Verify both role logins work.
if ! PGPASSWORD="$ARION_OWNER_PW" psql -h 127.0.0.1 -U arioncomply \
        -d arioncomply_compliance -tAc "SELECT 1" >/dev/null 2>&1; then
    fail "arioncomply (owner) role login failed with ARION_OWNER_PW — check psql -v pass-through in postgres_preamble.sql"
fi
if ! PGPASSWORD="$ARION_APP_PW" psql -h 127.0.0.1 -U arioncomply_app \
        -d arioncomply_compliance -tAc "SELECT 1" >/dev/null 2>&1; then
    fail "arioncomply_app (runtime) role login failed with ARION_APP_PW — check psql -v pass-through in postgres_preamble.sql"
fi

ok "roles + databases + extensions in place (both role logins verified)"

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
# Ship 111'.d — accumulate applied-migration names into APPLIED_MIGRATIONS
# so the deployment log at the end can record what actually landed.
applied_count=0
APPLIED_MIGRATIONS=()
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
            APPLIED_MIGRATIONS+=("$v")
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
# Ship 111'.a — the writer runs on BOTH first-install and update paths.
# On first install: copy the template, substitute every secret.
# On update: ensure ARION_OWNER_PW is present (it wasn't stashed in
# pre-111 installs); every other secret we recognize was already
# stashed correctly on first install.
if [[ ! -f "$ARION_ROOT/.env" ]]; then
    cp "$ARION_ROOT/deploy/.env.example" "$ARION_ROOT/.env"
    ARION_APP_PW="$ARION_APP_PW" ARION_OWNER_PW="$ARION_OWNER_PW" \
        NEO4J_PASSWORD="$NEO4J_PASSWORD" OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
        ARION_ENV_PATH="$ARION_ROOT/.env" python3 - <<'PYEOF'
import os, re, urllib.parse
path      = os.environ["ARION_ENV_PATH"]
app_pw    = os.environ["ARION_APP_PW"]
owner_pw  = os.environ["ARION_OWNER_PW"]
neo4j_pw  = os.environ["NEO4J_PASSWORD"]
openai    = os.environ.get("OPENAI_API_KEY", "")
enc       = urllib.parse.quote_plus  # URL-encodes @ : / etc

# Replace-or-append: if the key exists in the template, substitute the
# value; if not (older template, hand-edited .env), append the line at
# the end. Preserves all existing keys and comments.
subs = {
    "DATABASE_URL":          f"postgresql://arioncomply_app:{enc(app_pw)}@127.0.0.1/arioncomply_compliance",
    "SESSIONS_DATABASE_URL": f"postgresql://arioncomply_app:{enc(app_pw)}@127.0.0.1/arioncomply_sessions",
    "PGPASSWORD":            app_pw,
    "ARION_OWNER_PW":        owner_pw,       # Ship 111'.a
    "NEO4J_PASSWORD":        neo4j_pw,
}
if openai:
    subs["OPENAI_API_KEY"] = openai

with open(path) as f:
    text = f.read()
for k, v in subs.items():
    pattern = rf"^{re.escape(k)}=.*$"
    if re.search(pattern, text, flags=re.M):
        text = re.sub(pattern, f"{k}={v}", text, count=1, flags=re.M)
    else:
        if not text.endswith("\n"):
            text += "\n"
        text += f"{k}={v}\n"
with open(path, "w") as f:
    f.write(text)
PYEOF
    chmod 600 "$ARION_ROOT/.env"
    ok ".env written with secrets"
else
    # Update path — ensure ARION_OWNER_PW landed in the file. This is
    # a one-time backfill for pre-111 installs; harmless on 111+ boxes
    # where the fresh writer already put it there.
    if grep -qE "^ARION_OWNER_PW=" "$ARION_ROOT/.env"; then
        ok ".env already has ARION_OWNER_PW — no change"
    else
        # Append via a tempfile the invoking user can write (arionops
        # owns .env; sudo tee would work too but keeps ownership).
        printf '\n# Ship 111 — stashed for install.sh update mode\nARION_OWNER_PW=%s\n' \
            "$ARION_OWNER_PW" >> "$ARION_ROOT/.env"
        chmod 600 "$ARION_ROOT/.env"
        ok ".env: appended ARION_OWNER_PW for future update runs"
    fi
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
    # Ship 103'.a — the tar is stored in Git LFS. If git-lfs isn't
    # installed / initialized, `git pull` leaves a pointer file
    # (~130 bytes) instead of the real 141 MiB tar. Detect this
    # early and fail loud with recovery instructions.
    tar_size=$(stat -c%s "$CHROMA_TAR")
    if [[ "$tar_size" -lt 1000000 ]]; then
        fail "$CHROMA_TAR is $tar_size bytes — this is a Git LFS pointer, not the real tar.
Install LFS + re-pull:
    sudo apt install git-lfs
    git lfs install
    git -C $ARION_ROOT lfs pull"
    fi

    if [[ -z "$(ls -A "$ARION_ROOT/chroma_db" 2>/dev/null)" ]]; then
        log "  · extracting chroma_prebuilt.tar.gz ($(du -h "$CHROMA_TAR" | cut -f1)) into $ARION_ROOT/chroma_db"
        tar -xzf "$CHROMA_TAR" -C "$ARION_ROOT/chroma_db"
        ok "  · Chroma prebuilt extracted"
    else
        ok "  · Chroma prebuilt available but chroma_db is non-empty — leaving alone"
    fi
else
    warn "  · Chroma prebuilt tar not found at $CHROMA_TAR"
    warn "    This file is stored via Git LFS. Install git-lfs and re-pull:"
    warn "        sudo apt install git-lfs"
    warn "        git lfs install"
    warn "        git -C $ARION_ROOT lfs pull"
    warn "    Alternatively, run reindex_all.py post-install for the 5"
    warn "    rebuildable collections + accept the guidance gap for the 4"
    warn "    copyrighted collections (edpb_guidelines, iso27003/4/5)."
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
# value in $NEO4J_PASSWORD; export at the boundary.
step "8. Neo4j graph load (framework role model + all curated content)"
cd "$ARION_ROOT"

NEO4J_JSON="$ARION_ROOT/db/baseline/neo4j_baseline.json"
if [[ -f "$NEO4J_JSON" ]]; then
    log "  · loading via consolidated golden ($(du -h "$NEO4J_JSON" | cut -f1) JSON snapshot)"
    NEO4J_PASSWORD="$NEO4J_PASSWORD" PYTHONPATH="$ARION_ROOT" \
        python3 db/baseline/load_neo4j_baseline.py 2>&1 | tail -8
    ok "graph loaded from golden"
else
    warn "  · $NEO4J_JSON missing — falling back to 5-loader chain"
    warn "    (this path retires in Ship 103'; see db/AUTHORING.md)"

    log "  · loading RequirementNodes (iso + gdpr JSON)"
    NEO4J_PASSWORD="$NEO4J_PASSWORD" PYTHONPATH="$ARION_ROOT" \
        python3 load_neo4j.py 2>&1 | tail -3

    log "  · seeding ISO 27701 RequirementNodes"
    NEO4J_PASSWORD="$NEO4J_PASSWORD" PYTHONPATH="$ARION_ROOT" \
        python3 scripts/seed_27701_requirement_nodes.py 2>&1 | tail -3

    log "  · loading cross-framework relationship catalog"
    NEO4J_PASSWORD="$NEO4J_PASSWORD" PYTHONPATH="$ARION_ROOT" \
        python3 enrichment/relationships/load_to_neo4j.py 2>&1 | tail -3

    log "  · loading PART_OF hierarchy + control edges"
    NEO4J_PASSWORD="$NEO4J_PASSWORD" PYTHONPATH="$ARION_ROOT" \
        python3 load_graph_relationships.py 2>&1 | tail -3

    log "  · loading evidence layer (FulfilmentSpec + EvidenceRequirement + ChecklistItem)"
    NEO4J_PASSWORD="$NEO4J_PASSWORD" PYTHONPATH="$ARION_ROOT" \
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

# ── Deployment log (Ship 111'.d) ─────────────────────────────────────
# Append one JSON line to .deployment_log.jsonl capturing what
# actually ran this invocation. Machine-parseable for future automated
# deploy scripts + human-readable enough via `jq`. Append-only,
# chmod 600. Never edited by hand.
#
# Schema (per line):
#   {
#     "ts":                UTC ISO-8601,
#     "git_sha":           short SHA of HEAD at install.sh run time,
#     "git_branch":        branch name at run time,
#     "git_subject":       commit subject line (helps humans skim),
#     "migrations_applied":[...],   # empty when no new SQL fired
#     "invoker":           $USER,
#     "invoker_sudo":      $SUDO_USER if set,
#     "hostname":          from `hostname -s`,
#     "install_sh_step_9": "started" | "already_running",
#     "outcome":           "GREEN"  # fail() exits before we reach here
#   }
DEPLOY_LOG="$ARION_ROOT/.deployment_log.jsonl"
_git_sha=$(cd "$ARION_ROOT" && git rev-parse --short HEAD 2>/dev/null || echo "")
_git_branch=$(cd "$ARION_ROOT" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
_git_subject=$(cd "$ARION_ROOT" && git log -1 --format='%s' 2>/dev/null || echo "")
_ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
_hostname=$(hostname -s 2>/dev/null || echo "")
_step9_state=$(lsof -i :8080 -sTCP:LISTEN >/dev/null 2>&1 && echo "already_running" || echo "not_running")

# Build migrations_applied JSON array. Empty when no new migrations
# fired this run.
if [[ ${#APPLIED_MIGRATIONS[@]} -eq 0 ]]; then
    _migs="[]"
else
    _migs="["
    for m in "${APPLIED_MIGRATIONS[@]}"; do
        _migs+="\"$m\","
    done
    _migs="${_migs%,}]"
fi

# jq keeps quoting sane. Fall back to sed-escape if jq unavailable
# (unusual on a customer box that has curl + postgres + python
# already installed via step 1).
if command -v jq >/dev/null 2>&1; then
    _log_line=$(jq -cn \
        --arg ts "$_ts" --arg sha "$_git_sha" --arg br "$_git_branch" \
        --arg subj "$_git_subject" --arg inv "${USER:-unknown}" \
        --arg su "${SUDO_USER:-}" --arg host "$_hostname" \
        --arg s9 "$_step9_state" --argjson migs "$_migs" \
        '{ts:$ts, git_sha:$sha, git_branch:$br, git_subject:$subj,
          migrations_applied:$migs, invoker:$inv, invoker_sudo:$su,
          hostname:$host, install_sh_step_9:$s9, outcome:"GREEN"}')
else
    # Minimal fallback — sed-escape strings.
    _esc() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }
    _log_line="{\"ts\":\"$_ts\",\"git_sha\":\"$_git_sha\","
    _log_line+="\"git_branch\":\"$(_esc "$_git_branch")\","
    _log_line+="\"git_subject\":\"$(_esc "$_git_subject")\","
    _log_line+="\"migrations_applied\":$_migs,"
    _log_line+="\"invoker\":\"${USER:-unknown}\","
    _log_line+="\"invoker_sudo\":\"${SUDO_USER:-}\","
    _log_line+="\"hostname\":\"$_hostname\","
    _log_line+="\"install_sh_step_9\":\"$_step9_state\","
    _log_line+="\"outcome\":\"GREEN\"}"
fi

# Append + chmod 600 (may contain hostname/user; not secrets, but
# same chmod as .env for consistency).
echo "$_log_line" >> "$DEPLOY_LOG"
chmod 600 "$DEPLOY_LOG"
ok "deployment log appended: $DEPLOY_LOG"

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
