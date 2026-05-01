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


def _is_scope_na_query(query: str) -> bool:
    """
    Returns True if the query is asking about controls that are N/A
    for Arion Networks scope (physical security, software development).
    These have a deterministic answer — no LLM needed.
    """
    SCOPE_NA_PATTERNS = [
        r'physical\s+security\s+(?:gaps?|findings?|controls?|posture|status)',
        r'physical\s+(?:access|entry|perimeter|premises)\s+(?:gaps?|controls?|security)',
        r'software\s+(?:development|dev(?:elopment)?)\s+security\s+(?:gaps?|findings?|controls?)',
        r'secure\s+(?:coding|development|software\s+dev)\s+(?:gaps?|controls?|posture)',
    ]
    for pat in SCOPE_NA_PATTERNS:
        if re.search(pat, query, re.IGNORECASE):
            return True
    return False


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



def _is_scope_na_query(query: str) -> bool:
    PATTERNS = [
        r'\bphysical\s+security\s+(?:gaps?|findings?|controls?|posture|status)\b',
        r'\bsoftware\s+(?:development|dev)\s+security\s+(?:gaps?|findings?|controls?)\b',
    ]
    return any(re.search(p, query, re.IGNORECASE) for p in PATTERNS)


def _answer_scope_na(query: str, posture: dict) -> str:
    q = query.lower()
    if re.search(r'physical\s+security|physical\s+access', q):
        return (
            "Physical security controls (A.7.x) are marked not applicable "
            "for Arion Networks. Your ISMS scope excludes physical premises "
            "controls - Arion operates as a cloud-based organisation. "
            "No physical security gaps apply to your organisation."
        )
    return (
        "Software development security controls (A.8.25-A.8.31) are marked "
        "not applicable for Arion Networks. Your ISMS scope excludes software "
        "development - Arion Networks does not develop software products. "
        "No software development security gaps exist in your scope."
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

        # ── Vector search ──────────────────────────────────────────────────
        search = retriever.search(
            query     = state["query"],
            n         = 15,
            standards = intent.standards_scope,
        )

        # ── Build node_ids ─────────────────────────────────────────────────
        def _node_valid(standard_id: str, ref: str) -> bool:
            """Validate that a standard_id:ref pair is well-formed.
            Only allows standards in the tenant's applicable_standards scope.
            """
            # Must be in tenant's scope
            if standard_id not in tenant.applicable_standards:
                return False
            if standard_id == "GDPR:2016/679":
                return ref.startswith("Art.")
            if "27001" in standard_id:
                return (ref.startswith("A.") or
                        bool(_re.match(r"^\d+[.]\d", ref)))
            if "27701" in standard_id:
                return (ref.startswith("6.") or ref.startswith("7.") or
                        bool(_re.match(r"^\d+[.]\d", ref)))
            return bool(ref)  # allow any non-empty ref for unknown standards

        # 1. Cited refs — from classifier phrase match or explicit ref
        anchor_refs = intent.cited_refs if intent.cited_refs else intent.resolved_refs
        cited_node_ids = [
            f"{s}:{r}"
            for s in intent.standards_scope
            for r in anchor_refs
            if _node_valid(s, r)
        ]

        # 2. Posture nodes — include NC/OFI/Comply but NOT N/A
        # N/A controls are excluded from Arion's scope — never surface as gaps
        posture_node_ids = [
            node_id for node_id, rec in posture.items()
            if node_id not in cited_node_ids
            and rec.get("finding") != "N/A"
        ]

        # 3. Obligation-implied nodes — deterministic from client facts
        #    These are legally mandatory for this client — cannot be missed
        implied_node_ids = []
        if hasattr(tenant, "facts") and tenant.facts is not None:
            try:
                implied_node_ids = expander.get_implied_controls(
                    facts     = tenant.facts,
                    standards = intent.standards_scope,
                )
                # Exclude already-included nodes
                already = set(cited_node_ids + posture_node_ids)
                implied_node_ids = [n for n in implied_node_ids if n not in already]
            except Exception:
                pass  # fail silently — vector search covers most cases

        # 4. Open incident obligations — controls triggered by active incidents
        incident_contexts = []
        incident_node_ids = []
        try:
            incident_contexts = expander.get_incident_obligations(
                tenant_id = tenant.tenant_id,
                standards = intent.standards_scope,
            )
            already = set(cited_node_ids + posture_node_ids + implied_node_ids)
            for inc in incident_contexts:
                for nid in inc.triggered_node_ids:
                    if nid not in already:
                        incident_node_ids.append(nid)
                        already.add(nid)
        except Exception:
            pass

        # 5. Vector results — semantic similarity, top 3 when we have strong anchors
        has_anchors = bool(cited_node_ids or posture_node_ids)
        vector_ids  = search.node_ids()[:3] if has_anchors else search.node_ids()[:10]

        node_ids = list(dict.fromkeys(
            cited_node_ids +
            posture_node_ids +
            implied_node_ids +
            incident_node_ids +
            vector_ids
        ))[:25]

        # ── Graph expansion ────────────────────────────────────────────────
        t0 = time.time()
        expanded = expander.expand(node_ids, intent)
        neo4j_ms = round((time.time() - t0) * 1000)

        # ── Document contexts (when needs_documentation) ───────────────
        doc_contexts = {}
        if intent.dimensions.needs_documentation:
            try:
                # For document_inventory/content — use topic ref or all nodes
                if intent.question_type.value in (
                    "document_inventory", "document_content"
                ):
                    if intent.document_topic_ref:
                        # Pin the topic control as a mandatory cited ref
                        topic_node_id = None
                        for std in intent.standards_scope:
                            candidate = f"{std}:{intent.document_topic_ref}"
                            check = expander._get_driver().session().run(
                                "MATCH (n:RequirementNode {id: $id}) RETURN n.id",
                                id=candidate
                            ).single()
                            if check:
                                topic_node_id = candidate
                                break
                        if topic_node_id and topic_node_id not in cited_node_ids:
                            cited_node_ids.insert(0, topic_node_id)

                        ctx = expander.get_document_checklist(
                            control_ref = intent.document_topic_ref,
                            tenant_id   = tenant.tenant_id,
                        )
                        if ctx:
                            doc_contexts[f"{intent.standards_scope[0]}:{intent.document_topic_ref}"] = ctx
                    else:
                        inv = expander.get_document_inventory(
                            tenant_id = tenant.tenant_id,
                            standards = intent.standards_scope,
                        )
                        for ctx in inv:
                            doc_contexts[ctx.node_id] = ctx
                else:
                    # Mixed query — fetch for selected node_ids
                    doc_contexts = expander.get_document_requirements(
                        node_ids  = node_ids[:10],
                        tenant_id = tenant.tenant_id,
                        standards = intent.standards_scope,
                    )
            except Exception:
                pass

        # ── Rank + Answer in one Mistral call ──────────────────────────────
        # Pass all non-informational nodes as a numbered list.
        # Mistral selects the most relevant nodes and answers from them.
        # No position bias — every node gets equal attention.
        all_nodes = [
            n for n in (expanded.primary_nodes + expanded.secondary_nodes)
            if not n.is_informational
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

        
        # Scope N/A short-circuit
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

        return {
            "answer_text":    result.answer_text,
            "verified":       result.verified,
            "was_corrected":  result.was_corrected,
            "cited_refs":     result.cited_refs,
            "posture_findings": result.posture_findings,
            "node_count":     len(all_nodes),
            "neo4j_ms":       neo4j_ms,
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
    Get the appropriate checkpointer for the current environment.

    Priority:
      1. DATABASE_URL + langgraph-checkpoint-postgres installed
             → PostgresSaver  (production — persistent, multi-tenant)
      2. DATABASE_URL set but package missing
             → SqliteSaver with warning (install: pip install langgraph-checkpoint-postgres)
      3. No DATABASE_URL / dev mode
             → SqliteSaver at ~/.arioncomply/sessions.db

    To enable PostgresSaver:
        pip install langgraph-checkpoint-postgres
        # DATABASE_URL is already set in .env
    """
    import logging
    _log = logging.getLogger(__name__)

    db_url = os.getenv("DATABASE_URL")
    if db_url:
        try:
            from langgraph.checkpoint.postgres import PostgresSaver
            saver = PostgresSaver.from_conn_string(db_url)
            _log.info("Checkpointer: PostgresSaver (persistent)")
            return saver
        except ImportError:
            _log.warning(
                "DATABASE_URL is set but langgraph-checkpoint-postgres is not installed. "
                "Sessions will not persist across restarts. "
                "Install: pip install langgraph-checkpoint-postgres"
            )

    # SQLite fallback — persistent within a single process, single machine
    if db_path is None:
        home   = os.path.expanduser("~")
        db_dir = os.path.join(home, ".arioncomply")
        os.makedirs(db_dir, exist_ok=True)
        db_path = os.path.join(db_dir, "sessions.db")

    from langgraph.checkpoint.sqlite import SqliteSaver
    _log.info(f"Checkpointer: SqliteSaver ({db_path})")
    return SqliteSaver.from_conn_string(db_path)
