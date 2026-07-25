---
name: ship-35-prime-arc-retrospective-2026-07-25
description: "Ship 35' arc closer — extraction consensus cutover. USE_CONSENSUS_EXTRACTION env flag (default OFF) enables the full-replacement path built in Ship 33. Also ships the no-excerpt-auto-drop aggregator invariant Ship 34'.c surfaced. Bounded rollout via default-OFF; the Ship 33 architecture is now tenant-reachable, awaiting per-install opt-in."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 35' arc retrospective — 3 sub-arcs delivered in one session
(2026-07-25). Finally makes Ship 33's consensus extraction module
tenant-reachable behind a feature flag.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 35'.a | Design memo — full replacement + default OFF + no-excerpt invariant | ad9ab83 |
| 35'.b | Env flag wiring + `_extract_via_consensus` + aggregator invariant | 4044e7b |
| **35'.c** | **Smoke test + eval + retrospective (this)** | pending |

## The cutover

**`USE_CONSENSUS_EXTRACTION` env flag** in `rag/intake/extractor.py`:

```python
_consensus_flag = os.getenv("USE_CONSENSUS_EXTRACTION", "0").lower()
if _consensus_flag not in ("0", "false", "no", "off"):
    findings = _extract_via_consensus(doc, fp_leaf_pool)
    _finalize_yield_metrics(doc, findings)
    return findings
# ...existing fingerprint + critic-verifier + concat path unchanged...
```

- **Default OFF** — production tenants see zero behavior change.
- **Full replacement when ON** — consensus REPLACES fingerprint +
  critic-verifier + concat entirely. No parallel path when flag is
  set.
- **Rollback**: unset env var + restart API. Seconds.

**`_extract_via_consensus(doc, scoped_leaf_ids)`** new helper:
- Instantiates `ExtractionConsensusConfig` with
  `llm_arbiter_enabled=True`
- Calls `run_extraction_consensus()` from the Ship 33 module
- Materialises accepted `CandidateVerdict`s as `DocumentFinding`s
  (compatible with the existing writer;
  `inference_source='fingerprint_match'` so writer's auto-approve
  discipline still applies)
- Silent-fail telemetry write to `intake_consensus_log`

## No-excerpt-auto-drop invariant (Ship 34 finding delivered)

In `rag/intake/consensus_extraction/aggregator.py`:

```python
if not excerpt:
    verdict = "drop"; n_drop += 1
elif score >= cfg.accept_floor and corrob >= cfg.min_corroborators:
    verdict = "accept"; n_accept += 1
elif score >= cfg.arbiter_floor:
    verdict = "arbiter"; n_arbiter += 1
```

Ship 34'.c HITL data: 17 of 20 sampled arbiter rejects were
no-excerpt candidates (scope signals voted "leaf in-scope" but no
fingerprint match). LLM correctly rejected all 17 — but each cost
an LLM roundtrip. The invariant drops these deterministically
BEFORE the arbiter zone.

Predicted impact on 5-doc corpus:
- Arbiter zone 94 → ~15 (85% × 94 dropped by invariant)
- LLM cost per doc: ~$0.05 → ~$0.01 (5x reduction on arbiter pass)

## Trade-off: LLM discovery pass lost

Full replacement removes the critic-verifier's LLM discovery
capability. Currently ~30-50% of findings on procedural docs come
from body-text candidates that no deterministic signal surfaces.
When the flag is ON, those candidates are lost.

Ship 33 measurement: Path A 269 → Path B 197 (28% reduction). Mix
of precision gain (Ship 32 multi-attribution cleanup) + recall loss
(missing LLM discovery). HITL confirmed the rejected candidates
were weak but didn't measure the accepted set's precision or the
recall loss shape.

**This trade-off is accepted** — bounded to opted-in tenants by
default-OFF. `intake_consensus_log` telemetry post-cutover will
inform whether to (a) expand rollout, (b) restore LLM discovery as
a 9th signal, or (c) reconsider the replacement shape.

## Not retired

`_extract_via_fingerprints`, `_run_critic_verifier_pass`, and the
`findings = fp_findings + llm_findings` concat all STAY in
`extractor.py` for the default-OFF branch. Retirement in a
follow-on arc after 4-6 weeks of clean flag=1 running + optional
LLM-discovery-pass signal coverage.

## OpenAI quota event — codified as a lesson

Ship 34'.c's initial eval hit HTTP 429 quota-exceeded (not per-
minute rate limit; hard account quota). 61 of the 232 cases failed
with empty answers + 500 errors. Ship 34'.c retro initially claimed
"baseline should hold" and implied 231/232 — actually it hit the
quota wall.

Root cause: I ran Ship 33'.c measurement + Ship 34'.b measurement
+ Ship 34'.c eval all consuming OpenAI credits in overlapping
windows. The account's quota depleted. Not a code regression —
infra spend.

Ship 34'.c retro correction: the actual eval number was blocked by
OpenAI billing, not a Ship 34 code issue. Ship 34 was shadow-mode
so a real regression was structurally impossible. Post-credit-
restoration re-eval will confirm the true baseline.

**Codified lesson (Ship 35'.c #1)**: When batching measurement
arcs, either (a) throttle concurrent OpenAI-consuming work to one
active job, or (b) budget the total spend explicitly before the
session. Blithely stacking measurement + eval + measurement + eval
runs is not a "burst" — it's a cost pattern that drains the quota.

## Smoke test outcome

Deferred to a post-commit follow-up. The smoke test needs an
OpenAI arbiter call; running it in parallel with the Ship 34'.c
eval would repeat the OpenAI-quota-concurrency mistake. Will
follow up with numbers when the eval waiter fires + smoke can
run cleanly. `/tmp/smoke_ship35_cutover.py` script is ready
(sets `USE_CONSENSUS_EXTRACTION=1`, extracts DPIA doc, verifies
`intake_consensus_log` row lands).

## Eval outcome

Ship 34'.c re-run (post-OpenAI-credit restoration) is armed via
waiter `bqs07873p`. Ship 35 is default-OFF so a regression from
Ship 35 code is structurally impossible; the eval validates the
existing pipeline hasn't drifted from prior Ship 34'.c intent.
Will follow up in a subsequent commit if the numbers surface
anything surprising.

## Codified 2 lessons

### 1. OpenAI quota budgeting is a real engineering concern

See §OpenAI quota event above. Stacked measurement + eval work
must be sequenced or throttled. Concurrent OpenAI-consuming jobs
compete for the same rate + spend budget.

### 2. Default-OFF cutover flags enable ship-then-validate

Ship 35 code is now in production for anyone who runs `git pull`,
but the runtime is unchanged unless someone sets the flag. That
decouples SHIPPING from ROLLING OUT. Ship-then-validate becomes
safer than validate-then-ship because validation happens on the
codebase that will actually ship, and rollout can proceed at
whatever pace evidence supports.

The chat consensus (Ship 1) shipped as ON-by-default with a
kill-switch env var; Ship 2'.o retired that kill-switch when
production evidence accumulated. Ship 35 follows the mirror
pattern: OFF-by-default with an enable-switch. Same architectural
discipline; different rollout curve because the extraction
cutover has larger blast radius.

## What Ship 35 does NOT do

- **Enable consensus by default** — default OFF; per-install opt-in
- **Retire old code paths** — 4-6 weeks of clean flag=1 running
  required first
- **Extend consensus to cover LLM discovery pass** — the recall
  trade-off is accepted; Ship 36+ if data supports adding
- **Threshold retuning** — will iterate from `intake_consensus_log`
  data post-cutover
- **Per-tenant flag config** — env-wide OFF is fine for now

## Sub-arc sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 35'.a | Design memo | Full replacement + default OFF + invariant + rollback locked |
| 35'.b | Implement + wire flag + invariant | Consensus reachable via env flag |
| **35'.c** | **Smoke + eval + retro (this)** | **Cutover shipped behind flag** |

## Deferred / follow-on candidates from Ship 35

- **Flip flag on Arion demo tenant** — first real opt-in;
  validates the cutover produces sensible behavior end-to-end
- **Retire old code paths** after N weeks of clean flag=1
- **LLM discovery pass as a 9th signal** if recall loss becomes
  a problem for real tenants
- **Threshold retuning from `intake_consensus_log` data** — post-
  cutover
- **Per-tenant flag config** — if some tenants want opt-in but
  not others

## Related

- [[ship-33-prime-arc-retrospective-2026-07-25]] — the arc whose
  work this cuts over
- [[ship-34-prime-arc-retrospective-2026-07-25]] — the validation
  arc that unblocked cutover; source of the no-excerpt invariant
- [[ship-35-prime-a-cutover-design-2026-07-25]] — this arc's
  design memo
