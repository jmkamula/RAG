---
name: template-native-formats-hybrid-2026-06-26
description: "SHIPPED 2026-06-26: hybrid templates (5.3 RACI / 6.1.3 SoA / Art.30 RoPA) now render the doc-level narrative MUSTs as a new 'Document Fields' sheet in the xlsx, alongside the existing Register + Guidance sheets. Single .xlsx covers both table + narrative — no zip, no second file. _arion_meta hidden sheet tracks doc_field_NN mapping too. Closes the Phase A native-format arc for all 20 v2 anchors."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What shipped

`rag/templates/xlsx_renderer.py` gained:

- `_extract_doc_level_must_ids(template_body, column_ids)` — set
  difference between `EDIT-ZONE-START item:X` markers and the
  TABLE-COLUMNS item_ids. Preserves first-seen order so the sheet
  reads top-to-bottom matching the markdown source.
- A new optional **Document Fields** sheet, present only when
  doc-level MUSTs exist (hybrid templates).
- Three-column layout per doc-level MUST: `Field | Standard text |
  Your content`. Tenant fills the third column in Excel with multi-
  line text (Alt+Enter).
- Header style mirrors the Register sheet (dark fill, bold white).
  Row height 80px on Your content cells — visual cue that paragraph-
  style content fits here.
- Hidden `_arion_meta` now also tracks `doc_field_count` plus
  `doc_field_00 .. doc_field_NN` keyed to the doc-level item_ids —
  Phase B round-trip extractor reads both columns and doc-fields
  uniformly.

Verified on all three hybrid templates:
- **5.3 RACI** → Document Fields has Communicated, Owner, A52
  Consistency (3 doc-level MUSTs beside 3 table cols)
- **6.1.3 SoA** → SoA Owner, SoA Version (2 doc-level beside 5
  table cols / 93-row body)
- **Art.30 RoPA** → Controller Name, Processor Records (2 doc-level
  beside 7 table cols)

## Non-obvious decisions

### Separate sheet, not inline rows on Register

Hybrid templates conceptually have two data models: the per-row
register (one row per asset / activity / signoff) AND the per-
document fields (owner, version — singletons). Mixing them on one
sheet would confuse Excel formula targeting, freeze-pane behavior,
and the future round-trip extractor's row-index semantics. A
separate sheet keeps the two models cleanly separated.

### Field / Standard text / Your content — three columns

Mirrors the docx pattern of header → standard-text quote → editable
zone. Excel's wrap_text=True + vertical=top on a tall cell makes
paragraph-style content workable inside a table cell. Tenants
familiar with Excel will recognize the pattern (3-column key/value
layouts are standard in compliance spreadsheets).

### Sheet ordering: Register → Guidance → Document Fields → _arion_meta

Register first because the table is where most of the work
happens. Guidance second because it's where the auditor-grade
language lives (referenced by header label). Document Fields last
because it's typically 2-3 fields — small surface, but important —
positioned where the tenant has already engaged with the workbook.
_arion_meta is hidden at the end for the round-trip extractor.

### Hidden _arion_meta now mixed columns + doc_fields

Both groups use the same `<key>_NN = <item_id>` pattern:

    column_00 = item:5.3:isms_conformance
    column_01 = item:5.3:performance_reporting
    column_02 = item:5.3:authorities_assigned
    doc_field_count = 3
    doc_field_00 = item:5.3:communicated
    doc_field_01 = item:5.3:owner
    doc_field_02 = item:5.3:a52_consistency

A future Phase B xlsx extractor walks both keyspaces uniformly —
column_NN binds to per-row data, doc_field_NN binds to per-document
data. The data models are different but the metadata pattern is
identical, making the upload extractor simpler.

## What's closed and what's open

Phase A native-format download arc is now complete:
- Pure tabular (A.5.9, 10.1, Art.32) → .xlsx (Register + Guidance)
- Pure narrative (A.5.1, A.5.15, 4.3, etc., 14 leaves) → .docx
- **Hybrid (5.3, 6.1.3, Art.30) → .xlsx with Document Fields sheet**

Phase B (round-trip uploads) still open:
- `.xlsx` upload extractor reading _arion_meta + Register + Document
  Fields sheets, binding each to MUSTs deterministically
- `.docx` upload extractor preserving Word-native markers
  (comments / bookmarks) across edit-save cycles

## Related

- [[template-native-formats-xlsx-2026-06-26]] — sibling work for
  pure tabular templates; the Document Fields extension here builds
  on the same _arion_meta foundation.
- [[template-native-formats-docx-2026-06-26]] — sibling work for
  pure narrative templates.
- [[templates-v2-anchors-complete-2026-06-25]] — the 20 v2 anchors
  this serves. With hybrid complete, every v2 anchor has a
  native-format download path.
- [[tabular-evidence-rows-2026-06-26]] — the row store that
  prefills the Register sheet on hybrid templates too.
