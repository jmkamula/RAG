---
name: ship-93-prime-a-partial-explainability
description: Ship 93'.a — partial findings on the Stage-1 queue now show "what's missing + how to make it right" — derived from source YAML, tenant sees actionable next step
metadata:
  type: project
---

# Ship 93'.a — partial evidence explainability (2026-08-21)

## Framing

User's frame: "what's missing and how to make it right."

Ship 92'.b/d closed the cite lifecycle with attestation. Ship 93'.a
closes the other half of yellow-items-on-the-ledger: partial
findings. Every workbook partial on Arion (85 items) now has:

  1. **What's missing** — traced back to the source YAML pass; we
     know which anchor MUST wasn't populated or which optional
     column was corroboration-only by design.
  2. **How to make it right** — actionable prose the tenant reads
     directly. No system jargon.

Server-side derivation from catalog YAML (Ship 87 dejargonize
discipline — server ships human strings, client renders).

## The two branches

For each partial finding, the explainer traces back to the source
`workbook_intake_proposal.mapping_id` → `pass_yaml`. Then applies
one of two rules:

**Branch A — `anchor_missing`**
If the MUST is bound in the pass's `required_columns` but the
tenant's workbook doesn't have that column populated (only the
optional/corroboration column matched):
```
"Your workbook has the corroborating value in the DUE DATE column
 but not the anchor column that this evidence type expects.
 To move Action ID to present, do one of:
   (1) Add a column named like Ref Id, Action Id, Id to your
       ISMS Schedule register and populate it per row.
   (2) Or upload a supporting document that names Action ID
       explicitly."
```

**Branch B — `corroboration_only`**
If the MUST is bound ONLY in `optional_columns` (coverage:partial
by design — Ship 89'.a discipline):
```
"This is corroboration-only evidence by design. Your workbook shows
 DUE DATE, which supports but doesn't fully evidence Target date.
 To move it to present:
   (1) Upload a document that explicitly demonstrates Target date."
```

For each branch, additional cite-column paths are surfaced when
the MUST is also in `cite_columns`.

## Delivered

**`rag/posture/partial_explainer.py`** (~230 LOC):
- `_load_mapping_cache()` — module-level YAML cache
- `_humanize_must_label(must_id)` — reuses Ship 92'.d discipline
- `_humanize_fingerprint(fp)` — for column-name hints
- `_find_pass_for_finding(mapping_id, must_id)` — trace to source
- `_find_required_binding` / `_find_cite_binding` — YAML inspection
- `explain_partial(...)` — public entry, returns
  `{must_label, branch, why_partial, how_to_close, primary_prose}`
- `explain_finding(pg, tenant, finding_id)` — convenience for API

**`rag/posture/stage1_review_chat.py`** — `list_pending_for_control`:
- Query extended to JOIN `workbook_intake_proposal` for
  `mapping_id` + sheet name
- Per-row: if workbook partial, attach `completeness` field via
  `explain_partial`
- Best-effort — never blocks Stage-1 detail on explainer failure

**`static/arioncomply.html`** — Stage-1 detail renderer:
- Partial findings with `completeness` payload get an inline
  "▸ How to make this present" toggle
- Branch badge — orange `Anchor missing` or grey `Corroboration only`
- Prose renders as-is (server pre-humanized; contains `<strong>`
  and `<code>` tags — trusted)

## Dogfood on ISO Arion

Coverage:
- **85 partial workbook findings, 100% traceable to source YAML**
  (all have `workbook_proposal_id` + `mapping_id`)
- **100% in Stage-1 queue** — all get explainability rendered on
  the existing HITL surface
- Every partial finding on the queue now has "▸ How to make this
  present" affordance

Sample outputs on control 10.1 (ISMS Schedule):

| MUST | Branch | Prose |
|---|---|---|
| `reg_trigger_type` (matched `PRIORITY`) | corroboration_only | Add hyperlink to the internal document in the `Reference` column, OR upload a doc that explicitly demonstrates Trigger type. |
| `reg_dimension` (matched `TASK`) | corroboration_only | Upload a document that explicitly demonstrates Dimension. |
| `rev_signal_capture` (matched `Related Risk`) | corroboration_only | Upload a document that explicitly demonstrates Review signal capture. |
| `reg_status` (matched `Status`) | corroboration_only | Upload a document that explicitly demonstrates Status. |

All 8 partial findings on 10.1 correctly classified as
`corroboration_only` — the ISMS Schedule mapping YAML puts these
MUSTs in `optional_columns` only. Auditor semantics validated.

## Codified lessons

**Lesson 111: The catalog is the explainability source.** Ship 89'.a
codified the required/optional discipline in YAML. Ship 93'.a reads
that same YAML at runtime to explain partials. The catalog does
double duty: extraction contract + tenant guidance. No parallel
schema needed. **When you have a schema that encodes intent, the
same schema should explain outcomes.**

**Lesson 112: Ship 92'.d humanization primitives compose.** The
`_humanize_must_label` slug→title logic works across cite
attestation (Ship 92'.d) and partial explainability (Ship 93'.a)
because MUST ids are ID-shape everywhere. Same helper handles both.
**Humanization is compositional — a good primitive earns its keep
across surfaces.**

**Lesson 113: "How to make it right" beats "what went wrong."**
The old partial status told tenants a fact ("this is partial").
Ship 93'.a tells them a next action ("add column X" / "upload a
doc"). Different surface, same DB row. The primary UX shift is
from **passive state** to **active next step**.

## Files changed

- `rag/posture/partial_explainer.py` (new, ~230 LOC)
- `rag/posture/stage1_review_chat.py` — `list_pending_for_control`
  attaches `completeness` on workbook partials
- `static/arioncomply.html` — Stage-1 detail renders inline
  "How to make this present" panel
- `docs/memory/ship_93_prime_a_partial_explainability.md` (this)

## Deferred to future arcs

- **LLM arbiter partial explainability** — Ship 91's arbiter
  emits partials with LLM-supplied evidence_text. Explanation shape
  is different (LLM's judgment, not YAML). Own arc.
- **Missing MUSTs enumeration** — MUSTs a leaf declares that AREN'T
  bound anywhere in workbook (silent gaps). New advisory surface;
  probably belongs on the per-control drill-in, not Stage-1.
- **Column-name inference** — when the tenant's workbook has a
  differently-named column that COULD anchor a MUST (e.g. they used
  "Task ID" when we look for "Ref ID"), we could suggest a fuzzy
  match. Meaningful UX lift; needs fuzzy scorer + tenant confirm.

## Related

- [[ship-89-prime-a-curator-fix]] — required/optional discipline
  encoded in YAML — Ship 93'.a reads that same schema for
  explainability
- [[ship-92-prime-d-cite-attestation]] — Ship 92'.d humanization
  primitives reused in the explainer
- [[dejargonize-ux-pass-2026-07-01]] — server-ships-human-strings
  discipline
