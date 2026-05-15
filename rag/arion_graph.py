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

# "uploaded" is the canonical verb, but users naturally say submitted /
# delivered / provided / shared / sent in. Treat them as synonyms.
_UPLOAD_VERB = r'(?:uploaded|submitted|delivered|provided|shared|sent\s+in)'

_UPLOAD_STATUS_PATTERNS = [
    re.compile(rf'\bhave\s+we\s+{_UPLOAD_VERB}\b', re.IGNORECASE),
    re.compile(rf'\bdid\s+we\s+{_UPLOAD_VERB}\b', re.IGNORECASE),
    re.compile(rf'\b(?:is|are)\s+(?:our|the)\s+[\w\s]{{2,40}}(?:policy|procedure|plan|playbook|document)s?\s+(?:{_UPLOAD_VERB}|in\s+the\s+system|on\s+the\s+platform)\b', re.IGNORECASE),
    re.compile(rf'\bwhich\s+documents?\s+(?:have\s+(?:not|yet)\s+been|are\s+(?:not|still)?)\s+{_UPLOAD_VERB}\b', re.IGNORECASE),
    re.compile(r'\bshow\s+(?:me\s+)?(?:missing|unuploaded)\s+documents?\b', re.IGNORECASE),
    # "what/which documents are missing?", "are any documents missing?"
    re.compile(r'\b(?:what|which|any)\s+documents?\s+(?:are\s+)?(?:missing|unuploaded)\b', re.IGNORECASE),
    re.compile(r'\bdocuments?\s+(?:are\s+)?(?:missing|unuploaded|not\s+(?:yet\s+)?(?:uploaded|submitted))\b', re.IGNORECASE),
]


def _is_upload_status_query(query: str) -> bool:
    return any(p.search(query) for p in _UPLOAD_STATUS_PATTERNS)


_POSITIVE_UPLOAD_MARKERS = (
    # canonical verb variants
    "have we uploaded", "we have uploaded", "we uploaded",
    "documents uploaded", "uploaded documents",
    "what is uploaded", "what's uploaded", "what are uploaded",
    "show uploaded", "list uploaded", "list of uploaded",
    "which documents have we uploaded",
    # natural synonyms users actually use
    "have we submitted", "we submitted", "did we submit",
    "have we delivered", "we delivered",
    "have we provided", "we provided",
    "have we shared", "we shared",
    "have we sent", "we sent",
)

_NEGATIVE_UPLOAD_MARKERS = (
    "not uploaded", "haven't been uploaded", "have not been uploaded",
    "not yet uploaded", "yet to be uploaded", "still need to upload",
    "do we need to upload",
    "not submitted", "not yet submitted",
    "missing", "unuploaded",
)


def _detect_upload_polarity(query: str) -> str:
    """
    Classify an upload-status query as 'positive' (user wants list of
    uploaded docs), 'negative' (wants missing list), or 'ambiguous'
    (likely a specific-doc lookup — try title match against both lists).
    Negative markers win when both are present ("have we uploaded the
    things that aren't uploaded" → negative).
    """
    q = query.lower()
    if any(m in q for m in _NEGATIVE_UPLOAD_MARKERS):
        return "negative"
    if any(m in q for m in _POSITIVE_UPLOAD_MARKERS):
        return "positive"
    return "ambiguous"


_STOP_WORDS = {
    "have", "has", "our", "the", "any", "and", "what", "which", "are",
    "been", "yet", "have", "ours", "do", "did", "we", "we've", "your",
    "for", "with", "from", "this", "that", "these", "those",
    "document", "documents", "policy", "policies", "procedure",
    "procedures", "plan", "plans",
}


# Framework-aware ref helpers live in rag/framework_refs.py so they can be
# shared between arion_graph and context_assembler without circular import.
from rag.framework_refs import (
    group_refs_by_framework  as _group_refs_by_framework,
    render_framework_refs    as _render_framework_refs,
)


def _title_match_against(query: str, items: list, title_key: str) -> list:
    """
    Find items whose title overlaps the query by ≥2 significant words.
    Returns matching items ranked by overlap (best first). Significant =
    >3 chars and not in _STOP_WORDS.
    """
    q_words = {
        w for w in re.split(r"[\W_]+", query.lower())
        if len(w) > 3 and w not in _STOP_WORDS
    }
    if not q_words:
        return []
    ranked = []
    for it in items:
        title = (it.get(title_key) or "").lower()
        t_words = {
            w for w in re.split(r"[\W_]+", title)
            if len(w) > 3 and w not in _STOP_WORDS
        }
        overlap = len(q_words & t_words)
        if overlap >= 2:
            ranked.append((overlap, it))
    ranked.sort(key=lambda r: r[0], reverse=True)
    return [it for _, it in ranked]


def _answer_upload_status(
    query:    str,
    alerts:   list,
    uploaded: list | None = None,
) -> str | None:
    """
    Answer an upload status question directly from the right data source:
      - positive polarity → answer from client_documents (status='uploaded')
      - negative polarity → list from document_alerts (registered, missing)
      - ambiguous (specific doc by name) → match titles against both lists
    Deterministic — no LLM involved. Returns None to fall through to LLM.
    """
    uploaded = uploaded or []
    polarity = _detect_upload_polarity(query)

    # ── Positive: which documents have we uploaded / submitted / etc ───
    if polarity == "positive":
        # If the query names a specific document, answer about THAT one,
        # not the full inventory. Look in uploaded first (yes-answer wins),
        # then in alerts (no-answer for a known-but-missing doc).
        up_hits = _title_match_against(query, uploaded, "document_title")
        if up_hits:
            d = up_hits[0]
            title    = d.get("document_title") or d.get("filename") or "the requested document"
            ref      = d.get("external_ref") or d.get("platform_ref") or ""
            ref_s    = f" ({ref})" if ref else ""
            when     = d.get("uploaded_at")
            when_s   = f" on {when[:10]}" if when else ""
            doc_type = d.get("doc_type") or ""
            type_s   = f" ({doc_type})" if doc_type else ""
            extras = []
            if d.get("page_count"):
                extras.append(f"{d['page_count']} pages")
            framework_clause = _render_framework_refs(d.get("framework_refs"))
            if framework_clause:
                extras.append(f"assessed against {framework_clause}")
            extra_s = f" — {'; '.join(extras)}" if extras else ""
            return (
                f"Yes — {title}{ref_s}{type_s} has been uploaded{when_s}{extra_s}. "
                f"Document status: {d.get('document_status', 'uploaded')}."
            )

        alert_hits = _title_match_against(query, alerts, "document_title")
        if alert_hits:
            a = alert_hits[0]
            title = a.get("document_title") or "the requested document"
            ref   = a.get("external_ref") or ""
            ref_s = f" ({ref})" if ref else ""
            # Prefer the structured array from the view; fall back to the
            # flat string for older snapshots.
            framework_clause = _render_framework_refs(a.get("linked_control_refs"))
            if not framework_clause and a.get("linked_controls"):
                framework_clause = a["linked_controls"]
            ctl_s = f" It is linked to {framework_clause}." if framework_clause else ""
            return (
                f"No — {title}{ref_s} is registered but has not yet been "
                f"uploaded to the platform.{ctl_s}"
            )

        # No specific doc named — answer about the whole inventory
        if not uploaded:
            return (
                "No documents have been uploaded to the platform yet. "
                "Registered documents are tracked in our checklist but their "
                "files haven't been delivered — use the upload endpoint or "
                "tools/doc_uploader.py to upload them."
            )
        lines = [f"Uploaded documents ({len(uploaded)} total):"]
        for d in uploaded[:20]:
            title    = d.get("document_title") or d.get("filename") or "?"
            ref      = d.get("external_ref") or d.get("platform_ref") or ""
            ref_s    = f" ({ref})" if ref else ""
            doc_type = d.get("doc_type") or ""
            type_s   = f" — {doc_type}" if doc_type else ""
            when     = d.get("uploaded_at")
            when_s   = f", uploaded {when[:10]}" if when else ""
            framework_clause = _render_framework_refs(d.get("framework_refs"))
            asses_s  = f"; assessed against {framework_clause}" if framework_clause else ""
            lines.append(f"  • {title}{ref_s}{type_s}{when_s}{asses_s}")
        if len(uploaded) > 20:
            lines.append(f"  … and {len(uploaded) - 20} more")
        return "\n".join(lines)

    # ── Negative or ambiguous: report missing/registered from alerts ───
    if not alerts and polarity == "negative":
        return "No registered documents are currently flagged as missing."
    if not alerts:
        return None  # Nothing to say; let the LLM try

    query_lower = query.lower()

    # Title-match for ambiguous specific-doc queries
    relevant = []
    if polarity == "ambiguous":
        for alert in alerts:
            title = (alert.get("document_title") or "").lower()
            title_words = [w for w in title.split() if len(w) > 3]
            if any(w in query_lower for w in title_words):
                relevant.append(alert)

    # Negative polarity (or ambiguous with no title hit): list everything missing
    if not relevant:
        if polarity == "negative":
            relevant = [a for a in alerts
                       if a.get("alert_type") in ("CRITICAL", "WARNING", "INFO")]
        else:
            return None  # Ambiguous and no title match — let LLM handle

    lines = []
    critical = [a for a in relevant if a.get("alert_type") == "CRITICAL"]
    warning  = [a for a in relevant if a.get("alert_type") == "WARNING"]
    info     = [a for a in relevant if a.get("alert_type") == "INFO"]

    def _link_clause(a: dict) -> str:
        """Framework-aware 'linked to …' clause for one alert."""
        rendered = _render_framework_refs(a.get("linked_control_refs"))
        if rendered:
            return rendered
        # Legacy fallback when the structured array is unavailable
        flat = a.get("linked_controls")
        return flat if flat else "unknown"

    if critical:
        lines.append("The following documents are registered but NOT yet uploaded "
                     "and are linked to open NC findings:")
        for a in critical:
            lines.append(
                f"  • {a['document_title']} ({a['external_ref']}) "
                f"— linked to {_link_clause(a)}"
            )
    if warning:
        if lines:
            lines.append("")
        lines.append("Also registered but not uploaded — linked to OFI findings:")
        for a in warning:
            lines.append(
                f"  • {a['document_title']} ({a['external_ref']}) "
                f"— linked to {_link_clause(a)}"
            )
    if info:
        if not critical and not warning:
            lines.append("Registered but not yet uploaded:")
            for a in info[:5]:
                lines.append(f"  • {a['document_title']} ({a['external_ref']})")
            if len(info) > 5:
                lines.append(
                    f"  … and {len(info) - 5} more registered but not yet "
                    f"linked to findings."
                )
        else:
            # Critical/warning already listed individually; summarise the
            # rest so the LLM composer (and the user) know they exist.
            lines.append("")
            lines.append(
                f"There are also {len(info)} additional documents registered "
                f"but not yet uploaded (not currently linked to any open "
                f"NC or OFI findings)."
            )

    if lines:
        lines.append("")
        lines.append(
            "Upload these files to the platform so the system can verify "
            "their content against control checklists automatically."
        )

    return "\n".join(lines) if lines else None


# ── Generic short-circuit → LLM polish helper ────────────────────────────────

# Every ref shape that MUST survive any rewrite verbatim:
#   - DOC###, CD-XXX-### : entity identifiers (which document/control)
#   - A.x.y              : ISO 27001/27701 clause numbers (which control the
#                          finding/document maps to — auditors need these)
#   - Art.X              : GDPR / NIS2 articles (cross-framework attribution)
# Dropping any of these silently changes the answer's compliance content.
# The LLM should rephrase prose, never drop refs.
_SHORT_CIRCUIT_REQUIRED_REF_PATTERN = re.compile(
    r'\bDOC\d{3}\b'
    r'|\bCD-[A-Z]{2,4}-\d{3,4}\b'
    r'|\bA\.\d+(?:\.\d+)*\b'
    r'|\bArt\.\s?\d+(?:\(\d+\))?\b'
)

# Lines that look like a CLI action the user is expected to run.
_ACTION_HINT_MARKERS = ("upload:", "run:", "tools/")


def polish_short_circuit_answer(
    query:                str,
    deterministic_answer: str,
    llm,
) -> str:
    """
    Polish any deterministic short-circuit answer into conversational prose
    via LLMAnswer.compose(). Extracts every ref shape and action-hint line
    from the deterministic text so the composer can preserve them verbatim.
    On any failure compose() returns the deterministic text unchanged —
    the short-circuit invariant (no data loss) is preserved.
    """
    if not deterministic_answer:
        return deterministic_answer

    required_refs = list(set(_SHORT_CIRCUIT_REQUIRED_REF_PATTERN.findall(deterministic_answer)))

    action_hint = None
    for line in deterministic_answer.splitlines():
        s = line.strip()
        if any(m in s.lower() for m in _ACTION_HINT_MARKERS):
            action_hint = s
            break

    return llm.compose(
        query              = query,
        deterministic_text = deterministic_answer,
        required_refs      = required_refs,
        action_hint        = action_hint,
    )


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

        # Clarification response: user replied to a taxonomy question (a/b/c).
        # Accept bare letters ("a", "b)", "c."), bracketed forms ("(a)", "[c]"),
        # AND the rendered button text the UI sends back ("(c) Do you need ...").
        # The letter must be followed by ).].:.,/whitespace/end to avoid false
        # matches on real words that start with a-c (e.g. "are we GDPR …").
        import re as _re
        _letter_re = _re.compile(r"^[\(\[]?\s*([a-c])(?=\s*[\)\].\:,]|\s*$)")
        _letter_match = _letter_re.match(query.strip().lower()) if query else None
        _is_clarif_response = bool(
            state.get("turn_count", 0) > 0            # not first turn
            and state.get("needs_clarif") is True     # clarif question was shown
            and state.get("clarif_count", 0) > 0      # we did ask a clarif question
            and bool(state.get("clarif_question"))    # there is a pending question
            and _letter_match
        )
        if _is_clarif_response:
            # Map letter directly to intent type from taxonomy_options_map
            # stored in state (set when we returned the clarif question)
            tmap = state.get("taxonomy_options_map") or {}
            letter = _letter_match.group(1)
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
                count = state["clarif_count"] + 1
                if count >= 2:
                    # Already asked once — fall through to best-effort
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
                    "intent_type":    "unknown",
                    "focus_refs":     [],
                    "needs_posture":  False,
                    "confidence":     0.0,
                    "needs_clarif":   True,
                    "clarif_question": intake.clarification or "",
                    "clarif_count":   count,
                    "turn_count":     state["turn_count"] + 1,
                    "original_query": query,
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
            composed = polish_short_circuit_answer(
                query                = state["query"],
                deterministic_answer = na_answer,
                llm                  = llm,
            )
            return {
                **state,
                "answer_text":   composed,
                "answer":        composed,
                "cited_refs":    [],
                "question_type": "gap_analysis",
                "confidence":    1.0,
                "answer_source": "postgres+llm",
            }

        # ── Postgres short-circuit for upload status questions ─────────────
        # Runs BEFORE the resolver: the resolver's DOCUMENT_STATUS handler
        # only knows the "missing" side and mis-answers positive-polarity
        # queries via title-word heuristics. We have a polarity-aware
        # answerer + both data sides on the tenant profile, so use them.
        if (intent.question_type.value == "document_inventory"
                and _is_upload_status_query(state["query"])):
            _alerts   = getattr(tenant, "document_alerts", []) or []
            _uploaded = getattr(tenant, "uploaded_documents", []) or []
            pg_answer = _answer_upload_status(
                query    = state["query"],
                alerts   = _alerts,
                uploaded = _uploaded,
            )
            if pg_answer:
                # Fact-preserving prose polish over the deterministic answer.
                # Falls back to pg_answer on any failure — never regresses.
                composed = polish_short_circuit_answer(
                    query                = state["query"],
                    deterministic_answer = pg_answer,
                    llm                  = llm,
                )
                return {
                    **state,
                    "answer_text":   composed,
                    "answer":        composed,
                    "cited_refs":    [],
                    "question_type": "document_inventory",
                    "confidence":    1.0,
                    "answer_source": "postgres+llm",
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
            # Explicit refs from the query — used by handlers to seed graph
            # expansion when the user names a specific control by ref
            cited_refs       = list(getattr(intent, "cited_refs", []) or []),
            # Observability: thread_id from LangGraph state = conversation request_id
            # tenant_id denormalised for fast trace access without hitting tenant_context
            request_id       = state.get("thread_id") or state.get("session_id") or "",
            tenant_id        = str(getattr(tenant, "tenant_id", "") or ""),
        )
        _resolved = _resolver.resolve(_req)

        # Short-circuit: Resolver found a direct Postgres answer
        if _resolved.has_short_circuit:
            composed = polish_short_circuit_answer(
                query                = state["query"],
                deterministic_answer = _resolved.short_circuit_answer,
                llm                  = llm,
            )
            return {
                **state,
                "answer_text":   composed,
                "answer":        composed,
                "cited_refs":    [],
                "question_type": state["intent_type"],
                "confidence":    1.0,
                "answer_source": "postgres+llm",
            }

        # Store resolver trace in state for ANALYTICS display
        # (before we check for short-circuit so it's always available)
        _trace = getattr(_resolved, "trace", None)

        # Build expanded from resolved context
        # graph_nodes is always GraphResult after Phase 1 rewrite
        _gr              = _resolved.graph_nodes
        expanded_nodes   = _gr.all_nodes if hasattr(_gr, "all_nodes") else list(_gr)
        doc_contexts     = _resolved.doc_contexts   # property on ResolvedContext
        # Read active incidents + their materialized obligations from Postgres
        # (enriched by Neo4j for required-document IDs). Returns [] if either
        # store unavailable — chat still works without incident context.
        incident_contexts = expander.get_incident_obligations(
            tenant_id = state["tenant_id"],
            standards = state["standards"],
        )
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
            "turn_count":    state["turn_count"] + 1,
            "clarif_count":  0,
            "needs_clarif":  False,
            "clarif_question": "",
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
            # autocommit=True is REQUIRED by langgraph's PostgresSaver:
            # without it, checkpoint writes never commit and follow-up
            # turns can't see prior state across requests.
            conn = psycopg.connect(sessions_url, autocommit=True)
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
            # autocommit=True required: otherwise writes never commit and
            # cross-request state (turn_count, taxonomy_options_map, ...)
            # is lost between calls — causing infinite clarification loops.
            conn = await psycopg.AsyncConnection.connect(
                sessions_url, autocommit=True
            )
            saver = AsyncPostgresSaver(conn)
            await saver.setup()
            _log.info(f"AsyncCheckpointer: AsyncPostgresSaver ({sessions_url.split('@')[-1]})")
            return saver
        except Exception as _e:
            _log.warning(f"AsyncPostgresSaver failed ({_e}) — falling back to InMemorySaver")

    from langgraph.checkpoint.memory import InMemorySaver
    _log.info("AsyncCheckpointer: InMemorySaver")
    return InMemorySaver()

