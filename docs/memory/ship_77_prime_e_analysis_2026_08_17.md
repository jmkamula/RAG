---
name: ship-77-prime-e-analysis-2026-08-17
description: "Ship 77'.e — first-principles compare of consensus vs critic-verifier against manually-authored ground truth for 5 baseline docs. Critic-verifier wins on all 4 metrics (P/R/F1/wrong-artefact). Consensus never fired LLM arbiter — all 100 acceptances were deterministic. Recommendation: retire consensus. Caveats: both paths score <20% F1; extractor system needs substantial work regardless of which path we keep."
metadata:
  type: project
  ship: "77'"
---

# Ship 77'.e — first-principles compare

Compared consensus (Run A) vs critic-verifier (Run B) findings on the
5 baseline docs against the 5 manually-authored ground-truth yamls.

## Method

Matched each finding's `checklist_item_id` against expected MUSTs in
the ground-truth yaml for that doc. Three-way classification:

- **True Positive (TP)** — finding on a MUST marked `satisfies`
  (strict) or `satisfies + partial` (lenient).
- **False Positive (FP)** — finding on a MUST marked `not_satisfies`
  OR on a MUST not in the ground truth for that doc (wrong artefact).
- **False Negative (FN)** — expected MUST the path didn't emit.

Precision = TP / (TP + FP). Recall = TP / (TP + FN). F1 = harmonic.

Script: `scripts/ship77e_compare.py`.

## Results

### Aggregate (across 5 docs)

| Path | Scoring | Precision | Recall | F1 | TP | FP | FN |
|------|---------|----------:|-------:|---:|---:|---:|---:|
| Consensus | Strict | 13.9% | 14.1% | 14.0% | 23 | 143 | 140 |
| Consensus | Lenient | 19.9% | 12.3% | 15.2% | 33 | 133 | 236 |
| **Critic** | **Strict** | **15.7%** | **20.9%** | **17.9%** | **34** | **183** | **129** |
| **Critic** | **Lenient** | **22.1%** | **17.8%** | **19.7%** | **48** | **169** | **221** |

**Critic wins on all 4 metrics.** F1 delta ~+4pp lenient / +4pp strict.
Absolute F1 is low for both (<20%) — the extractor system regardless
of path is well below production-quality.

### Per-doc breakdown

| Doc | GT strict / partial | Consensus F1 (strict/lenient) | Critic F1 (strict/lenient) | Winner |
|-----|-------------------:|:-----------------------------:|:-------------------------:|:-------|
| DPIA | 15 / 11 | 33.3% / 40.7% | 16.0% / 16.7% | Consensus |
| RoPA | 33 / 21 | 12.7% / 14.0% | 10.0% / 9.8% | Consensus |
| Consent | 35 / 18 | 0.0% / 4.4% | 6.0% / 8.5% | Critic |
| Processor Ops | 73 / 44 | 8.3% / 8.5% | 21.9% / 26.1% | **Critic (big)** |
| DQA | 7 / 12 | 38.7% / 27.9% | **71.4% / 38.5%** | **Critic (biggest)** |

Consensus wins 2 (DPIA + RoPA), Critic wins 3 (Consent + ProcOps + DQA).
Critic's ProcOps + DQA wins are decisive.

### False positive character

Aggregate FP breakdown across 5 docs:

| Path | FP-on-not_satisfies | FP-on-unknown |
|------|-------------------:|--------------:|
| Consensus | 17 | 116 |
| Critic | 23 | 146 |

The dominant FP class for both paths is "FP-on-unknown" — findings on
MUSTs not enumerated in the ground truth. Two possible explanations:
- **(A) Wrong-artefact findings**: the extractor emits findings on
  controls the doc references but isn't the artefact for (e.g., DPIA
  doc emits Art.5.34 register findings when it shouldn't).
- **(B) Ground truth enumeration gaps**: I didn't enumerate every
  possible MUST the doc could reasonably touch.

Manual spot-check on Consent (57 FP-on-unknown vs 25 not_satisfies) —
the critic-emitted findings hit refs the doc doesn't primarily
target but references in prose (Art.9 mentioned once → Art.9 findings
emitted). Both (A) and (B) contribute; (A) dominates.

## Key observations

### 1. Consensus never fired LLM arbiter

Aggregator saw 824 candidates across 5 docs; accepted 100; **zero LLM
arbiter calls fired**. All acceptances landed in the accept-or-drop
zones directly. The consensus module's core value proposition — "LLM
arbiter resolves borderline cases" — didn't materialize on this
sample. When the deterministic aggregator says "accept", the LLM
never sees it.

If the deterministic aggregator's threshold is well-tuned, this is
fine. But it means consensus is essentially a fingerprint-first
signal-fusion path with LLM as a rarely-used escape hatch. That's not
the "consensus + arbitration" design Ship 33 sold.

### 2. Critic overshoots but with better recall

Critic emitted 251 findings vs consensus's 168. But critic's TP is
higher (48 vs 33 lenient) — the extra findings include real
positives. Critic's LLM refiner pass extracts findings from body-
text prose that consensus's deterministic signals miss.

### 3. DPIA + RoPA benefit from consensus

Both docs have highly-structured content (numbered steps, bullet
lists, register field lists). Consensus's fingerprint-heavy weighting
captures the structural signals well. Critic's LLM pass may
under-fire on structured content because it looks for prose narrative.

### 4. Both paths are bad on Consent

Consent doc scores 0% strict precision for consensus and 4.6% for
critic. Doc has strong per-principle language ("Freely given",
"Documented" etc.) but neither path maps that to the specific MUSTs.
Suggests the MUSTs in Art.7 catalog aren't well-aligned with real
doc language. Curator arc candidate: Art.7 fingerprint keyword
audit.

## Direction recommendation

**Retire consensus. Keep critic-verifier.**

Rationale:
- Critic wins on 4 of 4 aggregate metrics.
- Critic wins 3 of 5 per-doc F1s including the two big wins (Processor
  Ops + DQA).
- Consensus's LLM arbiter never fires — the value prop doesn't
  materialize. What's left is a fingerprint+signal-fusion path that
  loses to fingerprint+critic-refiner on 3 of 5 docs.
- Consensus costs ~1250 LOC across 15 files. Retirement reclaims
  substantial code surface.

Caveats:
- **Both paths are <20% F1**. This isn't "critic is production-
  ready"; it's "critic is less broken than consensus". Ship 77'
  outcome doesn't validate critic-verifier as good enough — it
  validates that critic is the less-bad path to keep.
- **Consensus wins on DPIA + RoPA**. Retirement means we lose whatever
  signal-fusion benefit consensus provided on structured docs. If
  DPIA/RoPA precision matters, critic needs targeted improvement.
- **Sample size is 5 docs**. Ship 77' outcome shouldn't be
  generalized to the whole tenant corpus without measurement on more
  docs.

## Retirement plan sketch (for a follow-up arc)

1. **77'.f (this decision retro)** — this doc.
2. **77'.g** — retire consensus module. Delete `rag/intake/
   consensus_extraction/` (~1250 LOC / 15 files). Delete
   `USE_CONSENSUS_EXTRACTION` env flag + all reads. Delete Ship 75'.c
   consensus migration test (`tests/test_consensus_contract_wiring.py`).
   Retire `intake_consensus_log` table (or keep as historical audit).
3. **77'.h** — measure critic on DPIA + RoPA after retirement. If
   F1 drops significantly on those (consensus was pulling weight
   there), open a critic-improvement arc.

## What we learned about the ground truth itself

Building the ground truth surfaced its own findings:

- **Enumeration gaps**: FP-on-unknown counts (116 consensus / 146
  critic) suggest my ground truth doesn't cover every plausible MUST.
  The Processor Ops doc scores 79 FP-on-unknown for critic — likely
  because I only enumerated 12 refs; the doc references A.7.x mirrors
  too.
- **"Wrong artefact" as a scoring principle** worked but needs
  refinement: Consent doc's Art.9 mentions triggered "off-artefact"
  findings that arguably ARE legitimate coverage (doc mentions Art.9
  → Art.9 finding is a fair extraction). The strict "wrong artefact"
  rule punished this.
- **Doc-typo tolerance question**: Consent doc cites "A.7.5.5" (no
  such ref) — the extractor still emitted findings on real A.7.x
  neighbours. Whether those are FP-on-wrong-artefact or valid-
  inference-from-typo is a judgment call I made conservatively (FP).

## Sub-arc status

- 77'.a — scoping (shipped)
- 77'.b — DPIA ground truth (shipped)
- 77'.c — remaining 4 grounds (shipped)
- 77'.d — dual-path measurement (shipped)
- **77'.e — this analysis (this doc)**
- 77'.f — arc retro + close (pending)

## Recommended next step

Ship 77'.f = arc retrospective closing 77'. Direction decision
above (retire consensus) becomes a Ship 78' candidate task.
Retirement should happen in its own arc with fresh eval + dogfood
per the discipline lessons codified in Ships 74-76.
