"""
Signal: evidence_uniqueness — cross-candidate signal that penalizes
findings whose evidence_text is shared by many other candidates.

Directly addresses Ship 32's finding: one sentence producing 43
fingerprint findings across 43 different MUSTs. All 43 candidates
share the same evidence_text; this signal counts how many
candidates share each text and penalizes those above the threshold.

Depends on fingerprint_keyword output (excerpts). Runs after it.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from rag.intake.consensus_extraction.types import (
    ExtractionSignalOutput,
    CandidateKey,
)
from rag.intake.consensus_extraction.config import (
    ExtractionConsensusConfig,
)


def compute(
    doc:                Any,
    scoped_leaf_ids:    list[str],
    cfg:                ExtractionConsensusConfig,
    fingerprint_signal: ExtractionSignalOutput = None,
) -> ExtractionSignalOutput:
    """Count how many candidates share each excerpt. Penalize those
    whose share-count exceeds `evidence_share_threshold`.

    The share-count is the number of OTHER candidates whose
    fingerprint match extracted the same evidence_text. A generic
    summary sentence that matches N MUSTs will produce N candidates
    with identical excerpts.
    """
    if not fingerprint_signal or not fingerprint_signal.fired:
        return ExtractionSignalOutput(name="evidence_uniqueness", fired=False)

    per_candidate = fingerprint_signal.metadata.get("per_candidate", {}) or {}
    if not per_candidate:
        return ExtractionSignalOutput(name="evidence_uniqueness", fired=False)

    # Count excerpts across all candidates
    excerpt_counts: Counter[str] = Counter()
    for key, meta in per_candidate.items():
        excerpt = (meta.get("excerpt") or "").strip()
        if excerpt:
            excerpt_counts[excerpt] += 1

    # Apply penalty to candidates whose excerpt exceeds threshold
    candidates: dict[CandidateKey, float] = {}
    penalized = 0
    per_cand_meta: dict[CandidateKey, dict] = {}
    for key, meta in per_candidate.items():
        excerpt = (meta.get("excerpt") or "").strip()
        if not excerpt:
            continue
        share_count = excerpt_counts[excerpt]
        if share_count >= cfg.evidence_share_threshold:
            candidates[key] = cfg.evidence_uniqueness_penalty
            penalized += 1
        per_cand_meta[key] = {"share_count": share_count}

    return ExtractionSignalOutput(
        name       = "evidence_uniqueness",
        candidates = candidates,
        metadata   = {
            "n_penalized":         penalized,
            "n_total_excerpts":    sum(excerpt_counts.values()),
            "n_unique_excerpts":   len(excerpt_counts),
            "top_shared_counts":   dict(excerpt_counts.most_common(3)),
            "per_candidate":       per_cand_meta,
        },
        fired      = True,
    )
