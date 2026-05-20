---
name: applies-when-phase1-regression-tests
description: Phase-1 applies_when contract (NULL=always-applies, False=NotApplicable, edge-False=skip+footnote, Phase-2=eval-reject, ""=LexError) — locked in regression tests on 2026-05-20
metadata: 
  node_type: memory
  type: project
  originSessionId: ab2912f3-a587-4819-891f-14d62eba574c
---

**Status: locked.** Phase-1 contract committed 2026-05-20 (76d6bc5) — 31 DSL tests in `tests/test_applies_when.py`, 20 engine tests in `tests/test_fulfilment_engine.py`. The first curator to write an `applies_when` expression will exercise paths that are protected by these tests; a regression now fails CI rather than mis-evaluating a real rule.

**Why:** The `NotApplicable` verdict path in `fulfilment_engine.py` and the edge-skip path were dead code before — the regression suite was the cheap insurance against the first real rule landing on a broken engine.

**Contract pinned by the tests:**
- (a) `applies_when IS NULL` short-circuits to "always applies" at both spec and edge level (`test_spec_level_applies_when_NULL_always_applies`, `test_edge_level_applies_when_NULL_always_applies`).
- (b) spec-level `applies_when` returning False ⇒ `NotApplicable` verdict, no leaves walked (`test_spec_level_applies_when_false_is_NotApplicable`).
- (c) edge-level `applies_when` returning False ⇒ leaf skipped, not a gap, BUT counts toward the `, N gated off by applies_when` footnote in `ControlVerdict.reason` — and the footnote is absent when nothing is gated (`test_edge_level_applies_when_false_skips_leaf`, `test_edge_level_applies_when_false_appears_in_reason_footnote`, `test_no_gated_edges_omits_footnote`).
- (d) Phase-2 reservations (`fact_value`, `register_count`, `date_after`) parse cleanly to `FuncCall` but raise `EvalError` mentioning "Phase 2" at evaluate time (`test_parse_phase2_funcs_parse_cleanly`, `test_eval_phase2_rejected`, `test_eval_phase2_register_count_rejected`, `test_eval_phase2_date_after_rejected`).
- (e) Empty applies_when string raises `LexError` — at the DSL boundary AND propagated through the engine at both spec and edge level (`test_lex_empty_source_rejected`, `test_empty_applies_when_string_propagates_LexError`, `test_empty_edge_applies_when_string_propagates_LexError`).

**How to apply:** Any change to `rag/posture/applies_when.py` or `rag/posture/fulfilment_engine.py` must keep these tests passing. If the contract needs to change (e.g. Phase 2 work converts a reservation to a real function), update the locked tests in the same commit so the new contract is what's pinned — never silently delete a contract test. The ER:&lt;leaf&gt; resolver gap is locked separately in `tests/test_engine_runner_resolver.py`. The driver-level warning suppression for `01N52` is still pending — see [[applies-when-warning-suppression]].

Related: [[applies-when-warning-suppression]], [[feedback-eval-with-each-feature]].
