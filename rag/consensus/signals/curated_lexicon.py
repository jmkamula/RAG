"""
Signal C — curated lexicon (CLEAR_INTENT_PHRASES + DOCUMENT_TOPIC_MAP).

Reuses the two curated vocabularies already living in classifier.py:

  CLEAR_INTENT_PHRASES   ~50 regex patterns, each mapped to a
                          question_type + optional seed refs.
                          Covers common phrasings like
                          "what does OFI mean" (definition),
                          "what documents do we need" (document_inventory),
                          "prepare for the ISO audit" (implementation).

  DOCUMENT_TOPIC_MAP     ~30 topic->ref entries: "access rights" -> A.5.18,
                          "cryptography" -> A.8.24, "DPIA" -> Art.35,
                          "records of processing" -> Art.30.

Role in consensus:
  - Emits question_type when a CLEAR_INTENT match hits.
  - Emits refs at curated_lexicon_weight (0.30). Refs come from
    (a) CLEAR_INTENT seed_refs list, (b) DOCUMENT_TOPIC_MAP hits.
  - The framework is inferred from the top ref's shape (delegates
    to explicit_refs._framework_of_ref).
  - fired=False when neither vocabulary matches.
"""
from __future__ import annotations

from typing import Optional

from rag.consensus.types import SignalOutput, ConsensusConfig
from rag.consensus.signals.explicit_refs import _framework_of_ref


def curated_lexicon(query: str, cfg: ConsensusConfig) -> SignalOutput:
    """Match against CLEAR_INTENT_PHRASES + DOCUMENT_TOPIC_MAP.

    On match: return SignalOutput with question_type (if CLEAR_INTENT
    hit) and refs (seed_refs + topic_map hits).
    """
    if not query:
        return SignalOutput(name="curated_lexicon", fired=False)

    # Lazy import — avoid pulling in the classifier's full LLM path
    # for a lightweight regex/dict lookup.
    from rag.classifier import CLEAR_INTENT_PHRASES, DOCUMENT_TOPIC_MAP

    matched_qt:      Optional[str] = None
    matched_pattern: Optional[str] = None
    matched_refs:    list[str]     = []

    # First CLEAR_INTENT match wins (the classifier uses the same
    # first-match semantics — we mirror it for consistency)
    for pattern, qt_str, seed_refs in CLEAR_INTENT_PHRASES:
        m = pattern.search(query)
        if m:
            matched_qt      = qt_str
            matched_pattern = pattern.pattern
            matched_refs.extend(seed_refs)
            break

    # Then check DOCUMENT_TOPIC_MAP — additive, all matching topics
    q_lower = query.lower()
    matched_topics: list[str] = []
    for topic, ref in DOCUMENT_TOPIC_MAP.items():
        # DOCUMENT_TOPIC_MAP keys are phrases; substring match is what
        # _detect_document_dimensions does today.
        if topic in q_lower:
            matched_topics.append(topic)
            if ref not in matched_refs:
                matched_refs.append(ref)

    if matched_qt is None and not matched_refs:
        return SignalOutput(name="curated_lexicon", fired=False)

    # Emit refs with curated_lexicon weight
    weight = cfg.curated_lexicon_weight
    refs_out = [(r, weight) for r in matched_refs]

    # Infer framework from ref shape if we have refs
    framework: Optional[str] = None
    if matched_refs:
        # Use the first ref's framework — CLEAR_INTENT seed_refs are
        # curated per-taxonomy and usually all one framework
        framework = _framework_of_ref(matched_refs[0])

    return SignalOutput(
        name          = "curated_lexicon",
        refs          = refs_out,
        question_type = matched_qt,
        framework     = framework,
        metadata      = {
            "matched_pattern": matched_pattern,
            "matched_topics":  matched_topics,
            "seed_refs_from_clear_intent": bool(matched_qt and matched_refs),
        },
        fired         = True,
    )
