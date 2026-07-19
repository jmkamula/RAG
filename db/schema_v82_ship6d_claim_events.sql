-- schema_v82_ship6d_claim_events.sql
--
-- Ship 6'.d (2026-07-19) — passive claim-scan observability.
--
-- Ship 6'.c's retrospective on chat_casefile_log showed 87.7% of
-- turns fire a preservation repair. Ship 6'.d asks a different
-- question of the same data: how often does the LLM make a
-- normative claim ("Art.32 requires X", "under GDPR, ...", "the
-- standard mandates Y") — and are those claims grounded in the
-- case-file digest?
--
-- The case-file architecture (verbatim MUST/SHOULD content in the
-- prompt) is designed to keep the LLM quoting rather than
-- paraphrasing from training data. Ship 6'.a spot-checks + Ship
-- 6'.d preliminary sampling suggests it's working (raw claim rate
-- ~1.3% on 500-char previews; spot-checks accurate). But we
-- currently have no per-turn record of what claims were made or
-- whether the ref cited was in the digest.
--
-- This migration adds passive observability. No enforcement, no
-- auto-repair, no test failures — just a record that Ship 6'.e+
-- can query and alert on if the numbers shift.
--
--   answer_text          : full post-repair answer, capped at 8000
--                          chars (>99% of realistic answers)
--   claim_events         : jsonb array of {ref, verb, snippet,
--                          ref_in_digest, standard_in_scope}
--   claim_events_count   : cardinality for cheap filtering
--
-- The ref_in_digest bool is the interesting field — a TRUE means
-- the LLM cited a ref it had case-file evidence for (safe); a
-- FALSE means the LLM invoked a ref not surfaced in this turn's
-- digest (worth reviewing).

BEGIN;

ALTER TABLE chat_casefile_log
    ADD COLUMN IF NOT EXISTS answer_text        text,
    ADD COLUMN IF NOT EXISTS claim_events       jsonb   NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS claim_events_count integer NOT NULL DEFAULT 0;

COMMENT ON COLUMN chat_casefile_log.answer_text IS
'Ship 6''.d: full post-repair LLM answer, capped at 8000 chars. Feeds the passive claim scanner and any future observability arc. NULL for pre-6''.d rows.';

COMMENT ON COLUMN chat_casefile_log.claim_events IS
'Ship 6''.d: passive claim-scan events. Array of {ref, verb, snippet, ref_in_digest, standard_in_scope}. See [[ship-6-prime-d-claim-scan-observability-2026-07-19]].';

CREATE INDEX IF NOT EXISTS idx_ccfl_claim_events
    ON chat_casefile_log(tenant_id, created_at DESC)
    WHERE claim_events_count > 0;

COMMIT;
