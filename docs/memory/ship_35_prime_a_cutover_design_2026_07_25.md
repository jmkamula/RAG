---
name: ship-35-prime-a-cutover-design-2026-07-25
description: "Ship 35'.a — design memo for the extraction consensus cutover. Full replacement of _extract_via_fingerprints + _run_critic_verifier_pass + concat when USE_CONSENSUS_EXTRACTION=1; default OFF for safe rollout. Ship 34'.c HITL validation (20/20 correct-reject) unblocked this arc. Also ships the no-excerpt-auto-drop aggregator invariant Ship 34 surfaced."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 35'.a — opens Ship 35 arc (cutover of the extraction
consensus module). Ship 34'.c HITL validation returned 20/20
correct-reject on the sampled arbiter rejects, unblocking this
arc. The consensus code from Ship 33 finally materializes as
tenant-facing behavior — behind a feature flag for safe rollout.

## Motivation

Ship 33 built + measured the consensus module across 3
calibration iterations, plus LLM arbiter (33'.c). Ship 34
delivered telemetry + HITL validation. Both arcs shipped in
shadow mode — the runtime pipeline still uses the existing
`_extract_via_fingerprints` + `_run_critic_verifier_pass` +
`fp_findings + llm_findings` concat.

Ship 35 flips the switch. Full replacement when
`USE_CONSENSUS_EXTRACTION=1`; default OFF ensures zero behavior
change until an operator opts in per install.

## Cutover shape

**User selected**: full replacement, default OFF.

- **Full replacement** — when the flag is ON, consensus REPLACES
  `_extract_via_fingerprints`, `_run_critic_verifier_pass`, AND
  the `findings = fp_findings + llm_findings` concat. One code
  path (extract via consensus) instead of two.
- **Default OFF** — `USE_CONSENSUS_EXTRACTION` env var defaults
  to "0". No production tenant sees any change on default
  installs. Ship 36+ decides adoption per tenant / per install.

The trade-off: full replacement loses the **LLM discovery pass**
that today finds candidates in body text with no deterministic
signal (~30-50% of findings on procedural docs). The consensus
module only processes candidates surfaced by
fingerprint + doc_mappings + must_semantic + explicit_ref +
per_protocol. Findings that only the LLM discovery pass would
find are LOST when the flag is ON.

Ship 33 measurement quantified this: Path A produced 269
findings, Path B produced 197 — a 28% reduction. Some of that
reduction is genuine precision gain (Ship 32 multi-attribution
cleanup); some is recall loss from the missing LLM discovery
pass. HITL sample confirmed the rejected candidates were weak,
but did not measure the accepted set's precision or the
missing-recall shape. **This is a known and accepted risk of
full replacement.**

Mitigation: default-OFF means the risk is bounded to opted-in
tenants. Post-cutover, `intake_consensus_log` data + tenant
feedback drive whether to expand rollout or reconsider the
replacement shape.

## Ship 34 tuning insight — no-excerpt-auto-drop invariant

Ship 34'.c sampled 20 arbiter rejects; 17 of 20 had
`fingerprint_excerpt=None`. These are candidates where
doc_mappings_target (0.60) or per_protocol_scope (0.10) voted
"leaf is in-scope" but no fingerprint match means no doc-body
text for the LLM to evaluate against. The LLM correctly
rejected all 17 — but each one cost an LLM roundtrip to say
"nothing to evaluate."

Ship 35'.b ships the invariant: **in the aggregator, candidates
with no `fingerprint_excerpt` and score below `accept_floor`
auto-drop instead of entering the arbiter zone.**

Impact estimate from Ship 34 data:
- Current arbiter zone: 94 candidates across 5-doc corpus
- No-excerpt candidates in arbiter zone: ~80 (85% × 94)
- Post-invariant arbiter zone: ~14 candidates
- LLM cost per doc: ~$0.05 → ~$0.01 (5x reduction on arbiter
  pass)
- Latency: proportional reduction

The invariant is a signal-family distinction: **scope signals
alone should not authorize LLM review**. Codified as Ship
34'.c lesson #2.

## What Ship 35 does — code diff

### File: `rag/intake/extractor.py`

**Current (approximate)**:
```python
# Lines ~271-311 in extract()
fp_findings, fp_covered = _extract_via_fingerprints(doc, fp_leaf_pool)

if _critic_flag not in ("0", ...):
    llm_findings = _run_critic_verifier_pass(doc, scoped, fp_findings, fp_covered)
elif doc.extraction_path == ExtractionPath.FULL_DOCUMENT:
    llm_findings = _extract_full(...)
else:
    llm_findings = _extract_sections(...)

findings = fp_findings + llm_findings
```

**Post-cutover**:
```python
# Ship 35 — full replacement when consensus flag is ON
_consensus_flag = os.getenv("USE_CONSENSUS_EXTRACTION", "0").lower()
if _consensus_flag not in ("0", "false", "no", "off"):
    findings = _extract_via_consensus(doc, fp_leaf_pool)
else:
    # Existing path — unchanged for default-OFF safety
    fp_findings, fp_covered = _extract_via_fingerprints(doc, fp_leaf_pool)
    if _critic_flag not in ("0", ...):
        llm_findings = _run_critic_verifier_pass(doc, scoped, fp_findings, fp_covered)
    elif doc.extraction_path == ExtractionPath.FULL_DOCUMENT:
        llm_findings = _extract_full(...)
    else:
        llm_findings = _extract_sections(...)
    findings = fp_findings + llm_findings
```

### New `_extract_via_consensus(doc, scoped_leaf_ids)`

- Instantiate `ExtractionConsensusConfig` with `llm_arbiter_enabled=True`
  (Ship 33'.c ships arbiter as the discrimination layer)
- Call `run_extraction_consensus(doc, scoped_leaf_ids, cfg)`
- Materialize each accepted `CandidateVerdict` as a
  `DocumentFinding` (fields: control_ref, standard_id,
  checklist_item_id, evidence_text, confidence,
  inference_source, extraction_path)
- Log via `log_consensus_result(pg_conn, tenant_id, upload_id,
  result)`  — silent-fail
- Return list of DocumentFindings

### File: `rag/intake/consensus_extraction/aggregator.py`

Add no-excerpt-auto-drop invariant:

```python
# Post-verdict pass — drop candidates with no evidence text
# regardless of aggregator score. Ship 34'.c finding: 85% of
# arbiter zone was single-signal scope-vote candidates with
# no fingerprint match. LLM correctly rejected all; save the
# roundtrip cost by dropping deterministically.
if not v.fingerprint_excerpt and v.verdict != "drop":
    v.verdict = "drop"
    n_drop += 1
    if verdict == "accept": n_accept -= 1
    elif verdict == "arbiter": n_arbiter -= 1
```

Applied inside the verdict-classification loop. Fail-safe:
if a candidate somehow accepts without an excerpt (shouldn't
happen — fingerprint is the only signal that produces
excerpts), it drops to prevent evidence-less findings from
being written.

### File: `rag/intake/doc_pipeline.py`

- Pass `pg_conn` + `tenant_id` + `upload_id` through to
  `_extract_via_consensus` so log_consensus_result can persist

## Rollback plan

**Immediate rollback**: unset `USE_CONSENSUS_EXTRACTION` (or set
to 0) + restart API. Reverts to existing behavior in seconds.
No database migration or code revert required.

**Data-side impact**: findings written under
`USE_CONSENSUS_EXTRACTION=1` have `inference_source='consensus'`
(new value — needs to be added to any CHECK constraint
allowing it). If a tenant hits issues, findings from the
consensus path can be filtered / soft-deleted per Ship 30's
demo_tenant_cleanup pattern.

**Full arc revert**: `git revert` the Ship 35'.b commit;
consensus code stays but the wiring is removed.

## Retirement roadmap

Ship 35 does NOT retire `_extract_via_fingerprints` /
`_run_critic_verifier_pass` / the concat. They stay operational
for the default-OFF path. Retirement happens in a follow-on arc
after:
- N weeks (probably 4-6) of `USE_CONSENSUS_EXTRACTION=1` running
  on the demo tenant without issues
- Optional: extending consensus to cover LLM discovery pass
  (adds a signal that mimics its behavior — e.g., a signal
  that queries the LLM for candidates on leaves the other
  signals didn't cover)
- Verification via re-measurement that recall didn't materially
  drop on a broader corpus

Until then, both paths remain in the codebase.

## Non-goals

- **Extending consensus to cover LLM discovery pass** — that's
  a bigger arc; Ship 35 accepts the recall trade-off as-is.
- **Threshold retuning from production data** — deferred to Ship
  36+ once `intake_consensus_log` has real data.
- **Per-tenant config for the flag** — env-wide default OFF is
  fine for now; per-tenant scoping is a follow-on if needed.
- **Chat consensus changes** — untouched.
- **inference_source CHECK constraint update** — will add
  'consensus' to the allowlist in 35'.b via schema_v90 if
  needed (may not be needed if the column is unconstrained).

## Sub-arc plan

| Sub-arc | Focus | Outcome |
|---|---|---|
| **35'.a** (this) | Design memo | Cutover shape + flag + invariant + rollback locked |
| 35'.b | Implement + smoke-test | Consensus reachable via `USE_CONSENSUS_EXTRACTION=1`; smoke on 1 doc |
| 35'.c | Eval (flag=OFF baseline) + retro | Baseline holds; arc closed |

## Related

- [[ship-33-prime-arc-retrospective-2026-07-25]] — the consensus
  arc this cuts over
- [[ship-34-prime-arc-retrospective-2026-07-25]] — the
  validation arc that unblocked this cutover
- [[ship-32-prime-arc-retrospective-2026-07-25]] — the
  measurement arc that surfaced the multi-attribution problem
  consensus addresses
- `rag/intake/consensus_extraction/` — the module this arc wires
  into the runtime path
