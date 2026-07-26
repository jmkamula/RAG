---
name: ship-45-prime-a-retrieve-decomposition-design-2026-07-26
description: "Ship 45'.a design memo — decompose the retrieve node's 11.7s (79% of chat latency) into sub-spans. Resolver.resolve() outer + per-handler span + vector_search + graph_expand + doc_context_enrich + incident_obligations. Hypothesis: graph_expand dominates because it walks Neo4j + fetches Chroma content for each expanded node. Ship 45'.b instruments; Ship 45'.c fixes if a specific hotspot surfaces."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 45'.a — decompose the retrieve node.

## Motivation

Ship 44'.d surfaced that `retrieve` = 11.7s of 14.8s chat latency
(79%). But retrieve is a single LangGraph node from OTel's
perspective — the auto-instrumentation from OpenInference/LangChain
sees it as one opaque span.

Inside retrieve is `Resolver.resolve()` which dispatches to
handlers, each of which calls:
- `retriever.search()` — Chroma vector query
- `expander.expand()` — Neo4j graph walk + Chroma content fetch
- `_enrich_doc_contexts()` — Postgres posture overlay
- Handler-specific Postgres queries

Plus arion_graph.retrieve calls (outside Resolver):
- `expander.get_incident_obligations()` — Postgres + Neo4j
- Various short-circuit checks

Trace metrics (neo4j_ms, vector_ms, postgres_ms) already exist in
ResolverTrace but aren't OTel spans. Decomposing to real spans
makes the Jaeger waterfall show where the 11.7s goes.

## Hypothesis before instrumenting

Given the code shape, my expected top 3:

1. **`expander.expand()`** — biggest single call. Walks Neo4j
   (SATISFIED_BY, MUST_CONTAIN, DEMONSTRATES, cross-framework
   IMPLEMENTS/SUPPORTS) + fetches Chroma content for each
   expanded node ID. Multiple round-trips.
2. **`retriever.search()`** — Chroma vector query with
   OpenAI embedding call for the query. Single round-trip
   but includes external OpenAI API.
3. **Neo4j incident obligations** — separate expander call.

I don't expect Postgres to dominate (per Ship 44'.d's DB spans
which showed most SELECT/UPDATE at <5ms each).

If the numbers confirm this hypothesis, Ship 45'.c could:
- Cache Neo4j graph expansion results per (query, standards)
  tuple within a session
- Or parallelize vector_search + posture prep since they don't
  depend on each other

## Spans to add

**In `rag/resolver.py`**:

- `arion.resolver.resolve` — outer wrapper. Attributes: taxonomy
  type_id, handler_name, strategy, tenant_id
- `arion.resolver.handler.<type_id>` — one span per handler call
- `arion.resolver.vector_search` — Chroma call inside
  `_retrieve_and_expand`. Attributes: n_results, top_score,
  standards
- `arion.resolver.graph_expand` — expander call inside
  `_retrieve_and_expand` or `_expand`. Attributes: n_input_ids,
  n_output_nodes
- `arion.resolver.enrich_doc_contexts` — `_enrich_doc_contexts`
  call. Attributes: n_doc_contexts, n_enriched

**In `rag/graph_expander.py`**:

- `arion.graph_expander.expand` — outer expand() with attributes:
  n_input_ids, budget, expander_online, path (graph vs
  vector-only)
- `arion.graph_expander._graph_expand` — inner Neo4j+Chroma
  path. Attributes: cited, parents, children, xfw counts, doc_contexts
- `arion.graph_expander.get_incident_obligations` — separate call.

**In `rag/arion_graph.py`**:

- `arion.retrieve.dispatch` — the whole retrieve function.
  Attributes: query_length, intent_type, standards
- (individual short-circuit paths can be sub-spans if they end
  up mattering)

## Content privacy

None of these spans need to capture content. All attributes are
counts / IDs / paths. `capture_content()` gate not needed here
— consensus signals and LLM calls are where content flows.

## Sub-arc plan

**Ship 45'.b**:
1. Add spans per the list above (~40 LOC across 3 files)
2. Restart API + fire chat requests
3. Capture the Jaeger trace waterfall for retrieve
4. Identify hotspot

**Ship 45'.c**:
- If hotspot is in `expander.expand()` — decompose further into
  cypher-query granularity spans + investigate cache opportunities
- If hotspot is in `retriever.search()` — investigate embedding
  cache or query batching
- If hotspot is spread — document that retrieve is genuinely
  N-round-trip-bound and needs parallelization not caching

## What Ship 45 does NOT do

- **Cross-node parallelization of retrieve** — would need
  LangGraph node splitting. Larger refactor if evidence supports.
- **Caching layer** — depends on what hotspot analysis reveals.
- **Chroma index optimization** — separate concern.
- **Retrieve node retrofit** — this arc is measurement + targeted
  fix, not restructure.

## Ship 46 preview (deferred)

If Ship 45 reveals that retrieve is fundamentally N-round-trip
bound, Ship 46 could parallelize with asyncio.gather() or a
tighter data-locality pattern (co-locate all Neo4j calls into
one Cypher, one Chroma call, etc.).

## Related

- [[ship-44-prime-arc-retrospective-2026-07-26]] — the arc that
  surfaced the 11.7s retrieve latency
- `rag/resolver.py::Resolver.resolve` — outer instrumentation point
- `rag/graph_expander.py::GraphExpander.expand` — the hypothesized
  hot function
- `rag/arion_graph.py:2127` — the retrieve LangGraph node
