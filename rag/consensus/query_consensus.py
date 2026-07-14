"""
Public entry point for the retrieval-first consensus layer.

Dispatches signals in cheap-first order, runs the aggregator,
returns a ConsensusResult ready for the classify graph node to
route on.

Dispatch order (cheap first, expensive last):
  B explicit_refs        <1ms
  C curated_lexicon      <1ms
  F framework_hint       <1ms
  G session_context      0ms
  A retrieval           150-300ms  ← the expensive one
  E graph_tightness      computed from A's refs, no I/O
  D posture_boost        computed from A + tenant posture, no I/O

Early-exit: if B (explicit_refs) fires with a hard-anchor AND C
(curated_lexicon) confirms the topic (same family or same ref),
skip A entirely. Saves ~200ms on the ~30% of queries with
explicit refs like "is A.5.18 compliant?".
"""
from __future__ import annotations

import time
from typing import Optional

from rag.consensus.types import ConsensusResult, ConsensusConfig, SignalOutput
from rag.consensus.aggregator import aggregate
from rag.consensus.signals.explicit_refs   import explicit_refs
from rag.consensus.signals.curated_lexicon import curated_lexicon
from rag.consensus.signals.framework_hint  import framework_hint
from rag.consensus.signals.session_context import session_context
from rag.consensus.signals.retrieval       import retrieve
from rag.consensus.signals.graph_tightness import graph_tightness
from rag.consensus.signals.posture_boost   import posture_boost


def _cheap_signals_hard_consensus(
    sig_b: SignalOutput,
    sig_c: SignalOutput,
) -> bool:
    """True when B (explicit_refs) fired AND its top ref is confirmed
    by C (curated_lexicon) — same ref or same family. That's enough
    signal to skip the expensive retrieval step.
    """
    if not sig_b.fired or not sig_b.refs:
        return False
    if not sig_c.fired or not sig_c.refs:
        return False
    from rag.guards.framework_scope_guard import _family_of
    b_top = sig_b.refs[0][0]
    b_family = _family_of(b_top)
    for ref, _ in sig_c.refs:
        if ref == b_top:
            return True
        if _family_of(ref) == b_family:
            return True
    return False


def _union_refs(signals: list[SignalOutput]) -> list[str]:
    """Collect all unique refs across signals, preserving first-seen order."""
    seen: set[str] = set()
    out:  list[str] = []
    for sig in signals:
        if not sig.fired:
            continue
        for ref, _ in sig.refs:
            if ref in seen:
                continue
            seen.add(ref)
            out.append(ref)
    return out


def _null_signal(name: str, **metadata) -> SignalOutput:
    """Placeholder for signals that were deliberately skipped."""
    return SignalOutput(name=name, fired=False, metadata=metadata)


def run_consensus(
    query:           str,
    tenant_context,               # TenantContext (or duck-typed)
    session_context_arg = None,   # SessionContext (or None)
    retriever        = None,      # VectorRetriever
    cfg:             Optional[ConsensusConfig] = None,
) -> ConsensusResult:
    """Retrieval-first, multi-signal consensus for query intent + refs.

    Args:
        query:               Raw user query.
        tenant_context:      Anything with .posture dict + .scope object
                              (or None-safe attribute access).
        session_context_arg: SessionContext for deictic follow-ups (or None).
        retriever:           VectorRetriever instance (or None → Signal A skipped).
        cfg:                 ConsensusConfig; None → default_config().

    Returns:
        ConsensusResult with verdict + refs + question_type + framework
        + full signal audit trail in .signals for logging.
    """
    if cfg is None:
        from rag.consensus.config import default_config
        cfg = default_config()

    t0 = time.time()

    # ── Cheap deterministic pass (B, C, F, G) ─────────────────────────
    sig_b = explicit_refs(query, cfg)
    sig_c = curated_lexicon(query, cfg)
    sig_f = framework_hint(query, cfg)
    sig_g = session_context(session_context_arg, cfg)
    signals: list[SignalOutput] = [sig_b, sig_c, sig_f, sig_g]

    # ── Signal A (retrieval) — skip if cheap consensus already hit ───
    if _cheap_signals_hard_consensus(sig_b, sig_c):
        signals.append(_null_signal(
            "retrieval",
            skipped=True,
            reason="cheap_consensus_hit",
        ))
    else:
        # Resolve tenant standards for scope
        standards = None
        scope = getattr(tenant_context, "scope", None) if tenant_context else None
        if scope is not None:
            standards = getattr(scope, "queryable_standards", None) or None
        sig_a = retrieve(query, retriever, standards=standards, cfg=cfg)
        signals.append(sig_a)

    # ── Modifiers (E, D) — compute over the union of candidate refs ──
    candidates = _union_refs(signals)
    sig_e = graph_tightness(candidates, cfg)
    tenant_posture = getattr(tenant_context, "posture", None) if tenant_context else None
    sig_d = posture_boost(candidates, tenant_posture, cfg)
    signals.extend([sig_e, sig_d])

    # ── Aggregate ─────────────────────────────────────────────────────
    result = aggregate(signals, cfg)
    result.latency_ms = int((time.time() - t0) * 1000)
    return result
