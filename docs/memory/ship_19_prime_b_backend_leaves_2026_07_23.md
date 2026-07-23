---
name: ship-19-prime-b-backend-leaves-2026-07-23
description: "Ship 19'.b — backend LeafState + RelatedCard.leaves[]; populates per-leaf checklist data from build_per_must_advisory_data; initial eval regressed 4 cases (fixed in 19'.d)"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 19'.b — backend delivery of per-leaf checklist data for the
Ship 19 card polish arc. Commit `916519f`.

## Schema addition

New `LeafState` model in `rag/casefile/answer_schema.py`:

```python
class LeafState(BaseModel):
    leaf_id:             str    # e.g. "req:A.5.15:access_control_policy"
    title:               str    # humanized ("Access Control Policy")
    evidence_type:       str    # raw slug ("policy") — tooltip
    evidence_type_label: str    # humanized ("policy document")
    satisfied:           bool   # True → ✓, False → ○
    n_have:              int    # per-MUST count satisfied
    n_total:             int    # per-MUST count total
```

`RelatedCard` extended with `leaves: list[LeafState] = []`
(additive; existing SDK consumers unaffected).

## Augment path

`answer_augment._evidence_summary` now returns a 3-tuple
`(summary, still_needed, leaves)`. Populates `LeafState` for every
leaf whose label is known, marking `satisfied` from
`build_per_must_advisory_data.leaves[].satisfied`.

`build_related_cards` passes leaves through into the RelatedCard
constructor. Populated for ALL cards (primary + related). Frontend
decides render granularity in Ship 19'.c per the 19'.a
primary-only decision.

## LLM output rule extension

Rule 1 in `LLM_OUTPUT_RULES` extended to forbid restating
N-of-M count in `intro.text`:

```
Do NOT restate the N-of-M item count (e.g. "1 of 4 items present"
/ "0 of 18 required items present") — the primary card renders
that as a per-leaf checklist. Intro's job is to frame WHAT the
control requires + the overall verdict tag ("OFI-DRAFT",
"NC-DRAFT").
```

## Verified live on "how do I remediate A.5.15?"

```
INTRO: "ISO 27001 A.5.15 (Access control) requires ensuring
        authorized access... Currently OFI-DRAFT." (no N-of-M)

A.5.15 [OFI] primary — leaves=4:
  ✓ Management Approval  (3/3)
  ○ Access Control Policy (5/6)
  ○ Communication Record  (1/5)
  ○ Periodic Review       (1/5)
```

## Initial eval regression (fixed in 19'.d)

**Baseline 231 → 227/232 + 4 FAIL** on Ship 19'.b's initial run.
The new rule 1 over-generalized in JSON mode; LLM dropped:

- **#3** `show me our OFI findings` — MISSING 'OFI'
- **#10** `are we certified?` — MISSING 'certif'
- **#223** `what does ISO 27003 say...` — MISSING '27003'
- **#224** `what does ISO 27004 say...` — MISSING '27004'

Root cause: the subtractive "don't restate N-of-M" rule got
interpreted as a general "be tighter" instruction. LLM dropped
peripheral context words including verdict acronyms +
guidance-standard names + query-echo terms.

**Closed in Ship 19'.d** by:
1. Restructuring rule 1 to make explicit that N-of-M drop is
   THE ONLY subtractive rule + adding a positive query-echo
   constraint + 3 examples for different query shapes.
2. Reinforcing rule 7 with an explicit "regardless of brevity"
   clause + query-echo requirement.

Post-fix eval: **231/232 PASS + 1 WARN + 0 FAIL**.

## Backward compat

- `leaves` defaults to `[]`; controls without advisory data
  (single-leaf, Comply, N/A) get empty list → frontend falls
  back to existing `still_needed` chip surface.
- SDK unaffected: `leaves` is Optional with default `[]`.
- No changes to `answer_text` prose reconstruction: it composes
  from `intro.text + actions[title:body]` (unchanged).

## Ship 14'.a addendum alignment

1. **Role split?** YES — leaves inherit role via `RelatedCard.role`.
2. **Parallel CaseFile view?** YES — leaves data flows from
   `build_per_must_advisory_data` sharing CaseFile's role model.
3. **Deterministic routing?** N/A — presentation-layer arc.
4. **Guidance-normative discipline?** YES — reinforced in 19'.d.

## Ship 19 progress

| Sub-arc | Status |
|---|---|
| 19'.a Design memo | ✓ (c433d63) |
| **19'.b Backend leaves[] + prompt tweak** | **✓ (916519f, this doc)** |
| 19'.c Frontend checklist + intro dedupe | ✓ (62eb419) |
| 19'.d Rule refinement + eval + retro | next |

## Related

- [[ship-19-prime-a-card-polish-design-2026-07-23]] — design
- [[ship-18-prime-b-structured-backend-2026-07-23]] — the
  structured payload arc this extends
- [[ship-18-prime-c-frontend-cards-prompt-rules-2026-07-23]] —
  precedent for JSON-mode prompt-rule regressions
