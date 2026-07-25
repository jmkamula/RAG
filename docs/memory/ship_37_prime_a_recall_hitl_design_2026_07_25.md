---
name: ship-37-prime-a-recall-hitl-design-2026-07-25
description: "Ship 37'.a — design memo for the recall HITL investigation. Ship 36 dropped 502 candidates via the no-excerpt-auto-drop invariant; Ship 37 samples 20-30 of them and manually classifies correctly-dropped / should-have-accepted / uncertain. Determines whether the aggressive invariant ships or needs relaxation. Mirror shape of Ship 34'.c (which sampled arbiter-zone rejects); different population (invariant drops)."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 37'.a — opens Ship 37 arc (recall HITL on the invariant's
drops). Ship 36'.c retro codified a big surprise: the
no-excerpt-auto-drop invariant reduces accepts from Ship 33's
shadow 197 → 33 real. 164 previously-accepted candidates now drop
because they had scope-signal-only corroboration with no
fingerprint excerpt.

The question Ship 37 answers: **are those 164 (and the broader
502) drops CORRECTLY dropped (auditor-friendly precision gain),
or are some SHOULD-HAVE-ACCEPTED (recall loss on legitimate
evidence)?**

## Sampling design

**Target population**: candidates that Ship 36 dropped BECAUSE
of the no-excerpt-auto-drop invariant. Defined as:
- `verdict='drop'` in Ship 36 real cutover
- `fingerprint_excerpt=None` (or empty)
- Score ≥ arbiter_floor (0.40) — meaning the aggregator would
  have routed them to arbiter or accept WITHOUT the invariant

Distinct from generic drops (score < 0.40 which drop anyway,
regardless of invariant).

**Sample size**: 20-25, stratified across the 5 re-extracted
docs. Random-seeded for reproducibility (matches Ship 34'.c
seed=42 approach).

**Sampling mechanism**: existing `intake_consensus_log.candidates_sample`
JSONB is biased toward top-scoring drops (with excerpts). The
invariant's targets are lower-scoring no-excerpt drops that
aren't in that sample. Need a supplementary script:
`scripts/dump_ship37_recall_sample.py` that:
1. Runs consensus on each of the 5 docs WITH LLM arbiter DISABLED
   + WITHOUT the invariant (i.e. the pre-invariant behavior)
2. Identifies candidates that:
   - Would be accepted OR arbiter under old rules
   - Have no fingerprint_excerpt
3. Samples 4-5 per doc (stratified)
4. Emits per-candidate record with:
   - leaf_id, must_id, control_ref, standard_id
   - MUST canonical text (from Neo4j)
   - Signals that fired (which scope signals put it above floor)
   - Score under old aggregator
   - No excerpt (that's the criterion)
5. Also dumps first ~2000 chars of the doc + topic_tokens for
   the reviewer to search for evidence

## Classification criteria

For each sampled candidate, reviewer decides one of:

- **Correctly dropped** — the doc does NOT actually address
  this MUST. The scope signals voted "leaf is in-scope" but
  that's a scope-family match (e.g. Art.28 is on-topic for a
  processor doc) that doesn't mean the specific MUST is
  addressed. Ship 34'.c pattern: 20/20 correctly rejected.
- **Should have accepted** — the doc DOES address this MUST
  in substance, but the fingerprint keyword set didn't fire.
  This is a fingerprint-catalog gap (Ship 28+29 didn't add
  the right keywords for this MUST). Recall loss.
- **Uncertain** — reviewer can't tell without deeper doc read.

## Validation thresholds

Mirror of Ship 34'.c bands:

- **≥ 80% correctly-dropped** → invariant validated for
  production; aggressive shape ships as-is; Ship 38+ moves to
  other work.
- **60-80% correctly-dropped** → invariant is directionally
  right but needs relaxation. Options:
  - Raise the drop threshold: only drop no-excerpt candidates
    with score < some higher threshold (e.g. 1.2), keep
    higher-score ones as scope indicators
  - Adjust signal weights so scope signals don't push
    candidates above accept_floor without evidence support
  - Ship 38 designs the relaxation.
- **< 60% correctly-dropped** → invariant is over-aggressive;
  substantial recall loss on legitimate evidence. Options:
  - Retire the invariant + rely on LLM arbiter (returns to
    Ship 33'.c v4 shape: 197 accepts, ~$0.05/doc arbiter cost)
  - Fix the fingerprint catalog gaps that caused the recall
    loss (curator arc)
  - Add LLM discovery pass as 9th signal (bigger arc — Ship
    35 already had this as follow-on)

## What Ship 37 does NOT do

- **Fix any recall loss found** — Ship 37 is diagnosis, not
  fix. If HITL surfaces significant recall loss, Ship 38 does
  the relaxation.
- **HITL of accepted findings** — Ship 34'.c reviewed arbiter
  rejects; Ship 37 reviews invariant drops. Neither has
  reviewed the ACCEPTED set. A future arc could sample the
  33 accepts to confirm precision.
- **Flip flag off** — flag stays ON on demo regardless of Ship
  37 finding; Ship 38+ decides based on HITL data whether to
  relax invariant + re-flip.
- **Re-run measurement** — Ship 36'.b's numbers stand;
  Ship 37 is orthogonal (samples the drops).

## Sub-arc plan

| Sub-arc | Focus | Outcome |
|---|---|---|
| **37'.a** (this) | Design memo | Sample size + classification criteria + thresholds locked |
| 37'.b | Dump script + 20-25 candidate sample + classify | Correctly-dropped rate reported |
| 37'.c | Eval + retro + invariant verdict | Ship / relax / retire decision codified |

## Related

- [[ship-36-prime-arc-retrospective-2026-07-25]] — the arc
  whose invariant this HITL validates
- [[ship-34-prime-arc-retrospective-2026-07-25]] — the mirror-
  shape HITL on arbiter rejects (20/20 correct-reject); Ship
  37 uses same sampling + thresholds discipline
- [[ship-35-prime-arc-retrospective-2026-07-25]] — the cutover
  arc where the invariant was designed + shipped
