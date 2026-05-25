-- =============================================================================
-- schema_v28_posture_log_revert_kind.sql
--
-- Adds 'revert' to posture_status_log.change_kind CHECK so the Path A cleanup
-- can record reverts of Stage-1-driven posture flips without losing audit
-- traceability.
--
-- The active plan ([[posture-engine-alignment-plan-2026-05-22]]) calls for
-- replaying status_before from posture_status_log to undo the 39 Stage-1
-- flips. Each replay produces a new log row whose change_kind needs to
-- distinguish it from the original 'extraction' rows being reverted —
-- otherwise the chain becomes a circular history (extraction → extraction
-- with reversed values) and downstream consumers (e.g. v_intake_runs) lose
-- the ability to filter cleanups out of "real" extraction activity.
--
-- 'assessor' would compress the audit signal; 'engine' is wrong (no engine
-- involvement); 'acknowledgement' is the Stage-1 gap-ack path.
--
-- Idempotent.
-- =============================================================================

ALTER TABLE posture_status_log DROP CONSTRAINT IF EXISTS posture_status_log_change_kind_check;
ALTER TABLE posture_status_log ADD CONSTRAINT posture_status_log_change_kind_check
  CHECK (change_kind = ANY (ARRAY[
    'extraction'::text,
    'engine'::text,
    'assessor'::text,
    'acknowledgement'::text,
    'revert'::text
  ]));
