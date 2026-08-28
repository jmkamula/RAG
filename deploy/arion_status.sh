#!/usr/bin/env bash
# ArionComply — service status probe (Ship 47+ systemd shape).
#
# Successor to arion_start_azure.sh (which predates Ship 47's systemd
# cutover and points at the pre-systemd nohup layout).
#
# Two usage modes:
#
#   source deploy/arion_status.sh       # Load .env into current shell + print
#                                       # human-readable colored status.
#
#   bash deploy/arion_status.sh --json  # Print machine-parseable JSON, do
#                                       # NOT export env into current shell.
#                                       # Suitable for Claude Code + scripts.
#
# What it checks:
#   - Postgres (compliance + sessions DBs)
#   - Neo4j (bolt + node count)
#   - Chroma (HTTP heartbeat + collection count)
#   - ArionComply API (/api/v1/health or /docs)
#   - Sweep timer (systemd timer state + last run)
#   - Docs server (:8001, if running)
#
# Exit code: 0 if all critical services healthy, 1 if any critical service
# down. Docs server is non-critical.
#
# Ship 51'.a — Claude Code (per CLAUDE_OPERATOR.md) runs this between
# phases to confirm state before proceeding. Also usable from
# operator laptop via SSH: ssh <target> 'bash /data/arioncomply/deploy/arion_status.sh --json' | jq .

set -o pipefail

# Detect invocation shape
JSON_MODE=0
for arg in "$@"; do
    case "$arg" in
        --json) JSON_MODE=1 ;;
        --help|-h)
            grep '^#' "$0" | head -30 | sed 's/^# \?//'
            exit 0 ;;
    esac
done

# Colors (only when TTY + not JSON mode)
if [[ -t 1 && "$JSON_MODE" -eq 0 ]]; then
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
    CYAN='\033[0;36m'; DIM='\033[2m'; RESET='\033[0m'
else
    RED=''; GREEN=''; YELLOW=''; CYAN=''; DIM=''; RESET=''
fi

# ── Locate + source .env ─────────────────────────────────────────────
if [[ -n "${BASH_SOURCE[0]}" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fi
ARION_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$ARION_ROOT/.env"

env_loaded=0
if [[ -f "$ENV_FILE" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
    env_loaded=1
fi

# ── Probes ───────────────────────────────────────────────────────────

pg_check() {
    # Returns 0 if reachable + prints "<size_mb>|<control_count>" to stdout.
    if ! command -v pg_isready >/dev/null 2>&1; then
        echo "0|0"
        return 1
    fi
    if ! pg_isready -h "${PGHOST:-127.0.0.1}" -p "${PGPORT:-5432}" -U "${PGUSER:-arioncomply_app}" >/dev/null 2>&1; then
        echo "0|0"
        return 1
    fi
    local size_mb count
    size_mb=$(psql "${DATABASE_URL:-}" -tAc \
        "SELECT (pg_database_size(current_database())/1024/1024)::int" 2>/dev/null || echo 0)
    count=$(psql "${DATABASE_URL:-}" -tAc \
        "SELECT count(*) FROM posture_controls" 2>/dev/null || echo 0)
    echo "${size_mb:-0}|${count:-0}"
    return 0
}

neo4j_check() {
    # Returns 0 if reachable + prints node count to stdout.
    if ! command -v python3 >/dev/null 2>&1; then
        echo 0; return 1
    fi
    local out
    out=$(python3 - <<'PYEOF' 2>/dev/null
import os, sys
try:
    from neo4j import GraphDatabase
    d = GraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
        auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "")),
        connection_timeout=3,
    )
    with d.session() as s:
        print(s.run("MATCH (n) RETURN count(n) AS c").single()["c"])
    d.close()
except Exception:
    print("")
PYEOF
)
    if [[ -z "$out" || "$out" == "0" ]]; then
        echo 0; return 1
    fi
    echo "$out"; return 0
}

chroma_check() {
    # Returns 0 if HTTP heartbeat OK + prints collection count.
    local host="${CHROMA_HOST:-127.0.0.1}"
    local port="${CHROMA_PORT:-8000}"
    if ! curl -sf --max-time 3 "http://${host}:${port}/api/v2/heartbeat" >/dev/null 2>&1; then
        # Fallback: v1 heartbeat (older Chroma)
        if ! curl -sf --max-time 3 "http://${host}:${port}/api/v1/heartbeat" >/dev/null 2>&1; then
            echo 0; return 1
        fi
    fi
    # Collection count via chromadb client
    local count
    count=$(python3 - <<PYEOF 2>/dev/null
import os
try:
    import chromadb
    c = chromadb.HttpClient(host="${host}", port=${port})
    print(len(c.list_collections()))
except Exception:
    print("")
PYEOF
)
    echo "${count:-0}"; return 0
}

api_check() {
    # Returns 0 if API reachable.
    if curl -sf --max-time 3 "http://127.0.0.1:${API_PORT:-8080}/api/v1/health" >/dev/null 2>&1; then
        return 0
    fi
    # Fallback: /docs
    if curl -sf --max-time 3 "http://127.0.0.1:${API_PORT:-8080}/docs" >/dev/null 2>&1; then
        return 0
    fi
    return 1
}

systemd_state() {
    # Print "<unit> <active-state>" for each arion unit, or "no-systemd".
    if ! command -v systemctl >/dev/null 2>&1; then
        echo "no-systemd"
        return
    fi
    for u in arioncomply-api arioncomply-chroma arioncomply-jaeger arioncomply-phoenix arioncomply-sweep.timer; do
        printf '%s %s\n' "$u" "$(systemctl is-active "$u" 2>/dev/null || echo unknown)"
    done
}

git_state() {
    # Emit "sha branch dirty" (space-separated) for the ArionComply checkout.
    # dirty = "clean" or "dirty" depending on `git status --porcelain`.
    # Prints "unknown unknown unknown" if not a git checkout.
    if ! command -v git >/dev/null 2>&1 || [[ ! -d "$ARION_ROOT/.git" ]]; then
        echo "unknown unknown unknown"
        return
    fi
    local sha branch dirty
    sha=$(git -C "$ARION_ROOT" rev-parse --short=8 HEAD 2>/dev/null || echo unknown)
    branch=$(git -C "$ARION_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)
    if [[ -z "$(git -C "$ARION_ROOT" status --porcelain 2>/dev/null)" ]]; then
        dirty="clean"
    else
        dirty="dirty"
    fi
    printf '%s %s %s\n' "$sha" "$branch" "$dirty"
}

# ── Execute probes ───────────────────────────────────────────────────

PG_OUT="$(pg_check)"; PG_RC=$?
PG_SIZE="${PG_OUT%%|*}"; PG_COUNT="${PG_OUT##*|}"

NEO_COUNT="$(neo4j_check)"; NEO_RC=$?
CHROMA_COUNT="$(chroma_check)"; CHROMA_RC=$?
API_RC=1; api_check && API_RC=0

# Docs server on :8001 — non-critical.
DOCS_RC=1
curl -sf --max-time 2 "http://127.0.0.1:8001/" >/dev/null 2>&1 && DOCS_RC=0

# Git state — SHA + branch + dirty flag. Handy for status reports so
# operators (and Claude Code) can pin observations to a specific ref.
read -r GIT_SHA GIT_BRANCH GIT_DIRTY < <(git_state)

# ── Output ───────────────────────────────────────────────────────────

if [[ "$JSON_MODE" -eq 1 ]]; then
    # Emit JSON (single line) for Claude Code / scripts.
    printf '{'
    printf '"env_loaded":%s,' "$env_loaded"
    printf '"git":{"sha":"%s","branch":"%s","dirty":%s},' \
        "$GIT_SHA" "$GIT_BRANCH" \
        "$([[ "$GIT_DIRTY" == "dirty" ]] && echo true || echo false)"
    printf '"postgres":{"ok":%s,"size_mb":%s,"posture_controls":%s},' \
        "$([[ $PG_RC -eq 0 ]] && echo true || echo false)" "$PG_SIZE" "$PG_COUNT"
    printf '"neo4j":{"ok":%s,"nodes":%s},' \
        "$([[ $NEO_RC -eq 0 ]] && echo true || echo false)" "$NEO_COUNT"
    printf '"chroma":{"ok":%s,"collections":%s},' \
        "$([[ $CHROMA_RC -eq 0 ]] && echo true || echo false)" "$CHROMA_COUNT"
    printf '"api":{"ok":%s},' \
        "$([[ $API_RC -eq 0 ]] && echo true || echo false)"
    printf '"docs":{"ok":%s},' \
        "$([[ $DOCS_RC -eq 0 ]] && echo true || echo false)"
    printf '"systemd":['
    first=1
    while read -r unit state; do
        [[ -z "$unit" ]] && continue
        [[ $first -eq 0 ]] && printf ','
        printf '{"unit":"%s","active":"%s"}' "$unit" "$state"
        first=0
    done < <(systemd_state)
    printf ']'
    printf '}\n'
else
    # Human-readable colored status.
    echo ""
    echo -e "${CYAN}╔═════════════════════════════════════╗${RESET}"
    echo -e "${CYAN}║   ArionComply — Service Status      ║${RESET}"
    echo -e "${CYAN}╚═════════════════════════════════════╝${RESET}"
    echo ""
    if [[ $env_loaded -eq 1 ]]; then
        echo -e "${GREEN}✓ .env loaded${RESET}          ($ENV_FILE)"
    else
        echo -e "${YELLOW}△ .env not found${RESET}      ($ENV_FILE)"
    fi
    # Git ref — helps pin any observation to a specific commit.
    if [[ "$GIT_SHA" != "unknown" ]]; then
        if [[ "$GIT_DIRTY" == "dirty" ]]; then
            echo -e "${YELLOW}◆ Codebase${RESET}            ${GIT_SHA} ${DIM}(${GIT_BRANCH}, dirty)${RESET}"
        else
            echo -e "${GREEN}◆ Codebase${RESET}            ${GIT_SHA} ${DIM}(${GIT_BRANCH})${RESET}"
        fi
    else
        echo -e "${YELLOW}◆ Codebase${RESET}            not a git checkout"
    fi
    echo ""
    echo -e "${DIM}Checking services...${RESET}"

    if [[ $PG_RC -eq 0 ]]; then
        echo -e "${GREEN}✓ PostgreSQL${RESET}          ${PG_SIZE}MB, ${PG_COUNT} posture_controls"
    else
        echo -e "${RED}✗ PostgreSQL${RESET}          not reachable"
        echo -e "  ${DIM}→ sudo systemctl start postgresql${RESET}"
    fi

    if [[ $NEO_RC -eq 0 ]]; then
        echo -e "${GREEN}✓ Neo4j${RESET}               ${NEO_COUNT} nodes"
    else
        echo -e "${RED}✗ Neo4j${RESET}               offline"
        echo -e "  ${DIM}→ sudo systemctl start neo4j${RESET}"
    fi

    if [[ $CHROMA_RC -eq 0 ]]; then
        echo -e "${GREEN}✓ Chroma${RESET}              ${CHROMA_COUNT} collections on :${CHROMA_PORT:-8000}"
    else
        echo -e "${RED}✗ Chroma${RESET}              not reachable"
        echo -e "  ${DIM}→ sudo systemctl start arioncomply-chroma${RESET}"
    fi

    if [[ $API_RC -eq 0 ]]; then
        echo -e "${GREEN}✓ ArionComply API${RESET}     :${API_PORT:-8080}"
    else
        echo -e "${RED}✗ ArionComply API${RESET}     not reachable"
        echo -e "  ${DIM}→ sudo systemctl start arioncomply-api${RESET}"
    fi

    if [[ $DOCS_RC -eq 0 ]]; then
        echo -e "${GREEN}✓ Docs server${RESET}         :8001"
    else
        echo -e "${DIM}· Docs server${RESET}         not running (optional)"
    fi

    echo ""
    echo -e "${DIM}Systemd units:${RESET}"
    while read -r unit state; do
        [[ -z "$unit" ]] && continue
        if [[ "$state" == "active" ]]; then
            echo -e "  ${GREEN}✓${RESET} $unit"
        elif [[ "$state" == "unknown" || "$state" == "no-systemd" ]]; then
            echo -e "  ${YELLOW}?${RESET} $unit ($state)"
        else
            echo -e "  ${RED}✗${RESET} $unit ($state)"
        fi
    done < <(systemd_state)

    echo ""
    if [[ $PG_RC -eq 0 && $NEO_RC -eq 0 && $CHROMA_RC -eq 0 && $API_RC -eq 0 ]]; then
        echo -e "${GREEN}✓ All critical services ready${RESET}"
    else
        echo -e "${YELLOW}△ Some critical services down (see above)${RESET}"
    fi
    echo ""
    echo -e "${DIM}Tip:${RESET}"
    echo -e "  ${CYAN}curl -sf -H \"X-API-Key: \$KEY\" http://127.0.0.1:${API_PORT:-8080}/api/v1/admin/deployment/status | jq${RESET}"
    echo -e "  ${CYAN}bash scripts/ops/diagnose.sh${RESET}     # produce diagnostic bundle"
    echo ""
fi

# Exit code: 0 if all critical services healthy, 1 otherwise.
if [[ $PG_RC -eq 0 && $NEO_RC -eq 0 && $CHROMA_RC -eq 0 && $API_RC -eq 0 ]]; then
    return 0 2>/dev/null || exit 0
else
    return 1 2>/dev/null || exit 1
fi
