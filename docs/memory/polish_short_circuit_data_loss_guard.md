---
name: polish-short-circuit-data-loss-guard
description: "SHIPPED 2026-06-09 (942995b): polish_short_circuit_answer now enforces ref-drop + bullet-drop parity after llm.compose(), falling back to deterministic text on any silent drop."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

The LLM polish step that turns deterministic short-circuit answers
into prose was silently dropping data. The first observed case: a
"what documents have we uploaded" query whose deterministic answer
correctly listed 6 uploaded documents with platform_refs DOC013-19.
The polished output rewrote "Uploaded documents (6 total)" as
"5 total" and omitted the freshest entry (today's upload).

Previously `polish_short_circuit_answer` passed `required_refs` to
the composer and *trusted* the prompt-level instruction to preserve
them. In practice the LLM dutifully included whatever felt prosaic
and quietly dropped the rest. The docstring's "On any failure
compose() returns the deterministic text unchanged" guarantee was
aspirational, not enforced.

## What ships (rag/arion_graph.py)

Two post-compose guards in `polish_short_circuit_answer`:

1. **Ref-drop guard.** Every distinctive ref captured by
   `_SHORT_CIRCUIT_REQUIRED_REF_PATTERN` in the deterministic input
   must appear in the composed output. If `set(required_refs) -
   set(composed_refs)` is non-empty → `get_logger().warning(...)` →
   return `deterministic_answer`.

2. **Bullet-drop guard.** `_count_bullets()` over the composed
   output must be ≥ deterministic. Catches list-shape losses where
   refs are sparse (e.g. a doc with `filename` but no `platform_ref`
   would slip past the ref guard but show as a missing bullet).

The deterministic text is always preserved — the guards never let
the polished version leak through with less data than the input.

## When to extend

- Adding a new short-circuit answer with structured data: make sure
  every distinctive identifier matches `_SHORT_CIRCUIT_REQUIRED_REF_PATTERN`
  OR appears in a bullet-prefixed line. Otherwise neither guard sees
  it and the LLM can drop it freely.
- Adding a new ref shape (e.g. "ISMS-2024-001"): extend the regex.
- The bullet prefix set is `("•", "* ", "- ")`. Numbered lists
  (`1.`) are NOT counted as bullets. Add to `_BULLET_PREFIXES` if
  needed.

## Related

- [[stage1-detail-ux]] — short-circuit responses surface most
  prominently in HITL detail views.
- [[doc-discovery-vocabulary-gap-fix]] — same chat-surface code path.
