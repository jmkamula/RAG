---
name: ship-40-prime-a-phase3-bypass-design-2026-07-25
description: "Ship 40'.a design memo — conditional bypass of doc_pipeline._filter_demonstrated_obligations when USE_CONSENSUS_EXTRACTION=1. Single call site at doc_pipeline.py:976; 3-4 LOC. Consensus's fingerprint+aggregator discipline replaces Phase 3's LLM-duplication guard. Ship 40'.b re-measures; Ship 40'.c handles direct-vs-overlay divergence."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 40'.a — design memo for Phase 3 filter bypass under consensus
extraction.

## Motivation

Ship 39'.b direct-extract test proved consensus can produce 10
Art.35 findings on DPIA when Phase 3 filter doesn't remove Art.35
upstream. Production API path shows 0 Art.35 (filter removes it).
The 78% recall loss for cross-framework GDPR on DPIA / DQA / RoPA
traces to layer 0 (`_filter_demonstrated_obligations`), not any
consensus signal weight.

Product direction (2026-07-25 session): consensus tenants get
direct auditor-facing cross-framework evidence. Overlay stays as
belt-and-suspenders backstop for demonstrated obligations when
consensus's direct finding is absent (e.g. weaker doc, low
score).

## Callchain audit — single gate site

Grep confirms `_filter_demonstrated_obligations` is called from
exactly one place:

- `doc_pipeline.py:976` — inside `_get_controls(standard_ids)`

And `_get_controls` itself is called from exactly one place:

- `doc_pipeline.py:367` — inside `run(file_path, tenant_id)`

No other filter site touches `all_controls` between Neo4j load and
`extract()`. Gate at line 976 is sufficient.

## The change

**`doc_pipeline.py:976`** — replace the unconditional filter call
with a consensus-aware gate:

```python
# Ship 40'.a — bypass Phase 3 obligation filter under consensus.
# Rationale: Phase 3 was designed against LLM discovery pass
# duplication; consensus (fingerprint excerpt requirement +
# 8-signal aggregator + LLM arbiter bounded) has its own
# discipline. Direct cross-framework findings are then an
# auditor-facing feature, not a duplication bug. The DEMONSTRATES
# overlay in posture_loader remains as belt-and-suspenders for
# obligations that consensus doesn't surface directly.
if os.getenv("USE_CONSENSUS_EXTRACTION") == "1":
    logger.info(
        f"Phase 3 filter BYPASSED under consensus "
        f"({len(all_controls)} controls remain in scope)"
    )
    return all_controls

filtered = self._filter_demonstrated_obligations(all_controls, standard_ids)
```

3 LOC of gate, no other code changes. `_filter_demonstrated_obligations`
stays intact for legacy pipeline callers (any tenant with
`USE_CONSENSUS_EXTRACTION` unset or 0).

## Why the gate is architecturally safe

Phase 3's rationale (from the code comment):

> letting the LLM also extract them directly reintroduces the
> pre-Phase 3 multi-framework guessing bias

This is a discipline claim against the OLD LLM discovery pipeline.
Under consensus:

1. **Fingerprint excerpt requirement** (Ship 35'.b no-excerpt-auto-drop
   invariant) — an Art.35 candidate can't accept without a
   deterministic fingerprint match in the doc. LLM cannot invent.
2. **8-signal aggregator** — score threshold (accept ≥ 0.75) requires
   ≥2 corroborating signals, not just single-signal semantic drift.
3. **Semantic fit gate** — post-fingerprint cosine gate drops
   candidates where doc excerpt drifts semantically from the MUST
   text.
4. **LLM arbiter** (borderline zone only) — cannot invent, cannot
   accept, can only downgrade `arbiter` → `drop`.

The Ship 34'.c HITL sample (20 of 20 rejects correctly rejected)
validated these gates. "Multi-framework guessing bias" is not the
consensus failure mode; consensus's failure mode is under-recall
(Ship 36-39 arc), not over-attribution.

## Direct-vs-overlay coexistence

Both surfaces will produce Art.35 posture for demonstrated
obligations:

- **Direct**: consensus writes an Art.35 document_finding →
  posture writer marks Art.35 status
- **Overlay**: `posture_loader._apply_demonstrates_overlay`
  propagates A.7.2.5's posture to Art.35 at posture-load time

Behavior in the common case (both agree, e.g. both Comply):
tenant sees Art.35 posture with an evidence link to the DPIA doc.
Overlay is silent when direct finding exists (no propagation
conflict; existing posture stands).

Behavior in the conflict case: direct finding says Art.35=Comply
(evidence in DPIA), overlay would say Art.35=NC (A.7.2.5 is NC
because Arion also has weak evidence for A.7.2.5's OTHER MUSTs).
Ship 40'.c investigates the tiebreaker: prefer direct
(auditor-facing evidence wins) OR prefer overlay (whole-control
posture is more conservative) OR surface both.

Ship 40'.b measurement will show how often conflict actually
happens. If rare (< 5% of demonstrated obligations), the tiebreak
question becomes low-stakes.

## Expected measurement impact (Ship 40'.b hypothesis)

Ship 39 direct-extract test gave us the ceiling for consensus
under widened scope. Ship 40'.b should approach it:

| Doc | Ship 39 (production) | Direct-test (39'.b) | Ship 40'.b target |
|---|---|---|---|
| DQA | 10 | ? | 10+ |
| DPIA | 11 | 17 (incl. 10 Art.35) | ~15-20 |
| RoPA | 4 | ? | 4-8 (Art.30 already unfiltered) |
| Consent | 6 | ? | 6-10 (Art.7 already unfiltered) |
| Processor Ops | 15 | ? | 15-25 |
| **TOTAL** | **46** | **? (single-doc measured)** | **~55-80** |

Ship 39 direct-extract was measured for DPIA only. Ship 40'.b
should run direct-extract on all 5 docs first to establish the
consensus ceiling, then run production API to confirm 40'.a bypass
hits it.

## Ship 40'.b implementation plan

1. Edit `doc_pipeline.py:976` with the gate (above)
2. Run direct-extract on all 5 Ship 10 baseline docs to establish
   ceiling
3. Restart API, re-extract via production API path, count accepts
4. Diff Ship 39 vs Ship 40 per-doc accept counts
5. Diff consensus-direct-finding refs vs overlay-propagated refs
   (feeds Ship 40'.c)

## Ship 40'.c preview

Direct-vs-overlay divergence check. Not a code change unless
measurement shows conflict:

- Query: for each Arion tenant, list controls where (a) direct
  finding exists AND (b) overlay would propagate a different
  status
- If N < 5% of demonstrated obligations: document as "known
  edge case, direct wins by construction" and close
- If N ≥ 5%: tiebreak rule needs explicit design (surface both
  in advisory, or prefer direct with overlay as annotation)

## Ship 40'.d retro

Standard arc closer. Roll up:
- Bypass shipped, measurement impact confirmed
- Divergence rate measured
- Layers 1-2 (xfw edge coverage, doc_mappings scope) status
- Consensus arc status (32-40) — is it converged enough to
  default-ON, or still opt-in?

## What Ship 40 does NOT do

- **Retire Phase 3 filter** — legacy pipeline still uses it;
  filter stays intact
- **Change consensus signal weights** — pure scope change
- **Fix layers 1-2** — deferred; Ship 40'.b measurement will
  show whether they're bottlenecks under widened scope
- **Change DEMONSTRATES overlay** — coexistence, not replacement

## Related

- [[ship-39-prime-arc-retrospective-2026-07-25]] — the layer-0
  diagnosis that motivates 40'.a
- [[framework-role-model-arc]] — the Phase 3 design 40'.a
  conditionally bypasses
- `rag/intake/doc_pipeline.py:976` — the gate site
- `rag/posture_loader.py::_apply_demonstrates_overlay` — the
  overlay that coexists with direct findings
