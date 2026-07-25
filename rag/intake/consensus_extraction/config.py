"""
Extraction consensus config — weights + thresholds in one place.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExtractionConsensusConfig:
    """Tunable via env / tenant scope; defaults from 33'.a-redux design.

    Thresholds:
      accept_floor:      score ≥ this AND corrob ≥ min_corroborators
                         → auto-accept (no LLM)
      arbiter_floor:     arbiter_floor ≤ score < accept_floor
                         → LLM gatekeeper decides
      min_corroborators: how many positive-weight signals must fire
                         for a candidate to auto-accept

    Weights (per-signal contribution to the candidate's fused score):
      explicit_ref_weight       — self-cite is authoritative
      doc_mappings_weight       — curator-authored filename→leaf mapping
      fingerprint_weight        — Ship 28+29 keyword catalog match
      must_semantic_weight      — semantic_musts_in_scope top-K
      per_protocol_weight       — per-standard Chroma retrieval
      semantic_fit_pass_weight  — _semantic_fit_ok passes threshold
      semantic_fit_fail_weight  — _semantic_fit_ok below threshold (penalty)
      content_shape_penalty     — sentence looks like field/header

    Empirical tuning after intake_consensus_log has real data.
    """
    # Thresholds
    accept_floor:      float = 0.75
    arbiter_floor:     float = 0.40
    min_corroborators: int   = 2

    # Signal weights
    explicit_ref_weight:       float = 1.00
    doc_mappings_weight:       float = 0.60
    fingerprint_weight:        float = 0.50
    must_semantic_weight:      float = 0.30
    # Ship 33'.b v3: per_protocol_scope reduced from 0.20 → 0.10 because
    # v2 measurement showed it correlates heavily with fingerprint +
    # must_semantic (all three answer "is this leaf in scope for this
    # doc?"). Lower weight so it acts as a small tiebreaker rather than
    # a corroboration multiplier.
    per_protocol_weight:       float = 0.10
    semantic_fit_pass_weight:  float = 0.30
    semantic_fit_fail_weight:  float = -0.30
    content_shape_penalty:     float = -0.50

    # Ship 33'.b v3: evidence_uniqueness — cross-candidate signal that
    # penalises multi-attribution (same excerpt claimed by many
    # candidates). Threshold = N candidates sharing an excerpt for the
    # penalty to fire.
    evidence_share_threshold:  int   = 5
    evidence_uniqueness_penalty: float = -0.50

    # Semantic top-K sizes
    must_semantic_topk:        int = 30
    per_protocol_topk:         int = 20

    # Feature flags
    llm_arbiter_enabled:       bool = False    # False in shadow mode; True post-cutover

    def with_overrides(self, **kwargs) -> "ExtractionConsensusConfig":
        from dataclasses import replace
        return replace(self, **kwargs)


def default_config() -> ExtractionConsensusConfig:
    return ExtractionConsensusConfig()
