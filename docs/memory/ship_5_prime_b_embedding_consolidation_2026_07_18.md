---
name: ship-5-prime-b-embedding-consolidation-2026-07-18
description: "Ship 5'.b — consolidate all Chroma collections onto text-embedding-3-large; add shared config + reindex_all CLI"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 5'.b (2026-07-18) — first fix from the Ship 5'.a LLM audit.
Consolidates all 4 Chroma collections onto a single embedding
model + removes an entire class of index-vs-query drift risk.

## Motivation

Ship 5'.a surfaced two embedding models in use:
- `text-embedding-3-large` (3072-dim) on RequirementNode
  collections (iso27001_2022, gdpr_2016_679, iso27701_2019,
  arioncombly_all)
- `text-embedding-3-small` (1536-dim) on `musts_arioncomply`

The split was cost-driven when `musts_arioncomply` was built
(~5400 vectors × -small ≈ $0.02 vs. × -large ≈ $0.10). At today's
scale that's meaningless. Two models = two constants to remember;
same-dimension silent swap (e.g. `-3-small` → `ada-002`, both
1536-dim) is undetectable by Chroma's dim check.

## What shipped

### New module: `rag/embedding_config.py`

Single source of truth for embedding config:

    EMBED_MODEL_STANDARD  = "text-embedding-3-large"
    EMBED_DIM             = 3072
    EMBED_PROVIDER        = "openai"

    def embedding_function_name() -> str:
        # canonical stored name; matches vector/indexer.py's
        # OpenAIEmbeddingFunction.name() output
        return f"openai-{EMBED_MODEL_STANDARD}"

Anything touching vectors should import from here.

### `scripts/build_must_index.py` — switched to naming-aware embed fn

Was using Chroma's builtin `OpenAIEmbeddingFunction` (does NOT
store name in metadata → no defensive rebuild). Now uses
`vector/indexer.py::OpenAIEmbeddingFunction` (stores name).

Also: model constant is now `EMBED_MODEL_STANDARD` from the
shared config. One edit to migrate future models.

### `rag/intake/must_embedding_lookup.py` — same treatment

Imports from `rag.embedding_config`; uses naming-aware embed fn.
Result: `_make_embed_fn_from_name()` defensive rebuild path is
now active for `musts_arioncomply` too — parity with the
RequirementNode collections.

### `scripts/reindex_all.py` — one-shot rebuild CLI

New. Options:
- `--reset` (drop + rebuild — needed for model changes)
- `--musts-only` / `--nodes-only`
- `--iso27701` (also run the ISO 27701 seed)

Future migration story is now:
1. Edit `rag/embedding_config.py::EMBED_MODEL_STANDARD`
2. `python3 scripts/reindex_all.py --reset`
3. Done.

### 2 `VectorRetriever()` no-arg call sites fixed

- `rag/intake/extractor.py:2415` — now passes
  `embedding_model=EMBED_MODEL_STANDARD` explicitly
- `rag/intake/critic_verifier.py:168` — same

Removes reliance on the defensive rebuild path for correctness;
caller now matches stored config directly.

### The re-index itself

Deleted the old `musts_arioncomply` (1536-dim) collection.
Rebuilt with `text-embedding-3-large` (3072-dim). 5385 vectors,
58 seconds, ~$0.10.

**Verified state post-consolidation:**

    iso27001_2022      dim=3072  ef=openai-text-embedding-3-large
    gdpr_2016_679      dim=3072  ef=openai-text-embedding-3-large
    arioncombly_all    dim=3072  ef=openai-text-embedding-3-large
    musts_arioncomply  dim=3072  ef=openai-text-embedding-3-large

Full consistency across all 4 collections.

**Spot-check** — semantic MUST query
"user access rights are reviewed quarterly against role
definitions" returned:
- `item:A.5.18:rev_actions`
- `item:A.5.18:rev_outcome`
- `item:A.5.18:rev_privileged_check`
- `item:A.5.18:rev_reviewer`
- `item:A.8.18:rev_user_list`

All 5 matches from A.5.18 (Access rights review) + A.8.18
(User account review). Semantic quality is good on the new
model.

## Follow-ups closed

- Ship 5'.a MEDIUM finding 3 (musts_arioncomply has no stored
  `embedding_function_name`) — CLOSED
- Ship 5'.a MEDIUM finding 4 (two VectorRetriever() no-arg
  sites) — CLOSED
- The whole class of "same-dimension silent swap" risk on the
  musts collection — CLOSED (naming-aware embed fn + defensive
  rebuild works here now)

## Ship 5 progress

| Sub-arc | Status |
|---|---|
| 5'.a Audit | ✓ |
| **5'.b Embedding consolidation** | **✓** |
| 5'.c Temperature + tier2_generator migration | next |
| 5'.d Dead-code cleanup + LLM config module | future |
| 5'.e ai_call_log purpose CHECK cleanup | future |
| 5'.f Arc retrospective | close |

## Related

- [[ship-5-prime-a-llm-audit-2026-07-18]] — audit that surfaced this
- `rag/embedding_config.py` — new module, canonical constants
- `scripts/reindex_all.py` — one-shot rebuild CLI
