"""
Signal: content_shape_penalty — Ship 11'.c gate as a negative signal.

For each fingerprinted candidate, check whether the excerpt looks
like a field label or section header. If yes, apply the penalty.

Depends on fingerprint_keyword output. Runs alongside semantic_fit_gate.
"""
from __future__ import annotations

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
    if not fingerprint_signal or not fingerprint_signal.fired:
        return ExtractionSignalOutput(name="content_shape_penalty", fired=False)

    per_candidate = fingerprint_signal.metadata.get("per_candidate", {}) or {}
    if not per_candidate:
        return ExtractionSignalOutput(name="content_shape_penalty", fired=False)

    from rag.intake.extractor import _looks_like_field_or_header

    candidates: dict[CandidateKey, float] = {}
    n_penalized = 0
    for key, meta in per_candidate.items():
        excerpt = meta.get("excerpt")
        must_id = key[1]
        if not excerpt:
            continue
        drop, _reason = _looks_like_field_or_header(excerpt, must_id=must_id)
        if drop:
            candidates[key] = cfg.content_shape_penalty
            n_penalized += 1

    return ExtractionSignalOutput(
        name       = "content_shape_penalty",
        candidates = candidates,
        metadata   = {"n_penalized": n_penalized},
        fired      = True,
    )
