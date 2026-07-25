---
name: ship-36-prime-arc-retrospective-2026-07-25
description: "Ship 36' arc closer — first real cutover test on Arion demo tenant. USE_CONSENSUS_EXTRACTION=1 flipped; all 5 baseline docs re-extracted via the real API endpoint; 5 intake_consensus_log rows landed; chat spot-check clean. Big surprise finding: the Ship 34-motivated no-excerpt-auto-drop invariant is much more aggressive than Ship 35 design predicted — collapses total accepts 197 → 33 on the 5-doc corpus (arbiter zone → 0, no LLM cost at all). Recall trade-off is real; Ship 37 opens as recall HITL investigation."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 36' arc retrospective — 3 sub-arcs delivered in one session
(2026-07-25). First real cutover test — proves Ship 33-35 wiring
works end-to-end + surfaces a big surprise about invariant
aggressiveness.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 36'.a | Design memo — flip procedure + success/failure signals | 758dbc0 |
| 36'.b | Flag flipped on Arion demo; 5 docs re-extracted; verified | (this arc) |
| **36'.c** | **Eval + retrospective (this)** | pending |

## What Ship 36'.b executed

1. Ship 34'.c v2 eval finished (231/232 PASS baseline held — confirmed
   the earlier 61-FAIL was OpenAI quota, not code)
2. `USE_CONSENSUS_EXTRACTION=1` set + API restarted
3. All 5 Ship-10-baseline uploads re-extracted via
   `/api/v1/admin/uploads/{id}/reextract` — the real doc_pipeline
   invocation (not just the standalone measurement script)
4. All 5 `intake_consensus_log` rows landed (telemetry wire clean)
5. Writer accepted consensus-emitted findings (tagged
   `inference_source='fingerprint_match'` for compat) — 4
   findings + 1 xfw_bridge landed on DQA; equivalent shape on
   the other 4 docs
6. Chat spot-check on A.7.4.3 + Art.35 + B.8.2.1 returned
   substantial coherent answers — no exceptions, no runtime break

## The numbers

| Doc | Total candidates | Accept | Arbiter | Drop | LLM calls | Latency |
|---|---|---|---|---|---|---|
| DQA | 24 | **4** | 0 | 20 | 0 | 9.7s |
| DPIA | 14 | **4** | 0 | 10 | 0 | 2.9s |
| RoPA | 70 | **5** | 0 | 65 | 0 | 2.6s |
| Consent Mgmt | 201 | **6** | 0 | 195 | 0 | 19.8s |
| **Processor Ops** | **226** | **14** | 0 | 212 | 0 | 32.1s |
| **TOTAL** | **535** | **33** | **0** | 502 | **0** | ~67s |

**Comparison series:**

| Corpus point | Total findings | Delta |
|---|---|---|
| Ship 32 Path A (existing pipeline) | 272 | baseline |
| Ship 33 Path B v3 (aggregator only, no invariant) | 196 | −28% |
| Ship 33 Path B v4 (+ LLM arbiter) | 197 | −28% |
| **Ship 36 real cutover (invariant on)** | **33** | **−88%** |

## The surprise finding

The no-excerpt-auto-drop invariant is MUCH more aggressive than
Ship 35'.a design memo predicted. Ship 35 forecasted "arbiter zone
94 → ~15" — meaning ~80 candidates would auto-drop pre-LLM. Reality:
**arbiter zone 94 → 0 AND many previously-accepted candidates also
drop** because they had scope-signal-only corroboration (no
fingerprint match, no evidence text).

Trace:
- Ship 33'.c shadow v3 DQA: 23 accept, 6 arbiter, 1 drop
- Ship 33'.c shadow v4 (+ LLM arbiter): 23 accept, 0 arbiter, 7 drop
- **Ship 36 real (+ invariant): 4 accept, 0 arbiter, 20 drop**

Delta from shadow-v4 to real: 19 previously-accepted candidates
now dropped. All of them had `fingerprint_excerpt=None` and were
scoring ≥ 0.75 with 2+ corroborators via combinations like
`doc_mappings_target (0.60) + explicit_ref (1.00) = 1.60,
corrob=2`.

Under the invariant: no excerpt = no finding, regardless of score.

## Semantically correct but aggressive

Every one of the 33 accepted findings is backed by an actual
fingerprint match — has an excerpt an auditor can read. That's
the correct auditor discipline.

But 88% reduction from Path A is a large recall change. The
existing pipeline's LLM discovery pass found candidates in body
text with no deterministic signal support; consensus doesn't. Ship
35 accepted this trade-off in design; Ship 36 quantifies it: the
lost candidates weren't 30-50% of findings (Ship 35's estimate) —
they're closer to 70-80%.

That's a real product decision to make: do compliance customers
want (a) 272 findings including many auditor-useless
evidence-less-scope-hint findings, or (b) 33 rock-solid
evidence-backed findings + missing coverage on leaves where LLM
would have found evidence but consensus's fingerprint-first flow
doesn't reach.

Ship 37 opens as the recall investigation.

## What's live on Arion demo now

`USE_CONSENSUS_EXTRACTION=1` in the API process env. Every doc
re-extract or new upload goes through consensus. `intake_consensus_log`
receives per-doc telemetry rows. Chat pipeline unaffected
(different subsystem). Existing findings from prior extractions
still active (the reextract endpoint doesn't auto-supersede — 2
sets coexist until tenant triages).

**Rollback**: unset env + restart API. Seconds.

## Codified 2 lessons

### 1. Shadow measurement predicts partial reality

Ship 33's shadow measurement + Ship 34'.b arbiter capture both
called `extract()` directly, seeing only per-candidate signal
outputs. Neither exercised the full doc_pipeline path, and
neither had the invariant. Ship 35'.a's prediction of "arbiter
zone 94 → ~15" was based on Ship 34 data + arithmetic —
mathematically correct but semantically incomplete.

Reality: with the invariant applied, arbiter zone → 0 AND many
previously-accepted candidates also drop. Shadow measurement
told us where the arbiter zone was; it did NOT tell us how many
previously-accepted candidates were also no-excerpt.

**Rule**: predictions from partial-shape measurements can be
off by 5-10x from real-shape execution. First real cutover
tests are irreplaceable data-generation events. Design memos
should mark predicted numbers as "estimates pending first
real-shape run" rather than as reliable targets.

### 2. Invariants added post-measurement need their own measurement

Ship 34'.c's HITL sample was on ARBITER-ZONE candidates only.
That gave a definitive answer about that zone (20/20
correct-reject). It did NOT sample the ACCEPTED-zone candidates
that would be affected by the invariant. The invariant was
designed based on data from a zone it doesn't apply to (the
arbiter zone), then applied to another zone (accepts) where its
impact wasn't measured.

**Rule**: when a design change would affect population X,
measure population X before shipping the change. Ship 34'.c
HITL should have included accepted-zone no-excerpt candidates
to validate the invariant's impact BEYOND the arbiter zone.

## What Ship 36 did NOT do

- **Flip flag on non-demo tenants** — no real customers today;
  flag stays default-OFF for anyone else
- **HITL recall investigation** — deferred to Ship 37
- **Retire old code paths** — needs 4-6 weeks of clean flag=1
  running + optional signal expansion first
- **Threshold retuning** — Ship 37+ from `intake_consensus_log`
  + HITL data

## Deferred / follow-on candidates from Ship 36

- **Ship 37: recall HITL** — sample 20-30 candidates that Ship
  36 DROPPED (no-excerpt scope-signal-only) + classify each as
  correctly-dropped / should-have-accepted / uncertain.
  Complements Ship 34'.c which sampled arbiter rejects.
- **Add LLM discovery pass as 9th signal** — if Ship 37 shows
  significant should-have-accepted rate, this addresses the
  recall gap
- **Relax invariant** — instead of hard-drop, allow no-excerpt
  candidates through if score ≥ higher threshold (e.g. 1.2 =
  fewer than 2 strong signals)
- **Consider inverting the invariant** — drop-when-scope-signals-only
  might be too narrow; the right primitive might be
  drop-when-no-substantive-signal
- **Compare with existing 2-DQA-active-findings baseline** — the
  4 new consensus findings for DQA sit alongside 2 prior active
  findings; tenant sees 6 findings; is that better or worse
  than pre-consensus 2? (Ship 37 could sample tenant impression)

## Sub-arc sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 36'.a | Design memo | Flip procedure locked |
| 36'.b | Flip + execute + verify | 5 re-extracts clean; wiring validated; big surprise on invariant impact |
| **36'.c** | **Eval + retro (this)** | **Baseline holds 231/232 PASS + 1 WARN (#200) + 0 FAIL; recall gap codified for Ship 37** |

## Related

- [[ship-35-prime-arc-retrospective-2026-07-25]] — the cutover
  arc this validates end-to-end
- [[ship-34-prime-arc-retrospective-2026-07-25]] — the HITL arc
  whose invariant is now shown to be more aggressive than
  predicted
- [[ship-33-prime-arc-retrospective-2026-07-25]] — the consensus
  arc whose real-world impact this arc quantifies
- `db/schema_v89_ship34b_intake_consensus_log.sql` — table
  now receiving production data
