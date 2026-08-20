---
name: ship-89-prime-a-curator-fix
description: Ship 89'.a — fixed Ship 86 curator's silent schema bug; corrected YAML shape + corroboration split; 0 → 13 findings from LLM-curated mappings
metadata:
  type: project
---

# Ship 89'.a — Ship 86 curator schema + corroboration fix (2026-08-20)

## Discovery

Audit of `db/workbook_mappings/*.yaml` (240 files) — driven by user
observation that Ship 88's `partial` semantics collided with a
pre-existing YAML discipline — surfaced two facts:

1. **Discipline**: 232 of 240 YAMLs declare `coverage: partial` on
   optional columns; 616 required columns bind anchors (`coverage:full`
   implicit), 815 optional columns bind corroboration (`coverage:partial`
   explicit). Auditor lens: `required` = row IS this artefact,
   `optional` = row is auditor-grade complete.
2. **Silent Ship 86 bug**: All 4 files authored by
   `scripts/ship86a_workbook_curator.py` used a non-canonical
   schema — `column_bindings:` list with `binds_to_must_id` +
   `required: true/false` fields. `workbook_discovery._scan_columns`
   only reads `required_columns`, `optional_columns`, `column_groups`.
   The 4 ship86 mappings fingerprint-matched sheets but produced
   **zero MUST findings**. Ship 86'.b retro's "18 new MUST-bindings
   populated" claim was based on assumption, not measurement.

## Fixes shipped

**Curator schema corrected.** Pass 2 prompt now emits:
```json
{
  "required_columns": [{"column_hint": [...], "must_id": "..."}],
  "optional_columns": [{"column_hint": [...], "must_id": "..."}]
}
```
YAML emission uses the canonical `required_columns:` + `optional_columns:`
blocks with `fingerprint:`, `binds_to:`, and `coverage: partial` (on
optional).

**Corroboration discipline added to Pass 2 prompt.** ~40 lines
explaining anchor vs corroboration with concrete examples:
- DSAR register: `received_date` + `requester` = required (row IS a DSAR);
  `scope`, `response_date`, `timing_flag`, `outcome` = optional
- Asset register: `asset_id` + `asset_name` = required (row IS an asset);
  `location`, `criticality`, `retention_class` = optional
- Risk register: `risk_id` + `description` = required; `treatment_plan`,
  `residual_score`, `review_date` = optional

Prompt rule: "If unsure, default to optional_columns — partial credit is
auditor-safe."

**Wider `header_row_hints: [1..8]`** — Business Partners Assessment has
a 6-row banner (Purpose / Scope / Frequency / Requirements) before the
real header at row 7. Old default `[1, 2, 3]` never reached it.

**`not_applicable` skip** at authoring time — TOC / Formulas /
Instructions / Mapping sheets no longer produce empty-target YAMLs
that would fail `validate_workbook_mappings.py` and abort the
workbook_persistence batch. Codifies Ship 86'.b Lesson 84 in the
curator itself.

**False-positive fingerprint removed** from
`ship86_competence_records.yaml` — dropped `[training, records]` which
matched the Ship 88 A.6.3 Training & Awareness Record sheet
(attendance-based, different column shape).

## Measurement (ISO workbook re-extraction)

| Mapping | Before | After | Present | Partial |
|---|---|---|---|---|
| Business Partners Assessment | 0 | **5** | 1 | 4 |
| Competence Records | 0 | **4** | 3 | 1 |
| Risk Comms Matrix | 0 | **4** | 1 | 3 |
| **Total from LLM-curated** | **0** | **13** | 5 | 8 |

Total workbook_persistence findings: 197 → 205 (+8 net). The corroboration
split fires correctly per sheet: `present` on anchor columns, `partial` on
corroboration columns. This is the first time the Ship 86 arc's YAMLs
have contributed real MUST evidence.

## Codified lessons

**Lesson 93: Curator output must match downstream schema exactly.**
LLM-authored YAMLs need to match the reader's actual keys, not the
LLM's approximation of the shape. Ship 86'.a authored `column_bindings`
because "that's what compliance bindings look like"; the downstream
reader wanted `required_columns` + `optional_columns`. **Every curator
output should be validated end-to-end at author time — parse the YAML
through the actual reader, not just YAML-valid.**

**Lesson 94: Ship-time measurement must count findings, not proposals.**
Ship 86'.b measured "48 proposals + 197 findings" and reported the
curator win as "4 new sheets recognized, 18 new MUST-bindings
populated." The proposals were real (sheets fingerprint-matched) but
the MUST bindings emitted zero findings. **When adding a new
discovery source, measure the terminal artefact (findings landed in
document_findings) — proposals-created is a leading indicator, not
outcome.**

**Lesson 95: Anti-pattern surface is a curator quality signal.**
The audit surfaced 8 files where `required_columns` bindings had
`coverage: partial` — a semantically confused mix. Not a bug in
discovery (which handles it), but a curator drift signal worth
surfacing in a future curator sweep. These are candidates for
reclassification: partial-required either means "required column
with softer signal" (belongs in optional) or "hard column with
weak fingerprint" (belongs in required, coverage:full).

## Files changed

- `scripts/ship86a_workbook_curator.py` — Pass 2 prompt rewrite,
  YAML emission rewrite, not_applicable skip, wider header_row_hints
- `db/workbook_mappings/ship86_business_partners_assessment.yaml` — regenerated
- `db/workbook_mappings/ship86_competence_records.yaml` — regenerated + fingerprint tightened
- `db/workbook_mappings/ship86_risk_comms_matrix.yaml` — regenerated
- `db/workbook_mappings/ship86_this_doc_chng_control.yaml` — regenerated

## Ship 89'.b opens next

Add declarative `cite_columns:` field to workbook_mappings YAML.
Cells in cite_columns emit `external_evidence_source` rows (Ship 3'
cite-mode) instead of the Ship 88 `workbook_hyperlink_followup`
sidecar. Revert Ship 88's schema_v102 + `has_hyperlink` corroborating
signal + `workbook_link_resolver` sweep — the cite-mode integration
is the correct home for hyperlink-as-evidence.

## Related

See [[ship-88-prime-arc-retrospective]] (draft, NOT committed — will
be superseded by 89'.b retro).
See [[curation-phase-b-retrospective]] for the YAML catalog history.
