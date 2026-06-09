---
name: intake-determinism-levers
description: "SHIPPED 2026-06-09 (2f28d9f, schema_v37): two levers to reduce intake non-determinism — admin endpoint for unmatched doc_mappings patterns + SHA-keyed enricher cache. Strategic answer to 'how do we get to deterministic state instead of trial-and-error on each doc shape'."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

The intake pipeline has three sources of non-determinism — addressed
in decreasing order of impact:

1. **doc_mappings coverage gaps** (largest) — uncurated doc shapes
   fall through to legacy `_scope_controls` (50-control "policy"
   clause-scope). Drives wrong-shape LLM evaluations + yellow yield
   flags.

2. **LLM enricher stochasticity** — same doc bytes → different
   `topic_tokens` across runs → different doc_mappings matches.

3. **LLM extractor stochasticity** — same scope → different findings
   per run. Quality telemetry catches the egregious cases via the
   `dropped_hallucinated` counter.

schema_v37 ships levers for (1) and (2). The remaining extractor
stochasticity is genuine "LLM doing creative reading of the doc" —
acceptable with the telemetry as guardrail.

## Lever 1: unmatched-pattern admin endpoint

`GET /api/v1/admin/intake/unmatched-patterns?days=N&limit=M`

Queries `intake_trace_log` for rows with `doc_mappings_match_count=0`
(legacy fallback fired), tokenises filenames via the
`workbook_discovery` tokenizer (the same one doc_mappings YAMLs use
for fingerprints), groups by token tuple, returns top patterns.

Operational use: nightly or on-demand. When the same filename token
pattern (e.g. `[it, security, policy]`) appears N times unmatched,
that's a candidate umbrella YAML to author. Surfaces gaps
proactively instead of waiting for a tenant complaint.

Example payload:
```json
{
  "patterns": [
    {"tokens": ["it","security","policy"], "n_uploads": 5,
     "examples": ["IT Security Policy.docx", ...]},
    ...
  ]
}
```

## Lever 2: SHA-keyed enricher cache

`enricher_cache` table — `(sha256, doc_type, standard_ids,
topic_tokens, scope_statement, hit_count, last_hit_at)`. The
`enrich()` function looks up cache by `doc.source_sha256` before
the LLM call; on hit it restores the cached fields and skips the
LLM entirely.

Same bytes → deterministic enrichment → deterministic doc_mappings
match → deterministic LLM scope. The downstream LLM extractor still
has its own stochasticity, but the *scope* is now stable.

Cache misses naturally rebuild. Cache TTL is implicit: schema
includes `cached_at` + `last_hit_at` for a future nightly purge
(none scheduled yet).

The helpers `_enricher_cache_load` / `_enricher_cache_store` in
`rag/intake/enricher.py` fail soft — any cache error degrades to a
fresh LLM call. Never raises.

## How to apply

- **Operational tuning loop**: hit `/admin/intake/unmatched-patterns`
  → see the top pattern → write the YAML → next upload uses it.
  Iterative coverage growth driven by real tenant uploads, not
  speculation.
- **Re-upload determinism**: tenants who re-upload the same file
  (or different tenants uploading the same template) now get the
  same scope and same matches. SHA dedup prevents the upload itself
  but cache also serves cross-tenant identical bytes if it ever
  matters.
- **When the cache produces wrong output**: rare but possible if
  the LLM had a bad day on the cached run. Delete the row from
  `enricher_cache WHERE sha256 = '<hash>'` and re-upload — next run
  rebuilds the cache.

## What's NOT addressed by this work

- **LLM extractor stochasticity**: still varies finding count
  across runs of the same doc. Acceptable per [[compose-posture-
  any-progress-ofi]] — the strict rule means partial-evidence
  variance doesn't move the verdict anyway. Future strategic fix
  if needed: per-tenant snapshot of "expected findings" + drift
  alert.
- **Auto-authoring doc_mappings YAMLs**: the unmatched-patterns
  endpoint surfaces gaps but doesn't fill them. An LLM-assisted
  authoring tool that proposes YAMLs from unmatched doc bodies
  could close the loop, but that's a separate future build.

## Related

- [[doc-curation-engine-v1]] — the doc_mappings architecture this
  works within.
- [[intake-quality-telemetry]] — the schema_v35 telemetry that the
  unmatched-pattern endpoint extends.
- [[doc-discovery-vocabulary-gap-fix]] — synonym + topic_tokens
  layer; topic_tokens stochasticity is what the SHA cache fixes.
- [[table-heavy-docx-rescue]] / [[extractor-grounding-rules]] —
  earlier same-day fixes for extractor-side determinism issues.
