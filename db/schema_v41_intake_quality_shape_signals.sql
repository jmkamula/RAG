-- schema_v41 — surface doc-shape filter outcomes in intake_trace_log.
--
-- Background. Two doc-shape filters shipped in the past three days:
--   - questionnaire (2026-06-12, d7f1160) — drops per-question evidence
--   - TOC          (2026-06-15, 5216168) — skips TOC/index uploads at entry
-- Both incidents that prompted the filters showed up as `quality_flag=green`
-- in the admin uploads-quality dashboard, because `findings_kept` was
-- non-zero. The dashboard couldn't see its own catches.
--
-- This migration persists those signals so:
--   1. operators can audit how often each filter fires
--   2. the quality flag can distinguish "found stuff" from "found nothing
--      useful" (TOC skip → no LLM call → no findings; questionnaire drop
--      → many findings dropped before they reach the kept count)
--
-- Both columns are nullable — historical rows pre-v41 stay NULL; the
-- endpoint treats NULL as 0 for arithmetic and as "not applicable" for
-- the TOC reason string.

ALTER TABLE intake_trace_log
    ADD COLUMN IF NOT EXISTS dropped_questionnaire INTEGER,
    ADD COLUMN IF NOT EXISTS skipped_as_toc        TEXT;

-- Extend the needs-attention index to include TOC-skipped uploads and
-- high-questionnaire-drop uploads. Existing predicate cases preserved
-- so older code paths still benefit.
DROP INDEX IF EXISTS idx_intake_trace_quality;
CREATE INDEX IF NOT EXISTS idx_intake_trace_quality
    ON intake_trace_log (tenant_id, traced_at DESC)
    WHERE stage = 'extract'
      AND (
          dropped_hallucinated > 0
          OR (findings_kept IS NOT NULL AND findings_kept = 0
              AND candidate_controls IS NOT NULL AND candidate_controls > 0)
          OR skipped_as_toc IS NOT NULL
          OR (dropped_questionnaire IS NOT NULL AND dropped_questionnaire > 0)
      );
