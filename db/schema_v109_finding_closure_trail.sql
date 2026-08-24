-- schema_v109_finding_closure_trail.sql
--
-- Ship 93'.z.iii (2026-08-24) — auditor-visible closure trail on
-- document_findings.
--
-- Ships 93'.a/f made partials + missing MUSTs actionable. Ship 93'.b
-- gave the tenant an "Upload evidence to close this" button. But
-- when the resulting upload actually closes the partial/missing state
-- (by producing a new present finding on the same MUST), there's no
-- explicit linkage back to the finding that got closed. Auditor sees
-- the new present finding + can see the old partial got superseded
-- (is_active=FALSE) but not the causal "resolved by upload X on Y."
--
-- This migration adds:
--
--   1. document_findings.resolved_by_upload_id UUID NULL
--      FK document_uploads(id) ON DELETE SET NULL — the upload whose
--      extraction produced a covering present finding.
--
--   2. document_findings.resolved_at TIMESTAMPTZ NULL — when the
--      closure linkage was stamped. Distinct from `extracted_at`
--      (when the source finding landed) — resolved_at is when the
--      linkage was recognized by the closure sweep.
--
--   3. document_findings.resolution_reason TEXT NULL — auditor
--      narrative ("upload of ‘X.docx’ produced present finding on
--      same MUST"). Free-form; explainer generates.
--
-- The stamping happens in the post-write closure sweep — a small
-- module that runs after write_findings inside doc_pipeline.
-- Ship 93'.z.iii adds the schema; the runtime hook is Ship 93'.z.iv
-- (or bundled here).

BEGIN;

ALTER TABLE document_findings
    ADD COLUMN IF NOT EXISTS resolved_by_upload_id UUID
        REFERENCES document_uploads(id) ON DELETE SET NULL;

ALTER TABLE document_findings
    ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMPTZ;

ALTER TABLE document_findings
    ADD COLUMN IF NOT EXISTS resolution_reason TEXT;

COMMENT ON COLUMN document_findings.resolved_by_upload_id IS
  'Ship 93''.z.iii — nullable FK to the upload whose extraction '
  'produced a covering present finding on the same MUST. Set by '
  'the post-upload closure sweep in rag/posture/finding_closure.py. '
  'NULL means the finding hasn''t been resolved via upload (still '
  'active-partial, active-missing-tracked-elsewhere, or already '
  'closed for another reason like Stage-1 rejection).';

COMMENT ON COLUMN document_findings.resolved_at IS
  'Ship 93''.z.iii — when the closure linkage was stamped. Distinct '
  'from extracted_at (source finding creation) and deleted_at (soft-'
  'delete). Populated together with resolved_by_upload_id.';

COMMENT ON COLUMN document_findings.resolution_reason IS
  'Ship 93''.z.iii — auditor-facing narrative for the closure. '
  'Example: "upload of ‘Info Security Policy.docx’ produced present '
  'finding on same MUST item:A.5.9:owner_per_asset".';

CREATE INDEX IF NOT EXISTS idx_document_findings_resolved_by_upload
    ON document_findings (tenant_id, resolved_by_upload_id)
    WHERE resolved_by_upload_id IS NOT NULL;

COMMIT;
