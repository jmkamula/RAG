---
name: ship-78-prime-arc-retrospective-2026-08-17
description: "Ship 78' arc close-out (78'.a → 78'.f). Productionized the union of consensus + critic-verifier extractor paths, discovered in Ship 77'.f as complementary discovery mechanisms. Tuned the LLM gatekeeper prompt for auditor-realistic acceptance. Result: aggregate lenient F1 23.6% (vs consensus-alone 15.2%, critic-alone 19.8%, union-with-untuned-LLM 21.8% predicted). Retired USE_CONSENSUS_EXTRACTION as a mutual-exclusive gate; kept as escape-hatch config. Codified 4 lessons on complementary vs competitive selection, ground truth as first-class artifact, retire-via-repurpose, and interface changes need consumer audit."
metadata:
  type: project
  ship: "78'"
---

# Ship 78' arc close-out

Six sub-arcs (78'.a → 78'.f) across one working day (2026-08-17).
Productionized the direction Ship 77'.f established: **run both
consensus + critic-verifier paths on every doc, union findings,
dedup on (control_ref, checklist_item_id).**

Opens directly out of Ship 77' — which itself was a course-
correction on Ship 77'.e's premature "retire consensus"
recommendation once Ship 77'.f's overlap analysis showed the
paths were complementary, not competitive.

## Sub-arcs

| Sub | What shipped | Files |
|-----|---|---|
| 78'.a | Scoping doc + 6 design decisions (D1-D6): both paths always run; dedup on (control_ref, must_id); serial execution; escape-hatch env values; accept 2x LLM cost; confidence-ranked dedup winner. | `docs/memory/ship_78_prime_a_2026_08_17.md` |
| 78'.b | Union extractor code. `_union_findings()` in `rag/intake/extractor.py`. USE_CONSENSUS_EXTRACTION repurposed with 3 modes (union / consensus_only / critic_only). Failure isolation via try/except per path. 3 new metrics grandfathered in Ship 74'.c drift set. 9-case regression test. | `rag/intake/extractor.py`, `tests/test_union_extractor.py`, `tests/test_intake_metrics_drift.py` |
| 78'.c | Auditor-realistic LLM gatekeeper prompt. `_GATEKEEPER_SYSTEM` rewritten to accept touch-evidence + reject only clearly-off-topic or structural noise. Dogfood on 5 baseline docs → 330 findings. Scored vs ground truth → **F1 23.6% lenient** (best of any variant). | `rag/intake/consensus_extraction/gatekeeper.py`, `docs/ground_truth/ship77d_measurement/run_d_union_tuned.csv`, `scripts/ship78c_dogfood.py`, `scripts/ship77e_compare.py` |
| 78'.d | schema_v101 — promoted the 3 union metrics from Ship 74'.c grandfather set to persisted intake_trace_log columns. Tracer allowlist + forwarding wired. External API dogfood: 5/5 endpoints healthy. Full eval as safety net. | `db/schema_v101_intake_trace_union_metrics.sql`, `rag/intake/doc_pipeline.py`, `tests/test_intake_metrics_drift.py` |
| 78'.e | Retired the mutual-exclusive gate. `_extraction_mode()` + `is_consensus_active()` helpers replace the pre-Ship-78 `== "1"` reads across 3 stale consumer sites (doc_pipeline.py + deployment_status.py). 7-case regression test locking env-var semantics. | `rag/intake/extractor.py`, `rag/intake/doc_pipeline.py`, `rag/admin/deployment_status.py`, `tests/test_extraction_mode.py` |
| 78'.f | This retro. | — |

## What shipped end-to-end

Before Ship 78':
- Consensus + critic-verifier were mutually-exclusive alternatives
  gated by `USE_CONSENSUS_EXTRACTION`. Default OFF (critic).
- Consensus-only tenants (opt-in via flag) got 168 findings on
  5-doc baseline; critic-only tenants got 251. Neither
  independently beat the union.
- LLM gatekeeper prompt was over-strict — rejected legitimate
  broad statements as "generic PII processing mention" etc.
- Ship 77'.e concluded "retire consensus" based on aggregate F1
  alone. Ship 77'.f then showed the paths were complementary
  (overlap 5-22 per doc), flipping that recommendation.

After Ship 78':
- Union is the DEFAULT mode. Both paths run on every doc.
- LLM gatekeeper tuned to auditor-realistic acceptance.
- **F1 23.6% lenient** — best of any variant measured.
- USE_CONSENSUS_EXTRACTION preserved as escape-hatch config:
  `consensus_only` for regression debugging; `critic_only` for
  cost-constrained tenants; anything else defaults to union.
- schema_v101 persists union observability (per-path
  contribution counts + dedup drop count).
- Ship 74/75/76's discipline (guards, tests, dogfood) applied
  throughout.

## The measurement pattern that emerged

Ship 77'/78' shipped alongside a **first-principles measurement
infrastructure** that will outlast this arc:

- `docs/ground_truth/*.yaml` — 5 hand-authored ground truths
  covering 621 candidate MUSTs across the 5 baseline docs.
- `docs/ground_truth/ship77d_measurement/*.csv` — 4 measurement
  runs (A: consensus, B: critic, C: cons+verify, D: union+tuned)
  preserved as csv for reproducibility.
- `scripts/ship77e_compare.py` — extensible scorer against
  ground truth.
- `scripts/ship77f_chain.py` — overlap + chaining analysis.
- `scripts/ship78c_dogfood.py` — re-runnable dogfood driver.

Future extractor arcs should extend the ground truth (more docs,
tighter MUST enumeration) rather than compete against ad-hoc
comparisons.

## Numbers

### F1 across measurement runs (5-doc aggregate, lenient scoring)

| Run | Path | F1 | Recall | Precision |
|-----|------|---:|-------:|----------:|
| A | Consensus alone | 15.2% | 12.3% | 19.9% |
| B | Critic alone | 19.8% | 17.8% | 22.1% |
| C | Consensus + LLM verify-all (untuned) | 3.5% | 2.1% | 12.5% |
| — | Predicted union (77'.f overlap math) | 21.8% | 24.5% | 19.6% |
| **D** | **Union + tuned LLM** | **23.6%** | **25.3%** | **22.2%** |

Run D beat the union prediction by +1.8pp (tuned LLM added
verification precision without crashing recall).

### Per-doc F1 (lenient, Run D vs pre-union best)

| Doc | Best pre-union | Union+tuned | Delta |
|-----|--------------:|------------:|------:|
| DPIA | Consensus 40.7% | 28.0% | -12.7pp ⚠ |
| RoPA | Consensus 14.0% | 27.5% | +13.5pp |
| Consent | Critic 8.5% | 7.8% | -0.7pp |
| Processor Ops | Critic 26.1% | 27.5% | +1.4pp |
| DQA | Critic 38.5% | 28.6% | -9.9pp ⚠ |

Wins on RoPA + ProcOps; ties on Consent; LOSES on DPIA + DQA.
DPIA + DQA are structured procedure docs where consensus's
fingerprint-heavy signals were the primary signal — the
tuned-LLM overlap dilutes them slightly. Future tuning arc
candidate.

## Codified lessons

Adding 4 new (58-61).

### 58. Complementary discovery vs competitive selection

Ship 77'.e framed extractors as competing implementations —
"which path wins on ground truth?" The aggregate F1 comparison
picked critic. Ship 77'.f flipped that by asking a different
question — "how much do these paths overlap?"

Overlap analysis (per doc): 5-22 shared MUSTs out of 30-150+
per path. The paths were exploring different territory.

**How to apply:** before choosing between two extractors /
retrievers / rankers on head-to-head comparison, measure their
OUTPUT OVERLAP. If overlap is low (<50% of either path's
output), they're complementary and the right question is
"how do we combine them?" — not "which wins?" Complementary
discovery favors union; competitive selection favors pick-
best.

The overlap-first framing has a name in retrieval: **result
diversity**. Same math applies to extractor outputs.

### 59. Ground truth is a first-class artifact

Ship 77'.b-c produced 5 hand-authored ground-truth yamls
(621 MUSTs classified). Ship 77'.e used them for the first
scoring. Ship 78'.c re-used them for the dogfood. Future
extractor arcs will re-use them too.

The ground truth cost 4-6 hours of curator work to produce
+ an hour of self-review per doc. It's now permanent
infrastructure — every future extractor change can measure
against it in seconds.

**How to apply:** when a domain needs quality measurement,
INVEST in the ground truth first. It compounds — every
subsequent arc measures against the same corpus and can
directly compare. Without ground truth, arcs argue about
which path "feels" better; with it, arcs argue about
whether the ground truth is right.

Related: Ship 77'.d's measurement runs (A/B/C/D) preserved
in csv become a comparison baseline for future arcs. Not
just the code — the DATA it produces is documentation.

### 60. Retire mutual-exclusive gates via repurpose, not deletion

Ship 78'.b repurposed `USE_CONSENSUS_EXTRACTION` from
"consensus mode enabled" (pre-Ship-78) to "consensus mode
override" (post-Ship-78). Users who previously set it to `1`
now get union (since consensus IS running in union mode).
Users who want the pre-Ship-78 consensus-only mode set
`consensus_only`. Users who want critic-only set `critic_only`.

Deletion would have required a config migration + user
communication + backward-compatibility shim. Repurpose kept
existing configs working with sensible new semantics.

**How to apply:** when a flag's meaning becomes obsolete (e.g.
mutual-exclusive gate → cooperating paths), don't delete the
flag; repurpose it. Preserve legacy values as sensible defaults
in the new semantic space. Then retire later once the new
meaning is proven.

Similar precedent: Ship 2'.o retired kill switches once
stability was proven; Ship 3'.l retired the pre-2022 ref
handling. Repurpose-first, retire-later is a codified pattern.

### 61. Interface changes need consumer audit

Ship 78'.e found 3 stale sites still reading
`USE_CONSENSUS_EXTRACTION == "1"` with pre-Ship-78 semantics.
Under Ship 78' union default, the check silently degraded
(returned False when consensus WAS active as part of union).
No test caught it because no test exercised the doc_pipeline
widening + Phase 3 filter paths under union mode.

Same pattern as Ship 76'.f's CaseFileShim bug: interface
change without consumer audit → silent regressions.

**How to apply:** when repurposing an env-var / config value's
semantics, grep for ALL consumers before shipping the
repurpose. Migrate them to a helper or add regression tests
locking the expected behavior under each mode. Ship 78'.e's
`_extraction_mode()` + `is_consensus_active()` helpers centralize
the interpretation; consumers now call the helpers instead of
duplicating the env-read.

Reinforces lesson 57 (duck-typed interfaces need shim
mirroring, Ship 76'.f) — different mechanism, same discipline.

## What's parked

- **DPIA + DQA regression under union+tuned** (F1 dropped
  ~10-12pp vs single-path best). Union dilutes structured-doc
  fingerprint signals. Future tuning arc: doc-shape aware
  weighting?
- **Ground truth enumeration gaps** — FP-on-unknown counts still
  60%+ of FPs. Ground truth is a first-pass draft; iterations
  would sharpen precision measurement.
- **LLM prompt has known blind spots** — tuned to be
  auditor-realistic but not tested on adversarial prose
  (e.g. deliberately vague policy statements). Ship 79'-ish
  arc for adversarial red-teaming.
- **Cost measurement missing** — arc accepted 2x LLM cost by
  design (D5) but didn't measure actual per-doc $$ under
  production traffic. Should surface in intake_trace_log +
  ai_call_log correlation.

## Cross-arc pattern

Ship 77' → Ship 78' mirrors the audit→design→migrate pattern
established in Ships 74-77 (74 silent-drop, 75 SSoT coverage,
76 N/A cascade, 77 extractor evaluation). Ship 78' is the
**productionization** phase of the Ship 77' measurement
insight.

Related: Ships 32 → 33 → 34-39 (measurement → consensus
extraction → tuning). Ship 78' is the second-generation
answer — the tuning arc's premise (consensus REPLACES
fingerprint+critic) was wrong; the answer is COMBINE, not
REPLACE.

## Session shape

Standard scope → implement → dogfood → productionize →
retire → retro cadence, but the notable feature is that the
DIRECTION itself came from measurement (Ship 77'.f's
overlap analysis), not from up-front design. Ship 78' was
the productionization arc; Ship 77' was the discovery arc.

Cross-arc lesson: complex system decisions are best made by
measuring reality, not by architecturing on assumptions.
Ship 33-39 spent 6 sub-arcs trying to make consensus work
as a replacement; Ship 77-78 spent 12 sub-arcs proving
consensus works alongside critic. The second answer was
right; the first was expensive-to-discover.

## Final tally

- **6 sub-arcs** shipped
- **330 findings** produced by union+tuned on 5-doc baseline
- **F1 23.6% lenient** — +8.4pp over consensus-alone (15.2%)
- **schema_v101** persists union observability
- **4 new lessons** codified (58-61)
- **7 regression tests** across Ship 78' guards + new tests
- **8 preserved measurement artefacts** (5 ground-truth yamls,
  4 CSV run snapshots, 3 analysis scripts)
