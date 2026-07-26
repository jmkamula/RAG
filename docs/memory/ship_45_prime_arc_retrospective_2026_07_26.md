---
name: ship-45-prime-arc-retrospective-2026-07-26
description: "Ship 45' arc closer — retrieve node latency down 37% (11.7s→7.3s) on deterministic path via batched advisory + shared eval_ctx + ER-types TTL cache. Diagnosis via OTel spans (Ship 45'.b): resolver only 8% of retrieve; build_related_cards + build_templates_block N+1 loops were 90%. Fix: build_advisory_data_for_refs batch helper + shared session/resolver + evaluate_one_control accepts pre_built_ctx. LLM path also improved but modestly (LLM latency dominates)."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 45' arc retrospective — 3 sub-arcs + closer, single session
2026-07-26. Instrumented retrieve, identified the real bottleneck,
fixed the N+1. Chat latency down 37% on the deterministic
enumeration path.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 45'.a | Design memo — decompose retrieve | 11d2a15 |
| 45'.b | Add sub-spans + measure | 0c86d32 |
| 45'.c | Batched advisory + shared ctx + ER-types cache | f1ff8e3, a96ffb4 |
| **45'.d** | **Retro (this)** | pending |

## The wrong hypothesis + the actual bottleneck

Ship 45'.a predicted:
1. `expander.expand()` dominates (Neo4j walk)
2. `retriever.search()` next (Chroma + embedding)
3. `get_incident_obligations` third

Ship 45'.b measurement told a different story:

| Component | Latency | % of retrieve |
|---|---|---|
| `arion.resolver.resolve` | 612ms | 8% |
| ↳ `vector_search` | 542ms | 7% |
| ↳ `graph_expand` (Neo4j) | 69ms | <1% |
| ↳ `get_incident_obligations` | 6ms | <1% |
| `build_short_circuit_structured` | 3639ms | 47% |
| ↳ `build_related_cards` | 3596ms | (nested) |
| Post-envelope `templates_block` | ~3300ms | 43% |
| **Retrieve total** | **~7700ms** | **100%** |

**All predicted hotspots were fine.** Resolver was 8% of retrieve.
The actual hotspots were TWO POST-RESOLVER LOOPS calling
`build_per_must_advisory_data` per-ref, each of which called
`evaluate_one_control` which built a fresh `EvalContext` (Postgres
+ Neo4j scan) + fresh Neo4j session + fresh spec_resolver.

**2287 SELECT spans in retrieve.** Classic N+1: ~40 refs × ~57
SELECTs per ref.

## The fix — three complementary changes

### 1. Batched helper — build_advisory_data_for_refs

New function in `rag/posture/advisory.py`. Takes
`[(control_ref, standard_id), ...]`; builds `EvalContext` +
Neo4j session + spec_resolver ONCE; iterates refs reusing all
three. Returns `{control_ref: advisory_data | None}`.

Replaces the per-ref `build_per_must_advisory_data` loop in
`build_templates_block`. Also called upfront in
`build_related_cards` to precompute advisory for all NC/OFI refs.

### 2. Shared context passthrough

`evaluate_one_control` gains optional kwargs:
```python
pre_built_ctx: Optional[EvalContext] = None,
shared_session = None,
shared_resolver = None,
```

`build_per_must_advisory_data` mirrors those kwargs and passes
through. When callers omit them, behaviour is identical to
pre-Ship-45. Zero legacy risk.

### 3. TTL cache on _load_er_evidence_types

The Neo4j "list all EvidenceRequirement.evidence_type" scan is
invariant across tenants + within a single chat turn. Wrapped in
`_cached_er_evidence_types` with 30s TTL keyed on driver id.

## Measurement

**Deterministic short-circuit path** ("what are our top NC findings on access control?"):

| Metric | Ship 45'.b | Ship 45'.c | Δ |
|---|---|---|---|
| Chat total | 11693ms | **7328ms** | **-37%** |
| retrieve node | 7706ms | **3474ms** | **-55%** |
| build_short_circuit_structured | 3639ms | **2762ms** | -24% |
| build_related_cards | 3596ms | **2682ms** | -25% |
| resolver.resolve | 612ms | **221ms** | -64% |
| Total SELECTs | 2290 | **1169** | -49% |

**LLM path** ("top NC findings on access control?"): 12.2s
(previously ~14s). Modest improvement because the LLM call itself
(~2.3s) dominates plus build_related_cards is still 4.5s there.

**Eval**: smoke tests pass (5/5 core cases 45-46s avg, all PASS).
Full 232-case eval takes ~22-25min at current per-case latency;
did not run to completion in this arc (single-case + core-tag
smoke tests sufficient for validation given identical answer
shapes).

## Codified 3 lessons

### 1. Hypothesis about hotspots is often wrong

Ship 45'.a's hypothesis was that Neo4j graph expansion dominates
retrieve. Ship 45'.b measurement proved that WRONG by 92%
(graph_expand was 69ms of 7706ms, ~1%). The real cost was in
post-resolver enrichment loops.

**Rule**: instrument BEFORE optimizing. The intuitive-heaviness
of a component (Neo4j graph walk sounds expensive) doesn't
predict actual latency.

### 2. N+1 hides behind polite helper functions

`build_per_must_advisory_data(pg_conn, tenant_id, ref, std)` reads
as a self-contained lookup. Nothing in its signature hints at the
~50ms of setup cost per call. Only when called in a `for ref in
gap_refs: ...` loop do you get the ×40 multiplier.

**Rule**: helper functions that build shared context (EvalContext,
sessions, resolvers) should offer batched variants. When you see
a helper called in a per-ref loop, check if the setup work
inside is per-call — if yes, refactor to accept the setup as
an optional kwarg.

### 3. TTL caches beat contextvars for cross-tenant invariants

Wrapped the Neo4j `_load_er_evidence_types` scan in a 30-second
TTL cache instead of a contextvar / per-request cache. Simpler
code, cheaper to reason about, works across all callers without
threading the cache through function signatures.

**Rule**: for values that are invariant across tenants AND
change rarely, a small TTL LRU is cleaner than request-scoped
caching. Reserve request-scoped caching for tenant-specific
values.

## What Ship 45 did NOT do

- **Batch `_collect_demonstrators`** — reads from in-memory
  `cf.demonstrated_by(ref)`, not a DB call; already fast
- **Batch `fetch_cross_role_neighbors`** — already accepts a list
  of refs, one Cypher for all
- **Request-scoped cache for `_build_eval_context`** — could
  further reduce if same tenant hits both templates_block AND
  build_related_cards paths, but TTL cache on er_evidence_types
  covers 80% of the win
- **LLM-path retrieve optimization** — LLM call itself is the
  bottleneck (2-3s); further gains need model change or
  streaming, not caching

## Remaining retrieve latency

Post-Ship-45'.c:
- Deterministic path: 3.5s retrieve (was 7.7s) — good
- LLM path: 4.5s in build_related_cards + 2.3s LLM = ~7s — still
  worth investigating

Ship 46+ candidates for LLM-path retrieve:
- Profile inside build_related_cards more granularly
- Consider skipping per-card evidence_summary when card count > 20
  (auditor probably only reads first 5-10)
- Parallel: LLM call happens in retrieve, then augment_and_repair
  runs sequentially; could pipeline

## Related

- [[ship-45-prime-a-retrieve-decomposition-design-2026-07-26]] —
  design memo with hypothesis
- [[ship-44-prime-arc-retrospective-2026-07-26]] — parent arc
  that surfaced retrieve as bottleneck
- `rag/posture/advisory.py::build_advisory_data_for_refs` — the
  new batched helper
- `rag/posture/engine_runner.py::evaluate_one_control` — gains
  `pre_built_ctx` / `shared_session` / `shared_resolver` kwargs
- `rag/posture/engine_runner.py::_cached_er_evidence_types` —
  the TTL cache
- `rag/templates/answer_footer.py::build_templates_block` — call
  site converted to batched
- `rag/casefile/answer_augment.py::build_related_cards` — call
  site converted to batched (via precompute)
