---
name: doc-pipeline-stage-4-6-2026-06-12
description: "SHIPPED 2026-06-12 (b2e880c): doc_pipeline.py Stage 4.6 auto-runs workbook discovery on xlsx/xlsm uploads. Closes the gap where workbook discovery only fired via CLI. Both paths now run on every xlsx upload — doc extractor (LLM narrative) + workbook discovery (structured per-row evidence). Verified: 1 upload → 10 findings across 4 stages."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Closes the architectural gap noted in
[[policy-acknowledgment-form-yaml-2026-06-12]]: workbook
discovery was CLI-only. Today's Microsoft Forms upload made
the gap concrete — the doc-extractor path produced 5 findings
(narrative LLM extraction), and only after manually invoking
`scripts/discover_workbook.py` did 7 more structured findings
land. From a tenant's POV, the second batch never would have
appeared.

Stage 4.6 in `doc_pipeline.py` now fires automatically after
Stage 4.5 (xfw proposer) when:
  - `file_name.lower().endswith((".xlsx", ".xlsm"))`
  - `summary["doc_id"]` is present (Stage 4 successfully linked
    the upload to a `client_documents` row)
  - Not in dry-run mode

The stage:
  1. Loads the workbook via `openpyxl.load_workbook(...,
     keep_vba=True, data_only=True, read_only=True)`
  2. Reads all sheets into `{sheet_name: rows}` dict
  3. Calls `discover_workbook(rows)`
  4. If any proposals, opens a fresh psycopg2 connection,
     sets app.tenant_id, calls `persist_proposals`
  5. Logs `Stage 4.6: workbook discovery wrote N proposals
     + M findings`
  6. Tracer writes telemetry record (proposals_written,
     findings_written, status, error_detail)

## Why best-effort

Like Stage 4.5, this stage runs AFTER Stage 4 has committed.
A workbook-discovery failure must not undo the LLM findings
that already landed. The stage wraps the whole block in
try/except — any exception is logged with the type name +
message and the upload still succeeds.

## Independent of doc extractor

The two paths produce complementary, not duplicate, evidence:
  - doc extractor (LLM): narrative findings tied to control_ref
    only (no checklist_item_id). Captures things the structured
    pass can't — e.g. policy language, scope statements, free-
    form contextual hints.
  - workbook discovery: per-MUST findings bound to specific
    `checklist_item_id`. Engine consumes these for leaf
    satisfaction counting.

Today's verification on the Acknowledgment upload landed both:
  - 1 narrative finding on A.5.1
  - 2 xfw proposals (GDPR Art.5 / Art.24)
  - 7 structured findings: 3 on A.6.3 + 4 on 7.4 with
    checklist_item_id

Total: 10 findings from one upload event, no manual CLI step.

## What still doesn't auto-fire

  - `.csv` uploads — same shape as workbook but the structured
    extractor path (`_extract_structured` in extractor.py)
    handles those at Stage 3, not Stage 4.6. Different code
    path. Could unify in a future refactor.
  - `.xls` (legacy Excel) — openpyxl doesn't support it.
    Would need xlrd or pandas. Skip for now.
  - Updates to workbook content within the same upload SHA —
    SHA dedup at upload edge skips entirely. Would need
    `--force-rediscover` admin endpoint.

## Operational note for cleanup runs

`workbook_intake_proposal` has restrictive permissions —
`arioncomply_app` can INSERT + UPDATE but not DELETE. Cleanup
of stale proposals must use `UPDATE ... SET status='superseded',
superseded_at=NOW()` rather than DELETE. Found this when
cleaning up before re-upload verification.

## Related

- [[policy-acknowledgment-form-yaml-2026-06-12]] — surfaced
  this gap; resolved here.
- [[sample-row-anchor-confirmation-2026-06-12]] — anchor
  system fires automatically inside discover_workbook, so
  Stage 4.6 inherits anchor protection without extra wiring.
- [[workbook-yaml-vocab-refresh-2026-06-11]] — the broader
  workbook-intake arc.
- [[intake-quality-telemetry]] — Stage 4.6 telemetry follows
  the same shape (status / error_detail / counts).
