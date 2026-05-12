"""
GraphExpander — ArionComply RAG Orchestration

Takes node IDs from vector search and expands them through Neo4j:
  - Vertical: PART_OF up to article root + one level down to children
  - Cross-framework: IMPLEMENTS/SUPPORTS/ENABLES/GOVERNANCE edges
  - Lateral: RELATED_TO one hop

After traversal, fetches full enriched content from ChromaDB
(not Neo4j) — so Tier 1 business descriptions and keywords are
always included without needing to re-ingest into the graph.

Design: Option C
  Neo4j  → graph structure only (IDs, relationships, traversal)
  ChromaDB → full node content (obligation text, enrichment, gaps)

Connection:
  URI  = "bolt://localhost:7687"  (local Neo4j Desktop)
  or   = "neo4j+s://xxxxx.databases.neo4j.io"  (AuraDB)

Offline mode: if Neo4j is unavailable, falls back to
  vector-result-only expansion (no graph traversal).
  Useful for development / CI without a live Neo4j instance.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Optional

from rag.classifier import QueryIntent, QuestionType


# ── Output data classes ────────────────────────────────────────────────────────

@dataclass
class CrossFrameworkEdge:
    source_id:  str
    target_id:  str
    rel_type:   str     # IMPLEMENTS, SUPPORTS, ENABLES, GOVERNANCE
    direction:  str     # "out" (source→target) or "in" (target→source)
    confidence: str     # HIGH, MEDIUM, LOW


@dataclass
class ExpandedNode:
    """
    A node returned by GraphExpander.
    Content is fetched from ChromaDB — not Neo4j.
    """
    node_id:       str
    ref:           str
    standard_id:   str
    title:         str
    document:      str           # full ChromaDB vector document (enriched)
    metadata:      dict          # ChromaDB metadata
    # How this node was discovered
    source:        str           # "cited" | "parent" | "child" | "xfw" | "lateral" | "vector"
    xfw_edges:     list[CrossFrameworkEdge] = field(default_factory=list)

    @property
    def is_gdpr(self) -> bool:
        return self.standard_id == "GDPR:2016/679"

    @property
    def is_iso(self) -> bool:
        return "ISO27001" in self.standard_id

    @property
    def obligation_type(self) -> str:
        return self.metadata.get("obligation_type", "")

    @property
    def is_informational(self) -> bool:
        return self.metadata.get("is_informational", False)

    @property
    def has_gaps(self) -> bool:
        return self.metadata.get("has_gaps", False)

    @property
    def has_evidence(self) -> bool:
        return self.metadata.get("has_evidence", False)

    @property
    def chapter(self) -> str:
        return self.metadata.get("chapter", "")


@dataclass
class ExpandedContext:
    """
    Full expansion result from GraphExpander.
    Structured for direct consumption by ContextAssembler.
    """
    # Primary nodes — always include in full in the LLM context
    # (cited refs + their direct parents)
    primary_nodes:   list[ExpandedNode]

    # Secondary nodes — important context, may be compressed
    # (children, cross-framework, lateral)
    secondary_nodes: list[ExpandedNode]

    # Cross-framework relationship map
    xfw_edges:       list[CrossFrameworkEdge]

    # Convenience accessors
    @property
    def all_nodes(self) -> list[ExpandedNode]:
        return self.primary_nodes + self.secondary_nodes

    @property
    def all_node_ids(self) -> list[str]:
        return [n.node_id for n in self.all_nodes]

    @property
    def gdpr_nodes(self) -> list[ExpandedNode]:
        return [n for n in self.all_nodes if n.is_gdpr]

    @property
    def iso_nodes(self) -> list[ExpandedNode]:
        return [n for n in self.all_nodes if n.is_iso]

    @property
    def node_map(self) -> dict[str, ExpandedNode]:
        return {n.node_id: n for n in self.all_nodes}

    # Stats
    total_nodes:     int = 0
    traversal_stats: dict = field(default_factory=dict)
    offline_mode:    bool = False   # True if Neo4j was unavailable


@dataclass
class ChecklistItemResult:
    """One checklist item with its evaluation status for this tenant."""
    item_id:      str
    text:         str
    category:     str           # "must" | "should"
    gdpr_required: bool
    rationale:    str
    # Evaluation status — None if no document uploaded
    status:       str | None    # "present" | "missing" | "partial" | None
    confidence:   str | None    # "high" | "medium" | "low" | None
    excerpt:      str | None    # relevant quote from document
    section:      str | None
    page:         int | None
    document_name: str | None


@dataclass
class DocumentContext:
    """
    Document requirement context for one control.
    Fetched from Neo4j when intent.dimensions.needs_documentation is True.
    """
    control_ref:    str
    node_id:        str
    document_title: str
    document_type:  str
    trigger_type:   str         # "universal" | "profile_fact" | "operational"
    description:    str
    must_contain:   list[ChecklistItemResult]
    should_contain: list[ChecklistItemResult]

    @property
    def missing_must(self) -> list[ChecklistItemResult]:
        return [i for i in self.must_contain
                if i.status in (None, "missing")]

    @property
    def present_must(self) -> list[ChecklistItemResult]:
        return [i for i in self.must_contain if i.status == "present"]

    @property
    def gdpr_gaps(self) -> list[ChecklistItemResult]:
        return [i for i in self.must_contain
                if i.gdpr_required and i.status in (None, "missing")]

    @property
    def has_document_uploaded(self) -> bool:
        return any(i.status is not None for i in self.must_contain)

    @property
    def completeness_pct(self) -> float | None:
        if not self.has_document_uploaded:
            return None
        assessed = [i for i in self.must_contain if i.status is not None]
        if not assessed:
            return None
        present = sum(1 for i in assessed if i.status == "present")
        return round(present / len(assessed) * 100, 1)


@dataclass
class IncidentObligationContext:
    """Controls triggered by an open incident."""
    incident_id:    str
    incident_type:  str
    title:          str
    severity:       str
    deadline_at:    str | None
    urgency:        str         # "overdue"|"critical"|"urgent"|"soon"|"on_track"
    triggered_node_ids: list[str]
    required_documents: list[str]   # DocumentRequirement ids


# ── Node budget per question type ─────────────────────────────────────────────


NODE_BUDGET: dict[QuestionType, int] = {
    QuestionType.DEFINITION:          12,
    QuestionType.IMPLEMENTATION:      15,
    QuestionType.GAP_ANALYSIS:        22,
    QuestionType.POSTURE_CHECK:       20,
    QuestionType.CROSS_FRAMEWORK:     18,
    QuestionType.FREE_ASSESSMENT:     22,
    QuestionType.DOCUMENT_INVENTORY:   8,   # structured query — fewer nodes needed
    QuestionType.DOCUMENT_CONTENT:    14,   # increased for xfw coverage
    QuestionType.UNKNOWN:             12,
}


# ── Cypher queries ─────────────────────────────────────────────────────────────

# Walk PART_OF hierarchy: up to root + down one level
CYPHER_HIERARCHY = """
UNWIND $node_ids AS nid
MATCH (n:RequirementNode {id: nid})

// Walk up to article root (max 5 hops covers Art.32.1.a → Art.32)
OPTIONAL MATCH (n)-[:PART_OF*1..5]->(ancestor:RequirementNode)

// Walk down one level — immediate children only
OPTIONAL MATCH (child:RequirementNode)-[:PART_OF]->(n)

// Lateral related obligations — one hop
OPTIONAL MATCH (n)-[:RELATED_TO]-(lateral:RequirementNode)

RETURN n.id                          AS source_id,
       collect(DISTINCT ancestor.id) AS ancestor_ids,
       collect(DISTINCT child.id)    AS child_ids,
       collect(DISTINCT lateral.id)  AS lateral_ids
"""

# Cross-framework edges (both directions)
CYPHER_CROSS_FRAMEWORK = """
UNWIND $node_ids AS nid
MATCH (n:RequirementNode {id: nid})

// Outbound: GDPR → ISO (e.g. Art.32.1.a IMPLEMENTS A.8.24)
OPTIONAL MATCH (n)-[r_out:IMPLEMENTS|SUPPORTS|ENABLES|GOVERNANCE]->
               (xfw_out:RequirementNode)

// Inbound: ISO → GDPR (reverse — any standard pointing to n)
OPTIONAL MATCH (n)<-[r_in:IMPLEMENTS|SUPPORTS|ENABLES]-
               (xfw_in:RequirementNode)

RETURN n.id AS source_id,
       collect(DISTINCT {
           id:         xfw_out.id,
           rel:        type(r_out),
           confidence: r_out.confidence
       }) AS outbound,
       collect(DISTINCT {
           id:         xfw_in.id,
           rel:        type(r_in),
           confidence: r_in.confidence
       }) AS inbound
"""

# Fetch node refs and standard_ids for a list of IDs
# (used to filter out informational nodes before ChromaDB fetch)
CYPHER_NODE_META = """
UNWIND $node_ids AS nid
MATCH (n:RequirementNode {id: nid})
RETURN n.id            AS id,
       n.ref           AS ref,
       n.standard_id   AS standard_id,
       n.obligation_type AS obligation_type,
       n.title         AS title
"""


# ── GraphExpander ──────────────────────────────────────────────────────────────

class GraphExpander:
    """
    Expands vector search results through the Neo4j knowledge graph,
    then fetches full enriched content from ChromaDB.

    Usage:
        expander = GraphExpander(
            neo4j_uri      = "bolt://localhost:7687",
            neo4j_user     = "neo4j",
            neo4j_password = "...",
            retriever      = vector_retriever,
        )

        context = expander.expand(
            node_ids = ["GDPR:2016/679:Art.32.1.a", "ISO27001:2022:A.8.24"],
            intent   = query_intent,
        )
    """

    def __init__(
        self,
        neo4j_uri:      str,
        neo4j_user:     str,
        neo4j_password: str,
        retriever,                  # VectorRetriever — for ChromaDB content
        connection_timeout: int = 5,
    ):
        self._uri      = neo4j_uri
        self._auth     = (neo4j_user, neo4j_password)
        self._retriever = retriever
        self._timeout  = connection_timeout
        self._driver   = None
        self._online   = None       # None = not yet tested

    # ── Public API ─────────────────────────────────────────────────────────

    def expand(
        self,
        node_ids: list[str],
        intent:   QueryIntent,
    ) -> ExpandedContext:
        """
        Expand a list of node IDs through the graph and return
        fully enriched ExpandedContext.

        Falls back to vector-only expansion if Neo4j is unavailable.
        """
        if not node_ids:
            return self._empty_context()

        budget = NODE_BUDGET.get(intent.question_type, 15)

        # Try graph expansion
        if self._is_online():
            return self._graph_expand(node_ids, intent, budget)
        else:
            print("  ⚠ Neo4j offline — using vector-only expansion")
            return self._vector_only_expand(node_ids, intent, budget)

    def test_connection(self) -> bool:
        """Test Neo4j connectivity. Returns True if connected."""
        return self._is_online()

    def close(self) -> None:
        """Close the Neo4j driver."""
        if self._driver:
            try:
                self._driver.close()
            except Exception:
                pass
            self._driver = None

    # ── Graph expansion ────────────────────────────────────────────────────

    def _graph_expand(
        self,
        node_ids: list[str],
        intent:   QueryIntent,
        budget:   int,
    ) -> ExpandedContext:
        """Full graph traversal + ChromaDB content fetch."""
        t0    = time.time()
        stats = {"cited": 0, "parents": 0, "children": 0,
                 "xfw": 0, "lateral": 0}

        driver = self._get_driver()

        with driver.session() as session:
            # ── Step 1: Hierarchy traversal ──────────────────────────────
            hier_result = session.run(CYPHER_HIERARCHY, node_ids=node_ids)

            parent_ids  = set()
            child_ids   = set()
            lateral_ids = set()

            for record in hier_result:
                parent_ids.update(
                    [i for i in record["ancestor_ids"] if i]
                )
                child_ids.update(
                    [i for i in record["child_ids"] if i]
                )
                lateral_ids.update(
                    [i for i in record["lateral_ids"] if i]
                )

            # ── Step 2: Cross-framework traversal ────────────────────────
            xfw_result = session.run(
                CYPHER_CROSS_FRAMEWORK, node_ids=node_ids
            )

            xfw_node_ids = set()
            xfw_edges    = []

            for record in xfw_result:
                source = record["source_id"]
                for item in record["outbound"]:
                    tid = item.get("id")
                    if tid:
                        xfw_node_ids.add(tid)
                        xfw_edges.append(CrossFrameworkEdge(
                            source_id  = source,
                            target_id  = tid,
                            rel_type   = item.get("rel", "IMPLEMENTS"),
                            direction  = "out",
                            confidence = item.get("confidence", "MEDIUM") or "MEDIUM",
                        ))
                for item in record["inbound"]:
                    tid = item.get("id")
                    if tid:
                        xfw_node_ids.add(tid)
                        xfw_edges.append(CrossFrameworkEdge(
                            source_id  = tid,
                            target_id  = source,
                            rel_type   = item.get("rel", "IMPLEMENTS"),
                            direction  = "in",
                            confidence = item.get("confidence", "MEDIUM") or "MEDIUM",
                        ))

        elapsed = time.time() - t0

        # ── Step 3: Prioritise and budget ─────────────────────────────────
        cited_set   = set(node_ids)
        all_ids     = self._prioritise(
            cited   = cited_set,
            parents = parent_ids - cited_set,
            xfw     = xfw_node_ids - cited_set - parent_ids,
            children = child_ids - cited_set - parent_ids - xfw_node_ids,
            lateral  = lateral_ids - cited_set - parent_ids - xfw_node_ids - child_ids,
            intent  = intent,
            budget  = budget,
        )

        stats["cited"]    = len(cited_set)
        stats["parents"]  = len(parent_ids)
        stats["xfw"]      = len(xfw_node_ids)
        stats["children"] = len(child_ids)
        stats["lateral"]  = len(lateral_ids)
        stats["neo4j_ms"] = round((elapsed) * 1000)

        # ── Step 4: Fetch content from ChromaDB ───────────────────────────
        primary_ids   = list(cited_set | parent_ids)
        secondary_ids = [i for i in all_ids if i not in set(primary_ids)]

        primary_nodes   = self._fetch_from_chroma(
            primary_ids, xfw_edges, cited_set, parent_ids
        )
        secondary_nodes = self._fetch_from_chroma(
            secondary_ids, xfw_edges, cited_set, parent_ids
        )

        total = len(primary_nodes) + len(secondary_nodes)
        return ExpandedContext(
            primary_nodes   = primary_nodes,
            secondary_nodes = secondary_nodes,
            xfw_edges       = xfw_edges,
            total_nodes     = total,
            traversal_stats = stats,
            offline_mode    = False,
        )

    def _vector_only_expand(
        self,
        node_ids: list[str],
        intent:   QueryIntent,
        budget:   int,
    ) -> ExpandedContext:
        """
        Fallback expansion when Neo4j is unavailable.
        Fetches content for the given node IDs from ChromaDB only.
        No graph traversal — no parents, children, or cross-framework.
        """
        nodes = self._fetch_from_chroma(
            node_ids[:budget], [], set(node_ids), set()
        )
        return ExpandedContext(
            primary_nodes   = nodes,
            secondary_nodes = [],
            xfw_edges       = [],
            total_nodes     = len(nodes),
            traversal_stats = {"mode": "vector_only"},
            offline_mode    = True,
        )

    # ── Prioritisation ─────────────────────────────────────────────────────

    def _prioritise(
        self,
        cited:    set[str],
        parents:  set[str],
        xfw:      set[str],
        children: set[str],
        lateral:  set[str],
        intent:   QueryIntent,
        budget:   int,
    ) -> list[str]:
        """
        Select which node IDs to include within budget.
        Priority varies by question type.
        """
        result  = list(cited)     # cited always included
        budget -= len(result)

        # Priority order depends on question type
        if intent.question_type in (
            QuestionType.GAP_ANALYSIS,
            QuestionType.POSTURE_CHECK,
        ):
            # Cross-framework first — need ISO controls for posture lookup
            order = [parents, xfw, children, lateral]
        elif intent.question_type == QuestionType.CROSS_FRAMEWORK:
            order = [xfw, parents, lateral, children]
        elif intent.question_type == QuestionType.DEFINITION:
            order = [parents, lateral, children, xfw]
        elif intent.question_type == QuestionType.IMPLEMENTATION:
            order = [parents, xfw, children, lateral]
        else:
            order = [parents, xfw, children, lateral]

        for group in order:
            if budget <= 0:
                break
            take     = list(group)[:budget]
            result  += take
            budget  -= len(take)

        return result

    # ── ChromaDB content fetch ─────────────────────────────────────────────

    def _fetch_from_chroma(
        self,
        node_ids:  list[str],
        xfw_edges: list[CrossFrameworkEdge],
        cited_set: set[str],
        parent_set: set[str],
    ) -> list[ExpandedNode]:
        """
        Fetch full enriched node content from ChromaDB by node ID.
        Skips informational nodes (no compliance value).
        Attaches relevant cross-framework edges to each node.
        """
        if not node_ids:
            return []

        # Build edge lookup: node_id → [edges]
        edge_map: dict[str, list[CrossFrameworkEdge]] = {}
        for e in xfw_edges:
            edge_map.setdefault(e.source_id, []).append(e)
            edge_map.setdefault(e.target_id, []).append(e)

        # Fetch from ChromaDB
        results = self._retriever.search_by_ids(node_ids)

        expanded = []
        for r in results:
            # Skip informational nodes — they add no compliance value
            if r.is_informational:
                continue

            # Determine how this node was discovered
            if r.node_id in cited_set:
                source = "cited"
            elif r.node_id in parent_set:
                source = "parent"
            else:
                source = "xfw"   # or child/lateral — all treated as secondary

            expanded.append(ExpandedNode(
                node_id    = r.node_id,
                ref        = r.ref,
                standard_id = r.standard_id,
                title      = r.title,
                document   = r.document,
                metadata   = r.metadata,
                source     = source,
                xfw_edges  = edge_map.get(r.node_id, []),
            ))

        # Preserve priority order from node_ids
        id_order = {nid: i for i, nid in enumerate(node_ids)}
        expanded.sort(key=lambda x: id_order.get(x.node_id, 999))
        return expanded

    # ── Connection management ──────────────────────────────────────────────


    def get_implied_controls(
        self,
        facts:     "ClientFacts",
        standards: list[str],
    ) -> list[str]:
        """
        Query Neo4j for mandatory controls implied by client facts.
        Returns list of node_ids that are legally required for this client.

        Deterministic — not probabilistic retrieval.
        A control returned here cannot be missed by vector search scoring.

        Falls back to Python-computed implied controls if Neo4j is offline.
        """
        from enrichment.obligations.obligation_rules import get_implied_controls
        from enrichment.obligations.client_facts     import ClientFacts as CF

        # Python fallback — works offline, same logic as Neo4j graph
        implied_py = get_implied_controls(facts)
        implied_ids = [
            item["control_id"]
            for item in implied_py
            if any(item["control_id"].startswith(s) for s in standards)
        ]

        if not self._is_online():
            return implied_ids

        # Neo4j path — same result but validates against actual graph
        # Only returns node_ids that exist as RequirementNodes in Neo4j
        try:
            driver = self._get_driver()
            with driver.session() as session:
                # Build fact flags from ClientFacts
                active_facts = facts.active_flags()

                result = session.run("""
                    UNWIND $active_facts AS fact_name
                    MATCH (f:ClientFact {fact: fact_name})
                          -[:TRIGGERS]->(rule:ObligationRule)
                          -[:REQUIRES_CONTROL {mandatory: true}]->(n:RequirementNode)
                    WHERE n.standard_id IN $standards
                    RETURN DISTINCT n.id AS node_id,
                                   rule.id AS rule_id,
                                   rule.rationale AS rationale
                    ORDER BY n.id
                """, active_facts=active_facts, standards=standards)

                neo4j_ids = [r["node_id"] for r in result]

                if neo4j_ids:
                    return neo4j_ids
                else:
                    # Graph is online but returned nothing — use Python fallback
                    # (may happen if obligation graph not yet loaded)
                    return implied_ids

        except Exception as e:
            # Any Neo4j error — fall back to Python computation
            return implied_ids

    # ── Phase 3: Document + Incident retrieval methods ──────────────────────────

    def get_document_requirements(
        self,
        node_ids:  list[str],
        tenant_id: str,
        standards: list[str],
    ) -> dict[str, "DocumentContext"]:
        """
        Fetch DocumentRequirement + ChecklistItems for a set of control node_ids.
        Returns: {node_id: DocumentContext} with status=None on all items.
        Status enrichment (present/missing) is done by the resolver using
        posture_controls data — not here.  Neo4j stays generic.
        """
        if not node_ids or not self._is_online():
            return {}

        try:
            driver = self._get_driver()
            with driver.session() as s:
                result = s.run("""
                    UNWIND $node_ids AS nid
                    MATCH (n:RequirementNode {id: nid})
                          -[:REQUIRES_DOCUMENT]->(req:DocumentRequirement)
                          -[rel:MUST_CONTAIN|SHOULD_CONTAIN]->(item:ChecklistItem)
                    RETURN
                        n.id                AS node_id,
                        n.ref               AS control_ref,
                        req.id              AS req_id,
                        req.document_title  AS document_title,
                        req.document_type   AS document_type,
                        req.trigger_type    AS trigger_type,
                        req.description     AS description,
                        item.id             AS item_id,
                        item.text           AS item_text,
                        type(rel)           AS category_rel,
                        item.gdpr_aligned   AS gdpr_required,
                        item.rationale      AS rationale
                    ORDER BY req.trigger_type, n.ref,
                             item.gdpr_aligned DESC, item.text
                """, node_ids=node_ids)

                contexts: dict[str, DocumentContext] = {}
                for row in result:
                    nid = row["node_id"]
                    if nid not in contexts:
                        contexts[nid] = DocumentContext(
                            control_ref    = row["control_ref"],
                            node_id        = nid,
                            document_title = row["document_title"],
                            document_type  = row["document_type"],
                            trigger_type   = row["trigger_type"],
                            description    = row["description"],
                            must_contain   = [],
                            should_contain = [],
                        )
                    ctx  = contexts[nid]
                    item = ChecklistItemResult(
                        item_id       = row["item_id"],
                        text          = row["item_text"],
                        category      = "must" if row["category_rel"] == "MUST_CONTAIN"
                                        else "should",
                        gdpr_required = bool(row["gdpr_required"]),
                        rationale     = row["rationale"] or "",
                        status        = None,   # enriched by resolver from posture_controls
                        confidence    = None,
                        excerpt       = None,
                        section       = None,
                        page          = None,
                        document_name = None,
                    )
                    if item.category == "must":
                        ctx.must_contain.append(item)
                    else:
                        ctx.should_contain.append(item)

                return contexts

        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(
                f"get_checklist_items failed: {e}"
            )
            return {}

    def get_document_inventory(
        self,
        tenant_id:   str,
        standards:   list[str],
        topic_ref:   str | None = None,
    ) -> list["DocumentContext"]:
        """
        Return all document requirements for this tenant's applicable standards.
        Used for DOCUMENT_INVENTORY queries: "what documents do we need?"
        Returns DocumentContext objects with status=None — enriched by resolver.
        Neo4j stays generic: no ClientDocument or DETECTED_IN references.
        """
        if not self._is_online():
            return []

        try:
            driver = self._get_driver()
            with driver.session() as s:
                if topic_ref:
                    result = s.run("""
                        MATCH (n:RequirementNode)
                        WHERE n.ref = $topic_ref
                          AND n.standard_id IN $standards
                        MATCH (n)-[:REQUIRES_DOCUMENT]->(req:DocumentRequirement)
                              -[rel:MUST_CONTAIN|SHOULD_CONTAIN]->(item:ChecklistItem)
                        RETURN
                            n.id AS node_id, n.ref AS control_ref,
                            req.id AS req_id, req.document_title AS document_title,
                            req.document_type AS document_type,
                            req.trigger_type AS trigger_type,
                            req.description AS description,
                            item.id AS item_id, item.text AS item_text,
                            type(rel) AS category_rel,
                            item.gdpr_aligned AS gdpr_required,
                            item.rationale AS rationale
                        ORDER BY item.gdpr_aligned DESC, item.text
                    """, topic_ref=topic_ref, standards=standards)
                else:
                    result = s.run("""
                        MATCH (n:RequirementNode)
                        WHERE n.standard_id IN $standards
                        MATCH (n)-[:REQUIRES_DOCUMENT]->(req:DocumentRequirement)
                              -[rel:MUST_CONTAIN|SHOULD_CONTAIN]->(item:ChecklistItem)
                        RETURN
                            n.id AS node_id, n.ref AS control_ref,
                            req.id AS req_id, req.document_title AS document_title,
                            req.document_type AS document_type,
                            req.trigger_type AS trigger_type,
                            req.description AS description,
                            item.id AS item_id, item.text AS item_text,
                            type(rel) AS category_rel,
                            item.gdpr_aligned AS gdpr_required,
                            item.rationale AS rationale
                        ORDER BY n.ref, item.gdpr_aligned DESC, item.text
                    """, standards=standards)

                contexts: dict[str, DocumentContext] = {}
                for row in result:
                    nid = row["node_id"]
                    if nid not in contexts:
                        contexts[nid] = DocumentContext(
                            control_ref    = row["control_ref"],
                            node_id        = nid,
                            document_title = row["document_title"],
                            document_type  = row["document_type"],
                            trigger_type   = row["trigger_type"],
                            description    = row["description"],
                            must_contain   = [],
                            should_contain = [],
                        )
                    ctx  = contexts[nid]
                    item = ChecklistItemResult(
                        item_id       = row["item_id"],
                        text          = row["item_text"],
                        category      = "must" if row["category_rel"] == "MUST_CONTAIN"
                                        else "should",
                        gdpr_required = bool(row["gdpr_required"]),
                        rationale     = row["rationale"] or "",
                        status        = None,   # enriched by resolver
                        confidence    = None,
                        excerpt       = None,
                        section       = None,
                        page          = None,
                        document_name = None,
                    )
                    if item.category == "must":
                        ctx.must_contain.append(item)
                    else:
                        ctx.should_contain.append(item)

                return list(contexts.values())

        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(
                f"get_document_inventory failed: {e}"
            )
            return []


    def get_document_checklist(
        self,
        control_ref:  str,
        tenant_id:    str,
        standard_id:  str | None = None,
        pg_findings:  list | None = None,    # from DocumentPipeline.get_findings_for_control()
    ) -> "DocumentContext | None":
        """
        Return full checklist for one control with evaluation status.
        Used for DOCUMENT_CONTENT queries: "what must our policy contain?"

        pg_findings: confirmed document_findings from Postgres (Postgres only — no Neo4j writes).
                     When provided, checklist items show ✓/✗ status from real evaluations.
        """
        if not self._is_online():
            return None



        try:
            driver = self._get_driver()
            with driver.session() as s:
                where = "n.ref = $ref"
                if standard_id:
                    where += " AND n.standard_id = $standard_id"

                result = s.run("""
                    MATCH (n:RequirementNode)
                    WHERE n.ref = $ref
                    AND ($standard_id = '' OR n.standard_id = $standard_id)
                    MATCH (n)-[:REQUIRES_DOCUMENT]->(req:DocumentRequirement)
                          -[rel:MUST_CONTAIN|SHOULD_CONTAIN]->(item:ChecklistItem)
                    RETURN
                        n.id AS node_id, n.ref AS control_ref,
                        req.document_title AS document_title,
                        req.document_type AS document_type,
                        req.trigger_type AS trigger_type,
                        req.description AS description,
                        item.id AS item_id, item.text AS item_text,
                        type(rel) AS category_rel,
                        item.gdpr_aligned AS gdpr_required,
                        item.rationale AS rationale
                    ORDER BY item.gdpr_aligned DESC, item.text
                """, ref=control_ref, tenant_id=tenant_id,
                     standard_id=standard_id or "")

                ctx = None
                for row in result:
                    if ctx is None:
                        ctx = DocumentContext(
                            control_ref   = row["control_ref"],
                            node_id       = row["node_id"],
                            document_title= row["document_title"],
                            document_type = row["document_type"],
                            trigger_type  = row["trigger_type"],
                            description   = row["description"],
                            must_contain  = [],
                            should_contain= [],
                        )
                    # Merge with Postgres findings if provided
                    pg = {}
                    if pg_findings:
                        pg = {f["checklist_item_id"]: f for f in pg_findings}

                    pg_match = pg.get(row["item_id"], {})
                    item = ChecklistItemResult(
                        item_id      = row["item_id"],
                        text         = row["item_text"],
                        category     = "must" if row["category_rel"] == "MUST_CONTAIN"
                                       else "should",
                        gdpr_required= bool(row["gdpr_required"]),
                        rationale    = row["rationale"] or "",
                        status       = pg_match.get("status"),
                        confidence   = pg_match.get("confidence"),
                        excerpt      = pg_match.get("excerpt"),
                        section      = None,
                        page         = pg_match.get("page"),
                        document_name= pg_match.get("document_name"),
                    )
                    if item.category == "must":
                        ctx.must_contain.append(item)
                    else:
                        ctx.should_contain.append(item)

                return ctx

        except Exception as e:
            return None

    def get_incident_obligations(
        self,
        tenant_id:  str,
        standards:  list[str],
    ) -> list["IncidentObligationContext"]:
        """
        Query Neo4j for open incidents and their triggered obligations.
        Called every retrieve pass — open incidents always add to mandatory pool.

        Reads from Neo4j Incident nodes (synced from Postgres).
        Falls back to empty list if no incidents or Neo4j offline.

        NOTE: Incident nodes are not yet synced to Neo4j — incidents live in
        Postgres only. This method returns empty until the Neo4j sync is built.
        Suppressed to avoid repeated warnings about missing labels.
        """
        if not self._is_online():
            return []

        # Guard: check if Incident label exists before querying
        # Avoids flooding logs with UnknownLabelWarning on every query
        if not getattr(self, '_incident_label_exists', None):
            try:
                driver = self._get_driver()
                with driver.session() as s:
                    r = s.run("CALL db.labels() YIELD label WHERE label='Incident' RETURN count(*) AS n")
                    self._incident_label_exists = r.single()["n"] > 0
            except Exception:
                self._incident_label_exists = False

        if not self._incident_label_exists:
            return []  # Incident nodes not yet in Neo4j — skip silently

        try:
            driver = self._get_driver()
            with driver.session() as s:
                result = s.run("""
                    MATCH (i:Incident {tenant_id: $tenant_id})
                    WHERE i.status IN ['open', 'in_progress']
                    MATCH (i)-[:INSTANCE_OF]->(e:Event)
                          -[:TRIGGERS_OBLIGATION]->(n:RequirementNode)
                    WHERE n.standard_id IN $standards
                    OPTIONAL MATCH (e)-[:REQUIRES_DOCUMENT]->(req:DocumentRequirement)
                    RETURN
                        i.id            AS incident_id,
                        i.incident_type AS incident_type,
                        i.title         AS title,
                        i.severity      AS severity,
                        i.deadline_at   AS deadline_at,
                        i.status        AS status,
                        collect(DISTINCT n.id)   AS triggered_node_ids,
                        collect(DISTINCT req.id) AS required_documents
                    ORDER BY i.severity, i.deadline_at
                """, tenant_id=tenant_id, standards=standards)

                incidents = []
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc)

                for row in result:
                    deadline_at = row["deadline_at"]
                    if deadline_at:
                        try:
                            hours_remaining = (
                                deadline_at.to_native() - now
                            ).total_seconds() / 3600
                            if hours_remaining < 0:
                                urgency = "overdue"
                            elif hours_remaining < 12:
                                urgency = "critical"
                            elif hours_remaining < 48:
                                urgency = "urgent"
                            elif hours_remaining < 168:
                                urgency = "soon"
                            else:
                                urgency = "on_track"
                        except Exception:
                            urgency = "unknown"
                    else:
                        urgency = "no_deadline"

                    incidents.append(IncidentObligationContext(
                        incident_id        = row["incident_id"],
                        incident_type      = row["incident_type"],
                        title              = row["title"] or row["incident_type"],
                        severity           = row["severity"],
                        deadline_at        = str(deadline_at) if deadline_at else None,
                        urgency            = urgency,
                        triggered_node_ids = list(row["triggered_node_ids"]),
                        required_documents = [r for r in row["required_documents"] if r],
                    ))

                return incidents

        except Exception as e:
            return []

    def _is_online(self) -> bool:
        """Check if Neo4j is reachable. Creates persistent driver on success."""
        if self._online is True and self._driver is not None:
            return True
        try:
            from neo4j import GraphDatabase
            # Create and keep the driver — reused by _get_driver()
            driver = GraphDatabase.driver(
                self._uri,
                auth=self._auth,
                connection_timeout=self._timeout,
            )
            with driver.session() as s:
                s.run("RETURN 1").single()
            # Keep driver alive — don't close it
            self._driver = driver
            self._online = True
        except Exception as e:
            self._online = False
            self._driver = None
        return bool(self._online)

    def _get_driver(self):
        """Return active Neo4j driver, connecting if needed."""
        if self._driver is None:
            from neo4j import GraphDatabase
            from neo4j import NotificationDisabledCategory
            try:
                self._driver = GraphDatabase.driver(
                    self._uri,
                    auth=self._auth,
                    notifications_disabled_categories={
                        NotificationDisabledCategory.UNRECOGNIZED
                    },
                )
            except Exception:
                # Older neo4j driver versions don't support notification filtering
                self._driver = GraphDatabase.driver(
                    self._uri, auth=self._auth
                )
        return self._driver

    # ── Helpers ────────────────────────────────────────────────────────────

    def _empty_context(self) -> ExpandedContext:
        return ExpandedContext(
            primary_nodes   = [],
            secondary_nodes = [],
            xfw_edges       = [],
            total_nodes     = 0,
            traversal_stats = {},
        )

    def summary(self, context: ExpandedContext) -> str:
        """Human-readable summary of an ExpandedContext."""
        lines = [
            f"ExpandedContext: {context.total_nodes} nodes "
            f"({'graph' if not context.offline_mode else 'vector-only'})",
            f"  Primary:   {len(context.primary_nodes)} "
            f"(GDPR:{sum(1 for n in context.primary_nodes if n.is_gdpr)} "
            f"ISO:{sum(1 for n in context.primary_nodes if n.is_iso)})",
            f"  Secondary: {len(context.secondary_nodes)} "
            f"(GDPR:{sum(1 for n in context.secondary_nodes if n.is_gdpr)} "
            f"ISO:{sum(1 for n in context.secondary_nodes if n.is_iso)})",
            f"  XFW edges: {len(context.xfw_edges)}",
        ]
        if context.traversal_stats:
            stats = context.traversal_stats
            lines.append(
                f"  Traversal: cited={stats.get('cited',0)} "
                f"parents={stats.get('parents',0)} "
                f"xfw={stats.get('xfw',0)} "
                f"children={stats.get('children',0)} "
                f"lateral={stats.get('lateral',0)} "
                f"({stats.get('neo4j_ms','?')}ms)"
            )
        lines.append("  Nodes:")
        for n in context.all_nodes[:8]:
            lines.append(
                f"    [{n.source:8s}] {n.ref:20s} "
                f"{n.obligation_type:15s} {n.title[:40]}"
            )
        if context.total_nodes > 8:
            lines.append(f"    ... and {context.total_nodes - 8} more")
        return "\n".join(lines)
