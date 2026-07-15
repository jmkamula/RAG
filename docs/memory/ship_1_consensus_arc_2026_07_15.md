---
name: ship-1-consensus-arc-2026-07-15
description: Full Ship 1 arc (2026-07-13 → 2026-07-15) — retrieval-first consensus + bounded LLM gatekeeper + xfw dedicated lane. Curator-lexicon at top-tier weight. 205/208 baseline; residuals are prose-layer stochasticity deferred to Ship 2+3.
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 1 arc — SHIPPED 2026-07-13 through 2026-07-15. Full retrieval-first
consensus architecture replacing the LLM-classifier-primary chat pipeline.

**Why:** LLM was drifting on intent classification. Case #16 root-cause
revealed the chat pipeline had drifted from its design: ChromaDB was
enriched with natural-language business_description on every node, but
retrieval had been buried inside per-taxonomy resolver strategies while
the classifier grew ~50 CLEAR_INTENT regex patterns that bypassed the
corpus. Ship 1 restores retrieval as the anchor + adds 6 corroborating
signals + a bounded LLM arbiter.

**How to apply:** Every downstream design decision touching intent
classification or chat routing should respect:
1. Curator-authored mappings are top-tier signal weight (1.00 in
   `rag/consensus/types.py`). When curator says X → Y, that mapping
   wins. This is "the optimal place to enhance as we learn" — add
   CLEAR_INTENT / DOCUMENT_TOPIC_MAP entries when you find failing cases.
2. Structural constraints in code beat prompt engineering. Signal C
   hard-locks question_type against LLM override; Signal B hard-locks
   framework. See `_signals_lock_question_type` and
   `_signals_lock_framework` in `rag/consensus/gatekeeper.py`.
3. LLM's role is a BOUNDED arbiter — approve, modify (refs only),
   or reject. Cannot invent, cannot override deterministic signals.
   Never give an LLM the freedom to override cleanly-fired signals.
4. xfw has a dedicated budget lane — as we add SOC2/NIS2/DORA, the
   cross-framework surfacing scales because it doesn't compete with
   sibling/parent expansion.
5. LLM prose stochasticity IS a real category of failure that Ship 1
   doesn't solve. Deferred to Ship 2 (AnswerPayload scaffold) and
   Ship 3 (preservation-checked polish). Residuals #3/#14/#33 are
   the leading indicators.

**Arc trajectory** (eval scores across the 14+ commits):
- Pre-Ship 1: 200/208 PASS + 7 FAIL + 1 WARN
- Ship 1.5 gatekeeper (unbounded): 198 + 5 + 5
- Ship 1.5b tuned prompt: 200 + 7 + 1
- Ship 1.6 resolver decouple: 202 + 4 + 2
- Ship 1.6b Signal C lock: 206 + 1 + 1
- Ship 1.7abc xfw lane: 205 + 1 + 2
- Ship 1.7d curator weight=1.0: 205 + 1 + 2 (case #7 stabilised)

**Component map** — where the architecture lives:
- `rag/consensus/types.py` — SignalOutput, ConsensusResult, ConsensusConfig
- `rag/consensus/signals/` — 7 signal implementations (B/C/A/D/E/F/G)
- `rag/consensus/aggregator.py` — fusion math + verdict decision
- `rag/consensus/gatekeeper.py` — bounded LLM arbiter with hard-locks
- `rag/consensus/query_consensus.py` — public entry point `run_consensus()`
- `rag/consensus/log.py` — persistence to chat_consensus_log (schema_v67)
- `rag/consensus/gatekeeper_prompts.py` — LLM prompt (kept separate for
  A/B baseline diffs)
- `rag/graph_expander.py` — NODE_BUDGET_PRIMARY + NODE_BUDGET_XFW +
  _prioritise_xfw + ExpandedContext.xfw_nodes
- `rag/resolver.py` — GraphResult.xfw_nodes carried; _resolve_posture_status
  extends posture with xfw-linked postures; _resolve_cross_framework
  also seeds with cited_refs (Ship 1.6)
- `rag/llm_answer.py` — bridge footer data-driven; framework_scope_guard
  context extends to all resolver-surfaced refs
- `rag/arion_graph.py` — classify node wires consensus in

**Escape hatch:** `USE_LEGACY_CLASSIFIER=1` env disables consensus entirely.
Only use for rollback if consensus regresses production.

**Related memories:**
- `[[dejargonize-ux-pass-2026-07-01]]` — de-jargonize conventions still apply
- `[[framework-role-model-arc]]` — role model that Ship 2's per-taxonomy
  scaffold builders will consume
- `[[llm-free-intake-arc-2026-07-06]]` — intake arc's critic-verifier pattern
  informed the bounded-arbiter design
- `[[feedback-eval-with-each-feature]]` — every Ship 1.x commit added
  eval cases per the rule

**Ship 2 (next) targets:** per-taxonomy AnswerPayload builders that own
their own data-fetch + scaffold. Ship 3 (later): constrained prose polish
with preservation-check on scaffold elements. Together they close the
residual prose stochasticity (#3/#14/#33 class).
