---
name: ship-34-prime-arc-retrospective-2026-07-25
description: "Ship 34' arc closer — validation + telemetry gate before Ship 35 cutover of the extraction consensus module. HITL sample of 20 arbiter rejects returned 20/20 correct-reject (100%, above 80% threshold). Cutover unblocked. Also delivered schema_v89 intake_consensus_log + log writer + measurement script enhancement to capture arbiter verdicts. Surfaced tuning insight: majority of arbiter zone is no-excerpt single-signal candidates that should auto-drop pre-LLM."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 34' arc retrospective — 3 sub-arcs delivered in one session
(2026-07-25). Prerequisite arc that gates Ship 35's cutover of
the consensus extraction path.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 34'.a | Design memo — schema + HITL sample plan + thresholds | 50b4ae0 |
| 34'.b | schema_v89 + log writer + measurement script enhancement + capture | 581d0ef |
| **34'.c** | **HITL review + eval + retrospective (this)** | pending |

## The HITL sample verdict

**20 of 20 sampled arbiter rejects → correct reject** (100%).

Well above the 80% cutover-approval threshold. Cutover unblocked.

### Sample breakdown

Stratified across the 5 Ship-10-baseline docs (3-4 per doc,
random-seeded for reproducibility):

| Category | Count | Notes |
|---|---|---|
| Correct reject — no excerpt at all | 17 | doc_mappings_target / per_protocol_scope voted but no fingerprint match → no evidence text for LLM to evaluate |
| Correct reject — Ship 32 multi-attribution TOC line | 3 | Same bullet-list sentence ("- Logging processing activities (A.8.3.1) - Secure return...") that fingerprinted 43 leaves on Processor Ops. LLM correctly said "TOC/summary, not evidence for this specific MUST" |
| Should-have-accepted | 0 | — |
| Uncertain | 0 | — |

### What this tells us

The LLM arbiter's 93/94 reject rate (Ship 33'.c) is NOT
prompt-shape bias — it's correct discrimination on genuinely
weak candidates.

Two failure modes it caught cleanly:
1. **No-excerpt candidates** — signals fired on scope/mapping
   evidence but no fingerprint match means no doc-body text to
   review. LLM correctly refuses to accept without evidence.
2. **TOC/summary excerpts** — Ship 32's poster-child pattern
   (one bullet-list line matching 43 different MUSTs). LLM
   correctly identifies these as document structure, not
   substantive evidence.

## Surfaced tuning insight (for Ship 35+)

17 of 20 sampled rejects (85%) have `excerpt=None`. These are
candidates where doc_mappings_target (0.60) alone fires — no
fingerprint match, no evidence text. They cross `arbiter_floor=0.40`
on a single-signal score and reach the LLM. But without evidence
text, the LLM has nothing to evaluate → always rejects.

**Follow-on optimization**: add an aggregator invariant —
"no fingerprint_excerpt → auto-drop regardless of score."
Would reduce arbiter-zone size + LLM cost per doc substantially
(this measurement had 94 arbiter candidates; ~75-80 would
auto-drop under the new invariant, leaving ~15-20 for LLM
review).

Alternative: raise `arbiter_floor` requirement — accept-floor
already requires `min_corroborators ≥ 2`; arbiter zone doesn't.
Adding the same requirement to arbiter would push single-signal
candidates to drop directly.

Both retire to Ship 35+ post-cutover data-driven tuning. This
arc's HITL sample confirms the current thresholds ship-safe;
optimization can iterate from production data via
`intake_consensus_log`.

## What Ship 34 delivered end-to-end

**Telemetry (schema_v89)**:
- `intake_consensus_log` table + RLS + indexes
- retention_class='diagnostic' per Ship 4'.b addendum
- arioncomply_app has INSERT/SELECT/DELETE

**Log writer (`rag/intake/consensus_extraction/log.py`)**:
- `log_consensus_result()` — silent-fail
- `build_candidates_sample()` — bounded top-K + arbiter zone

**Measurement script enhancement**:
- Two-pass run per doc: aggregator-only then arbiter-enabled
- Diff captures LLM verdict per arbiter-zone candidate
- Emits per-run JSON with leaf_id + must_id + excerpt + must_text
  + signals + LLM verdict + reason

**HITL validation**:
- 20/20 correct rejects on stratified sample
- Cutover unblocked; Ship 35 can proceed with confidence

## What Ship 34 did NOT do

- **Write-path cutover** — that's Ship 35's arc. Ship 34 was
  prep only.
- **Wire log writer into runtime** — the writer exists but no
  runtime path calls it yet. Ship 35 wires alongside cutover.
- **Threshold retuning** — HITL data supports the current
  thresholds. Post-cutover data may motivate the "no-excerpt →
  auto-drop" invariant; that's Ship 35+ work.
- **Cost measurement** — the arbiter pass adds ~$0.05/doc but
  we didn't formally instrument. `intake_consensus_log.cost_usd`
  column is there for it; measurement uses estimation only.

## Codified 2 lessons

### 1. HITL sample bounds where telemetry alone can't

Ship 33'.c said "LLM arbiter rejected 93/94" — a stark number
but ambiguous. Was it correct discrimination or reject-biased
prompt? Only human review of specific candidates disambiguates.
The 20-candidate sample took ~15 minutes but gave a definitive
answer that telemetry couldn't.

**Rule**: when telemetry shows an extreme rate (0% or 100% of
some class), human sample the class BEFORE trusting or fixing
the rate. The extreme may be correct; it may be broken; without
sampling you're guessing.

### 2. Signals without evidence should exit early

17 of 20 sampled rejects had no evidence text (no fingerprint
match). doc_mappings_target voted "this leaf is in-scope" but
there's no doc-body text to actually evaluate the MUST against.
The LLM correctly rejected — but it costs an LLM roundtrip to
say "there's nothing to evaluate."

**Rule**: signals that vote on SCOPE (candidate is in-scope) are
categorically different from signals that vote on EVIDENCE (this
excerpt shows the MUST is addressed). Scope signals alone should
not authorize LLM review — some evidence signal must corroborate
first. The threshold-tuning follow-on captures this.

## Sub-arc sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 34'.a | Design memo | schema + sample plan + thresholds locked |
| 34'.b | Implement + capture | schema_v89 applied; 94 arbiter verdicts dumped to JSON |
| **34'.c** | **HITL + eval + retro (this)** | **20/20 correct-reject; cutover unblocked** |

## Related

- [[ship-33-prime-arc-retrospective-2026-07-25]] — the consensus
  arc this validates
- [[ship-34-prime-a-validate-telemetry-design-2026-07-25]] — the
  design memo defining HITL thresholds
- Ship 35 (next) — cutover of the consensus write path;
  gate lifted by this arc

## Deferred / follow-on candidates from Ship 34

- **Post-cutover: no-excerpt-auto-drop invariant** — 85% of
  sampled arbiter zone is no-excerpt single-signal candidates.
  Auto-drop them pre-LLM to save cost + latency. Data will
  validate the exact threshold via `intake_consensus_log`.
- **Larger HITL sample** — 20 is small; a 100-candidate sample
  would give tighter bounds on the reject rate. If Ship 35
  surfaces unexpected patterns, expand the sample.
- **HITL of ACCEPTED consensus findings** — this arc reviewed
  rejects only. Reviewing accepts would confirm precision on
  the other side.
- **Signal weight iteration from real production data** — post-
  cutover, `intake_consensus_log` provides the tuning data. Ship
  35+ arcs can run periodic tuning passes.
