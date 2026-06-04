-- =============================================================================
-- schema_v32_workbook_intake_into_stage1.sql
--
-- Course-correction: workbook intake confirmation merges into posture Stage 1.
--
-- The Phase-2 design originally proposed three workbook-intake stages
-- (Discovery / Confirmation / Extraction) with their own HITL surface. That
-- collided terminologically with the already-shipped posture Stage 1 / Stage
-- 2 HITL pipeline AND duplicated the same conceptual layer ("is this a
-- correct evidence claim?"). Realisation: both LLM-doc-extraction and
-- workbook-fingerprinting are upstream evidence-source channels that
-- produce document_findings rows; one queue, one approval flow, two
-- producers.
--
-- Concrete changes in this migration:
--   1. document_findings.inference_source CHECK extended with 'workbook'.
--   2. workbook_intake_proposal.status CHECK simplified to
--      ('pending', 'superseded'). The per-pass accept/reject decision
--      no longer lives on the proposal row — it lives on the underlying
--      document_findings rows via review_status, which posture Stage 1
--      already manages.
--   3. workbook_intake_proposal gains client_document_id (FK to
--      client_documents — the SAME table document_findings.document_id
--      references). The pipeline already follows the filename →
--      client_documents resolution that posture_writer._match_registered_
--      document uses. document_uploads is the upload audit log; it's a
--      parallel table, not the evidence anchor.
--   4. document_findings gains workbook_proposal_id (FK to
--      workbook_intake_proposal, nullable, set only for workbook-sourced
--      findings). Lets Stage 1 group "all findings from sheet X" without
--      a JOIN through the file path.
--
-- This migration does NOT drop the v31 columns (decided_at / decided_by /
-- decision_note) because they could still serve as proposal-level notes
-- if the Stage 1 surface eventually needs a sheet-level accept-all action.
-- They become unused, not invalid.
--
-- Idempotent. Self-committing per [[sql-dry-run-nested-transaction]].
-- =============================================================================

BEGIN;

-- ───────── 1. inference_source: accept 'workbook' ─────────────────────────
ALTER TABLE document_findings
    DROP CONSTRAINT IF EXISTS document_findings_inference_source_check;

ALTER TABLE document_findings
    ADD CONSTRAINT document_findings_inference_source_check
    CHECK (inference_source = ANY (ARRAY[
        'extracted'::text,
        'xfw_bridge'::text,
        'regex_explicit'::text,
        'llm_xfw'::text,
        'workbook'::text
    ]));

-- ───────── 2. workbook_intake_proposal status: drop accept/reject ─────────
-- Existing 'pending' rows stay valid; nothing to backfill.
ALTER TABLE workbook_intake_proposal
    DROP CONSTRAINT IF EXISTS workbook_intake_proposal_status_check;

ALTER TABLE workbook_intake_proposal
    ADD CONSTRAINT workbook_intake_proposal_status_check
    CHECK (status = ANY (ARRAY['pending'::text, 'superseded'::text]));

-- The decided_consistency check referenced 'confirmed'/'rejected' which no
-- longer exist; drop it (decided_at / decided_by may still be set as notes
-- but are not constraint-tied to status anymore).
ALTER TABLE workbook_intake_proposal
    DROP CONSTRAINT IF EXISTS workbook_intake_proposal_decided_consistency;

-- ───────── 3. workbook_intake_proposal.client_document_id ────────────────
-- Earlier draft of this migration added a document_upload_id column pointing
-- at document_uploads. That was wrong: document_findings.document_id
-- references client_documents, and we want the proposal to link to the same
-- evidence anchor its findings reference. Drop the misnamed column (safe —
-- no rows hold values since the v31-era proposals were cleared) and
-- introduce client_document_id.
ALTER TABLE workbook_intake_proposal
    DROP COLUMN IF EXISTS document_upload_id;

ALTER TABLE workbook_intake_proposal
    ADD COLUMN IF NOT EXISTS client_document_id uuid
        REFERENCES client_documents(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_workbook_intake_proposal_client_doc
    ON workbook_intake_proposal (tenant_id, client_document_id);

-- ───────── 4. document_findings.workbook_proposal_id ──────────────────────
ALTER TABLE document_findings
    ADD COLUMN IF NOT EXISTS workbook_proposal_id bigint
        REFERENCES workbook_intake_proposal(id) ON DELETE SET NULL;

-- Lookup: "all findings from this workbook proposal" — the Stage 1 chat
-- surface uses this to group sheet-scoped findings together.
CREATE INDEX IF NOT EXISTS idx_document_findings_workbook_proposal
    ON document_findings (workbook_proposal_id)
    WHERE workbook_proposal_id IS NOT NULL;

COMMIT;
