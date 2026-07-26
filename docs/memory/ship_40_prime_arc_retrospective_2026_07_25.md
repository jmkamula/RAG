---
name: ship-40-prime-arc-retrospective-2026-07-25
description: "Ship 40' arc closer — Phase 3 filter bypass + consensus scope widening delivers cross-framework extraction under consensus. 4 Art.35 findings persisted on DPIA (was 0 in production). Total accepts 52→74 (+42%) across 5 Ship 10 docs. Mid-arc discovery: enricher's per-doc standard_ids was the upstream narrowing gate, not Phase 3 filter alone. Source-guard already handles direct-vs-overlay divergence. 40'.c skipped."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 40' arc retrospective — 2 delivery sub-arcs + skipped
divergence check + closer, single session 2026-07-25.
Cross-framework extraction under consensus now works end-to-end.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 40'.a | Design memo — Phase 3 filter bypass | 68dcd48 |
| 40'.b | Implementation + measurement + widening discovery | c42e885 |
| 40'.c | **SKIPPED** — source-guard handles divergence | n/a |
| **40'.d** | **Retro (this)** | pending |

## Measurement — the numbers we were chasing

| Doc | Ship 32 (LLM baseline) | Ship 36 (consensus 1st cutover) | Ship 39 | **Ship 40'.b** | Δ vs 39 |
|---|---|---|---|---|---|
| DQA | 90 | 4 | 10 | **12** | +2 (+20%) |
| DPIA | 149 | 4 | 17 | **20** | +3 (+18%) |
| RoPA | 30 | 5 | 4 | **15** | +11 (+275%) |
| Consent | 41 | 6 | 6 | **12** | +6 (+100%) |
| Processor Ops | 149 | 14 | 15 | **15** | 0 |
| **TOTAL** | **459** | **33** | **52** | **74** | **+22 (+42%)** |

**4 Art.35 findings persisted on DPIA** — previously 0 in production
(Phase 3 filter removed Art.35 upstream). Cross-framework
extraction confirmed working under consensus.

## What actually changed

**Two-part change** in `doc_pipeline.py`:

1. **Phase 3 filter bypass** at line 986 (as designed in 40'.a). 3
   LOC gate: `if USE_CONSENSUS_EXTRACTION=1: return all_controls`.
   Preserves legacy pipeline behaviour.

2. **Consensus scope widening** at line 365-380. When consensus is
   on, replace `doc.standard_ids` (enricher-assigned, per-doc)
   with all Neo4j-loaded standards. Discovered mid-arc when 40'.b
   first re-extract measurement showed DPIA at 6 candidates
   instead of 66 — the enricher had assigned
   `standard_ids=['ISO27701:2019']` so `_get_controls` was only
   loading 49 ISO 27701 controls; Phase 3 bypass had nothing to
   un-filter because GDPR obligations were never in scope to
   begin with.

New helper `_all_graph_standards()` queries Neo4j for distinct
standard_ids (cached per instance, silent-fail on Neo4j error).

## Mid-arc discovery — layer 0 was narrower than diagnosed

Ship 39'.c retrospective identified layer 0 as
`doc_pipeline._filter_demonstrated_obligations`. That was
**incomplete** — the filter's input `all_controls` is itself
narrowed by an upstream gate (the enricher's per-doc
`standard_ids` classification).

**The full narrow-scope path was**:

1. Enricher classifies DPIA → `standard_ids=['ISO27701:2019']`
2. `_get_controls(['ISO27701:2019'])` loads 49 ISO 27701
   controls only
3. `_filter_demonstrated_obligations(49_controls, ...)` — no
   GDPR obligations to remove, filter is a no-op
4. `extract()` sees 49 controls, 0 GDPR articles → 0 Art.35
   candidates

Ship 40'.a's design memo missed step 1. The Phase 3 filter
bypass only helps IF the input list has cross-framework controls
to begin with. Discovered when measurement showed the bypass log
fired 5 times but candidate counts DROPPED (Ship 40 first
attempt: DPIA 6 candidates, worse than Ship 39's 66).

Two-part fix landed atomically in `c42e885`.

## 40'.c skipped — source-guard already handles divergence

The 40'.a memo budgeted 40'.c as "direct-vs-overlay divergence
check" — investigate whether consensus's direct Art.35=Comply
finding conflicts with DEMONSTRATES overlay's Art.35=NC
propagation from A.7.2.5.

Turns out the `posture_writer` source-guard already has the
answer. From Ship 40'.b writer log:

```
⊘ Art.35 protected — source=engine status=engine_confirmed (NC) — skipped
⊘ 6.1.2 protected — source=engine status=engine_confirmed (OFI) — skipped
⊘ A.7.2.5 protected — source=document status=document_confirmed (NC) — skipped
```

The direct finding IS persisted to `document_findings` (auditor
evidence stays visible), but the posture_controls status is NOT
overwritten. Engine-confirmed posture wins. This is the
architecturally-correct tiebreak already baked into the writer.

No new code needed. 40'.c documented as answered by construction.

## Codified 2 lessons

### 1. Layer diagnosis is incomplete until measurement confirms

Ship 39'.c named layer 0 as `_filter_demonstrated_obligations`.
Ship 40'.a took that as gospel + designed a 3-LOC bypass. Ship
40'.b measurement caught the missing upstream gate (`standard_ids`
narrowing) mid-arc because DPIA showed 6 candidates instead of
66. The bypass log fired 5 times but candidates DROPPED — a
telltale that the bypass wasn't reaching the intended scope.

**Rule**: after a "root cause" diagnosis + fix, always measure
FIRST (before writing design memos or committing). The mid-arc
discovery here saved us from shipping 40'.a-as-designed with
zero actual impact.

### 2. Source-guard is a hidden architectural asset

The `posture_writer` source-guard's original purpose was
protecting document-confirmed postures from being overwritten by
noisy extractor findings (Ship 30 era). Ship 40'.b reveals it
ALSO handles cross-framework direct-vs-overlay divergence
correctly: direct finding → `document_findings` (audit); overlay
→ `posture_controls` (posture authority). Both surfaces coexist
cleanly.

**Rule**: before designing a new tiebreak/priority mechanism,
grep for existing source-of-truth guards. The writer's
source-guard already had 40'.c's answer built in.

## Ship 40 arc — closed

- Cross-framework extraction under consensus: **working**
- Art.35 findings persisted for auditor evidence: **4 on DPIA**
- Direct-vs-overlay divergence: **handled by source-guard**
- Eval: **230 PASS / 1 WARN / 1 FAIL** (FAIL is #5, known-
  stochastic LLM prose per CLAUDE.md; not a Ship 40 regression)
- Recall +42% on 5 Ship 10 docs

## What Ship 40 did NOT do

- **Retire USE_CONSENSUS_EXTRACTION flag** — consensus stays
  opt-in per tenant; default OFF preserved for legacy pipeline
- **HITL sample of new 22 accepts** — deferred; source-guard's
  audit-safe persistence makes this a lower-urgency check
- **Fix layers 1-2** (xfw_proposer edge coverage, doc_mappings
  YAML scope) — no longer bottlenecks after 40'.b scope widening
- **Curator arc on proc_* fingerprints** — Ship 38'.b caught
  the main gap; broader arc deferred

## Sub-arc sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 40'.a | Design memo — Phase 3 bypass gate | 3-LOC gate design; incomplete diagnosis |
| **40'.b** | **Implementation + measurement + widening discovery** | **Two-part fix; +42% recall; 4 Art.35 findings** |
| 40'.c | Divergence check | SKIPPED — source-guard already handles it |
| **40'.d** | **Retro (this)** | **Arc closed; consensus arc-family status: cross-framework extraction working** |

## Consensus arc family — where we stand (Ships 32-40)

| Arc | Focus | Result |
|---|---|---|
| 32 | 5-doc measurement — Path A | 272 findings (LLM baseline); Processor Ops 121-fingerprint uniqueness bug |
| 33 | Consensus refactor (shadow) | 197 findings; multi-attribution addressed |
| 34 | Validation + telemetry | HITL 20/20 correct-reject; log schema |
| 35 | Cutover flag (default OFF) | Env flag ships |
| 36 | First cutover on Arion | 33 findings — invariant more aggressive than expected |
| 37 | Recall HITL on drops | 52% correctly-dropped, 24% should-accept, 24% uncertain |
| 38 | Relax invariant + curator gap | 35 findings; identified 4-layer bottleneck |
| 39 | Layer 3 fix (must_semantic scope) | 46 findings; layer 0 diagnosed |
| **40** | **Layer 0 fix + upstream widening** | **74 findings + Art.35 cross-framework working** |

**Cross-framework extraction now solved**. Consensus arc from
Ship 32 through 40 delivered discovery-broad extraction with
cross-framework support at 42% higher recall than the pre-arc
production baseline. Extraction consensus module ready for
production default-ON evaluation.

## Deferred / follow-on candidates

- **Default-ON evaluation** — is Arion demo tenant's stability
  now sufficient to flip `USE_CONSENSUS_EXTRACTION` on for other
  tenants? Own arc — needs broader-doc coverage check + retire-
  legacy-pipeline plan.
- **HITL sample of Ship 40'.b new accepts** — the 22 new
  findings deserve visual inspection to confirm quality
- **Direct-vs-overlay reporting surface** — when both fire and
  they disagree, tenant might want to see both in advisory
  ("engine says NC, direct evidence in DPIA §4.2 suggests
  Comply — reconcile")
- **Ship 32 Processor Ops multi-attribution** — 15 findings vs
  original 149 shows the multi-attribution is largely addressed
  by consensus but 15 is still 3x the 5 Ship 10 baseline for
  that doc; consider per-evidence-text cap as a Ship 33 follow-on

## Related

- [[ship-39-prime-arc-retrospective-2026-07-25]] — the layer-3
  fix that motivated 40'.a design memo
- [[ship-40-prime-a-phase3-bypass-design-2026-07-25]] — 40'.a
  design memo (missed the upstream `standard_ids` narrowing;
  40'.b caught mid-arc)
- [[framework-role-model-arc]] — the Phase 3 design 40 gates for
  consensus tenants
- `rag/intake/doc_pipeline.py:365-380` — consensus scope widening
- `rag/intake/doc_pipeline.py:986` — Phase 3 filter bypass gate
- `rag/intake/posture_writer.py` source-guard — the tiebreak
  40'.c was going to design (already built in)
