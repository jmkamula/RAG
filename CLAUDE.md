# ArionComply — Claude Code Context

## Project
Compliance intelligence platform. RAG pipeline (vector + graph) + LLM advisory.
Multi-standard: ISO 27001, ISO 27002, GDPR, ISO 27701 (pending OCR).

## Working Directory
```
~/Documents/Arion Networks/compliance/Neo4j/enhancement/localchroma/chroma-consent/ingestion/
```
Referred to as `$INGESTION` throughout.

## Services (must be running)
```bash
# ChromaDB — Mac localhost
chroma run --path ~/chromadb_data --port 8000

# Neo4j — Mac localhost  
# Started via Neo4j Desktop, bolt://localhost:7687, pw: arionneo4j@2026

# Mistral — RunPod A100 via SSH tunnel
ssh -L 9000:localhost:8000 root@216.81.245.127 -p 16558 -i ~/.ssh/id_ed25519 \
    -N -o ServerAliveInterval=30 -o ServerAliveCountMax=10 -f
# Verify: curl http://localhost:9000/v1/models
```

## Environment Variables
```bash
export LOCAL_LLM_BASE_URL=http://localhost:9000/v1
export LOCAL_LLM_MODEL=mistral-small-3.2-24b
export NEO4J_PASSWORD=arionneo4j@2026
export CHROMA_HOST=localhost
export CHROMA_PORT=8000
# OPENAI_API_KEY already set (embeddings only)
```

## Run Chat
```bash
cd $INGESTION
python3 chat.py                    # current orchestrator
python3 chat.py --chain-log        # full LLM chain logging
```

## Key Files
```
rag/
  classifier.py       — QueryClassifier, CLEAR_INTENT_PHRASES, _fast_classify
  orchestrator.py     — RAGOrchestrator, OVERRIDE_PHRASES (791 lines — being replaced)
  llm_answer.py       — LLMAnswer, VERIFICATION_PROMPT, SYSTEM_PROMPT
  context_assembler.py— ContextAssembler, AssembledContext
  graph_expander.py   — GraphExpander (Neo4j traversal)
  chain_logger.py     — ChainLogger (--chain-log flag)
  arion_state.py      — ArionState TypedDict (LangGraph migration)
  arion_graph.py      — build_arion_graph() (LangGraph migration)

enrichment/
  keyword_patches.py       — KEYWORD_PATCHES dict (9 nodes + A.7.10)
  apply_keyword_patches.py — apply + rebuild ChromaDB index
  tier2_generated.json     — 259 LLM-generated GDPR business descriptions

vector/
  indexer.py    — VectorIndexer (embedding model: text-embedding-3-large)
  retriever.py  — VectorRetriever

iso_nodes_phase1.json   — 126 ISO nodes (enriched with 27001 + 27002)
gdpr_nodes_phase2.json  — 303 GDPR nodes (enriched with tier1 + tier2)
```

## Current State
- 429 nodes indexed (126 ISO + 303 GDPR), text-embedding-3-large, 3072 dims
- 9 posture controls loaded (ARION_POSTURE in chat.py)
- All LLM calls → Mistral 3.2 24B on RunPod (embeddings stay on OpenAI)
- CLEAR_INTENT_PHRASES in both _check_explicit() and _fast_classify()

## Active Work: LangGraph Migration
Replacing orchestrator.py with LangGraph StateGraph.
Files: rag/arion_state.py + rag/arion_graph.py
Status: imports work, first invoke() failing — debugging AssembledContext fields.

### AssembledContext fields (context_assembler.py)
```python
AssembledContext(
    context_text    = ...,
    question_type   = qtype,        # QuestionType enum
    tenant_name     = ...,
    has_posture     = bool,
    posture_summary = {},
    intent          = intent,       # QueryIntent
    node_ids_used   = [],           # list[str]
    primary_count   = 0,            # int (not node_count)
)
# NOTE: no node_count or primary_node_count — use primary_count
```

### TenantProfile (classifier.py)
```python
TenantProfile(
    tenant_id            = "arion-networks",
    name                 = "Arion Networks",
    applicable_standards = ["ISO27001:2022", "GDPR:2016/679"],
    role                 = ["controller", "processor"],
    sector               = "technology",
    jurisdiction         = ["EU", "UK"],
    has_posture_data     = True,
)
```

### GraphExpander init
```python
GraphExpander(
    neo4j_uri      = config.neo4j_uri,
    neo4j_user     = config.neo4j_user,
    neo4j_password = config.neo4j_password,
    retriever      = retriever,        # VectorRetriever — required
)
```

### LangGraph benchmark command
```bash
cd $INGESTION
python3 - <<'PYEOF'
import sys, os, traceback
sys.path.insert(0, '.')
os.environ['LOCAL_LLM_BASE_URL'] = 'http://localhost:9000/v1'
os.environ['LOCAL_LLM_MODEL']    = 'mistral-small-3.2-24b'

from chat import ARION as tenant, ARION_POSTURE
from rag.arion_graph       import build_arion_graph, get_checkpointer
from rag.arion_state       import make_initial_state
from rag.orchestrator      import OrchestratorConfig
from rag.llm_answer        import LLMAnswer
from rag.context_assembler import ContextAssembler
from rag.graph_expander    import GraphExpander
from rag.classifier        import QueryClassifier
from vector.retriever      import VectorRetriever

config    = OrchestratorConfig()
retriever = VectorRetriever(chroma_host=config.chroma_host, chroma_port=config.chroma_port)
expander  = GraphExpander(
    neo4j_uri=config.neo4j_uri, neo4j_user=config.neo4j_user,
    neo4j_password=config.neo4j_password, retriever=retriever,
)
assembler  = ContextAssembler(tenant=tenant)
llm        = LLMAnswer()
classifier = QueryClassifier(tenant_profile=tenant, retriever=retriever)

try:
    with get_checkpointer() as cp:
        graph = build_arion_graph(
            tenant=tenant, retriever=retriever, expander=expander,
            assembler=assembler, llm=llm, classifier=classifier,
            posture=ARION_POSTURE, checkpointer=cp,
        )
        cfg  = {"configurable": {"thread_id": "test_1"}}
        init = make_initial_state(tenant)
        for q in ["what are our encryption gaps?",
                  "preparing for our ISO 27001 audit next month",
                  "what are our obligations for cloud storage?"]:
            result = graph.invoke({**init, "query": q}, cfg)
            print(f"Q: {q[:40]}")
            print(f"  intent={result['intent_type']} refs={result['focus_refs']} verified={result['verified']}")
except Exception as e:
    traceback.print_exc()
PYEOF
```

## Known Issues / Pending
- arion_graph.py: full traceback needed to fix remaining __init__ error
- A.7.10 still appearing in cloud storage answers (keyword patch applied, index needs rebuild)
- Art.28 sub-clause hallucination (A.28.3.a/g) — citation rule added to system prompt
- 5 ISO nodes with thin guidance: A.5.7, A.5.19, A.7.10, A.8.11, A.8.27

## RunPod
```
Pod ID:   dxhcu1p4caax06
IP:       216.81.245.127
SSH port: 16558
SSH key:  ~/.ssh/id_ed25519
vLLM:     serving mistralai/Mistral-Small-3.2-24B-Instruct-2506 on port 8000
Restart:  bash /workspace/serve_mistral.sh
```

## Lab Server
- Mistral Small 3.2 24B via llama.cpp on port 8080
- Service: llm-model-a.service
- 377GB RAM, 80 threads

## Next Steps (in order)
1. Fix arion_graph.py __init__ error — get benchmark running
2. Write chat_graph.py with --graph flag alongside existing chat.py
3. Run same benchmark queries through both, compare output
4. Once graph matches orchestrator quality: deprecate orchestrator.py
5. Add PostgresSaver for multi-tenant (same Postgres as posture data)
6. Training data generation when RAG quality is stable
