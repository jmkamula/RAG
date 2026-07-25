"""
Extraction consensus aggregator.

Fuses per-candidate signal contributions into per-candidate verdicts.
Same math as rag/consensus/aggregator.py::_fuse_ref_scores adapted
for (leaf_id, must_id) keys.
"""
from __future__ import annotations

from typing import Optional

from rag.intake.consensus_extraction.types import (
    ExtractionSignalOutput,
    CandidateVerdict,
    CandidateKey,
    ExtractionConsensusResult,
)
from rag.intake.consensus_extraction.config import (
    ExtractionConsensusConfig,
    default_config,
)


# Which signals count toward corroborator count. Negative-weight
# signals (penalties) are excluded — they modulate the score but
# don't count as agreement.
_POSITIVE_SIGNAL_NAMES = {
    "explicit_ref",
    "doc_mappings_target",
    "fingerprint_keyword",
    "must_semantic_topk",
    "per_protocol_scope",
    "semantic_fit_gate",     # both pass and fail modes emit for this signal;
                             #   pass counts as corroborator, fail doesn't
    "bridge_substantiveness",
}


def aggregate_extraction(
    signals: list[ExtractionSignalOutput],
    cfg:     Optional[ExtractionConsensusConfig] = None,
) -> ExtractionConsensusResult:
    """Fuse signals into per-candidate verdicts.

    For each candidate that appears in any fired signal:
      score        = Σ (signal-weight) across signals that emit it
      corroborators = count of positive-weight signals emitting it
      verdict:
        accept   if score ≥ accept_floor AND corroborators ≥ min_corroborators
        arbiter  else if score ≥ arbiter_floor
        drop     otherwise

    Enriches CandidateVerdicts with fingerprint excerpt + position + control_ref +
    standard_id from the fingerprint_keyword signal's metadata (single source of
    truth for finding-level fields; other signals only vote).
    """
    if cfg is None:
        cfg = default_config()

    fused_scores:   dict[CandidateKey, float]      = {}
    corroborators:  dict[CandidateKey, int]        = {}
    signals_by_c:   dict[CandidateKey, list[str]]  = {}
    signal_fire_counts: dict[str, int]             = {}

    # Metadata joins — pulled from fingerprint_keyword signal
    fp_excerpts:  dict[CandidateKey, str] = {}
    fp_positions: dict[CandidateKey, int] = {}
    fp_control_refs: dict[CandidateKey, str] = {}
    fp_standard_ids: dict[CandidateKey, str] = {}

    for sig in signals:
        if not sig.fired:
            continue
        signal_fire_counts[sig.name] = len(sig.candidates)
        for candidate, weight in sig.candidates.items():
            fused_scores[candidate] = fused_scores.get(candidate, 0.0) + weight
            signals_by_c.setdefault(candidate, []).append(sig.name)
            if weight > 0 and sig.name in _POSITIVE_SIGNAL_NAMES:
                corroborators[candidate] = corroborators.get(candidate, 0) + 1

        # Metadata harvest — fingerprint_keyword emits excerpt + position
        if sig.name == "fingerprint_keyword":
            per_match = sig.metadata.get("per_candidate", {}) or {}
            for candidate, meta in per_match.items():
                if isinstance(meta, dict):
                    if meta.get("excerpt"):
                        fp_excerpts[candidate] = meta["excerpt"]
                    if meta.get("position") is not None:
                        fp_positions[candidate] = meta["position"]
                    if meta.get("control_ref"):
                        fp_control_refs[candidate] = meta["control_ref"]
                    if meta.get("standard_id"):
                        fp_standard_ids[candidate] = meta["standard_id"]

    verdicts: list[CandidateVerdict] = []
    n_accept = n_arbiter = n_drop = 0
    for candidate in sorted(fused_scores.keys()):
        score = fused_scores[candidate]
        corrob = corroborators.get(candidate, 0)
        excerpt = fp_excerpts.get(candidate)

        # Ship 34'.c finding — no-excerpt-auto-drop invariant. When a
        # candidate has no fingerprint_excerpt, there is no doc-body
        # text for the arbiter LLM to evaluate. Ship 34 HITL sample:
        # 17 of 20 sampled arbiter rejects were no-excerpt candidates
        # (scope signals voted "leaf in-scope" but no fingerprint
        # match); LLM correctly rejected all 17. Save the LLM
        # roundtrip by dropping deterministically. Scope signals
        # alone should not authorize LLM review.
        #
        # Ship 37'.b — toggle via cfg.no_excerpt_auto_drop. Default
        # True (Ship 35 shape). Set False for HITL sampling of what
        # the invariant drops.
        if not excerpt and cfg.no_excerpt_auto_drop:
            verdict = "drop"; n_drop += 1
        elif score >= cfg.accept_floor and corrob >= cfg.min_corroborators:
            verdict = "accept"; n_accept += 1
        elif score >= cfg.arbiter_floor:
            verdict = "arbiter"; n_arbiter += 1
        else:
            verdict = "drop"; n_drop += 1
        verdicts.append(CandidateVerdict(
            candidate            = candidate,
            score                = round(score, 3),
            corroborators        = corrob,
            signals              = signals_by_c.get(candidate, []),
            verdict              = verdict,
            fingerprint_excerpt  = excerpt,
            fingerprint_position = fp_positions.get(candidate),
            control_ref          = fp_control_refs.get(candidate),
            standard_id          = fp_standard_ids.get(candidate),
        ))

    return ExtractionConsensusResult(
        verdicts            = verdicts,
        total_candidates    = len(verdicts),
        n_accept            = n_accept,
        n_arbiter           = n_arbiter,
        n_drop              = n_drop,
        n_signals_fired     = sum(1 for s in signals if s.fired),
        signal_fire_counts  = signal_fire_counts,
    )
