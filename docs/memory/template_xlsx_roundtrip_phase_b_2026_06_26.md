---
name: template-xlsx-roundtrip-phase-b-2026-06-26
description: "SHIPPED 2026-06-26: Phase B xlsx round-trip. Reader detects _arion_meta hidden sheet → captures Register + Document Fields raw rows → extractor._extract_templated_xlsx binds per-column + per-doc-field findings ordinal-keyed by meta → writes tabular_evidence_rows + per-MUST document_findings (auto-approved, inference_source='templated'). doc_pipeline cross-checks tenant_id (mismatch → strip meta + log warning → fall through to generic lane). Verified on A.5.9 + 5.3 RACI. .docx round-trip still open."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What shipped

The download side (xlsx renderer + _arion_meta hidden sheet) was
foundation for this. The upload side now reads what the download
side wrote — closing the closed loop for tabular + hybrid templates.

### `rag/intake/readers.py`

New `_read_templated_xlsx_meta(wb)` — detects our `_arion_meta`
sheet at parse time:

- Parses key/value rows into a dict: `leaf_id`, `tenant_id`,
  ordered `column_NN → item_id` list, ordered `doc_field_NN → item_id`
  list (hybrid only).
- Reads Register sheet rows as sparse `{col_ix: cell_text}` payloads
  (non-empty cells only).
- Reads Document Fields sheet rows as `{label, standard_text,
  your_content}` triples.
- Returns the whole structure or None if the meta sheet is missing.

When present, `_read_xlsx` stashes the result on
`doc.extraction_metrics['templated_xlsx_meta']` for the extractor.

### `rag/intake/doc_pipeline.py`

Two changes:

- **Tenant cross-check**: if `meta.tenant_id != uploading tenant_id`,
  log warning + strip the meta. File falls through to the generic
  workbook lane (zero findings — safe default). Not a hard 400 —
  forgiving in case a teammate's file lands on the wrong account.
- **RLS GUC for writer connection**: `SET app.tenant_id = <tenant>`
  on the psycopg2 connection before `write_findings`. Was a latent
  bug the markdown templated lane never surfaced because no test
  had exercised multi-row tabular markdown + RLS together. xlsx
  round-trip is the first path that actually INSERTs into
  `tabular_evidence_rows` at scale.

### `rag/intake/extractor.py`

New `_extract_templated_xlsx(doc)` — runs in `extract()` BEFORE the
markdown templated path. Binds:

- **Per-column satisfaction** (mimicking markdown lane): for each
  column with ANY non-empty cell across all Register rows, emit one
  `DocumentFinding` (item_id = `column_NN` from meta, `inference_source
  = 'templated'`, `confidence = 'high'`, `finding = 'Comply'`).
  Auto-approved by existing posture_writer discipline.
- **Per-row content capture**: every non-empty row appended to
  `doc.tabular_rows` keyed by row_index. posture_writer persists into
  `tabular_evidence_rows` (schema_v47) with proper RLS.
- **Document Fields** (hybrid templates): one finding per filled
  "Your content" cell, ordinal-bound to `doc_field_NN`. Skipped if
  the cell is empty.
- Telemetry: leaf_id, column count + bound count, register row
  count, doc_field count + bound count.

## Non-obvious decisions

### Bind by ordinal, not by header text

The Register sheet's column headers are humanized slugs ("Asset
Records", "Owner Per Asset"). A tenant could rename them in Excel
without affecting our binding — column position in the canonical
`_arion_meta.column_NN` ordering is the source of truth, NOT the
visible header. Same for Document Fields rows: parallel to
`doc_field_NN` by ordinal.

### Tenant cross-check: warn + fall through, not 400

A hard reject would surprise tenants on edge cases (teammate
forwards a file, file restored from a backup, etc.). Falling
through to the generic workbook lane = zero findings + a clear
warning in the trace — observable, not surprising.

### Auto-approve, same trust as markdown templated

The xlsx was rendered for THIS tenant, downloaded BY this tenant,
edited BY this tenant, uploaded BY this tenant. No inference, no
LLM, no extraction uncertainty. Same auto-approve discipline as
the markdown templated lane (posture_writer:370). Already visible
in `/api/v1/stage1/auto-approved` panel because the filter is
`inference_source IN ('templated','form')`.

### RLS GUC on writer connection was a latent bug

`tabular_evidence_rows` (schema_v47) and `tenant_profile`
(schema_v49) enforce strict RLS. The pipeline's psycopg2 connection
in `doc_pipeline.run` didn't have `app.tenant_id` set, so the
INSERT into `tabular_evidence_rows` was blocked. The markdown
templated lane sometimes writes there too (if the .md upload has
multi-row tabular content) but apparently no real upload had
exercised that path before xlsx round-trip. Surfaced + fixed in
this session.

## Failure modes (designed but not yet stress-tested)

| Failure | Behaviour |
|---|---|
| `_arion_meta` deleted by tenant | Fall through to generic workbook lane. **Open**: filename-fallback identification (e.g. `A_5_9_asset_inventory.xlsx` → `req:A.5.9:asset_inventory`) not yet implemented. |
| Tenant edits `_arion_meta.leaf_id` to a wrong leaf | Their own data, their own scope (RLS) — they'd bind to the wrong leaf. Detectable, not a security risk. |
| Different tenant uploads the file | Cross-check rejects — meta stripped, falls through. Verified path. |
| Tenant reordered Register columns | Ordinal binding survives (we read by index, not header). |
| Tenant added extra columns | Ignored — `_arion_meta.column_count` is authoritative width. Beyond it = unread cells. |
| Tenant deleted a column | Ordinal mapping shifts and corrupts. **Open**: validate `column_count` matches Register width on read; reject if mismatch. |
| Tenant pastes whole rows from another sheet | Treated as data rows — included in tabular_evidence_rows. If they pasted MUST satisfaction patterns by accident, they get auto-approved. Low risk (their own scope) but worth a future "preview before commit" gate. |

## End-to-end verified

**Pure tabular** — A.5.9 Asset Inventory:
- Downloaded fresh xlsx, filled 4 asset rows in Excel, uploaded
- 6 per-MUST findings (all 6 columns had data, all bound)
- 4 `tabular_evidence_rows` with complete `column_values` JSONB
- xfw_bridge proposed Art.30:categories_data binding as a bonus

**Hybrid** — 5.3 RACI:
- Filled 1 Register row (3 cols) + 1 Document Fields cell
  ("Communicated" row, Your content column)
- 4 findings: 3 table-bound + 1 doc-field-bound
- All `inference_source='templated'`, `review_status='approved'`

Eval pending; chat path untouched so expect baseline 198/199 or
better.

## What's still open

- **.docx round-trip**: not implemented. Markers in our generated
  .docx are visible plain text (Consolas, small). Round-trip would
  need to either (a) preserve them through Word save/reload — risky
  because tenants might delete them, or (b) switch to Word-native
  comments/bookmarks during the .docx render (more code, safer).
- **Filename-fallback identification**: when `_arion_meta` is
  missing but the filename matches our convention
  (`<control_ref>_<slug>.xlsx`), we could still recover. Not
  implemented; not urgent (the meta is hidden and unlikely to be
  deleted).
- **Column-count validation**: detect tenant column-delete by
  comparing Register width to `_arion_meta.column_count`; reject
  with explanatory message rather than silently misbind.
- **Preview-before-commit UX**: show the tenant what bindings the
  upload produced + give them a chance to roll back before findings
  enter posture.

## Related

- [[template-native-formats-xlsx-2026-06-26]] — the download side
  that produces `_arion_meta`. This entry is the upload side.
- [[template-native-formats-hybrid-2026-06-26]] — Document Fields
  sheet, the other half of hybrid templates this lane now extracts.
- [[tabular-evidence-rows-2026-06-26]] — schema_v47, the row store
  this lane populates.
- [[templated-lane-discipline-2026-06-25]] — auto-approve trust
  model inherited here for xlsx uploads.
- [[form-lane-parity-2026-06-26]] — sibling tenant-authored lane;
  auto-approved panel already surfaces xlsx-round-trip findings
  via the `inference_source IN ('templated','form')` filter.
