---
name: feedback-validate-the-denominator
description: "RULE: validate the denominator of any ratio metric BEFORE building infrastructure on it. A flawed denominator can make a moderate problem look catastrophic. Surfaced 2026-06-26 by the LLM-under-discovery arc: I anchored hours of work on a 30-minute query reporting 17% median yield; the real per-leaf yield was 57%, and oracle ground-truth found ~0-6% real extraction failures vs. 94-100% real-evidence-gaps."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## Rule

**Before building infrastructure on a ratio metric, ground-truth the
denominator.** Especially when the ratio is small / alarming. Ask:

1. What's the universe the denominator is counting?
2. Is that the right universe for the question I'm trying to answer?
3. Can I spot-check 2-3 items at the extremes (smallest ratio) and
   confirm the failure is the one I think it is?

If any of those is shaky, the metric isn't trustworthy enough to act on.

## Why

The 2026-06-26 LLM-narrative-under-discovery arc consumed most of a
session on what turned out to be a non-problem (or a 5%-of-claimed
problem). The chain:

- 30-min audit query computed `bound / total_catalog_MUSTs_per_control`
  → median 17%
- Anchored on "17%" as evidence of widespread LLM under-discovery
- Shipped: schema_v48 telemetry (5 columns), MUST embedding index
  (4133 vectors), Phase 2 prototype, audit memo, multiple commits
- Phase 2 prototype returned 0 grounded findings → "must be the
  prompt" → debugging
- Eventually computed `bound / MUSTs_in_touched_leaves` → median
  **57%**
- Oracle ground-truth on lowest-yield docs → **0-6% real extraction
  failures**; 94-100% are real-evidence-gaps (wrong doc type uploaded
  for the missing MUSTs)
- Conclusion: the gap at the magnitude originally claimed didn't exist

The denominator bug was: control has multiple leaves; doc usually
covers one or two. Summing across ALL leaves of the control inflates
the denominator 2-5x for multi-leaf controls. The right denominator
is **MUSTs of leaves the doc actually addresses**.

## How to apply

When a ratio metric motivates new infrastructure, do this first
(should take ≤30 minutes):

1. **Pick 2-3 specimens at the extremes** (smallest ratio cases).
   Compute their numerator + denominator by hand.
2. **Ask: is the denominator the right universe?** For "yield"
   metrics, are you counting things that COULD reasonably be in the
   numerator's source? For "coverage" metrics, are you counting things
   actually in scope?
3. **Spot-check the failure mode**. If the ratio says "X is missing
   Y", manually verify Y is *expected to be* in X. The semantic-search
   arc was built to fix "LLM missed evidence"; a 5-minute oracle test
   showed the evidence was never in the doc to begin with.
4. **Only then** build infrastructure on the metric.

**Oracle tests are cheap.** A single LLM call with full-doc context +
the candidate gap can definitively distinguish "real extraction
failure" from "real evidence gap". Run it BEFORE shipping extraction
fixes; if it returns "not in doc" most of the time, the fix isn't
extraction.

## Related

- [[llm-narrative-under-discovery-audit-2026-06-26]] — the arc where
  this lesson surfaced. The audit memo's "G3-G6 gap catalog" was
  built on the bad denominator; superseded.
- [[feedback-telemetry-before-trouble]] — adjacent lesson: instrument
  absence, not just rejection. Both lessons say: think carefully about
  what's actually being measured before treating the number as ground
  truth.
- [[feedback-anchor-before-choices]] — adjacent style lesson: give
  the user the framing before asking them to pick. Today the user
  caught the wrong direction by asking "is this getting us
  anywhere?" — they should have had the framing earlier.
