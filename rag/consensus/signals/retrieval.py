"""
Signal A — ChromaDB semantic retrieval (the anchor).

Reuses the existing VectorRetriever which searches over ChromaDB
enriched with natural-language business_description on every
compliance node. This is the RETRIEVAL-FIRST signal — the whole
consensus layer is anchored on what semantic search returns.

Role in consensus:
  - Anchor. Top-K refs with cosine scores are the base for all
    other signals to corroborate against.
  - Score is the raw signal weight (0-1, higher = more relevant).
  - Framework inferred by majority vote across top-K standard_ids.
  - metadata records the full score distribution + framework counts
    so the aggregator can detect tie bands + framework spread.
  - fired=False when retriever is None (test injection) or returns
    no results (empty corpus / connection failure).
"""
from __future__ import annotations

from typing import Optional

from rag.consensus.types import SignalOutput, ConsensusConfig


def retrieve(
    query:      str,
    retriever,                          # VectorRetriever instance (or fake)
    standards:  Optional[list[str]] = None,
    cfg:        Optional[ConsensusConfig] = None,
) -> SignalOutput:
    """Run ChromaDB semantic search and normalise into a SignalOutput.

    Args:
        query:     Raw user query text.
        retriever: Anything with a .search(query, n, standards)->obj
                   where obj has a .results list of VectorResult-like
                   items (with .ref, .score, .standard_id). Duck-typed
                   so tests can substitute a fake.
        standards: Restrict to specific frameworks (tenant scope).
        cfg:       ConsensusConfig; defaults to ConsensusConfig() when None.
    """
    cfg = cfg or ConsensusConfig()
    if not query or retriever is None:
        return SignalOutput(name="retrieval", fired=False)

    try:
        ctx = retriever.search(query, n=cfg.max_top_k_retrieval,
                                standards=standards)
    except Exception as e:
        return SignalOutput(
            name="retrieval",
            fired=False,
            metadata={"error": type(e).__name__, "detail": str(e)[:200]},
        )

    results = getattr(ctx, "results", None) or []
    if not results:
        return SignalOutput(name="retrieval", fired=False,
                            metadata={"empty": True})

    # Build (ref, score) tuples, dedupe by ref keeping best score
    seen_refs:      dict[str, float] = {}
    framework_votes: dict[str, int]   = {}
    all_scores:     list[float]       = []

    for r in results:
        ref   = getattr(r, "ref", None)
        score = getattr(r, "score", 0.0) or 0.0
        std   = getattr(r, "standard_id", "")
        if not ref:
            continue
        all_scores.append(score)
        if ref not in seen_refs or score > seen_refs[ref]:
            seen_refs[ref] = score
        framework_votes[std] = framework_votes.get(std, 0) + 1

    if not seen_refs:
        return SignalOutput(name="retrieval", fired=False,
                            metadata={"no_valid_refs": True})

    # Order by score desc
    ordered = sorted(seen_refs.items(), key=lambda kv: kv[1], reverse=True)
    refs_out = ordered  # list of (ref, score)

    # Framework majority — the standard_id with the most hits in top-K
    if framework_votes:
        dominant = max(framework_votes.items(), key=lambda kv: kv[1])
        primary_framework = dominant[0] if dominant[0] else None
    else:
        primary_framework = None

    top_score  = ordered[0][1]
    tie_count  = sum(1 for _, s in ordered if s >= top_score - cfg.refs_tie_band)

    return SignalOutput(
        name       = "retrieval",
        refs       = refs_out,
        framework  = primary_framework,
        metadata   = {
            "n_results":         len(ordered),
            "top_score":         top_score,
            "top_ref":           ordered[0][0],
            "tie_band_size":     tie_count,
            "framework_votes":   framework_votes,
            "score_distribution": [round(s, 4) for _, s in ordered[:5]],
            "above_min_floor":   top_score >= cfg.refs_min_floor,
            "above_confident":   top_score >= cfg.refs_confident_floor,
        },
        fired      = True,
    )
