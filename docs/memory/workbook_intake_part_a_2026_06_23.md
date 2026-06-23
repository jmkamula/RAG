---
name: workbook-intake-part-a-2026-06-23
description: "SHIPPED 2026-06-23 (9b16b93, schema_v44): Part A of the workbook-intake architectural cleanup. Retired _extract_structured for xlsx/xlsm — workbook_persistence (Stage 4.6) becomes the canonical path with deterministic per-MUST YAML binding. Sheets without YAML mapping now produce 0 findings (vs 93 unbound noise). Meta-sheet blacklist + sheet classifier + telemetry land the architectural symmetry with the doc pattern. Part B (5 missing YAMLs, ~8-10hr curation) deferred."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What and why

Before today, workbook intake had **two parallel writers** producing
overlapping findings:

1. **`_extract_structured`** (Stage 3) — read XLSX rows, created ONE
   finding per row, control-ref-level only, **no `checklist_item_id`**
2. **`workbook_persistence`** (Stage 4.6) — used
   `db/workbook_mappings/*.yaml` for per-MUST deterministic binding

The 2026-06-23 workbook re-upload made the cost visible: 169 bound
findings (path 2, useful) + 93 unbound findings (path 1, Stage-1
noise) + bare-Annex-A ambiguity (path 1, mis-routed rows) +
"Not per ISMS Scope" status mis-classification (path 1, lost N/A
intent).

The architectural fix discussed: **adopt the doc pattern** —
`doc_mappings` narrows scope → per-MUST binding → done. For workbook
the YAML mapping IS the per-MUST binding. There's no need for the
LLM-style fallback. Retire path 1; path 2 is the canonical writer.

## What changed

### `rag/intake/readers.py`

- `_META_SHEET_PATTERNS` blacklist: TOC, Documentation, Mapping,
  Instructions, Formulas, Key/Legend, Version History, Readme, Cover
- `_is_meta_sheet()` checks lowercased substring
- `_read_xlsx` skips meta sheets entirely (no section, no row processing)
- `doc.extraction_metrics["workbook_skipped_meta_sheets"]` records names

### `rag/intake/extractor.py`

- `_classify_workbook_sheets()` — sheet-name jaccard against
  `workbook_mappings` YAML `sheet_name_fingerprints`; threshold = 0.5.
  Returns `(n_mapped, n_unmapped, unmapped_names)`. Telemetry-grade.
- `extract()` STRUCTURED branch for xlsx/xlsm:
  - Run classifier
  - Log unmapped sheets (curation gap surface)
  - Return `[]` (Stage 4.6 will write findings)
- CSV files unchanged (still go through `_extract_structured` —
  workbook_persistence doesn't handle them)

### `rag/intake/doc_pipeline.py`

- Stage 4.6 doc_id fallback: when `extract()` returns `[]`,
  `summary` lacks `doc_id`. Look up the client_documents row by
  sha256 + tenant_id. Without this fallback, workbook_persistence
  would skip the run when extract was retired.
- Tracer allowed-list extended with schema_v44 columns
- Extract trace.write forwards classification metrics

### `db/schema_v44_workbook_sheet_telemetry.sql`

```sql
ALTER TABLE intake_trace_log
    ADD COLUMN workbook_sheets_total        INTEGER,
    ADD COLUMN workbook_sheets_mapped       INTEGER,
    ADD COLUMN workbook_sheets_unmapped     INTEGER,
    ADD COLUMN workbook_unmapped_sheets     TEXT,
    ADD COLUMN workbook_skipped_meta_sheets TEXT;
```

## Verified end-to-end on Arion

```
Re-extract of ISO 27001 workbook Arion Networks.xlsm:

Stage 1: read → 38 sheets total, 5 meta sheets skipped (TOC,
                Documentation, Mapping, Instructions and Definitions,
                Formulas), 33 content sections built
Stage 3: extract → 0 findings (structured extraction retired for xlsm)
         5 unmapped sheets logged + persisted:
           - This Doc Chng Control
           - ISMS Schedule
           - BIA Bus. Impact Ass.
           - Spec Int Engagement log
           - Quarterly Security Review
Stage 4: write → 0 findings (extract returned [])
Stage 4.6: doc_id sha256 lookup → 64f10b73-d6e1-4b54-9197-4640b8220eef
           workbook_persistence wrote 38 proposals + 169 findings

Before: 169 bound + 93 unbound = 262 noisy Stage-1
After:  169 bound + 0 unbound  = 169 actionable Stage-1
```

Eval 197/199 (within baseline band; #5 + #16 LLM-stochastic).

## What Part A explicitly does NOT solve

- **5 unmapped sheets need YAMLs** — that's Part B, ~1-2hr per YAML
  authoring × 5 = ~8-10hr. Until shipped, tenants with the same
  workbook shape will get a gap signal but zero findings on those
  5 sheets.
- **CSV workbook uploads** — still use `_extract_structured`
  (workbook_persistence doesn't support multi-sheet-less CSVs).
  CSV is a small surface; deferred.
- **The headline-recompute API response confusion** — separate
  follow-up; the approve endpoint still returns legacy
  recommendations that aren't the actual engine effect.

## Architectural significance

This change establishes **architectural symmetry** between doc and
workbook intake:

| | Doc intake | Workbook intake (post Part A) |
|---|---|---|
| Mapping registry | `db/doc_mappings/*.yaml` | `db/workbook_mappings/*.yaml` |
| Mapping artefact | per-leaf target controls + LLM candidate list | per-MUST sheet→column→checklist_item_id |
| Binding mechanism | LLM (Direction C pass-2 for recall) | Deterministic (YAML row filters) |
| Gap signal | doc_mappings_match_count = 0 (legacy fallback) | workbook_sheets_unmapped > 0 (telemetry) |
| Action when gap | curate doc_mappings YAML | curate workbook_mappings YAML |

Both paths now agree: **the YAML is the contract**. Anything without
a YAML is either filtered (meta sheets) or surfaced as gap signal.
No more "we did some best-effort thing in the background."

## Part B scope (deferred)

Author YAMLs for the 5 unmapped sheets identified today:

| Sheet | Likely target leaves | Effort |
|---|---|---|
| This Doc Chng Control | ISMS 7.5 (Documented information) + A.5.34 PII | ~1.5 hr |
| ISMS Schedule | ISMS 9.x + 10.x (Performance evaluation + Improvement schedule) | ~1.5 hr |
| BIA Bus. Impact Ass. | A.5.30 + ISMS 6.1.2 | ~2 hr |
| Spec Int Engagement log | A.5.6 (Contact with special interest groups) | ~1 hr |
| Risk Comms Matrix (may turn out to be mapped — verify) | ISMS 7.4 | ~1 hr |
| Quarterly Security Review | A.5.36 / ISMS 9.3 | ~1.5 hr |

Total ~8-10 hr focused curation. Each YAML is shared infrastructure
— benefits every future tenant with similar workbook shapes.

## Related

- [[workbook-importer-bare-annex-a-2026-06-23]] — the OPEN follow-up
  that Part A closes (this entry can be referenced from there as
  "closed by Part A")
- [[per-must-recall-direction-c-2026-06-23]] — the doc-side pattern
  that Part A adopts
- [[strategic-arc-2026-06-23]] — arc capstone (written mid-session;
  doesn't yet include Part A — could be amended or left as
  point-in-time)
- [[intake-pipeline-architecture]] — diagram needs a refresh:
  workbook intake now has a single canonical writer, not two
