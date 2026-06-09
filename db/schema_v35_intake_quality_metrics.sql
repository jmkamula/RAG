-- schema_v35 — extraction-quality telemetry on intake_trace_log.
--
-- Surfaces signals that catch under-extraction without manual review:
--   - drop buckets — what the LLM produced but we filtered (low_conf,
--     short_quote, hallucinated_quote, unknown_ref). A high hallucination
--     rate signals an off-target scope; high short_quote signals the
--     LLM is paraphrasing instead of citing.
--   - coverage signals — markdown_chars vs paragraph_chars catches docx
--     uploads where the table-heavy rescue should have fired (or did).
--     candidate_controls is what doc_mappings scoped to; combined with
--     findings_kept it gives the "yield ratio".
--
-- Companion to commit eba649c (table-heavy docx rescue) — that fix
-- demonstrated why telemetry matters: a 107K-token doc with only 1
-- finding looked "done" without anyone noticing the 98% under-extraction.

ALTER TABLE intake_trace_log
    ADD COLUMN IF NOT EXISTS dropped_low_conf          INTEGER,
    ADD COLUMN IF NOT EXISTS dropped_short_quote       INTEGER,
    ADD COLUMN IF NOT EXISTS dropped_hallucinated      INTEGER,
    ADD COLUMN IF NOT EXISTS dropped_unknown_ref       INTEGER,
    ADD COLUMN IF NOT EXISTS markdown_chars            INTEGER,
    ADD COLUMN IF NOT EXISTS paragraph_chars           INTEGER,
    ADD COLUMN IF NOT EXISTS candidate_controls        INTEGER;

-- Index for quick "needs-attention" queries: find uploads with high
-- hallucination rate or zero-yield extractions. Operational use case
-- is "show me recent uploads where extraction quality looks off".
CREATE INDEX IF NOT EXISTS idx_intake_trace_quality
    ON intake_trace_log (tenant_id, traced_at DESC)
    WHERE stage = 'extract'
      AND (
          dropped_hallucinated > 0
          OR (findings_kept IS NOT NULL AND findings_kept = 0
              AND candidate_controls IS NOT NULL AND candidate_controls > 0)
      );
