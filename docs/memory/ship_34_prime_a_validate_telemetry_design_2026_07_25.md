---
name: ship-34-prime-a-validate-telemetry-design-2026-07-25
description: "Ship 34'.a — design memo for the validation + telemetry arc that gates Ship 35 cutover of the consensus extraction path. Two deliverables: (1) intake_consensus_log schema_v87 + writer; (2) HITL sample review of the 93 arbiter rejects from Ship 33'.c to confirm LLM discrimination vs prompt-shape bias."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 34'.a — opens Ship 34 arc (validate + persist telemetry).
Prerequisite for Ship 35's write-path cutover.

## Motivation

Ship 33 shipped in shadow mode: consensus extraction runs only
from `scripts/measure_ship33_consensus.py`; the runtime pipeline
still uses the existing critic-verifier + concat path. To flip
the switch (Ship 35 cutover), two gaps close in Ship 34:

**Validation gap** — Ship 33'.c's LLM arbiter rejected 93 of 94
arbiter-zone candidates (98.9% reject rate). Two possible
interpretations:
- LLM is correctly discriminating weak candidates (arbiter zone
  contains genuinely borderline evidence)
- LLM is reject-biased by prompt shape (the system prompt has
  more "Prefer reject when..." guidance than "Prefer accept
  when...")

Cutting over without disambiguating risks shipping a system that
silently over-drops legitimate evidence.

**Telemetry gap** — post-cutover, production data will drive
threshold tuning + weight iteration. Without `intake_consensus_log`
capturing per-doc verdicts, we'd be tuning blind. Ship 33'.a-redux
designed the schema; Ship 34 implements it.

## Deliverable 1 — intake_consensus_log (schema_v87)

Locked from 33'.a-redux memo:

```sql
CREATE TABLE intake_consensus_log (
    id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id                UUID NOT NULL,
    upload_id                UUID NOT NULL,
    logged_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
    total_candidates         INT  NOT NULL,
    n_accept                 INT  NOT NULL,
    n_arbiter                INT  NOT NULL,
    n_drop                   INT  NOT NULL,
    n_arbiter_llm_accept     INT  NOT NULL DEFAULT 0,
    n_arbiter_llm_reject     INT  NOT NULL DEFAULT 0,
    signals_summary          JSONB NOT NULL,   -- per-signal fire counts
    candidates_sample        JSONB,            -- top 20 by score (tuning)
    latency_ms               INT,
    cost_usd                 NUMERIC(10, 6)
);
CREATE INDEX ON intake_consensus_log(tenant_id, logged_at DESC);
CREATE INDEX ON intake_consensus_log(upload_id);
```

Post-cutover this table is the tuning-data-source-of-truth.
Follow-on arcs (threshold tuning automation, signal-weight
iteration) will read from it.

**Retention**: `retention_class='diagnostic'` — sweep-eligible
after 90 days per Ship 4'.b addendum audit-log classification.

## Deliverable 2 — HITL sample of arbiter rejects

**Sample size**: 15-20 of the 93 rejects. Stratified across the 5
docs so no doc is under-represented.

**Sample record shape** (persisted to `intake_consensus_log.candidates_sample` OR a lightweight JSON file):
```json
{
  "leaf_id":       "req:A.7.4.3:accuracy_procedure",
  "must_id":       "item:A.7.4.3:proc_correction_link",
  "must_text":     "Cross-link to A.7.3.6 correction procedure...",
  "excerpt":       "This procedure references A.7.3.6 for...",
  "score":         0.62,
  "signals":       ["fingerprint_keyword", "must_semantic_topk", ...],
  "llm_verdict":   "reject",
  "llm_reason":    "generic reference, no concrete link"
}
```

**Review criteria** (for each sampled candidate):
- **Correct reject** — LLM's reasoning holds up; the excerpt
  is genuinely weak evidence for the MUST
- **Should have accepted** — the excerpt IS evidence; LLM
  over-rejected
- **Uncertain** — reasonable case either way

**Validation threshold**:
- Correct-reject rate ≥ 80% → LLM arbiter validated for cutover
- Correct-reject rate 60-80% → tune the prompt (add positive
  examples, rebalance "Prefer accept when" clauses); re-measure
- Correct-reject rate < 60% → LLM is over-rejecting; investigate
  before cutover

**Sample capture mechanism**: extend
`scripts/measure_ship33_consensus.py` to dump the arbiter-zone
verdicts (with LLM decision + reason) to a reviewable JSON file.
No new tooling required.

## What Ship 34 does NOT do

- **Cutover** — the write-path integration is Ship 35's work.
  Ship 34 is prep only.
- **Threshold retuning** — even if HITL surfaces slight
  over-rejection, we don't retune this arc. Ship 35 or 36
  handles iteration based on production data.
- **New signal additions** — Ship 33's 8 signals stay. Coverage
  gap for LLM-discovery-pass candidates remains open (Ship 35+
  work).
- **HITL review of Ship 32's original findings** — different
  scope; that would be a separate quality audit arc.

## Sub-arc plan

| Sub-arc | Focus | Outcome |
|---|---|---|
| **34'.a** (this) | Design memo — schema + HITL sample plan | Sample criteria + schema locked |
| 34'.b | Schema + writer + sample capture | Telemetry persisting; sample JSON produced |
| 34'.c | HITL review + eval + retro | Cutover-ready verdict; Ship 35 unblocked or blocked |

## Related

- [[ship-33-prime-arc-retrospective-2026-07-25]] — the arc this
  validates
- [[ship-33-prime-a-redux-extraction-consensus-design-2026-07-25]] —
  original schema spec (33'.a-redux §Telemetry)
- Ship 4'.b addendum (schema_v79) — audit-log classification
  precedent for `retention_class='diagnostic'`
