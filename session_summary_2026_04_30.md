# ArionComply Session — 2026-04-30

## Achievements

### Evaluation suite — 21/21 PASS baseline established
- Built EvalPipeline wrapper connecting to live LangGraph pipeline
- 21 test cases covering all taxonomy types
- Baseline: eval_baseline_21_21.csv saved in results/

### Taxonomy
- rag/taxonomy.py: 9-type QUERY_TAXONOMY registry (open/closed extensible)
- rag/resolver.py: per-type dispatch handlers
- CLASSIFIER_TO_TAXONOMY mapping for incremental migration

### Pipeline improvements
- Classifier fast-path phrases added:
    implementation: "what should we do to close/address X"
    implementation: "how should we prepare for our next X audit"
    document_content: "what must our X policy contain"
    gap_analysis: "physical security gaps" → short-circuit
    gap_analysis: "software dev security gaps" → short-circuit
    posture: "what is our ISO 27001 posture?"
- Scope N/A short-circuit (rag/arion_graph.py):
    physical security → 306ms deterministic answer
    software dev → 265ms deterministic answer
- Clarification improved:
    taxonomy_options_map added to IntakeResult
    process_clarification resolves taxonomy type directly from user choice
    CLARIFICATION_WRITER_PROMPT now generates taxonomy-typed options

### Data foundation
- schema_v6.sql: soft delete + retention on all 24 tables
- schema_v6_fix.sql: retention_policies recreated correctly (13 rows)
- deletion_log: append-only, DELETE revoked from app user
- DeletionService: rag/deletion_service.py

### Multi-tenant
- TenantContextCache: TTL-based, thread-safe, replaces module-level globals
- build_pg_pool + pool_conn: connection pooling for concurrent use
- PostgresSaver: ready to activate (pip install langgraph-checkpoint-postgres)

### GitHub
- Repo: github.com/jmkamula/RAG
- First commit pushed with full codebase

## Eval progression
  Baseline (11/21) → v2 (17/21) → v3 (19/21) → v4 (19/21) → v5 (21/21)

## Next session
  Phase 2b: Wire Resolver into arion_graph.py (replace make_retrieve_node ~200 lines)
  Phase 4:  JFYI engine (related findings, upload status, audit timeline)
  Documents: Upload Arion PDFs (doc_uploader.py ready)
  Clarification: Test taxonomy-led clarification in chat
