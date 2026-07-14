"""
Signal E — graph tightness (family clustering, pure ref-string analysis).

Given a set of candidate refs (from other signals — usually
retrieval's top-K), measure how tightly they cluster in the same
"family" (first two segments of the ref — A.5, A.7, Art.32, etc.).

Role in consensus:
  - Ambiguity detector. If retrieval's top-K spread across A.5, A.7,
    A.8 (three different families), the query is probably ambiguous
    and the aggregator should ask to clarify.
  - Ref-level modifier: refs in the majority family get a small boost;
    refs outside get a small penalty (graph_tight_family_boost +
    graph_spread_penalty from config).
  - No I/O — reuses the family taxonomy from framework_scope_guard.
"""
from __future__ import annotations

from typing import Optional
from collections import Counter

from rag.consensus.types import SignalOutput, ConsensusConfig
from rag.guards.framework_scope_guard import _family_of


def graph_tightness(
    candidate_refs: list[str],
    cfg:            Optional[ConsensusConfig] = None,
) -> SignalOutput:
    """Score cluster tightness across candidate refs.

    Args:
        candidate_refs: refs from other signals — usually retrieval's
                        top-K. Order matters only for tie-breaking on
                        the majority family (first-seen wins).
        cfg:            ConsensusConfig; None → defaults.
    """
    cfg = cfg or ConsensusConfig()
    if not candidate_refs:
        return SignalOutput(name="graph_tightness", fired=False)

    # Compute family per ref
    families: list[tuple[str, str]] = [(r, _family_of(r)) for r in candidate_refs]

    # Count families
    fam_counts = Counter(fam for _, fam in families if fam)
    if not fam_counts:
        return SignalOutput(name="graph_tightness", fired=False,
                            metadata={"no_families": True})

    total = sum(fam_counts.values())
    # Preserve first-seen order for the majority: sort by count desc
    # then by first-seen order (via candidate_refs)
    first_seen: dict[str, int] = {}
    for i, (_, fam) in enumerate(families):
        if fam and fam not in first_seen:
            first_seen[fam] = i
    ordered = sorted(
        fam_counts.items(),
        key=lambda kv: (-kv[1], first_seen.get(kv[0], 999)),
    )
    majority_family, majority_count = ordered[0]

    # Tightness = share of candidates in the majority family
    tightness = majority_count / total

    # Emit refs with tightness modifiers: majority members +boost,
    # outliers -penalty. Weight is the modifier — aggregator adds
    # this to the base score.
    boost   = cfg.graph_tight_family_boost
    penalty = cfg.graph_spread_penalty
    refs_out: list[tuple[str, float]] = []
    for ref, fam in families:
        if not fam:
            continue
        if fam == majority_family:
            refs_out.append((ref, boost))
        else:
            refs_out.append((ref, penalty))

    is_tight = tightness >= 0.5   # majority is at least half — heuristic

    return SignalOutput(
        name       = "graph_tightness",
        refs       = refs_out,
        metadata   = {
            "family_counts":    dict(fam_counts),
            "majority_family":  majority_family,
            "majority_share":   round(tightness, 3),
            "tight":            is_tight,
            "families_present": list(fam_counts.keys()),
            "n_candidates":     total,
        },
        fired      = True,
    )
