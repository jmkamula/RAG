-- =============================================================================
-- seed_demo_timeline.sql
--
-- One-shot seed (NOT a migration) for posture_status_log. Populates two
-- illustrative timeline entries for A.6.4 in the Arion Networks tenant so
-- the "timeline for A.6.4" eval case has something to read until real
-- document re-uploads naturally produce live transitions.
--
-- Idempotent: skips if any rows already exist for (tenant, A.6.4).
--
-- Why A.6.4? It's the only currently-tracked control whose posture row was
-- written by the document path (source='document'), so the historical
-- narrative "first OFI, then Comply" is plausible and not in conflict
-- with an assessor or workbook source-authority decision.
--
-- Run: psql -U arioncomply -h 127.0.0.1 -d arioncomply_compliance \
--          -f db/seed_demo_timeline.sql
-- =============================================================================

BEGIN;

DO $$
DECLARE
    v_tenant   uuid := '00000000-0000-0000-0000-000000000001';
    v_posture  uuid;
    v_existing int;
BEGIN
    SELECT id INTO v_posture
      FROM posture_controls
     WHERE tenant_id   = v_tenant
       AND control_ref = 'A.6.4'
       AND standard_id = 'ISO27001:2022'
       AND is_active   = TRUE
     LIMIT 1;

    IF v_posture IS NULL THEN
        RAISE NOTICE 'No A.6.4 posture row for tenant — skipping seed';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO v_existing
      FROM posture_status_log
     WHERE tenant_id   = v_tenant
       AND control_ref = 'A.6.4';

    IF v_existing > 0 THEN
        RAISE NOTICE 'posture_status_log already populated for A.6.4 — skipping seed';
        RETURN;
    END IF;

    INSERT INTO posture_status_log (
        tenant_id, posture_id, control_ref, standard_id,
        status_before, status_after,
        source, source_upload_id,
        evidence_citation, confidence,
        changed_at
    )
    VALUES
        (v_tenant, v_posture, 'A.6.4', 'ISO27001:2022',
         NULL, 'OFI',
         'document', NULL,
         'Initial assessment: training plan partially documented.', 'medium',
         '2026-03-15 10:00:00+00'),
        (v_tenant, v_posture, 'A.6.4', 'ISO27001:2022',
         'OFI', 'Comply',
         'document', NULL,
         'Training schedule updated with quarterly cadence and owner.', 'high',
         '2026-05-06 14:30:00+00');

    RAISE NOTICE 'Seeded 2 demo timeline rows for A.6.4';
END $$;

COMMIT;
