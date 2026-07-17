---
name: ship-3-prime-l-iso27001-2013-renumber-2026-07-17
description: "Ship 3'.l — closes the deferred ISO 27001:2013→2022 renumbering data-quality arc"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 3'.l (2026-07-17) — pivots off the notification arc after 11
sub-arcs. Closes a long-deferred data-quality item from CLAUDE.md.

## Problem

CLAUDE.md's build-sequence table carried `ISO 27001:2013→2022
renumbering in source JSONs (12 stale refs) — DEFERRED`. The
`framework_scope_guard` in `rag/guards/framework_scope_guard.py`
had been catching post-hoc leaks where the LLM cited 2013-style
Annex A refs (A.9.x, A.10.x, ..., A.18.x — controls that were
consolidated into A.5-A.8 in the 2022 revision). But the source
data had at least some remaining stale refs polluting the graph
and downstream context.

## What I found (audit)

A systematic sweep for legacy 2013 Annex A refs across
production data (excluding tests / prompt-guard text / comments)
turned up two files:

1. `gdpr_nodes_phase2.json` — 12+ raw occurrences of
   `"ISO27001:2022:A.9.1"` and `"ISO27001:2022:A.9.3"` in
   `cross_framework_summary` blocks. Reading the rationale text
   next to each:
   * "**Monitoring, measurement, analysis and evaluation**
     produces the metrics..." → intent was ISMS clause **9.1**
     (Performance evaluation ‣ Monitoring, measurement, analysis
     and evaluation).
   * "**Management review** demonstrates top management
     accountability..." → intent was ISMS clause **9.3**
     (Management review).
   Author had prefixed ISMS chapter refs with `A.` as if they
   were Annex A. Not a 2013 leak — a **misprefixing bug**.

2. `db/doc_mappings/compliance_requirements_register.yaml` —
   `cross_control_links: A.18.1`. Genuine 2013 leak. A.18 was
   the 2013 "Compliance" chapter, absorbed into A.5.31 in 2022
   (which was already the mapping's PRIMARY target). Rationale
   text said "compliance obligations feed audit / management
   review" — matching ISMS clause 9.2 (Internal audit) better
   than the self-reference.

## What shipped

- **`gdpr_nodes_phase2.json`**: 16 substitutions via sed
  * `"ISO27001:2022:A.9.1"` → `"ISO27001:2022:9.1"` (×8)
  * `"ISO27001:2022:A.9.3"` → `"ISO27001:2022:9.3"` (×8)
  * Display-title forms (`"ISO 27001:2022 A.9.1"` → `"ISO 27001:2022 9.1"`)
  * JSON stayed valid; only `cross_framework_summary` text
    properties on GDPR nodes changed.

- **`db/doc_mappings/compliance_requirements_register.yaml`**:
  * `A.18.1` → `9.2` (Internal audit) with a comment explaining
    the reasoning (rationale text was the tell).

- **Neo4j reload** — 429 nodes reloaded via `load_neo4j.py`.
  Post-reload verification: 0 nodes still holding stale refs;
  3 nodes each now hold the corrected `9.1` / `9.3` refs.

- **CLAUDE.md build-sequence** — DEFERRED row replaced with
  SHIPPED marker.

## Why the guard stays

`framework_scope_guard` (`rag/guards/framework_scope_guard.py`)
continues catching 2013-form refs the LLM emits stochastically
from training-data bias. Source data being clean doesn't stop
the LLM's tendency to write "A.9.2" — the guard is defensive
against LLM behaviour, not source data. Keep the guard.

## Baseline

**207/208 PASS + 1 WARN + 0 FAIL**
(`results/eval_20260717_1836_ship3l.csv`). Same #200 WARN.
The renumbering doesn't affect the RAG path since the fixed
refs were in `cross_framework_summary` text that mostly feeds
diagnostic context, and the guard's Layer A namespace filter
would have stripped them anyway.

## Related

- [[cross-framework-bridge-footer-2026-06-14]] — where xfw
  posture surfacing lives
- `framework-role-model-arc` — the role-model that made these
  cross-refs matter in the first place
