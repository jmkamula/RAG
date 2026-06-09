-- schema_v36 — track the top doc_mappings match's target list size
-- separately from the union of all matches.
--
-- candidate_controls (schema_v35) records the UNION of every
-- doc_mappings match's target_leaves — i.e. everything sent to the
-- LLM. For broad-shape docs (e.g. "HR Security Policy.docx" matched
-- 50 controls because the filename triggers many policy-umbrella
-- fingerprints), this denominator inflates the yield-ratio yellow
-- gate even when extraction is healthy (9/50 = 18% would flag yellow
-- despite 9 substantive findings).
--
-- primary_candidate_controls records the TOP-CONFIDENCE match's
-- target list only — the "tight target scope" the umbrella mapping
-- was authored to cover. Used as the yield-ratio denominator in
-- _extraction_quality_flag; the union still records what was sent
-- to the LLM for cost/perf tracking.
--
-- Surfaced 2026-06-09 by HR Security Policy.docx flagging yellow at
-- 9 findings / 50 candidates while the umbrella match was clearly
-- being hit (9 findings on relevant HR controls).

ALTER TABLE intake_trace_log
    ADD COLUMN IF NOT EXISTS primary_candidate_controls INTEGER;
