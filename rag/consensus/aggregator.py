"""
Consensus aggregator — fuses SignalOutputs into a ConsensusResult.

The math is deliberately simple + inspectable. Every decision is a
sum-of-weights per ref plus a corroborator count. Tuning happens
via ConsensusConfig (empirical from chat_consensus_log later).

Verdict decision tree:

    if no signal fired:
        insufficient — nothing to work with
    elif top ref score >= refs_confident_floor AND
         corroborators >= min_corroborators:
        confident
    elif top-K within refs_tie_band span multiple families:
        ambiguous — emit clarification
    elif top ref score < refs_min_floor:
        insufficient — score too low
    else:
        confident (borderline — score above min but not confident_floor,
        or above confident_floor but only 1 corroborator)

Priority for question_type: Signal C (curated_lexicon) → Signal G
(session carryover) → None (caller decides / falls back).

Priority for framework: Signal B (explicit_refs) → Signal F
(framework_hint) → Signal A (retrieval majority) → None.
"""
from __future__ import annotations

from typing import Optional

from rag.consensus.types import (
    SignalOutput, ConsensusResult, ConsensusConfig,
    Clarification, ClarificationOption,
)


# Signals whose entries count toward the corroborator count on a ref.
# Framework_hint has no ref opinion so is excluded automatically.
_REF_EMITTING_SIGNAL_NAMES = {
    "retrieval",
    "explicit_refs",
    "curated_lexicon",
    "session_context",
    "graph_tightness",
    "posture_boost",
}


def _fuse_ref_scores(
    signals: list[SignalOutput],
) -> tuple[dict[str, float], dict[str, int], dict[str, list[str]]]:
    """Union refs across signals.

    Returns:
        fused_scores:   ref -> sum of weights across all signals
        corroborators:  ref -> count of signals contributing POSITIVE
                        weight for this ref (graph_tightness penalties
                        don't count as corroboration)
        signals_by_ref: ref -> list of signal names that emitted it
    """
    fused_scores:   dict[str, float]     = {}
    corroborators:  dict[str, int]       = {}
    signals_by_ref: dict[str, list[str]] = {}

    for sig in signals:
        if not sig.fired:
            continue
        if sig.name not in _REF_EMITTING_SIGNAL_NAMES:
            continue
        seen_in_this_signal: set[str] = set()
        for ref, weight in sig.refs:
            fused_scores[ref] = fused_scores.get(ref, 0.0) + weight
            signals_by_ref.setdefault(ref, []).append(sig.name)
            # Corroboration: only positive contributions count
            if weight > 0 and ref not in seen_in_this_signal:
                corroborators[ref] = corroborators.get(ref, 0) + 1
                seen_in_this_signal.add(ref)
    return fused_scores, corroborators, signals_by_ref


def _pick_framework(signals: list[SignalOutput]) -> Optional[str]:
    """Priority: explicit_refs > framework_hint > retrieval majority."""
    by_name = {s.name: s for s in signals if s.fired}
    for name in ("explicit_refs", "framework_hint", "retrieval"):
        sig = by_name.get(name)
        if sig and sig.framework:
            return sig.framework
    return None


def _pick_question_type(signals: list[SignalOutput]) -> Optional[str]:
    """Priority: curated_lexicon > session_context."""
    by_name = {s.name: s for s in signals if s.fired}
    for name in ("curated_lexicon", "session_context"):
        sig = by_name.get(name)
        if sig and sig.question_type:
            return sig.question_type
    return None


def _detect_ambiguity(
    ordered_refs:  list[tuple[str, float]],
    signals:       list[SignalOutput],
    cfg:           ConsensusConfig,
) -> Optional[Clarification]:
    """Detect topic ambiguity across ref families.

    If the top-K within tie_band span multiple graph_tightness
    families, emit a topic_ambiguity clarification.

    Skip when the query has a decisive intent that doesn't need
    a ref anchor (definition/gap_analysis/cross_framework can be
    answered without pinning to one specific control). Retrieval
    scores for those query types often mix unrelated refs — that's
    NOT a topic ambiguity, it's the LLM having plenty to talk about.
    """
    if not ordered_refs or len(ordered_refs) < 2:
        return None

    # Skip ambiguity check for intent types that don't need a specific
    # ref anchor. Signal C (curated_lexicon) is the authority on this.
    _refless_intent = {"definition", "gap_analysis", "cross_framework",
                       "free_assessment"}
    for sig in signals:
        if (sig.fired and sig.name == "curated_lexicon"
                and sig.question_type in _refless_intent):
            return None

    top_score = ordered_refs[0][1]
    # Only refs within tie_band of the top
    tied = [r for r, s in ordered_refs if s >= top_score - cfg.refs_tie_band]
    if len(tied) < 2:
        return None

    # Check families — reuse graph_tightness's family_of
    from rag.guards.framework_scope_guard import _family_of
    tied_families = {_family_of(r) for r in tied if _family_of(r)}
    if len(tied_families) < 2:
        return None   # tied refs share a family, not ambiguous

    # Look up titles from retrieval metadata if available
    titles_by_ref = _titles_from_retrieval(signals)
    frameworks_by_ref = _frameworks_from_retrieval(signals)

    options: list[ClarificationOption] = []
    for ref in tied:
        options.append(ClarificationOption(
            ref       = ref,
            title     = titles_by_ref.get(ref, ref),
            framework = frameworks_by_ref.get(ref, ""),
        ))

    # Build a human question
    if len(options) == 2:
        a, b = options[0], options[1]
        question = (
            f"Do you mean {a.ref} ({a.title}) or {b.ref} ({b.title})?"
        )
    else:
        listed = ", ".join(o.ref for o in options[:3])
        question = f"Do you mean one of: {listed}?"

    return Clarification(
        kind     = "topic_ambiguity",
        question = question,
        options  = options,
    )


def _titles_from_retrieval(signals: list[SignalOutput]) -> dict[str, str]:
    """Extract ref->title map from retrieval metadata if present."""
    for s in signals:
        if s.name == "retrieval" and s.fired:
            return s.metadata.get("titles_by_ref", {}) or {}
    return {}


def _frameworks_from_retrieval(signals: list[SignalOutput]) -> dict[str, str]:
    """Extract ref->framework map from retrieval metadata if present."""
    for s in signals:
        if s.name == "retrieval" and s.fired:
            return s.metadata.get("frameworks_by_ref", {}) or {}
    return {}


def _framework_disagreement_note(signals: list[SignalOutput]) -> Optional[str]:
    """Return a diagnostic string if signals disagree on framework."""
    frameworks = set()
    for s in signals:
        if s.fired and s.framework:
            frameworks.add(s.framework)
    if len(frameworks) > 1:
        return f"framework disagreement: {sorted(frameworks)}"
    return None


def aggregate(
    signals: list[SignalOutput],
    cfg:     Optional[ConsensusConfig] = None,
) -> ConsensusResult:
    """Fuse signal outputs into a ConsensusResult.

    Args:
        signals: outputs from run_consensus (A-G in any order).
        cfg:     ConsensusConfig; None → default_config().

    Returns:
        ConsensusResult with verdict, refs, question_type, framework,
        corroborators, and (for verdict=ambiguous) a clarification.
    """
    if cfg is None:
        from rag.consensus.config import default_config
        cfg = default_config()

    if not signals or not any(s.fired for s in signals):
        return ConsensusResult(
            verdict              = "insufficient",
            signals              = signals,
            llm_fallback_needed  = cfg.llm_fallback_enabled,
            disagreement_notes   = ["no signal fired"],
        )

    fused_scores, corroborators, signals_by_ref = _fuse_ref_scores(signals)

    if not fused_scores:
        # Signals fired but none contributed refs (e.g. only framework_hint)
        return ConsensusResult(
            verdict              = "insufficient",
            signals              = signals,
            question_type        = _pick_question_type(signals),
            framework            = _pick_framework(signals),
            llm_fallback_needed  = cfg.llm_fallback_enabled,
            disagreement_notes   = ["no signal contributed refs"],
        )

    ordered = sorted(fused_scores.items(), key=lambda kv: kv[1], reverse=True)
    top_ref, top_score = ordered[0]
    top_corroborators  = corroborators.get(top_ref, 0)

    disagreement_notes: list[str] = []
    fw_note = _framework_disagreement_note(signals)
    if fw_note:
        disagreement_notes.append(fw_note)

    picked_framework    = _pick_framework(signals)
    picked_question_type = _pick_question_type(signals)

    # Ambiguity check
    clarification = _detect_ambiguity(ordered, signals, cfg)
    if clarification is not None:
        return ConsensusResult(
            verdict              = "ambiguous",
            refs                 = [r for r, _ in ordered],
            question_type        = picked_question_type,
            framework            = picked_framework,
            top_ref_confidence   = round(top_score, 3),
            corroborators        = top_corroborators,
            signals              = signals,
            disagreement_notes   = disagreement_notes,
            clarification        = clarification,
            llm_fallback_needed  = False,
        )

    # Insufficient — top score too low
    if top_score < cfg.refs_min_floor:
        disagreement_notes.append(
            f"top score {top_score:.3f} below refs_min_floor {cfg.refs_min_floor}"
        )
        return ConsensusResult(
            verdict              = "insufficient",
            refs                 = [r for r, _ in ordered],
            question_type        = picked_question_type,
            framework            = picked_framework,
            top_ref_confidence   = round(top_score, 3),
            corroborators        = top_corroborators,
            signals              = signals,
            disagreement_notes   = disagreement_notes,
            llm_fallback_needed  = cfg.llm_fallback_enabled,
        )

    # Confident (proper) — high score + corroborators
    if (top_score >= cfg.refs_confident_floor
            and top_corroborators >= cfg.min_corroborators):
        return ConsensusResult(
            verdict              = "confident",
            refs                 = [r for r, _ in ordered],
            question_type        = picked_question_type,
            framework            = picked_framework,
            top_ref_confidence   = round(top_score, 3),
            corroborators        = top_corroborators,
            signals              = signals,
            disagreement_notes   = disagreement_notes,
            llm_fallback_needed  = False,
        )

    # Borderline confident — above min_floor but not the full "confident"
    # bar. Ships an answer path rather than clarify, but marks the low
    # confidence for the caller to log.
    return ConsensusResult(
        verdict              = "confident",
        refs                 = [r for r, _ in ordered],
        question_type        = picked_question_type,
        framework            = picked_framework,
        top_ref_confidence   = round(top_score, 3),
        corroborators        = top_corroborators,
        signals              = signals,
        disagreement_notes   = disagreement_notes + [
            f"borderline: score={top_score:.3f} corrob={top_corroborators} "
            f"(confident_floor={cfg.refs_confident_floor}, "
            f"min_corroborators={cfg.min_corroborators})"
        ],
        llm_fallback_needed  = False,
    )
