---
name: workbook-importer-bare-annex-a-2026-06-23
description: "OPEN follow-up 2026-06-23: workbook re-upload (ebf724de) wrote 168 findings using bare numbering (5.x/6.x/7.x/8.x) for Annex A controls. normalize_control_ref correctly refuses to auto-prefix (ISMS/Annex A 2-dot collision). Workbook source data uses tenant-friendly bare convention for both ISMS clauses AND Annex A. One-off data fix shipped (db/data_fix_2026_06_23_workbook_bare_annex_a.sql); permanent fix is context-aware normalization using sheet name (e.g. Annex A sheet → auto-A-prefix; ISMS Controls sheet → bare keeps)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What happened

2026-06-23: Arion re-uploaded an updated ISO 27001 workbook. The
new workbook source data used bare numbering for Annex A controls
(e.g. `5.18` instead of `A.5.18`), while the previous workbook
(2026-05-21) used A-prefix.

The structured-extraction path (`rag/intake/extractor.py:_extract_structured`)
forwards `control_ref` from workbook rows verbatim. The normalizer
(`rag/framework_refs.py:normalize_control_ref`) deliberately preserves
bare 2-dot refs since the 2026-06-09 fix
([[normalizer-annex-a-isms-collision]]) because ISMS clauses 5-8 and
Annex A 5-8 collide at the 2-dot level.

Result:
- 168 findings landed on bare-prefix control_refs
- 79 NEW posture_controls rows created as duplicates of existing A.x rows
- Stage-1 queue grew by 262 pending findings (94 ISMS legit + 168 Annex A misrouted)

## Disambiguation rule (per evidence inspection)

Examining workbook evidence text confirmed the convention:
- **Unambiguous bands → A-prefix**:
  - `5.[4-37]` → `A.5.x` (ISMS clause 5 only has 5.1-5.3 Leadership)
  - `6.[4-8]` → `A.6.x` (ISMS clause 6 only has 6.1-6.3 + 6.1.x sub-clauses)
  - `7.[6-14]` → `A.7.x` (ISMS clause 7 only has 7.1-7.5 Support)
  - `8.[4-34]` → `A.8.x` (ISMS clause 8 only has 8.1-8.3 Operation)

- **Ambiguous bands → leave bare** (evidence: workbook sheet names like
  Competence Records, ISMS Objectives, Change Mgmt Log confirmed ISMS context):
  - `5.[1-3]`, `6.[1-3]`, `6.1.x`, `7.[1-5]`, `8.[1-3]`, `9.x`, `10.x`, `4.x` → ISMS

## Data fix shipped today

`db/data_fix_2026_06_23_workbook_bare_annex_a.sql`:
- UPDATE 262 findings (157 prefixed where unambiguous, 105 left bare ISMS)
- Retire 79 duplicate posture_controls rows (where A.x equivalent already active)

Per-tenant data fix, idempotent.

## Permanent fix (open)

The workbook importer should normalize *context-aware* — looking at
the sheet name where the row came from:

| Sheet name pattern | Normalization rule |
|---|---|
| "Annex A" / "Controls" / contains "A.5"-"A.8" | bare 5-8.x → A-prefix |
| "ISMS Clauses" / "Clauses 4-10" / contains "ISMS" | bare → leave alone |
| `Competence Records`, `ISMS Objectives`, `Change Mgmt Log` etc. | infer ISMS (these are ISMS-clause-specific sheets) |
| Ambiguous (no signal) | leave bare; flag via crosscheck-style telemetry |

Effort: ~1-2 hours in `rag/intake/readers.py:_read_xlsx` + per-row
context propagation through `_extract_structured`.

Until shipped, the workbook re-upload story has the same trap.

## Related

- [[normalizer-annex-a-isms-collision]] — the 2026-06-09 fix that
  deliberately stops auto-prefixing
- [[posture-controls-ref-format]] — convention: ISMS bare, Annex A
  A-prefixed
- [[workbook-intake-corpus-v1-complete]] — workbook intake corpus
- docs/data_fix_2026_06_23_workbook_bare_annex_a.sql — the one-off
  data fix shipped for this upload
