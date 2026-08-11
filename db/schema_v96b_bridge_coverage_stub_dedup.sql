-- schema_v96b — refine UNIQUE constraint on posture_must_bridge_coverage
-- to include target_control_ref.
--
-- Ship 59'.e (2026-08-11). Ship 59'.a's UNIQUE key was
-- (tenant_id, target_must_id, source_must_id, edge_type). With stub
-- roll-down landing in Ship 59'.e, stub attribution rows (target_control_ref
-- = 'Art.32.1.b') share target_must_id with parent attribution rows
-- (target_control_ref = 'Art.32') because both borrow the same MUSTs from
-- the parent article. Same (target_must_id, source_must_id, edge_type)
-- tuple + different target_control_ref = both are legitimate self-contained
-- attribution shapes and must coexist.
--
-- Adds target_control_ref to the UNIQUE constraint. Migration on the
-- existing table via DROP + ADD (Postgres doesn't support in-place
-- UNIQUE modification).

ALTER TABLE posture_must_bridge_coverage
    DROP CONSTRAINT IF EXISTS uq_pmv_bridge_coverage;

ALTER TABLE posture_must_bridge_coverage
    ADD CONSTRAINT uq_pmv_bridge_coverage
    UNIQUE (tenant_id, target_must_id, target_control_ref, source_must_id, edge_type);
