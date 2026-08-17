-- Ship 78'.d (2026-08-17) — promote Ship 78'.b union-extractor metrics
-- from Ship 74'.c grandfather set to persisted intake_trace_log columns.
--
-- Ship 78'.b introduced 3 metrics on doc.extraction_metrics:
--   union_from_consensus  — count of findings emitted by consensus path
--   union_from_critic     — count of findings emitted by critic path
--   union_deduped_count   — findings dropped by (control_ref, must_id)
--                            dedup at union merge time
--
-- These are the canonical Ship 78' observability surface. Without them
-- in intake_trace_log, we can't answer "how much did each path
-- contribute?" or "how many duplicates did the union dedup catch?"
-- for a given upload. Ship 74'.c drift-guard flagged them; Ship 78'.d
-- promotes them alongside the eval + dogfood work.
--
-- No RLS change (intake_trace_log already tenant-scoped). No index —
-- these are aggregation counters queried by tenant + time, not
-- filtered on directly.

BEGIN;

ALTER TABLE intake_trace_log
  ADD COLUMN union_from_consensus INT NULL,
  ADD COLUMN union_from_critic    INT NULL,
  ADD COLUMN union_deduped_count  INT NULL;

COMMENT ON COLUMN intake_trace_log.union_from_consensus IS
  'Ship 78''.d — number of findings emitted by consensus path on this '
  'extract stage. NULL when consensus was disabled '
  '(USE_CONSENSUS_EXTRACTION=critic_only) or the union code path didn''t '
  'execute (e.g. templated fast-path).';

COMMENT ON COLUMN intake_trace_log.union_from_critic IS
  'Ship 78''.d — number of findings emitted by critic-verifier path on '
  'this extract stage. NULL when critic was disabled '
  '(USE_CONSENSUS_EXTRACTION=consensus_only) or union code path didn''t '
  'execute.';

COMMENT ON COLUMN intake_trace_log.union_deduped_count IS
  'Ship 78''.d — findings dropped by (control_ref, checklist_item_id) '
  'dedup at union merge time. Formula: '
  'union_from_consensus + union_from_critic - final_findings_count. '
  'Non-zero means both paths hit the same MUST for at least one finding.';

COMMIT;
