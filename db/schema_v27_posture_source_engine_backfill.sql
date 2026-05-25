-- =============================================================================
-- schema_v27_posture_source_engine_backfill.sql
--
-- Adds 'engine_backfill' to posture_controls.source CHECK constraint.
--
-- The fulfilment engine produces verdicts for curated controls (e.g. all 303
-- GDPR articles with a FulfilmentSpec in Neo4j) but _persist_engine_proposals
-- can only attach proposals to posture_controls rows that already exist. The
-- engine writes engine_proposed_finding on UPDATE — it does not create the
-- inventory row itself. Before this commit only ISO 27001 + a hand-picked
-- single GDPR row (Art.28) were present, so 19 of the 20 GDPR engine verdicts
-- had nowhere to land and never reached the chat.
--
-- A one-time backfill inserts the missing rows with finding='Not assessed'
-- and source='engine_backfill' so they are auditable as "inventory created by
-- the backfill, not by chat/document extraction/assessor workflow". Existing
-- allowed source values do not capture this provenance — 'engine' implies a
-- finding the engine asserted (we have not yet), 'Not assessed' loses the
-- backfill signal entirely.
--
-- Idempotent.
-- =============================================================================

ALTER TABLE posture_controls DROP CONSTRAINT IF EXISTS posture_controls_source_check;
ALTER TABLE posture_controls ADD CONSTRAINT posture_controls_source_check
  CHECK (source = ANY (ARRAY[
    'chat'::text,
    'questionnaire'::text,
    'document'::text,
    'assessor'::text,
    'self_reported'::text,
    'workbook'::text,
    'Not assessed'::text,
    'engine'::text,
    'engine_backfill'::text
  ]));
