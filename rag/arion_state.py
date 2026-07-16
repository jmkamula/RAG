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
    # tenant_id is the CANONICAL UUID from tenants.id — used for Postgres
    # RLS (app.tenant_id GUC) and every ::uuid cast in downstream writers.
    # tenant_display_name is the human-readable label for prompts + UI.
    # DO NOT put the display name in tenant_id — Ship 2'.i (2026-07-16)
    # separated these after chat_casefile_log writes were silently failing
    # because state["tenant_id"] used to be tenant.name. See id_types.py.
    tenant_id:            str            # UUID (validated via TenantUUID)
    tenant_display_name:  str            # "Arion Networks"
    standards:            list[str]      # ["ISO27001:2022", "GDPR:2016/679"]
    role:                 str            # "controller" | "processor" | "both"

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
    # Tier-4 structured templates block (2026-07-02). Populated when
    # the query is action-oriented and cited refs include NC/OFI
    # controls. Payload shape documented in
    # rag/templates/answer_footer.py:build_templates_block.
    # Chat UI renders per-leaf; API consumers get JSON.
    templates_block: dict | None

    # ── Error handling ─────────────────────────────────────────────────────
    error:        str
    resolver_trace: object          # ResolverTrace from last resolve() call

    # ── Conversational context (carries across turns) ──────────────────────
    # Last short-circuit-matched entity, e.g. {"type": "document",
    # "title": "Business Continuity Policy", "ref": "DOC007",
    # "doc_type": "policy"}. Populated when an upload-status short-circuit
    # matched a specific doc; read on the next turn so the LLM has prior-
    # turn context for deictic follow-ups ("what about X?", "this", "that
    # doc"). Empty dict when no prior match. See [[conversational-context-
    # routing-followup]].
    last_entity:  dict


def make_initial_state(tenant: TenantProfile, query: str = "") -> ArionState:
    """Create the initial state for a new conversation thread.

    Ship 2'.i: tenant_id is now the canonical UUID (validated at
    TenantProfile construction). The display name lives on
    tenant_display_name — separate field, separate contract.
    """
    from rag.id_types import TenantUUID
    # tenant.tenant_id must be UUID-shaped by contract; validate loudly.
    # TenantUUID(...) raises ValueError if the fixture / caller handed
    # us a slug or display name, which is exactly the failure mode we
    # want to see early instead of silently miswriting logs downstream.
    tid = TenantUUID(tenant.tenant_id)
    return ArionState(
        tenant_id            = tid,
        tenant_display_name  = tenant.name or "",
        standards            = tenant.applicable_standards,
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
        templates_block = None,
        error           = "",
        resolver_trace  = None,
        last_entity     = {},
    )
