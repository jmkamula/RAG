-- schema_v96c — allow posture_must_verdicts to hold stub-context rows.
--
-- Ship 59'.e (2026-08-11). Original UNIQUE on
-- (tenant_id, must_id) enforced one row per (tenant, MUST). Ship 59'.e
-- writes additional rows for stub RequirementNodes where the effective
-- MUSTs come from a parent article — same must_id (e.g.
-- item:Art.32:purposes) appears both under its canonical owner
-- (control_ref='Art.32') and under stub contexts (control_ref='Art.32.1.b').
-- Both are legitimate self-contained representations and must coexist.
--
-- Migrating on the existing table via DROP + ADD (Postgres doesn't
-- support in-place UNIQUE modification).

ALTER TABLE posture_must_verdicts
    DROP CONSTRAINT IF EXISTS uq_pmv_tenant_must;

ALTER TABLE posture_must_verdicts
    ADD CONSTRAINT uq_pmv_tenant_must
    UNIQUE (tenant_id, must_id, control_ref);
