---
name: ship-19-prime-a-card-polish-design-2026-07-23
description: "Ship 19'.a — card polish design memo; primary card gains per-leaf checklist (✓ fulfilled / ○ missing) with actual leaf titles; intro drops N-of-M summary + duplicated ref chip"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 19'.a — opens Ship 19 arc (chat card polish). Direct
follow-up to Ship 18 landing the structured payload — user
tested the new UI and flagged three concrete usability gaps.

## User feedback (source of the arc)

Test query: "how do I remediate A.5.15?" against the Ship 18
card render. Three issues raised:

1. **Redundant ref chip.** Intro card shows `[A.5.15]` chip
   THEN the intro text begins "ISO 27001 A.5.15 (Access
   control) requires...". The ref appears twice.

2. **Cards don't enumerate fulfilled items.** Primary card
   shows `still_needed[]` (missing items) as chips but not
   the fulfilled counterparts. Tenant can't see "what's
   already in place" at a glance.

3. **Intro "1 of 4 items present" is vague.** The N-of-M
   summary duplicates card content AND doesn't tell the tenant
   WHICH items are which. Should be replaced by an actual
   enumerated checklist on the card.

## The fix: per-leaf checklist on primary card

Extend `RelatedCard` with a `leaves[]` array carrying each leaf's
state. Frontend renders the primary card (`relation=="primary"`)
as a check-list with fulfilled leaves marked `✓` and unfulfilled
marked `○`. Non-primary cards keep their current summary shape
(evidence_summary + still_needed chips) — over-decorating them
would clutter the drill-down surface.

### Schema addition

```python
class LeafState(BaseModel):
    leaf_id:       str        # e.g. "req:A.5.15:access_control_policy"
    title:         str        # e.g. "Access Control Policy"
    evidence_type: str        # e.g. "policy"
    satisfied:     bool       # True → ✓, False → ○
    n_have:        int        # progress detail (per-MUST count)
    n_total:       int

class RelatedCard(BaseModel):
    # ... existing fields ...
    leaves: list[LeafState] = []   # NEW — per-leaf checklist
```

### Data source

`build_per_must_advisory_data(pg, tid, ref, sid)` already returns
leaves in this shape — see `rag/posture/advisory.py:255+`. The
Ship 18'.b augment path calls it for `evidence_summary` +
`still_needed`; Ship 19'.b just serialises the `leaves[]` list too.

### Rendering (frontend)

- Only render `leaves[]` as a checklist when `card.relation ==
  "primary"`. Other cards keep the compact summary shape.
- Row format: icon (`✓` for satisfied, `○` for missing) +
  leaf title + optional evidence_type label (small, muted).
- No progress-percentage bar in this arc — the per-row check
  state IS the progress signal.
- Preserve existing `still_needed[]` chip row as a compact
  fallback surface (some queries may return leaves=[] where
  advisory data isn't computed — e.g. non-multi-leaf controls;
  in that case chips are still the right visual).

### Intro card changes

- **Drop the leading ref chip when redundant.** If
  `intro.text` starts with the ref (or with a phrase that
  includes the ref within its first ~40 chars), skip the chip.
- **Prompt update**: intro focuses on WHAT the control requires
  in one clean sentence. Drop the "1 of X items present"
  phrasing — that lives on the card as a checklist. The intro
  keeps its OFI-DRAFT / NC-DRAFT verdict marker for context but
  doesn't repeat the N-of-M count.

### LLM_OUTPUT_RULES update

New rule (or extension to rule 1):

```
When the primary_ref carries a per-MUST progress state (e.g.
"1 of 4 items present"), DO NOT restate that count in
`intro.text`. The related-card checklist owns the enumeration;
the intro's job is to frame WHAT the control requires + the
overall verdict tag ("OFI-DRAFT", "NC-DRAFT"). Example intro:
  "ISO 27001 A.5.15 (Access control) requires authorized
   access to information and assets. Currently OFI-DRAFT."
Not:
  "...OFI-DRAFT with only 1 of 4 required items present."
```

## Design decisions locked in 19'.a

1. **Primary card only** for the checklist — related-card
   drill-downs stay compact. User explicitly picked
   "per-leaf checklist on the primary card" over the deeper
   per-MUST option. Simpler UX; matches auditor mental model
   ("show me the leaf-level scorecard").

2. **`leaves[]` populated for ALL cards, rendered only for
   primary** — the frontend decides render granularity. Keeps
   backend uniform and lets future arcs surface leaves in
   other contexts (e.g. related cards' expanded state) without
   backend changes.

3. **Fallback for controls with no advisory data** — when
   `build_per_must_advisory_data` returns None (single-leaf
   controls or non-NC/OFI verdicts), `leaves` stays `[]`. UI
   falls back to the current still_needed chip row + evidence
   summary line. Backward-compat safe.

4. **APPEND-ONLY discipline preserved** — leaves[] is derived
   from posture, not LLM-authored. Same principle as Ship 18:
   structural metadata never has a hallucination surface.

5. **Chip dedupe on frontend, not backend** — the intro chip's
   redundancy is a render-layer concern. Backend continues to
   emit `intro.primary_ref` so callers that render prose (SDK,
   external API) still see it. Frontend just decides not to
   render it when the ref is already prominent in the text.

## Sub-arc plan

### 19'.b — Backend

- `rag/casefile/answer_schema.py` — add `LeafState` model;
  extend `RelatedCard` with `leaves: list[LeafState] = []`.
- `rag/casefile/answer_augment.py` — extend
  `_evidence_summary(...)` return signature (or add a new
  `_leaf_states(...)` helper) to return the leaves list;
  `build_related_cards()` populates `leaves` alongside
  `evidence_summary` + `still_needed`.
- `rag/casefile/answer_schema.py::LLM_OUTPUT_RULES` — new
  rule (or extension of rule 1) forbidding N-of-M restatement
  in intro.text.

### 19'.c — Frontend

- `static/arioncomply.html::renderStructuredAnswer`:
  - Dedupe intro ref chip: check if `intro.text` contains
    `intro.primary_ref` within first ~40 chars → skip chip.
  - Render `card.leaves[]` as a checklist when
    `card.relation === "primary"` and `leaves.length > 0`.
    Fall back to `still_needed[]` chips otherwise.
  - New CSS: `.sa-leaf-checklist`, `.sa-leaf-row`,
    `.sa-leaf-icon` (fulfilled = green ✓, missing = gray ○).

### 19'.d — Eval + retro

- Full eval regression check — baseline should stay 231/232 +
  1 WARN + 0 FAIL. No prompt change should affect assertions
  (rule extension is a subtractive constraint on intro).
- Manual visual verification of the three flagged behaviors.
- Arc retrospective.

## Ship 14'.a addendum alignment

| Check | Applied |
|---|---|
| Role split? | YES — leaves[] carries the framework-role-model context indirectly (each leaf inherits its control's role, which is already on RelatedCard). |
| Parallel CaseFile view? | YES — leaves[] data comes from `build_per_must_advisory_data` which shares the CaseFile's role model. |
| Deterministic routing? | N/A — presentation-layer arc. |
| Guidance-normative discipline? | YES — leaves[] carries evidence state per leaf; guidance-role controls (which typically have no evidence expectations) will render empty checklist correctly. |

## What Ship 19 does NOT do

- **Per-MUST expansion under leaves** — the deeper option was
  offered; user picked leaf-level only. Per-MUST detail stays
  in the Stage-1 detail panel (`humanizeSlug` chips) and the
  dashboard drill-in.
- **Change non-primary card rendering** — related cards for
  ISMS clauses / cross-framework bridges / demonstrated-by
  keep their current shape. Adding leaves[] to them would
  quadruple the card count on a typical remediation query.
- **Progress bars / percentage rings** — the check icons carry
  the state; progress-bar rendering adds visual weight without
  new information.
- **Backward-incompat SDK change** — `leaves` is
  Optional / default `[]`. Existing SDK consumers unaffected.

## Ship 19 progress

| Sub-arc | Status |
|---|---|
| **19'.a Design memo (this)** | **✓** |
| 19'.b Backend leaves[] + prompt tweak | next |
| 19'.c Frontend checklist + intro dedupe | pending |
| 19'.d Eval + arc retrospective | pending |

## Related

- [[ship-18-prime-arc-retrospective-2026-07-23]] — the arc whose
  UI Ship 19 polishes
- [[ship-18-prime-c-frontend-cards-prompt-rules-2026-07-23]] —
  the card render + LLM_OUTPUT_RULES that Ship 19 extends
- [[ship-15-prime-d-demonstrates-sdk-2026-07-22]] — precedent for
  extending card data without breaking existing consumers
- [[feedback-anchor-before-choices]] — user gave concrete
  UI feedback; arc opens with concrete plan not abstract options
