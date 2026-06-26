-- schema_v48: extraction yield + pass-2 telemetry on intake_trace_log
--
-- Surfaces extraction quality the pipeline already computes but
-- silently drops at trace write time. Audit on 2026-06-26 found:
--
--   - Median yield (distinct MUSTs bound / catalog MUSTs in scope)
--     was 17% on the production Arion corpus; 66% of (doc,control)
--     pairs under 25% yield.
--   - The recall pass (`_run_pass2`) writes pass2_leaves_targeted +
--     pass2_findings to doc.extraction_metrics, but doc_pipeline's
--     trace-writer whitelist didn't allow them → silent loss.
--
-- New columns make the under-discovery signal visible per-upload:
--
--   - distinct_musts_bound    — count(DISTINCT checklist_item_id)
--                               in findings_kept
--   - leaf_musts_in_scope     — sum(len(must_contain)) across
--                               target_leaves (the catalog's denominator)
--   - yield_ratio_pct         — distinct_musts_bound / leaf_musts_in_scope
--                               (integer 0-100; NULL when denominator unknown)
--   - pass2_leaves_targeted   — partial-leaf count fed to pass-2
--   - pass2_findings          — additional findings from pass-2
--
-- The columns are nullable + additive — old extract rows stay NULL.

BEGIN;

ALTER TABLE intake_trace_log
    ADD COLUMN IF NOT EXISTS distinct_musts_bound  INTEGER,
    ADD COLUMN IF NOT EXISTS leaf_musts_in_scope   INTEGER,
    ADD COLUMN IF NOT EXISTS yield_ratio_pct       INTEGER,
    ADD COLUMN IF NOT EXISTS pass2_leaves_targeted INTEGER,
    ADD COLUMN IF NOT EXISTS pass2_findings        INTEGER;

ALTER TABLE intake_trace_log
    ADD CONSTRAINT intake_trace_log_yield_ratio_range
    CHECK (yield_ratio_pct IS NULL OR (yield_ratio_pct >= 0 AND yield_ratio_pct <= 100));

COMMENT ON COLUMN intake_trace_log.yield_ratio_pct IS
    'distinct_musts_bound / leaf_musts_in_scope * 100, integer 0-100. NULL when target_leaves was unknown (no doc_mappings match).';
COMMENT ON COLUMN intake_trace_log.leaf_musts_in_scope IS
    'Sum of catalog must_contain across target_leaves at extract time. The denominator for yield_ratio_pct.';
COMMENT ON COLUMN intake_trace_log.pass2_leaves_targeted IS
    'Count of partially-bound leaves fed to _run_pass2. 0 means pass-1 fully bound (or zero-bound) every targeted leaf.';

COMMIT;
