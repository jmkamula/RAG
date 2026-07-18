---
name: ship-5-prime-a-llm-audit-2026-07-18
description: "Ship 5'.a — full audit of every LLM + embedding call site; findings + prioritization for Ship 5'.b+ fixes"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 5'.a (2026-07-18) — opens Ship 5 arc. Systematic inventory
of LLM + embedding usage across the codebase, targeting
best-practice + consistency (particularly index-vs-query
embedding model alignment).

## Central dispatch: `rag/llm_client.py::call()`

Every LLM call SHOULD go through this. Provider-neutral
(anthropic wire for `claude-*`, openai-compatible for
everything else), auto-logs to `ai_call_log`, never raises.

Signature:
```
call(system, user, model, *, purpose, max_tokens=1500,
     temperature=0.4, timeout_s=60.0, messages=None, ...)
```

## LLM call sites — full inventory

| # | File:line | Model | Purpose | Temp | Max tokens | Timeout | Via llm_client? |
|---|---|---|---|---|---|---|---|
| 1 | `llm_answer.py:1655` (compose) | `gpt-4o` (`self.answer_model`) | `chat` | `self.temperature` (default 0.4) | var | 180s | ✓ |
| 2 | `llm_answer.py:1718` (verify) | `gpt-4o-mini` (`self.verify_model`) | `chat` | **0.0** | 400 | 60s (default) | ✓ |
| 3 | `llm_answer.py:1784` (correct) | `gpt-4o` (`self.answer_model`) | `chat` | `self.temperature` | var | 60s | ✓ |
| 4 | `classifier.py:1763` | `gpt-4o-mini` (`clf_model`/`clr_model`) | `classifier` | **0.1** | 5/120/200/250 | 60s | ✓ |
| 5 | `enricher.py:251` | `claude-haiku-4-5-20251001` | `enricher` | 0.4 (default) | 300 | 15s | ✓ |
| 6 | `critic_verifier.py:429` | `claude-sonnet-4-6` | `extractor` | **0.0** | var | var | ✓ |
| 7 | `extractor.py:1606` (pass2) | `claude-sonnet-4-6` (`EXTRACT_MODEL`) | `extractor_pass2` | 0.4 (default) | 4000 | 60s | ✓ |
| 8 | `extractor.py:1821` (pass1) | `claude-sonnet-4-6` (`EXTRACT_MODEL`) | `extractor` | 0.4 (default) | 4000 | 60s | ✓ |
| 9 | `gatekeeper.py:279` | `gpt-4o-mini` (env override `GATEKEEPER_MODEL`) | `consensus_gatekeeper` | **0.0** | 150 | 15s | ✓ |
| 10 | **`enrichment/tier2_generator.py:287,302`** | `gpt-4o-mini` (default arg) | *(no purpose tag)* | ? | ? | ? | **✗ direct OpenAI SDK** |

### Direct OpenAI clients (bypass llm_client)

- **`enrichment/tier2_generator.py:389`** — `openai.OpenAI(api_key=...)` + `.chat.completions.create()` at lines 287 + 302. Purpose: xfw pair generation for enrichment JSON. **NOT auto-logged** in `ai_call_log`. Fix in Ship 5'.b.
- `rag/classifier.py:1809` — `openai.OpenAI(...)` init, but `self._openai` is **NEVER USED**. Dead code — the `_call_llm` path uses `llm_call`. Delete in Ship 5'.b cleanup.
- `rag/llm_answer.py:1995` — `openai.OpenAI(...)` init at `_get_client()`. Similar dead-pathway suspicion; verify no live consumer.
- `rag/llm_answer.py.old.py` — legacy file, direct OpenAI calls throughout. Whole file is dead; delete in Ship 5'.b.

## Embedding call sites — full inventory

### Vector store: `chroma_db/`

Two separate collection families with different embedding models:

| Collection | Indexed with | Indexer script | Runtime users |
|---|---|---|---|
| `iso27001_2022` | **`text-embedding-3-large`** (3072 dim) | `vector/indexer.py` | `VectorRetriever` (chat / arion_graph / extractor / critic_verifier) |
| `gdpr_2016_679` | **`text-embedding-3-large`** | `vector/indexer.py` | same |
| `iso27701_2019` | (via `scripts/index_27701_to_chroma.py` → `vector/indexer.py`) | — | same |
| `arioncombly_all` | **`text-embedding-3-large`** | `vector/indexer.py` | same |
| `musts_arioncomply` | **`text-embedding-3-small`** (1536 dim) | `scripts/build_must_index.py` | `rag/intake/must_embedding_lookup.py` |

### Index-vs-query alignment — where it holds + where it's fragile

**Bedrock principle: index-time embedding model MUST equal query-time
embedding model.** Different models produce embeddings in
incompatible vector spaces; comparing them returns garbage.

**Today the system IS consistent** — both collection families
match index-time and query-time. But it's held together by two
different mechanisms, one robust and one fragile.

**RequirementNode collections (iso/gdpr/27701/all):** ROBUST.
- Indexed with `text-embedding-3-large` (3072-dim).
- `vector/indexer.py::OpenAIEmbeddingFunction.name()` returns
  `"openai-text-embedding-3-large"`, stored in Chroma's
  `collection_metadata` under key `embedding_function_name`.
- `VectorIndexer._make_embed_fn_from_name()` re-hydrates the
  correct function on collection open. So a runtime call with a
  MISMATCHED `embedding_model` arg still uses the right function.
- Confirmed via sqlite3 inspection: all 3 collections carry
  `ef=openai-text-embedding-3-large`, `dim=3072`.

**musts_arioncomply collection:** CONSISTENT TODAY BUT FRAGILE.
- Indexed with `text-embedding-3-small` (1536-dim).
- `scripts/build_must_index.py` uses Chroma's *builtin*
  `chromadb.utils.embedding_functions.OpenAIEmbeddingFunction`,
  which does NOT store a name in collection_metadata (verified:
  `ef=NONE` on disk).
- `rag/intake/must_embedding_lookup.py::EMBED_MODEL = "text-embedding-3-small"` is a hardcoded constant matching the builder's.
- Discipline gap: two matching hardcoded constants in two files.
  If someone bumps one and not the other, the outcome depends on
  whether the new model has the SAME embedding dimensions:
  * **Different dimensions** (e.g. swap `-3-small` for `-3-large`):
    Chroma raises loudly with
    `Collection expecting embedding with dimension of 1536, got 3072`.
    Verified empirically — see below.
  * **Same dimensions** (e.g. swap `-3-small` for `ada-002`,
    both 1536-dim): No Chroma error — silent semantic garbage.
  So the actual silent-wrong-answer risk is narrower than "any
  swap"; it's specifically "swap to a different model with
  matching dimension". Low probability but non-zero.
- Fix: switch `build_must_index.py` to use
  `vector/indexer.py`'s naming-aware `OpenAIEmbeddingFunction` so
  the stored metadata + defensive rebuild path works here too.

### The dimension safety net — verified empirically

Direct test in Ship 5'.a: force a caller to query a 3072-dim
collection (`iso27001_2022`) using a 1536-dim embedding function.
Chroma refused with:

    InvalidArgumentError: Collection expecting embedding with
    dimension of 3072, got 1536

So the ONLY silent-failure mode is same-dimension model swaps.
`text-embedding-3-small` and `text-embedding-ada-002` are both
1536-dim; that pair is the concrete instance of the risk today.

### Runtime `VectorRetriever` instantiation

- `rag/orchestrator.py:779` — passes `cfg.embedding_model` explicitly
  (default `"text-embedding-3-large"`). ✓
- `rag/intake/extractor.py:2415` — calls `VectorRetriever()` with NO
  args. Falls through to `VectorIndexer` default (`"text-embedding-3-small"`).
  Would mismatch the stored `-large` in RequirementNode collections
  BUT the defensive `_make_embed_fn_from_name()` rebuild catches it.
  RELIES on the defensive path, not the caller's argument.
- `rag/intake/critic_verifier.py:168` — same pattern as extractor.

**Assessment:** RequirementNode collections work today thanks to
the defensive rebuild; if the rebuild ever regresses, the 2
no-arg call sites go silently broken. musts_arioncomply has no
such safety net.

## Model-tier alignment (task appropriateness)

| Task | Model | Appropriate? |
|---|---|---|
| Chat answer composition (`gpt-4o`) | Heavy reasoning + long-form prose | ✓ |
| Chat verify+correct (`gpt-4o-mini`) | Small JSON verdict | ✓ (cheap) |
| Query classifier (`gpt-4o-mini`) | Small structured decision | ✓ |
| Consensus gatekeeper (`gpt-4o-mini`) | Small structured decision, deterministic | ✓ |
| Enricher (`claude-haiku`) | Small structured JSON | ✓ |
| Extractor pass1+pass2 (`claude-sonnet`) | Long-form structured extraction from docs | ✓ |
| Extractor critic (`claude-sonnet`) | Verify extractor output | ✓ |
| tier2_generator (`gpt-4o-mini`) | Enrichment JSON | ✓ (but bypasses llm_client — see finding 1) |

Overall: model-tier picks look right. **No wrong-model-for-task
issues found.**

## Temperature discipline

Task category | Site | Temp | Should be |
|---|---|---|---|
| Extraction (structured JSON) | `extractor.py` pass1+pass2 | 0.4 (default) | **0.0** — deterministic |
| Enrichment (structured JSON) | `enricher.py` | 0.4 (default) | **0.0** — deterministic |
| Chat compose | `llm_answer.py` compose | 0.4 | ~0.4 keep |
| Chat correct | `llm_answer.py` correct | 0.4 | Consider 0.0-0.2 (correction should be deterministic) |
| Verify | `llm_answer.py` verify | 0.0 | ✓ |
| Classifier | `classifier.py` | 0.1 | ✓ |
| Consensus gatekeeper | `gatekeeper.py` | 0.0 | ✓ |
| Extractor critic | `critic_verifier.py` | 0.0 | ✓ |

**Finding:** `extractor.py` and `enricher.py` inherit the default
`temperature=0.4` from `llm_client.call()`. Extraction should be
deterministic — same doc + same prompt → same JSON. A future
regression in extraction would be near-impossible to debug if
temperature drift is masking it.

## Timeout discipline

Task | Timeout | Assessment |
|---|---|---|
| Chat compose | 180s | ✓ (long-form answers can take 60-120s) |
| Chat verify / correct | 60s (default) | ✓ |
| Classifier | 60s (default) | ✓ (small responses; could reduce to 15s) |
| Enricher | 15s | ✓ |
| Extractor pass1+pass2 | 60s | ✓ (large context; could go 90-120s for safety) |
| Extractor critic | var (caller passes) | ✓ |
| Gatekeeper | 15s | ✓ |

## Findings — prioritized

Ship 5'.b+ fixes:

**HIGH priority (correctness / silent-failure surface):**

1. **`enrichment/tier2_generator.py` bypasses `llm_client`.**
   Direct OpenAI SDK calls at lines 287 + 302, direct client init
   at line 389. Not logged in `ai_call_log`; not covered by the
   provider-neutral routing. Migrate to `llm_client.call`.

2. **Extractor + enricher use `temperature=0.4` for structured
   JSON extraction.** Should be `0.0`. Fix in both call sites
   (extractor.py:1606,1821 + enricher.py:251).

**MEDIUM priority (fragility / hidden coupling):**

3. **`musts_arioncomply` collection has no stored
   `embedding_function_name`** metadata. If `EMBED_MODEL` drifts
   between `build_must_index.py` and `must_embedding_lookup.py`
   TO A DIFFERENT MODEL WITH THE SAME DIMENSION (e.g. `-3-small`
   → `ada-002`, both 1536-dim), queries return silent semantic
   garbage. Different-dimension swaps are caught loudly by
   Chroma's dim check — see "dimension safety net" above.
   Fix: switch the builder to `vector/indexer.py`'s naming-aware
   `OpenAIEmbeddingFunction` so the defensive rebuild path works
   here too.

4. **2 runtime `VectorRetriever()` calls with no args**
   (extractor.py:2415, critic_verifier.py:168) rely on the
   defensive `_make_embed_fn_from_name()` rebuild path.
   Explicit caller arg would remove the hidden dependency.
   Change to `VectorRetriever(embedding_model="text-embedding-3-large")`
   or pull from a shared constant.

**LOW priority (dead code / cleanup):**

5. **`rag/classifier.py:1804-1822`** — `_get_openai_client()`
   builds `self._openai` but the client is never used. Delete.

6. **`rag/llm_answer.py:1990-2013`** — `_get_client()` (direct
   OpenAI) may be dead too. Verify + delete if so.

7. **`rag/llm_answer.py.old.py`** — legacy file with pre-Ship 2'
   direct-OpenAI calls. Delete.

**INFORMATIONAL (not fixes, just note):**

8. Consider a **top-level LLM config module** with named
   constants:
   * `MODEL_CHAT_ANSWER = "gpt-4o"`
   * `MODEL_CLASSIFIER = "gpt-4o-mini"`
   * `MODEL_EXTRACTOR = "claude-sonnet-4-6"`
   * `EMBED_MODEL_REQUIREMENTS = "text-embedding-3-large"`
   * `EMBED_MODEL_MUSTS = "text-embedding-3-small"`
   Currently model names are scattered across ~10 files as
   default args. One config module makes future migrations
   (e.g. gpt-4o → gpt-4o-2025) a single edit.

9. `ai_call_log_purpose_check` CHECK constraint has been
   throwing warnings during evals for months (Ship 3'/4'
   logs). Someone is calling `log_llm_call` with a purpose
   value not in the allowlist. Worth a quick fix.

## Ship 5 roadmap ahead

| Sub-arc | Scope |
|---|---|
| 5'.a Audit | ✓ THIS ARC |
| 5'.b Temperature + tier2_generator migration | HIGH priority findings 1 + 2 |
| 5'.c Embedding metadata + explicit args | MEDIUM findings 3 + 4 |
| 5'.d Dead-code cleanup + LLM config module | LOW findings 5-8 + informational 8 |
| 5'.e ai_call_log purpose CHECK cleanup | INFORMATIONAL 9 |
| 5'.f Arc retrospective | close-out |

## Related

- [[ship-2-prime-retrospective-2026-07-17]] — the case-file
  arc that consolidated the chat pipeline; this audit follows up
- [[ship-4-prime-arc-retrospective-2026-07-18]] — previous arc
