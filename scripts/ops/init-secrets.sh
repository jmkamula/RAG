#!/usr/bin/env bash
#
# scripts/ops/init-secrets.sh — one-time secret provisioner.
#
# Runs on a fresh customer VM to generate (or prompt for) the 3
# credentials install.sh needs, then write /data/arioncomply/.env
# from deploy/.env.example. After this runs, install.sh becomes
# fully non-interactive — every subsequent invocation reads .env.
#
# Design (Ship 116', 2026-09-04):
#   · Default mode: auto-generate 3 strong random passwords (32-char
#     URL-safe from openssl / /dev/urandom). Prints them once for
#     the operator to capture into their password manager.
#   · --prompt mode: prompts each password with read -s (typed, not
#     shown). Useful for operators who prefer to bring their own.
#   · OpenAI key: cannot be auto-generated — always prompted (or
#     provided via --openai-key <k>). Blank is accepted (Chat
#     pipeline won't work without it but Postgres/Neo4j do).
#
# Refuses to overwrite an existing .env. If secrets need to rotate
# post-install, edit .env directly + restart arioncomply-api.
#
# Usage:
#   bash scripts/ops/init-secrets.sh                 # auto-generate + prompt for OpenAI key
#   bash scripts/ops/init-secrets.sh --prompt        # prompt for every secret
#   bash scripts/ops/init-secrets.sh --openai-key=sk-...   # skip OpenAI prompt
#
# Deploy pattern (fresh install):
#   ssh -i ~/.ssh/arion_operator_ed25519 arionops@<host>
#   cd /data/arioncomply
#   bash scripts/ops/init-secrets.sh
#   bash deploy/install.sh          # non-interactive from here on

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────
ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"

PROMPT_MODE=0
OPENAI_ARG=""

for arg in "$@"; do
    case "$arg" in
        --prompt)              PROMPT_MODE=1 ;;
        --openai-key=*)        OPENAI_ARG="${arg#*=}" ;;
        --openai-key)          echo "--openai-key needs a value (use --openai-key=<key>)" >&2; exit 64 ;;
        -h|--help)
            sed -n '3,/^set -euo/p' "$0" | sed 's/^#//' | sed '$d'
            exit 0 ;;
        *) echo "unknown arg: $arg" >&2; exit 64 ;;
    esac
done

# ── Pretty printers ──────────────────────────────────────────────
if [[ -t 1 ]]; then
    _ok()   { printf '\033[32m✓\033[0m %s\n' "$*"; }
    _warn() { printf '\033[33m!\033[0m %s\n' "$*"; }
    _err()  { printf '\033[31m✗\033[0m %s\n' "$*" >&2; }
    _bold() { printf '\033[1m%s\033[0m\n' "$*"; }
else
    _ok()   { printf 'OK:   %s\n' "$*"; }
    _warn() { printf 'WARN: %s\n' "$*"; }
    _err()  { printf 'ERR:  %s\n' "$*" >&2; }
    _bold() { printf '=== %s ===\n' "$*"; }
fi

# ── Guards ────────────────────────────────────────────────────────
[[ -d "$ARION_ROOT" ]] || {
    _err "$ARION_ROOT does not exist — is this the arioncomply host?"
    exit 78
}
[[ -f "$ARION_ROOT/deploy/.env.example" ]] || {
    _err "deploy/.env.example missing at $ARION_ROOT — check the repo layout"
    exit 78
}
if [[ -f "$ARION_ROOT/.env" ]]; then
    _err ".env already exists at $ARION_ROOT/.env"
    echo "  init-secrets.sh is a one-time bootstrap script by design." >&2
    echo "  To rotate a secret: edit .env directly + restart arioncomply-api." >&2
    echo "  To start over: delete .env manually first (LOSES ALL SECRETS)." >&2
    exit 1
fi

# ── Password generation helper ───────────────────────────────────
# 32 URL-safe chars from openssl (falls back to /dev/urandom).
# Trims / + = so passwords don't need URL-encoding when embedded
# in DATABASE_URL — the Python writer below quote_plus's anyway,
# but readable + copy-paste-safe passwords help operators.
_gen() {
    if command -v openssl >/dev/null 2>&1; then
        openssl rand -base64 32 | tr -d '/+=' | cut -c1-32
    else
        # POSIX fallback — 32 chars from base64-encoded /dev/urandom
        LC_ALL=C tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 32
        echo
    fi
}

# ── Prompt helper (for --prompt mode) ────────────────────────────
_prompt_pw() {
    local var="$1"; local msg="$2"
    local v
    while :; do
        read -r -s -p "  $msg: " v
        echo
        if [[ -n "$v" ]]; then
            printf -v "$var" '%s' "$v"
            export "$var"
            break
        fi
        _warn "password cannot be empty — try again"
    done
}

# ── Generate or prompt for the 3 database passwords ──────────────
_bold "init-secrets.sh — one-time secret provisioning"
echo "  target .env: $ARION_ROOT/.env"
echo "  mode:        $([[ $PROMPT_MODE -eq 1 ]] && echo 'prompt (typed)' || echo 'auto-generate')"
echo

if [[ "$PROMPT_MODE" -eq 1 ]]; then
    echo "Postgres + Neo4j credentials (typed, not shown):"
    _prompt_pw ARION_OWNER_PW  "arioncomply Postgres OWNER role password"
    _prompt_pw ARION_APP_PW    "arioncomply_app Postgres APP role password (RLS-scoped)"
    _prompt_pw NEO4J_PASSWORD  "Neo4j password"
else
    ARION_OWNER_PW="$(_gen)"
    ARION_APP_PW="$(_gen)"
    NEO4J_PASSWORD="$(_gen)"
    export ARION_OWNER_PW ARION_APP_PW NEO4J_PASSWORD
    _ok "generated 3 strong random passwords"
fi

# ── OpenAI key — always prompted (or via --openai-key=) ──────────
if [[ -n "$OPENAI_ARG" ]]; then
    OPENAI_API_KEY="$OPENAI_ARG"
    _ok "OpenAI key provided via --openai-key"
else
    echo
    echo "OpenAI API key (optional — Chat pipeline needs this; press Enter to skip):"
    read -r -s -p "  OPENAI_API_KEY: " OPENAI_API_KEY
    echo
fi
export OPENAI_API_KEY

# ── Write .env ────────────────────────────────────────────────────
cp "$ARION_ROOT/deploy/.env.example" "$ARION_ROOT/.env"
ARION_ENV_PATH="$ARION_ROOT/.env" python3 - <<'PYEOF'
import os, re, urllib.parse
path      = os.environ["ARION_ENV_PATH"]
app_pw    = os.environ["ARION_APP_PW"]
owner_pw  = os.environ["ARION_OWNER_PW"]
neo4j_pw  = os.environ["NEO4J_PASSWORD"]
openai    = os.environ.get("OPENAI_API_KEY", "")
enc       = urllib.parse.quote_plus  # URL-encodes @ : / etc

# Replace-or-append: substitute existing lines from the template,
# append any keys not in the template.
subs = {
    "DATABASE_URL":          f"postgresql://arioncomply_app:{enc(app_pw)}@127.0.0.1/arioncomply_compliance",
    "SESSIONS_DATABASE_URL": f"postgresql://arioncomply_app:{enc(app_pw)}@127.0.0.1/arioncomply_sessions",
    "PGPASSWORD":            app_pw,
    "ARION_OWNER_PW":        owner_pw,
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
_ok ".env written + chmod 600"

# ── Show generated passwords ONCE for operator capture ───────────
if [[ "$PROMPT_MODE" -eq 0 ]]; then
    echo
    _bold "Auto-generated secrets — STORE THESE NOW"
    echo "  (this is the only time they're printed; .env is chmod 600)"
    echo
    echo "  ARION_OWNER_PW  = $ARION_OWNER_PW"
    echo "  ARION_APP_PW    = $ARION_APP_PW"
    echo "  NEO4J_PASSWORD  = $NEO4J_PASSWORD"
    if [[ -n "$OPENAI_API_KEY" ]]; then
        echo "  OPENAI_API_KEY  = (redacted — from your input)"
    else
        echo "  OPENAI_API_KEY  = (not set — Chat pipeline won't work until you add one)"
    fi
    echo
fi

echo
_bold "Next steps"
echo "  1. Store the 3 database passwords in your password manager / handback notes."
echo "  2. Run: bash deploy/install.sh"
echo "     (install.sh reads .env from here on — no prompts.)"
