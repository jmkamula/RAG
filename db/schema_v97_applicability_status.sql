-- Ship 66'.a (2026-08-12) — split applicability from finding.
--
-- Codified rule [[feedback-engine-should-not-clobber-tenant-na]] said
-- "tenant N/A must dominate engine derivation always." The rule was
-- documented but not structurally enforced: `posture_controls.finding`
-- mixed two semantically different signals — evidence assessment
-- (NC/OFI/Comply/Not assessed) and scoping (N/A) — in a single column.
-- Every consumer of `finding` had to remember that N/A was a special
-- case. A past Stage-2 mass-approval regressed the guard and clobbered
-- 17 Arion N/A declarations by flipping engine_proposal_status='approved'.
--
-- Ship 66'.a makes N/A structurally dominant by adding a separate
-- `applicability_status` axis. This commit is data-shape only — no
-- consumer reads the new column yet. Subsequent Ship 66'.b, 66'.c,
-- 66'.d migrate consumers. Ship 66'.d retires `finding = 'N/A'` as a
-- valid value.
--
-- Two-column model:
--
--   applicability_status = 'applicable' | 'na'
--     Scoping decision. Immutable by engine. If 'na', the control is
--     out of scope for this tenant — no evidence assessment applies.
--
--   finding = 'NC' | 'OFI' | 'Comply' | 'Not assessed' | 'N/A' *
--     Evidence assessment (post-scope). Only meaningful when
--     applicability_status = 'applicable'.
--     * 'N/A' remains a legal value for backward compat until Ship
--       66'.d; consumers should prefer applicability_status.

ALTER TABLE posture_controls
    ADD COLUMN IF NOT EXISTS applicability_status TEXT
        NOT NULL DEFAULT 'applicable'
        CHECK (applicability_status IN ('applicable', 'na'));

-- Populate: every existing row where finding='N/A' becomes
-- applicability_status='na'. Idempotent — subsequent runs are no-ops
-- (the WHERE clause is a subset of 'applicable' by default, and
-- controls already flipped this pass are already 'na').
UPDATE posture_controls
   SET applicability_status = 'na'
 WHERE finding = 'N/A'
   AND applicability_status = 'applicable';

-- Index the new column so Ship 66'.b's overlay guard + Ship 66'.c's
-- readers can filter cheaply.
CREATE INDEX IF NOT EXISTS ix_posture_controls_applicability
    ON posture_controls (tenant_id, applicability_status)
 WHERE applicability_status = 'na';
