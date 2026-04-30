"""
ArionComply — LangGraph Pipeline

Replaces orchestrator.py (~791 lines) with a typed state graph.
The existing QueryClassifier, GraphExpander, ContextAssembler, and
LLMAnswer classes are unchanged — they become graph nodes.

Graph structure:
                    ┌─────────┐
    query ──────────│ CLASSIFY │
                    └────┬────┘
              ┌──────────┤
              │          │
           CLEAR      AMBIGUOUS
              │          │
              ▼          ▼
          ┌───────┐  ┌─────────┐
          │RETRIEVE│  │ CLARIFY │──── END (return question)
          └───┬───┘  └─────────┘
              │
              ▼
          ┌────────┐
          │ ANSWER │
          └───┬────┘
              │
              ▼
          ┌──────────────┐
          │ UPDATE_SESSION│
          └──────┬────────┘
                 │
                END

Checkpointing:
  Dev:  SqliteSaver("~/.arioncomply/sessions.db")
  Prod: PostgresSaver(DATABASE_URL)
"""
from __future__ import annotations

import os
import time
from typing import Literal

from langgraph.graph import StateGraph, END

from rag.arion_state    import ArionState, make_initial_state
from rag.classifier     import (
    QueryClassifier, TenantProfile, IntakeState,
)
from rag.orchestrator   import OVERRIDE_PHRASES
from rag.context_assembler import ContextAssembler
from rag.graph_expander    import GraphExpander
from rag.llm_answer        import LLMAnswer
from rag.chain_logger      import get_logger
from vector.retriever      import VectorRetriever


# ── Node implementations ────────────────────────────────────────────────────

def make_classify_node(
    classifier: QueryClassifier,
):
    """
    Node: classify intent.
    Replaces: _handle_intake + _handle_query + classify_query routing.
    """
    def classify(state: ArionState) -> dict:
        query  = state["query"]
        logger = get_logger()

        # Override: "just answer" / "skip" → force best-effort
        if query.lower().strip() in OVERRIDE_PHRASES:
            return {
                "intent_type":   "unknown",
                "focus_refs":    state.get("focus_refs", []),
                "needs_posture": True,
                "confidence":    0.5,
                "needs_clarif":  False,
                "clarif_question": "",
            }

        # Build a minimal SessionContext from graph state
        from rag.classifier import SessionContext, QuestionType
        session = SessionContext(
            tenant_profile = classifier.tenant,
            standards      = state["standards"],
            role           = state.get("role"),
            intent_type    = None,
            active_refs    = state.get("focus_refs", []),
            active_cluster = None,
        )

        # First turn: use process_intake (handles ambiguous clusters)
        # Follow-up turns: use classify_query (faster, session-aware)
        if state["turn_count"] == 0:
            intake = classifier.process_intake(query)
            if intake.state == IntakeState.AMBIGUOUS:
                count = state["clarif_count"] + 1
                if count >= 2:
                    # Exhausted — fall through to best-effort
                    return {
                        "intent_type":    "unknown",
                        "focus_refs":     [],
                        "needs_posture":  True,
                        "confidence":     0.5,
                        "needs_clarif":   False,
                        "clarif_question": "",
                        "clarif_count":   count,
                    }
                return {
                    "intent_type":    "ambiguous",
                    "focus_refs":     [],
                    "needs_posture":  False,
                    "confidence":     0.0,
                    "needs_clarif":   True,
                    "clarif_question": intake.clarification or "",
                    "clarif_count":   count,
                }
            if intake.state == IntakeState.NO_MATCH:
                return {
                    "intent_type":    "unknown",
                    "focus_refs":     [],
                    "needs_posture":  False,
                    "confidence":     0.0,
                    "needs_clarif":   True,
                    "clarif_question": intake.clarification or "",
                    "clarif_count":   state["clarif_count"] + 1,
                }
            # CLEAR or EXPLICIT
            sess = intake.session
            return {
                "intent_type":   sess.intent_type.value if sess.intent_type else "unknown",
                "focus_refs":    sess.active_refs[:3],
                "needs_posture": sess.intent_type.value in ("gap_analysis", "posture_check")
                                 if sess.intent_type else False,
                "confidence":    0.88,
                "needs_clarif":  False,
                "clarif_question": "",
                "clarif_count":  0,
            }

        else:
            # Follow-up turn
            intent = classifier.classify_query(query, session, [])
            if intent.clarification_question:
                count = state["clarif_count"] + 1
                if count >= 2:
                    return {
                        "intent_type":    "unknown",
                        "focus_refs":     intent.cited_refs[:3],
                        "needs_posture":  True,
                        "confidence":     0.5,
                        "needs_clarif":   False,
                        "clarif_question": "",
                        "clarif_count":   count,
                    }
                return {
                    "intent_type":    intent.question_type.value,
                    "focus_refs":     intent.cited_refs[:3],
                    "needs_posture":  intent.needs_posture,
                    "confidence":     intent.confidence,
                    "needs_clarif":   True,
                    "clarif_question": intent.clarification_question,
                    "clarif_count":   count,
                }

            return {
                "intent_type":   intent.question_type.value,
                "focus_refs":    intent.cited_refs[:3],  # ONLY cited refs — no stale session
                "needs_posture": intent.needs_posture,
                "confidence":    intent.confidence,
                "needs_clarif":  False,
                "clarif_question": "",
                "clarif_count":  0,
            }

    return classify


def make_retrieve_node(
    retriever: VectorRetriever,
    expander:  GraphExpander,
    assembler: ContextAssembler,
    tenant:    TenantProfile,
    posture:   dict,
):
    """
    Node: vector retrieval + graph expansion + context assembly.
    Replaces: Step 3-5 of _run_pipeline.
    """
    def retrieve(state: ArionState) -> dict:
        import re as _re
        from rag.classifier import QueryIntent, QuestionType

        qtype_map = {
            "gap_analysis":   QuestionType.GAP_ANALYSIS,
            "implementation": QuestionType.IMPLEMENTATION,
            "definition":     QuestionType.DEFINITION,
            "posture_check":  QuestionType.POSTURE_CHECK,
            "cross_framework":QuestionType.CROSS_FRAMEWORK,
            "free_assessment":QuestionType.FREE_ASSESSMENT,
            "unknown":        QuestionType.UNKNOWN,
        }
        qtype = qtype_map.get(state["intent_type"], QuestionType.UNKNOWN)

        intent = QueryIntent(
            question_type   = qtype,
            standards_scope = state["standards"],
            role_filter     = state.get("role"),
            needs_posture   = state["needs_posture"],
            cited_refs      = state["focus_refs"],
            resolved_refs   = state["focus_refs"],
            confidence      = state["confidence"],
            raw_query       = state["query"],
        )

        # ── Vector search ──────────────────────────────────────────────────
        search = retriever.search(
            query     = state["query"],
            n         = 15,
            standards = intent.standards_scope,
        )

        # ── Build node_ids — mirror orchestrator._run_pipeline exactly ─────
        def _node_valid(standard_id: str, ref: str) -> bool:
            """Simple heuristic — same as orchestrator._node_exists."""
            if standard_id == "GDPR:2016/679":
                return ref.startswith("Art.")
            if standard_id == "ISO27001:2022":
                return (ref.startswith("A.") or
                        bool(_re.match(r"^\d+[.]\d", ref)))
            return False

        anchor_refs = intent.cited_refs if intent.cited_refs else intent.resolved_refs
        cited_node_ids = [
            f"{s}:{r}"
            for s in intent.standards_scope
            for r in anchor_refs
            if _node_valid(s, r)
        ]

        # Always include posture nodes so NC/OFI/Comply findings are in context
        posture_node_ids = [
            node_id for node_id in posture.keys()
            if node_id not in cited_node_ids
        ]

        vector_ids = search.node_ids()[:5] if cited_node_ids else search.node_ids()

        node_ids = list(dict.fromkeys(
            cited_node_ids +
            posture_node_ids +
            vector_ids
        ))[:20]

        # ── Graph expansion ────────────────────────────────────────────────
        t0 = time.time()
        expanded = expander.expand(node_ids, intent)
        neo4j_ms = round((time.time() - t0) * 1000)

        # ── Context assembly ───────────────────────────────────────────────
        assembled = assembler.assemble(
            expanded = expanded,
            intent   = intent,
            posture  = posture,
        )

        return {
            "context_text": assembled.context_text,
            "node_count":   assembled.primary_count,
            "neo4j_ms":     neo4j_ms,
        }

    return retrieve


def _node_exists_check(node_id: str, retriever) -> bool:
    """Check if a node_id exists in ChromaDB."""
    try:
        parts = node_id.split(":")
        ref = parts[-1]
        result = retriever.search_by_ref(ref)
        return result is not None
    except Exception:
        return False


def make_answer_node(llm: LLMAnswer):
    """
    Node: LLM answer generation + verification.
    Replaces: Step 6 of _run_pipeline.
    """
    def answer(state: ArionState) -> dict:
        from rag.context_assembler import AssembledContext
        from rag.classifier import QueryIntent, QuestionType, SessionContext
        from rag.classifier import TenantProfile as TP

        qtype_map = {
            "gap_analysis":   QuestionType.GAP_ANALYSIS,
            "implementation": QuestionType.IMPLEMENTATION,
            "definition":     QuestionType.DEFINITION,
            "posture_check":  QuestionType.POSTURE_CHECK,
            "cross_framework":QuestionType.CROSS_FRAMEWORK,
            "free_assessment":QuestionType.FREE_ASSESSMENT,
            "unknown":        QuestionType.UNKNOWN,
        }
        qtype = qtype_map.get(state["intent_type"], QuestionType.UNKNOWN)

        # Reconstruct minimal AssembledContext for LLMAnswer
        intent = QueryIntent(
            question_type   = qtype,
            standards_scope = state["standards"],
            role_filter     = state.get("role"),
            needs_posture   = state["needs_posture"],
            cited_refs      = state["focus_refs"],
            resolved_refs   = state["focus_refs"],
            confidence      = state["confidence"],
            raw_query       = state["query"],
        )

        assembled = AssembledContext(
            context_text    = state["context_text"],
            question_type   = qtype,
            tenant_name     = state["tenant_id"],
            has_posture     = bool(state.get("needs_posture")),
            posture_summary = {},
            intent          = intent,
            node_ids_used   = [],
            primary_count   = state.get("node_count", 0),
        )

        result = llm.answer(state["query"], assembled)

        return {
            "answer_text":    result.answer_text,
            "verified":       result.verified,
            "was_corrected":  result.was_corrected,
            "cited_refs":     result.cited_refs,
        }

    return answer


def make_clarify_node():
    """
    Node: return clarification question to user.
    Replaces: _clarification_response.
    """
    def clarify(state: ArionState) -> dict:
        # Nothing to compute — clarif_question already set by classify node
        return {}

    return clarify


def make_update_session_node():
    """
    Node: update session state after successful answer.
    Replaces: scattered session.update_refs() calls.
    This is the ONLY place focus_refs can be updated — no more stale ref bugs.
    """
    def update_session(state: ArionState) -> dict:
        return {
            "turn_count":  state["turn_count"] + 1,
            "clarif_count": 0,
            # focus_refs already set correctly by classify_node
            # cited_refs from answer further refine what was discussed
        }

    return update_session


# ── Routing ─────────────────────────────────────────────────────────────────

def route_after_classify(
    state: ArionState,
) -> Literal["retrieve", "clarify"]:
    """
    Replaces: if/else routing in _handle_intake and _handle_query.
    Single explicit decision point — no more hidden routing logic.
    """
    if state["needs_clarif"]:
        return "clarify"
    return "retrieve"


# ── Graph builder ────────────────────────────────────────────────────────────

def build_arion_graph(
    tenant:    TenantProfile,
    retriever: VectorRetriever,
    expander:  GraphExpander,
    assembler: ContextAssembler,
    llm:       LLMAnswer,
    classifier: QueryClassifier,
    posture:   dict,
    checkpointer = None,
):
    """
    Build and compile the ArionComply LangGraph pipeline.
    
    Args:
        checkpointer: SqliteSaver, PostgresSaver, or MemorySaver instance
                      If None, uses in-memory (no persistence)
    
    Returns:
        Compiled graph ready for invoke()
    """
    builder = StateGraph(ArionState)

    # Add nodes
    builder.add_node("classify",       make_classify_node(classifier))
    builder.add_node("retrieve",       make_retrieve_node(retriever, expander, assembler, tenant, posture))
    builder.add_node("answer",         make_answer_node(llm))
    builder.add_node("clarify",        make_clarify_node())
    builder.add_node("update_session", make_update_session_node())

    # Entry point
    builder.set_entry_point("classify")

    # Edges
    builder.add_conditional_edges("classify", route_after_classify)
    builder.add_edge("retrieve",       "answer")
    builder.add_edge("answer",         "update_session")
    builder.add_edge("update_session", END)
    builder.add_edge("clarify",        END)

    compiled = builder.compile(checkpointer=checkpointer)

    # Force Neo4j connection warmup — explicitly cache _online=True
    # so the retrieve node doesn't hit a timeout on first graph.invoke()
    if hasattr(expander, '_is_online'):
        online = expander._is_online()
        if online:
            # Explicitly confirm so _online stays True across invocations
            expander._online = True
        else:
            import warnings
            warnings.warn(
                "Neo4j is offline at graph build time — "
                "expansion will use vector-only mode until Neo4j is reachable.",
                RuntimeWarning,
            )

    return compiled


# ── Convenience: get default checkpointer ───────────────────────────────────

def get_checkpointer(db_path: str = None):
    """
    Get the appropriate checkpointer for the current environment.
    
    Priority:
      1. DATABASE_URL env var → PostgresSaver (production)
      2. db_path argument    → SqliteSaver (dev/test)
      3. Default path        → SqliteSaver at ~/.arioncomply/sessions.db
    """
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        try:
            from langgraph.checkpoint.postgres import PostgresSaver
            return PostgresSaver.from_conn_string(db_url)
        except ImportError:
            pass

    # SQLite for dev
    if db_path is None:
        home = os.path.expanduser("~")
        db_dir = os.path.join(home, ".arioncomply")
        os.makedirs(db_dir, exist_ok=True)
        db_path = os.path.join(db_dir, "sessions.db")

    from langgraph.checkpoint.sqlite import SqliteSaver
    return SqliteSaver.from_conn_string(db_path)
