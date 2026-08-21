-- schema_v107_cite_attestation_confidence.sql
--
-- Ship 92'.f (2026-08-21) — codify expose+track: retire silent
-- machine attestations; every verification_log row has a tenant
-- decision behind it.
--
-- Ship 92'.a's `resolve_cites_on_document_upload` used to write
-- verification_log automatically when a URL basename matched an
-- uploaded filename + linked doc had present findings on same MUST.
-- Ship 92'.f downgrades that path to CANDIDATE GENERATION: on match,
-- create a cite_attestation_prompt with confidence='high' instead
-- of writing verification_log. Tenant still one-clicks confirm on
-- the same Ship 92'.d card; a "strong match — one-click recommended"
-- visual hint surfaces the confidence.
--
-- New `confidence` column on cite_attestation_prompt distinguishes
-- MUST-overlap-only (confidence='must_overlap', the Ship 92'.b default)
-- from URL-basename-strong-match (confidence='url_and_must'). The
-- UI can visually escalate the strong-match rows.
--
-- No verification_log schema change — the log itself already requires
-- verified_by NOT NULL, which is the invariant Ship 92'.f enforces.

BEGIN;

ALTER TABLE cite_attestation_prompt
    ADD COLUMN IF NOT EXISTS confidence TEXT NOT NULL DEFAULT 'must_overlap';

ALTER TABLE cite_attestation_prompt
    DROP CONSTRAINT IF EXISTS cite_attestation_prompt_confidence_chk;
ALTER TABLE cite_attestation_prompt
    ADD CONSTRAINT cite_attestation_prompt_confidence_chk
    CHECK (confidence IN ('must_overlap', 'url_and_must'));

COMMENT ON COLUMN cite_attestation_prompt.confidence IS
  'Ship 92''.f — signal quality behind the prompt. '
  '''must_overlap'' (default, Ship 92''.b): uploaded doc has present '
  'findings on the same MUST as the cite. '
  '''url_and_must'' (Ship 92''.f): the doc''s filename ALSO matches the '
  'cite URL basename ILIKE (Ship 92''.a-style URL match) IN ADDITION '
  'to MUST overlap. UI can visually escalate url_and_must to '
  '"strong match — one-click confirm recommended".';

CREATE INDEX IF NOT EXISTS idx_cite_attestation_prompt_pending_confidence
    ON cite_attestation_prompt (tenant_id, confidence, created_at DESC)
    WHERE status = 'pending';

COMMIT;
