# Ship 77'.d — dual-path measurement outputs

Raw extractor outputs on the 5 baseline docs for the 77'.e first-
principles compare against ground truth.

## Files

- **run_a_consensus.csv** — findings emitted when consensus path
  (`USE_CONSENSUS_EXTRACTION=1`) was active. 168 findings across
  5 docs (100 fingerprint_match + 68 xfw_bridge). Deactivated
  after snapshot with `deletion_reason='ship77d_run_a_snapshot'`.

- **run_b_critic.csv** — findings emitted with default critic-
  verifier path (flag OFF). 251 findings across 5 docs (188
  fingerprint_match + 24 xfw_bridge + 39 extracted via LLM).

- **consensus_telemetry.csv** — per-doc consensus aggregator
  telemetry from `intake_consensus_log`: candidates + accept +
  arbiter + drop counts + LLM cost.

## Aggregate counts

| Path | Total | fingerprint | extracted (LLM) | xfw_bridge |
|------|------:|-----------:|--------------:|----------:|
| Consensus (A) | 168 | 100 | 0 | 68 |
| Critic-verifier (B) | 251 | 188 | 39 | 24 |

## Per-doc

| Doc | Consensus (A) | Critic-verifier (B) |
|-----|-------------:|--------------------:|
| DPIA | 34 | 13 |
| RoPA | 46 | 16 |
| Consent | 40 | 65 |
| Processor Ops | 24 | 145 |
| DQA | 24 | 12 |
| **Total** | **168** | **251** |

### Preliminary observation

Consensus produces **fewer findings** than critic on 3 of 5 docs
(DPIA, RoPA, DQA) and **way fewer** on Processor Ops (24 vs 145 —
6x reduction). Consensus produces MORE on Consent (40 vs 65 —
wait that's less. Let me re-read: 40 < 65 → critic wins). Critic
produces more overall — but that doesn't tell us precision or
recall until we score against ground truth in 77'.e.

**Processor Ops is the surprising signal**: critic-verifier
produces 145 findings vs consensus's 24. The ground truth
(processor_ops_expected.yaml) has ~71 strict expected findings.
So critic overshoots by 2x; consensus undershoots by 3x. Neither
matches ground truth well without further analysis of what's
actually in the findings vs what SHOULD be there.

## Consensus telemetry (aggregator internals)

Aggregator saw 824 total candidates across 5 docs (avg 164/doc).
Accepted 100 (12%). No LLM arbiter calls fired (all landed in
accept or drop zones directly). Deterministic-only run.

| Doc | Candidates | Accept | Arbiter | Drop | LLM (A/R) | Latency ms |
|-----|----------:|------:|-------:|-----:|:---------:|----------:|
| DQA | 135 | 16 | 0 | 119 | 0/0 | 36891 |
| Consent | 135 | 17 | 0 | 118 | 0/0 | 41574 |
| DPIA | 163 | 28 | 0 | 135 | 0/0 | 43540 |
| RoPA | 136 | 21 | 0 | 115 | 0/0 | 45985 |
| Processor Ops | 255 | 18 | 0 | 237 | 0/0 | 68232 |

## Method notes

1. Baseline: all 5 docs had 0 active findings before Run A.
2. Run A executed against `USE_CONSENSUS_EXTRACTION=1`. After
   completion the 168 findings were snapshotted here + then
   deactivated with `is_active=false, deletion_reason=
   'ship77d_run_a_snapshot'` so Run B started clean.
3. Run B executed with the flag unset (default). API restarted
   between runs to reset the env var.
4. Both runs used the same 5 upload_ids + the admin re-extract
   endpoint. Same doc contents. Same extractor plumbing except
   the consensus flag.

## Next: Ship 77'.e

Compare each path's findings against the 5 ground-truth yamls
(dpia_expected.yaml + ropa_expected.yaml + consent_expected.yaml
+ processor_ops_expected.yaml + dqa_expected.yaml). Compute
precision + recall per (doc, path) pair against strict
(satisfies only) + lenient (satisfies + partial) expected sets.

Also: characterize false positives by class (fingerprint over-
fire? LLM hallucination? Wrong-artefact per ground-truth
principle?).
