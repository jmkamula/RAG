-- schema_v56_clock_anchor.sql — S3h clock attribution
--
-- Adds clock_anchor column on triggered_implication so the source
-- of the deadline clock (verified_at vs structured-event occurred_at)
-- is traceable on every implication. Auditor + tenant can both see
-- whether the SLA was timed from awareness or from actual occurrence.

BEGIN;

ALTER TABLE triggered_implication
    ADD COLUMN IF NOT EXISTS clock_anchor TEXT NOT NULL DEFAULT 'verified_at';

-- Allowed values: 'verified_at' (default — clock starts at the cite
-- verification timestamp; current behaviour) | 'occurred_at' (tenant
-- supplied an event-occurred timestamp in structured_events.metadata).
ALTER TABLE triggered_implication
    DROP CONSTRAINT IF EXISTS triggered_implication_clock_anchor_chk;
ALTER TABLE triggered_implication
    ADD CONSTRAINT triggered_implication_clock_anchor_chk
        CHECK (clock_anchor IN ('verified_at', 'occurred_at'));

COMMENT ON COLUMN triggered_implication.clock_anchor IS
    'Which timestamp anchored the deadline clock for this implication: verified_at (default) or occurred_at (tenant-supplied event-time, for processor-discovered breach and similar scenarios where awareness postdates occurrence).';

COMMIT;
