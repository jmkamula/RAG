---
name: ship-93-prime-f-missing-musts
description: Ship 93'.f — surface missing MUSTs (no evidence anywhere) on per-control advisory panel; reuses Ship 93'.b upload flow.
metadata:
  type: project
---

# Ship 93'.f — missing MUSTs on per-control drill-in (2026-08-24)

See commit `4d636aa1` for the full change. Summary in MEMORY.md.

**Delivered:**
- New `partial_explainer.explain_missing(must_id, leaf_id)`: scans all workbook_mappings YAMLs for any pass that binds the MUST → picks required (preferred) or optional fallback → derives `evidence_type` + column fingerprint variants for prose
- Two branches: `workbook_or_doc` (mapping binds — suggests column add + doc upload) / `doc_only` (no mapping — doc upload only)
- `expand` map in `_humanize_must_label` extended: `disc→discovery`, `recon→reconciliation`
- `/api/v1/dashboard/control/{ref}/advisory` enriches each unsatisfied `must_item` with `completeness` payload
- Advisory panel UI: "Still needed" list rewritten as per-MUST cards with inline "▸ How to add this" toggle (Workbook or doc / Doc only badges) + Ship 93'.b upload button

**Dogfood on ISO Arion A.5.9:**
- 18 missing MUSTs, 18 with completeness prose (100%)
- 10 `doc_only` (no catalog mapping binds them)
- 8 `workbook_or_doc` (mapping binds; suggests specific columns to add)

**Yellow-item picture now complete** across three surfaces (partial workbook / partial arbiter / missing MUST) — same primitives, same button flow.

**Related:**
- [[ship-93-prime-a-partial-explainability]] — workbook partial branches; Ship 93'.f mirrors the pattern for missing
- [[ship-93-prime-b-upload-affordance-2026-08-22]] — button reused
