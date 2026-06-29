-- schema_v51_structured_events.sql — S2c cascade-event capture
--
-- Adds the `structured_events` JSONB column to
-- external_evidence_verification_log so the cite-verify path can
-- capture structured event emissions alongside the free-text
-- changes_detected attestation. The cascade engine (S3) will read
-- this column and walk the Event→TRIGGERS_OBLIGATION /
-- EMITS_EVENT / EXPECTS_FOLLOWUP_EVENT graph to fire implications.
--
-- Shape per array element:
--   {
--     "event_type":   "personnel_added",     // REQUIRED — must match
--                                            // Event.event_type in Neo4j
--     "count":        5,                     // REQUIRED, positive integer
--     "subject_refs": ["emp:101", "emp:102"],// OPTIONAL: per-subject ids
--     "metadata":     {"site": "lon-01"}     // OPTIONAL: free-form
--   }
--
-- App-level validation enforces event_type membership in the known
-- vocabulary (~50 events from enrichment/events/event_nodes.py).
-- DB-level checks only enforce that it's a JSON array.
--
-- This column is REQUIRED only in the sense of "must be a list" —
-- the list MAY be empty (tenant verifies without claiming structured
-- changes; that's the original cite-mode behaviour).

BEGIN;

ALTER TABLE external_evidence_verification_log
    ADD COLUMN IF NOT EXISTS structured_events JSONB NOT NULL DEFAULT '[]'::jsonb;

-- Constraint: must be a JSON array (objects with event_type + count
-- are validated app-side; this prevents storing scalars or objects).
ALTER TABLE external_evidence_verification_log
    DROP CONSTRAINT IF EXISTS external_evidence_verification_log_structured_events_is_array;

ALTER TABLE external_evidence_verification_log
    ADD CONSTRAINT external_evidence_verification_log_structured_events_is_array
        CHECK (jsonb_typeof(structured_events) = 'array');

COMMENT ON COLUMN external_evidence_verification_log.structured_events IS
    'Optional array of structured event emissions for the cascade engine. Each element: {event_type, count, subject_refs?, metadata?}. event_type must match a known Event.event_type from enrichment/events/event_nodes.py.';

-- Index for cascade-engine sweeps that look for verifications with
-- non-empty structured events.
CREATE INDEX IF NOT EXISTS idx_external_evidence_verification_log_has_events
    ON external_evidence_verification_log(tenant_id, verified_at DESC)
    WHERE structured_events <> '[]'::jsonb;

COMMIT;
