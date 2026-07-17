---
name: ship-3-prime-e-notification-producers-2026-07-17
description: "Ship 3'.e — stage2_proposal_ready + upload_failed notification producers wired end-to-end; baseline 207/208 held"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 3'.e (2026-07-17) — two additional notification producers.

## What shipped

- **`stage2_proposal_ready`** — fires inside
  `rag/posture_loader.py::_persist_engine_proposals` immediately after
  the `set_assertion(source='engine', status='pending', ...)` write.
  Only fires when `write_status == "pending"` (i.e. an actual queue
  entry, not an 'active' concurrence). Severity ladder:
  * `high` when engine proposes NC over a live `Comply` (auditor
    critical — a hidden failure surfacing)
  * `medium` otherwise
  Dedup: `related_entity_id = posture_row_id` — one active
  notification per (tenant, kind, posture_row) via the partial
  unique index.

- **`upload_failed`** — fires inside `rag/intake/doc_pipeline.py`
  exception handler after `_update_status(upload_id, 'failed', ...)`.
  Only fires on the real pipeline path (`not self.dry_run`). Opens
  a fresh connection because the caller's connection may be in an
  aborted transaction state after the exception. Severity `medium`.
  Dedup: `related_entity_id = upload_id` — one notification per
  upload attempt, since a retry gets a new upload_id.

## Not covered by this arc

The `FileNotFound` early-return branch in `doc_pipeline.py` line
234-250 does NOT fire `upload_failed`. Rationale: that path
predates the `_update_status` call — no `document_uploads` row
exists yet — so there's nothing to reference in
`related_entity_id`. That corner case is caller-provided path
error, not a pipeline failure.

## Wiring

- Schema: `db/schema_v71_ship3e_producer_kinds.sql` — adds
  `stage2_proposal_ready` + `upload_failed` to
  `tenant_notification_kind_check`.
- Producer 1 (stage2): inside `_persist_engine_proposals` gated on
  `if write_status == "pending":`, imported inline
  (`from rag.cascade.notify import notify as _notify`).
- Producer 2 (upload_failed): fresh `psycopg2.connect(self.db_url)`
  in the pipeline exception handler; commits on close;
  best-effort with `logger.warning` on failure.

## Tests

10/10 in `tests/test_notification_producers.py`:
- 5 nc_surfaced tests (from Ship 3'.c) — still pass
- 1 upload_processed guard test (from Ship 3'.c) — still passes
- 2 stage2_proposal_ready tests — wiring + `write_status == "pending"`
  gate
- 2 upload_failed tests — wiring + `not self.dry_run` gate

Source-reading style (verify wiring by regex on the source file)
rather than DB-integration to keep them fast and independent of
tenant seed state.

## Baseline

**207/208 PASS + 1 WARN + 0 FAIL** (`results/eval_20260717_1003_
ship3e.csv`). Same WARN #200 as Ship 3'.c-d (gap_analysis vs
posture_check type mismatch — pre-existing arc, unrelated to
producers). A.5.9 restore from earlier state-drift held; #48 PASS.

## Related

- [[ship-3-prime-a-sweep-scheduler-2026-07-17]] — sweep tick + timer
- [[ship-3-prime-b-freshness-expiry-producer-2026-07-17]] — freshness_expiry
- [[ship-3-prime-c-notification-producers-2026-07-17]] — nc_surfaced + upload_processed
- [[ship-3-prime-d-channel-config-ui-2026-07-17]] — channels UI + RLS policies
- [[feedback-posture-test-state-cleanup]] — A.5.9 restore discipline

## Producer inventory (post Ship 3'.e)

`tenant_notification_kind_check` now covers 10 kinds:

| Kind | Producer | Sweep-driven |
|---|---|---|
| implication_overdue | cascade engine | no |
| followup_overdue | cascade engine | no |
| threshold_crossed | cascade engine | no |
| cascade_blocked | cascade engine | no |
| auto_resolved | cascade engine | no |
| freshness_expiry | scheduler tick | yes (`freshness_expiry` work_type) |
| nc_surfaced | posture_writer._log_status_change | no |
| upload_processed | posture_writer.write_findings | no |
| **stage2_proposal_ready** | **posture_loader._persist_engine_proposals** | no (fires on load_posture) |
| **upload_failed** | **doc_pipeline exception handler** | no |

Two remaining candidates (not shipped in 3'.e):
- `cite_verification_overdue` — cite-mode freshness (needs sweep lane)
- `posture_flip_to_comply` — mirror of nc_surfaced (near-zero cost;
  worth bundling with any future posture_writer touch)
- `api_key_expiring` — operational hygiene (needs `expires_at`
  column + sweep lane)
