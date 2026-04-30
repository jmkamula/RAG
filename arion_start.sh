#!/usr/bin/env zsh
# ArionComply — Environment Initialisation Script
#
# Usage:
#   source arion_start.sh        (sets env in current shell)
#   ./arion_start.sh             (runs in subshell — env not persisted)

# ── Colours ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
DIM='\033[2m'
RESET='\033[0m'

# ── Find script location (zsh-safe) ───────────────────────────────────────────
if [[ -n "${ZSH_VERSION}" ]]; then
    INGESTION_DIR="${0:A:h}"
elif [[ -n "${BASH_VERSION}" ]]; then
    INGESTION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    INGESTION_DIR="$(pwd)"
fi
ENV_FILE="$INGESTION_DIR/.env"

echo ""
echo "${CYAN}╔══════════════════════════════════════╗${RESET}"
echo "${CYAN}║   ArionComply — Environment Setup    ║${RESET}"
echo "${CYAN}╚══════════════════════════════════════╝${RESET}"
echo ""

# ── Load .env ─────────────────────────────────────────────────────────────────
if [[ ! -f "$ENV_FILE" ]]; then
    echo "${RED}✗ .env not found at $ENV_FILE${RESET}"
    echo "  Copy .env.example to .env and fill in your values"
    return 1 2>/dev/null || exit 1
fi

# Export all non-comment, non-empty lines — using zsh-safe approach
while IFS='=' read -r key value; do
    [[ "$key" =~ ^[[:space:]]*# ]] && continue
    [[ -z "$key" ]] && continue
    key="${key// /}"
    value="${value%%#*}"       # strip inline comments
    value="${value%"${value##*[! ]}"}"  # strip trailing whitespace
    export "$key=$value"
done < "$ENV_FILE"

echo "${GREEN}✓ Environment loaded${RESET}  ($ENV_FILE)"

# ── Check ChromaDB ────────────────────────────────────────────────────────────
echo ""
echo "${DIM}Checking services...${RESET}"

CHROMA_OK=false
if curl -s --max-time 2 "http://${CHROMA_HOST:-localhost}:${CHROMA_PORT:-8000}/api/v1/heartbeat" > /dev/null 2>&1; then
    echo "${GREEN}✓ ChromaDB${RESET}    running on port ${CHROMA_PORT:-8000}"
    CHROMA_OK=true
else
    echo "${YELLOW}△ ChromaDB${RESET}    not running"
    echo "  ${DIM}Start: chroma run --path ~/chromadb_data --port ${CHROMA_PORT:-8000}${RESET}"
fi

# ── Check Neo4j ───────────────────────────────────────────────────────────────
NEO4J_OK=false
NODE_COUNT=$(python3 - <<PYEOF 2>/dev/null
from neo4j import GraphDatabase
try:
    d = GraphDatabase.driver("bolt://127.0.0.1:7687",
                              auth=("neo4j", "${NEO4J_PASSWORD}"),
                              connection_timeout=3)
    with d.session() as s:
        print(s.run("MATCH (n) RETURN count(n) as c").single()["c"])
    d.close()
except:
    print("")
PYEOF
)

if [[ -n "$NODE_COUNT" && "$NODE_COUNT" -gt 0 ]]; then
    echo "${GREEN}✓ Neo4j${RESET}       online ($NODE_COUNT nodes)"
    NEO4J_OK=true
else
    echo "${YELLOW}△ Neo4j${RESET}       offline — start the database in Neo4j Desktop"
fi

# ── Check/Start SSH tunnel ────────────────────────────────────────────────────
LOCAL_PORT="${RUNPOD_TUNNEL_LOCAL_PORT:-9000}"
REMOTE_PORT="${RUNPOD_TUNNEL_REMOTE_PORT:-8000}"
TUNNEL_OK=false

if lsof -i ":$LOCAL_PORT" > /dev/null 2>&1; then
    echo "${GREEN}✓ SSH tunnel${RESET}  localhost:$LOCAL_PORT already open"
    TUNNEL_OK=true
else
    echo "${DIM}  Opening SSH tunnel to RunPod...${RESET}"
    ssh \
        -L "${LOCAL_PORT}:localhost:${REMOTE_PORT}" \
        "root@${RUNPOD_IP}" \
        -p "${RUNPOD_SSH_PORT}" \
        -i "${RUNPOD_SSH_KEY}" \
        -N \
        -o ServerAliveInterval=30 \
        -o ServerAliveCountMax=10 \
        -o StrictHostKeyChecking=no \
        -o ConnectTimeout=5 \
        -f 2>/dev/null

    sleep 2
    if lsof -i ":$LOCAL_PORT" > /dev/null 2>&1; then
        echo "${GREEN}✓ SSH tunnel${RESET}  opened on localhost:$LOCAL_PORT"
        TUNNEL_OK=true
    else
        echo "${RED}✗ SSH tunnel${RESET}  failed — is RunPod pod running?"
        echo "  ${DIM}Pod: ${RUNPOD_POD_ID}  IP: ${RUNPOD_IP}:${RUNPOD_SSH_PORT}${RESET}"
    fi
fi

# ── Check Mistral ─────────────────────────────────────────────────────────────
MISTRAL_OK=false
if $TUNNEL_OK; then
    MISTRAL_RESP=$(curl -s --max-time 3 "http://localhost:$LOCAL_PORT/v1/models" 2>/dev/null)
    if [[ -n "$MISTRAL_RESP" ]]; then
        MODEL=$(echo "$MISTRAL_RESP" | python3 -c \
            "import sys,json; d=json.load(sys.stdin); print(d['data'][0]['id'])" 2>/dev/null \
            || echo "$LOCAL_LLM_MODEL")
        echo "${GREEN}✓ Mistral${RESET}     $MODEL"
        MISTRAL_OK=true
    else
        echo "${YELLOW}△ Mistral${RESET}     vLLM not responding"
        echo "  ${DIM}Restart: ssh root@${RUNPOD_IP} -p ${RUNPOD_SSH_PORT} -i ${RUNPOD_SSH_KEY} 'bash /workspace/serve_mistral.sh'${RESET}"
    fi
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "${DIM}───────────────────────────────────────────────${RESET}"

ALL_OK=true
$CHROMA_OK  || ALL_OK=false
$NEO4J_OK   || ALL_OK=false
$MISTRAL_OK || ALL_OK=false

if $ALL_OK; then
    echo "${GREEN}✓ All services ready${RESET}"
else
    echo "${YELLOW}△ Some services need attention (see above)${RESET}"
fi

echo ""
echo "${DIM}Run:${RESET}"
echo "  ${CYAN}python3 chat_graph.py${RESET}              LangGraph pipeline"
echo "  ${CYAN}python3 chat_graph.py --chain-log${RESET}  with full LLM logging"
echo "  ${CYAN}python3 chat.py${RESET}                    orchestrator pipeline"
echo ""
echo "${DIM}Working directory: $INGESTION_DIR${RESET}"
echo ""
