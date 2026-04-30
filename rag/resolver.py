"""
ArionComply — Resolver

Dispatches each query to the correct data sources based on taxonomy type.
Replaces the make_retrieve_node monolith (~200 lines of if/elif) with a
clean per-type handler pattern.

Each handler:
  - Receives a ResolveRequest (query + intent + tenant context)
  - Calls the appropriate DB/graph/vector sources
  - Returns a ResolvedContext ready for the assembler

Adding support for a new taxonomy type:
  1. Add the type to taxonomy.py (no code change needed here)
  2. Add a _resolve_<type> method to Resolver
  3. Register it in _HANDLERS

The existing pipeline (arion_graph.py) calls Resolver.resolve() as a drop-in
replacement for the inline retrieval logic. The Resolver is stateless — safe
to share across threads.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional, Callable

from rag.taxonomy import QUERY_TAXONOMY, get_taxonomy_type, TaxonomyEntry

logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ResolveRequest:
    """Input to the resolver for one query."""
    query:          str
    classifier_type: str           # from classifier.py (e.g. "gap_analysis")
    tenant_context: object         # TenantContext from tenant_context.py
    topic_ref:      Optional[str]  # e.g. "A.5.18" if detected
    standards:      list[str]      # applicable standards for this tenant
    history:        list[dict] = field(default_factory=list)


@dataclass
class ResolvedContext:
    """
    Output from the resolver — everything the assembler needs to build LLM context.
    """
    # Primary data
    taxonomy_type:   str           # e.g. "POSTURE_STATUS"
    taxonomy_entry:  TaxonomyEntry

    # Posture data (from Postgres)
    posture_nodes:   dict          # {node_id: {finding, gap, control_ref, ...}}

    # Graph data (from Neo4j)
    graph_nodes:     list          # expanded RequirementNodes
    doc_contexts:    dict          # {node_id: DocumentContext}

    # Vector data (from ChromaDB)
    vector_nodes:    list          # VectorSearchResult items

    # Document alerts (from Postgres via TenantContext)
    document_alerts: list          # [{platform_ref, document_title, alert_type, ...}}]

    # Short-circuit answer (set when can_short_circuit=True and answer found)
    short_circuit_answer: Optional[str] = None
    answer_source:        str = "llm"  # "postgres" | "llm"

    # Performance
    neo4j_ms:        int = 0
    vector_ms:       int = 0
    postgres_ms:     int = 0

    @property
    def has_short_circuit(self) -> bool:
        return self.short_circuit_answer is not None


# =============================================================================
# RESOLVER
# =============================================================================

class Resolver:
    """
    Stateless dispatcher — maps taxonomy type to the right data sources.
    Instantiated once per process, shared across requests.

    Usage:
        resolver = Resolver(
            retriever  = chroma_retriever,
            expander   = neo4j_expander,
            posture    = tenant_posture_dict,
        )
        resolved = resolver.resolve(request)
    """

    def __init__(
        self,
        retriever,       # VectorRetriever (ChromaDB)
        expander,        # GraphExpander (Neo4j)
        posture: dict,   # full posture dict from TenantContext
    ):
        self._retriever = retriever
        self._expander  = expander
        self._posture   = posture

        # Dispatch table: taxonomy_type → handler method
        self._handlers: dict[str, Callable] = {
            "POSTURE_STATUS":    self._resolve_posture_status,
            "DOCUMENT_STATUS":   self._resolve_document_status,
            "REMEDIATION_GUIDE": self._resolve_remediation_guide,
            "DOCUMENT_CONTENT":  self._resolve_document_content,
            "STANDARD_KNOWLEDGE":self._resolve_standard_knowledge,
            "CROSS_FRAMEWORK":   self._resolve_cross_framework,
            "EVIDENCE_CHECK":    self._resolve_evidence_check,
            "ASSESSMENT":        self._resolve_assessment,
            "EVENT_RESPONSE":    self._resolve_event_response,
        }

    def resolve(self, request: ResolveRequest) -> ResolvedContext:
        """
        Main entry point. Maps classifier_type → taxonomy_type → handler.
        """
        entry   = get_taxonomy_type(request.classifier_type)
        handler = self._handlers.get(entry.type_id, self._resolve_default)

        logger.debug(
            f"resolve: classifier={request.classifier_type} "
            f"→ taxonomy={entry.type_id} "
            f"→ handler={handler.__name__}"
        )
        return handler(request, entry)

    # =========================================================================
    # TIER 1: DB-first handlers
    # =========================================================================

    def _resolve_document_status(
        self, req: ResolveRequest, entry: TaxonomyEntry
    ) -> ResolvedContext:
        """
        DOCUMENT_STATUS — pure Postgres lookup.
        Short-circuits: no LLM, no Neo4j, no ChromaDB.
        Answer built directly from document_alerts on TenantContext.
        """
        alerts  = req.tenant_context.document_alerts or []
        answer  = _build_document_status_answer(req.query, alerts)

        return ResolvedContext(
            taxonomy_type         = "DOCUMENT_STATUS",
            taxonomy_entry        = entry,
            posture_nodes         = {},
            graph_nodes           = [],
            doc_contexts          = {},
            vector_nodes          = [],
            document_alerts       = alerts,
            short_circuit_answer  = answer,
            answer_source         = "postgres",
        )

    def _resolve_posture_status(
        self, req: ResolveRequest, entry: TaxonomyEntry
    ) -> ResolvedContext:
        """
        POSTURE_STATUS — posture from Postgres, graph context for richness.
        Needs LLM to synthesise multiple findings into a coherent answer.
        """
        t0 = time.time()

        # Filter posture to relevant controls
        posture = _filter_posture(self._posture, req.topic_ref)

        # Vector retrieval
        vector_t0  = time.time()
        v_results  = self._retriever.search(
            req.query, n=10, standards=req.standards
        )
        vector_ms  = int((time.time() - vector_t0) * 1000)

        # Graph expansion on top vector nodes
        neo4j_t0   = time.time()
        node_ids   = [r.node_id for r in v_results.results[:8]]
        expanded   = self._expander.expand_nodes(
            node_ids, req.tenant_context.tenant_id, req.standards
        ) if node_ids else type("E", (), {"nodes": [], "doc_contexts": {}})()
        neo4j_ms   = int((time.time() - neo4j_t0) * 1000)

        return ResolvedContext(
            taxonomy_type  = "POSTURE_STATUS",
            taxonomy_entry = entry,
            posture_nodes  = posture,
            graph_nodes    = getattr(expanded, "nodes", []),
            doc_contexts   = getattr(expanded, "doc_contexts", {}),
            vector_nodes   = v_results.results,
            document_alerts= req.tenant_context.document_alerts or [],
            neo4j_ms       = neo4j_ms,
            vector_ms      = vector_ms,
        )

    # =========================================================================
    # TIER 2: LLM synthesis handlers
    # =========================================================================

    def _resolve_remediation_guide(
        self, req: ResolveRequest, entry: TaxonomyEntry
    ) -> ResolvedContext:
        """
        REMEDIATION_GUIDE — finding + policy pointer + steps + documents.
        Uses: posture (what the gap is) + graph (what steps/docs are needed)
        + chroma (standard context) + document_alerts (what's uploaded/missing).
        """
        posture   = _filter_posture(self._posture, req.topic_ref)

        vector_t0 = time.time()
        v_results = self._retriever.search(
            req.query, n=12, standards=req.standards
        )
        vector_ms = int((time.time() - vector_t0) * 1000)

        neo4j_t0  = time.time()
        node_ids  = [r.node_id for r in v_results.results[:10]]

        # Get document inventory for topic_ref — core of remediation guide
        doc_inv   = {}
        if req.topic_ref and self._expander._is_online():
            doc_inv = self._expander.get_document_inventory(
                node_ids   = node_ids,
                tenant_id  = req.tenant_context.tenant_id,
                standards  = req.standards,
                topic_ref  = req.topic_ref,
            )

        expanded  = self._expander.expand_nodes(
            node_ids, req.tenant_context.tenant_id, req.standards
        ) if node_ids else type("E", (), {"nodes": [], "doc_contexts": {}})()
        neo4j_ms  = int((time.time() - neo4j_t0) * 1000)

        return ResolvedContext(
            taxonomy_type  = "REMEDIATION_GUIDE",
            taxonomy_entry = entry,
            posture_nodes  = posture,
            graph_nodes    = getattr(expanded, "nodes", []),
            doc_contexts   = {**getattr(expanded, "doc_contexts", {}), **doc_inv},
            vector_nodes   = v_results.results,
            document_alerts= req.tenant_context.document_alerts or [],
            neo4j_ms       = neo4j_ms,
            vector_ms      = vector_ms,
        )

    def _resolve_document_content(
        self, req: ResolveRequest, entry: TaxonomyEntry
    ) -> ResolvedContext:
        """
        DOCUMENT_CONTENT — what a document must contain (checklist from graph).
        Primary source: Neo4j DocumentRequirement → ChecklistItem.
        """
        neo4j_t0 = time.time()
        node_ids = []

        if req.topic_ref:
            # Direct lookup by control ref
            doc_inv = self._expander.get_document_inventory(
                node_ids   = [],
                tenant_id  = req.tenant_context.tenant_id,
                standards  = req.standards,
                topic_ref  = req.topic_ref,
            ) if self._expander._is_online() else {}
        else:
            # Vector search to find relevant controls
            v_results = self._retriever.search(
                req.query, n=8, standards=req.standards
            )
            node_ids  = [r.node_id for r in v_results.results[:6]]
            doc_inv   = self._expander.get_document_inventory(
                node_ids   = node_ids,
                tenant_id  = req.tenant_context.tenant_id,
                standards  = req.standards,
                topic_ref  = None,
            ) if self._expander._is_online() else {}

        neo4j_ms = int((time.time() - neo4j_t0) * 1000)

        return ResolvedContext(
            taxonomy_type  = "DOCUMENT_CONTENT",
            taxonomy_entry = entry,
            posture_nodes  = {},
            graph_nodes    = [],
            doc_contexts   = doc_inv,
            vector_nodes   = [],
            document_alerts= req.tenant_context.document_alerts or [],
            neo4j_ms       = neo4j_ms,
        )

    def _resolve_standard_knowledge(
        self, req: ResolveRequest, entry: TaxonomyEntry
    ) -> ResolvedContext:
        """
        STANDARD_KNOWLEDGE — definition/explanation from graph + vector.
        Does NOT inject posture by default (answers a generic "what is X?" question).
        JFYI engine adds "your posture on this" afterwards if relevant.
        """
        vector_t0 = time.time()
        v_results = self._retriever.search(
            req.query, n=8, standards=req.standards
        )
        vector_ms = int((time.time() - vector_t0) * 1000)

        neo4j_t0  = time.time()
        node_ids  = [r.node_id for r in v_results.results[:6]]
        expanded  = self._expander.expand_nodes(
            node_ids, req.tenant_context.tenant_id, req.standards
        ) if node_ids else type("E", (), {"nodes": [], "doc_contexts": {}})()
        neo4j_ms  = int((time.time() - neo4j_t0) * 1000)

        return ResolvedContext(
            taxonomy_type  = "STANDARD_KNOWLEDGE",
            taxonomy_entry = entry,
            posture_nodes  = {},   # JFYI adds posture if relevant
            graph_nodes    = getattr(expanded, "nodes", []),
            doc_contexts   = getattr(expanded, "doc_contexts", {}),
            vector_nodes   = v_results.results,
            document_alerts= [],
            neo4j_ms       = neo4j_ms,
            vector_ms      = vector_ms,
        )

    # =========================================================================
    # TIER 3: Cross-cutting handlers
    # =========================================================================

    def _resolve_cross_framework(
        self, req: ResolveRequest, entry: TaxonomyEntry
    ) -> ResolvedContext:
        """
        CROSS_FRAMEWORK — ISO 27701 → GDPR bridge.
        Posture on bridge controls + graph for Annex D mapping.
        """
        # Include all posture (need full picture for GDPR assessment)
        posture = self._posture

        vector_t0 = time.time()
        v_results = self._retriever.search(
            req.query, n=12, standards=req.standards
        )
        vector_ms = int((time.time() - vector_t0) * 1000)

        neo4j_t0  = time.time()
        node_ids  = [r.node_id for r in v_results.results[:10]]
        expanded  = self._expander.expand_nodes(
            node_ids, req.tenant_context.tenant_id, req.standards
        ) if node_ids else type("E", (), {"nodes": [], "doc_contexts": {}})()
        neo4j_ms  = int((time.time() - neo4j_t0) * 1000)

        return ResolvedContext(
            taxonomy_type  = "CROSS_FRAMEWORK",
            taxonomy_entry = entry,
            posture_nodes  = posture,
            graph_nodes    = getattr(expanded, "nodes", []),
            doc_contexts   = getattr(expanded, "doc_contexts", {}),
            vector_nodes   = v_results.results,
            document_alerts= req.tenant_context.document_alerts or [],
            neo4j_ms       = neo4j_ms,
            vector_ms      = vector_ms,
        )

    def _resolve_evidence_check(
        self, req: ResolveRequest, entry: TaxonomyEntry
    ) -> ResolvedContext:
        """
        EVIDENCE_CHECK — what exists + what's missing for a control.
        Combines posture (finding) + doc_contexts (checklist) + document_alerts.
        """
        posture   = _filter_posture(self._posture, req.topic_ref)

        vector_t0 = time.time()
        v_results = self._retriever.search(
            req.query, n=10, standards=req.standards
        )
        vector_ms = int((time.time() - vector_t0) * 1000)

        neo4j_t0  = time.time()
        node_ids  = [r.node_id for r in v_results.results[:8]]

        # Get both expanded nodes and document inventory
        expanded  = self._expander.expand_nodes(
            node_ids, req.tenant_context.tenant_id, req.standards
        ) if node_ids else type("E", (), {"nodes": [], "doc_contexts": {}})()

        doc_inv = {}
        if req.topic_ref and self._expander._is_online():
            doc_inv = self._expander.get_document_inventory(
                node_ids   = node_ids,
                tenant_id  = req.tenant_context.tenant_id,
                standards  = req.standards,
                topic_ref  = req.topic_ref,
            )

        neo4j_ms  = int((time.time() - neo4j_t0) * 1000)

        return ResolvedContext(
            taxonomy_type  = "EVIDENCE_CHECK",
            taxonomy_entry = entry,
            posture_nodes  = posture,
            graph_nodes    = getattr(expanded, "nodes", []),
            doc_contexts   = {**getattr(expanded, "doc_contexts", {}), **doc_inv},
            vector_nodes   = v_results.results,
            document_alerts= req.tenant_context.document_alerts or [],
            neo4j_ms       = neo4j_ms,
            vector_ms      = vector_ms,
        )

    def _resolve_assessment(
        self, req: ResolveRequest, entry: TaxonomyEntry
    ) -> ResolvedContext:
        """
        ASSESSMENT — full posture summary, no graph needed.
        All data lives in Postgres (posture_controls).
        """
        return ResolvedContext(
            taxonomy_type  = "ASSESSMENT",
            taxonomy_entry = entry,
            posture_nodes  = self._posture,   # full posture
            graph_nodes    = [],
            doc_contexts   = {},
            vector_nodes   = [],
            document_alerts= req.tenant_context.document_alerts or [],
        )

    # =========================================================================
    # TIER 4: Event-triggered (future)
    # =========================================================================

    def _resolve_event_response(
        self, req: ResolveRequest, entry: TaxonomyEntry
    ) -> ResolvedContext:
        """
        EVENT_RESPONSE — triggered obligations + immediate actions.
        Primarily graph-driven (incident obligations, Art.33 timelines).
        """
        vector_t0 = time.time()
        v_results = self._retriever.search(
            req.query, n=10, standards=req.standards
        )
        vector_ms = int((time.time() - vector_t0) * 1000)

        neo4j_t0  = time.time()
        node_ids  = [r.node_id for r in v_results.results[:8]]
        expanded  = self._expander.expand_nodes(
            node_ids, req.tenant_context.tenant_id, req.standards
        ) if node_ids else type("E", (), {"nodes": [], "doc_contexts": {}})()
        neo4j_ms  = int((time.time() - neo4j_t0) * 1000)

        return ResolvedContext(
            taxonomy_type  = "EVENT_RESPONSE",
            taxonomy_entry = entry,
            posture_nodes  = {},
            graph_nodes    = getattr(expanded, "nodes", []),
            doc_contexts   = getattr(expanded, "doc_contexts", {}),
            vector_nodes   = v_results.results,
            document_alerts= [],
            neo4j_ms       = neo4j_ms,
            vector_ms      = vector_ms,
        )

    def _resolve_default(
        self, req: ResolveRequest, entry: TaxonomyEntry
    ) -> ResolvedContext:
        """
        Fallback handler for unregistered types.
        Behaves like POSTURE_STATUS — safe default.
        """
        logger.warning(
            f"No handler for taxonomy type '{entry.type_id}' — using default"
        )
        return self._resolve_posture_status(req, entry)


# =============================================================================
# HELPERS
# =============================================================================

def _filter_posture(posture: dict, topic_ref: Optional[str]) -> dict:
    """
    If a topic_ref is detected (e.g. "A.5.18"), filter posture to that control
    plus related controls (same clause group).
    Falls back to full posture if topic_ref not found.
    """
    if not topic_ref or not posture:
        return posture

    # Try exact match first
    matched = {k: v for k, v in posture.items()
               if v.get("control_ref") == topic_ref
               or k.endswith(f":{topic_ref}")}

    # If exact match found, also include related controls in same clause (A.5.x)
    if matched and "." in topic_ref:
        clause_prefix = topic_ref.rsplit(".", 1)[0]  # "A.5.18" → "A.5"
        related = {k: v for k, v in posture.items()
                   if (v.get("control_ref") or "").startswith(clause_prefix)
                   and k not in matched}
        # Add at most 5 related controls to avoid overwhelming the context
        matched.update(dict(list(related.items())[:5]))

    return matched if matched else posture


def _build_document_status_answer(query: str, alerts: list) -> Optional[str]:
    """
    Build a direct Postgres-sourced answer for DOCUMENT_STATUS queries.
    Returns None if no relevant alerts found (LLM should handle it).
    """
    import re

    if not alerts:
        return (
            "All registered documents appear to have been uploaded, "
            "or no documents have been registered yet. "
            "Run 'python3 tools/doc_audit.py' to see the full register."
        )

    query_lower = query.lower()
    relevant    = []
    all_missing = alerts  # all are "registered but not uploaded"

    # Try to match query to specific document titles
    for alert in alerts:
        title       = (alert.get("document_title") or "").lower()
        title_words = [w for w in re.split(r'\W+', title) if len(w) > 4]
        if any(w in query_lower for w in title_words):
            relevant.append(alert)

    # Check if query is asking about all documents
    is_all_query = re.search(
        r'\b(all|missing|unuploaded|not.{0,10}uploaded)\s+(documents?|files?|policies)\b',
        query, re.IGNORECASE
    )

    if not relevant and not is_all_query:
        # Query mentions something we can't match — let LLM handle it
        return None

    lines = []

    if relevant:
        for doc in relevant:
            atype    = doc.get("alert_type", "INFO")
            title    = doc.get("document_title", "Unknown")
            ref      = doc.get("external_ref", "")
            controls = doc.get("linked_controls", "")
            icon     = "⚠ CRITICAL" if atype == "CRITICAL" else \
                       "⚠ WARNING"  if atype == "WARNING"  else "ℹ INFO"
            lines.append(
                f"{icon} — {title} ({ref}) is registered in the platform "
                f"but has NOT been uploaded yet."
            )
            if controls:
                lines.append(f"  Linked to controls: {controls}")

    elif is_all_query:
        critical = [a for a in all_missing if a.get("alert_type") == "CRITICAL"]
        warning  = [a for a in all_missing if a.get("alert_type") == "WARNING"]
        info     = [a for a in all_missing if a.get("alert_type") == "INFO"]

        if critical:
            lines.append(
                f"⚠ CRITICAL ({len(critical)} documents) — "
                f"not uploaded, linked to open NC findings:"
            )
            for a in critical:
                lines.append(
                    f"  • {a['document_title']} ({a['external_ref']}) "
                    f"→ {a.get('linked_controls', '')}"
                )
        if warning:
            lines.append(
                f"⚠ WARNING ({len(warning)} documents) — "
                f"not uploaded, linked to OFI findings:"
            )
            for a in warning[:5]:
                lines.append(
                    f"  • {a['document_title']} ({a['external_ref']}) "
                    f"→ {a.get('linked_controls', '')}"
                )
        if info:
            lines.append(
                f"ℹ {len(info)} additional document(s) registered "
                f"but not uploaded (no open findings linked)."
            )

    if not lines:
        return None

    lines.extend([
        "",
        "To upload documents, place files in your documents folder and run:",
        "  python3 tools/doc_uploader.py --dir /path/to/docs --live",
    ])
    return "\n".join(lines)
