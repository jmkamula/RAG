"""
ArionComply — Resolver  (Phase 1 rewrite)

Dispatches each query to the correct data sources based on taxonomy type.

Phase 1 fixes applied (per review report):
  - GraphResult dataclass: unified type for all graph returns
  - doc_contexts owned exclusively by GraphResult — no merging issues
  - All handlers return ResolvedContext with graph_nodes: GraphResult
  - _expand() always returns GraphResult, never raises
  - get_document_inventory() called with correct signature (no node_ids kwarg)
  - posture NC/OFI node_ids used by POSTURE_STATUS, DOCUMENT_CONTENT, CROSS_FRAMEWORK
  - Thread safe: posture dict read-only, never mutated
  - Dead code removed
"""
from __future__ import annotations

import logging
import time
import traceback as _tb
import uuid
from dataclasses import dataclass, field
from typing import Optional, Callable

from rag.taxonomy import get_taxonomy_type, TaxonomyEntry

logger = logging.getLogger(__name__)


# =============================================================================
# GRAPH RESULT
# =============================================================================

@dataclass
class GraphResult:
    """
    Single unified type for all Neo4j output.
    Eliminates type inconsistencies between ExpandedContext, lists, and None.
    """
    primary_nodes:      list = field(default_factory=list)
    secondary_nodes:    list = field(default_factory=list)
    doc_contexts:       dict = field(default_factory=dict)
    node_ids_input:     int  = 0    # count of node_ids passed to _expand() — for trace
    # Phase 3 granularity fields
    posture_ids_used:   list = field(default_factory=list)  # NC/OFI ids passed to expand
    vector_top_scores:  list = field(default_factory=list)  # [(node_id, score), ...]

    @property
    def all_nodes(self) -> list:
        return self.primary_nodes + self.secondary_nodes

    @classmethod
    def empty(cls) -> "GraphResult":
        return cls()

    @classmethod
    def from_expanded(cls, expanded) -> "GraphResult":
        """Convert any expanded result to GraphResult safely."""
        if expanded is None:
            return cls.empty()
        if isinstance(expanded, GraphResult):
            return expanded
        if isinstance(expanded, list):
            return cls(primary_nodes=list(expanded))
        return cls(
            primary_nodes   = list(getattr(expanded, "primary_nodes",   []) or []),
            secondary_nodes = list(getattr(expanded, "secondary_nodes", []) or []),
            doc_contexts    = dict(getattr(expanded, "doc_contexts",    {}) or {}),
        )


# =============================================================================
# REQUEST / RESPONSE
# =============================================================================

@dataclass
class ResolveRequest:
    """Input to the resolver for one query."""
    query:           str
    classifier_type: str
    tenant_context:  object
    topic_ref:       Optional[str]
    standards:       list
    history:         list  = field(default_factory=list)
    # Observability — set by caller, propagated through the full trace
    request_id:      str   = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id:       str   = ""   # denormalised from tenant_context for fast access


@dataclass
class ResolvedContext:
    """
    Output from the resolver.
    graph_nodes is always GraphResult.
    doc_contexts is a property — reads from graph_nodes.doc_contexts.
    """
    taxonomy_type:   str
    taxonomy_entry:  TaxonomyEntry
    posture_nodes:      dict          # {node_id: {finding, gap, control_ref, confirmation_status, ...}}
    graph_nodes:     GraphResult
    vector_nodes:    list
    document_alerts: list
    posture_confirmed:  int = 0   # count of confirmed/overridden findings
    posture_draft:      int = 0   # count of draft findings

    short_circuit_answer: Optional[str] = None
    answer_source:        str = "llm"

    neo4j_ms:    int = 0
    vector_ms:   int = 0
    postgres_ms: int = 0

    trace: Optional["ResolverTrace"] = None

    @property
    def has_short_circuit(self) -> bool:
        return self.short_circuit_answer is not None

    @property
    def doc_contexts(self) -> dict:
        """Single source of truth — always from graph_nodes."""
        return self.graph_nodes.doc_contexts


# =============================================================================
# RESOLVER TRACE
# =============================================================================

@dataclass
class ResolverTrace:
    # ── Identity — links this trace to a specific request and tenant ──────
    request_id:      str = ""   # UUID — set from ResolveRequest.request_id
    tenant_id:       str = ""   # set from ResolveRequest.tenant_id

    query:           str = ""
    classifier_type: str = ""
    taxonomy_type:   str = ""
    handler_name:    str = ""

    posture_total:   int = 0
    posture_nc:      int = 0
    posture_ofi:     int = 0
    posture_na:      int = 0

    node_ids_built:  int = 0
    nodes_primary:   int = 0
    nodes_secondary: int = 0
    doc_contexts:    int = 0
    vector_results:  int = 0

    short_circuit:   bool = False
    answer_source:   str  = "llm"

    # Posture confirmation counts
    posture_confirmed:   int  = 0
    posture_draft:       int  = 0

    # Retrieval granularity (Phase 3) — noted from review report
    strategy:            str  = ""    # e.g. "posture_first+vector_supplement"
    posture_ids_used:    list = field(default_factory=list)   # NC/OFI node_ids passed to expand
    vector_top_scores:   list = field(default_factory=list)   # top-3 [(node_id, score), ...]

    # Retrieval policy snapshot (from TaxonomyEntry at dispatch time)
    policy_posture:      bool = True
    policy_vector:       bool = True
    policy_graph:        bool = True
    policy_doc_inv:      bool = False
    policy_short_circuit:bool = False

    neo4j_ms:    int = 0
    vector_ms:   int = 0
    postgres_ms: int = 0
    total_ms:    int = 0

    error:      Optional[str] = None
    error_call: Optional[str] = None
    error_hint: Optional[str] = None

    def summary_line(self) -> str:
        rid = self.request_id[:8] if self.request_id else "--------"
        if self.error:
            return f"[{rid}] RESOLVER ERROR  handler={self.handler_name}  error={self.error}"
        if self.short_circuit:
            return f"[{rid}] {self.taxonomy_type}  strategy={self.strategy}  short_circuit=True  {self.total_ms}ms"
        return (
            f"[{rid}] {self.taxonomy_type}  strategy={self.strategy}  "
            f"NC={self.posture_nc}  OFI={self.posture_ofi}  "
            f"primary={self.nodes_primary}  secondary={self.nodes_secondary}  "
            f"docs={self.doc_contexts}  {self.total_ms}ms"
        )

    def full_trace(self) -> str:
        # Format posture_ids_used — show refs not raw UUIDs
        _pids = ", ".join(
            p.split(":")[-1] if ":" in p else p
            for p in (self.posture_ids_used or [])[:6]
        ) or "none"
        _vscore_str = ", ".join(
            f"{nid.split(':')[-1]}={score}"
            for nid, score in (self.vector_top_scores or [])[:3]
        ) or "none"

        lines = [
            "  [resolver trace]",
            f"    request_id   : {self.request_id}",
            f"    tenant_id    : {self.tenant_id or '(not set)'}",
            f"    query        : {self.query[:80]}",
            f"    classifier   : {self.classifier_type}",
            f"    taxonomy     : {self.taxonomy_type}",
            f"    handler      : {self.handler_name}",
            f"    strategy     : {self.strategy}",
            f"    policy       : posture={self.policy_posture} vector={self.policy_vector} graph={self.policy_graph} doc_inv={self.policy_doc_inv} short_circuit={self.policy_short_circuit}",
            f"    posture      : total={self.posture_total} NC={self.posture_nc} OFI={self.posture_ofi} NA={self.posture_na}",
            f"    confirmation : confirmed={self.posture_confirmed} draft={self.posture_draft}",
            f"    posture_ids  : {_pids}",
            f"    node_ids_in  : {self.node_ids_built}",
            f"    nodes_out    : primary={self.nodes_primary} secondary={self.nodes_secondary}",
            f"    doc_contexts : {self.doc_contexts}",
            f"    vector_hits  : {self.vector_results}",
            f"    vector_scores: {_vscore_str}",
            f"    short_circuit: {self.short_circuit} ({self.answer_source})",
            f"    timing       : neo4j={self.neo4j_ms}ms vector={self.vector_ms}ms postgres={self.postgres_ms}ms total={self.total_ms}ms",
        ]
        if self.error:
            lines += [
                f"    ERROR        : {self.error}",
                f"    called as    : {self.error_call or 'unknown'}",
                f"    hint         : {self.error_hint or 'check resolver.py handler'}",
            ]
        return "\n".join(lines)


# =============================================================================
# HELPERS
# =============================================================================

def _build_error_hint(exc: Exception, call_str: str) -> str:
    msg = str(exc).lower()
    if "unexpected keyword argument" in msg:
        kwarg = str(exc).split("'")[-2] if "'" in str(exc) else "?"
        return f"Remove kwarg {kwarg!r} — check method signature"
    if "no attribute" in msg:
        attr = str(exc).split("'")[-2] if "'" in str(exc) else "?"
        return f"{attr!r} missing — check GraphExpander or VectorRetriever API"
    if "list' object is not a mapping" in msg:
        return "get_document_inventory returns a list — do not use **dict unpack"
    if "not subscriptable" in msg:
        return "Object is None — check expander/retriever returned valid result"
    return "See full traceback above"


def _empty_context(entry: TaxonomyEntry) -> ResolvedContext:
    return ResolvedContext(
        taxonomy_type   = entry.type_id,
        taxonomy_entry  = entry,
        posture_nodes   = {},
        graph_nodes     = GraphResult.empty(),
        vector_nodes    = [],
        document_alerts = [],
    )


def _posture_nc_ofi_ids(posture: dict, topic_ref: Optional[str] = None) -> list:
    """Return node_ids for NC/OFI controls, with topic_ref matches first."""
    topic_ids   = []
    finding_ids = []
    for node_id, data in posture.items():
        finding = data.get("finding", "")
        ref     = data.get("control_ref", "") or node_id.split(":")[-1]
        if topic_ref and (topic_ref in node_id or ref == topic_ref):
            topic_ids.append(node_id)
        elif finding in ("NC", "OFI"):
            finding_ids.append(node_id)
    seen, result = set(), []
    for nid in topic_ids + finding_ids:
        if nid not in seen:
            seen.add(nid)
            result.append(nid)
    return result


def _filter_posture(posture: dict, topic_ref: Optional[str]) -> dict:
    """Filter posture to topic_ref + related clause. Falls back to full posture."""
    if not topic_ref or not posture:
        return posture
    matched = {
        k: v for k, v in posture.items()
        if v.get("control_ref") == topic_ref or k.endswith(f":{topic_ref}")
    }
    if matched and "." in topic_ref:
        clause_prefix = topic_ref.rsplit(".", 1)[0]
        related = {
            k: v for k, v in posture.items()
            if (v.get("control_ref") or "").startswith(clause_prefix) and k not in matched
        }
        matched.update(dict(list(related.items())[:5]))
    return matched if matched else posture


def _merge_doc_inv(gr: GraphResult, doc_inv) -> None:
    """Merge doc inventory result (list or dict) into gr.doc_contexts safely."""
    if isinstance(doc_inv, list):
        for doc in doc_inv:
            doc_id = getattr(doc, "req_id", None) or getattr(doc, "node_id", None)
            if doc_id:
                gr.doc_contexts[doc_id] = doc
    elif isinstance(doc_inv, dict):
        gr.doc_contexts.update(doc_inv)


def _build_document_status_answer(query: str, alerts: list) -> Optional[str]:
    import re
    if not alerts:
        return (
            "All registered documents appear to have been uploaded, "
            "or no documents have been registered yet."
        )
    query_lower = query.lower()
    relevant = []
    for alert in alerts:
        title       = (alert.get("document_title") or "").lower()
        title_words = [w for w in re.split(r"\W+", title) if len(w) > 4]
        if any(w in query_lower for w in title_words):
            relevant.append(alert)
    is_all = re.search(
        r"\b(all|missing|unuploaded|not.{0,10}uploaded)\s+(documents?|files?|policies)\b",
        query, re.IGNORECASE,
    )
    if not relevant and not is_all:
        return None
    lines = []
    if relevant:
        for doc in relevant:
            atype    = doc.get("alert_type", "INFO")
            title    = doc.get("document_title", "Unknown")
            ref      = doc.get("external_ref", "")
            controls = doc.get("linked_controls", "")
            icon     = "CRITICAL" if atype == "CRITICAL" else "WARNING" if atype == "WARNING" else "INFO"
            lines.append(f"[{icon}] {title} ({ref}) — registered but NOT uploaded.")
            if controls:
                lines.append(f"  Linked controls: {controls}")
    elif is_all:
        critical = [a for a in alerts if a.get("alert_type") == "CRITICAL"]
        warning  = [a for a in alerts if a.get("alert_type") == "WARNING"]
        info     = [a for a in alerts if a.get("alert_type") == "INFO"]
        if critical:
            lines.append(f"CRITICAL ({len(critical)} docs) — linked to NC findings:")
            for a in critical:
                lines.append(f"  - {a['document_title']} ({a['external_ref']}) -> {a.get('linked_controls','')}")
        if warning:
            lines.append(f"WARNING ({len(warning)} docs) — linked to OFI findings:")
            for a in warning[:5]:
                lines.append(f"  - {a['document_title']} ({a['external_ref']}) -> {a.get('linked_controls','')}")
        if info:
            lines.append(f"{len(info)} additional doc(s) registered but not uploaded.")
    if not lines:
        return None
    lines.append("")
    lines.append("Upload: python3 tools/doc_uploader.py --dir /path/to/docs --live")
    return "\n".join(lines)


# =============================================================================
# RESOLVER
# =============================================================================

class Resolver:
    """
    Stateless dispatcher. Safe to share across threads.
    posture dict is read-only — never mutated inside Resolver.
    """

    def __init__(self, retriever, expander, posture: dict):
        self._retriever = retriever
        self._expander  = expander
        # One-level-deep copy: protects both the outer dict and inner value dicts
        # Full deepcopy is unnecessary — inner values contain only strings/ints
        self._posture   = {k: dict(v) for k, v in posture.items()} if posture else {}

        self._handlers: dict[str, Callable] = {
            "POSTURE_STATUS":     self._resolve_posture_status,
            "DOCUMENT_STATUS":    self._resolve_document_status,
            "REMEDIATION_GUIDE":  self._resolve_remediation_guide,
            "DOCUMENT_CONTENT":   self._resolve_document_content,
            "STANDARD_KNOWLEDGE": self._resolve_standard_knowledge,
            "CROSS_FRAMEWORK":    self._resolve_cross_framework,
            "EVIDENCE_CHECK":     self._resolve_evidence_check,
            "ASSESSMENT":         self._resolve_assessment,
            "EVENT_RESPONSE":     self._resolve_event_response,
        }

    # --- shared retrieval helper ---

    def _retrieve_and_expand(
        self,
        req:            ResolveRequest,
        entry:          "TaxonomyEntry" = None,
        n_vector:       int = 10,
        n_expand:       int = 8,
        extra_node_ids: list = None,
    ) -> tuple:
        """
        Shared retrieval pattern used by most handlers.
        When entry is provided, uses its retrieval policy (vector_n, expand_n).
        Falls back to n_vector / n_expand for callers that pre-date the policy.

        Returns: (GraphResult, vector_results, neo4j_ms, vector_ms, node_ids_count)
        """
        # Policy-driven sizes override explicit args when entry is provided
        if entry is not None:
            n_vector = entry.vector_n if entry.vector_n > 0 else n_vector
            n_expand = entry.expand_n if entry.expand_n > 0 else n_expand

        extra = extra_node_ids or []

        # Vector retrieval — skipped if policy says use_vector=False
        if entry is None or entry.use_vector:
            vector_t0 = time.time()
            v_results = self._retriever.search(req.query, n=n_vector, standards=req.standards)
            vector_ms = int((time.time() - vector_t0) * 1000)
            vector_ids = [
                r.node_id for r in v_results.results[:n_expand]
                if r.node_id not in extra
            ]
        else:
            v_results  = type("V", (), {"results": []})()
            vector_ms  = 0
            vector_ids = []

        node_ids = extra + vector_ids

        # Graph expansion — skipped if policy says use_graph=False
        if entry is None or entry.use_graph:
            neo4j_t0 = time.time()
            gr       = self._expand(node_ids, req)
            neo4j_ms = int((time.time() - neo4j_t0) * 1000)
        else:
            gr       = GraphResult.empty()
            neo4j_ms = 0

        gr.node_ids_input    = len(node_ids)
        gr.posture_ids_used  = list(extra)   # the posture NC/OFI ids we passed in
        gr.vector_top_scores = [
            (r.node_id, round(float(r.score), 3))
            for r in (v_results.results[:3] if hasattr(v_results, "results") else [])
            if hasattr(r, "score")
        ]
        return gr, v_results.results, neo4j_ms, vector_ms, len(node_ids)

    # --- dispatch ---

    def resolve(self, request: ResolveRequest) -> ResolvedContext:
        t0      = time.time()
        entry   = get_taxonomy_type(request.classifier_type)
        handler = self._handlers.get(entry.type_id, self._resolve_default)

        posture = self._posture if entry.use_posture else {}
        # Resolve tenant_id — prefer explicit field, fall back to tenant_context
        _tenant_id = request.tenant_id or getattr(
            request.tenant_context, "tenant_id", ""
        ) or ""

        # Strategy label: describes the retrieval pattern this query will use
        _strategy_parts = []
        if entry.use_posture:   _strategy_parts.append("posture")
        if entry.use_vector:    _strategy_parts.append("vector")
        if entry.use_graph:     _strategy_parts.append("graph")
        if entry.use_doc_inventory: _strategy_parts.append("doc_inventory")
        if entry.allow_short_circuit: _strategy_parts.append("short_circuit")
        _strategy = "+".join(_strategy_parts) or "none"

        trace   = ResolverTrace(
            request_id           = request.request_id,
            tenant_id            = str(_tenant_id),
            query                = request.query,
            classifier_type      = request.classifier_type,
            taxonomy_type        = entry.type_id,
            handler_name         = handler.__name__,
            strategy             = _strategy,
            posture_total        = len(posture),
            posture_nc           = sum(1 for v in posture.values() if v.get("finding") == "NC"),
            posture_ofi          = sum(1 for v in posture.values() if v.get("finding") == "OFI"),
            posture_na           = sum(1 for v in posture.values() if v.get("finding") == "N/A"),
            # Snapshot the retrieval policy declared in taxonomy
            policy_posture       = entry.use_posture,
            policy_vector        = entry.use_vector,
            policy_graph         = entry.use_graph,
            policy_doc_inv       = entry.use_doc_inventory,
            policy_short_circuit = entry.allow_short_circuit,
        )

        try:
            # ── Short-circuit: policy says no LLM needed ──────────────────
            if entry.allow_short_circuit and entry.type_id == "DOCUMENT_STATUS":
                # DOCUMENT_STATUS is the only current short-circuit type.
                # When more types are added, the pattern extends here.
                pass  # handler itself returns short_circuit_answer

            result = handler(request, entry)
            gn = result.graph_nodes
            trace.nodes_primary   = len(gn.primary_nodes)
            trace.nodes_secondary = len(gn.secondary_nodes)

            # Granularity: which posture nodes were used + top vector scores
            trace.posture_ids_used   = gn.posture_ids_used
            trace.vector_top_scores  = gn.vector_top_scores

            # Count confirmed vs draft posture findings — used by assembler for LLM prompt
            posture = result.posture_nodes or {}
            result.posture_confirmed = sum(
                1 for v in posture.values()
                if v.get("confirmation_status") in ("confirmed", "overridden")
            )
            result.posture_draft = sum(
                1 for v in posture.values()
                if v.get("confirmation_status") == "draft"
                or v.get("confirmation_status") is None  # legacy rows
            )
            trace.posture_confirmed = result.posture_confirmed
            trace.posture_draft     = result.posture_draft

            # node_ids_built = true input count, stored on GraphResult by _retrieve_and_expand
            # Handlers that bypass the helper set gr.node_ids_input directly
            trace.node_ids_built  = gn.node_ids_input if gn.node_ids_input > 0                                     else trace.nodes_primary + trace.nodes_secondary
            trace.doc_contexts    = len(gn.doc_contexts)
            trace.vector_results  = len(result.vector_nodes or [])
            trace.short_circuit   = result.has_short_circuit
            trace.answer_source   = result.answer_source
            trace.neo4j_ms        = result.neo4j_ms
            trace.vector_ms       = result.vector_ms
            trace.postgres_ms     = result.postgres_ms

        except Exception as exc:
            tb_lines   = _tb.format_exc().splitlines()
            call_lines = [
                l.strip() for l in tb_lines
                if any(k in l for k in ("get_document", "expand", "search", "retriever"))
            ]
            trace.error      = f"{type(exc).__name__}: {exc}"
            trace.error_call = call_lines[-1] if call_lines else tb_lines[-2].strip()
            trace.error_hint = _build_error_hint(exc, trace.error_call)
            result = _empty_context(entry)
            result.trace = trace
            trace.total_ms = round((time.time() - t0) * 1000)
            logger.error(
                f"[resolver] handler={handler.__name__} FAILED\n"
                f"  error: {trace.error}\n"
                f"  call:  {trace.error_call}\n"
                f"  hint:  {trace.error_hint}"
            )
            # Return empty context with trace — caller (arion_graph.py) handles errors
            # Re-raising here discards the trace; returning preserves observability
            return result

        trace.total_ms = round((time.time() - t0) * 1000)
        result.trace   = trace
        logger.info(f"[resolver] {trace.summary_line()}")
        return result

    # --- Tier 1: DB-first ---

    def _resolve_document_status(self, req, entry):
        alerts = req.tenant_context.document_alerts or []
        answer = _build_document_status_answer(req.query, alerts)
        return ResolvedContext(
            taxonomy_type        = "DOCUMENT_STATUS",
            taxonomy_entry       = entry,
            posture_nodes        = {},
            graph_nodes          = GraphResult.empty(),
            vector_nodes         = [],
            document_alerts      = alerts,
            short_circuit_answer = answer,
            answer_source        = "postgres",
        )

    # --- Tier 2: Posture-first ---

    def _resolve_posture_status(self, req, entry):
        posture          = _filter_posture(self._posture, req.topic_ref)
        posture_node_ids = _posture_nc_ofi_ids(self._posture, req.topic_ref)
        gr, v_nodes, neo4j_ms, vector_ms, _nids = self._retrieve_and_expand(
            req, entry=entry, extra_node_ids=posture_node_ids
        )
        return ResolvedContext(
            taxonomy_type   = "POSTURE_STATUS",
            taxonomy_entry  = entry,
            posture_nodes   = posture,
            graph_nodes     = gr,
            vector_nodes    = v_nodes,
            document_alerts = req.tenant_context.document_alerts or [],
            neo4j_ms        = neo4j_ms,
            vector_ms       = vector_ms,
        )

    # --- Tier 3: LLM synthesis ---

    def _resolve_remediation_guide(self, req, entry):
        posture          = _filter_posture(self._posture, req.topic_ref)
        posture_node_ids = _posture_nc_ofi_ids(self._posture, req.topic_ref)
        gr, v_nodes, neo4j_ms, vector_ms, _ = self._retrieve_and_expand(
            req, entry=entry, extra_node_ids=posture_node_ids
        )
        # Doc inventory: appended after expand — topic-specific checklist
        if req.topic_ref and self._is_expander_online():
            _merge_doc_inv(gr, self._expander.get_document_inventory(
                tenant_id = req.tenant_context.tenant_id,
                standards = req.standards,
                topic_ref = req.topic_ref,
            ))
        self._enrich_doc_contexts(gr.doc_contexts)
        return ResolvedContext(
            taxonomy_type   = "REMEDIATION_GUIDE",
            taxonomy_entry  = entry,
            posture_nodes   = posture,
            graph_nodes     = gr,
            vector_nodes    = v_nodes,
            document_alerts = req.tenant_context.document_alerts or [],
            neo4j_ms        = neo4j_ms,
            vector_ms       = vector_ms,
        )

    def _resolve_document_content(self, req, entry):
        posture          = _filter_posture(self._posture, req.topic_ref)
        posture_node_ids = _posture_nc_ofi_ids(self._posture, req.topic_ref)

        neo4j_t0 = time.time()
        gr = GraphResult.empty()

        if self._is_expander_online():
            doc_inv = self._expander.get_document_inventory(
                tenant_id = req.tenant_context.tenant_id,
                standards = req.standards,
                topic_ref = req.topic_ref,
            )
            _merge_doc_inv(gr, doc_inv)

        neo4j_ms = int((time.time() - neo4j_t0) * 1000)

        vector_t0 = time.time()
        v_results = self._retriever.search(req.query, n=10, standards=req.standards)
        vector_ms = int((time.time() - vector_t0) * 1000)

        vector_ids = [r.node_id for r in v_results.results[:6] if r.node_id not in posture_node_ids]
        node_ids   = posture_node_ids + vector_ids

        if node_ids:
            neo4j_t0b = time.time()
            gr2 = self._expand(node_ids, req)
            neo4j_ms += int((time.time() - neo4j_t0b) * 1000)
            gr.primary_nodes   = gr2.primary_nodes
            gr.secondary_nodes = gr2.secondary_nodes
            gr.node_ids_input  = len(node_ids)   # for trace accuracy
            for k, v in gr2.doc_contexts.items():
                if k not in gr.doc_contexts:
                    gr.doc_contexts[k] = v

        self._enrich_doc_contexts(gr.doc_contexts)
        return ResolvedContext(
            taxonomy_type   = "DOCUMENT_CONTENT",
            taxonomy_entry  = entry,
            posture_nodes   = posture,
            graph_nodes     = gr,
            vector_nodes    = v_results.results,
            document_alerts = req.tenant_context.document_alerts or [],
            neo4j_ms        = neo4j_ms,
            vector_ms       = vector_ms,
        )

    def _resolve_standard_knowledge(self, req, entry):
        gr, v_nodes, neo4j_ms, vector_ms, _nids = self._retrieve_and_expand(
            req, entry=entry
        )
        return ResolvedContext(
            taxonomy_type   = "STANDARD_KNOWLEDGE",
            taxonomy_entry  = entry,
            posture_nodes   = {},
            graph_nodes     = gr,
            vector_nodes    = v_nodes,
            document_alerts = [],
            neo4j_ms        = neo4j_ms,
            vector_ms       = vector_ms,
        )

    # --- Tier 4: Cross-cutting ---

    def _resolve_cross_framework(self, req, entry):
        posture_node_ids = _posture_nc_ofi_ids(self._posture)
        gr, v_nodes, neo4j_ms, vector_ms, _nids = self._retrieve_and_expand(
            req, entry=entry, extra_node_ids=posture_node_ids
        )
        return ResolvedContext(
            taxonomy_type   = "CROSS_FRAMEWORK",
            taxonomy_entry  = entry,
            posture_nodes   = self._posture,
            graph_nodes     = gr,
            vector_nodes    = v_nodes,
            document_alerts = req.tenant_context.document_alerts or [],
            neo4j_ms        = neo4j_ms,
            vector_ms       = vector_ms,
        )

    def _resolve_evidence_check(self, req, entry):
        posture          = _filter_posture(self._posture, req.topic_ref)
        posture_node_ids = _posture_nc_ofi_ids(self._posture, req.topic_ref)
        gr, v_nodes, neo4j_ms, vector_ms, _ = self._retrieve_and_expand(
            req, entry=entry, extra_node_ids=posture_node_ids
        )
        if req.topic_ref and self._is_expander_online():
            _merge_doc_inv(gr, self._expander.get_document_inventory(
                tenant_id = req.tenant_context.tenant_id,
                standards = req.standards,
                topic_ref = req.topic_ref,
            ))
        self._enrich_doc_contexts(gr.doc_contexts)
        return ResolvedContext(
            taxonomy_type   = "EVIDENCE_CHECK",
            taxonomy_entry  = entry,
            posture_nodes   = posture,
            graph_nodes     = gr,
            vector_nodes    = v_nodes,
            document_alerts = req.tenant_context.document_alerts or [],
            neo4j_ms        = neo4j_ms,
            vector_ms       = vector_ms,
        )

    def _resolve_assessment(self, req, entry):
        return ResolvedContext(
            taxonomy_type   = "ASSESSMENT",
            taxonomy_entry  = entry,
            posture_nodes   = self._posture,
            graph_nodes     = GraphResult.empty(),
            vector_nodes    = [],
            document_alerts = req.tenant_context.document_alerts or [],
        )

    def _resolve_event_response(self, req, entry):
        gr, v_nodes, neo4j_ms, vector_ms, _nids = self._retrieve_and_expand(
            req, entry=entry
        )
        return ResolvedContext(
            taxonomy_type   = "EVENT_RESPONSE",
            taxonomy_entry  = entry,
            posture_nodes   = {},
            graph_nodes     = gr,
            vector_nodes    = v_nodes,
            document_alerts = [],
            neo4j_ms        = neo4j_ms,
            vector_ms       = vector_ms,
        )

    def _resolve_default(self, req, entry):
        logger.warning(f"No handler for {entry.type_id!r} — using POSTURE_STATUS fallback")
        return self._resolve_posture_status(req, entry)

    # --- _expand: always returns GraphResult, never raises ---

    def _is_expander_online(self) -> bool:
        """Check expander availability. Prefers public is_online(); falls back to _is_online()."""
        for method_name in ("is_online", "_is_online"):
            fn = getattr(self._expander, method_name, None)
            if fn:
                try:
                    return bool(fn())
                except Exception:
                    return False
        return False


    # --- doc context enrichment from posture ---

    def _enrich_doc_contexts(self, doc_contexts: dict) -> dict:
        """
        Enrich DocumentContext checklist items with status/confidence/excerpt
        from self._posture (Postgres posture_controls).
        Neo4j returns status=None — this fills it from confirmed posture data.
        Comply→present, NC/OFI→missing, N/A→not_applicable, None→None.
        """
        if not doc_contexts or not self._posture:
            return doc_contexts

        posture_by_ref = {}
        for node_id, data in self._posture.items():
            ref = data.get('control_ref') or node_id.split(':')[-1]
            if ref:
                posture_by_ref[ref] = data

        _STATUS = {'Comply': 'present', 'NC': 'missing', 'OFI': 'missing', 'N/A': 'not_applicable'}

        for node_id, ctx in doc_contexts.items():
            ref  = getattr(ctx, 'control_ref', None)
            data = posture_by_ref.get(ref, {})
            if not data:
                continue
            status     = _STATUS.get(data.get('finding', ''))
            confidence = data.get('confidence')
            excerpt    = data.get('gap_description') or data.get('evidence_text')
            for item in list(getattr(ctx, 'must_contain', [])) + list(getattr(ctx, 'should_contain', [])):
                if item.status is None:
                    item.status     = status
                    item.confidence = confidence
                    item.excerpt    = excerpt
        return doc_contexts

    def _expand(self, node_ids: list, req: ResolveRequest) -> GraphResult:
        if not node_ids or not self._is_expander_online():
            return GraphResult.empty()
        try:
            from rag.classifier import QueryIntent, QuestionType, QueryDimensions
            entry  = get_taxonomy_type(req.classifier_type)
            _QMAP  = {
                "POSTURE_STATUS":     QuestionType.GAP_ANALYSIS,
                "REMEDIATION_GUIDE":  QuestionType.IMPLEMENTATION,
                "DOCUMENT_CONTENT":   QuestionType.DOCUMENT_CONTENT,
                "DOCUMENT_STATUS":    QuestionType.DOCUMENT_INVENTORY,
                "STANDARD_KNOWLEDGE": QuestionType.DEFINITION,
                "CROSS_FRAMEWORK":    QuestionType.CROSS_FRAMEWORK,
                "EVIDENCE_CHECK":     QuestionType.GAP_ANALYSIS,
                "ASSESSMENT":         QuestionType.FREE_ASSESSMENT,
                "EVENT_RESPONSE":     QuestionType.UNKNOWN,
            }
            qtype  = _QMAP.get(entry.type_id, QuestionType.UNKNOWN)
            intent = QueryIntent(
                question_type      = qtype,
                standards_scope    = req.standards,
                role_filter        = None,
                needs_posture      = entry.needs_posture,
                cited_refs         = [],
                resolved_refs      = [],
                confidence         = 0.8,
                raw_query          = req.query,
                dimensions         = QueryDimensions(
                    needs_obligation    = False,
                    needs_posture       = entry.needs_posture,
                    needs_documentation = entry.needs_graph,
                ),
                detected_events    = [],
                document_topic_ref = req.topic_ref,
            )
            return GraphResult.from_expanded(self._expander.expand(node_ids, intent))
        except Exception as exc:
            logger.warning(f"_expand failed ({len(node_ids)} nodes): {exc}")
            return GraphResult.empty()
