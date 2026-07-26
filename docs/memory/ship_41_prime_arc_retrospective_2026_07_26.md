---
name: ship-41-prime-arc-retrospective-2026-07-26
description: "Ship 41' arc closer — HITL sample on Ship 40'.b's 74+69=143 fresh findings surfaces multi-attribution regression. DPIA opener sentence → 20 findings across 5 controls (textbook Ship 32-shape multi-attribution). Cross-framework unlock is real (4 Art.35 findings grounded) but MUST-level attribution weak. Default-ON evaluation NOT recommended; Ship 42 direction locked on evidence_uniqueness re-tuning + per-doc excerpt dedup."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 41' arc retrospective — 3 delivery sub-arcs + closer, single
session 2026-07-25/26. HITL validation of Ship 40'.b's cross-
framework unlock. Surfaces multi-attribution regression that
evidence_uniqueness signal doesn't catch at current thresholds.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 41'.a | Identify Ship 40'.b fresh findings (143 = 74 consensus + 69 xfw_proposer bridges) | inline |
| 41'.b | HITL categorization of fresh findings by grounding quality | inline |
| 41'.c | Processor Ops residual investigation | inline |
| **41'.d** | **Retro (this)** | pending |

Analysis-only arc — no code changes. HITL findings feed Ship 42
direction.

## Isolating Ship 40'.b fresh findings

`document_findings.extracted_at` filter (2026-07-25 20:15-20:17 UTC)
isolates the Ship 40'.b re-extract writes. Historical findings
from Ship 32/36/39 stay outside the window.

| Doc | n_fresh | unique_excerpts | uniqueness_pct |
|---|---|---|---|
| Consent | 33 | 25 | 76% |
| DPIA | 27 | 7 | **26%** |
| DQA | 28 | 22 | 79% |
| Processor Ops | 18 | 10 | 56% |
| RoPA | 37 | 26 | 70% |
| **Total** | **143** | **~90** | **~63%** |

## The 143 vs 74 discrepancy — xfw_proposer bridges

Ship 40'.b intake_consensus_log said n_accept=74 total across 5
docs. document_findings shows 143 fresh rows. Where do the extra
69 come from?

**xfw_proposer post-hoc bridges**. After consensus emits findings,
xfw_proposer runs a bridge pass — for each consensus finding on a
demonstrated leaf (e.g. A.7.2.5), it materializes cross-framework
bridge findings on the demonstrator's target (e.g. A.5.34,
A.5.31) with a `[Bridge: ...]` prefix. These are clean single-MUST
attributions.

Bridge count per doc:
- Consent: 21 bridges of 33 fresh (63%)
- RoPA: 22 of 37 (59%)
- DQA: 16 of 28 (57%)
- DPIA: 7 of 27 (26%)
- Processor Ops: 3 of 18 (17%)

**Consensus + bridges together produce the +42% recall claim.
Bridges are architecturally clean; consensus outputs have the
multi-attribution issue below.**

## Multi-attribution regression on DPIA — Ship 32 pattern in miniature

**One sentence → 20 findings across 5 different controls.**

DPIA doc opener:

> "This procedure defines how Arion Networks conducts Data
> Protection Impact Assessments (DPIAs) to identify and mitigate
> privacy risks in accordance with..."

Tagged to:
- Art.35 (GDPR) x 4 MUSTs (dpo_advice, trigger_criteria, content_minimum, review_trigger)
- 6.1.2 (ISO 27001) x 4 MUSTs
- 6.1.3 (ISO 27001) x 1 MUST
- 8.3 (ISO 27001) x 1 MUST
- A.7.2.5 (ISO 27701) x 10 MUSTs

**Total: 20 findings from 1 sentence.**

This is exactly the pattern Ship 32 diagnosed on Processor Ops
(one bullet → 43 findings across 43 controls) and Ship 33's
`evidence_uniqueness` signal was designed to catch.

The signal DOES fire — 20 candidates share the excerpt,
`share_count=20 ≥ threshold=5` → each gets `-0.50` penalty. But
each candidate ALSO has:
- doc_mappings_target: +0.60 (all 5 controls in DPIA's YAML target_leaves)
- fingerprint_keyword: +0.50 (opener keywords match all leaves)
- must_semantic_topk: +0.30

Net score: 1.40 - 0.50 = 0.90, above accept threshold (0.75).
**Penalty magnitude insufficient at threshold=5.**

## Cross-control vs within-control multi-attribution

Ship 32's pattern: cross-control (one bullet on 43 DIFFERENT
control refs). Considered fabrication.

Ship 40'.b's pattern: mixed:
- DPIA opener case = **cross-control** (5 controls). Ship 32-shape
  regression.
- RoPA A.5.34 x12 MUSTs from 3 sentences = **within-control**
  (one control, 12 MUSTs). Different failure mode — the doc's
  summary sentences legitimately speak to the control but don't
  itemize per-MUST. Arguably a granularity issue, not
  fabrication.
- Consent A.5.34 x8 MUSTs from 1 sentence = within-control
- Processor Ops section-header multi-attribution (A.7.4.2 x4
  MUSTs, A.7.5.3 x3) = within-control
- Processor Ops section header + control-family = cross-control
  (A.7.5.3 + B.8.5.1 share the "Return/Transfer/Deletion" header)

**~38% of Ship 40'.b's 143 fresh findings share excerpts (fanout
≥ 3 within-doc)**. Bridge findings (48%) are clean. Unique
per-MUST findings ~14%.

## Processor Ops residual (Ship 41'.c)

Ship 10 baseline: 5 findings.  
Ship 40'.b: 18 findings (3× Ship 10).

Pattern:
- 3 xfw_proposer bridges (clean)
- 4 A.7.4.2 MUSTs share "## 3.1 Purpose Limitation (B.8.2.2)"
  section header
- 3 A.7.5.3 + 1 B.8.5.1 share "Return, Transfer or Deletion" header
- 3 A.7.3.6/A.7.3.8 share "Complies with ISO/IEC 27701:2019 and
  GDPR Article 28(3)"

Better than Ship 32's 149 in absolute terms (85% reduction) but
still shows the same within-control section-header attribution
pattern. Within-control is defensible ("the doc's section IS about
purpose limitation, all 4 MUSTs of A.7.4.2 apply"); cross-control
via shared section header is not.

## Ship 41'.b HITL categorization summary

Of 143 Ship 40'.b fresh findings:

| Category | Count | % |
|---|---|---|
| Bridge findings (xfw_proposer, clean single-MUST) | 69 | 48% |
| Cross-control multi-attribution (fanout ≥3 across different controls) | ~15 | 10% |
| Within-control multi-attribution (fanout ≥3 within same control) | ~40 | 28% |
| Unique per-MUST or per-control | ~19 | 13% |

**Cross-framework unlock (4 Art.35 findings persisted) is real
and grounded at the control level.** Auditor sees "DPIA doc
addresses Art.35" correctly. Per-MUST attribution is weak
(same evidence excerpt across 4 different Art.35 MUSTs) but
this is arguably a granularity issue, not fabrication.

**Cross-control multi-attribution (10% of findings, esp. DPIA
opener → 5 controls) IS a regression** — evidence_uniqueness
signal not catching it at current threshold=5/penalty=-0.50.

## Codified 2 lessons

### 1. Isolate fresh from historical BEFORE analysis

Initial HITL analysis on document_findings without extracted_at
filter showed "110-finding fanout" — but that was Ship 32/36
historical baggage still in the table (posture_writer appends,
doesn't clear on re-extract). Filtering by `extracted_at > run
start` isolated Ship 40'.b's fresh 143 findings, revealing the
actual current-arc quality.

**Rule**: `document_findings` accumulates across re-extractions.
Any per-arc analysis must timestamp-filter or the numbers reflect
years of prior extractions. Ship 30 knew this (soft-deleted 102
orphan Ship 11'.e findings); the discipline needs re-applying
each measurement arc.

### 2. Signal thresholds tuned for one pattern miss adjacent patterns

Ship 33 designed evidence_uniqueness against Ship 32's cross-
control multi-attribution (one bullet → 43 different controls,
9% uniqueness). Threshold=5 / penalty=-0.50 caught THAT specific
disaster but doesn't catch:

- Cross-control at scale 5-20 (DPIA opener case — 20 findings, 5 controls)
- Within-control multi-attribution (12 MUSTs of A.5.34 from 3 sentences)

The signal's design was Ship 32-specific; Ship 41 reveals it
underweights the intermediate-scale multi-attribution that
consensus-mode Ship 40'.b unlocked.

**Rule**: signal weights + thresholds tuned against one
measurement pattern often miss adjacent patterns at different
scales. Future signal design should assume threshold sweeps are
part of the arc.

## Ship 41 verdict — default-ON evaluation NOT recommended

Ship 40 delivered cross-framework extraction technically. But
Ship 41 HITL shows:
- Multi-attribution regression exists (Ship 32-shape in miniature)
- 38% of findings share excerpts within-doc
- DPIA case: 20 findings from 1 sentence across 5 controls

**Default-ON on other tenants would multiply this pattern across
their doc corpus.** Cleanup effort would exceed the recall gain.

## Ship 42 direction candidates

**A. Tune evidence_uniqueness thresholds**
- Drop `evidence_share_threshold` from 5 → 3 (catches earlier)
- Increase `evidence_uniqueness_penalty` from -0.50 → -1.0
  (kills more of the doc-mappings-boosted candidates)
- Add cross-control gate: extra penalty when shared excerpt
  spans > 2 distinct control_refs

**B. Per-doc excerpt dedup at write time**
- Post-consensus writer sees candidates with duplicated excerpts
- Keeps 1 finding per (excerpt, control_ref) pair
- Aggregates the collapsed MUSTs into a single row's metadata

**C. Product-level change**
- Advisory surfaces "Evidence in DPIA §1 supports Art.35" (one
  citation) with a "5 MUSTs addressed" annotation instead of
  20 separate finding rows
- Requires UI + advisory-render changes

**Option A is smallest scope, config-only. Option B changes
write-path semantics. Option C is a product decision.**

Recommendation: Ship 42'.a = design memo weighing A vs B vs
combined A+B. Product-level C deferred to a separate arc after
tuning proves quantitative floor.

## What Ship 41 did NOT do

- **No code changes** — analysis arc only
- **No default-ON evaluation** — Ship 41 explicitly recommends
  against it until Ship 42 fixes
- **No orphan-finding cleanup** — Ship 30 pattern; separate arc
- **No config change to consensus** — Ship 42 candidate

## Deferred / follow-on candidates

- **Ship 42**: multi-attribution fix (A/B/C options above)
- **Ship 43**: default-ON evaluation (blocked by Ship 42)
- **Orphan finding cleanup arc**: document_findings has ~4000
  entries; count of orphans from prior Ship 32/36/39 measurement
  runs is unknown
- **posture_writer clear-on-reextract**: currently APPENDS; each
  re-extract leaves prior findings, complicating measurement +
  potentially confusing auditor. Add `_clear_prior_findings(upload_id)`
  before write? Product decision.

## Related

- [[ship-40-prime-arc-retrospective-2026-07-25]] — the arc whose
  quality Ship 41 measured
- [[ship-32-prime-arc-retrospective-2026-07-25]] — original
  multi-attribution diagnosis; evidence_uniqueness designed here
- Ship 42 (next) — evidence_uniqueness re-tuning + per-doc dedup
- `rag/intake/consensus_extraction/signals/evidence_uniqueness.py`
  — the signal Ship 42 will re-tune
- `rag/intake/consensus_extraction/config.py:57-58` — the
  thresholds Ship 42 will adjust
