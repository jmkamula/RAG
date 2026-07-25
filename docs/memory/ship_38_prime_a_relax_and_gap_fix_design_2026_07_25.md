---
name: ship-38-prime-a-relax-and-gap-fix-design-2026-07-25
description: "Ship 38'.a — design memo for the two-pronged remedy the Ship 37 HITL diagnosed. Relax the no-excerpt-auto-drop invariant so high-corroboration candidates escape to arbiter zone; targeted curator fix on the 6 HITL should-have-accepted proc_* fingerprints (add doc-prose verb-pattern keywords). Re-measure the 5-doc corpus expecting 60-100 accepts (middle path between too-aggressive 33 and too-permissive 197)."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 38'.a — opens Ship 38 arc. Ship 37'.c HITL diagnosed the
Ship 36 invariant as directionally right but too aggressive — 6 of
25 should-have-accepted (52%/24%/24%). All 6 SHOULD-HAVE-ACCEPTED
cases share a shape: `proc_*` procedure-MUSTs on docs where the
MUST is the primary subject. The current fingerprint keywords are
description-vocabulary derived (auto-generated from MUST
description text) and don't match the doc's actual prose.

Two-pronged remedy per user direction: "relax and fix the gap? then
test."

## Part 1 — Invariant relaxation

**Current** (Ship 35'.b `aggregator.py`):
```python
if not excerpt and cfg.no_excerpt_auto_drop:
    verdict = "drop"
elif score >= cfg.accept_floor and corrob >= cfg.min_corroborators:
    verdict = "accept"
elif score >= cfg.arbiter_floor:
    verdict = "arbiter"
else:
    verdict = "drop"
```

**Proposed** (Ship 38'.b): add escape clause — no-excerpt candidates
with STRONG corroboration escape to arbiter (LLM decides), instead
of hard-drop.

```python
if not excerpt and cfg.no_excerpt_auto_drop:
    if (score >= cfg.no_excerpt_escape_score
            and corrob >= cfg.no_excerpt_escape_corrob):
        verdict = "arbiter"   # let LLM decide the strong-scope case
    else:
        verdict = "drop"       # weak-scope-only drops directly
elif ...
```

New config values (proposal):
```python
no_excerpt_escape_score:  float = 1.5   # roughly 2 strong signals
no_excerpt_escape_corrob: int   = 3     # or 1 strong + 2 medium
```

**Impact on Ship 37 HITL sample**:
- 4 of 6 should-have-accepted cases had score ≥ 1.5 + corrob ≥ 3 →
  under relaxation these escape to arbiter (where LLM decides;
  Ship 34 showed 20/20 LLM-correct at that layer)
- The other 2 had lower scores (score=1.1 corrob=2 and score=0.4
  corrob=2) → still drop
- Correctly-dropped cases were mostly single-signal (corrob=1 or 2)
  at score 0.6-0.7 → still drop cleanly

**Predicted outcome**: 4 of 25 HITL candidates escape to arbiter;
LLM likely accepts most (since they're primary-subject MUSTs).
Ship 38 measurement will show ~4-8 more accepts per doc on the
5-doc corpus.

## Part 2 — Curator fix on the 6 HITL-surfaced proc_* fingerprints

**Target MUSTs** (from Ship 37 HITL):

| MUST | Doc | Current keyword shape |
|---|---|---|
| `item:A.7.4.3:proc_inaccuracy_response` | DQA | `[inaccuracy, response, accuracy]` — description-derived |
| `item:A.7.4.3:proc_inaccuracy_prevention` | DQA | `[inaccuracy, prevention, accuracy]` — description-derived |
| `item:A.7.2.5:reg_signoff` | DPIA | register-shape (correct for the leaf; DPIA doc might not have register rows) |
| `item:Art.35:trigger_criteria` | DPIA | needs check |
| `item:Art.35:dpo_advice` | DPIA | needs check |
| `item:B.8.2.2:proc_technical_binding` | Processor Ops | needs check |

**Curator process per MUST**:
1. Read the actual doc text (200-500 chars around where the topic
   is naturally discussed)
2. Extract 3-5 distinctive verb-driven phrases the doc uses
3. Add those as new `excerpt_keywords` sets in the fingerprint YAML
4. Preserve the existing description-derived sets (they might match
   other docs' vocabulary)

**Example — DQA doc + `proc_inaccuracy_response`**:
- Doc uses: "responds to inaccuracy reports", "when inaccuracy is
  identified", "correction workflow", "flagged by customer or
  internal review"
- Add keyword sets:
  - `[respond, inaccuracy, report]`
  - `[identify, inaccuracy]`
  - `[correction, workflow]`
  - `[customer, flag]`

## Part 3 — Measurement

Re-run `scripts/measure_ship33_consensus.py` (already extended
with two-pass logic) to compare:

| Corpus point | Accepts | Arbiter | LLM cost |
|---|---|---|---|
| Ship 32 Path A (existing) | 272 | — | ~$0.24/doc |
| Ship 33 v4 shadow (invariant off, arbiter on) | 197 | 0 (LLM decided 94) | ~$0.05/doc |
| Ship 36 real (invariant on) | 33 | 0 | ~$0/doc |
| **Ship 38 target** | **60-100** | small | ~$0.02-0.05/doc |

Success:
- ✅ Accept count in 60-100 range (middle path)
- ✅ 4+ of the 6 Ship 37 should-have-accepted MUSTs now surface
  (via curator fix or via arbiter escape)
- ✅ Correctly-dropped MUSTs (Ship 37's 13) STAY dropped
- ✅ Chat unaffected (baseline eval holds)
- ✅ Cost per doc under $0.10 (still deterministic-dominant)

Failure:
- ❌ Accept count > 150 (over-permissive; relaxation too broad)
- ❌ Accept count < 40 (curator fix didn't catch enough; invariant
  still too tight)
- ❌ HITL re-verify shows correctly-dropped cases now escape
  (relaxation broke discrimination)

## Sub-arc plan

| Sub-arc | Focus | Outcome |
|---|---|---|
| **38'.a** (this) | Design memo | Relaxation + curator scope + measurement plan locked |
| 38'.b | Implement + curator + re-measure | Numbers on the 5-doc corpus |
| 38'.c | HITL re-verify (small sample) + eval + retro | Combined cutover shape ships / iterates |

## What Ship 38 does NOT do

- **Broad curator arc** — targets only the 6 HITL-surfaced MUSTs;
  broader `proc_*` catalog audit is a separate arc if needed
- **Retire the invariant** — relaxation, not retire
- **Change signal weights** — weights stay from Ship 35'.b
- **Add new signals** — LLM discovery pass as 9th signal deferred

## Related

- [[ship-37-prime-arc-retrospective-2026-07-25]] — the HITL arc
  that motivated this remedy
- [[ship-36-prime-arc-retrospective-2026-07-25]] — the cutover
  arc whose invariant is being relaxed
- [[ship-34-prime-arc-retrospective-2026-07-25]] — the arbiter
  HITL (20/20) that validates escape-to-arbiter as safe
