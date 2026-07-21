---
name: ship-11-prime-e-reextraction-measurement-2026-07-21
description: "Ship 11'.e — re-extraction measurement checkpoint; surfaced two real issues + a methodology confounder"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 11'.e (2026-07-21) — the measurement checkpoint from the
Ship 11'.a plan. Dry-run re-extract of Ship 10's 5 documents
under the Ship 11'.b + 11'.c + 11'.d filters to measure combined
impact.

## What the measurement revealed

Three findings, most of them uncomfortable:

### Finding 1 — Ship 11'.c gap on the fingerprint path (CORRECTED IN-ARC)

`_looks_like_field_or_header` was wired into
`_run_critic_verifier_pass` + `_parse_llm_response` but NOT
`_extract_via_fingerprints`. That path emits DocumentFindings
directly with `inference_source='fingerprint_match'` and
constituted 40-80% of the per-doc finding volume on procedural
docs.

**Fix shipped**: extended the filter to
`_extract_via_fingerprints` too. Content-shape drops now
accumulate across both paths into the shared
`dropped_content_shape` metric.

### Finding 2 — Ship 11'.d prompt violated case-file discipline (REDESIGNED)

Ship 11'.d grew the critic system prompt 2100 → 4900 chars +
added `obligation:` lines per priming control (~+2700 chars).
This is the OPPOSITE of what the case-file arc codified:
compact prompt + deterministic post-critic gates.

On Consent Management the enlarged prompt destabilized JSON
output — "both attempts returned malformed JSON" — dropping
ALL critic findings for that doc. Fallback was the un-filtered
fingerprint path.

**Redesign shipped**: reverted the prompt bloat. Added a
post-critic `_semantic_fit_ok()` gate using cosine similarity
between quote embedding + anchor `business_description`
embedding. Threshold 0.30, fail-open on missing infrastructure.
`business_description` stays on `PrimingControl` (feeds the
gate) but is no longer rendered in the prompt.

**Empirical caveat**: sanity testing showed the 0.30 threshold
is too coarse. Legitimate matches score ~0.46; the
"Subprocessors → contracts" false positive also scored ~0.48.
Cosine embeddings don't cleanly separate the semantic-fit
cases we care about. The gate is in-place but tuned
conservatively (few drops observed in the v2 measurement).

### Finding 3 — Measurement methodology confound (UNCORRECTABLE)

Comparing today's re-extract volume to Ship 10's original
counts is NOT a fair Ship 11 measurement, because Ship 9'.c
(2026-07-20) added 189 new doc_mappings between Ship 10 and
today. The fingerprint index grew:

- Ship 10 era: ~317 leaves, ~2100 fingerprints (estimated)
- Post-Ship 9: 506 leaves, 2595 fingerprints (measured)

51 `program_review` leaves alone were added by Ship 9'.c.
Each carries fingerprint tokens like "purpose", "records",
"review" that broadly match procedural documents.

**The v2 measurement shows 227 findings on the same 5 docs
today, vs Ship 10's 97.** That's +134% but attributable to
Ship 9's coverage expansion, not Ship 11 regressions.

## What was actually measured

Ignoring the confounder, the drop-counter telemetry did fire:

- **Content-shape drops** (Ship 11'.c + 11'.e FP-path
  extension): 2 on DQA (both v1 and v2). Low but real.
- **Semantic-fit drops** (Ship 11'.d/redesign): 2 on Consent,
  3 on Processor. Low; threshold conservative.
- **Bridge source-quality drops** (Ship 11'.b): 0 measurable
  in dry-run — bridges emit from `xfw_proposer`, a separate
  post-extract stage this measurement doesn't invoke.

## The uncomfortable comparison

v1 (with Ship 11'.d prompt bloat, before redesign): 183 findings
v2 (with Ship 11'.d redesigned, post-critic gate): 227 findings

Prompt bloat DID reduce noise (24% reduction), but at the cost
of case-file discipline + JSON parse instability. The
principled redesign scored WORSE numerically but preserved the
architectural invariant.

## Honest interpretation

Ship 11's structural filters are correctly implemented and
firing on the right patterns. But:

1. **Fingerprint layer breadth dominates.** With 2595
   fingerprints across 506 leaves, procedural docs match
   dozens of MUSTs by keyword-family overlap regardless of
   Layer 1/2/3 filters.

2. **Embedding-based semantic-fit is too coarse.** Related
   concepts embed similarly ("subprocessors" ≈ "contracts with
   processors") even when the sentence doesn't establish the
   anchor's core obligation.

3. **Real Pattern-2 fix needs curator work** — tightening
   fingerprint token sets on individual MUSTs. That's out of
   scope for Ship 11 (which stayed pipeline-only) and belongs
   in a curator arc.

## What ships from Ship 11'.e

- `scripts/measure_ship11_reextraction.py` — the measurement
  harness. Useful for future re-runs against different filter
  states.
- Ship 11'.c filter extended to `_extract_via_fingerprints`
  in `extractor.py`.
- Ship 11'.d/redesign: revert + post-critic semantic-fit gate
  in `critic_verifier.py` (via `_semantic_fit_ok`).
- New telemetry: `dropped_semantic_fit`.

## Recommendation for Ship 11'.f (arc closer)

Ship 11 delivered structurally-correct filter infrastructure
across three layers, but the empirical impact on the noise
floor is modest. Two follow-up arcs to consider:

1. **Curator arc on fingerprint token discipline.** Audit the
   ~2595 fingerprints for over-broad keyword sets. Focused on
   `program_review` (51 leaves × ~5 fingerprints each = ~255
   generous fingerprints) — many probably match too many docs.

2. **HITL-driven filter calibration.** As tenants approve/
   reject new findings, learn which sources routinely produce
   rejects and tighten the filters against those specific
   patterns. Feed the Ship 6'.d claim-events log into filter
   tuning.

## Ship 11' progress

| Sub-arc | Status |
|---|---|
| 11'.a Extractor quality plan | ✓ |
| 11'.b Bridge source-quality gate | ✓ |
| 11'.c Content-shape filter | ✓ (extended to FP path in 11'.e) |
| 11'.d Critic prompt enhancement | ✓ (redesigned as post-critic gate in 11'.e) |
| **11'.e Re-extraction measurement checkpoint** | **✓** |
| 11'.f Arc retrospective | next |

## Related

- [[ship-11-prime-a-extractor-quality-plan-2026-07-20]]
- [[ship-11-prime-b-bridge-source-quality-gate-2026-07-20]]
- [[ship-11-prime-c-content-shape-filter-2026-07-20]]
- [[ship-11-prime-d-critic-prompt-enhancement-2026-07-21]]
- Ship 10 HITL review (2026-07-20) — the source dataset
- [[ship-2-prime-casefile-arc-2026-07-15]] — the "compact
  prompt + deterministic gates" discipline the redesign restores
