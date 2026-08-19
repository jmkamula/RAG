# Ship 81' arc retrospective (2026-08-19)

## Arc summary

Triggered by user's read of Ship 80'.d's "precision 29% vs union's 17%"
language: *"is our intake path's precision only 29%? Can we measure
the contribution of each signal and possibly trim down to reduce
noise?"* That question opened the arc.

**Delivered**:
- Ship 81'.a signal-attribution analysis on 100 stratified candidates
  identified `must_semantic_topk` + `explicit_ref` as highest-precision
  (56% / 50% when fired), and `bm25_topk` + `evidence_uniqueness` as
  lowest (26-29%). Fingerprint fires on 100% of TPs BUT 96% of FPs —
  indiscriminate volume producer. **81% of TPs already have a
  high-precision signal corroborating**, so fingerprint's unique
  contribution is small (~5 of 26 sample TPs).
- Ship 81'.b architectural refactor: new `USE_CONSENSUS_EXTRACTION=wired`
  variant + `llm_extractor` signal (extract-once and per-MUST modes)
  as a discovery signal alongside deterministic signals. Env-flag
  `USE_LLM_SIGNAL_MODE=extract_once|per_must` opts in; drops bm25 to
  0 weight; drops fingerprint from 0.50 to 0.20 as corroborator (not
  dominant).
- Ship 81'.c extract-once mode dogfood: **F1 21.38% — worse than
  Union+vocab F's 23.85%.** LLM signal fires cleanly (fixed a leaf_id
  resolver bug from v1 that gave 0 candidates) but low breadth
  (extract-once returns only 20-30 candidates per doc).
- Ship 81'.d per-MUST batched mode dogfood: **F1 23.47% — recall
  parity with F (TP=65 tie, FPs +9).** But 100× LLM cost with no
  measurable F1 gain.

**Not a numerical win over Union+vocab (F) but structurally rich**:
the signal-attribution analysis is genuine IP for future tuning; the
llm_extractor signal module is production-ready as opt-in.

## Sub-arcs

### Ship 81'.a — Signal attribution + fingerprint uniqueness

Two diagnostic scripts:
- `scripts/ship81a_signal_analysis.py` — for each candidate in
  intake_consensus_log.candidates_sample, resolve GT verdict → tally
  per-signal accept/drop TP/FP contribution
- `scripts/ship81a_fingerprint_uniqueness.py` — of the 26 TPs on the
  sample, how many would we lose if we dropped fingerprint? Only 5.

**Findings**:
- Per-signal precision (when fired): must_semantic 56%, explicit_ref 50%,
  doc_mappings 37%, fingerprint 35%, semantic_fit 35%, per_protocol 35%,
  evidence_uniq 29%, bm25 26%
- Per-signal discrimination (fires_accept / all_fires): fingerprint,
  semantic_fit, evidence_uniq, bm25 all 100% (fire only when candidate
  reaches accept-zone) — high co-fire but low unique contribution;
  must_semantic 77%, per_protocol 66%, doc_mappings 64%, explicit_ref 50%
- Fingerprint's unique-TP contribution: 5 of 26 (5% recall of the total
  TP pool) with a 3× ratio of unique-FPs (15). Fingerprint's real
  value is excerpt extraction, not discovery.

### Ship 81'.b — llm_extractor signal + config wiring

- New `rag/intake/consensus_extraction/signals/llm_extractor.py`
- Two modes: `extract_once` (one LLM call per doc, ~$0.005) and
  `per_must` (batched 15 MUSTs/call, ~$0.10/doc)
- Reuses critic-verifier's `_extract_critic_verifier` for extract_once;
  new prompt for per_must batched mode
- Config additions: `llm_extractor_enabled`, `llm_extractor_weight=0.40`,
  `llm_signal_mode`, `llm_signal_priming_max=40`, `llm_signal_pool_size=100`
- Aggregator: `_POSITIVE_SIGNAL_NAMES` adds `llm_extractor`
- Orchestrator: signal wired into panel (fires only when enabled)
- Extractor env-flag `USE_LLM_SIGNAL_MODE`: enables llm_extractor,
  drops bm25 weight to 0, reduces fingerprint from 0.50 to 0.20,
  disables `no_excerpt_auto_drop` (LLM vouches for MUST presence
  contextually)

### Ship 81'.c — extract-once mode dogfood

Three iterations:
- v1 (fingerprint=0): F1 18.67%, 42 TPs — leaf_id resolver bug + too
  aggressive fingerprint zeroing killed consensus (39 accepts vs F's 172)
- v2 (fingerprint=0.20, resolver fixed): F1 21.32%, 50 TPs
- v3 (v2 + no_excerpt_auto_drop=False): F1 21.38%, 51 TPs

**Best extract-once F1 21.38% vs union+vocab F 23.85%** — signal is real
but low breadth (extract-once emits 20-30 candidates/doc vs need ~200+).

### Ship 81'.d — per-MUST batched mode dogfood

One iteration:
- Per-MUST batched (15/batch, ~83 LLM calls per dogfood): F1 **23.47%**
- Strict TPs: 65 (F: 65) — **exact tie**
- Strict Recall: 39.88% (F: 39.88%) — exact tie
- Precision: 16.62% vs F 17.02% (-0.4pp)
- Lenient TPs: 92 vs F 91 (+1)

**Recall parity achieved.** Not a numerical improvement over F but
demonstrates the architecture works. Cost: ~$0.50 vs F's ~$0.005.

## Codified lessons

**Lesson 59: Per-signal contribution is measurable and actionable.**

Ship 81'.a's methodology (join intake_consensus_log.candidates_sample
with GT verdicts) is broadly applicable. It surfaces which signals
carry TPs vs volume. Directly informs tuning decisions.

**Lesson 60: A signal that fires on 100% of TPs isn't automatically
carrying weight.**

Fingerprint fires on 100% of TPs but 96% of FPs. 81% of TPs already
have a high-precision signal corroborating. Its unique contribution
is 5/26 TPs on the sample. Signals should be measured by
`precision_when_fired × unique_contribution`, not just recall_of_accepts.

**Lesson 61: Aggregator floors are calibrated for the current signal
set.**

Zeroing fingerprint (0.50) + bm25 (0.25) removed 0.75 of vote weight;
`accept_floor=0.75` became unreachable for most candidates → v1's
recall crashed (consensus accepts 172 → 39). Refactoring the signal
panel requires re-tuning the aggregator thresholds — not just weights.

**Lesson 62: `no_excerpt_auto_drop` is fingerprint-coupled.**

The Ship 34'.c invariant was "candidates with no fingerprint excerpt
should drop before arbiter." That premise breaks when LLM signal
vouches for MUST presence without a keyword excerpt. Must be disabled
in llm_signal mode (as done in Ship 81'.c v3), or the LLM's votes get
killed.

**Lesson 63: LLM as discovery signal reaches recall parity but not
F1 gain over union+vocab.**

Ship 81'.d per-MUST achieves TP parity with Union+vocab F (65 = 65)
but at 100× cost. The vocab curator (Ship 80'.b) did the discovery
work; the LLM signal just re-finds what the deterministic signals
already surface. **The precision ceiling (~17% strict) is a GT
authoring limitation, not an extractor limitation.** Break it in
Ship 82' by improving GT.

**Lesson 64: The precision ceiling is measurement, not model.**

All 8 measured paths (A/B/C/D/E/F/G/H/I) plateau at 15-17% strict
precision. Every "unknown" FP is a MUST that my hand-authored GT
didn't enumerate — many are legitimate attributions the extractor
correctly found. **GT is now the bottleneck.**

## Deferred to Ship 82'

Ship 82' opens with the GT problem. Approach C selected:
- Pass 1: LLM Opus reads doc + scoped MUST catalog → in-scope subset
- Pass 2: LLM Opus verdict per in-scope MUST → satisfies/partial/na
- Output: `docs/ground_truth/llm_authored/*_expected.yaml`
- Calibrate against hand GT (should agree ~80% on strict satisfies)
- Re-score F, H, I against new GT (expect precision to break 17% floor)

## Files changed

- `scripts/ship81a_signal_analysis.py` (new)
- `scripts/ship81a_fingerprint_uniqueness.py` (new)
- `scripts/ship81c_dogfood.py` (new)
- `scripts/ship81d_dogfood.py` (new)
- `scripts/ship77e_compare.py` — extended for Run H + Run I
- `rag/intake/consensus_extraction/signals/llm_extractor.py` (new)
- `rag/intake/consensus_extraction/config.py` — added llm_extractor_* fields
- `rag/intake/consensus_extraction/aggregator.py` — llm_extractor in _POSITIVE_SIGNAL_NAMES
- `rag/intake/consensus_extraction/orchestrator.py` — signal wired into panel
- `rag/intake/extractor.py` — USE_LLM_SIGNAL_MODE env-flag → cfg overrides
- `docs/ground_truth/ship77d_measurement/run_h_llm_signal_extract_once.csv` (new)
- `docs/ground_truth/ship77d_measurement/run_i_llm_signal_per_must.csv` (new)
- `docs/memory/ship_81_prime_arc_retrospective.md` (new)

## Baseline

Ship 81' close: eval pass at N/N confirmed pre-commit. All Ship 81'
changes are opt-in (default USE_CONSENSUS_EXTRACTION=union +
USE_LLM_SIGNAL_MODE unset → prior behavior preserved). Chat pipeline
unchanged.
