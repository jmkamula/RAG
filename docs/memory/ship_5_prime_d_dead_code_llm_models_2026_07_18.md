---
name: ship-5-prime-d-dead-code-llm-models-2026-07-18
description: "Ship 5'.d — deleted dead direct-OpenAI code + created rag/llm_models.py as single source of truth for model choices"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 5'.d (2026-07-18) — closes Ship 5'.a LOW findings 5-7 +
INFORMATIONAL 8. Two concerns: dead code cleanup + centralize
model-name constants.

## Dead code deleted

Three dead pathways surfaced by Ship 5'.a audit:

1. **`rag/classifier.py::_get_openai`** (lines 1801-1821) —
   built `self._openai = openai.OpenAI(...)` at init but was
   NEVER consumed. Confirmed by grep: only init sites, no
   `.chat.completions.create()` calls. All classifier LLM
   traffic goes through `rag.llm_client.call`. Deleted the
   method + the `self._openai = None` init line.

2. **`rag/llm_answer.py::_get_client`** (lines 1975-2013) —
   same pattern. `self._client` init + `_get_client()` method
   both dead. All llm_answer LLM traffic goes through
   `rag.llm_client.call` via lines 1655/1718/1784. Deleted.

3. **`rag/llm_answer.py.old.py`** — 30KB legacy file from
   pre-Ship-2' era. Not imported anywhere in the tree. Deleted.

## New module: `rag/llm_models.py`

Single source of truth for LLM model choice. Parallel to
`rag/embedding_config.py` shipped in Ship 5'.b.

Constants (with env override each):

    MODEL_CHAT_ANSWER    = "gpt-4o"                (chat compose)
    MODEL_CHAT_VERIFY    = "gpt-4o-mini"           (verify+correct)
    MODEL_CLASSIFIER     = "gpt-4o-mini"           (classifier)
    MODEL_CONSENSUS_GK   = "gpt-4o-mini"           (Ship 1 gatekeeper)
    MODEL_EXTRACTOR      = "claude-sonnet-4-6"     (extractor + critic)
    MODEL_ENRICHER       = "claude-haiku-4-5-20251001" (doc enricher)
    MODEL_ENRICHMENT_T2  = "gpt-4o-mini"           (offline tier2)

Every constant is `os.getenv("MODEL_X", default)` so a partner
can override without code changes. `MODEL_CONSENSUS_GK` reuses
the existing `GATEKEEPER_MODEL` env var for backwards compat.

`all_models()` helper returns a snapshot for diagnostics /
smoke tests.

## Call sites migrated

Every hardcoded model string in the codebase now references the
config module:

  * `rag/llm_answer.py::LLMAnswer.__init__` — `MODEL_CHAT_ANSWER` +
    `MODEL_CHAT_VERIFY`
  * `rag/classifier.py::QueryClassifier.__init__` — `MODEL_CLASSIFIER`
    for both classify + clarify defaults
  * `rag/intake/extractor.py` — `EXTRACT_MODEL` now `from
    rag.llm_models import MODEL_EXTRACTOR as EXTRACT_MODEL`
    (preserves local alias for existing callers)
  * `rag/intake/enricher.py` — `MODEL_ENRICHER` imported lazily
    at call site
  * `rag/intake/critic_verifier.py` — `MODEL_EXTRACTOR` (critic
    shares the extractor's tier)
  * `rag/consensus/gatekeeper.py::_gatekeeper_model` — reads
    `MODEL_CONSENSUS_GK` (which itself reads `GATEKEEPER_MODEL`)
  * `enrichment/tier2_generator.py::Tier2Generator.__init__` —
    `MODEL_ENRICHMENT_T2`; also fixed the argparse `--model`
    default from hardcoded to `None` so it falls through to the
    class default.

## Model tier snapshot (post-migration)

    MODEL_CHAT_ANSWER        = gpt-4o
    MODEL_CHAT_VERIFY        = gpt-4o-mini
    MODEL_CLASSIFIER         = gpt-4o-mini
    MODEL_CONSENSUS_GK       = gpt-4o-mini
    MODEL_EXTRACTOR          = claude-sonnet-4-6
    MODEL_ENRICHER           = claude-haiku-4-5-20251001
    MODEL_ENRICHMENT_T2      = gpt-4o-mini

No model changes — the audit confirmed all picks are
appropriate. This arc changes only WHERE the strings live.

## Verified

- All 7 modules import cleanly
- `all_models()` returns the expected values
- API server boots + eval running

## Migration story

Future model bumps (e.g. gpt-4o → gpt-4o-2025) are now:

    1. Edit `rag/llm_models.py::MODEL_X`
    2. Re-run relevant eval slice
    3. Update `rag/ai_trace.py::_MODEL_PRICING` if pricing differs

Or, per-partner without code changes:

    export MODEL_CHAT_ANSWER=gpt-4o-2025

## Ship 5 progress

| Sub-arc | Status |
|---|---|
| 5'.a Audit | ✓ |
| 5'.b Embedding consolidation | ✓ |
| 5'.c Temperature + tier2 migration | ✓ |
| **5'.d Dead code + LLM config module** | **✓** |
| 5'.e ai_call_log purpose CHECK cleanup | next |
| 5'.f Arc retrospective | close |

## Related

- [[ship-5-prime-a-llm-audit-2026-07-18]] — audit that surfaced these
- [[ship-5-prime-b-embedding-consolidation-2026-07-18]] —
  companion config module (`rag/embedding_config.py`)
