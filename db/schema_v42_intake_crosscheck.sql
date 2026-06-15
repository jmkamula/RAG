-- schema_v42 — extractor↔catalog crosscheck telemetry.
--
-- Post-B (commit 307dbdc, 2026-06-15), the extractor emits findings
-- with checklist_item_id when doc_mappings narrows to specific leaves
-- and the LLM picks a MUST id from the per-control candidate list.
-- Validating the id against the valid set (B) catches hallucinated
-- ids but doesn't catch SEMANTIC misalignment — the LLM picks a
-- legitimate MUST id whose intent doesn't match its own evidence quote.
--
-- The crosscheck (commit-after-this) tests each (must_id, evidence)
-- pair against the must_fingerprints catalog's keyword sets for that
-- MUST. Disagreement = LLM and catalog don't agree the evidence
-- satisfies this MUST.
--
-- Soft signal: disagreement does NOT drop the binding (autogen
-- catalogs are noisy enough that hard drops would lose real
-- bindings). Counter accumulates; quality dashboard surfaces.

ALTER TABLE intake_trace_log
    ADD COLUMN IF NOT EXISTS crosscheck_disagreements INTEGER,
    ADD COLUMN IF NOT EXISTS crosscheck_confirmed     INTEGER,
    ADD COLUMN IF NOT EXISTS crosscheck_unavailable   INTEGER;
