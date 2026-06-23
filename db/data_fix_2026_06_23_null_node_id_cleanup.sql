-- Data fix 2026-06-23: cleanup of NULL node_id rows in posture_controls.
--
-- Background: 28 posture_controls rows on tenant_arion_demo had NULL
-- node_id, leaving them invisible to the engine's verdict-by-node-id
-- lookup. Surfaced during the Direction C debugging session when
-- A.5.15 wouldn't move from NC to OFI despite ample evidence —
-- backfilled 3 (A.5.15/16/17) on the spot, deferred the broader 25.
--
-- This fix sweeps the rest:
--
-- Categories
-- ----------
-- Backfill-safe (11) — exist in Neo4j, valid:
--   6.1, A.5.1, A.5.2, A.5.3, A.5.12, A.5.20, A.5.31, A.5.34, A.5.36,
--   A.6.4, Art.28 (GDPR)
--
-- Misclassified standard_id (2) — Art.28/Art.30 stored as ISO27001:
--   correct GDPR rows exist separately. Mark inactive with audit note.
--
-- Obsolete 2013-era (3) — A.6.1.1/2/3 don't exist in 2022 graph.
--   Mark inactive.
--
-- Custom tenant controls (9) — X.XXXX.99 — already inactive, no Neo4j
--   match by design. Leave NULL.
--
-- This is per-tenant data, not migrated to other tenants. Future
-- onboarding should populate node_id at insert time (workbook_importer +
-- direct seed paths both already do this for new rows; the gap was
-- historical).

\set ON_ERROR_STOP on

BEGIN;

-- Backfill 11 controls that exist in Neo4j with their standard:ref id
UPDATE posture_controls
SET node_id = standard_id || ':' || control_ref
WHERE tenant_id = '00000000-0000-0000-0000-000000000001'
  AND node_id IS NULL
  AND (
    (standard_id = 'ISO27001:2022' AND control_ref IN
      ('6.1', 'A.5.1', 'A.5.2', 'A.5.3', 'A.5.12', 'A.5.20',
       'A.5.31', 'A.5.34', 'A.5.36', 'A.6.4'))
    OR (standard_id = 'GDPR:2016/679' AND control_ref = 'Art.28')
  );

-- Retire misclassified Art.28/Art.30 (ISO27001 standard_id)
UPDATE posture_controls
SET is_active = FALSE,
    last_updated = now()
WHERE tenant_id = '00000000-0000-0000-0000-000000000001'
  AND standard_id = 'ISO27001:2022'
  AND control_ref IN ('Art.28', 'Art.30');

-- Retire obsolete 2013-era controls
UPDATE posture_controls
SET is_active = FALSE,
    last_updated = now()
WHERE tenant_id = '00000000-0000-0000-0000-000000000001'
  AND control_ref IN ('A.6.1.1', 'A.6.1.2', 'A.6.1.3');

COMMIT;
