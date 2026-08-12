---
name: feedback-no-stochastic-cases
description: "'Stochastic' is not an acceptable category. When an eval case intermittently fails, root-cause it. The failure is almost always a deterministic bug — a naive substring, a bad prompt slot, a data-shape assumption — not LLM noise."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

When an eval case intermittently fails, do NOT label it "known-flaky
LLM stochasticity" and move on. Investigate and fix the underlying
defect.

**Why:** Ship 60'.k root-caused a case #1 failure that had been
tagged "stochastic physical-leak" for weeks. The actual root cause
was a naive substring check in `tests/eval_suite.py:4875` —
`if ref in answer:` — that false-positive-matched `A.7.1` inside
`A.7.1.5` (a legitimately relevant ISO 27701 sub-control on a
27701-enrolled tenant answering an access-rights query). Every
"stochastic" run was actually a deterministic collision fired by
whether the LLM cited an ISO 27701 sub-clause that shared a prefix
with the forbidden ref. Fixed with a word-boundary + negative-lookahead
pattern (`re.escape(ref) + r'(?!\.\d)'`).

Two more historical examples (recorded in the CLAUDE.md eval notes):
- Case #21 was tagged "LLM-stochastic" until Ship 1 (9443aeb) traced
  it to a 60-second LLM timeout + verify-correct-loop truncating at
  1500 tokens. Fix: skip verify+correct for implementation queries +
  raise timeout to 180s.
- Case #24 Art.32 bridge was called stochastic until Ship 1.14
  proved the LLM was stochastically dropping the bridge footer.
  Fix: deterministic bridge footer append after LLM response.

**How to apply:**
- When an eval case fails intermittently, treat it like any
  production bug: reproduce, diagnose, fix the root cause.
- Common latent bugs behind "stochastic" labels:
  - Substring collisions in assertion matchers (word-boundary fix)
  - Timeouts too tight for a specific class of queries
  - Post-hoc processing steps that stochastically drop content
    (fix: append deterministically after LLM output)
  - Prompt slots that vary in a way the LLM's cadence exposes
- If you truly believe an LLM behavior is stochastic (paraphrasing
  in prose that hits a strict-string assertion), the fix is usually
  to relax the assertion to structural shape (see
  [[feedback-eval-state-drift]]) OR add a deterministic post-process
  that guarantees the required content — never accept the FAIL.
- CLAUDE.md rule: "'LLM-stochastic' is not an acceptable category —
  it usually hides a real infra defect. Root-cause intermittent
  failures rather than hedging assertions."
