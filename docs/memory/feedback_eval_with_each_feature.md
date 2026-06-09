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

## Stage-2 ratchet-fatigue — SHIPPED 2026-06-09 (376628d + 4eba6ff)

Cases of the form `pending engine verdict for X` are state-sensitive
(pending → approved → re-proposed). Strict-string `must_contain`
required re-ratcheting on every state shift; two ratchets in one
session on the same 9 cases proved the cost wasn't sustainable.

**The fix:** EvalCase.shape="stage2" + `_check_stage2_shape()`
validator that accepts ANY valid post-engine state and verifies
internal consistency. All 157 Stage-2 cases converted; eval 194/198
with no Stage-2 regressions.

Full design + usage: [[eval-shape-validators]]. New Stage-2 cases
should default to `shape="stage2"`, leave `must_contain=[]`.
