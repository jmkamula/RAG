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
import re as _re_graph
import re

# ── Upload status query helpers ───────────────────────────────────────────────

_UPLOAD_STATUS_PATTERNS = [
    re.compile(r'\bhave\s+we\s+uploaded\b', re.IGNORECASE),
    re.compile(r'\b(?:is|are)\s+(?:our|the)\s+[\w\s]{2,40}(?:policy|procedure|plan|playbook)\s+(?:uploaded|in\s+the\s+system|on\s+the\s+platform)\b', re.IGNORECASE),
    re.compile(r'\bwhich\s+documents?\s+(?:have\s+(?:not|yet)\s+been|are\s+(?:not|still)?)\s+uploaded\b', re.IGNORECASE),
    re.compile(r'\bshow\s+(?:me\s+)?(?:missing|unuploaded)\s+documents?\b', re.IGNORECASE),
]


def _is_upload_status_query(query: str) -> bool:
    return any(p.search(query) for p in _UPLOAD_STATUS_PATTERNS)


def _answer_upload_status(query: str, alerts: list) -> str | None:
    """
    Answer an upload status question directly from document_alerts data.
    Returns plain-text answer or None if no relevant documents found.
    This is deterministic — no LLM involved.
    """
    if not alerts:
        return None

    query_lower = query.lower()

    # Match alerts to query by document title words
    relevant = []
    for alert in alerts:
        title = (alert.get("document_title") or "").lower()
        title_words = [w for w in title.split() if len(w) > 3]
        if any(w in query_lower for w in title_words):
            relevant.append(alert)

    # "show missing documents" or "which documents not uploaded"
    if not relevant and any(
        p in query_lower
        for p in ["missing", "not uploaded", "unuploaded", "which documents"]
    ):
        relevant = [a for a in alerts
                   if a.get("alert_type") in ("CRITICAL", "WARNING")]

    if not relevant:
        return None  # Fall through to LLM

    lines = []
    critical = [a for a in relevant if a.get("alert_type") == "CRITICAL"]
    warning  = [a for a in relevant if a.get("alert_type") == "WARNING"]
    info     = [a for a in relevant if a.get("alert_type") == "INFO"]

    if critical:
        lines.append("The following documents are registered but NOT yet uploaded "
                     "and are linked to open NC findings:")
        for a in critical:
            lines.append(
                f"  • {a['document_title']} ({a['external_ref']}) "
                f"— linked to controls: {a.get('linked_controls', 'unknown')}"
            )
    if warning:
        if lines:
            lines.append("")
        lines.append("Also registered but not uploaded — linked to OFI findings:")
        for a in warning:
            lines.append(
                f"  • {a['document_title']} ({a['external_ref']}) "
                f"— linked to: {a.get('linked_controls', '')}"
            )
    if info and not critical and not warning:
        lines.append("Registered but not yet uploaded:")
        for a in info[:5]:
            lines.append(f"  • {a['document_title']} ({a['external_ref']})")

    if lines:
        lines.append("")
        lines.append(
            "Upload these files to the platform so the system can verify "
            "their content against control checklists automatically."
        )

    return "\n".join(lines) if lines else None
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
                "intent_type":   "gap_analysis",   # best-effort default
                "focus_refs":    state.get("focus_refs", []),
                "needs_posture": True,
                "confidence":    0.5,
                "needs_clarif":  False,
                "clarif_question": "",
                "clarif_count":  0,
            }

        # Clarification response: user replied to a taxonomy question (a/b/c)
        # Route through process_clarification instead of re-classifying as new query
        import re as _re
        _is_clarif_response = (
            state.get("turn_count", 0) > 0            # not first turn
            and state.get("needs_clarif") is True     # clarif question was shown
            and state.get("clarif_count", 0) > 0      # we did ask a clarif question
            and bool(state.get("clarif_question"))    # there is a pending question
            and _re.match(r"^[a-c][.)\s]*$", query.strip().lower())
        )
        if _is_clarif_response:
            # Map letter directly to intent type from taxonomy_options_map
            # stored in state (set when we returned the clarif question)
            tmap = state.get("taxonomy_options_map") or {}
            letter = query.strip().lower()[0]
            taxonomy_id = tmap.get(letter)
            from rag.taxonomy import CLASSIFIER_TO_TAXONOMY
            TAXONOMY_TO_CLASSIFIER = {v: k for k, v in CLASSIFIER_TO_TAXONOMY.items()}
            if taxonomy_id:
                intent_type = TAXONOMY_TO_CLASSIFIER.get(taxonomy_id, "gap_analysis")
                return {
                    "intent_type":    intent_type,
                    "focus_refs":     state.get("focus_refs", []),
                    "needs_posture":  intent_type in ("gap_analysis", "posture_check"),
                    "confidence":     0.95,
                    "needs_clarif":   False,
                    "clarif_question": "",
                    "clarif_count":   0,
                    # Keep original query for retrieval
                    "query":          state.get("original_query", state["query"]),
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
                    "intent_type":       "ambiguous",
                    "focus_refs":        [],
                    "needs_posture":     False,
                    "confidence":        0.0,
                    "needs_clarif":      True,
                    "clarif_question":   intake.clarification or "",
                    "clarif_count":      count,
                    "turn_count":        state["turn_count"] + 1,  # advance so next turn is follow-up
                    "taxonomy_options_map": getattr(intake, "taxonomy_options_map", {}) or {},
                    "original_query":    query,
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
            # Follow-up turn — build history from graph state for context
            _history = []
            if state.get("original_query"):
                _history.append({"role": "user", "content": state["original_query"]})
            if state.get("answer_text"):
                _history.append({"role": "assistant", "content": state["answer_text"][:400]})
            _history.append({"role": "user", "content": query})
            intent = classifier.classify_query(query, session, _history)
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


from rag.scope_na import is_scope_na_query as _is_scope_na_query

def _answer_scope_na(query: str, posture: dict) -> str:
    """
    Answer scope N/A queries directly — no LLM, no graph traversal.
    Returns a direct statement that these controls are out of scope.
    """
    query_lower = query.lower()

    is_physical = re.search(
        r'physical\s+security|physical\s+access|perimeter|premises', query_lower)
    is_dev = re.search(
        r'software\s+dev|secure\s+cod|development\s+security', query_lower)

    if is_physical:
        # Confirm from posture that A.7.x are all N/A
        na_controls = [
            v.get("control_ref", k.split(":")[-1])
            for k, v in posture.items()
            if (v.get("control_ref","") or k.split(":")[-1]).startswith(("7.","A.7."))
            and v.get("finding") == "N/A"
        ]
        controls_note = (
            f" ({', '.join(sorted(na_controls)[:5])}{'...' if len(na_controls) > 5 else ''})"
            if na_controls else ""
        )
        return (
            f"Physical security controls (A.7.x) are marked not applicable "
            f"for Arion Networks{controls_note}. "
            f"Your ISMS scope excludes physical premises controls — "
            f"Arion operates as a cloud-based organisation without dedicated physical facilities "
            f"requiring ISO 27001 physical security controls. "
            f"No physical security gaps apply to your organisation."
        )
    elif is_dev:
        na_controls = [
            v.get("control_ref", k.split(":")[-1])
            for k, v in posture.items()
            if (v.get("control_ref","") or k.split(":")[-1]).startswith(("A.8.2","8.2"))
            and v.get("finding") == "N/A"
        ]
        controls_note = (
            f" ({', '.join(sorted(na_controls)[:5])}{'...' if len(na_controls) > 5 else ''})"
            if na_controls else " (A.8.25–A.8.31)"
        )
        return (
            f"Software development security controls{controls_note} are marked "
            f"not applicable for Arion Networks. "
            f"Your ISMS scope excludes software development — "
            f"Arion Networks does not develop software products, so secure development "
            f"lifecycle controls do not apply to your organisation. "
            f"No software development security gaps exist in your scope."
        )

    return (
        "The controls related to this area are marked not applicable "
        "for Arion Networks and are excluded from your ISMS scope."
    )


def make_retrieve_node(
    retriever: VectorRetriever,
    expander:  GraphExpander,
    assembler: ContextAssembler,   # kept for API compat, used by fallback
    llm:       LLMAnswer,
    tenant:    TenantProfile,
    posture:   dict,
):
    """
    Node: vector retrieval + graph expansion + rank_and_answer (combined).
    Replaces: Steps 3-6 of _run_pipeline in one node.
    Uses rank_and_answer for zero-position-bias answering.
    """
    def retrieve(state: ArionState) -> dict:
        import re as _re
        from rag.classifier import QueryIntent, QuestionType

        qtype_map = {
            "gap_analysis":       QuestionType.GAP_ANALYSIS,
            "implementation":     QuestionType.IMPLEMENTATION,
            "definition":         QuestionType.DEFINITION,
            "posture_check":      QuestionType.POSTURE_CHECK,
            "cross_framework":    QuestionType.CROSS_FRAMEWORK,
            "free_assessment":    QuestionType.FREE_ASSESSMENT,
            "document_inventory": QuestionType.DOCUMENT_INVENTORY,
            "document_content":   QuestionType.DOCUMENT_CONTENT,
            "unknown":            QuestionType.UNKNOWN,
        }
        qtype = qtype_map.get(state["intent_type"], QuestionType.UNKNOWN)

        from rag.classifier import QueryDimensions
        from enrichment.events.event_nodes import detect_events

        # Reconstruct dimensions from state
        # needs_documentation detected from query phrases
        from rag.classifier import _detect_document_dimensions, _detect_document_question_type
        needs_doc, doc_topic = _detect_document_dimensions(state["query"])
        doc_qtype = _detect_document_question_type(state["query"])
        if doc_qtype:
            qtype = doc_qtype

        dimensions = QueryDimensions(
            needs_obligation    = True,
            needs_posture       = state["needs_posture"],
            needs_documentation = needs_doc,
        )

        # Detect events from query
        try:
            detected_events = detect_events(state["query"])
        except Exception:
            detected_events = []

        intent = QueryIntent(
            question_type      = qtype,
            standards_scope    = state["standards"],
            role_filter        = state.get("role"),
            needs_posture      = state["needs_posture"],
            cited_refs         = state["focus_refs"],
            resolved_refs      = state["focus_refs"],
            confidence         = state["confidence"],
            raw_query          = state["query"],
            dimensions         = dimensions,
            detected_events    = detected_events,
            document_topic_ref = doc_topic,
        )

        # ── Scope N/A short-circuit ───────────────────────────────────────
        # Physical security (A.7.x) and dev controls (A.8.25-31) are N/A.
        # Don't surface unrelated findings for these scope-excluded queries.
        if _is_scope_na_query(state["query"]):
            na_answer = _answer_scope_na(state["query"], posture)
            return {
                **state,
                "answer_text":   na_answer,
                "answer":        na_answer,
                "cited_refs":    [],
                "question_type": "gap_analysis",
                "confidence":    1.0,
                "answer_source": "postgres",
            }

        # ── Resolver: dispatch to per-taxonomy data sources ──────────────
        # Replaces ~190 lines of inline retrieval assembly.
        # Each taxonomy type gets the right sources (DB / graph / vector / both).
        from rag.resolver import Resolver, ResolveRequest
        from rag.taxonomy  import get_taxonomy_type

        _resolver = Resolver(
            retriever = retriever,
            expander  = expander,
            posture   = posture,
        )
        _req = ResolveRequest(
            query            = state["query"],
            classifier_type  = state["intent_type"],
            tenant_context   = tenant,
            topic_ref        = intent.document_topic_ref,
            standards        = intent.standards_scope,
            history          = [],
            # Observability: thread_id from LangGraph state = conversation request_id
            # tenant_id denormalised for fast trace access without hitting tenant_context
            request_id       = state.get("thread_id") or state.get("session_id") or "",
            tenant_id        = str(getattr(tenant, "tenant_id", "") or ""),
        )
        _resolved = _resolver.resolve(_req)

        # Short-circuit: Resolver found a direct Postgres answer
        if _resolved.has_short_circuit:
            return {
                **state,
                "answer_text":   _resolved.short_circuit_answer,
                "answer":        _resolved.short_circuit_answer,
                "cited_refs":    [],
                "question_type": state["intent_type"],
                "confidence":    1.0,
                "answer_source": "postgres",
            }

        # Store resolver trace in state for ANALYTICS display
        # (before we check for short-circuit so it's always available)
        _trace = getattr(_resolved, "trace", None)

        # Build expanded from resolved context
        # graph_nodes is always GraphResult after Phase 1 rewrite
        _gr              = _resolved.graph_nodes
        expanded_nodes   = _gr.all_nodes if hasattr(_gr, "all_nodes") else list(_gr)
        doc_contexts     = _resolved.doc_contexts   # property on ResolvedContext
        incident_contexts = []
        neo4j_ms         = _resolved.neo4j_ms

        # ── Rank + Answer in one Mistral call ──────────────────────────────
        # Pass all non-informational nodes as a numbered list.
        # Mistral selects the most relevant nodes and answers from them.
        # No position bias — every node gets equal attention.
        all_nodes = [
            n for n in expanded_nodes
            if not getattr(n, 'is_informational', False)
        ]

        standards_str = " + ".join(
            s.split(":")[0].replace("ISO27001", "ISO 27001")
            for s in state["standards"]
        )

        # ── Postgres short-circuit for upload status questions ─────────────
        # "have we uploaded X?" has a definitive answer in client_documents.
        # Don't involve the LLM for factual DB lookups — answer directly.
        if (intent.question_type.value == "document_inventory"
                and _is_upload_status_query(state["query"])):
            # Get alerts from tenant profile (set at startup from Postgres)
            _alerts = getattr(tenant, "document_alerts", []) or []
            pg_answer = _answer_upload_status(
                query   = state["query"],
                alerts  = _alerts,
            )
            if pg_answer:
                return {
                    **state,
                    "answer_text":   pg_answer,
                    "answer":        pg_answer,
                    "cited_refs":    [],
                    "question_type": "document_inventory",
                    "confidence":    1.0,   # deterministic DB answer
                    "answer_source": "postgres",
                }



        result = llm.rank_and_answer(
            query            = state["query"],
            nodes            = all_nodes,
            posture          = posture,
            intent           = intent,
            tenant_name      = state["tenant_id"],
            standards        = standards_str,
            doc_contexts     = doc_contexts     if doc_contexts     else None,
            incident_contexts= incident_contexts if incident_contexts else None,
        )


        # ── Write structured trace to DB (best-effort, never blocks answer) ─
        if _trace:
            try:
                _write_request_trace(
                    posture_db = posture_db if "posture_db" in dir() else None,
                    trace      = _trace,
                    tenant     = tenant,
                    topic_ref  = getattr(intent, "document_topic_ref", None),
                )
            except Exception as _te:
                logger.debug(f"[trace] write skipped: {_te}")

        return {
            "answer_text":    result.answer_text,
            "verified":       result.verified,
            "was_corrected":  result.was_corrected,
            "cited_refs":     result.cited_refs,
            "posture_findings": result.posture_findings,
            "node_count":     len(all_nodes),
            "neo4j_ms":       neo4j_ms,
            "resolver_trace": _trace,
        }

    return retrieve


def _write_request_trace(posture_db, trace, tenant, topic_ref) -> None:
    """
    Write one row to request_trace_log.
    Best-effort — called in a try/except so failures never block answers.
    posture_db: the Postgres connection/engine used for posture queries.
    """
    if not posture_db or not trace:
        return

    tenant_id = str(getattr(tenant, "tenant_id", "") or "")
    if not tenant_id:
        return

    sql = """
        INSERT INTO request_trace_log (
            request_id, tenant_id,
            query_text, classifier_type, taxonomy_type, handler_name,
            strategy, topic_ref,
            policy_posture, policy_vector, policy_graph,
            policy_doc_inv, policy_short_circuit,
            node_ids_built, nodes_primary, nodes_secondary,
            vector_hits, doc_contexts,
            posture_ids_used, vector_top_scores,
            posture_total, posture_nc, posture_ofi,
            posture_confirmed, posture_draft,
            short_circuit, answer_source,
            neo4j_ms, vector_ms, postgres_ms, total_ms,
            error_type, error_hint,
            traced_at
        ) VALUES (
            %(request_id)s, %(tenant_id)s::UUID,
            %(query_text)s, %(classifier_type)s, %(taxonomy_type)s, %(handler_name)s,
            %(strategy)s, %(topic_ref)s,
            %(policy_posture)s, %(policy_vector)s, %(policy_graph)s,
            %(policy_doc_inv)s, %(policy_short_circuit)s,
            %(node_ids_built)s, %(nodes_primary)s, %(nodes_secondary)s,
            %(vector_hits)s, %(doc_contexts)s,
            %(posture_ids_used)s, %(vector_top_scores)s::JSONB,
            %(posture_total)s, %(posture_nc)s, %(posture_ofi)s,
            %(posture_confirmed)s, %(posture_draft)s,
            %(short_circuit)s, %(answer_source)s,
            %(neo4j_ms)s, %(vector_ms)s, %(postgres_ms)s, %(total_ms)s,
            %(error_type)s, %(error_hint)s,
            NOW()
        )
        ON CONFLICT DO NOTHING
    """
    import json
    params = {
        "request_id":         trace.request_id or "",
        "tenant_id":          tenant_id,
        "query_text":         trace.query[:500],
        "classifier_type":    trace.classifier_type,
        "taxonomy_type":      trace.taxonomy_type,
        "handler_name":       trace.handler_name,
        "strategy":           trace.strategy,
        "topic_ref":          topic_ref,
        "policy_posture":     trace.policy_posture,
        "policy_vector":      trace.policy_vector,
        "policy_graph":       trace.policy_graph,
        "policy_doc_inv":     trace.policy_doc_inv,
        "policy_short_circuit": trace.policy_short_circuit,
        "node_ids_built":     trace.node_ids_built,
        "nodes_primary":      trace.nodes_primary,
        "nodes_secondary":    trace.nodes_secondary,
        "vector_hits":        trace.vector_results,
        "doc_contexts":       trace.doc_contexts,
        "posture_ids_used":   trace.posture_ids_used or [],
        "vector_top_scores":  json.dumps(trace.vector_top_scores or []),
        "posture_total":      trace.posture_total,
        "posture_nc":         trace.posture_nc,
        "posture_ofi":        trace.posture_ofi,
        "posture_confirmed":  trace.posture_confirmed,
        "posture_draft":      trace.posture_draft,
        "short_circuit":      trace.short_circuit,
        "answer_source":      trace.answer_source,
        "neo4j_ms":           trace.neo4j_ms,
        "vector_ms":          trace.vector_ms,
        "postgres_ms":        trace.postgres_ms,
        "total_ms":           trace.total_ms,
        "error_type":         type(trace.error).__name__ if trace.error else None,
        "error_hint":         trace.error_hint,
    }

    # Support psycopg2 connection, SQLAlchemy engine, or connection pool
    if hasattr(posture_db, "execute"):
        posture_db.execute(sql, params)
    elif hasattr(posture_db, "connect"):
        with posture_db.connect() as conn:
            conn.execute(sql, params)
            if hasattr(conn, "commit"):
                conn.commit()


def _node_exists_check(node_id: str, retriever) -> bool:
    """Check if a node_id exists in ChromaDB."""
    try:
        parts = node_id.split(":")
        ref = parts[-1]
        result = retriever.search_by_ref(ref)
        return result is not None
    except Exception:
        return False


# make_answer_node removed — rank_and_answer is now in make_retrieve_node

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
    builder.add_node("retrieve",       make_retrieve_node(retriever, expander, assembler, llm, tenant, posture))
    builder.add_node("clarify",        make_clarify_node())
    builder.add_node("update_session", make_update_session_node())

    # Entry point
    builder.set_entry_point("classify")

    # Edges — retrieve now includes rank_and_answer (no separate answer node)
    builder.add_conditional_edges("classify", route_after_classify)
    builder.add_edge("retrieve",       "update_session")
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
    Sync checkpointer for graph.invoke() — uses PostgresSaver (psycopg v3).
    For async streaming use get_async_checkpointer().
    """
    import logging
    _log = logging.getLogger(__name__)

    sessions_url = (
        os.getenv("SESSIONS_DATABASE_URL") or
        os.getenv("DATABASE_URL", "").replace(
            "arioncomply_compliance", "arioncomply_sessions"
        )
    )

    if sessions_url and "arioncomply" in sessions_url:
        try:
            import psycopg
            from langgraph.checkpoint.postgres import PostgresSaver
            conn = psycopg.connect(sessions_url)
            saver = PostgresSaver(conn)
            saver.setup()
            _log.info(f"Checkpointer: PostgresSaver ({sessions_url.split('@')[-1]})")
            return saver
        except Exception as _e:
            _log.warning(f"PostgresSaver failed ({_e}) — falling back to InMemorySaver")

    from langgraph.checkpoint.memory import InMemorySaver
    _log.info("Checkpointer: InMemorySaver")
    return InMemorySaver()


async def get_async_checkpointer():
    """
    Async checkpointer for graph.astream_events() — uses AsyncPostgresSaver (psycopg v3 async).
    Falls back to InMemorySaver if Postgres unavailable.
    """
    import logging
    _log = logging.getLogger(__name__)

    sessions_url = (
        os.getenv("SESSIONS_DATABASE_URL") or
        os.getenv("DATABASE_URL", "").replace(
            "arioncomply_compliance", "arioncomply_sessions"
        )
    )

    if sessions_url and "arioncomply" in sessions_url:
        try:
            import psycopg
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
            conn = await psycopg.AsyncConnection.connect(sessions_url)
            saver = AsyncPostgresSaver(conn)
            await saver.setup()
            _log.info(f"AsyncCheckpointer: AsyncPostgresSaver ({sessions_url.split('@')[-1]})")
            return saver
        except Exception as _e:
            _log.warning(f"AsyncPostgresSaver failed ({_e}) — falling back to InMemorySaver")

    from langgraph.checkpoint.memory import InMemorySaver
    _log.info("AsyncCheckpointer: InMemorySaver")
    return InMemorySaver()

def _is_scope_na_query(query: str) -> bool:
    """True for physical security or software dev queries — N/A for Arion."""
    import re as _re
    return (
        bool(_re.search(r'\bphysical\s+security\s+(?:gaps?|findings?|controls?|posture)\b', query, _re.IGNORECASE)) or
        bool(_re.search(r'\bsoftware\s+(?:development|dev)\s+security\s+(?:gaps?|findings?|controls?)\b', query, _re.IGNORECASE))
    )

def _answer_scope_na(query: str, posture: dict) -> str:
    """
    Answer scope N/A queries directly — no LLM, no graph traversal.
    Returns a direct statement that these controls are out of scope.
    """
    query_lower = query.lower()

    is_physical = re.search(
        r'physical\s+security|physical\s+access|perimeter|premises', query_lower)
    is_dev = re.search(
        r'software\s+dev|secure\s+cod|development\s+security', query_lower)

    if is_physical:
        # Confirm from posture that A.7.x are all N/A
        na_controls = [
            v.get("control_ref", k.split(":")[-1])
            for k, v in posture.items()
            if (v.get("control_ref","") or k.split(":")[-1]).startswith(("7.","A.7."))
            and v.get("finding") == "N/A"
        ]
        controls_note = (
            f" ({', '.join(sorted(na_controls)[:5])}{'...' if len(na_controls) > 5 else ''})"
            if na_controls else ""
        )
        return (
            f"Physical security controls (A.7.x) are marked not applicable "
            f"for Arion Networks{controls_note}. "
            f"Your ISMS scope excludes physical premises controls — "
            f"Arion operates as a cloud-based organisation without dedicated physical facilities "
            f"requiring ISO 27001 physical security controls. "
            f"No physical security gaps apply to your organisation."
        )
    elif is_dev:
        na_controls = [
            v.get("control_ref", k.split(":")[-1])
            for k, v in posture.items()
            if (v.get("control_ref","") or k.split(":")[-1]).startswith(("A.8.2","8.2"))
            and v.get("finding") == "N/A"
        ]
        controls_note = (
            f" ({', '.join(sorted(na_controls)[:5])}{'...' if len(na_controls) > 5 else ''})"
            if na_controls else " (A.8.25–A.8.31)"
        )
        return (
            f"Software development security controls{controls_note} are marked "
            f"not applicable for Arion Networks. "
            f"Your ISMS scope excludes software development — "
            f"Arion Networks does not develop software products, so secure development "
            f"lifecycle controls do not apply to your organisation. "
            f"No software development security gaps exist in your scope."
        )

    return (
        "The controls related to this area are marked not applicable "
        "for Arion Networks and are excluded from your ISMS scope."
    )


def make_retrieve_node(
    retriever: VectorRetriever,
    expander:  GraphExpander,
    assembler: ContextAssembler,   # kept for API compat, used by fallback
    llm:       LLMAnswer,
    tenant:    TenantProfile,
    posture:   dict,
):
    """
    Node: vector retrieval + graph expansion + rank_and_answer (combined).
    Replaces: Steps 3-6 of _run_pipeline in one node.
    Uses rank_and_answer for zero-position-bias answering.
    """
    def retrieve(state: ArionState) -> dict:
        import re as _re
        from rag.classifier import QueryIntent, QuestionType

        qtype_map = {
            "gap_analysis":       QuestionType.GAP_ANALYSIS,
            "implementation":     QuestionType.IMPLEMENTATION,
            "definition":         QuestionType.DEFINITION,
            "posture_check":      QuestionType.POSTURE_CHECK,
            "cross_framework":    QuestionType.CROSS_FRAMEWORK,
            "free_assessment":    QuestionType.FREE_ASSESSMENT,
            "document_inventory": QuestionType.DOCUMENT_INVENTORY,
            "document_content":   QuestionType.DOCUMENT_CONTENT,
            "unknown":            QuestionType.UNKNOWN,
        }
        qtype = qtype_map.get(state["intent_type"], QuestionType.UNKNOWN)

        from rag.classifier import QueryDimensions
        from enrichment.events.event_nodes import detect_events

        # Reconstruct dimensions from state
        # needs_documentation detected from query phrases
        from rag.classifier import _detect_document_dimensions, _detect_document_question_type
        needs_doc, doc_topic = _detect_document_dimensions(state["query"])
        doc_qtype = _detect_document_question_type(state["query"])
        if doc_qtype:
            qtype = doc_qtype

        dimensions = QueryDimensions(
            needs_obligation    = True,
            needs_posture       = state["needs_posture"],
            needs_documentation = needs_doc,
        )

        # Detect events from query
        try:
            detected_events = detect_events(state["query"])
        except Exception:
            detected_events = []

        intent = QueryIntent(
            question_type      = qtype,
            standards_scope    = state["standards"],
            role_filter        = state.get("role"),
            needs_posture      = state["needs_posture"],
            cited_refs         = state["focus_refs"],
            resolved_refs      = state["focus_refs"],
            confidence         = state["confidence"],
            raw_query          = state["query"],
            dimensions         = dimensions,
            detected_events    = detected_events,
            document_topic_ref = doc_topic,
        )

        # ── Scope N/A short-circuit ───────────────────────────────────────
        # Physical security (A.7.x) and dev controls (A.8.25-31) are N/A.
        # Don't surface unrelated findings for these scope-excluded queries.
        if _is_scope_na_query(state["query"]):
            na_answer = _answer_scope_na(state["query"], posture)
            return {
                **state,
                "answer_text":   na_answer,
                "answer":        na_answer,
                "cited_refs":    [],
                "question_type": "gap_analysis",
                "confidence":    1.0,
                "answer_source": "postgres",
            }

        # ── Resolver: dispatch to per-taxonomy data sources ──────────────
        # Replaces ~190 lines of inline retrieval assembly.
        # Each taxonomy type gets the right sources (DB / graph / vector / both).
        from rag.resolver import Resolver, ResolveRequest
        from rag.taxonomy  import get_taxonomy_type

        _resolver = Resolver(
            retriever = retriever,
            expander  = expander,
            posture   = posture,
        )
        _req = ResolveRequest(
            query            = state["query"],
            classifier_type  = state["intent_type"],
            tenant_context   = tenant,
            topic_ref        = intent.document_topic_ref,
            standards        = intent.standards_scope,
            history          = [],
            # Observability: thread_id from LangGraph state = conversation request_id
            # tenant_id denormalised for fast trace access without hitting tenant_context
            request_id       = state.get("thread_id") or state.get("session_id") or "",
            tenant_id        = str(getattr(tenant, "tenant_id", "") or ""),
        )
        _resolved = _resolver.resolve(_req)

        # Short-circuit: Resolver found a direct Postgres answer
        if _resolved.has_short_circuit:
            return {
                **state,
                "answer_text":   _resolved.short_circuit_answer,
                "answer":        _resolved.short_circuit_answer,
                "cited_refs":    [],
                "question_type": state["intent_type"],
                "confidence":    1.0,
                "answer_source": "postgres",
            }

        # Store resolver trace in state for ANALYTICS display
        # (before we check for short-circuit so it's always available)
        _trace = getattr(_resolved, "trace", None)

        # Build expanded from resolved context
        # graph_nodes is always GraphResult after Phase 1 rewrite
        _gr              = _resolved.graph_nodes
        expanded_nodes   = _gr.all_nodes if hasattr(_gr, "all_nodes") else list(_gr)
        doc_contexts     = _resolved.doc_contexts   # property on ResolvedContext
        incident_contexts = []
        neo4j_ms         = _resolved.neo4j_ms

        # ── Rank + Answer in one Mistral call ──────────────────────────────
        # Pass all non-informational nodes as a numbered list.
        # Mistral selects the most relevant nodes and answers from them.
        # No position bias — every node gets equal attention.
        all_nodes = [
            n for n in expanded_nodes
            if not getattr(n, 'is_informational', False)
        ]

        standards_str = " + ".join(
            s.split(":")[0].replace("ISO27001", "ISO 27001")
            for s in state["standards"]
        )

        # ── Postgres short-circuit for upload status questions ─────────────
        # "have we uploaded X?" has a definitive answer in client_documents.
        # Don't involve the LLM for factual DB lookups — answer directly.
        if (intent.question_type.value == "document_inventory"
                and _is_upload_status_query(state["query"])):
            # Get alerts from tenant profile (set at startup from Postgres)
            _alerts = getattr(tenant, "document_alerts", []) or []
            pg_answer = _answer_upload_status(
                query   = state["query"],
                alerts  = _alerts,
            )
            if pg_answer:
                return {
                    **state,
                    "answer_text":   pg_answer,
                    "answer":        pg_answer,
                    "cited_refs":    [],
                    "question_type": "document_inventory",
                    "confidence":    1.0,   # deterministic DB answer
                    "answer_source": "postgres",
                }



        result = llm.rank_and_answer(
            query            = state["query"],
            nodes            = all_nodes,
            posture          = posture,
            intent           = intent,
            tenant_name      = state["tenant_id"],
            standards        = standards_str,
            doc_contexts     = doc_contexts     if doc_contexts     else None,
            incident_contexts= incident_contexts if incident_contexts else None,
        )


        # ── Write structured trace to DB (best-effort, never blocks answer) ─
        if _trace:
            try:
                _write_request_trace(
                    posture_db = posture_db if "posture_db" in dir() else None,
                    trace      = _trace,
                    tenant     = tenant,
                    topic_ref  = getattr(intent, "document_topic_ref", None),
                )
            except Exception as _te:
                logger.debug(f"[trace] write skipped: {_te}")

        return {
            "answer_text":    result.answer_text,
            "verified":       result.verified,
            "was_corrected":  result.was_corrected,
            "cited_refs":     result.cited_refs,
            "posture_findings": result.posture_findings,
            "node_count":     len(all_nodes),
            "neo4j_ms":       neo4j_ms,
            "resolver_trace": _trace,
        }

    return retrieve


def _write_request_trace(posture_db, trace, tenant, topic_ref) -> None:
    """
    Write one row to request_trace_log.
    Best-effort — called in a try/except so failures never block answers.
    posture_db: the Postgres connection/engine used for posture queries.
    """
    if not posture_db or not trace:
        return

    tenant_id = str(getattr(tenant, "tenant_id", "") or "")
    if not tenant_id:
        return

    sql = """
        INSERT INTO request_trace_log (
            request_id, tenant_id,
            query_text, classifier_type, taxonomy_type, handler_name,
            strategy, topic_ref,
            policy_posture, policy_vector, policy_graph,
            policy_doc_inv, policy_short_circuit,
            node_ids_built, nodes_primary, nodes_secondary,
            vector_hits, doc_contexts,
            posture_ids_used, vector_top_scores,
            posture_total, posture_nc, posture_ofi,
            posture_confirmed, posture_draft,
            short_circuit, answer_source,
            neo4j_ms, vector_ms, postgres_ms, total_ms,
            error_type, error_hint,
            traced_at
        ) VALUES (
            %(request_id)s, %(tenant_id)s::UUID,
            %(query_text)s, %(classifier_type)s, %(taxonomy_type)s, %(handler_name)s,
            %(strategy)s, %(topic_ref)s,
            %(policy_posture)s, %(policy_vector)s, %(policy_graph)s,
            %(policy_doc_inv)s, %(policy_short_circuit)s,
            %(node_ids_built)s, %(nodes_primary)s, %(nodes_secondary)s,
            %(vector_hits)s, %(doc_contexts)s,
            %(posture_ids_used)s, %(vector_top_scores)s::JSONB,
            %(posture_total)s, %(posture_nc)s, %(posture_ofi)s,
            %(posture_confirmed)s, %(posture_draft)s,
            %(short_circuit)s, %(answer_source)s,
            %(neo4j_ms)s, %(vector_ms)s, %(postgres_ms)s, %(total_ms)s,
            %(error_type)s, %(error_hint)s,
            NOW()
        )
        ON CONFLICT DO NOTHING
    """
    import json
    params = {
        "request_id":         trace.request_id or "",
        "tenant_id":          tenant_id,
        "query_text":         trace.query[:500],
        "classifier_type":    trace.classifier_type,
        "taxonomy_type":      trace.taxonomy_type,
        "handler_name":       trace.handler_name,
        "strategy":           trace.strategy,
        "topic_ref":          topic_ref,
        "policy_posture":     trace.policy_posture,
        "policy_vector":      trace.policy_vector,
        "policy_graph":       trace.policy_graph,
        "policy_doc_inv":     trace.policy_doc_inv,
        "policy_short_circuit": trace.policy_short_circuit,
        "node_ids_built":     trace.node_ids_built,
        "nodes_primary":      trace.nodes_primary,
        "nodes_secondary":    trace.nodes_secondary,
        "vector_hits":        trace.vector_results,
        "doc_contexts":       trace.doc_contexts,
        "posture_ids_used":   trace.posture_ids_used or [],
        "vector_top_scores":  json.dumps(trace.vector_top_scores or []),
        "posture_total":      trace.posture_total,
        "posture_nc":         trace.posture_nc,
        "posture_ofi":        trace.posture_ofi,
        "posture_confirmed":  trace.posture_confirmed,
        "posture_draft":      trace.posture_draft,
        "short_circuit":      trace.short_circuit,
        "answer_source":      trace.answer_source,
        "neo4j_ms":           trace.neo4j_ms,
        "vector_ms":          trace.vector_ms,
        "postgres_ms":        trace.postgres_ms,
        "total_ms":           trace.total_ms,
        "error_type":         type(trace.error).__name__ if trace.error else None,
        "error_hint":         trace.error_hint,
    }

    # Support psycopg2 connection, SQLAlchemy engine, or connection pool
    if hasattr(posture_db, "execute"):
        posture_db.execute(sql, params)
    elif hasattr(posture_db, "connect"):
        with posture_db.connect() as conn:
            conn.execute(sql, params)
            if hasattr(conn, "commit"):
                conn.commit()


def _node_exists_check(node_id: str, retriever) -> bool:
    """Check if a node_id exists in ChromaDB."""
    try:
        parts = node_id.split(":")
        ref = parts[-1]
        result = retriever.search_by_ref(ref)
        return result is not None
    except Exception:
        return False


# make_answer_node removed — rank_and_answer is now in make_retrieve_node

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
    builder.add_node("retrieve",       make_retrieve_node(retriever, expander, assembler, llm, tenant, posture))
    builder.add_node("clarify",        make_clarify_node())
    builder.add_node("update_session", make_update_session_node())

    # Entry point
    builder.set_entry_point("classify")

    # Edges — retrieve now includes rank_and_answer (no separate answer node)
    builder.add_conditional_edges("classify", route_after_classify)
    builder.add_edge("retrieve",       "update_session")
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

