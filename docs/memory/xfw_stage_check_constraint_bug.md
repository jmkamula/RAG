---
name: xfw-stage-check-constraint-bug
description: "RESOLVED 2026-05-21 via schema_v26 + 2026-05-22 follow-ups: tracer swallow raised to WARNING and test_intake_table_extraction.py asserts intake_trace_log.xfw_targets non-NULL on a fresh upload."
metadata: 
  node_type: memory
  type: project
  originSessionId: 9eeea5c7-cafb-4a85-9b32-8f0ceef552bf
---

**RESOLVED 2026-05-21** — `db/schema_v26_xfw_stage_constraint.sql` widened the
CHECK to include `'xfw'`. Verified in-conversation: empty `xfw_targets` for
upload `5a8ec7f5-...` was caused by the swallowed CheckViolation; constraint
now reads `read|enrich|extract|write|xfw|complete|failed`.

**Follow-ups closed 2026-05-22:**
- Tracer's swallowed exception now logs at `logger.warning` in
  `rag/intake/doc_pipeline.py:134` so the next CHECK mismatch surfaces in
  `api.log` instead of hiding at debug.
- `tests/test_intake_table_extraction.py` adds Assertion 4: after the
  synthetic .docx upload runs, an `intake_trace_log` row with `stage='xfw'`
  and `xfw_targets IS NOT NULL` must exist for the upload_id. Empty array
  is acceptable — the bug we guard against is structural (CHECK constraint
  blocks the INSERT, row missing entirely). Confirmed PASS with
  `xfw_targets=['GDPR:2016/679']` on 2026-05-22.

---

Historical context below.



`schema_v17_xfw_trace.sql` added `proposals_written`/`proposals_skipped`/`xfw_targets` columns and rewrote `v_intake_runs` to aggregate `WHERE stage = 'xfw'`, but **forgot to update the stage CHECK constraint**:

```sql
-- current constraint
CHECK (stage = ANY (ARRAY['read','enrich','extract','write','complete','failed']))
-- 'xfw' is missing → every tracer.write("xfw", ...) raises CheckViolation
```

The tracer (`rag/intake/doc_pipeline.py:133-134`) swallows the exception at `logger.debug`, so the failure is invisible. Net result: `v_intake_runs.proposals_written` stays NULL for every upload, and the UI's new xfw chip never goes green even when Stage 4.5 succeeds.

**Why this wasn't caught earlier:** No upload had produced findings between commit 178b826 and 2026-05-16, so Stage 4.5's "skip when findings=0" guard short-circuited every time. The integration test added for [[wip-document-text-commit]] was the first run that actually triggered Stage 4.5 with non-zero findings — Neo4j wrote 1 GDPR proposal but the trace insert silently failed.

**How to apply / fix recipe:**
1. New migration `schema_v19_xfw_stage_constraint.sql`:
   ```sql
   ALTER TABLE intake_trace_log DROP CONSTRAINT intake_trace_log_stage_check;
   ALTER TABLE intake_trace_log ADD CONSTRAINT intake_trace_log_stage_check
     CHECK (stage = ANY (ARRAY['read','enrich','extract','write','xfw','complete','failed']));
   ```
2. Optional: raise the tracer's swallowed exception from `logger.debug` to `logger.warning` so the next constraint mismatch is loud.
3. Eval coverage: re-upload a fixture, query `/api/v1/documents/{id}/status`, assert `proposals_written` is an integer (not null) when findings>0.

Keep this as its own commit — clean diff, clean revert.
