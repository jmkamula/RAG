---
name: ship-93-prime-b-upload-affordance-2026-08-22
description: Ship 93'.b — "Upload evidence to close this" button on Ship 93'.a completeness panel. Zero backend change.
metadata:
  type: project
---

# Ship 93'.b — upload affordance from partial completeness panel (2026-08-22)

See commit `1e8dd7f9` for the full change. Summary in MEMORY.md.

**Delivered:**
- Button on Ship 93'.a `completeness` panel: `[ Upload evidence to close this ]`
- `_startPartialResolutionUpload(controlRef, standardId, mustLabel, leafTitle)` in `static/arioncomply.html`:
  installs `window._uploadHintsOverride` (one-shot), switches to docs mode via `setMode('docs')`, pre-selects framework dropdown, inserts purple-bordered banner above drop zone
- `uploadFile()` extended to consume the override — appends `declared_standard_id` (+ `declared_evidence_type` if global dropdown supplied) then clears the override
- Cancel link on banner clears without upload

**Zero new endpoints, zero new backend columns.** Existing `declared_standard_id` on `/api/v1/documents/upload` accepts the hint; extraction runs normally; resulting present findings cover the partial via engine's leaf-level union.

**Reused by Ship 93'.f** for missing MUSTs on the per-control advisory panel — same button flow.

**Related:**
- [[ship-93-prime-a-partial-explainability]] — provides the completeness panel this button sits on
- [[ship-93-prime-f-missing-musts]] — reuses the flow for missing MUSTs
