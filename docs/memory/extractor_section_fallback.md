---
name: extractor-section-fallback
description: "SHIPPED 2026-06-09 (a2662ca): _scope_controls_to_section returning [] now falls back to doc-level scope instead of skipping the section. Stopped silently discarding 13/14 sections of a 120K-token meta-policy."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

The sections-path extractor (rag/intake/extractor.py `_extract_sections`)
runs section-by-section for large docs. Before each LLM call, it
narrows the candidate controls per-section via
`_scope_controls_to_section`, which uses (a) explicit refs in the
section text and (b) a small hand-written `keyword_map` over the
section heading (e.g. `"access" → A.5.15-18`, `"incident" →
A.5.24-28`, `"supplier" → A.5.19-23`).

If neither signal matched, the function returned `[]` and the caller
**skipped the section entirely** — no LLM call, no findings, no
evidence considered.

## Why the bug was invisible until doc_mappings

`_scope_controls_to_section` predates the doc_mappings pre-filter
([[doc-curation-engine-v1]]). When the only pre-filter was a generic
`evidence_type` match returning hundreds of candidate controls,
aggressive per-section narrowing was load-bearing — you couldn't
afford to send 100+ controls to the LLM per section.

After doc_mappings narrowed the candidate set to ~10-15 tight matches
at the doc level, the per-section narrowing became counterproductive:
it could strip the doc-level scope back down to `[]` for any section
whose heading wasn't in the small keyword_map. The doc_mappings
investment was being defeated by a downstream filter that was sized
for a pre-doc_mappings universe.

## Trigger case (2026-06-09)

`Information Security and Data Management Process.docx` — 14
sections, ~120K tokens. doc_mappings correctly identified 12
candidate controls (A.5.1, A.5.15-18, A.5.24, A.8.2, A.8.33,
Art.25/28/35, …). But the section headings were generic ("Purpose",
"Scope", "Roles", "Procedure", "Review", "Documentation") and only
one section had "incident" in its heading.

Pre-fix: 1 finding extracted (A.5.24, from the lone incident-matched
section). Post-fix: 7 findings + 11 xfw proposals (sections that
previously got skipped now reach the LLM with the 12-control scope).

## The fix (one block)

```python
section_controls = _scope_controls_to_section(controls, section, doc)
if not section_controls:
    # No section-specific signal → fall back to the doc-level scope.
    # `controls` here is already pre-filtered by doc_mappings, so
    # it's the tight target set, not the universe.
    section_controls = controls
```

The LLM's 40-char verbatim-quote bar keeps the wider scope from
generating false positives — the section either contains a
substantive quote for one of the 12 candidate controls or it
doesn't.

## When to revisit

- If a future doc-mappings policy returns >50 candidate controls per
  doc, per-section narrowing may need to come back to keep token
  cost down.
- If the keyword_map gets extended significantly, the fallback path
  becomes less load-bearing (more sections will match keywords
  directly).
- The keyword_map itself (rag/intake/extractor.py:609-623) is
  hand-curated and could become outdated as new doc shapes ship —
  consider mining heading words from the doc_mappings corpus.

## Related

- [[doc-curation-engine-v1]] — the doc-level pre-filter this defers to.
- [[doc-discovery-vocabulary-gap-fix]] — same extractor pipeline,
  different layer.
