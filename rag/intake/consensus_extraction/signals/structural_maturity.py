"""
Ship 54'.e Phase 3 — structural_maturity consensus signal.

Reads the doc-level structural evidence summary that Ship 54'.e
Phase 2 stashes on `doc.extraction_metrics['structural_evidence']`
and emits a per-candidate boost for every content-based candidate
in the extraction pass.

The rationale: a document that carries consultant-toolkit structural
shape (doc-control header, revision history, interested parties)
is a formal artefact — not an ad-hoc note. Content-based extractions
from a structurally-mature document are more likely to be real
compliance evidence, so the aggregator should give each candidate a
small boost.

Design shape:
  - Signal fires per-doc, boosts every candidate the same amount.
    Independent of whether fingerprint / doc_mappings / etc. fired.
  - Boost weight scales with structural evidence density (more
    detected patterns → larger boost, capped).
  - Metadata carries the summary so the aggregator + downstream can
    reference it.
  - Fires only when the doc has ≥1 structural pattern detected.
    Otherwise skips (doesn't count as corroborator).

This is the second half of Ship 54'.e's hybrid dual-role design:
Phase 2 gave structural patterns a self-standing inference_source
lane (structural_pattern findings bound to specific MUSTs); Phase 3
gives them a signal role that boosts content-based extractions.

Together, Ship 54'.e closes the round-trip: renderer emits doc-
control shape, detector recognises it on re-upload, AND uses it to
strengthen every other signal fired on the same document.
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


# Boost weight scales with how many structural patterns are present.
# One pattern (e.g., only revision history) → base weight. Multiple
# patterns → scaled up to full weight. Capped to keep the signal
# subordinate to per-candidate signals like fingerprint.
_PATTERN_MAX = 4       # doc_control + rev_history + interested_parties + toc
_PATTERN_BASE_FRAC = 0.4    # 1 pattern → 40% of full weight
_PATTERN_FULL_AT = 3        # ≥3 patterns → full weight


def compute(
    doc:              Any,   # ParsedDocument
    scoped_leaf_ids:  list[str],
    cfg:              ExtractionConsensusConfig,
) -> ExtractionSignalOutput:
    """Emit `structural_maturity_weight` for every scoped candidate
    when the doc has structural evidence markers.

    Reads: `doc.extraction_metrics['structural_evidence']` (populated
    by rag/intake/doc_pipeline.py after extract_structural_evidence
    runs). Skips (fired=False) when structural detection didn't run
    or didn't detect anything.

    Signal is doc-level not candidate-level, so every candidate gets
    the same weight. Corroborator-role: fires alongside content-based
    signals to add a "this doc is a formal artefact" boost.
    """
    if not scoped_leaf_ids:
        return ExtractionSignalOutput(name="structural_maturity", fired=False)

    metrics = getattr(doc, "extraction_metrics", None) or {}
    summary = metrics.get("structural_evidence") or {}
    if not summary:
        # Doc pipeline didn't run structural detection (skipped by
        # config OR older code path). Non-fatal.
        return ExtractionSignalOutput(name="structural_maturity", fired=False)

    # Count distinct structural patterns present.
    patterns_present = 0
    if summary.get("doc_control_present"):
        patterns_present += 1
    if summary.get("revision_history"):
        patterns_present += 1
    if summary.get("interested_parties", 0) > 0:
        patterns_present += 1
    if summary.get("toc"):
        patterns_present += 1
    if summary.get("signatures", 0) > 0:
        # Signatures overlap with doc_control (both prove approval);
        # count as half a pattern so we don't double-boost when both
        # signals corroborate the same evidence.
        patterns_present += 0.5

    if patterns_present == 0:
        return ExtractionSignalOutput(name="structural_maturity", fired=True)

    # Scale weight linearly between _PATTERN_BASE_FRAC (1 pattern)
    # and 1.0 (≥ _PATTERN_FULL_AT patterns).
    if patterns_present >= _PATTERN_FULL_AT:
        scale = 1.0
    else:
        # 1 pattern → base; interpolate up
        scale = _PATTERN_BASE_FRAC + (
            (1.0 - _PATTERN_BASE_FRAC)
            * ((patterns_present - 1) / max(1, _PATTERN_FULL_AT - 1))
        )
    boost = cfg.structural_maturity_weight * scale

    candidates: dict[CandidateKey, float] = {}
    # Emit boost for every scoped candidate — one per (leaf_id, None)
    # since the signal doesn't have per-MUST resolution. The aggregator
    # sums these into the leaf-level score. Ship 33'.b's per-MUST
    # per_protocol_scope pattern (same shape).
    for lid in scoped_leaf_ids:
        candidates[(lid, None)] = boost

    return ExtractionSignalOutput(
        name        = "structural_maturity",
        candidates  = candidates,
        fired       = True,
        metadata    = {
            "patterns_present":     patterns_present,
            "boost":                boost,
            "scale":                scale,
            "structural_summary":   summary,
        },
    )


__all__ = ["compute"]
