"""
Dispatcher — routes a query intent to the appropriate payload builder.

Called by the retrieve node after Ship 1's consensus produces an
intent + refs. The dispatcher picks the taxonomy-specific builder
by question_type and hands off. All builders return a subclass of
AnswerPayloadBase.

During Ship 2 migration, taxonomies without dedicated builders fall
through to `freeform.build`. As each builder lands (Ship 2.1..2.5),
its entry is added to _BUILDERS.
"""
from __future__ import annotations

import logging
from typing import Callable

from rag.answer.types    import AnswerPayloadBase, FreeformPayload
from rag.answer.builders import freeform


logger = logging.getLogger("rag.answer.dispatcher")


# Registry of question_type → builder. Populated as Ship 2 rolls out
# per-taxonomy builders (Ship 2.1 = standard_knowledge / definition,
# Ship 2.2 = posture_status, etc.). Anything not in the registry
# falls through to freeform.build.
_BUILDERS: dict[str, Callable] = {
    # Populated by Ship 2.1..2.5 as each builder is implemented.
}


def _normalize_question_type(intent) -> str:
    """Get a lowercase string key from intent.question_type. Handles
    both string values and QuestionType enum values."""
    if intent is None:
        return "unknown"
    qt = getattr(intent, "question_type", None)
    if qt is None:
        return "unknown"
    return (getattr(qt, "value", str(qt)) or "unknown").lower()


def dispatch_builder(
    intent,
    tenant_context,
    resolver,
    neo_driver=None,
    chroma_retriever=None,
) -> AnswerPayloadBase:
    """Route to the taxonomy-specific builder by intent.question_type.

    Args:
        intent:            QueryIntent from the classify node
        tenant_context:    TenantContext (posture + scope + document_alerts)
        resolver:          The Resolver instance (for _resolve_* strategies)
        neo_driver:        Optional Neo4j driver for graph queries
        chroma_retriever:  Optional VectorRetriever for enrichment lookups

    Returns:
        A subclass of AnswerPayloadBase — never raises. On any error,
        the freeform fallback fires and captures the reason.
    """
    qt_key = _normalize_question_type(intent)
    builder = _BUILDERS.get(qt_key, freeform.build)

    try:
        return builder(
            intent          = intent,
            tenant_context  = tenant_context,
            resolver        = resolver,
            neo_driver      = neo_driver,
            chroma_retriever= chroma_retriever,
        )
    except Exception as e:
        logger.warning(
            "dispatch_builder: %s builder raised %s: %s — falling back to freeform",
            qt_key, type(e).__name__, str(e)[:200],
        )
        fallback = freeform.build(
            intent          = intent,
            tenant_context  = tenant_context,
            resolver        = resolver,
            neo_driver      = neo_driver,
            chroma_retriever= chroma_retriever,
        )
        fallback.reason_fallback = f"builder crash: {type(e).__name__}"
        return fallback


def register_builder(question_type: str, builder: Callable) -> None:
    """Test helper — register a builder for a question_type. Used by
    Ship 2.1..2.5 commits to activate each taxonomy's builder."""
    _BUILDERS[question_type.lower()] = builder


def registered_taxonomies() -> list[str]:
    """Return list of question_types with dedicated builders."""
    return sorted(_BUILDERS.keys())
