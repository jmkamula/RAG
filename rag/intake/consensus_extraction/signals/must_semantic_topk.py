"""
Signal: must_semantic_topk — first caller of `semantic_musts_in_scope`.

Queries the `musts_arioncomply` Chroma collection with the doc text;
top-K MUSTs (default 30) receive this signal's weight. Independent
of fingerprint matches — this is the semantic corroboration signal.

Ship 39'.b — the scope filter on ctrl_to_leaves was removed. Emit
candidates for ALL Chroma-surfaced MUSTs regardless of whether their
leaf's control is in scoped_leaf_ids. Restores critic-verifier's
`_build_extend_pool(pool_size=100)` discovery breadth. Aggregator
still needs corroboration to auto-accept, so scope-only candidates
can't over-accept alone.

For each must_id, we resolve its parent leaf_id via Neo4j
`MUST_CONTAIN` query. Results cached at process level.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from rag.intake.consensus_extraction.types import (
    ExtractionSignalOutput,
    CandidateKey,
)
from rag.intake.consensus_extraction.config import (
    ExtractionConsensusConfig,
)


logger = logging.getLogger(__name__)

# Process-cached must_id -> leaf_id lookup. Populated lazily on first
# call. Since a MUST belongs to exactly one leaf (via MUST_CONTAIN
# edge), the mapping is stable across runs.
_MUST_LEAF_CACHE: dict[str, str] = {}


def _resolve_must_to_leaf(must_ids: list[str]) -> dict[str, str]:
    """Return {must_id: leaf_id} via Neo4j MUST_CONTAIN query.

    Uses process-level cache to avoid repeat lookups. Cache
    populated lazily as new must_ids are encountered.

    Fail-open: on Neo4j unavailable / query error, returns partial
    map with cached entries only; caller degrades gracefully.
    """
    missing = [m for m in must_ids if m and m not in _MUST_LEAF_CACHE]
    if not missing:
        return {m: _MUST_LEAF_CACHE[m] for m in must_ids if m in _MUST_LEAF_CACHE}

    try:
        from rag.posture_loader import _build_engine_neo4j_driver
        driver = _build_engine_neo4j_driver()
        if driver is None:
            return {m: _MUST_LEAF_CACHE.get(m, "") for m in must_ids if m}
        with driver.session() as s:
            rows = s.run(
                """
                MATCH (er:EvidenceRequirement)-[:MUST_CONTAIN]->(ci:ChecklistItem)
                 WHERE ci.id IN $ids
                RETURN ci.id AS must_id, er.id AS leaf_id
                """,
                ids=missing,
            ).data()
        for r in rows:
            _MUST_LEAF_CACHE[r["must_id"]] = r.get("leaf_id") or ""
        try:
            driver.close()
        except Exception:
            pass
    except Exception as e:
        logger.warning("_resolve_must_to_leaf Neo4j query failed: %s", e)

    return {m: _MUST_LEAF_CACHE.get(m, "") for m in must_ids if m}


def compute(
    doc:              Any,
    scoped_leaf_ids:  list[str],
    cfg:              ExtractionConsensusConfig,
) -> ExtractionSignalOutput:
    """Ask the MUST Chroma collection for the top-K most semantically
    similar MUSTs to this doc. Emit each with `must_semantic_weight`.

    Ship 39'.b — no scope filter. All Chroma-surfaced MUSTs become
    candidates. Their leaf_id is resolved via Neo4j MUST_CONTAIN
    query.
    """
    from rag.intake.must_embedding_lookup import semantic_musts_in_scope

    doc_text = getattr(doc, "markdown", None) or getattr(doc, "full_text", None) or ""
    tenant_stds = getattr(doc, "standard_ids", None) or None
    if not doc_text:
        return ExtractionSignalOutput(name="must_semantic_topk", fired=False)

    must_ids = semantic_musts_in_scope(
        doc_text    = doc_text,
        top_k       = cfg.must_semantic_topk,
        tenant_stds = tenant_stds,
    )
    if not must_ids:
        return ExtractionSignalOutput(name="must_semantic_topk", candidates={}, fired=True)

    # Ship 39'.b — resolve must_id → leaf_id via Neo4j (was: filter
    # to scoped_leaf_ids' controls, which dropped cross-framework
    # mirrors). This removes layer 3 of the Ship 38 bottleneck stack.
    must_to_leaf = _resolve_must_to_leaf(list(must_ids))

    candidates: dict[CandidateKey, float] = {}
    n_in_scope = 0
    scoped_set = set(scoped_leaf_ids)
    for must_id in must_ids:
        leaf_id = must_to_leaf.get(must_id)
        if not leaf_id:
            continue
        candidates[(leaf_id, must_id)] = cfg.must_semantic_weight
        if leaf_id in scoped_set:
            n_in_scope += 1

    return ExtractionSignalOutput(
        name       = "must_semantic_topk",
        candidates = candidates,
        metadata   = {"n_must_ids_topk":         len(must_ids),
                      "n_candidates":            len(candidates),
                      "n_candidates_in_scope":   n_in_scope,
                      "n_candidates_out_of_scope": len(candidates) - n_in_scope},
        fired      = True,
    )
