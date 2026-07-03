---
name: must-embedding-index-2026-06-26
description: "RETIRED 2026-07-03. SHIPPED 2026-06-26 (3b75461) as foundation for semantic-search extraction to replace the single-shot LLM path. Prototype (scripts/prototype_semantic_extract.py) validated the approach but the expected extraction improvement didn't materialise — the extractor stayed on the pattern-based path (doc_mappings + workbook_mappings + must_fingerprints). Collection sat unconsumed in production. RETIRED to avoid future confusion: musts_arioncomply Chroma collection deleted, scripts/build_must_index.py + scripts/prototype_semantic_extract.py removed. Framework-scoped collections (iso27001_2022 / gdpr_2016_679 / arioncombly_all) — the ones used by chat retrieval via vector/retriever.py — are unaffected and remain live. Historical detail preserved below."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## RETIRED 2026-07-03 — why

The foundation shipped but the follow-on semantic-search extraction
never became live. Prototype in `scripts/prototype_semantic_extract.py`
was exercised on a handful of docs but the pattern-based path
(catalog + doc_mappings + workbook_mappings + must_fingerprints)
kept outperforming per-doc-per-MUST embedding recall, and the
extractor remained on the pattern path. Collection sat unconsumed
in production for a week.

Retirement 2026-07-03 was triggered by the ISO 27701 arc raising
"what about MUST embeddings for the new framework?" — clarifying
that this collection was never live prevented an unnecessary
extension into the retired path. Cleanup:

  - Chroma collection `musts_arioncomply` deleted (4133 items)
  - `scripts/build_must_index.py` removed
  - `scripts/prototype_semantic_extract.py` removed
  - CLAUDE.md Key Files entry removed

Historical detail from the shipping memo preserved below for
archaeology.

## What shipped

A standalone build script (`scripts/build_must_index.py`) that walks
`enrichment/documents/document_requirements.py` and upserts every
ChecklistItem into a new ChromaDB collection `musts_arioncomply`.

- **4133 vectors** (3270 MUSTs + 863 SHOULDs across ISO 27001 + GDPR)
- **Embedding model**: `text-embedding-3-small` (matches existing
  leaf collections; the two vector spaces are now compatible for
  future hybrid retrieval)
- **~42s to build**, ~$0.05 in OpenAI embedding API cost
- **Idempotent** — re-running upserts by `must_id`. Rerun on curation
  refresh.

## Vector document composition

Five layers, ordered most-to-least semantically central:

1. Header: `{standard_id} {control_ref} :: {must_id}`
2. Leaf identity: `Leaf: {title} (evidence_type={...})`
3. **Leaf description** — practitioner-language context (Tier-1
   enrichment lives here; carries curation-paraphrased 27002-flavor
   without shipping ISO 27002 verbatim — copyright-safe)
4. The MUST text itself (primary signal)
5. Rationale citation (e.g. `27002:5.18 — provisioning`)

Metadata stored (filterable in Chroma queries):
`must_id, leaf_id, control_ref, standard_id, evidence_type,
category (must/should), gdpr_aligned, trigger_type, leaf_title`.

## Why ChromaDB and not pgvector

ChromaDB was already in the stack (used by chat retrieval). Same
PersistentClient, same `/data/arioncomply/chroma_db` directory, same
embedding function (`OpenAIEmbeddingFunction`). Adding a new
collection beside the 3 existing leaf-level ones (`iso27001_2022`,
`gdpr_2016_679`, `arioncombly_all`) reuses all the plumbing and the
prod path's embedding cache.

## Sanity-test outcome

10 natural-language probes mirroring real tenant phrasing
(`/tmp/test_must_retrieval.py`). Every probe returned the correct
auditor-grade MUSTs in top-5, with cosine distances 0.7-0.85 (cos
sim 0.15-0.30 — strong semantic match given short queries):

- "We revoke access within 24h when an employee leaves" →
  `A.5.18:rev_hr_link` (perfect)
- "Privacy policy is reviewed annually" → `Art.13:rev_date`,
  `Art.14:rev_date`, `A.5.34:rev_date` (mixed ISO + GDPR, all correct)
- "Incidents reported to supervisory authority within 72h" →
  `Art.33:timing` (perfect)
- "Least privilege" → `A.5.15`, `A.5.18`, `A.8.18` cluster (correct
  cross-control surface)

## How to use it next

The next session's extractor prototype walks each MUST in
`target_leaves`, queries `musts_arioncomply` for the top-K nearest
neighbors of each doc passage, and runs a focused LLM verify call
per (MUST, passage) pair. The yield_ratio_pct telemetry shipped in
[[llm-narrative-under-discovery-audit-2026-06-26]] is the A/B gauge
to confirm semantic-search extraction beats the current single-shot
baseline.

## Non-obvious decisions

### Catalog source = Python file, not Neo4j

`document_requirements.py` is the authoritative source. Neo4j has
the same data but mediated by `load_to_neo4j.py`. Reading Python
directly skips one layer of indirection and keeps the index build
runnable without a Neo4j connection (the loader doesn't need to be
running). Trade-off: drift between Python and Neo4j is possible if
the loader fails — but that's already a known issue that surfaces
elsewhere (graph queries vs catalog text mismatches).

### One collection, not three

The existing leaf indexer splits ISO / GDPR / combined into three
collections — useful when chat queries want to filter "ISO only".
For MUSTs the extractor always queries within a specific
target_leaves set, so the standard is implicit in the leaf_id
metadata. One collection + metadata filter is simpler.

### Same embedding model as leaf collections

`text-embedding-3-small`, not `text-embedding-3-large`. The
orchestrator config defaults to 3-large but the indexer's actual
ship default is 3-small. Stay consistent with what's in production
— mixing dimensions would prevent any future hybrid retrieval
(leaf + MUST scores combined).

## Related

- [[llm-narrative-under-discovery-audit-2026-06-26]] — the audit
  that motivated this and shipped the `yield_ratio_pct` telemetry
  that will measure whether semantic-search extraction wins.
- [[tabular-evidence-rows-2026-06-26]] — sibling under-discovery
  fix (different class — multi-row tabular content; this is
  narrative LLM extraction).
- [[feedback-telemetry-before-trouble]] — instrument absence, not
  just rejection. Yield_ratio is exactly that — counts what we
  *didn't* find.
