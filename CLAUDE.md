# ArionComply — Claude Code Guide

## Project
Compliance RAG platform on Azure VM (172.211.244.144).
Stack: FastAPI + LangGraph + Neo4j + ChromaDB + PostgreSQL + GPT-4o.

## VM Access
```bash
ssh -i ~/.ssh/arioncomplySK.pem arionlabs@172.211.244.144
cd /data/arioncomply
```

## Start / Stop
```bash
# Start API
PYTHONPATH=/data/arioncomply python3 api_server.py > /tmp/api.log 2>&1 &

# Stop API
kill $(lsof -ti:8080) 2>/dev/null

# Check logs
tail -f /tmp/api.log
grep -E "ERROR|WARNING" /tmp/api.log
```

## Run Evals (always run before restarting after code changes)
```bash
PYTHONPATH=/data/arioncomply python3 tests/eval_suite.py \
  --csv results/eval_$(date +%Y%m%d_%H%M).csv --pause 2 \
  2>&1 | grep -E "PASS|FAIL|RESULTS"
# Must be 21/21 PASS before any restart
```

## Test Streaming
```bash
curl -s -N "http://localhost:8080/api/v1/chat/stream?question=what+are+our+NC+findings&session_id=test_1" \
  -H "X-API-Key: arion_dev_key_2026"
```

## Test Sync Chat
```bash
curl -s -X POST http://localhost:8080/api/v1/chat \
  -H "X-API-Key: arion_dev_key_2026" \
  -H "Content-Type: application/json" \
  -d '{"question": "what are our NC findings?"}' \
  | python3 -m json.tool
```

## Key Files
api_server.py              — FastAPI server, streaming endpoint, auth
rag/arion_graph.py         — LangGraph pipeline, nodes, checkpointers
rag/llm_answer.py          — LLM answer generation, layered node presentation
rag/classifier.py          — Query classification, CLEAR_INTENT_PHRASES
rag/resolver.py            — Per-taxonomy data source dispatch
rag/graph_expander.py      — Neo4j graph traversal, xfw edge expansion
static/arioncomply.html    — UI (single file, streaming chat)
tests/eval_suite.py        — 21-query evaluation suite

## Architecture
Query → classify node → retrieve node → update_session node → END
↓                ↓
clarify node    (LLM rank_and_answer OR Postgres short-circuit)

### Answer layers
- Layer 1: Primary standard nodes (ISO 27001 with posture NC/OFI/Comply)
- Layer 2: Cross-framework nodes (GDPR xfw edges from Neo4j)
- Short-circuit: document_inventory, scope N/A → direct Postgres answer, no LLM

### Session persistence
- Sync chat: PostgresSaver (arioncomply_sessions DB)
- Streaming: AsyncPostgresSaver (same DB)
- thread_id format: `{tenant_id[:8]}:{session_id}`

## Known Issues to Fix

### 1. Code duplication in rag/arion_graph.py (CRITICAL)
The file contains duplicate definitions of these functions:
- `_is_scope_na_query` (lines ~844 and removed, but verify)
- `_answer_scope_na`
- `make_retrieve_node`
- `make_clarify_node`
- `make_update_session_node`
- `route_after_classify`
- `build_arion_graph`

**How to find duplicates:**
```bash
grep -n "^def " rag/arion_graph.py
```
Any function appearing twice must have the second copy removed.
The FIRST copy of each function is the correct/patched version.
The graph uses the LAST definition — so duplicates shadow fixes.

**Fix approach:** For each duplicate, keep the first definition, remove the second.
After removing duplicates, always run eval (21/21 must pass) before restarting.

### 2. Clarification loop (depends on fix #1)
Query: "what documents are missing?" triggers clarification instead of
routing directly to document_inventory.

Root cause: `make_update_session_node` (second duplicate) doesn't reset
`needs_clarif=False` and `clarif_question=''` — so the next turn still
sees `needs_clarif=True` and loops.

Fix already applied to FIRST copy of `make_update_session_node`:
```python
def update_session(state: ArionState) -> dict:
    return {
        "turn_count":      state["turn_count"] + 1,
        "clarif_count":    0,
        "needs_clarif":    False,
        "clarif_question": "",
    }
```
Once duplicate is removed, this fix will take effect.

### 3. Classifier duplicate pattern (minor)
`rag/classifier.py` has the document_inventory pattern added twice around line 630.
Remove the duplicate entry.

## Databases
```bash
# Compliance data
psql -U arioncomply -h 127.0.0.1 -d arioncomply_compliance

# Session persistence
psql -U arioncomply -h 127.0.0.1 -d arioncomply_sessions

# Key tables
# arioncomply_compliance: posture_controls, api_keys, document_uploads
# arioncomply_sessions: checkpoints (LangGraph state)
```

## Neo4j
```bash
# Check node/edge counts
python3 -c "
from neo4j import GraphDatabase
import os; from dotenv import load_dotenv; load_dotenv('.env')
d = GraphDatabase.driver(os.getenv('NEO4J_URI'), auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD')))
with d.session() as s:
    print('nodes:', s.run('MATCH (n) RETURN count(n) AS c').single()['c'])
    print('rels:', s.run('MATCH ()-[r]->() RETURN count(r) AS c').single()['c'])
"
# Expected: 654 nodes, 778 relationships
```

## Eval Baseline
- File: results/eval_layered4.csv
- Score: 21/21 PASS
- Never deploy with a regression below 21/21

## Git
```bash
git add -A
git commit -m "description"
git push origin main
```
