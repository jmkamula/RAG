"""
Retrieval-first consensus layer for chat intent + topic detection.

Overview
--------
The chat pipeline used to route intent primarily via LLM classification
(with regex short-circuits as fast paths). That drifted from the
original design where ChromaDB — enriched with natural-language
business_description on every compliance node — was intended to be the
anchor. Case #16 was the concrete symptom: "what documents do we need
to address the access rights NC?" routed to DOCUMENT_STATUS short-
circuit (primary=0 nodes), skipping the very corpus we built to
answer it.

This module puts retrieval back at the front, corroborated by 6 other
cheap deterministic signals. Only when signals don't reach consensus
does the LLM classifier fire (intra-consensus fallback for rare
cases). The full kill-switch (USE_LEGACY_CLASSIFIER env) was
retired in Ship 2'.o (2026-07-16) — consensus always runs.

Signals (see the taxonomies + rules in docs/ship_1_design):

    A ChromaDB retrieval           the anchor
    B explicit_refs (regex)        hard-anchor when hit
    C curated_lexicon              CLEAR_INTENT + DOCUMENT_TOPIC_MAP
    D posture_boost                tenant NC/OFI re-weight
    E graph_tightness              family clustering across top-K
    F framework_hint               "GDPR" / "ISO 27001" in query
    G session_context              deictic follow-up support

Public entry point: `run_consensus(query, tenant_ctx, session_ctx,
retriever) -> ConsensusResult`.

The ConsensusResult carries a verdict of "confident", "ambiguous" or
"insufficient". The classify graph node reads it and:
  - confident  → builds QueryIntent directly (no LLM classifier)
  - ambiguous  → routes to clarify with a deterministic prompt
  - insufficient → falls through to the legacy LLM classifier
"""
from rag.consensus.types import (
    SignalOutput, ConsensusResult, ConsensusConfig,
    Clarification, ClarificationOption,
)
from rag.consensus.query_consensus import run_consensus, intent_dict_from_consensus
from rag.consensus.aggregator      import aggregate
from rag.consensus.config          import gatekeeper_enabled

__all__ = [
    "SignalOutput", "ConsensusResult", "ConsensusConfig",
    "Clarification", "ClarificationOption",
    "run_consensus", "intent_dict_from_consensus",
    "aggregate", "gatekeeper_enabled",
]
