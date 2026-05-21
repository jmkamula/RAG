-- =============================================================================
-- schema_v26_xfw_stage_constraint.sql
--
-- Adds 'xfw' to intake_trace_log.stage CHECK so Stage-4.5 trace rows can
-- actually be inserted.
--
-- v17 added xfw_targets / proposals_written / proposals_skipped columns and
-- rewrote v_intake_runs to aggregate WHERE stage='xfw', but forgot to widen
-- the stage CHECK constraint. Every tracer.write("xfw", ...) since then has
-- raised CheckViolation, which doc_pipeline swallows at logger.debug. Net
-- effect: v_intake_runs.{proposals_written,proposals_skipped,xfw_targets}
-- stay NULL for every upload and the UI's Stage-4.5 chip is permanently
-- empty even when xfw_proposer succeeds.
--
-- Idempotent.
-- =============================================================================

ALTER TABLE intake_trace_log DROP CONSTRAINT IF EXISTS intake_trace_log_stage_check;
ALTER TABLE intake_trace_log ADD CONSTRAINT intake_trace_log_stage_check
  CHECK (stage = ANY (ARRAY['read','enrich','extract','write','xfw','complete','failed']));
