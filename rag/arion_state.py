"""
ArionComply — LangGraph State Definition

Single typed state object replacing:
  - SessionContext
  - ClarificationState  
  - OrchestratorResponse
  - pending_intake in chat.py

Checkpoint backends:
  Dev (Mac):   SqliteSaver  → /workspace/arioncomply.db
  Prod:        PostgresSaver → DATABASE_URL env var
"""
from __future__ import annotations
from typing import Annotated
import operator
from typing_extensions import TypedDict

from rag.classifier import QuestionType, QueryIntent, TenantProfile


class ArionState(TypedDict):
    """
    Full conversation state — persisted by LangGraph checkpointer.
    
    Fields marked Annotated[list, operator.add] accumulate across turns.
    All other fields are replaced each turn.
    """

    # ── Conversation-level (static for session lifetime) ───────────────────
    tenant_id:    str                    # e.g. "arion"
    standards:    list[str]              # ["ISO27001:2022", "GDPR:2016/679"]
    role:         str                    # "controller" | "processor" | "both"

    # ── Turn tracking ──────────────────────────────────────────────────────
    turn_count:   int                    # increments each completed turn
    clarif_count: int                    # resets after successful answer
    taxonomy_options_map: dict           # letter → taxonomy_id for clarif responses
    original_query: str                  # original query before clarif response

    # ── Per-turn inputs ────────────────────────────────────────────────────
    query:        str                    # current user query

    # ── Classification output ──────────────────────────────────────────────
    intent_type:  str                    # "gap_analysis" | "implementation" | ...
    focus_refs:   list[str]              # THIS query's cited refs only (no stale)
    needs_posture: bool
    confidence:   float
    needs_clarif: bool
    clarif_question: str

    # ── Retrieval output ───────────────────────────────────────────────────
    context_text: str
    node_count:   int
    neo4j_ms:     int

    # ── Answer output ──────────────────────────────────────────────────────
    answer_text:  str
    verified:     bool
    was_corrected: bool
    cited_refs:   list[str]
    posture_findings: dict
    answer_source: str                   # "postgres" | "llm" | ""

    # ── Error handling ─────────────────────────────────────────────────────
    error:        str
    resolver_trace: object          # ResolverTrace from last resolve() call


def make_initial_state(tenant: TenantProfile, query: str = "") -> ArionState:
    """Create the initial state for a new conversation thread."""
    return ArionState(
        tenant_id       = tenant.name,
        standards       = tenant.applicable_standards,
        role            = tenant.role[0] if tenant.role else "controller",
        turn_count      = 0,
        clarif_count    = 0,
        taxonomy_options_map = None,
        original_query  = "",
        query           = query,
        intent_type     = "",
        focus_refs      = [],
        needs_posture   = False,
        confidence      = 0.0,
        needs_clarif    = False,
        clarif_question = "",
        context_text    = "",
        node_count      = 0,
        neo4j_ms        = 0,
        answer_text     = "",
        verified        = False,
        was_corrected   = False,
        cited_refs      = [],
        posture_findings= {},
        answer_source   = "",
        error           = "",
        resolver_trace  = None,
    )
