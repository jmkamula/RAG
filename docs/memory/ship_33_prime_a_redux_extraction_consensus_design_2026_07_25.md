---
name: ship-33-prime-a-redux-extraction-consensus-design-2026-07-25
description: "Ship 33'.a-redux — design memo for extending Ship 1's proven chat-consensus architecture to intake extraction. Supersedes the earlier semantic-fit-inline-gate design after user redirect motivated by strategic weight of automated evidence collection. 7-signal consensus with weighted aggregator + bounded LLM gatekeeper. Preserves determinism, keeps all curator investment (doc_mappings + fingerprints + per-protocol scoping + MUST embeddings) as signals with weights, collapses 7 bespoke gates into one aggregator with one threshold."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 33'.a-redux — supersedes the initial Ship 33'.a design
memo (which proposed a semantic-fit-inline gate — a 40-LOC patch).
After Ship 32's measurement finding + user pushback ("I thought
we had converged on a single path"), further discussion surfaced
that the right move is not another gate but the same
consensus-architecture pattern Ship 1 successfully deployed for
chat classification. This memo designs that pattern for extraction.

User's strategic framing:

> "automated evidence collection is a key feature trending
> heavily so we need to get this right for documents"

Given that, this memo over-invests in specification — signal
semantics, weights, thresholds, A/B plan, measurement targets,
migration — so the implementation arc (33'.b) can proceed from
a concrete plan.

## Motivation recap

Ship 32 measured the 5-doc corpus: 265 findings, 100% deterministic
grounding_method (above Ship 27's 89.2% baseline), but Processor Ops
surged 30 → 143 with 9% `evidence_text` uniqueness (one bullet-list
line producing 43 findings across 43 MUSTs). Root cause: sentence-
level multi-MUST attribution — each MUST's leaf-distinctive token
set (post-Ship-29 anchor injection) fired on the same summary
sentence. No single gate caught it because gates operate on
individual candidates in isolation; multi-attribution is a cross-
candidate property.

The chat classifier (Ship 1) faced an analogous problem: LLM alone
was stochastic on routing decisions; multiple deterministic signals
had to corroborate before it could confidently pin a query to a
specific ref. Consensus architecture solved it. Ship 33 applies
the same pattern to extraction.

## Architecture

### Unit of decision

**Chat consensus**: one query → many candidate refs → one winning
ref + question_type + framework.

**Extraction consensus**: one doc → many candidate `(leaf_id,
must_id)` pairs → per-candidate verdict (accept as finding /
drop / arbitrate via LLM).

Extraction's per-candidate structure is CLEANER than chat's
one-query-many-refs because each candidate is independent. No
tie-band ambiguity across families; no clarification prompt shape.

### Signal shape

Every signal returns per-candidate contributions:

```python
@dataclass
class ExtractionSignalOutput:
    name:         str            # e.g. "fingerprint_keyword"
    candidates:   dict[tuple[str, str], float]
        # (leaf_id, must_id) -> signal-local weight
    metadata:     dict           # signal-specific extras (e.g. match position)
    fired:        bool = True
```

Mirrors `rag/consensus/types.py::SignalOutput` verbatim in shape;
the difference is `candidates` (dict keyed by pair) instead of
`refs` (list ordered high-to-low).

### Signal catalog (7 signals + 1 negative gate)

| Name | Fires on | Weight | Determ? | Source |
|---|---|---|---|---|
| **`explicit_ref`** | Doc self-cites this candidate's control_ref (via enrich's `doc.explicit_refs`) | 1.00 | ✓ | Existing — reuse `enrich` output |
| **`doc_mappings_target`** | Filename YAML mapping (`db/doc_mappings/*.yaml`) names this candidate's leaf | 0.60 | ✓ | Existing — reuse `_scope_controls_via_doc_mappings` |
| **`fingerprint_keyword`** | AND-keyword set from `db/must_fingerprints/*.yaml` matches doc body for this MUST | 0.50 | ✓ | Existing — `_fingerprint_extract_matches` |
| **`must_semantic_topk`** | MUST is in `semantic_musts_in_scope(doc_text)` top-K=30 | 0.30 | ✓ | Existing but unused — `rag/intake/must_embedding_lookup.py:semantic_musts_in_scope` (defined; Ship 33 becomes first caller) |
| **`per_protocol_scope`** | Control is in `_scope_controls_via_retrieval` result | 0.20 | ✓ | Existing — per-standard Chroma queries |
| **`semantic_fit_gate`** | Cosine(fingerprint_excerpt, MUST anchor_description) ≥ threshold | +0.30 pass, −0.30 fail | ✓ | Existing — `_semantic_fit_ok` |
| **`content_shape_penalty`** | Match's surrounding sentence looks like field/header (`_looks_like_field_or_header`) | −0.50 | ✓ | Existing — Ship 11'.c gate |
| **`bridge_substantiveness`** *(optional, defer)* | Fingerprint match is inside a section spanning multiple MUSTs (Ship 16'.c) | +0.10 | ✓ | Existing — Ship 16'.c |

Note: No `retrieval` signal in the chat sense (Chroma cosine directly
becomes a base score) because for extraction, `must_semantic_topk`
and `per_protocol_scope` already play that role at different
granularities.

### Aggregator

Same math as `rag/consensus/aggregator.py::_fuse_ref_scores` — sum
weighted contributions per candidate, count positive-weight
corroborators. Adapt for per-candidate keying:

```python
def aggregate_extraction(
    signals: list[ExtractionSignalOutput],
    cfg:     ExtractionConsensusConfig,
) -> dict[tuple[str, str], CandidateVerdict]:
    fused_scores:  dict[tuple[str, str], float] = {}
    corroborators: dict[tuple[str, str], int]   = {}
    signals_by_c:  dict[tuple[str, str], list[str]] = {}

    for sig in signals:
        if not sig.fired:
            continue
        for candidate, weight in sig.candidates.items():
            fused_scores[candidate] = fused_scores.get(candidate, 0.0) + weight
            signals_by_c.setdefault(candidate, []).append(sig.name)
            if weight > 0:
                corroborators[candidate] = corroborators.get(candidate, 0) + 1

    verdicts: dict[tuple[str, str], CandidateVerdict] = {}
    for candidate, score in fused_scores.items():
        corrob = corroborators.get(candidate, 0)
        if score >= cfg.accept_floor and corrob >= cfg.min_corroborators:
            verdict = "accept"
        elif score >= cfg.arbiter_floor:
            verdict = "arbiter"          # borderline — LLM decides
        else:
            verdict = "drop"
        verdicts[candidate] = CandidateVerdict(
            score       = score,
            corrob      = corrob,
            signals     = signals_by_c.get(candidate, []),
            verdict     = verdict,
        )
    return verdicts
```

### Thresholds (initial — tune from Ship 32 data)

```python
@dataclass
class ExtractionConsensusConfig:
    accept_floor:       float = 0.75    # auto-accept
    arbiter_floor:      float = 0.40    # LLM arbiter zone (0.40..0.75)
    min_corroborators:  int   = 2       # accept requires 2 signals to agree
    # Weights (see signal catalog above) — one place for tuning
    explicit_ref_weight:          float = 1.00
    doc_mappings_weight:          float = 0.60
    fingerprint_weight:           float = 0.50
    must_semantic_weight:         float = 0.30
    per_protocol_weight:          float = 0.20
    semantic_fit_pass_weight:     float = 0.30
    semantic_fit_fail_weight:     float = -0.30
    content_shape_penalty:        float = -0.50
```

Threshold justification (initial):
- **accept_floor=0.75**: requires two moderate signals (e.g.
  fingerprint=0.50 + must_semantic_topk=0.30) OR one strong +
  one weak (explicit_ref=1.00 + anything positive)
- **arbiter_floor=0.40**: requires roughly one moderate signal.
  Below this, drop without LLM cost.
- **min_corroborators=2**: matches chat aggregator's baseline;
  fingerprint alone (weight 0.50, one signal) cannot auto-accept.
  Prevents the Ship 32 multi-attribution: 43 fingerprint hits
  on one sentence get score=0.50, corroborators=1 — falls to
  arbiter or drop unless another signal also fires.

**Tuning plan**: after 33'.b's A/B run, look at findings with
`verdict='arbiter'` — how many did the LLM accept vs reject.
If LLM accept rate is ≥ 80%, lower `accept_floor` (relax
determinism, more auto-accepts, less LLM cost). If ≤ 20%, raise
`arbiter_floor` (drop the low-hanging false positives without
LLM call).

### LLM gatekeeper (bounded arbiter)

Same discipline as `rag/consensus/gatekeeper.py`:
- Runs only for candidates with `verdict='arbiter'`
- Batched: single prompt with up to N (~30) borderline candidates
- LLM sees: candidate metadata (leaf title, MUST canonical text,
  MUST anchor description), the fingerprint match excerpt (if
  any), doc scope
- LLM outputs per-candidate: `accept` / `reject` / `modify`
  (with a new quote from doc body; verbatim-grounded via
  `_evidence_grounded`)
- **Hard-locks** (same shape as chat gatekeeper): LLM cannot
  invent new candidates; cannot override
  `verdict='accept'`; cannot override `verdict='drop'`. Only
  the `arbiter` zone is LLM-mediated.

Cost bound: one LLM call per doc for the entire arbiter batch.
Processor Ops with today's numbers: ~30-50 candidates in the
arbiter zone (down from 121 raw fingerprint hits after aggregator
filtering) → one batched prompt of ~10-15K tokens → ~$0.10/doc
for the arbiter pass. Plus one embedding call for
`must_semantic_topk`. Total: probably below current $0.24/doc.

## Data path (side-by-side with existing)

New module: `rag/intake/consensus_extraction/`
```
consensus_extraction/
    __init__.py
    types.py                — ExtractionSignalOutput, CandidateVerdict
    config.py               — ExtractionConsensusConfig
    aggregator.py           — aggregate_extraction()
    gatekeeper.py           — bounded LLM arbiter (batched)
    orchestrator.py         — run_extraction_consensus(doc, controls) → findings
    signals/
        __init__.py
        explicit_ref.py
        doc_mappings_target.py
        fingerprint_keyword.py     — wraps existing _fingerprint_extract_matches
        must_semantic_topk.py      — first caller of semantic_musts_in_scope
        per_protocol_scope.py      — wraps _scope_controls_via_retrieval
        semantic_fit_gate.py       — wraps _semantic_fit_ok
        content_shape_penalty.py   — wraps _looks_like_field_or_header
    log.py                  — writes to intake_consensus_log (schema_v87)
```

Signal modules are thin wrappers around existing code — Ship 33
does not rewrite fingerprint matching, semantic lookup, or
content-shape logic. It just re-shapes them as SignalOutput
producers.

### Enrich integration

Enrich stage unchanged. Consensus reads:
- `doc.explicit_refs` (Signal explicit_ref input)
- `doc.standard_ids` (per_protocol_scope filter)
- `doc.topic_tokens` (doc_mappings_target matching)
- `doc.markdown / doc.full_text` (fingerprint_keyword + semantic
  queries)

### Feature flag + A/B

`USE_CONSENSUS_EXTRACTION` env flag (like `USE_CRITIC_VERIFIER_PASS`
before default-on):
- **0** (default first): existing critic-verifier + concat path
  runs. Consensus runs in **shadow mode** — produces findings but
  they're logged, not written. Comparison in
  `intake_consensus_log` (new).
- **1**: consensus is the write path. Critic-verifier + concat
  path skipped.

Shadow mode gives us the A/B window without changing tenant-
facing behavior. Compare per-doc: `n_findings`, `evidence_text
uniqueness`, `distinct MUSTs`, `LLM cost`, `latency`.

## Success + failure signals for 33'.b

Re-measure the 5-doc corpus:

| Metric | Ship 32 (baseline) | Ship 33 target |
|---|---|---|
| Total findings (5-doc) | 265 | 130-180 |
| Processor Ops findings | 143 | 30-60 |
| Processor Ops evidence_text uniqueness | 11 (9%) | ≥ 60% |
| Deterministic grounding_method % | 100% | 100% (stays) |
| Cost per doc | ~$0.24 | ≤ $0.30 |
| Findings-per-LLM-call ratio | ~1:1 (critic-verifier) | ~30:1 (batched arbiter) |

**Failure signals**:
- Deterministic % < 100% (bug: findings taking a non-consensus path)
- Total findings < 100 (over-tight aggregator; recall regression)
- Any doc missing a known-should-be-found finding from Ship 10's
  approve list

### Telemetry — `intake_consensus_log` (schema_v87)

```sql
CREATE TABLE intake_consensus_log (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id         UUID NOT NULL,
    upload_id         UUID NOT NULL,
    logged_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    total_candidates  INT  NOT NULL,
    n_accept          INT  NOT NULL,
    n_arbiter         INT  NOT NULL,
    n_drop            INT  NOT NULL,
    n_arbiter_llm_accept  INT NOT NULL,
    n_arbiter_llm_reject  INT NOT NULL,
    signals_summary   JSONB NOT NULL,   -- per-signal fire counts + weight sums
    candidates_sample JSONB,            -- top 20 candidates by score, for tuning
    latency_ms        INT,
    cost_usd          NUMERIC(10, 6)
);
```

Provides tuning data: which signals fire most, what the arbiter
LLM says vs the deterministic score would have said, per-doc
cost.

## Sub-arc plan

| Sub-arc | Focus | Outcome |
|---|---|---|
| **33'.a-redux** (this) | Full design memo | Signal catalog + weights + thresholds + A/B plan locked |
| 33'.b | Implement consensus_extraction module + shadow-mode A/B on 5-doc corpus | Numbers side-by-side; go/no-go on switching write path |
| 33'.c | Cutover (if 33'.b clean) OR tuning iteration; eval + retro | Consensus becomes write path; critic-verifier + concat retired |

## What Ship 33 does NOT do

- **Not** replace the fast paths (templated markdown, templated
  xlsx, workbook_persistence, STRUCTURED). Consensus is the LLM-
  lane refactor only.
- **Not** replace enrich (Stage 3). Enrich still routes doc into
  the LLM lane and populates `explicit_refs` + `topic_tokens`.
- **Not** replace the writer (Stage 5). `write_findings` still
  writes; consensus just decides WHICH findings to hand it.
- **Not** touch chat consensus. Same pattern, different code
  path.
- **Not** touch xfw_proposer. Cross-framework bridges continue
  their own path downstream of the writer.

## Migration + retirement

After 33'.c cutover:

**Retired code**:
- `_run_critic_verifier_pass` (or its priming/extend machinery
  becomes obsolete; the LLM arbiter takes over its role)
- `findings = fp_findings + llm_findings` concat at
  extractor.py:309
- Gate cascade inside `_extract_via_fingerprints` (specificity
  gate + content-shape gate + inline semantic-fit) — those become
  standalone signal modules
- `_build_priming_set` / `_build_extend_pool` — no longer needed
- Auto-approve corroboration in `posture_writer` (Wave 3 N-of-M)
  — consensus verdict IS the acceptance decision; writer becomes
  a dumb persister again

**Kept as-is**:
- Fingerprint catalog (598 files) — wrapped as signal
- doc_mappings YAML (~100 files) — wrapped as signal
- MUST-level Chroma collection — wrapped as signal
- Per-standard Chroma collections — wrapped as signal
- `_semantic_fit_ok` — wrapped as signal
- `_looks_like_field_or_header` — wrapped as negative-weight signal
- Enrich stage, reader stage, writer stage — untouched

**Net LOC change** (rough):
- `rag/intake/extractor.py`: ~3000 LOC → ~500 LOC (or the LLM lane
  becomes a thin dispatcher into consensus_extraction)
- New `rag/intake/consensus_extraction/`: ~700 LOC across
  orchestrator + aggregator + gatekeeper + 7 signal modules +
  types + config + log
- **Net**: ~2000 LOC reduction, one architecture instead of
  seven bespoke gates.

## Codified properties (locked in this design)

1. **Signal parity with chat consensus** — same shape
   (`SignalOutput`, `aggregate`, `gatekeeper`), same discipline
   (bounded LLM arbiter, curator lexicon dominant).
2. **Determinism** — high-score + low-score decisions made by
   deterministic aggregator. LLM sees only the arbiter zone.
3. **Curator investment preserved** — every existing catalog
   (fingerprint / doc_mappings / MUST embeddings / per-protocol
   Chroma) becomes a signal with a weight.
4. **Uniform provenance** — one `grounding_method` value
   (`consensus`, new; or continue `extractor_verbatim`) rather
   than seven bespoke sources. Auditor gets one story.
5. **Tunable from data** — thresholds + weights in one
   `ExtractionConsensusConfig`; `intake_consensus_log` provides
   the data.
6. **Shadow-mode A/B before cutover** — no tenant-facing risk
   during 33'.b measurement window.

## Threshold-tuning-from-data plan (33'.c input)

After 33'.b shadow-mode run on 5-doc corpus, query
`intake_consensus_log` for:

1. **Arbiter LLM accept rate** by score band
   (0.40-0.50 / 0.50-0.60 / 0.60-0.75). If 0.60-0.75 band's LLM
   accept rate ≥ 90%, lower `accept_floor` to 0.60.
2. **Signal fire distribution** per candidate. Signals that
   fire but never contribute to accepted candidates are
   candidates for weight-down or removal.
3. **Multi-attribution collapse** — for Ship 32's "43-findings
   on one sentence" case, confirm consensus produces ≤5
   findings on the same sentence.
4. **Recall vs Ship 10 baseline** — compare which of Ship 10's
   48 approves still surface. Missing ones may indicate
   threshold too tight; extras may indicate threshold too loose
   (or genuine recall gain).

Any threshold change post-33'.c gets an eval regression check.

## Related

- **Chat consensus** (Ship 1) — proven pattern this arc mirrors:
  - `rag/consensus/aggregator.py` — the reference implementation
  - `rag/consensus/types.py` — SignalOutput / ConsensusResult
    shape
  - `rag/consensus/gatekeeper.py` — bounded LLM arbiter pattern
  - `rag/consensus/config.py` — ConsensusConfig weights + thresholds
- [[ship-32-prime-arc-retrospective-2026-07-25]] — measurement
  arc that surfaced the multi-attribution problem this arc
  addresses
- [[ship-11-prime-arc-retrospective-2026-07-21]] — critic-verifier
  arc whose two-path shape this arc retires
- `docs/critic_verifier_design_2026_07_11.md` — the original
  critic-verifier design; Ship 33 supersedes it
- Original Ship 33'.a (semantic-fit inline gate) — superseded by
  this memo; kept in git history as `b15e44b` for context
