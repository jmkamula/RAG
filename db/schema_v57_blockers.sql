-- schema_v57_blockers.sql — S3i BLOCKS_WHEN suppression
--
-- Extends cascade_suppression_log so it can record BLOCKS_WHEN-driven
-- suppressions of triggered_implication writes in addition to the
-- EMITS_EVENT-driven suppressions S3d captured.
--
-- BLOCKS_WHEN semantics: a control's implication is suppressed when
-- another control's blocker condition (legal hold, active incident,
-- etc.) evaluates true against the structured-event metadata.

BEGIN;

ALTER TABLE cascade_suppression_log
    ADD COLUMN IF NOT EXISTS suppression_kind TEXT NOT NULL DEFAULT 'emits_event';
ALTER TABLE cascade_suppression_log
    ADD COLUMN IF NOT EXISTS target_requirement_id TEXT;

-- target_event_type is required by the original (S3d) schema but
-- isn't meaningful for blocks_when (the suppression isn't about a
-- downstream event). Loosen the NOT NULL to allow blocks_when rows
-- without inventing a fake event type.
ALTER TABLE cascade_suppression_log
    ALTER COLUMN target_event_type DROP NOT NULL;

ALTER TABLE cascade_suppression_log
    DROP CONSTRAINT IF EXISTS cascade_suppression_log_kind_chk;
ALTER TABLE cascade_suppression_log
    ADD CONSTRAINT cascade_suppression_log_kind_chk
        CHECK (suppression_kind IN ('emits_event', 'blocks_when'));

ALTER TABLE cascade_suppression_log
    DROP CONSTRAINT IF EXISTS cascade_suppression_log_consistency_chk;
ALTER TABLE cascade_suppression_log
    ADD CONSTRAINT cascade_suppression_log_consistency_chk
        CHECK (
            (suppression_kind = 'emits_event'
              AND target_event_type IS NOT NULL)
            OR
            (suppression_kind = 'blocks_when'
              AND target_requirement_id IS NOT NULL)
        );

CREATE INDEX IF NOT EXISTS idx_cascade_suppression_target_req
    ON cascade_suppression_log(tenant_id, target_requirement_id, fired_at DESC)
    WHERE suppression_kind = 'blocks_when';

COMMENT ON COLUMN cascade_suppression_log.suppression_kind IS
    'Which suppression mode fired this row: emits_event (S3d EMITS_EVENT applies_when=false) or blocks_when (S3i implication suppressed because a BLOCKS_WHEN blocker matched the cascade metadata).';
COMMENT ON COLUMN cascade_suppression_log.target_requirement_id IS
    'For blocks_when: the control whose implication was suppressed. For emits_event: NULL.';

COMMIT;
