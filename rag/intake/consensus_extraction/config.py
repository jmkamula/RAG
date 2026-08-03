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

    # Ship 43'.b — BM25 lexical scoring as 9th consensus signal.
    # Complements must_semantic (embeddings/semantic) with lexical
    # relevance ranking. Same discovery-mode shape as must_semantic:
    # emits candidates outside scoped_leaf_ids via top-K + score floor.
    # Weight 0.25 sits between fingerprint (0.50, exact-token-set) and
    # must_semantic (0.30, semantic-only) — lexical fuzzy is stronger
    # than pure semantic but weaker than curated exact match.
    bm25_weight:               float = 0.25
    bm25_topk:                 int   = 30
    bm25_score_floor:          float = 1.0

    # Ship 54'.e Phase 3 — structural_maturity as 10th consensus signal.
    # Doc-level boost that fires when the uploaded document carries
    # consultant-toolkit structural shape (doc-control header,
    # revision history table, interested parties, TOC). Reads the
    # summary Phase 2 stashes on doc.extraction_metrics. Every
    # scoped candidate gets the same per-doc boost — not a per-
    # candidate match. Weight 0.15 sits between per_protocol_scope
    # (0.10, tiebreaker) and bm25 (0.25, lexical) — the signal is
    # subordinate to per-candidate evidence but adds real corroboration
    # when the doc IS a formal artefact.
    structural_maturity_weight: float = 0.15

    # Feature flags
    llm_arbiter_enabled:       bool = False    # False in shadow mode; True post-cutover
    # Ship 37'.b — toggle for the no-excerpt-auto-drop invariant.
    # Default True (Ship 35 shape). Set False to bypass the invariant
    # for measurement / HITL sampling of what the invariant drops.
    no_excerpt_auto_drop:      bool = True

    # Ship 38'.b — invariant escape clause. When invariant is on AND
    # the candidate has no excerpt BUT score ≥ escape_score AND
    # corroborators ≥ escape_corrob, route to arbiter (LLM decides)
    # instead of hard-drop. Ship 37 HITL: 4 of 6 should-have-accepted
    # cases had score ≥ 1.5 + corrob ≥ 3 (primary-subject MUSTs on
    # docs where multiple signals corroborated but fingerprint didn't
    # fire).
    no_excerpt_escape_score:   float = 1.5
    no_excerpt_escape_corrob:  int   = 3

    def with_overrides(self, **kwargs) -> "ExtractionConsensusConfig":
        from dataclasses import replace
        return replace(self, **kwargs)


def default_config() -> ExtractionConsensusConfig:
    return ExtractionConsensusConfig()
