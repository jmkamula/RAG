---
name: per-must-recall-direction-c-2026-06-23
description: "SHIPPED 2026-06-23: Direction C from docs/per_must_recall_strategy.md — two-pass LLM extraction at upload time. Pass-2 targets partial leaves (1+ but <N MUSTs bound) with focused LLM calls listing only unfilled MUSTs. Closes the recall ceiling on single-pass extraction. Measured lift: 14 → 17 → 22 findings across iterations on same doc; A.5.15 flipped NC→OFI as direct result. Cost ~$0.08 extra per doc."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

The architectural answer to "single-pass LLM extraction can't reliably
catch every MUST visible in the text." Shipped same-day as the
strategy doc that framed the problem (`docs/per_must_recall_strategy.md`),
because the empirical data made the architectural ceiling obvious in
real-time:

## The arc that surfaced the ceiling

Same Access Control Policy.docx, same content, three iterations:

| Iteration | What changed | Findings | A.5.15 closest leaf |
|---|---|---|---|
| 1 (07:20) | morning extract — cap=15, default prompt | 14 | management_approval 1/3 |
| 2 (07:55, ec7f2bb) | cap=60, sign-off + revision-history prompt | 17 (+3) | 2/3 (caught approval_date) |
| 3 (10:56, 7a0f5b3) | + pass-2 enabled (Direction C) | **22 (+5)** | **3/3 ✓** (caught approval_target) |

The progression made the ceiling concrete: prompt tightening + cap
raising helped but kept missing cross-section metadata MUSTs.
**approval_target** (the "Version 1.1" reference in revision history
that needed linking to the approval-row date) was the canonical case —
needed a SECOND PASS with focused attention.

After tenant approved Direction-C bindings, **A.5.15 flipped NC → OFI**.
That's the posture movement the original morning upload couldn't
produce — exactly what the architecture promised but pass-1 couldn't
deliver alone.

## Implementation

Three new functions in `rag/intake/extractor.py`:

- `_find_partial_leaves(leaf_musts, pass1_findings)` — returns
  `[(leaf_id, unfilled_musts), ...]` for leaves with 1+ but <N coverage.
  Leaves with zero pass-1 bindings excluded (no signal the doc covers).

- `_llm_extract_pass2(text, leaf_id, evidence_type, unfilled_musts, ...)`
  — focused LLM call with a dedicated system prompt emphasising
  metadata + cross-section MUSTs. Distinct from the pass-1 system
  prompt: explicitly tells the LLM "this is a SECOND PASS, look
  again at metadata-shaped content the first pass skipped."

- `_run_pass2(doc, leaf_musts, pass1_findings, api_key, controls)` —
  orchestrates per-partial-leaf calls; reuses `_parse_llm_response`
  so all existing filters (grounding, crosscheck, questionnaire,
  referential demotion, validation) apply uniformly; merges via
  `(control_ref, checklist_item_id)` dedup with confidence priority.

Wired into `_extract_full` and `_extract_sections` after pass-1
completes. Pass-2 always runs doc-scoped (not section-scoped) because
cross-section linking is the whole point.

Cost: ~5 extra LLM calls per doc with partial-coverage leaves
(typically 1-5 per doc), ~$0.05-0.10 additional. Within the strategy
doc's projected cost model.

## Coupled fixes shipped same commit chain

Two bugs surfaced during Direction-C implementation that needed
addressing:

**`max_tokens=2000` truncation** (`ec7f2bb`): the raised cap +
expanded prompt made pass-1 emit longer responses that hit the
2000-token output limit and truncated mid-JSON. Symptom: extract
returned 0 findings with "JSON parse error". Fix: raised
`max_tokens` to 4000 across both pass-1 and pass-2 calls; added
JSON salvage that recovers N-1 complete findings from truncated
arrays.

**Stochastic same-MUST dedup**: pass-1 and pass-2 can both bind the
same MUST with slightly different evidence quotes. Without dedup
the engine sees duplicate findings on the same checklist_item_id.
The merge in `_run_pass2` keeps the higher-confidence binding;
parse-side dedup in `_parse_llm_response` was already there for the
within-pass case via section-based extraction.

## Empirical metadata MUSTs caught by pass-2 (today)

- `A.5.15:approval_target` ← *"Version 1.1"* in revision history
  (the canonical cross-section blind spot)
- `A.5.15:logical_rules`
- `A.5.16:authn_link`, `A.5.16:ownership`
- `A.5.18:modification_path`, `A.5.18:policy_reference`

These are the kinds of MUSTs single-pass LLM extraction always
struggled with — implicit metadata, cross-section references,
table-row metadata that "looks like" sign-off paperwork but is
actually first-class evidence per the engine model.

## What this doesn't fully solve

- **MUSTs the LLM never connects to evidence at all** — Direction C
  doesn't help if the doc evidences a MUST in a way the LLM
  semantically misses (not just textually). For these, the form
  (Direction A in the strategy) is still the deterministic
  completion path.
- **Whole leaves with 0/N coverage** — pass-2 only fires on partial
  leaves. A leaf the doc doesn't address at all stays empty.
  Correct behaviour, but operationally still requires tenant
  awareness via the dashboard advisory.
- **LLM stochasticity on the same MUST** — pass-1 and pass-2 may
  emit slightly different evidence quotes for the same MUST. The
  dedup keeps one; the dropped one is gone (no audit trail of
  "we tried both"). Acceptable for now.

## Related

- `[[per-must-binding-in-extractor-2026-06-15]]` — the B path that
  Direction C extends with a second pass
- `[[extractor-catalog-crosscheck-2026-06-15]]` — the validation
  signal that helps quantify Direction C's quality
- `[[intake-pipeline-architecture]]` — diagram should be updated
  with pass-2 row (next-thread polish)
- `[[strategic-pause-2026-06-15]]` — the prior pause that
  established the discipline of "step back when the pattern emerges"
- `[[templates-hybrid-2026-06-15]]` — Direction A in the strategy
  (still relevant for what Direction C can't reach)

## Strategy doc

Full reasoning, three-direction comparison, cost model, open
decisions, and prerequisites in `docs/per_must_recall_strategy.md`
(committed `ec7f2bb`). This memory entry indexes it from the
runtime memory pointer.
