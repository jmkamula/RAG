-- schema_v71_ship3e_producer_kinds.sql
--
-- Ship 3'.e (2026-07-17) — expand tenant_notification.kind for two
-- more producers wired in this arc.
--
-- Adds:
--   stage2_proposal_ready — engine has surfaced a new pending Stage-2
--                           verdict divergent from live posture; the
--                           tenant should review the proposal.
--   upload_failed         — a document upload landed in status='failed'
--                           (Stage 1 read/extract raised an exception).
--
-- The existing kinds
-- (implication_overdue / followup_overdue / threshold_crossed /
--  cascade_blocked / auto_resolved / freshness_expiry / nc_surfaced /
--  upload_processed) stay untouched.

BEGIN;

ALTER TABLE tenant_notification
    DROP CONSTRAINT IF EXISTS tenant_notification_kind_chk;
ALTER TABLE tenant_notification
    DROP CONSTRAINT IF EXISTS tenant_notification_kind_check;

ALTER TABLE tenant_notification
    ADD CONSTRAINT tenant_notification_kind_check
    CHECK (kind = ANY (ARRAY[
        'implication_overdue',
        'followup_overdue',
        'threshold_crossed',
        'cascade_blocked',
        'auto_resolved',
        'freshness_expiry',
        'nc_surfaced',
        'upload_processed',
        'stage2_proposal_ready',
        'upload_failed'
    ]));

COMMENT ON COLUMN tenant_notification.kind IS
'Notification category. Kinds added in Ship 3''.e (2026-07-17): stage2_proposal_ready (engine wrote a new pending Stage-2 verdict — fired inside rag/posture_loader.py::_persist_engine_proposals); upload_failed (document upload exception path — fired in rag/intake/doc_pipeline.py exception handler).';

COMMIT;
