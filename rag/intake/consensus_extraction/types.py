"""
Data types for extraction consensus. Mirrors rag/consensus/types.py
shape; per-candidate (leaf_id, must_id) keying instead of ref-list.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# A candidate is a (leaf_id, must_id) pair. must_id may be None for
# leaf-level signals that don't have per-MUST resolution (e.g.
# per_protocol_scope only knows the control_ref).
CandidateKey = tuple[str, Optional[str]]   # (leaf_id, must_id | None)


@dataclass
class ExtractionSignalOutput:
    """One signal's contribution to the extraction consensus.

    Every signal — fingerprint_keyword, doc_mappings_target,
    must_semantic_topk, per_protocol_scope, explicit_ref,
    semantic_fit_gate, content_shape_penalty — returns one of these.

    Attributes:
        name:          Signal identifier matching the module name
                       (e.g. "fingerprint_keyword").
        candidates:    (leaf_id, must_id) -> signal-local weight.
                       Positive = "this candidate is real"; negative
                       = penalty (e.g. content-shape gate). Weights
                       come from ExtractionConsensusConfig, not from
                       the signal itself, so tuning happens in one
                       place.
        metadata:      Signal-specific extras — match position,
                       excerpt, retrieval score, etc. Kept opaque
                       so signals can evolve without changing the
                       wire.
        fired:         False when the signal was skipped (no input
                       available, dependency unavailable, etc.). The
                       aggregator does not count non-fired signals
                       toward corroborators.
    """
    name:        str
    candidates:  dict[CandidateKey, float] = field(default_factory=dict)
    metadata:    dict                       = field(default_factory=dict)
    fired:       bool                       = True


@dataclass
class CandidateVerdict:
    """Aggregator's decision on one candidate.

    verdict:
      "accept"  — score ≥ accept_floor AND corroborators ≥ min_corroborators.
                  Emit as a finding without LLM cost.
      "arbiter" — arbiter_floor ≤ score < accept_floor. LLM
                  gatekeeper decides (batched arbiter pass).
      "drop"    — score < arbiter_floor. Below the threshold; drop.

    signals:      Names of signals that emitted this candidate with
                  positive weight (corroborators).
    fingerprint_excerpt: The doc-body excerpt captured by the
                  fingerprint match (if fingerprint_keyword fired for
                  this candidate). Used as the finding's evidence_text
                  and as input to the LLM arbiter when applicable.
    """
    candidate:            CandidateKey
    score:                float
    corroborators:        int
    signals:              list[str]
    verdict:              str
    fingerprint_excerpt:  Optional[str] = None
    fingerprint_position: Optional[int] = None
    control_ref:          Optional[str] = None
    standard_id:          Optional[str] = None


@dataclass
class ExtractionConsensusResult:
    """Result of one doc's consensus extraction pass.

    Consumed by the shadow-mode logger and (post-cutover) the
    write path.
    """
    verdicts:              list[CandidateVerdict]
    total_candidates:      int = 0
    n_accept:              int = 0
    n_arbiter:             int = 0
    n_drop:                int = 0
    n_signals_fired:       int = 0
    signal_fire_counts:    dict[str, int] = field(default_factory=dict)
    latency_ms:            int = 0

    def accepted(self) -> list[CandidateVerdict]:
        return [v for v in self.verdicts if v.verdict == "accept"]

    def arbiter_zone(self) -> list[CandidateVerdict]:
        return [v for v in self.verdicts if v.verdict == "arbiter"]

    def dropped(self) -> list[CandidateVerdict]:
        return [v for v in self.verdicts if v.verdict == "drop"]
