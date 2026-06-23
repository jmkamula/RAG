---
name: multipath-data-cleanup-2026-06-23
description: "SHIPPED 2026-06-23 after Part A/B: data-side cleanup of pre-multipath residue. 113 unbound + 580 stale-batch workbook findings + 102 doc-side unbound — all soft-deleted with rejection_reason audit trail. State: 0 active unbound extracted across tenant; only by-design xfw_bridge unbound remains."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What and why

Part A/B retired the multipath xlsx writer in CODE. The DATA-side
residue from months of dual-writer + re-extract churn was still in
`document_findings` after Part B shipped. User asked "have we
cleaned up the previous multipath architecture?" — the honest answer
was "code yes, data no". This entry records the data-side cleanup.

## Three soft-deletes shipped

All marked `is_active=FALSE`, `review_status='rejected'`, with a
distinct `rejection_reason` per cohort. No hard deletes — full audit
trail preserved.

| Cohort | Rows | rejection_reason |
|---|---|---|
| Workbook unbound (`extracted`, NULL `checklist_item_id`) | 113 | `superseded_by_workbook_part_a_2026_06_23` |
| Workbook older extract batches (kept latest per `document_id`) | 580 | `superseded_by_latest_extract_batch_2026_06_23` |
| Doc-side unbound (`extracted`, non-workbook docs, two passes) | 102 | `superseded_by_direction_c_2026_06_23` |

Two passes on the doc-side: first pass used `mime_type NOT LIKE
'%sheet%'` which missed 2 rows with NULL mime_type; second pass used
`COALESCE(cd.mime_type, '') NOT LIKE '%sheet%'`.

## False start to remember

First dedup attempt partitioned by `(document_id, checklist_item_id)`
and kept the latest extracted_at per pair — collapsed **per-row
evidence** to per-MUST (e.g., 50 asset-register rows producing
findings for `item:A.5.9:owner` got reduced to 1). Workbook bound
fell 535 → 29. Reverted via `WHERE rejection_reason LIKE
'superseded_by_latest_reextract_2026_06_23%'`.

The correct dedup partitions by `document_id` and keeps the latest
extract **batch** (latest `extracted_at` overall, not per MUST). That
preserves all per-row evidence within the canonical batch.

**Rule for future workbook re-extract cleanups**: dedupe by
`document_id` (whole batch), never by `(document_id,
checklist_item_id)`.

## Why these were safe to soft-delete

The 113 + 102 unbound rows had `checklist_item_id=NULL`, so the
engine has been ignoring them since Phase-1 retirement
(2026-06-13). No posture impact from removing them — just removing
inert audit clutter that was being conflated with actual evidence
in DB-level counts.

The 580 stale workbook batches were superseded by re-extract output
but the writer didn't supersede the prior batch. Pre-Part-A
`_extract_structured` + `workbook_persistence` re-extracts created
new rows without retiring old ones. Cleaning these makes
`document_findings` reflect the canonical latest extract.

## Final state on Arion (post-cleanup)

```
inference_source | unbound_active | bound_active
extracted        |              0 |           22
form             |              0 |            0
leaf_scan        |              0 |           51
workbook         |              0 |          204    (197 active workbook
                                                     + 7 historical approved)
xfw_bridge       |            112 |            0    (by-design)
```

Only `xfw_bridge` carries active unbound rows, and that's intentional
(bridges don't bind to a single MUST — they cite a cross-framework
link, not evidence for a MUST).

## What was NOT cleaned

- **`posture_assertions` 359 active `backfill:schema_v29` rows**:
  Phase-1c memory captured the fix — engine reader excludes
  `backfill:%` set_by, so these rows are inert. Could clean for DB
  hygiene; no functional impact. Deferred as low priority.

- **Doc re-extraction**: the 100+2 soft-deleted doc-side unbound rows
  came from pre-Direction-C extracts. Direction C (2026-06-08) ships
  per-MUST + grounding, but those docs haven't been re-extracted yet.
  Soft-deleting the unbound row puts them in the same state as a
  never-extracted doc. Re-extracting them via Direction-C-era code
  would produce bound findings; that's a separate workstream, not
  cleanup.

## Future hardening

The root cause that allowed 537 stale workbook findings to accumulate
is: **`workbook_persistence` doesn't supersede prior extract batches
on re-extract**. Same likely applies to doc-side extractor. Each
re-extract just inserts; nothing flips the prior batch to
`is_active=FALSE`.

Could be solved by either:
- Writer-side: on extract success, supersede prior active findings
  for the same `document_id + inference_source` before writing new
- Schema-side: unique constraint on `(document_id,
  inference_source, extract_batch_id)` with a CHECK that only one
  batch is `is_active=TRUE`

Not shipping today; logged here for the next intake-side iteration.

## Related

- [[workbook-intake-part-a-2026-06-23]] — retired `_extract_structured`
  for xlsx/xlsm (the code-side counterpart of this cleanup)
- [[workbook-intake-part-b-2026-06-23]] — 4 new YAMLs + meta-skip
  extension (closed sheet coverage)
- [[posture-assertions-phase-1c]] — explains why
  `backfill:schema_v29` rows are inert
- [[doc-curation-engine-v1]] — Direction C (doc-side per-MUST
  binding), the doc analog of Part A
