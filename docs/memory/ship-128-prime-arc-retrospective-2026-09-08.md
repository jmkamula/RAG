---
name: ship-128-prime-arc-retrospective-2026-09-08
description: Ship 128' arc — workbook 0-findings root cause (missing client_documents insert) + counter aggregation across write paths
metadata:
  type: project
---

# Ship 128' — workbook 0-findings fix + counter aggregation

**Date:** 2026-09-08
**Sub-arcs:** 128'.a client_documents insert → 128'.b PoC cleanup → 128'.c counter aggregation + retro
**Trigger:** Operator reported live: "I have started intake and the workbook is finding 0" — ISO 27001 workbook uploaded to PoC, all pipeline stages completed with 0 findings in 2746ms (way too fast for real workbook processing).

## Diagnostic path (4 iterations)

The diagnostic went through 4 hypotheses before landing on the real bug. Worth documenting because each iteration corrected a wrong theory:

**v0 (initial hypothesis)**: "customer edited the file, changed column headers, workbook mappings don't match anymore." Ruled out when both workbook uploads on the PoC (jk + `(1)`) failed identically — not a customer-modified-file issue.

**v1 diagnostic** (wrong attribute names): Tried to inspect `PassProposal.sheet_name` + `PassProposal.column_hits`. Neither exists; the real fields are `SheetProposal.sheet` + `PassProposal.matched_columns`. Reported col_hits=0 for all 47 proposals — WRONG (getattr default returned 0). Would have led to "column matcher regression" as the second-wrong-hypothesis.

**v2 diagnostic** (correct attributes + persist_proposals dry-run): Confirmed `discover_workbook` returns 47 rich SheetProposals with real `matched_columns` + `satisfied` MUSTs. Then `persist_proposals` FK-violated on `workbook_intake_proposal_client_document_id_fkey` — client_document_id from my diagnostic was actually the upload_id, not a client_documents.id. FK violation was diagnostic-only, not the real bug. But surfaced the KEY insight: persist_proposals expects a client_documents row.

**v3 diagnostic** (count uploads vs client_documents): 3 uploads on PoC vs 1 client_documents row (the docx that went through LLM extract). Both workbook uploads' SHAs missing from client_documents. **Root cause confirmed**: no upload-time insert exists; `posture_writer._upsert_client_document` is the sole insert site + only runs when there are LLM-extract findings to write. Workbooks skip LLM extract by design → no client_documents row → workbook_discovery's SHA lookup returns 0 → whole block silently skips.

The comment in `doc_pipeline.py::Stage 4.6` says: *"the workbook still has a client_documents row from the upload"* — an assumption that was TRUE when the web-fill lane existed (probably created rows at upload time) but FALSE after that lane was retired.

## Delivery summary

### 128'.a — upload-time client_documents insert

`api_server.py::upload_document` now inserts a companion `client_documents` row in the same transaction as the `document_uploads` insert. Matches `posture_writer._upsert_client_document`'s shape (`document_status='uploaded'` + `is_active=TRUE` + `is_metadata_only=FALSE` + `retention_class='compliance'`) + adds `sha256`, `storage_path`, `file_size_bytes` so `workbook_discovery`'s checksum lookup succeeds first-time. `ON CONFLICT DO NOTHING` for concurrent-upload safety.

Verified on the operator's re-upload: `Stage 4.6: doc_id from sha256 lookup: c5756b19-...` + `workbook discovery wrote 47 proposals + 207 findings` + `Stage 4.7: workbook LLM arbiter mode=1 proposed=1140 written=449`. Total 656 findings landed across 29 controls, 228 distinct MUSTs. 19.5-min pipeline runtime — matches dev-VM historical baseline for the same file shape.

### 128'.b — PoC cleanup

`scripts/ops/ship-128-poc-update.sh` hard-deleted the 2 stuck workbook uploads from `document_uploads` + removed their storage files. Let the operator re-upload via the UI for a clean-slate verification (rather than admin-triggered reextract).

### 128'.c — counter aggregation across 3 write paths

Fixed the "656 landed but UI shows 0" reporting bug. Three sites edited in `rag/intake/doc_pipeline.py`:

- **`_arb_written` init moved to outer scope** (line ~858) alongside `_wbd_findings`. Previously local to Stage 4.7's try block; downstream counter aggregation would `UnboundLocalError` if that block didn't run.
- **`tracer.write("write", findings_written=...)` aggregates** `summary.get("written") + _wbd_findings + _arb_written`. Fixes the `v_intake_runs` view's `findings_written` that `/api/v1/documents/{id}/status` reads (drives UI display).
- **New refresh call to `update_upload_status`** after Stage 4.6/4.7 with the aggregate. Fixes `document_uploads.findings_count` for admin queries + dashboards. Skipped when no workbook writes occurred (avoids no-op round-trip).
- **Complete log line + PipelineResult** now show breakdown: `656 findings (extract=0 discovery=207 arbiter=449)`.

Backfill helper `scripts/dev/backfill_findings_count.sh` — one-shot fix for the already-completed upload (updates `document_uploads.findings_count` from an actual COUNT of `document_findings` joined via `client_documents.checksum_sha256`). Verified: ui_shows went from 0 → 656.

## Lessons codified

### Lesson 257 — Data pipelines that split write paths must aggregate at every counter site

Ship 128'.a fixed the DATA path. Ship 128'.c fixed the REPORTING. Both were needed — landing data without also fixing the counter meant the tenant saw "0 findings" in the UI despite 656 real findings existing in `document_findings`. The counter is downstream infrastructure, not a "nice to have" — if the tenant can't see the number, they don't know intake worked.

Every time a pipeline adds a new write path (Stage 4.6 workbook_discovery / Stage 4.7 LLM arbiter, in this case), audit every counter/summary site that surfaces "findings landed" — completion log, tracer stage rows, view definitions, dashboard columns, API response fields, UI labels — and aggregate at each. Otherwise counters silently under-report.

### Lesson 258 — "Assumption in a comment" is a load-bearing dependency

The comment in `doc_pipeline.py::Stage 4.6` said *"the workbook still has a client_documents row from the upload"* — a factual claim about upstream behavior with no test enforcing it. When the web-fill lane was retired (some earlier commit), the assumption became false + workbook uploads silently produced 0 findings. Nothing failed loud.

Rule: when code depends on a state established by a different module (row exists, config value present, service available), the dependency should be either (a) enforced by a test that fails when the dependency is broken, or (b) checked at runtime with a clear error message. A code comment is documentation, not enforcement.

### Lesson 259 — Silent-skip is the worst failure mode

The 19ms `workbook_discovery` stage-status=ok trace row was the smoking gun that took 4 diagnostic iterations to find. If the block had raised (or even just logged a WARNING when `_wbd_doc_id` is None on a workbook), the bug would have been visible in the api log within the first search. Instead, the guard `if _is_workbook and _wbd_doc_id` silently no-oped + the tracer still fired a "ok/0" stage row.

Fix pattern: any silent-skip guard that gates a load-bearing feature should log a WARNING (at least) when it skips. Preferably ERROR when the skip is unexpected. The 5 minutes it costs to grep the log later is dwarfed by the hours it costs to diagnose "the feature just doesn't do anything."

### Lesson 260 — Diagnostic scripts should use the actual dataclass fields

v1 diagnostic used `getattr(p, "sheet_name", "?")` + `getattr(p, "column_hits", [])` — neither attribute exists on `SheetProposal`/`PassProposal`. The `?` and `0` defaults SILENTLY covered the mismatch. When you use `getattr(obj, "field", default)` in a diagnostic, a wrong field name doesn't fail loud — it returns the default. For diagnostics specifically, use `obj.field` (raises AttributeError on typo) unless you actually want fallback behavior. Save `getattr` for cases where the field genuinely may or may not be present.

## Related arcs

- [[ship-91-prime-a-workbook-llm-arbiter]] — the Stage 4.7 arbiter that landed 449 of the 656 findings on this run
- [[ship-89-prime-b-cite-columns-workbook-hyperlinks]] — workbook_discovery hyperlinks_per_sheet plumbing
- Older: the retired web-fill lane commit (`2fee9d46 retire: web-fill (form-lane)`) — the arc that inadvertently removed the upload-time client_documents insert

## Deferred to Ship 129'+

- **workbook_arbiter Risk Register TimeoutError** — one sheet's LLM pass timed out at ~5 min into the arbiter run. Deterministic workbook_discovery still wrote its 207 findings; the arbiter path skipped that sheet. Fix options: larger per-request timeout, retry-with-backoff, streaming the LLM response, or splitting sheets that exceed a size threshold into chunks. Small arc; not urgent (data still landed via the deterministic path).
- **The reporting bug pattern applies to other write paths**. Stage 4.5 xfw proposer, Stage 4.6 workbook_discovery, Stage 4.7 arbiter — all now aggregate. If a future Stage 4.N adds another path, this arc's discipline says: also aggregate its count. A test that asserts `document_uploads.findings_count == COUNT(document_findings)` post-intake would catch future regressions.
- **`v_intake_runs` view should aggregate across `workbook_discovery` + `write` stages natively**, so the view returns the right number even if the write stage's `findings_written` isn't refreshed. Would make the view self-healing.
- **Ship 128'.a's dependency chain is fragile**. If the `client_documents` insert ever moves back to write-time (say a future refactor), workbook intake breaks again. A test that uploads a workbook + asserts `findings_count > 0` post-processing would lock it.

## PoC state after Ship 128'

- Ship 128'.a code deployed via `install.sh` + `sudo systemctl restart arioncomply-api`
- The stuck jk workbook now shows 656 findings in the UI (backfilled counter)
- Future workbook uploads will complete with an accurate counter at completion (no backfill needed)
- `.deployment_log.jsonl` will show Ship 128' when its next install.sh run appends
