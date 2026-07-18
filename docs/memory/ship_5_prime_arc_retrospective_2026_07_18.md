---
name: ship-5-prime-arc-retrospective-2026-07-18
description: "Ship 5' arc retrospective — 6 sub-arcs (a→f) auditing + hardening all LLM/embedding usage"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 5' arc — start-to-finish log of the LLM + embedding
consistency audit and cleanup. Entry-point for future work
on anything touching `rag/llm_client.py`, `rag/llm_models.py`,
`rag/embedding_config.py`, or the vector-store collections.

**Arc window:** 2026-07-18. 6 sub-arcs across ~half a day.

## Motivation

User's ask: "audit the way we are using LLMs, every LLM use
site and which LLM is in use. The key is to ensure best practice
and consistency, e.g. vector embedding model and query
embedding model consistency."

Prior arcs (Ship 2' chat pipeline, Ship 3' notifications,
Ship 4' external API) all added LLM call sites without a
top-down consistency pass. The concern was legitimate —
Ship 5'.a's audit surfaced 9 real findings across the
codebase.

## Sub-arc inventory

| Sub-arc | What | Key win |
|---|---|---|
| 5'.a | Audit | Systematic inventory of 10 LLM sites + 5 Chroma collections; 9 findings prioritized H/M/L/INFO |
| 5'.b | Embedding consolidation | All 4 Chroma collections on `text-embedding-3-large`; `rag/embedding_config.py` + `scripts/reindex_all.py` |
| 5'.c | Temperature + tier2 migration | Extractor + enricher on `temperature=0.0`; tier2_generator moved off direct OpenAI SDK to `llm_client.call` |
| 5'.d | Dead code + `rag/llm_models.py` | Deleted 3 dead pathways; new 7-constant model config with env override; every hardcoded model string migrated |
| 5'.e | ai_call_log purpose allowlist | schema_v80 added `consensus_gatekeeper` + `enrichment_tier2` to CHECK; recovers 5-15% previously-missing LLM telemetry |
| **5'.f** | **Arc retrospective** | This document |

## Findings — how they closed

From Ship 5'.a:

- **HIGH 1** — `enrichment/tier2_generator.py` bypasses
  `llm_client` → CLOSED in 5'.c (migrated + deleted dead
  `_get_client`)
- **HIGH 2** — extractor + enricher use `temperature=0.4` for
  structured JSON extraction → CLOSED in 5'.c (`temperature=0.0`
  at 3 sites)
- **MEDIUM 3** — `musts_arioncomply` has no stored
  `embedding_function_name` → CLOSED in 5'.b (switched builder
  to naming-aware embed fn)
- **MEDIUM 4** — 2 `VectorRetriever()` no-arg call sites rely
  on defensive rebuild → CLOSED in 5'.b (explicit
  `embedding_model=EMBED_MODEL_STANDARD`)
- **LOW 5** — `rag/classifier.py::_get_openai_client` dead →
  CLOSED in 5'.d
- **LOW 6** — `rag/llm_answer.py::_get_client` dead → CLOSED
  in 5'.d
- **LOW 7** — `rag/llm_answer.py.old.py` legacy file → CLOSED
  in 5'.d
- **INFO 8** — top-level LLM config module → SHIPPED in 5'.d
  as `rag/llm_models.py`
- **INFO 9** — `ai_call_log_purpose_check` rejects two purposes
  used in code → CLOSED in 5'.e (schema_v80)

**All 9 findings closed.**

## Architectural constants that emerged

1. **One-file config modules** — `rag/embedding_config.py`
   (5'.b) + `rag/llm_models.py` (5'.d) are the pattern. Each
   constant is `os.getenv(NAME, default)` so partners can
   override without code changes. Adding a new constant is
   a one-file edit.
2. **Naming-aware embedding function** — `vector/indexer.py`'s
   `OpenAIEmbeddingFunction.name()` returns the canonical
   `openai-<model>` string that Chroma stores in
   `collection_metadata`. This enables the defensive rebuild
   in `VectorIndexer._make_embed_fn_from_name()` for any
   collection that uses this class. As of 5'.b, all 4
   collections do.
3. **`llm_client.call` as the only path** — Ship 5'.c moved the
   last bypass (`tier2_generator.py`) to the central dispatch.
   Every LLM call in the codebase now hits `ai_call_log`
   automatically. Discipline: no direct `openai.OpenAI()` or
   `Anthropic()` clients in `rag/` or `enrichment/`.
4. **`temperature=0.0` for structured JSON extraction** —
   extractor pass1+pass2, enricher, critic_verifier,
   consensus_gatekeeper all set explicit `temperature=0.0`.
   The default 0.4 in `llm_client.call` is for chat prose
   only; JSON-out sites always override to 0.0.
5. **Chroma dim safety net is real** — verified empirically
   in 5'.a. Chroma rejects `Collection expecting embedding
   with dimension of 3072, got 1536` when a caller's embed
   function produces wrong-dim vectors. Silent-failure only
   possible for same-dim swaps (e.g. `-3-small` → `ada-002`
   both 1536-dim). Since 5'.b eliminated `-3-small` from the
   tree, that specific instance is gone.

## Config module inventory (post-Ship 5')

    rag/embedding_config.py
        EMBED_MODEL_STANDARD = "text-embedding-3-large"
        EMBED_DIM            = 3072
        EMBED_PROVIDER       = "openai"

    rag/llm_models.py
        MODEL_CHAT_ANSWER    = "gpt-4o"                (chat compose)
        MODEL_CHAT_VERIFY    = "gpt-4o-mini"           (verify+correct)
        MODEL_CLASSIFIER     = "gpt-4o-mini"           (classifier)
        MODEL_CONSENSUS_GK   = "gpt-4o-mini"           (gatekeeper — reads GATEKEEPER_MODEL for compat)
        MODEL_EXTRACTOR      = "claude-sonnet-4-6"     (extractor + critic)
        MODEL_ENRICHER       = "claude-haiku-4-5-20251001" (doc enricher)
        MODEL_ENRICHMENT_T2  = "gpt-4o-mini"           (offline tier2)

## Vector store — post-consolidation

All 4 Chroma collections uniformly configured:

    iso27001_2022      dim=3072  ef=openai-text-embedding-3-large
    gdpr_2016_679      dim=3072  ef=openai-text-embedding-3-large
    arioncombly_all    dim=3072  ef=openai-text-embedding-3-large
    musts_arioncomply  dim=3072  ef=openai-text-embedding-3-large

Also live: `iso27701_2019` (via `scripts/index_27701_to_chroma.py`;
same config).

## Test suite impact

Ship 5' didn't add new integration tests — the arc was
audit + fix + retrospective. Eval baseline held 207/208 PASS +
1 WARN + 0 FAIL across every sub-arc.

Where new tests WOULD have helped:
- A CI check that greps for direct-OpenAI/Anthropic SDK imports
  outside the allowed files (`rag/llm_client.py`,
  `vector/indexer.py`, embedding functions)
- A CI check that greps for hardcoded model strings outside
  the config modules
- A CI check that greps for `temperature=` arguments and warns
  when a JSON-extraction site drifts from 0.0

Deferred.

## Lessons carried forward

- **"Just an inventory" is a real deliverable.** Ship 5'.a
  didn't change any code — but the audit memo listed 9 things
  to fix and gave a prioritized roadmap. Without that, none of
  the specific fixes in 5'.b-e would've been obvious targets.
- **Dimension safety nets don't cover all mismatches.** Chroma
  catches different-dim mismatches loudly; same-dim swaps go
  silent. Stored metadata + defensive rebuild is the pattern
  that fixes both.
- **Env-overridable config is worth the extra line.** Each
  `MODEL_X = os.getenv(...)` is 2 lines instead of 1, but it
  enables partner-specific pinning + A/B tests + local-Mistral
  swaps without a redeploy.
- **CHECK constraints on log tables need equal discipline.**
  Silent-fail via `try/except: pass` masked 5-15% missing
  telemetry for months. When adding a new `log_llm_call`
  purpose, bump the CHECK in the same migration. The
  `COMMENT ON COLUMN` added in 5'.e is the discipline reminder.
- **Consolidation cost is often trivial.** The re-index of
  `musts_arioncomply` from `-small` to `-large` was $0.10 and
  58 seconds. Historically-motivated splits ("save cost") are
  worth re-examining at any scale where compute is cheap
  relative to human coordination cost.

## Deferred / future work

- **Async SDK migration** — Ship 4 SDK is sync-only; async
  client for external consumers is worthwhile
- **Retry-on-429 with backoff** in `llm_client.call` — the
  ~5-15% slow-OpenAI evals we saw across Ship 3/4/5 would
  benefit from a bounded retry
- **CI grep checks** for direct-OpenAI imports + hardcoded
  models + temperature drift (see "Test suite impact" above)
- **`_prettify_reason()` upstream** — the extractor's
  temperature=0.0 change means extraction runs will be
  deterministic; if we surface extraction-diff tests, we'll
  need a reason-humanization consolidation
- **Pricing table updates** — `rag/ai_trace.py::_MODEL_PRICING`
  is hand-maintained. Auto-fetch or CI check that it stays
  in sync with reality

## Related

- [[ship-5-prime-a-llm-audit-2026-07-18]] — audit that opened
  the arc
- [[ship-5-prime-b-embedding-consolidation-2026-07-18]] — 5'.b
- [[ship-5-prime-c-temperature-tier2-2026-07-18]] — 5'.c
- [[ship-5-prime-d-dead-code-llm-models-2026-07-18]] — 5'.d
- [[ship-5-prime-e-ai-call-log-purpose-allowlist-2026-07-18]] — 5'.e
- [[ship-4-prime-arc-retrospective-2026-07-18]] — previous arc
- [[ship-3-prime-arc-retrospective-2026-07-17]] — 2 arcs back
