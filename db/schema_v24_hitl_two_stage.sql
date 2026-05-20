-- =============================================================================
-- schema_v24_hitl_two_stage.sql
--
-- Additive schema for the two-stage HITL approval model
-- ([[hitl-two-stage-approval-design]]):
--
--   upload → extract → document_findings (review_status='pending')
--          → user batch-approves per control
--          → posture_controls.confirmation_status = 'document_confirmed'
--          → engine runs, writes posture_controls.engine_proposed_*
--          → user approves engine verdict
--          → posture_controls.finding overwritten + confirmation_status='engine_confirmed'
--
-- This migration adds storage only. The writer, engine, and chat surfaces are
-- wired in commits 2–5. After this commit lands, behaviour is unchanged: new
-- columns default to nulls/legacy markers and nothing reads them yet.
--
-- Backfill policy (per design "no back-confirmation pass"):
--   document_findings.review_status  → 'approved' for existing rows.
--     Rationale: legacy rows already feed posture; the engine source-set
--     filter (commit 4) would otherwise drop all 144 rows on deploy.
--   posture_status_log.change_kind   → 'extraction' for existing rows.
--     Rationale: the only existing writer is the document-intake path
--     (source='document'), so every historical row is an extraction event.
--
-- CHECK extensions are additive (new allowed values, existing values stay
-- valid), so this remains a forward-only migration.
--
-- Per [[sql-dry-run-nested-transaction]]: the COMMIT below makes this file
-- self-committing. Do not rely on an outer BEGIN/ROLLBACK to undo it.
-- =============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 1) document_findings: per-finding review gate (Stage 1)
-- ----------------------------------------------------------------------------

ALTER TABLE document_findings
    ADD COLUMN IF NOT EXISTS review_status    text NOT NULL DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS rejection_reason text,
    ADD COLUMN IF NOT EXISTS reviewed_by      uuid,
    ADD COLUMN IF NOT EXISTS reviewed_at      timestamptz;

-- Backfill: pre-deploy rows are grandfathered as approved so the engine
-- source-set filter in commit 4 doesn't shrink behaviour on the day of deploy.
-- New rows arriving after deploy get the column default ('pending').
UPDATE document_findings
   SET review_status = 'approved'
 WHERE review_status = 'pending'  -- i.e. just-defaulted by the ADD COLUMN
   AND extracted_at < now();

-- Allowed states.
ALTER TABLE document_findings
    DROP CONSTRAINT IF EXISTS document_findings_review_status_check;
ALTER TABLE document_findings
    ADD CONSTRAINT document_findings_review_status_check
    CHECK (review_status IN ('pending', 'approved', 'rejected', 'expired'));

-- Rejected/expired findings must not be active — the engine filters on
-- is_active=true and we want a rejected/expired row to be invisible to it
-- without relying on the writer to remember to flip both columns.
ALTER TABLE document_findings
    DROP CONSTRAINT IF EXISTS document_findings_review_inactive_check;
ALTER TABLE document_findings
    ADD CONSTRAINT document_findings_review_inactive_check
    CHECK (review_status NOT IN ('rejected', 'expired') OR is_active = false);

-- Stage-1 chat surface read pattern: "show pending findings for control X".
CREATE INDEX IF NOT EXISTS idx_document_findings_review_pending
    ON document_findings (tenant_id, control_ref)
    WHERE review_status = 'pending' AND is_active = true;

-- Engine source-set lookup (used by commit 4's engine_runner filter).
CREATE INDEX IF NOT EXISTS idx_document_findings_review_approved
    ON document_findings (tenant_id, control_ref)
    WHERE review_status = 'approved' AND is_active = true;

-- ----------------------------------------------------------------------------
-- 2) posture_controls: engine proposal gate (Stage 2)
-- ----------------------------------------------------------------------------

ALTER TABLE posture_controls
    ADD COLUMN IF NOT EXISTS engine_proposed_finding text,
    ADD COLUMN IF NOT EXISTS engine_proposed_at      timestamptz,
    ADD COLUMN IF NOT EXISTS engine_proposal_status  text NOT NULL DEFAULT 'none',
    ADD COLUMN IF NOT EXISTS engine_approved_by      uuid,
    ADD COLUMN IF NOT EXISTS engine_approved_at      timestamptz,
    ADD COLUMN IF NOT EXISTS engine_proposal_reason  text;

-- Allowed states for the engine-proposal track.
ALTER TABLE posture_controls
    DROP CONSTRAINT IF EXISTS posture_controls_engine_proposal_status_check;
ALTER TABLE posture_controls
    ADD CONSTRAINT posture_controls_engine_proposal_status_check
    CHECK (engine_proposal_status IN ('none', 'proposed', 'approved', 'rejected'));

-- The engine_proposed_finding must use the same vocabulary as `finding`,
-- with NULL meaning "no proposal currently outstanding".
ALTER TABLE posture_controls
    DROP CONSTRAINT IF EXISTS posture_controls_engine_proposed_finding_check;
ALTER TABLE posture_controls
    ADD CONSTRAINT posture_controls_engine_proposed_finding_check
    CHECK (engine_proposed_finding IS NULL
           OR engine_proposed_finding IN ('NC', 'OFI', 'Comply', 'N/A', 'Not assessed'));

-- Extend confirmation_status vocabulary to cover the two new gates. Existing
-- 'draft' / 'confirmed' / 'overridden' values remain valid.
ALTER TABLE posture_controls
    DROP CONSTRAINT IF EXISTS posture_controls_confirmation_status_check;
ALTER TABLE posture_controls
    ADD CONSTRAINT posture_controls_confirmation_status_check
    CHECK (confirmation_status IN (
        'draft',
        'confirmed',
        'overridden',
        'document_confirmed',  -- Stage 1 passed: all findings for this control approved
        'engine_confirmed'     -- Stage 2 passed: engine verdict approved & applied
    ));

-- Stage-2 chat surface read pattern: "show controls with an outstanding
-- engine proposal awaiting approval".
CREATE INDEX IF NOT EXISTS idx_posture_controls_engine_proposed
    ON posture_controls (tenant_id, engine_proposal_status)
    WHERE engine_proposal_status = 'proposed' AND is_active = true;

-- ----------------------------------------------------------------------------
-- 3) posture_status_log: explain *why* a transition happened
-- ----------------------------------------------------------------------------

ALTER TABLE posture_status_log
    ADD COLUMN IF NOT EXISTS change_kind text;

-- Backfill: the only writer wired pre-v24 is the document-intake path
-- (source='document'); every existing row is therefore an extraction event.
UPDATE posture_status_log
   SET change_kind = 'extraction'
 WHERE change_kind IS NULL;

ALTER TABLE posture_status_log
    ALTER COLUMN change_kind SET DEFAULT 'extraction';
ALTER TABLE posture_status_log
    ALTER COLUMN change_kind SET NOT NULL;

ALTER TABLE posture_status_log
    DROP CONSTRAINT IF EXISTS posture_status_log_change_kind_check;
ALTER TABLE posture_status_log
    ADD CONSTRAINT posture_status_log_change_kind_check
    CHECK (change_kind IN ('extraction', 'engine', 'assessor', 'acknowledgement'));

-- ----------------------------------------------------------------------------
-- Grants: no new tables, so existing arioncomply_app SELECT/INSERT/UPDATE
-- on these three tables continues to cover the new columns. RLS policies
-- are column-blind, so nothing to re-grant.
-- ----------------------------------------------------------------------------

COMMIT;
