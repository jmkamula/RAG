#!/usr/bin/env bash
# ArionComply - Environment Initialisation Script (Azure VM)
#
# Usage:
#   source arion_start.sh        (sets env in current shell)
#   ./arion_start.sh             (runs in subshell - env not persisted)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
DIM='\033[2m'
RESET='\033[0m'

if [[ -n "${BASH_VERSION}" ]]; then
    INGESTION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
elif [[ -n "${ZSH_VERSION}" ]]; then
    INGESTION_DIR="${0:A:h}"
else
    INGESTION_DIR="$(pwd)"
fi
ENV_FILE="$INGESTION_DIR/.env"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════╗${RESET}"
echo -e "${CYAN}║   ArionComply - Environment Setup    ║${RESET}"
echo -e "${CYAN}╚══════════════════════════════════════╝${RESET}"
echo ""

if [[ ! -f "$ENV_FILE" ]]; then
    echo -e "${RED}✗ .env not found at $ENV_FILE${RESET}"
    return 1 2>/dev/null || exit 1
fi

while IFS='=' read -r key value; do
    [[ "$key" =~ ^[[:space:]]*# ]] && continue
    [[ -z "$key" ]] && continue
    key="${key// /}"
    value="${value%%#*}"
    value="${value%"${value##*[! ]}"}"
    export "$key=$value"
done < "$ENV_FILE"

echo -e "${GREEN}✓ Environment loaded${RESET}  ($ENV_FILE)"
echo ""
echo -e "${DIM}Checking services...${RESET}"

# ── PostgreSQL ────────────────────────────────────────────────────────────────
PG_OK=false
if pg_isready -h 127.0.0.1 -p 5432 -U arioncomply_app > /dev/null 2>&1; then
    CONTROL_COUNT=$(python3 -c "
import psycopg2, os
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL',''))
    cur  = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM posture_controls')
    print(cur.fetchone()[0])
    conn.close()
except:
    print(0)
" 2>/dev/null)
    echo -e "${GREEN}✓ PostgreSQL${RESET}  running - ${CONTROL_COUNT} posture controls"
    PG_OK=true
else
    echo -e "${YELLOW}△ PostgreSQL${RESET}  not running"
    echo -e "  ${DIM}Start: sudo systemctl start postgresql${RESET}"
fi

# ── Neo4j ─────────────────────────────────────────────────────────────────────
NEO4J_OK=false
NODE_COUNT=$(python3 - <<PYEOF 2>/dev/null
from neo4j import GraphDatabase
import os
try:
    d = GraphDatabase.driver(
        os.getenv("NEO4J_URI","bolt://127.0.0.1:7687"),
        auth=(os.getenv("NEO4J_USER","neo4j"), os.getenv("NEO4J_PASSWORD","")),
        connection_timeout=3
    )
    with d.session() as s:
        print(s.run("MATCH (n) RETURN count(n) as c").single()["c"])
    d.close()
except:
    print("")
PYEOF
)
if [[ -n "$NODE_COUNT" && "$NODE_COUNT" -gt 0 ]]; then
    echo -e "${GREEN}✓ Neo4j${RESET}       online (${NODE_COUNT} nodes)"
    NEO4J_OK=true
else
    echo -e "${YELLOW}△ Neo4j${RESET}       offline"
    echo -e "  ${DIM}Start: sudo systemctl start neo4j${RESET}"
fi

# ── ChromaDB ──────────────────────────────────────────────────────────────────
CHROMA_OK=false
if curl -s --max-time 2 "http://${CHROMA_HOST:-localhost}:${CHROMA_PORT:-8000}/api/v1/heartbeat" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ ChromaDB${RESET}    running on port ${CHROMA_PORT:-8000}"
    CHROMA_OK=true
else
    echo -e "${YELLOW}△ ChromaDB${RESET}    not running"
    echo -e "  ${DIM}Start: nohup chroma run --path /data/chroma_db --port 8000 > /data/chroma_db/chroma.log 2>&1 &${RESET}"
fi

# ── RAG API ───────────────────────────────────────────────────────────────────
API_OK=false
if curl -s --max-time 2 "http://localhost:8080/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ RAG API${RESET}     running on port 8080"
    API_OK=true
else
    echo -e "${YELLOW}△ RAG API${RESET}     not running"
    echo -e "  ${DIM}Start: python3 api_server.py &${RESET}"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${DIM}───────────────────────────────────────────────${RESET}"

ALL_OK=true
$PG_OK     || ALL_OK=false
$NEO4J_OK  || ALL_OK=false
$CHROMA_OK || ALL_OK=false

if $ALL_OK; then
    echo -e "${GREEN}✓ All services ready${RESET}"
else
    echo -e "${YELLOW}△ Some services need attention (see above)${RESET}"
fi

export INGESTION="$INGESTION_DIR"
export PYTHONPATH="$INGESTION_DIR:$PYTHONPATH"

echo ""
echo -e "${DIM}Run:${RESET}"
echo -e "  ${CYAN}python3 chat_graph.py${RESET}              LangGraph pipeline"
echo -e "  ${CYAN}python3 chat_graph.py --chain-log${RESET}  with full LLM logging"
echo -e "  ${CYAN}python3 tests/eval_suite.py${RESET}        run eval suite"
echo -e "  ${CYAN}python3 api_server.py${RESET}              start RAG API on :8080"
  echo -e "  ${CYAN}http://localhost:8080/docs${RESET}            API documentation"
  echo -e "  ${CYAN}http://localhost:8080/docs${RESET}            API documentation"
echo ""
echo -e "${DIM}Working directory: $INGESTION_DIR${RESET}"
echo ""
