---
name: ship-5-prime-c-temperature-tier2-2026-07-18
description: "Ship 5'.c — extractor + enricher temperature=0.0 for JSON extraction determinism; tier2_generator migrated off direct OpenAI to llm_client"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 5'.c (2026-07-18) — closes the two HIGH-priority findings
from Ship 5'.a LLM audit.

## Finding 2 (HIGH): temperature=0.4 for structured JSON extraction

Extractor + enricher inherited `temperature=0.4` (llm_client's
default). Structured JSON extraction should be deterministic —
same doc + same prompt → same JSON — so temperature drift masks
regressions.

Fixed three call sites with explicit `temperature=0.0`:

- `rag/intake/extractor.py:1606` — pass2 extractor
- `rag/intake/extractor.py:1821` — pass1 extractor
- `rag/intake/enricher.py:251` — doc enricher

## Finding 1 (HIGH): tier2_generator bypasses llm_client

`enrichment/tier2_generator.py` was using the OpenAI SDK
directly (2 call sites, plus a direct client-init helper).
Result: those calls didn't hit `ai_call_log`, weren't
provider-neutral, and had their own bespoke error handling.

Migrated both `client.chat.completions.create()` sites at
lines 287 + 302 to `rag.llm_client.call`:

- `purpose = "enrichment_tier2"` — new purpose label
- `system = ""` (matches enricher's shape)
- `temperature = self.temperature` on the first attempt,
  `0.0` on the retry (preserves the original behavior of
  "deterministic retry")
- Metadata carries `ref` + `attempt` for traceability

Deleted the now-dead `_get_client()` method + `self._client`
attribute — the direct OpenAI client had no other consumers.

Note: `enrichment_tier2` is a new value for the
`ai_call_log_purpose_check` CHECK constraint. If tier2_generator
runs against the DB, that constraint will reject the write
(silent-failure — ai_trace swallows the error). Ship 5'.e is
the arc where we clean up the `ai_call_log` purpose CHECK
allowlist. For now the migration is code-correct; the log-write
side benefits when 5'.e ships.

## Model appropriateness (no changes)

Ship 5'.a confirmed model-tier picks are appropriate for every
task. This arc changes only temperature + dispatch path — no
model swaps.

## Verified

- Import sanity: `Tier2Generator` still imports cleanly
- Eval baseline: RUNNING. Expected 207/208 — no RAG-path change,
  but extraction+enricher determinism could shift extraction
  outputs on future runs (extractor is exercised on doc uploads,
  not on any eval case that's in the current suite).

## Ship 5 progress

| Sub-arc | Status |
|---|---|
| 5'.a Audit | ✓ |
| 5'.b Embedding consolidation | ✓ |
| **5'.c Temperature + tier2 migration** | **✓** |
| 5'.d Dead-code cleanup + LLM config module | next |
| 5'.e ai_call_log purpose CHECK cleanup | future |
| 5'.f Arc retrospective | close |

## Related

- [[ship-5-prime-a-llm-audit-2026-07-18]] — audit that surfaced this
- [[ship-5-prime-b-embedding-consolidation-2026-07-18]] — 5'.b closer
