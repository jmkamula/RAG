---
name: cross-framework-bridge-footer-2026-06-14
description: "SHIPPED 2026-06-14 (f23a2ca): rank_and_answer appends deterministic '↳ Bridges to ISO 27001 for Art.X: ...' footer for CROSS_FRAMEWORK queries. Closes the cases where the LLM dropped bridges from its answer when the article carried its own DerivedSpec posture. Bridges come from xfw_nodes_list + xfw_rel_map + posture_by_ref already in scope — no extra retrieval."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Pattern: when the LLM has freedom over surfacing structural data,
it's stochastic. When the data is authoritative (e.g. graph
traversal), surface it deterministically and let the LLM provide
prose around it.

## What ships

`rag/llm_answer.py:rank_and_answer` — just before
`return ComplianceAnswer`, when `intent.question_type ==
CROSS_FRAMEWORK` and any `Art.*` ref is in context, append:

```
↳ Bridges to ISO 27001 for Art.32: 6.1.2 [NC], 9.1 [OFI],
  A.5.1 [NC], A.5.15 [OFI], A.5.18 [OFI], ...
```

Mechanics:
- Article refs pulled from `intent.cited_refs`; falls back to
  query-string regex if cited_refs is empty.
- Bridge candidates are existing `xfw_nodes_list` entries (already
  fetched by retrieval) whose `xfw_rel_map[node_id]` includes the
  queried article OR any sub-paragraph of it (`Art.32.1.d` counts
  for an `Art.32` query via `lr.startswith(article + ".")`).
- Posture tag comes from `posture_by_ref[ref]['finding']`; defaults
  to "Not yet assessed" if absent.
- Dedupe by ref, sorted alphabetically.
- Footer is suppressed if every bridge ref is already in
  `answer_text` — keeps surface clean when LLM cites them all.

## Why this is the right shape

The LLM's prose remains the primary answer (verdict reasoning,
remediation guidance). The footer is a guaranteed structural
enumeration auditors and users can rely on. Same pattern as
`Evidence:`/`Gap:` deterministic labels in posture compose (see
[[posture-discipline-dup-label-fix]]).

The footer ships authoritative graph data — IMPLEMENTS / SUPPORTS /
GOVERNANCE edges in Neo4j — which the LLM can't invent and can't
hallucinate from. The risk of duplication is acceptable; the risk
of bridges silently missing is not (auditor visibility).

## What this didn't try

  - Force the LLM in the prompt to enumerate bridges — wouldn't
    handle hallucinated bridge refs and adds prompt complexity.
  - Restructure the Layer-2 presentation in the prompt — already
    well-structured; the LLM just sometimes prunes it.
  - Add to short_circuit_answer — cross-framework queries don't
    short-circuit; they go through rank_and_answer.

## Eval coverage

Locked by #24 + #25 (re-authored same day to `shape="cross_framework"`)
which now reliably PASS at 195/198. The shape validator catches
"no ISO bridge ref" if the footer ever regresses.

## Related
- [[case-24-art32-bridge-followup]] — the closing memo on the
  case that drove this
- [[posture-discipline-dup-label-fix]] — sibling deterministic-
  suffix pattern in posture compose
- [[polish-short-circuit-data-loss-guard]] — sibling rule: when
  the LLM drops structural data, fall back to deterministic
- [[curation-phase-b-batch-29a-2026-06-02]] — where Art.32 + Art.5
  got their own DerivedSpec direct evidence (the change that made
  the LLM stop needing bridges to answer)
