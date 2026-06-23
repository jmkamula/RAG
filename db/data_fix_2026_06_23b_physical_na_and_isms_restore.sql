-- Data fix 2026-06-23 (round 2): physical-scope N/A + ISMS 7.x restoration.
--
-- Follow-up to db/data_fix_2026_06_23_workbook_bare_annex_a.sql (commit
-- f4677ba). After normalizing bare Annex A refs from the 2026-06-23
-- workbook re-upload, investigation surfaced two more cleanups:
--
-- 1. Workbook explicitly declares physical-scope controls as N/A via
--    evidence text "Not per ISMS Scope as no physical assets exist"
--    (A.7.6, A.7.8, A.7.11, A.7.12) and "Not per ISMS Scope" (A.8.21,
--    A.8.22, A.8.26). These landed as status='present' (workbook
--    importer mis-classification — see [[workbook-importer-bare-annex-a-2026-06-23]]).
--    Fix: mark these controls + the rest of the A.7.x physical family
--    as finding='N/A' on posture_controls. Arion is cloud-only with no
--    physical infrastructure in scope.
--
-- 2. The first data fix retired bare 7.1-7.5 posture_controls rows
--    assuming they were Annex A duplicates. Closer inspection shows
--    the workbook uses bare 7.x for BOTH ISMS clauses 7.1-7.5 (Support:
--    Resources/Competence/Awareness/Communication/Documentation) AND
--    Annex A.7.1-7.5 (Physical security perimeters/entry-exit/work/
--    desk/empty-screen) in different rows of the same workbook.
--    The Annex A.7.1-7.5 findings landed via different path; the
--    bare 7.1-7.5 rows are the ISMS clauses. Restore them.
--
-- Architectural follow-up (deferred): workbook importer should
-- 2a. recognize "Not per ISMS Scope" / "no [physical|software|...]
--     assets exist" as status='not_applicable' instead of 'present'
-- 2b. disambiguate bare 7.x by sheet context (Competence Records →
--     ISMS; physical asset sheets → Annex A)
--
-- Per-tenant. Idempotent.

\set ON_ERROR_STOP on

BEGIN;

-- 1. Mark physical-scope + workbook-declared-N/A controls as N/A
UPDATE posture_controls
SET finding = 'N/A',
    gap_description = COALESCE(gap_description, '') ||
        ' [N/A 2026-06-23: per Arion workbook — cloud-only operations, no physical infrastructure in scope]',
    source = 'document',
    last_updated = now()
WHERE tenant_id = '00000000-0000-0000-0000-000000000001'
  AND is_active = TRUE
  AND finding <> 'N/A'
  AND control_ref IN
    ('A.7.1','A.7.2','A.7.3','A.7.4','A.7.5','A.7.6','A.7.7','A.7.8','A.7.9',
     'A.7.10','A.7.11','A.7.12','A.7.13','A.7.14',
     'A.8.21','A.8.22','A.8.26');

-- 2. Restore ISMS clause 7.1-7.5 posture_controls rows. These were
--    retired by f4677ba's bare-duplicate cleanup but are actually
--    distinct ISMS clauses (Support family) with workbook evidence
--    (Competence Records, ISMS training, awareness). Engine has
--    per-MUST findings on these; just need posture rows to surface.
UPDATE posture_controls
SET is_active = TRUE,
    node_id = 'ISO27001:2022:' || control_ref,
    finding = 'Not assessed',  -- engine overlay computes the verdict
    last_updated = now()
WHERE tenant_id = '00000000-0000-0000-0000-000000000001'
  AND standard_id = 'ISO27001:2022'
  AND control_ref IN ('7.1','7.2','7.3','7.4','7.5')
  AND is_active = FALSE;

COMMIT;
