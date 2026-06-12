-- schema_v38: extend intake_trace_log.stage CHECK constraint to allow
-- the new 'workbook_discovery' value.
--
-- doc_pipeline.py Stage 4.6 (commit b2e880c, 2026-06-12) auto-runs
-- workbook discovery on xlsx/xlsm uploads and writes a telemetry row
-- with stage='workbook_discovery'. The original CHECK constraint
-- (created with the table) only allowed:
--   {read, enrich, extract, write, xfw, complete, failed}
-- so the new row silently CheckViolations on every xlsx upload. The
-- pipeline catches the error as non-fatal but the telemetry is lost.
--
-- Fix: drop the old constraint, add a new one that includes
-- 'workbook_discovery'.

BEGIN;

ALTER TABLE intake_trace_log
    DROP CONSTRAINT IF EXISTS intake_trace_log_stage_check;

ALTER TABLE intake_trace_log
    ADD CONSTRAINT intake_trace_log_stage_check
    CHECK (stage = ANY (ARRAY[
        'read'::text,
        'enrich'::text,
        'extract'::text,
        'write'::text,
        'xfw'::text,
        'workbook_discovery'::text,
        'complete'::text,
        'failed'::text
    ]));

COMMIT;
