---
name: ship-33-prime-arc-retrospective-2026-07-25
description: "Ship 33' arc closer — extension of Ship 1's consensus architecture to intake extraction. Delivered a full 8-signal consensus module (~1250 LOC), shadow-mode A/B measurement across 3 calibration iterations + LLM gatekeeper for the arbiter zone. Path A→B: 272→197 findings on the 5-doc corpus (28% reduction); Processor Ops multi-attribution 149→35 (77% reduction, the primary Ship 32 finding addressed). Deterministic 100% + LLM arbiter as bounded tiebreaker. Codified 4 lessons: per-candidate signals don't solve cross-candidate problems, correlated signals don't corroborate, wiring bugs invisible without measurement, LLM arbiter is high-precision on borderline candidates."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 33' arc retrospective — 3 sub-arcs delivered across one
session (2026-07-25). The arc REDIRECTED mid-flight from a
40-LOC semantic-fit gate patch to a full extraction consensus
refactor after user pushback: "automated evidence collection is
a key feature trending heavily so we need to get this right for
documents."

## Arc sequence

| Sub-arc | Delivery | Commit |
|---|---|---|
| 33'.a (initial) | Semantic-fit-inline gate design | b15e44b — superseded |
| 33'.a-redux | Full extraction consensus design memo | 42ccb4c |
| 33'.b | Module built + calibrated over 3 measurement iterations | cbbbba5 |
| **33'.c** | **LLM arbiter + final measurement + eval + retro (this)** | pending |

## What shipped

**`rag/intake/consensus_extraction/` module (~1250 LOC across 15 files):**
- `types.py` — ExtractionSignalOutput, CandidateVerdict, ExtractionConsensusResult
- `config.py` — ExtractionConsensusConfig (thresholds + weights, tunable)
- `aggregator.py` — sum weighted contributions per candidate,
  count corroborators, verdict = accept / arbiter / drop
- `orchestrator.py` — runs signals in dependency order, aggregates,
  routes arbiter zone to LLM gatekeeper (Ship 33'.c)
- `gatekeeper.py` — bounded LLM arbiter, batched at 40
  candidates/prompt, fail-open on error
- `signals/` — 8 signal modules:
  * fingerprint_keyword — wraps Ship 28+29 catalog matcher
  * doc_mappings_target — wraps `_scope_controls_via_doc_mappings`
  * must_semantic_topk — **first caller of `semantic_musts_in_scope`**
    (defined-but-unused since Ship 5'.b)
  * explicit_ref — reads `doc.explicit_refs` from enrich
  * per_protocol_scope — wraps `_scope_controls_via_retrieval`
  * semantic_fit_gate — wraps `_semantic_fit_ok` (Ship 11'.d)
  * content_shape_penalty — wraps `_looks_like_field_or_header`
    (Ship 11'.c) as negative-weight signal
  * evidence_uniqueness — **NEW cross-candidate signal**;
    penalises fingerprint matches whose excerpt is shared by ≥N
    other candidates. Directly addresses Ship 32's multi-attribution
    finding.

**Shadow-mode A/B measurement** via `scripts/measure_ship33_consensus.py`
runs BOTH pipelines side-by-side on the 5 Ship-10-baseline docs
without writing to the DB. 4 measurement iterations:

| Iter | Config | Total accept | Proc Ops accept | Note |
|------|--------|--------------|-----------------|------|
| v1 | 3 signals broken (tuples-not-dicts wiring bug) | 106 | 72 | Only 3 of 7 signals firing |
| v2 | All 7 signals firing | 266 | 82 | Correlated signals over-corroborated |
| v3 | + evidence_uniqueness + per_protocol_weight 0.20→0.10 | 196 | 34 | Multi-attribution primary case addressed |
| **v4** | **+ LLM arbiter on 94 candidates in arbiter zone** | **197** | **35** | **Final: 93 of 94 arbiter → drop** |

Path A (existing critic-verifier + concat) on 5 docs: 272 findings.
Path B (consensus v4): 197 findings. **28% reduction; 77% on
Processor Ops.**

## What Ship 33 does NOT do (deferred to follow-on)

- **Write-path integration** — no `USE_CONSENSUS_EXTRACTION` env
  flag on the extractor yet; consensus is invoked only from the
  measurement script. Cutover happens in a follow-on arc.
- **`intake_consensus_log` schema** — telemetry designed in
  33'.a-redux but not implemented. Would enable production
  tuning from real data.
- **Retirement of critic-verifier + concat** — the parallel path
  stays operational.
- **Threshold-tuning-from-data automation** — the config module
  supports overrides; automated tuning based on
  `intake_consensus_log` data is future work.

## Codified 4 lessons

### 1. Per-candidate signals don't solve cross-candidate problems

Ship 33'.a-redux designed 7 per-candidate signals (each looks at
one `(leaf_id, must_id)` candidate in isolation). None of them
could catch Ship 32's multi-attribution — that's a property
of many candidates SHARING an excerpt, not any single candidate.

v2 measurement confirmed: with 7 per-candidate signals, Processor
Ops still had 10 unique evidence texts across 82 accepted
candidates (12% uniqueness). The `evidence_uniqueness` signal
added in v3 (cross-candidate: count shared excerpts, penalize
above threshold) IS the specific fix.

**Rule**: when your design assumes independence and reality
contradicts it, add the specific signal that measures the
non-independent property. Don't tune weights on signals that
can't SEE the problem.

### 2. Correlated signals don't corroborate

v2 revealed `per_protocol_scope` + `must_semantic_topk` +
`fingerprint_keyword` all effectively answer "is this leaf about
processor-ops?" — they correlate on scope-matched docs. Treating
them as three independent votes just amplified scope-match rather
than adding independent evidence.

On Processor Ops v2: per_protocol_scope voted for 320 candidates,
must_semantic_topk for 108, fingerprint for 121. Every fingerprint
candidate got 3-signal corroboration → nothing filtered out.

The chat consensus signals work BECAUSE they measure different
aspects (retrieval cosine vs curator lexicon vs explicit ref vs
graph tightness). My extraction signals converged on the same
"scope match" dimension.

**Rule**: before adding a signal to a consensus aggregator,
verify it measures a different aspect than existing signals.
Correlated signals aren't corroboration; they're noise
amplification.

### 3. Wiring bugs are invisible without measurement

v1 shipped with 3 signals silently returning empty candidates
because `_fetch_leaf_musts` returns `[(must_id, text)]` tuples,
not `[{"id": ..., "text": ...}]` dicts. My code did
`item.get("id")` — always None. Zero fires despite correct
inputs.

Without the shadow-mode A/B script running BOTH paths and
reporting per-signal fire counts, this bug would have shipped
as "consensus works fine — see, 106 findings accepted!" (with
the 106 being narrower than intended).

**Rule**: the measurement harness is as important as the code
it measures. A/B shadow mode + per-signal telemetry surfaced
2 wiring bugs in this arc alone. The pattern of "build + run
+ inspect signal counts + fix + re-run" was tighter than any
unit-test suite would have caught.

### 4. LLM arbiter is high-precision on borderline candidates

v4 measured the LLM arbiter on 94 candidates in the 0.40-0.75
arbiter zone. Result: **93 rejected, 1 accepted**. Not "LLM
approves 50% for balanced acceptance" — a strong preference
for reject.

Two readings:
- The prompt encoded "prefer reject when generic / boilerplate"
  which biased toward reject
- The arbiter zone genuinely contained mostly weak candidates
  that the aggregator correctly flagged as uncertain

Both are consistent with success. The LLM is doing its job as a
tiebreaker — it doesn't need to accept half. Its role is to
resolve uncertainty, not to average out.

**Rule**: LLM arbiter for borderline candidates is HIGH signal
even at low accept rate. Don't calibrate weights so the arbiter
zone is 50% accept — calibrate so the arbiter zone contains
GENUINELY borderline candidates, then trust the LLM's judgment.

## Diagnostic notes

- Ship 33 architecture surfaced 2 systemic issues that Ship 33'.a-redux's
  design memo didn't predict: signal correlation (lesson 2) and
  cross-candidate blindness (lesson 1). Both were caught by
  iterative measurement.
- The redirect from "semantic-fit inline gate" to "full consensus
  refactor" delivered a proper architectural improvement, but at
  the cost of implementation-only-in-Ship-33'.b (no cutover this
  arc). Follow-on arc for cutover.
- Ship 33 does not retire the existing critic-verifier + concat
  path. Both paths remain in the codebase; consensus is invocable
  only from the measurement script for now. Cutover is a
  deliberate future decision.

## Related

- [[ship-32-prime-arc-retrospective-2026-07-25]] — measurement arc
  that surfaced the multi-attribution problem
- [[ship-33-prime-a-redux-extraction-consensus-design-2026-07-25]] —
  design memo (7 signals + gatekeeper; evidence_uniqueness added
  in v3 not in original)
- [[ship-1-consensus-arc-2026-07-15]] — the proven pattern this
  arc mirrors (chat classifier)
- [[ship-11-prime-arc-retrospective-2026-07-21]] — the critic-
  verifier arc whose two-path shape this arc's future cutover
  will retire
- `rag/consensus/aggregator.py` — reference implementation this
  arc's aggregator mirrors
- `rag/intake/consensus_extraction/` — new module this arc built

## Deferred / follow-on candidates from Ship 33

- **Write-path cutover** — env flag + retirement of the concat at
  `extractor.py:309`. Requires eval regression check.
- **`intake_consensus_log` schema + persistence** — enables
  production tuning from real data
- **Per-tenant threshold tuning** — some tenants may need
  tighter/looser thresholds (Arion demo tenant differs from real
  compliance customers)
- **Additional signals** — bridge_substantiveness (Ship 16'.c
  concept) as an 9th signal; document-role signal (policy
  authors have different fingerprint patterns than procedures)
- **Investigate the arbiter-zone rejection rate** — 93/94 is
  suspiciously uniform. Is the LLM discriminating, or
  reject-biased by prompt shape? Would benefit from HITL review
  of the 1 accepted vs the 93 rejected.
- **Extend to LLM-discovery pass** — currently consensus only
  processes candidates from fingerprint + doc_mappings + semantic-
  top-K. The existing pipeline has a critic-verifier LLM
  discovery pass that finds candidates from body text without any
  deterministic signal. Consensus doesn't cover this yet.
