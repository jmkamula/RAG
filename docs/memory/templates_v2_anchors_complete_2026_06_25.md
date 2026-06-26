---
name: templates-v2-anchors-complete-2026-06-25
description: "SHIPPED 2026-06-25 (af0d4eb): closes the v2-anchor templating arc — 6 hybrid/tabular v2 anchors (A.5.9, 10.1, Art.32 pure; 5.3, 6.1.3, Art.30 hybrid) + 132 standard-text blockquotes across the 14 narrative v2 anchors. Extractor now processes table_zones AND edit_zones in one pass (additive, was if/elif). Eval 199/199 — first clean sweep above the 198/199 target."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What shipped

1. **6 tabular/hybrid v2 anchors** — written in this session
   - Pure tabular (TABLE-COLUMNS metadata + table EDIT-ZONE only):
     `req:A.5.9:asset_inventory`, `req:10.1:improvement_action_register`,
     `req:Art.32:risk_appropriate_measures_register`
   - Hybrid (table zone + per-MUST item zones for doc-level MUSTs):
     `req:5.3:isms_roles_authorities` (3 cols + 3 narrative),
     `req:6.1.3:statement_of_applicability` (5 cols + 2 narrative),
     `req:Art.30:records_of_processing` (7 cols + 2 narrative)

2. **132 standard-text blockquotes** inserted across 14 narrative v2
   anchors via `/tmp/add_standard_text.py`. Pattern:

       <<MUST item:X>>

       > _Standard text:_ <ChecklistItem.text from catalog>

       <existing consultant prose + ✓ Good / ✗ Avoid>

   All 14 bumped to `template_version: 3` to mark the addition.

3. **Extractor: hybrid in one pass** — `rag/intake/extractor.py
   _extract_templated` was if-table-elif-zones; now collects findings
   from BOTH paths additively. Hybrid templates need it: per-row
   findings come from the table zone, doc-level findings come from
   the item zones, both must surface for the engine to see all MUSTs.

## Non-obvious decisions

### Standard-text alignment is mechanical, not editorial

The consultant prose in v2 templates was hand-authored (~hours per
anchor). Adding the standard-text blockquote was script-driven —
keyed off `ChecklistItem.text` in
`enrichment/documents/document_requirements.py`. **Distinguish**:
prose = judgment, slow; standard-text = derivable, fast. Future
template work should reuse this division — never hand-type
catalog wording into the markdown when a script can extract it.

The catalog key gotcha: ChecklistItem.id includes the `item:`
prefix (e.g. `item:A.5.18:identity_link`) but the template marker
regex captures only the part after `<<MUST item:` (so just
`A.5.18:identity_link`). Insert `item:` when looking up.

### Per-MUST edit zones can coexist with table edit zones

The renderer wraps every `<<MUST item:X>>` with a per-MUST edit
zone — including the column-guidance MUSTs in hybrid templates.
That looks like duplication (a column-guidance MUST has both a
TABLE-COLUMNS mapping AND a per-MUST item zone), but it's
harmless: the per-MUST zone for those contains only scaffolding
(heading + ✓/✗ examples + `<<TEXT>>` placeholder), which the
extractor skips via `_is_pure_scaffolding`. So:

- Findings come from TABLE row data → bound to MUST via column index
- The same MUST's per-item zone is skipped as scaffolding
- No double-counting

Verified on 5.3 RACI smoke: render has 6 per-MUST item zones but
extractor's `templated_edit_zones_total: 3` — the 3 column-guidance
zones were correctly identified as scaffolding-only and discarded.

### Eval 199/199 was the upper-tail run

Baseline target is 198/199 (case #16 is LLM-stochastic on A.5.18
ref surfacing in `doc_inventory` answers, ~85-95% pass rate). Today
we got the lucky tail. Don't lock 199/199 as the new target — the
distribution didn't shift, this was variance. See
[[feedback-eval-state-drift]].

## How to apply (next batch of templates)

1. Hand-author the markdown (preamble + per-MUST sections + ✓/✗).
2. Save with `template_version: 2`.
3. Run `/tmp/add_standard_text.py` (or equivalent) to insert
   `> _Standard text:_ ...` blockquotes — script bumps to v3.
4. Reload via `enrichment/templates/load_to_postgres.py`.
5. Run hybrid smoke (`/tmp/smoke_hybrid.py`) if the new template
   has tabular or hybrid layout.

## Related

- [[templates-v1-foundation-2026-06-24]] — the foundation: filesystem
  → loader → Postgres templates, marker convention.
- [[templated-lane-discipline-2026-06-25]] — auto-approve at write +
  edit-zone markers; the lane on which this v2-anchor work runs.
- [[templates-hybrid-2026-06-15]] — earlier hybrid (form + doc)
  surface; different "hybrid" word — that was form-vs-document
  dual-surface; today's hybrid is table-vs-narrative within ONE
  document.
- [[feedback-eval-state-drift]] — why 199/199 isn't the new target.
