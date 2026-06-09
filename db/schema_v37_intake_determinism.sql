-- schema_v37 — two changes toward deterministic intake.
--
-- (1) doc_mappings_match_count on intake_trace_log: how many
--     doc_mappings YAMLs fingerprinted the upload. 0 means the
--     extractor fell through to legacy _scope_controls. The new
--     admin endpoint /admin/intake/unmatched-patterns groups
--     zero-match uploads by tokenised filename to surface common
--     shapes that need umbrella YAMLs.
--
-- (2) enricher_cache: SHA-keyed cache of the LLM enricher's output
--     (doc_type, standard_ids, topic_tokens, scope_statement).
--     The enricher is the dominant non-determinism source — same
--     doc bytes produce different topic_tokens across runs,
--     leading to different doc_mappings matches downstream. Caching
--     by source_sha256 makes the enricher path fully deterministic
--     for repeat uploads of the same bytes.

ALTER TABLE intake_trace_log
    ADD COLUMN IF NOT EXISTS doc_mappings_match_count INTEGER;

CREATE TABLE IF NOT EXISTS enricher_cache (
    sha256          TEXT PRIMARY KEY,
    doc_type        TEXT,
    standard_ids    TEXT[],
    topic_tokens    TEXT[],
    scope_statement TEXT,
    cached_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    hit_count       INTEGER     NOT NULL DEFAULT 0,
    last_hit_at     TIMESTAMPTZ
);

-- Cleanup index — cached_at lets us age out old entries via a
-- nightly purge (e.g. keep last 30 days only; cache hit refreshes
-- last_hit_at, so frequently-used entries stay).
CREATE INDEX IF NOT EXISTS idx_enricher_cache_cached_at
    ON enricher_cache (cached_at);

GRANT SELECT, INSERT, UPDATE ON enricher_cache TO arioncomply_app;
