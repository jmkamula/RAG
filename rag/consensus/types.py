"""
Data types for the retrieval-first consensus layer.

All signals return SignalOutput. The aggregator fuses them into a
ConsensusResult that the classify graph node consumes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SignalOutput:
    """One signal's normalised contribution.

    Every signal — retrieval, explicit_refs, curated_lexicon, etc. —
    returns one of these. The aggregator only needs to look at these
    fields to fuse a consensus verdict.

    Attributes:
        name:           Signal identifier, matches the module name
                        (e.g. "retrieval", "explicit_refs").
        refs:           [(ref, weight), ...] ordered high-to-low weight.
                        Weights are signal-local (see config for scales).
                        Empty when the signal has no ref opinion.
        question_type:  Signal's opinion on the query taxonomy, or None
                        (e.g. curated_lexicon fires "definition" on
                        "what does OFI mean").
        framework:      Signal's opinion on the primary framework, e.g.
                        "ISO27001:2022" or "GDPR:2016/679". None if the
                        signal has no framework opinion.
        metadata:       Signal-specific extras — retrieval scores,
                        graph tightness metrics, curated_lexicon
                        pattern that matched, etc. Kept opaque so
                        signals can evolve without changing the wire.
        fired:          False when the signal was skipped or had no
                        input (e.g. session_context with no active_refs).
                        The aggregator does not count non-fired signals
                        toward corroborators.
    """
    name:          str
    refs:          list[tuple[str, float]] = field(default_factory=list)
    question_type: Optional[str]           = None
    framework:     Optional[str]           = None
    metadata:      dict                    = field(default_factory=dict)
    fired:         bool                    = True

    def top_ref(self) -> Optional[str]:
        return self.refs[0][0] if self.refs else None

    def has_ref(self, ref: str) -> bool:
        return any(r == ref for r, _ in self.refs)


@dataclass
class ClarificationOption:
    """One deterministic clarification choice — no LLM prompt needed."""
    ref:        str
    title:      str
    framework:  str


@dataclass
class Clarification:
    """A deterministic clarification, emitted when signals disagree.

    kind:
      "topic_ambiguity"   — multiple candidate refs in different families
      "framework_missing" — multi-framework tenant, query framework unclear
      "below_floor"       — retrieval too weak for any confident answer
    """
    kind:     str
    question: str
    options:  list[ClarificationOption] = field(default_factory=list)


@dataclass
class ConsensusResult:
    """Aggregated outcome across signals.

    verdict:
      "confident"    — top ref + question_type resolved with corroborators;
                       skip the LLM classifier.
      "ambiguous"    — signals disagree in a way that needs the user to
                       choose; emit clarification.
      "insufficient" — nothing reached the floor; the caller falls
                       through to the LLM classifier (intra-consensus
                       fallback). Ship 2'.o (2026-07-16) retired the
                       USE_LEGACY_CLASSIFIER kill-switch — the layer
                       always runs.
    """
    verdict:              str
    refs:                 list[str] = field(default_factory=list)
    question_type:        Optional[str] = None
    framework:            Optional[str] = None
    top_ref_confidence:   float = 0.0
    corroborators:        int   = 0
    signals:              list[SignalOutput] = field(default_factory=list)
    disagreement_notes:   list[str] = field(default_factory=list)
    clarification:        Optional[Clarification] = None
    llm_fallback_needed:  bool = False
    latency_ms:           int  = 0


@dataclass
class ConsensusConfig:
    """Thresholds and weights the aggregator applies.

    Defaults chosen to match the intake arc's precision-weighted math.
    Empirical tuning after chat_consensus_log has real data.

    Thresholds:
      refs_min_floor       — below this the top ref is discarded
      refs_confident_floor — above this + ≥2 corroborators = confident
      refs_tie_band        — scores within this at the top are a tie
      min_corroborators    — how many signals must agree for confident

    Weights (per-signal contribution to a ref's fused score):
      explicit_ref_weight       — Signal B hard anchor (1.0)
      curated_lexicon_weight    — Signal C match (1.00 — highest tier,
                                    curator-authored mappings are
                                    authoritative)
      framework_hint_weight     — Signal F match on framework (0.20)
      session_boost_weight      — Signal G active_ref boost (0.10)
      posture_boost_weight      — Signal D NC/OFI boost (0.15)
      graph_tight_family_boost  — Signal E same-family boost (0.05)
      graph_spread_penalty      — Signal E outlier penalty (-0.10)

    Signal A (retrieval) contributes its own cosine score, no separate
    weight — the aggregator uses the raw score as the base.
    """
    refs_min_floor:            float = 0.20
    refs_confident_floor:      float = 0.35
    refs_tie_band:             float = 0.05
    min_corroborators:         int   = 2
    max_top_k_retrieval:       int   = 10

    explicit_ref_weight:       float = 1.00
    # Signal C (curated_lexicon) is the highest-weight signal because
    # it encodes learned domain knowledge from human curators
    # (DOCUMENT_TOPIC_MAP + CLEAR_INTENT_PHRASES). When the tenant/
    # curator says "chatgpt → A.8.19", that mapping is authoritative
    # — it's the optimal place to enhance as we learn from evals and
    # real queries. Weight >= explicit_ref_weight so a curated topic
    # match wins over retrieval spread even when the topic isn't
    # semantically obvious in Chroma's business_description.
    curated_lexicon_weight:    float = 1.00
    framework_hint_weight:     float = 0.20
    session_boost_weight:      float = 0.10
    posture_boost_weight:      float = 0.15
    graph_tight_family_boost:  float = 0.05
    graph_spread_penalty:      float = -0.10

    # Log tuning
    log_full_signals_json:     bool  = True

    # Kill-switch — fall through to legacy LLM classifier when
    # consensus is insufficient. When False, the classify node
    # returns a generic clarify instead of running the LLM.
    llm_fallback_enabled:      bool  = True

    # Ship 1.5: inline gatekeeper toggle. When False, aggregator's
    # tentative decision goes straight through. Useful in tests
    # that want to isolate aggregator behavior without LLM.
    gatekeeper_enabled_flag:   bool  = True

    def with_overrides(self, **kwargs) -> "ConsensusConfig":
        """Return a copy with fields replaced — for tenant-scoped tuning later."""
        from dataclasses import replace
        return replace(self, **kwargs)
