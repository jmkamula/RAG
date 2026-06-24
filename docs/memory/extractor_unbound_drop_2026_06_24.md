---
name: extractor-unbound-drop-2026-06-24
description: "SHIPPED 2026-06-24: extractor now drops findings with no checklist_item_id unconditionally. Closes the last open follow-up from the doc-reextraction workstream. Cleaned up 26 pre-fix unbound + 4 fresh unbound on Arion. Un-mapped docs now surface as 0-findings, making the doc_mapping gap visible instead of polluting Stage-1 with inert control-level matches."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What and why

The 2026-06-23 doc re-extraction workstream left 26 active unbound
findings on Arion (`checklist_item_id IS NULL`,
`inference_source='extracted'`). Per Phase-1 retirement
(2026-06-13) the engine ignores unbound rows, so they were inert —
but they cluttered Stage-1 with "almost evidence" that looked
real to the tenant.

Two-stage fix:

1. **First attempt** (gated): drop only when
   `valid_items_by_ctrl.get(ref)` is non-empty. Meaning: drop when
   the doc_mapping path provided MUST candidates for this control
   but the LLM failed to bind. Pre-Direction-C un-mapped paths
   (legacy fallback) kept control-level findings.
   
   Result: smoke-test re-extract of Vendor Security Assessment
   Report.docx still produced 4 unbound because that doc has no
   doc_mapping. The legacy fallback path kicked in.

2. **Tightening** (unconditional): drop unbound regardless of
   whether MUSTs were available. Reasoning: post-Direction-C, the
   canonical path is doc_mappings + per-MUST binding. If the LLM
   couldn't bind, the right answer is to add the missing
   doc_mapping — not to emit inert control-level matches that
   look like evidence.

## Implementation

In `rag/intake/extractor.py::_parse_llm_response`, after the
crosscheck block and before appending the DocumentFinding:

```python
if bound_item_id is None:
    dropped_unbound += 1
    continue
```

`bound_item_id` is set on line ~1220 only when the LLM's
`checklist_item_id` is in the valid set for this control. So this
drop catches both (a) un-mapped docs where no MUSTs were supplied
and (b) mapped docs where the LLM didn't emit a valid id.

Added `dropped_unbound` counter to telemetry log + extraction
metrics (mirrors the other drop reasons).

## Design pressure

The change makes the doc_mapping coverage gap *visible*. Before:
un-mapped docs produced control-level "evidence of awareness"
findings that engaged Stage-1 review attention but didn't move
posture. After: un-mapped docs produce 0 findings, which surfaces
clearly in the intake-quality dashboard as "this doc isn't
contributing — author a doc_mapping or skip the doc".

Smoke-test confirmation: Vendor Security Assessment Report.docx
re-extract after the unconditional drop went from 4 unbound → 0
findings. Two chunks reported `unbound=2` + `unbound=1` (3
findings successfully dropped). The doc's doc_mapping gap is now
the right next action (author a vendor_security_assessment.yaml
umbrella, similar to today's training_awareness_policy.yaml fix).

## What was cleaned up

| Cohort | Rows | rejection_reason |
|---|---|---|
| Pre-fix unbound (26 from 2026-06-23 workstream) | 26 | `unbound_control_level_match_2026_06_24: pre-fix residue; extractor now drops unbound when MUST candidates were available` |
| Fresh unbound from re-extracts during the fix-in-progress (4) | 4 | `unbound_control_level_match_2026_06_24: extractor now drops unbound unconditionally; un-mapped docs surface as 0-findings to flag the doc_mapping gap` |

## Final state on Arion

```
inference_source | unbound | bound
extracted        |       0 |   329
form             |       0 |     0
leaf_scan        |       0 |    51
workbook         |       0 |   204
xfw_bridge       |      95 |     0   (by-design — bridges don't bind)
```

Only by-design unbound (xfw_bridge) remains.

## Open follow-up — doc_mapping gaps surfaced by the change

Docs that previously emitted unbound but had no doc_mapping match
will now show 0 findings until a mapping is authored:

- Vendor Security Assessment Report.docx (supplier family
  assessment-report shape)
- 214427_Client Report 27001_DG3D87.pdf (Czech audit report —
  ISMS clauses 9.x/10.x)
- Lead Sales and Client Data Handling.docx (multi-control PII
  procedure spanning A.5.1/2/12/15/31/34/36/37, A.8.2/10)
- Compliance Requirements.docx (A.5.31 register-shape)
- HR Security Policy.docx (A.6.3 + A.6.6 not covered by existing
  hr_security_policy.yaml)

Each is a candidate for a hand-authored doc_mapping umbrella
following the established pattern. Lower priority than the
zero-finding-doc fix (those were already at 0 active bound);
these still have *some* bound findings from existing partial
matches.

## Related

- [[doc-reextraction-workstream-2026-06-23]] — the workstream
  that surfaced these 26 unbound; this entry closes its last
  follow-up
- [[doc-mapping-training-awareness-2026-06-24]] — same-day fix
  for a different doc_mapping vocabulary gap; pattern to follow
  for the open follow-ups above
- [[doc-curation-engine-v1]] — Direction C extractor (per-MUST
  binding + grounding)
