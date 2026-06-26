---
name: template-native-formats-xlsx-2026-06-26
description: "SHIPPED 2026-06-26: Phase A xlsx download for tabular templates. GET /api/v1/templates/{leaf_id}/download?format=xlsx produces a 3-sheet workbook (Register / Guidance / hidden _arion_meta). Frontend shows '📊 .xlsx' button alongside '📄 .md' only for tabular evidence types — JS mirrors scripts/generate_template_scaffolds._is_tabular_evidence. Compliance officers can now author in Excel for the 6 tabular v2 anchors instead of struggling with markdown tables."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What shipped

`rag/templates/xlsx_renderer.py` + `?format=xlsx` extension on
`GET /api/v1/templates/{leaf_id}/download` + frontend format picker
on the evidence-class breakdown panel.

Workbook structure per tabular template:

- **Register** sheet — humanized-slug headers (e.g. "Asset Records",
  "Owner Per Asset"), frozen header row, prefilled rows from
  `tabular_evidence_rows`, blank rows for new entries.
- **Guidance** sheet — header label → full auditor-grade MUST text
  from the catalog. Lets tenants click a header and look up the
  exact ISO/27002 wording without clobbering the Register's column
  widths.
- **_arion_meta** (HIDDEN) — leaf_id + column ordinal → item_id
  mapping. Foundation for a future Phase B round-trip extractor; not
  yet read on upload.

Verified shapes:
- A.5.9 Asset Inventory: 6-column Register + 6-row Guidance, opens
  cleanly in Excel
- 5.3 RACI (hybrid): 3 table columns rendered; doc-level narrative
  MUSTs (`communicated`, `owner`, `a52_consistency`) intentionally
  excluded — tenant gets those via the existing per-MUST form or .md

## Non-obvious decisions

### Humanized slugs as headers, not full MUST text

First cut used MUST text directly. Produced ugly mixed-length headers
(some 12 chars, some 200 chars) that broke Excel's column width
heuristics. Switched to `_humanize_column` (`item:A.5.9:owner_per_asset`
→ "Owner Per Asset"). Compact, consistent, readable. Full MUST text
moves to the Guidance sheet keyed by the same header label so the
auditor-grade language remains one click away.

### Hidden _arion_meta sheet now, even though no reader exists yet

Foundation for Phase B (round-trip upload of edited xlsx). The
metadata sheet survives all Excel save/load operations. When a
future xlsx extractor exists, it reads `column_00`...`column_NN` to
recover the MUST id for each column even if the tenant reordered or
renamed headers in Excel. Ship the metadata now — it's free, and
reverse-engineering it from a future tenant-edited workbook would
be much harder.

### JS classifier mirrors Python — keep in sync

`scripts/generate_template_scaffolds._is_tabular_evidence` is the
canonical predicate (suffixes + exact-set). `static/arioncomply.html`
duplicates the list as `isTabularEvidenceType` so the frontend can
hide the .xlsx button on narrative leaves rather than always show it
and rely on the backend 400. If the Python list grows, the JS list
needs the same update. Annotated in both source files.

### Why narrative templates can't be .xlsx

A narrative MUST is one block of prose per item, not a column. An
Excel column would force one-paragraph-per-cell which fights Excel's
display model. Frontend doesn't show the .xlsx button on narrative
leaves; backend returns 400 with `"Use format=md instead"`. Phase A
.docx (next) is the native fit for narrative.

## Roadmap

Phase A (this session):
- ✓ xlsx download for tabular templates
- Next: .docx download for narrative templates (pandoc → docx)

Phase B (future, deferred):
- Round-trip xlsx upload — extractor that reads `_arion_meta` to
  bind columns to MUSTs even after reorder/rename
- Round-trip docx upload — marker preservation strategy
  (Word-native comments/bookmarks vs HTML comments)

## Related

- [[templates-v2-anchors-complete-2026-06-25]] — the 6 tabular
  templates this serves; the standard-text blockquotes from that
  arc become the Guidance sheet rows.
- [[tabular-evidence-rows-2026-06-26]] — the row store that
  prefills the Register sheet (multi-row content captured on
  templated uploads).
- [[evidence-class-breakdown-backend-2026-06-26]] — the dashboard
  panel where the .xlsx button appears.
- [[templated-lane-discipline-2026-06-25]] — auto-approve trust for
  the upload side when round-trip ships.
