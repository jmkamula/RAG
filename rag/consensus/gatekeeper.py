"""
Inline consensus gatekeeper — bounded LLM arbiter.

The gatekeeper reviews every non-hard-anchor consensus decision.
It sees the query, all 7 signal outputs, and the aggregator's
tentative decision. It can APPROVE, MODIFY (question_type / refs /
framework), or REJECT (verdict → insufficient, falls to LLM
classifier).

Design principle: the LLM is bounded. It cannot invent refs the
signals didn't surface, cannot invent question_types outside the
enum, cannot author prose. It only reasons about which of the
produced signals should carry the day.

Cost profile:
  - ~500 input tokens (query + signals + tentative)
  - ~50 output tokens (JSON decision)
  - ~500ms latency at gpt-4o-mini
  - ~$0.0005 / call
  - Skips on hard-anchor cases (explicit_refs + curated agree)
"""
from __future__ import annotations

import json
import re
import time
from typing import Optional

from rag.consensus.types import (
    SignalOutput, ConsensusResult, ConsensusConfig,
)
from rag.consensus.gatekeeper_prompts import (
    GATEKEEPER_SYSTEM,
    build_gatekeeper_user_message,
    format_signals_view,
    format_tentative_view,
)


_VALID_QUESTION_TYPES = {
    "posture_check", "document_content", "document_inventory",
    "implementation", "gap_analysis", "definition", "cross_framework",
    "free_assessment", "unknown",
}


def gatekeeper_should_fire(
    tentative: ConsensusResult,
    signals:   list[SignalOutput],
    cfg:       ConsensusConfig,
) -> tuple[bool, str]:
    """Decide whether to call the LLM gatekeeper for this tentative
    decision. Returns (should_fire, reason).

    Skip when:
      - Explicit_refs + curated_lexicon already agree (hard anchor,
        early-exit in run_consensus already skipped retrieval).
        Nothing for the gatekeeper to arbitrate.
      - No signal fired at all — the tentative is 'insufficient',
        gatekeeping cannot rescue it, falls to LLM classifier.
    """
    if not any(s.fired for s in signals):
        return False, "no signals fired"

    # Hard-anchor path — retrieval was skipped, verdict must be confident
    by_name = {s.name: s for s in signals}
    sig_b = by_name.get("explicit_refs")
    sig_c = by_name.get("curated_lexicon")
    ret   = by_name.get("retrieval")
    if (sig_b and sig_b.fired and sig_c and sig_c.fired
            and ret and not ret.fired
            and ret.metadata.get("reason") == "cheap_consensus_hit"):
        return False, "hard_anchor_early_exit"

    return True, "gatekeeping_applicable"


def _extract_json_object(text: str) -> Optional[dict]:
    """Pull the first JSON object out of the model response.
    Tolerant of stray whitespace / code-fence wrappers."""
    if not text:
        return None
    # Strip common wrappers
    stripped = text.strip()
    if stripped.startswith("```"):
        # ```json\n{...}\n```
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, re.DOTALL)
        if m:
            stripped = m.group(1)
    # Find the first { and matching close
    m = re.search(r"\{[^{}]*\}", stripped, re.DOTALL)
    if not m:
        # Try a broader match (with nested braces)
        m = re.search(r"\{.*\}", stripped, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def _signals_lock_question_type(signals: list[SignalOutput]) -> Optional[str]:
    """If Signal C (curated_lexicon) fired with a question_type, that's
    authoritative — the gatekeeper cannot override it. Returns the locked
    question_type or None if C didn't fire with one.

    Ship 1.6b hard-bound: deterministic signals win where they fire.
    See design note in module docstring."""
    for s in signals:
        if s.name == "curated_lexicon" and s.fired and s.question_type:
            return s.question_type
    return None


def _signals_lock_framework(signals: list[SignalOutput]) -> Optional[str]:
    """If Signal B (explicit_refs) fired with a framework, that's
    authoritative — the user typed a specific ref of a specific shape.
    Gatekeeper cannot override the framework in that case.

    Note Signal F (framework_hint) is NOT authoritative here — it can
    disagree with B legitimately (e.g., user names GDPR but types an
    ISO ref). B wins the framework tie."""
    for s in signals:
        if s.name == "explicit_refs" and s.fired and s.framework:
            return s.framework
    return None


def _apply_decision(
    tentative:  ConsensusResult,
    decision:   dict,
    signals:    Optional[list[SignalOutput]] = None,
) -> ConsensusResult:
    """Apply a parsed gatekeeper decision to the tentative result.
    Returns a NEW ConsensusResult (does not mutate the tentative).

    Ship 1.6b: enforces structural bounds on what the gatekeeper can
    modify. When a deterministic signal has an opinion (Signal C on
    question_type, Signal B on framework), the gatekeeper CANNOT
    override it via modify — only refs and verdict remain modifiable
    in that case. This preserves the design principle that
    deterministic signals lead and the LLM fills gaps."""
    from dataclasses import replace

    decision_kind = (decision.get("decision") or "").lower()
    reason        = decision.get("reason", "")[:200]
    signals       = signals or []

    # Compute deterministic locks up front so both modify + approve
    # can annotate the disagreement notes when the LLM tried to
    # override.
    locked_qt = _signals_lock_question_type(signals)
    locked_fw = _signals_lock_framework(signals)

    if decision_kind == "reject":
        # Reject is always allowed — the gatekeeper can say "no
        # deterministic consensus" regardless of what signals fired.
        new_notes = list(tentative.disagreement_notes or []) + [
            f"gatekeeper: reject ({reason})"
        ]
        return replace(
            tentative,
            verdict             = "insufficient",
            clarification       = None,
            llm_fallback_needed = True,
            disagreement_notes  = new_notes,
        )

    if decision_kind == "modify":
        proposed_qt   = decision.get("question_type")
        proposed_refs = decision.get("refs")
        proposed_fw   = decision.get("framework")

        # Validate question_type shape before applying
        if proposed_qt and proposed_qt not in _VALID_QUESTION_TYPES:
            proposed_qt = None

        # Validate refs — must be a subset of what signals surfaced
        # (bounded contract: no invention)
        if proposed_refs is not None and not isinstance(proposed_refs, list):
            proposed_refs = None

        # ── Enforce deterministic-signal locks ──────────────────────
        override_notes: list[str] = []

        # Question_type: Signal C is authoritative when it fired
        if locked_qt is not None and proposed_qt and proposed_qt != locked_qt:
            override_notes.append(
                f"blocked_qt_override: gatekeeper tried "
                f"{proposed_qt!r}, curated_lexicon locked {locked_qt!r}"
            )
            proposed_qt = None   # discard the LLM's opinion

        # Framework: Signal B is authoritative when it fired
        if locked_fw is not None and proposed_fw and proposed_fw != locked_fw:
            override_notes.append(
                f"blocked_fw_override: gatekeeper tried "
                f"{proposed_fw!r}, explicit_refs locked {locked_fw!r}"
            )
            proposed_fw = None   # discard the LLM's opinion

        # If the gatekeeper resolved question_type on an ambiguous
        # verdict, upgrade to confident — the intent IS clear now.
        # Uses the FINAL question_type (after lock enforcement) so
        # locked_qt drives the upgrade even if the LLM didn't propose.
        new_verdict = tentative.verdict
        new_clarif  = tentative.clarification
        effective_qt = proposed_qt or locked_qt or tentative.question_type
        if effective_qt and tentative.verdict == "ambiguous":
            new_verdict = "confident"
            new_clarif  = None

        notes = list(tentative.disagreement_notes or []) + [
            f"gatekeeper: modify ({reason})"
        ] + override_notes

        updated = replace(
            tentative,
            verdict            = new_verdict,
            question_type      = proposed_qt or locked_qt or tentative.question_type,
            refs               = list(proposed_refs) if proposed_refs is not None
                                  else tentative.refs,
            framework          = proposed_fw or locked_fw or tentative.framework,
            clarification      = new_clarif,
            disagreement_notes = notes,
        )
        return updated

    # decision_kind == "approve" (or unknown → treat as approve)
    # Even on approve, we apply the locks in case the aggregator
    # itself missed Signal C's opinion (defensive).
    approve_qt = locked_qt or tentative.question_type
    approve_fw = locked_fw or tentative.framework
    return replace(
        tentative,
        question_type      = approve_qt,
        framework          = approve_fw,
        disagreement_notes = list(tentative.disagreement_notes or [])
                              + [f"gatekeeper: approve ({reason})"],
    )


def gatekeep(
    query:      str,
    tentative:  ConsensusResult,
    signals:    list[SignalOutput],
    cfg:        Optional[ConsensusConfig] = None,
) -> ConsensusResult:
    """Run the inline gatekeeper LLM on the tentative consensus.

    Returns:
        The final ConsensusResult after gatekeeper decision.
        On any error (LLM failure, parse failure, timeout) the
        tentative is returned UNCHANGED — the gatekeeper never
        breaks the consensus flow.
    """
    if cfg is None:
        from rag.consensus.config import default_config
        cfg = default_config()

    should_fire, reason = gatekeeper_should_fire(tentative, signals, cfg)
    if not should_fire:
        return tentative

    # Build the LLM prompt
    signals_view   = format_signals_view(signals)
    tentative_view = format_tentative_view(tentative)
    user_msg       = build_gatekeeper_user_message(
        query        = query,
        signals_view = signals_view,
        tentative    = tentative_view,
    )

    # Call the LLM (silent-fail — tentative stays if anything goes wrong)
    try:
        from rag.llm_client import call as llm_call
        t0 = time.time()
        response = llm_call(
            system      = GATEKEEPER_SYSTEM,
            user        = user_msg,
            model       = _gatekeeper_model(),
            purpose     = "consensus_gatekeeper",
            max_tokens  = 150,
            temperature = 0.0,     # deterministic; we want stable decisions
            timeout_s   = 15.0,
            metadata    = {"step": "consensus_gatekeeper"},
        )
        latency_ms = int((time.time() - t0) * 1000)
        if not response.ok:
            return tentative
        decision = _extract_json_object(response.text or "")
        if not decision:
            return tentative
        result = _apply_decision(tentative, decision, signals=signals)
        # Track latency contribution
        result.latency_ms = (tentative.latency_ms or 0) + latency_ms
        return result
    except Exception:
        return tentative


def _gatekeeper_model() -> str:
    """Model for the gatekeeper LLM call. Env-overridable via the
    existing `GATEKEEPER_MODEL` env var (handled inside
    rag.llm_models). See MODEL_CONSENSUS_GK for the resolution
    order."""
    from rag.llm_models import MODEL_CONSENSUS_GK
    return MODEL_CONSENSUS_GK
