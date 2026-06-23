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
  CLEANED 2026-06-23 (commit pending). Flipped to
  `status='superseded'` with `superseded_at=now()` — pure hygiene
  pass; engine reader (`get_latest_engine_assertion` with
  `engine_authored_only=True`) already excluded these rows.
  Verified only one caller exists (`posture_loader.py:383`) and it
  uses the engine-authored-only path. Post-state: all backfill
  rows now 'superseded' (433 total); 308 legit active PAs intact
  (40 engine + 234 trigger:document + 34 trigger:engine). Eval not
  re-run — functional behavior unchanged.

- **Doc re-extraction**: the 100+2 soft-deleted doc-side unbound rows
  came from pre-Direction-C extracts. Direction C (2026-06-08) ships
  per-MUST + grounding, but those docs haven't been re-extracted yet.
  Soft-deleting the unbound row puts them in the same state as a
  never-extracted doc. Re-extracting them via Direction-C-era code
  would produce bound findings; that's a separate workstream, not
  cleanup.

## Future hardening — RESOLVED 2026-06-23 (0e510cf)

The root cause that allowed 537 stale workbook findings to accumulate
was: **writers INSERT new findings on re-extract without retiring
prior batches**. Shipped writer-side supersede in both intake paths:

- `workbook_persistence.persist_proposals`: in same transaction as
  new inserts, supersede prior pending `workbook_intake_proposal`
  rows + prior active `inference_source='workbook'` findings with
  `rejection_reason='superseded_by_extract_run:<run_uuid>'`. Gated
  on `proposals` non-empty.

- `posture_writer._write_document_findings`: before per-row INSERT
  loop, supersede prior active `inference_source='extracted'`
  findings with
  `rejection_reason='superseded_by_extract_batch:<timestamp>'`.
  Gated on `findings` non-empty.

Both run in the same transaction as the new writes; rollback
restores prior state if the inserts fail. Smoke test against live
Arion workbook verified: 197 prior → 1 new + 197 superseded with
correct rejection_reason. Schema gotcha caught during smoke test:
`workbook_intake_proposal` has CHECK
`(status='superseded') = (superseded_at IS NOT NULL)`, so the
UPDATE must set `superseded_at = now()`.

`leaf_driven_scan.persist` intentionally NOT changed —
back-bind-from-finding semantics + within-call dedup are
sufficient.

Effect: future workbook + doc re-extracts will not accumulate
stale findings; this entry's manual cleanup of 795 rows was a
one-off catch-up.

## Related

- [[workbook-intake-part-a-2026-06-23]] — retired `_extract_structured`
  for xlsx/xlsm (the code-side counterpart of this cleanup)
- [[workbook-intake-part-b-2026-06-23]] — 4 new YAMLs + meta-skip
  extension (closed sheet coverage)
- [[posture-assertions-phase-1c]] — explains why
  `backfill:schema_v29` rows are inert
- [[doc-curation-engine-v1]] — Direction C (doc-side per-MUST
  binding), the doc analog of Part A
