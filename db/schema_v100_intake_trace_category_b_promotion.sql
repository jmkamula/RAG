-- Ship 74'.d (2026-08-16) — promote 18 category-B counters from
-- Ship 74'.c's `_INTENTIONAL_DEBUG_ONLY` grandfather set to persisted
-- columns on intake_trace_log.
--
-- Ship 74'.c catalogued 25-ish keys that producers set on
-- `doc.extraction_metrics` but never forwarded to the tracer. Some are
-- genuinely inline (nested dicts, decision aids) — those stay in the
-- debug-only set. The rest are counters with real auditor value that
-- just never got a schema column. Ship 74'.d turns 18 of them into
-- proper trace columns.
--
-- Scope selection: highest-value counters that most directly answer
-- "what did extraction see, keep, and drop?"
--
--   Critic telemetry (7)  — Ship 11'.d critic priming + outcomes.
--                            Shows how much the critic-verifier moved
--                            candidates.
--   Filter drops (2)      — Ship 11'.c/d content-shape + semantic-fit
--                            gates. Tuning signal for gate thresholds.
--   Fingerprint yield (2) — deterministic-path recall. Peer to the
--                            already-persisted `distinct_musts_bound`.
--   Classifier gate (3)   — Ship 11'.c classifier + fingerprint
--                            overlap. Explains why some leaves ran
--                            through the LLM and others didn't.
--   Templated yield (4)   — templated fast-path pass-through counts.
--                            First-order surface for templated-doc
--                            round-trip debugging.
--
-- Deferred to a later arc (still in Ship 74'.c debug-only):
--   Templated table-zone counters (5) — narrow observability.
--   Templated xlsx per-leaf detail (7) — narrow observability + 2 TEXT.
--
-- All columns nullable INT — populated only on the `extract` stage row.

BEGIN;

ALTER TABLE intake_trace_log
  -- Critic telemetry (Ship 11'.d)
  ADD COLUMN critic_priming_size    INT NULL,
  ADD COLUMN critic_pool_size       INT NULL,
  ADD COLUMN critic_confirmed_raw   INT NULL,
  ADD COLUMN critic_extended_raw    INT NULL,
  ADD COLUMN critic_rejected        INT NULL,
  ADD COLUMN critic_flagged_missing INT NULL,
  ADD COLUMN critic_findings_kept   INT NULL,
  -- Filter drops (Ship 11'.c/d)
  ADD COLUMN dropped_content_shape  INT NULL,
  ADD COLUMN dropped_semantic_fit   INT NULL,
  -- Fingerprint deterministic-path yield
  ADD COLUMN fingerprint_findings         INT NULL,
  ADD COLUMN fingerprint_covered_leaves   INT NULL,
  -- Classifier gate (Ship 11'.c)
  ADD COLUMN leaves_dropped_by_classifier INT NULL,
  ADD COLUMN leaves_fingerprint_hit       INT NULL,
  ADD COLUMN leaves_unfingerprinted_kept  INT NULL,
  -- Templated fast-path yield
  ADD COLUMN templated_findings            INT NULL,
  ADD COLUMN templated_xlsx_findings       INT NULL,
  ADD COLUMN templated_edit_zones_total    INT NULL,
  ADD COLUMN templated_edit_zones_bound    INT NULL;

COMMENT ON COLUMN intake_trace_log.critic_priming_size IS
  'Ship 74''.d — Ship 11''.d critic priming set size at the pass-1 boundary.';
COMMENT ON COLUMN intake_trace_log.critic_pool_size IS
  'Ship 74''.d — Ship 11''.d critic candidate pool size after prefilter.';
COMMENT ON COLUMN intake_trace_log.critic_confirmed_raw IS
  'Ship 74''.d — critic-verifier ``confirmed`` bucket count (pre-filter).';
COMMENT ON COLUMN intake_trace_log.critic_extended_raw IS
  'Ship 74''.d — critic-verifier ``extended`` bucket count (pre-filter).';
COMMENT ON COLUMN intake_trace_log.critic_rejected IS
  'Ship 74''.d — critic-verifier explicit reject count.';
COMMENT ON COLUMN intake_trace_log.critic_flagged_missing IS
  'Ship 74''.d — critic-verifier ``flagged_missing_control`` count.';
COMMENT ON COLUMN intake_trace_log.critic_findings_kept IS
  'Ship 74''.d — findings retained after critic-verifier applies gates.';

COMMENT ON COLUMN intake_trace_log.dropped_content_shape IS
  'Ship 74''.d — Ship 11''.c content-shape filter drop count '
  '(pruned by looks_like_field_or_header MUST-aware predicate).';
COMMENT ON COLUMN intake_trace_log.dropped_semantic_fit IS
  'Ship 74''.d — Ship 11''.d post-critic embedding-cosine semantic-fit '
  'gate drop count.';

COMMENT ON COLUMN intake_trace_log.fingerprint_findings IS
  'Ship 74''.d — deterministic fingerprint-path findings emitted on '
  'this doc (peer to `distinct_musts_bound`).';
COMMENT ON COLUMN intake_trace_log.fingerprint_covered_leaves IS
  'Ship 74''.d — distinct leaves the fingerprint path bound at least '
  'one MUST for.';

COMMENT ON COLUMN intake_trace_log.leaves_dropped_by_classifier IS
  'Ship 74''.d — Ship 11''.c classifier gate: leaves the classifier '
  'ruled out before extraction even attempted them.';
COMMENT ON COLUMN intake_trace_log.leaves_fingerprint_hit IS
  'Ship 74''.d — leaves the fingerprint-path already covered (no LLM '
  'attempt needed).';
COMMENT ON COLUMN intake_trace_log.leaves_unfingerprinted_kept IS
  'Ship 74''.d — leaves that survived the classifier but had no '
  'fingerprint match — the LLM extraction attempts these.';

COMMENT ON COLUMN intake_trace_log.templated_findings IS
  'Ship 74''.d — templated markdown fast-path findings on this doc.';
COMMENT ON COLUMN intake_trace_log.templated_xlsx_findings IS
  'Ship 74''.d — templated xlsx (Excel round-trip) fast-path findings.';
COMMENT ON COLUMN intake_trace_log.templated_edit_zones_total IS
  'Ship 74''.d — total ▽/△ edit zones detected across the doc.';
COMMENT ON COLUMN intake_trace_log.templated_edit_zones_bound IS
  'Ship 74''.d — templated edit zones whose contents bound as findings.';

COMMIT;
