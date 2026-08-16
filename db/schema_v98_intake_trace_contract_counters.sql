-- Ship 74'.a (2026-08-16) — persist FindingContract counters to
-- intake_trace_log.
--
-- The Ship 72' FindingContract SSoT emits per-rejection metrics
-- (`contract_skip_empty_text` / `_pure_scaffolding` /
-- `_mangled_item_id` / `_unresolvable_control_ref`) into
-- `doc.extraction_metrics` during every `.bind()` call. Ship 72'.d's
-- retro claimed these "surface in intake_trace_log automatically" —
-- the Ship 73' dogfood proved that wrong. `doc_pipeline.py::tracer.write()`
-- explicitly lists every persisted column and never forwarded the
-- contract-native counters (or Task #606's pre-existing
-- `templated_zones_scaffolding` / `_mangled` counters, which had the
-- same problem).
--
-- Impact of the gap:
--   Contract rejections landed on the in-memory `ParsedDocument` object
--   during extraction but never reached persistent storage. Silent-drop
--   remained invisible in production traces despite the whole point of
--   the SSoT + metric layer being to make silent-drop observable.
--
-- Fix:
--   6 nullable INT columns on `intake_trace_log`. NULL when the row's
--   pipeline stage didn't touch the contract (all stages other than
--   `extract`); populated by `tracer.write()` from
--   `doc.extraction_metrics` on the `extract` stage.
--
-- No RLS change (intake_trace_log already tenant-scoped). No index —
-- these are aggregation counters, queried by tenant + time, not
-- filtered on directly.

BEGIN;

ALTER TABLE intake_trace_log
  -- FindingContract SSoT native counters (Ship 72'.a / Ship 74'.a)
  ADD COLUMN contract_skip_empty_text              INT NULL,
  ADD COLUMN contract_skip_pure_scaffolding        INT NULL,
  ADD COLUMN contract_skip_mangled_item_id         INT NULL,
  ADD COLUMN contract_skip_unresolvable_control_ref INT NULL,
  -- Backward-compat counters (Task #606 / Ship 72'.a) — same shape as
  -- Ship 72'.d retro described but never wired.
  ADD COLUMN templated_zones_scaffolding INT NULL,
  ADD COLUMN templated_zones_mangled     INT NULL;

COMMENT ON COLUMN intake_trace_log.contract_skip_empty_text IS
  'Ship 74''.a — count of ExtractedCandidate.bind() calls this extract '
  'stage rejected as EMPTY_TEXT. NULL for non-extract stages.';

COMMENT ON COLUMN intake_trace_log.contract_skip_pure_scaffolding IS
  'Ship 74''.a — bind() rejections as PURE_SCAFFOLDING '
  '(FindingContract.is_scaffolding predicate matched).';

COMMENT ON COLUMN intake_trace_log.contract_skip_mangled_item_id IS
  'Ship 74''.a — bind() rejections as MANGLED_ITEM_ID '
  '(catalog_recognises returned False for the candidate.item_id). '
  'Task #606 defence against tenant-mangled markers.';

COMMENT ON COLUMN intake_trace_log.contract_skip_unresolvable_control_ref IS
  'Ship 74''.a — bind() rejections as UNRESOLVABLE_REF '
  '(item_control_ref failed to derive a control_ref).';

COMMENT ON COLUMN intake_trace_log.templated_zones_scaffolding IS
  'Ship 74''.a — Task #606 pre-existing counter, now persisted. '
  'Union of PURE_SCAFFOLDING + EMPTY_TEXT contract rejections in '
  'templated edit-zone paths (backward-compat mapping preserved by '
  'Ship 72''.a extractor.py wiring).';

COMMENT ON COLUMN intake_trace_log.templated_zones_mangled IS
  'Ship 74''.a — Task #606 pre-existing counter, now persisted. '
  'Number of edit-zone binding markers (`<<MUST item:X>>` /'
  '`<<SHOULD item:X>>`) that failed catalog_recognises on this doc — '
  'typically indicates tenant edited the marker directly or a mapping '
  'YAML typo.';

COMMIT;
