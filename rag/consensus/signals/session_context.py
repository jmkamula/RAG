"""
Signal G — session context (deictic follow-up support).

Reads SessionContext.active_refs — the last few refs the user
discussed in this session. When the current query has no explicit
refs (e.g. "what about the fifth one?" or "so we're OFI on it?"),
active_refs provide the missing anchor.

Role in consensus:
  - Small boost (session_boost_weight=0.10) to any active_ref.
  - Also emits the session's question_type carryover — if the last
    turn was POSTURE_STATUS on A.5.18 and the current query is
    "and what about that policy content?", the question_type should
    carry over as DOCUMENT_CONTENT with A.5.18 anchored.
  - fired=False when session has no active_refs.
"""
from __future__ import annotations

from typing import Optional, Any

from rag.consensus.types import SignalOutput, ConsensusConfig


def session_context(session, cfg: ConsensusConfig) -> SignalOutput:
    """Emit refs + optional question_type from SessionContext.

    Args:
        session: Optional SessionContext (from rag.classifier). May be
                 None on first turn. Any object with `active_refs`
                 attribute is accepted (duck-typing keeps this signal
                 testable without importing the full classifier).
        cfg:     ConsensusConfig for weight lookup.
    """
    if session is None:
        return SignalOutput(name="session_context", fired=False)

    active_refs: list[str] = list(getattr(session, "active_refs", []) or [])
    if not active_refs:
        return SignalOutput(name="session_context", fired=False)

    weight = cfg.session_boost_weight
    refs_out = [(r, weight) for r in active_refs]

    # Carry over question_type from prior turn — SessionContext stores
    # this as `intent_type` (a QuestionType enum) per the classifier
    # dataclass.
    prior_intent = getattr(session, "intent_type", None)
    qt: Optional[str] = None
    if prior_intent is not None:
        qt = getattr(prior_intent, "value", str(prior_intent))
        # Only carry over if it's a real question_type (not UNKNOWN)
        if qt.lower() == "unknown":
            qt = None

    # Framework — inferred from active_refs (first one's shape)
    framework: Optional[str] = None
    if active_refs:
        # Import lazily to avoid circular imports
        from rag.consensus.signals.explicit_refs import _framework_of_ref
        framework = _framework_of_ref(active_refs[0])

    return SignalOutput(
        name          = "session_context",
        refs          = refs_out,
        question_type = qt,
        framework     = framework,
        metadata      = {
            "carried_question_type": qt,
            "active_refs_count":     len(active_refs),
            "top_active_ref":        active_refs[0] if active_refs else None,
        },
        fired         = True,
    )
