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
# Must be 60/67 PASS before any restart (67 cases; #24 + #25 known-stale;
#   #3 + #21 also LLM-stochastic but ~85% PASS — not formally known-stale):
#   #25 — "is Art.5 a non-conformity?" (anti-hallucination, since 2026-05-27)
#   #24 — "what is our GDPR Art.32 status?" (~30-50% pass rate; LLM-stochastic
#         A.5-bridge mention; since 2026-05-30 batch 2). Some runs both pass;
#         a 61/62 or 62/62 result is fine but isn't reproducible. Follow-up:
#         see memory case_24_art32_bridge_followup.md.
# Any non-#24/#25 regression blocks restart.
# Whenever you add a user-facing feature/fix, append an EvalCase that would
# have failed pre-change and passes post-change — see the feedback-memory rule.
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
After removing duplicates, always run eval (60/62 must pass; #24 + #25 known-stale) before restarting.

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
- Most recent: results/eval_20260531_*.csv (67 cases — 21 core + 18
  feature-locked + 2 engine-NC/posture-discipline + 4 calibration multi-leaf +
  5 Phase B records + 5 Phase B policy_program + 5 Phase B op_process supplier
  + 2 Phase B op_process incident family + 1 Phase B op_process threat-intel +
  1 Phase B op_process evidence-handling + 1 Phase B op_process project-security
  + 1 Phase B op_process return-of-assets + 1 Phase B op_process labelling)
- Score: 60/67 PASS, 0 WARN, 7 FAIL (some runs 61/67 or 62/67 due to #24
  stochasticity; cases #3 + #21 also occasionally fail on LLM citation-list
  position — re-runs pass, not known-stale):
  - #25 known-stale since 2026-05-27 (anti-hallucination on "is Art.5 a non-
    conformity?", needs separate fix)
  - #24 known-stale since 2026-05-30 batch 2 (~20% pass rate; LLM-stochastic
    on whether Art.32 answer surfaces the A.5-bridge control; was reported as
    PASS in batch 2 commit msg but CSV evidence shows it had already started
    failing — see memory case_24_art32_bridge_followup.md)
- Never deploy with a regression below the current case count
- Cases 22-26 lock in: cited refs in POSTURE_STATUS / STANDARD_KNOWLEDGE,
  xfw posture inheritance, Layer-2 anti-hallucination, uploaded-doc short-circuit
- Cases 27-28 lock in: xfw proposer HITL queue (chat surface + isolation guard)
- Cases 33-36 lock in: Stage-1 HITL surfaces (list / approve / acknowledge)
- Cases 37-38 lock in: Stage-2 HITL surfaces (engine-verdict list / approve)
- Case 39 locks in: [DRAFT] label fix — document_confirmed rows must not be
  hedged via the CONFIRMATION RULE
- Cases 40-41 lock in: engine 0/N → NC (was OFI) + posture-tag-is-the-verdict
- Cases 42-45 lock in: multi-leaf calibrations #2-#5 (A.8.2, A.5.2, Art.30, Art.15)
  via Stage-2 list_one surface — "0/4 children satisfied" reason text PROVES
  the 4-leaf shape end-to-end. Pre-promotion would have been "0/1".
- Cases 46-50 lock in: Phase B records_program 5-pack (A.5.5/6/9/31/32; #48 is
  A.5.9 register/review both freshness=90; #50 is A.5.32 procedure-variant)
- Cases 51-55 lock in: Phase B policy_program 5-pack (A.5.3/4/10/12/15; #51-52
  are matrix + directive primary-leaf variants; #55 is A.5.15 partial-evidence
  OFI 1/4 path — companion to 0/4 default in 46-54)
- Cases 56-60 lock in: Phase B operational_process supplier+cloud 5-pack
  (A.5.19/20/21/22/23; #57 is A.5.20 template variant; #58 is A.5.21 review
  freshness=180; #59 is A.5.22 review-record-shaped variant; #60 is A.5.23
  partial-evidence OFI 1/4 + profile_fact triggering — second partial-evidence
  case in suite after #55)
- Cases 61-62 lock in: Phase B operational_process incident family
  (A.5.25/27; both review freshness for incident-hot controls and uniform-
  procedure-primary shape). A.5.26 also promoted to 4-leaf but NOT eval-
  covered — engine NC at 0/4 verified via direct compute_engine_verdicts()
  but doesn't reach Stage-2 surface because engine agrees with live NC
  (posture_loader.py:343 no-op suppression keeps Stage-2 queue clean)
- Case 63 locks in: Phase B operational_process threat-intel (A.5.7;
  per-product-record lifecycle-end variant — program output IS the
  closure artefact, distinct from triage_decision / incident_closure /
  improvement_action / offboarding / deviation / EOL / exit-migration /
  change-response variants on prior batches; program review freshness
  180d for detection-landscape volatility)
- Case 64 locks in: Phase B operational_process evidence-handling
  (A.5.28; disposal_record lifecycle-end variant — chain-of-custody
  *end*, distinct from per-event / per-product / per-action variants;
  first op_process batch with 365d review freshness — forensic
  discipline doesn't churn like detection/IR/threat-intel; closes the
  incident-evidence triangle alongside A.5.25-27 from batch 4)
- Case 65 locks in: Phase B operational_process project-security
  (A.5.8; closure_record lifecycle-end variant — first OWNERSHIP-
  transferring variant: per-project three-way signoff (sponsor +
  InfoSec + operational owner) with residual-risk register transfer;
  review freshness 365d (stable PM methodology); cross-control links
  to A.8.25/A.8.26 SDLC + A.5.20 supplier + A.5.23 cloud + A.5.27
  lessons)
- Case 66 locks in: Phase B operational_process return-of-assets
  (A.5.11; per-leaver return_record lifecycle-end variant — inclusive
  write-off path captures BOTH confirmed returns AND risk-accepted
  non-returns; new non_return_path MUST surfaces real-world friction;
  review freshness 365d (HR methodology stable); cross-control links
  to A.5.9 asset register + A.8.10 information deletion)
- Case 67 locks in: Phase B operational_process labelling (A.5.13;
  per-platform application_record lifecycle-end variant — proves
  labelling extended to each new system; first cascade-cadence pattern
  (review freshness inherited from A.5.12 parent scheme); new
  pii_overlay MUST pins ISO confidentiality × GDPR PII integration
  at spec level; cross-control links to A.5.12 scheme + A.7.10 media)
- Prior known-stale cases (#2, #3, #4, #24, #25, #28) restored to PASS on
  2026-05-25 via Path A: replayed status_before from posture_status_log to
  revert the 27 Stage-1-driven finding mutations, and stripped the offending
  UPDATE from stage1_review_chat.py (commit d6329c4). Stage-1 now only
  confirms evidence; engine + Stage-2 own posture. #24 regressed again
  2026-05-30 (separate cause from the Stage-1 fix; xfw context injection).
- TODO: add case for incident obligations once the chat surface (commit 40ad607)
  exposes a non-clarification answer path
- TODO: add case for SPEC_ART_25 (GDPR Art.25 DPbD DerivedSpec, 6 deps + 1 direct
  evidence leaf). Engine→chat wiring landed 2026-05-25 (commit 9ac0ac3); the
  prerequisite is now met but the regression test still needs writing.

## Git
```bash
git add -A
git commit -m "description"
git push origin main
```
