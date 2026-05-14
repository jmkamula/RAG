-- ArionComply Schema v14 — Canonical control_ref form + dedup posture_controls
-- Safe to run on top of v13. Idempotent for re-runs.
--
-- Discovered bug: ISO 27001 Annex A controls existed in posture_controls in
-- TWO forms — bare (e.g. "5.18", workbook-imported) and A-prefix ("A.5.18",
-- intake/assessor-created). load_posture indexes by STANDARD:VERSION:REF so
-- each duplicate pair landed in posture state as TWO entries with conflicting
-- findings (workbook "Comply" + intake "NC"). Whichever the resolver hit
-- first won. 17 such pairs existed for this tenant.
--
-- Canonical form chosen: ISO 27001 Annex A → 'A.<n>.<m>' (matches the
-- standard text and document_findings). Main body clauses (9.x, 10.x) stay
-- bare. ISO 27701 and GDPR unchanged.
--
-- Retention: every mutated/removed row is archived to posture_history with
-- a deletion_reason BEFORE the change. The intake (evidence-based) finding
-- wins each merge per user direction — workbook "Comply" defaults were
-- presumptive, intake assessments were extracted from policy text.

BEGIN;

-- ── Step 0: build the merge map ───────────────────────────────────────────
-- 17 expected rows: one per (workbook bare, intake A-prefix) duplicate pair.
CREATE TEMP TABLE pc_merge_map AS
SELECT
    workbook.id           AS old_id,
    workbook.control_ref  AS old_ref,
    workbook.tenant_id    AS tenant_id,
    workbook.standard_id  AS standard_id,
    intake.id             AS new_id,
    intake.control_ref    AS new_ref,
    workbook.finding      AS old_finding,
    workbook.gap_description AS old_gap,
    intake.finding        AS new_finding
FROM posture_controls workbook
JOIN posture_controls intake
  ON intake.tenant_id   = workbook.tenant_id
 AND intake.standard_id = workbook.standard_id
 AND intake.control_ref = 'A.' || workbook.control_ref
WHERE workbook.standard_id = 'ISO27001:2022'
  AND workbook.is_active   = TRUE
  AND intake.is_active     = TRUE
  AND workbook.control_ref ~ '^[5-8]\.'   -- only Annex A subclauses
  AND workbook.control_ref NOT LIKE 'A.%';

-- ── Step 1: archive workbook rows (about to be deactivated) to history ────
INSERT INTO posture_history (
    control_id, tenant_id, finding, confidence,
    gap_description, action_required, source, source_authority,
    chat_session_id, established_via, changed_by, changed_by_role,
    confirmed_by, confirmed_at,
    deletion_reason, is_active, retention_class, expires_at
)
SELECT
    pc.id, pc.tenant_id, pc.finding, pc.confidence,
    pc.gap_description, pc.action_required, pc.source, pc.source_authority,
    NULL, 'workbook_import', NULL, 'system',
    pc.confirmed_by, pc.confirmed_at,
    'merged into A-prefix row during control_ref normalization (schema v14)',
    TRUE, 'compliance', NOW() + INTERVAL '7 years'
FROM posture_controls pc
JOIN pc_merge_map m ON m.old_id = pc.id;

-- ── Step 2: annotate intake row with the prior workbook signal when it
-- conflicts. Preserves the audit-trail expectation that the surviving row
-- knows about its predecessor.
UPDATE posture_controls intake
   SET gap_description = COALESCE(intake.gap_description, '')
       || CASE WHEN intake.gap_description IS NOT NULL AND intake.gap_description <> ''
               THEN E'\n\n' ELSE '' END
       || '[Pre-existing workbook assessment was: ' || m.old_finding
       || CASE WHEN m.old_gap IS NOT NULL AND m.old_gap <> ''
               THEN ' — ' || m.old_gap ELSE '' END
       || ' — superseded by document/assessor evidence ' || NOW()::date || ']'
  FROM pc_merge_map m
 WHERE intake.id = m.new_id
   AND m.old_finding <> m.new_finding;

-- ── Step 3: reroute control_documents FK refs from workbook → intake ─────
INSERT INTO control_documents (tenant_id, control_id, document_id, relationship, source)
SELECT cd.tenant_id, m.new_id, cd.document_id, cd.relationship, cd.source
  FROM control_documents cd
  JOIN pc_merge_map m ON m.old_id = cd.control_id
ON CONFLICT (tenant_id, control_id, document_id, relationship) DO NOTHING;

DELETE FROM control_documents
 WHERE control_id IN (SELECT old_id FROM pc_merge_map);

-- posture_pending / remediation_plans / confirmation_log all have 0 rows
-- pointing at the workbook duplicates (verified pre-migration). Keep the
-- reroute pattern here as future-proof guards, but they will be no-ops.

UPDATE posture_pending pp
   SET control_id = m.new_id
  FROM pc_merge_map m
 WHERE pp.control_id = m.old_id;

UPDATE remediation_plans rp
   SET control_id = m.new_id
  FROM pc_merge_map m
 WHERE rp.control_id = m.old_id;

UPDATE confirmation_log cl
   SET posture_control_id = m.new_id
  FROM pc_merge_map m
 WHERE cl.posture_control_id = m.old_id;

-- ── Step 4: soft-delete the workbook duplicates ──────────────────────────
UPDATE posture_controls
   SET is_active       = FALSE,
       deleted_at      = NOW(),
       deletion_reason = 'merged into A-prefix row during control_ref '
                         'normalization (schema v14)'
 WHERE id IN (SELECT old_id FROM pc_merge_map);

-- ── Step 5: archive the bare-form Annex A rows we're about to rename ────
-- These are the remaining workbook rows (no intake counterpart) whose
-- control_ref still needs normalization.
INSERT INTO posture_history (
    control_id, tenant_id, finding, confidence,
    gap_description, action_required, source, source_authority,
    chat_session_id, established_via, changed_by, changed_by_role,
    confirmed_by, confirmed_at,
    deletion_reason, is_active, retention_class, expires_at
)
SELECT
    pc.id, pc.tenant_id, pc.finding, pc.confidence,
    pc.gap_description, pc.action_required, pc.source, pc.source_authority,
    NULL, 'workbook_import', NULL, 'system',
    pc.confirmed_by, pc.confirmed_at,
    'control_ref normalized from "' || pc.control_ref
       || '" to "A.' || pc.control_ref
       || '" (schema v14 canonical Annex A form)',
    TRUE, 'compliance', NOW() + INTERVAL '7 years'
FROM posture_controls pc
WHERE pc.standard_id = 'ISO27001:2022'
  AND pc.is_active   = TRUE
  AND pc.control_ref ~ '^[5-8]\.'
  AND pc.control_ref NOT LIKE 'A.%';

-- ── Step 6: rename remaining bare-form Annex A rows to A-prefix ──────────
UPDATE posture_controls
   SET control_ref = 'A.' || control_ref,
       node_id     = standard_id || ':A.' || control_ref
 WHERE standard_id = 'ISO27001:2022'
   AND is_active   = TRUE
   AND control_ref ~ '^[5-8]\.'
   AND control_ref NOT LIKE 'A.%';

-- ── Step 7: prevent future regressions ────────────────────────────────────
-- Unique (tenant_id, standard_id, control_ref) for active rows. Bare rows
-- and A-prefix rows of the same underlying control can no longer coexist.
DROP INDEX IF EXISTS uidx_posture_controls_active;
CREATE UNIQUE INDEX uidx_posture_controls_active
    ON posture_controls (tenant_id, standard_id, control_ref)
 WHERE is_active = TRUE;

COMMIT;
