---
name: feedback-eval-with-each-feature
description: Every user-facing change to the RAG pipeline must extend tests/eval_suite.py in the same commit — no feature ships without an EvalCase that would have failed before the change
metadata: 
  node_type: memory
  type: feedback
  originSessionId: fc213bac-393a-4fc0-b0cf-eaccbffc7f60
---

When implementing a new feature, bug fix, or behaviour change in the
ArionComply RAG pipeline (classifier, resolver, llm_answer, graph_expander,
intake, etc.), add at least one `EvalCase` to `tests/eval_suite.py` in the
same commit. The case must be one that would have failed before the change
and passes after — so a regression silently breaks the eval rather than
silently slipping through.

**Why:** the eval suite is the only repeatable behaviour gate ("21/21 PASS
before any restart" — see CLAUDE.md). If the suite never grows, every new
feature becomes untested as soon as the manual smoke-test is forgotten. The
A.6.4 cited-ref bug in `_resolve_posture_status` is the canonical example:
commit 0b55716 fixed three sibling handlers but missed POSTURE_STATUS, and
no eval case caught it for nearly a day.

**How to apply:**
- Before claiming a feature/fix is done, write the EvalCase first or
  alongside the code. Use `expected_refs`, `forbidden_refs`,
  `must_contain`, `must_not_contain`, `min_findings`, `expected_type` —
  whichever combination locks in the change.
- Run the full suite (`python3 tests/eval_suite.py`) and report N/N PASS,
  not just "the new case passes". Regressions in other cases count.
- Re-use existing taxonomy tags (`gap`, `posture`, `documents`, `cross_framework`,
  `definition`, `scope`, `na`, `software`, `audit`, `ir`) and add new ones
  (`xfw_inheritance`, `cited_ref`, `incident_obligations`, etc.) when a
  feature warrants a new dimension.
- The case lives in the same PR/commit as the implementation — not "a
  follow-up". Follow-ups never land.

See also: [[user-role]], [[human-in-the-loop-positioning]]

## Stage-2 ratchet-fatigue — deferred shape-match helper

Cases of the form `pending engine verdict for X` are state-sensitive:
every Stage-2 approval (or Stage-1 approval that triggers an engine-
kick producing a Stage-2 proposal) shifts the chat surface from
"engine proposes ... 0/N" → "engine proposes ... 1/N" → "already
approved ... 'OFI'" → eventually "already approved ... 'Comply'".
Tenant action churn = constant re-ratcheting.

On 2026-06-09 we ratcheted the same 9 cases (A.5.16, A.5.17,
A.5.19, A.5.23, A.8.2, A.8.5, Art.18, Art.21, Art.46) **twice in
one day**: once when the engine-kick proposed OFI, once again when
Stage-2 approved. That's the strongest signal so far that the
strict-string `must_contain` model doesn't scale for state-sensitive
queries.

**The deferred fix** (proposed + accepted then parked 2026-06-09):
ship `assert_stage2_shape(ref, response)` accepting ANY valid post-
engine state (`already approved` ∨ `engine proposes X` ∨ `no pending
verdict`) and additionally verifying internal consistency (if
"engine proposes" then a finding label + `N/M children satisfied`
must be present). Loose enough to survive evidence churn, strict
enough to catch real regressions (clarification loops, no-spec
errors, malformed multi-leaf math). ~50 cases would convert.

Until then: ratchet when state shifts, expect to do it again. The
ratchet shape today is `[ref, "already approved", "'OFI'"]` —
literal single-quoted form pins the chat's `Live finding: 'OFI'`
output.
