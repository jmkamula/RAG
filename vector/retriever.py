"""
VectorRetriever — Semantic search over the ChromaDB knowledge base.

Wraps ChromaDB queries with compliance-aware logic:
  - Standard-scoped search (ISO only, GDPR only, or both)
  - Obligation type filtering (skip informational nodes)
  - Role-based filtering (controller vs processor obligations)
  - Result deduplication and ranking
  - Graph expansion hints (which parent/child nodes to also fetch)

This is the VECTOR half of the hybrid RAG.
The GRAPH half (graph_retriever.py) handles traversal from these results.
"""

from __future__ import annotations
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from vector.indexer import (
    VectorIndexer, COL_ISO, COL_GDPR, COL_ALL,
    AnthropicEmbeddingFunction, FallbackEmbeddingFunction,
)


# ── Result dataclass ───────────────────────────────────────────────────────────

@dataclass
class VectorResult:
    """A single result from a semantic search."""
    node_id:         str
    standard_id:     str
    ref:             str
    title:           str
    document:        str            # the full vector document text
    distance:        float          # cosine distance (lower = more similar)
    score:           float          # 1 - distance (higher = better)
    metadata:        dict = field(default_factory=dict)

    @property
    def is_gdpr(self) -> bool:
        return self.standard_id == "GDPR:2016/679"

    @property
    def is_iso(self) -> bool:
        return self.standard_id == "ISO27001:2022"

    @property
    def obligation_type(self) -> str:
        return self.metadata.get("obligation_type", "")

    @property
    def applies_to(self) -> list[str]:
        raw = self.metadata.get("applies_to", "controller,processor")
        return [r.strip() for r in raw.split(",") if r.strip()]

    @property
    def xfw_ids(self) -> list[str]:
        raw = self.metadata.get("xfw_ids", "")
        return [x.strip() for x in raw.split(",") if x.strip()]

    @property
    def is_informational(self) -> bool:
        return self.metadata.get("is_informational", False)

    def __repr__(self):
        return (f"VectorResult({self.ref}, score={self.score:.3f}, "
                f"type={self.obligation_type})")


@dataclass
class RetrievalContext:
    """
    Full retrieval context assembled for one query.
    Contains vector results from ChromaDB — the graph traversal
    layer will expand these into the full prompt context.
    """
    query:            str
    results:          list[VectorResult]
    standards_scope:  list[str]     # which standards were searched
    role_filter:      Optional[str] # "controller" / "processor" / None
    n_results:        int

    @property
    def iso_results(self) -> list[VectorResult]:
        return [r for r in self.results if r.is_iso]

    @property
    def gdpr_results(self) -> list[VectorResult]:
        return [r for r in self.results if r.is_gdpr]

    @property
    def top_result(self) -> Optional[VectorResult]:
        return self.results[0] if self.results else None

    def node_ids(self) -> list[str]:
        return [r.node_id for r in self.results]

    def summary(self) -> str:
        lines = [
            f"Query:    '{self.query[:60]}'",
            f"Scope:    {self.standards_scope}",
            f"Results:  {len(self.results)} "
            f"(ISO:{len(self.iso_results)} GDPR:{len(self.gdpr_results)})",
        ]
        for r in self.results[:5]:
            lines.append(
                f"  [{r.score:.3f}] {r.ref:20s} {r.obligation_type:15s} {r.title[:50]}"
            )
        return "\n".join(lines)


# ── Retriever ──────────────────────────────────────────────────────────────────

class VectorRetriever:
    """
    Semantic search over the ArionComply knowledge base.

    Usage:
        retriever = VectorRetriever(persist_dir="/path/to/chroma_db")

        # Cross-standard search
        ctx = retriever.search("encryption of personal data at rest")

        # Standard-scoped
        ctx = retriever.search_iso("cryptography policy requirements")
        ctx = retriever.search_gdpr("security of processing")

        # Role-filtered (controller obligations only)
        ctx = retriever.search(
            "data breach notification",
            role="controller",
        )

        # Use the results
        for result in ctx.results:
            print(result.ref, result.score, result.title)
    """

    def __init__(
        self,
        persist_dir:             str  = None,
        provider:                str  = "openai",
        embedding_model:         str  = None,
        use_fallback_embeddings: bool = False,
        skip_informational:      bool = True,
        dimensions:              int  = None,
        chroma_host:             str  = None,
        chroma_port:             int  = 8000,
    ):
        self.skip_informational = skip_informational

        # Re-use the indexer's embed function and chroma client
        self._indexer = VectorIndexer(
            persist_dir             = persist_dir,
            provider                = provider,
            embedding_model         = embedding_model,
            use_fallback_embeddings = use_fallback_embeddings,
            dimensions              = dimensions,
            chroma_host             = chroma_host,
            chroma_port             = chroma_port,
        )

    # ── Public API ─────────────────────────────────────────────────────────

    def search(
        self,
        query:     str,
        n:         int           = 10,
        role:      Optional[str] = None,
        standards: Optional[list[str]] = None,
    ) -> RetrievalContext:
        """
        Cross-standard semantic search.

        Args:
            query:     Natural language query
            n:         Number of results to return
            role:      Filter by applies_to — "controller" or "processor"
            standards: Limit to specific standards e.g. ["ISO27001:2022"]
                       If None, searches all standards.
        """
        collection = self._indexer.get_collection(COL_ALL)
        where      = self._build_where(role, standards)

        raw = self._query(collection, query, n=n * 2, where=where)
        results = self._process_results(raw)
        results = self._post_filter(results, role)
        results = results[:n]

        return RetrievalContext(
            query           = query,
            results         = results,
            standards_scope = standards or ["ISO27001:2022"],
            role_filter     = role,
            n_results       = n,
        )

    def search_iso(
        self,
        query: str,
        n:     int           = 8,
        role:  Optional[str] = None,
    ) -> RetrievalContext:
        """ISO 27001-scoped semantic search."""
        collection = self._indexer.get_collection(COL_ISO)
        where      = self._build_where(role)
        raw        = self._query(collection, query, n=n * 2, where=where)
        results    = self._post_filter(self._process_results(raw), role)[:n]

        return RetrievalContext(
            query           = query,
            results         = results,
            standards_scope = ["ISO27001:2022"],
            role_filter     = role,
            n_results       = n,
        )

    def search_gdpr(
        self,
        query: str,
        n:     int           = 8,
        role:  Optional[str] = None,
    ) -> RetrievalContext:
        """GDPR-scoped semantic search."""
        collection = self._indexer.get_collection(COL_GDPR)
        where      = self._build_where(role)
        raw        = self._query(collection, query, n=n * 2, where=where)
        results    = self._post_filter(self._process_results(raw), role)[:n]

        return RetrievalContext(
            query           = query,
            results         = results,
            standards_scope = ["GDPR:2016/679"],
            role_filter     = role,
            n_results       = n,
        )

    def search_by_ref(self, ref: str) -> Optional[VectorResult]:
        """
        Look up a specific node by its ref (e.g. 'A.8.24' or 'Art.32.1.a').
        Returns None if not found.
        """
        collection = self._indexer.get_collection(COL_ALL)
        try:
            raw = collection.get(
                where     = {"ref": {"$eq": ref}},
                include   = ["documents", "metadatas"],
            )
            if raw["ids"]:
                return self._make_result(
                    raw["ids"][0],
                    raw["documents"][0],
                    0.0,
                    raw["metadatas"][0],
                )
        except Exception:
            pass
        return None

    def search_by_ids(self, node_ids: list[str]) -> list[VectorResult]:
        """Fetch specific nodes by their IDs."""
        if not node_ids:
            return []
        collection = self._indexer.get_collection(COL_ALL)
        try:
            raw = collection.get(
                ids     = node_ids,
                include = ["documents", "metadatas"],
            )
            results = []
            for nid, doc, meta in zip(
                raw["ids"], raw["documents"], raw["metadatas"]
            ):
                results.append(self._make_result(nid, doc, 0.0, meta))
            return results
        except Exception:
            return []

    # ── Internal ───────────────────────────────────────────────────────────

    def _query(
        self,
        collection,
        query:  str,
        n:      int,
        where:  Optional[dict],
    ) -> dict:
        """Execute a ChromaDB query, gracefully handle empty where."""
        kwargs = dict(
            query_texts = [query],
            n_results   = min(n, collection.count() or 1),
            include     = ["documents", "metadatas", "distances"],
        )
        if where:
            kwargs["where"] = where
        return collection.query(**kwargs)

    def _process_results(self, raw: dict) -> list[VectorResult]:
        """Convert ChromaDB query response into VectorResult list."""
        results = []
        if not raw.get("ids") or not raw["ids"][0]:
            return results

        for nid, doc, meta, dist in zip(
            raw["ids"][0],
            raw["documents"][0],
            raw["metadatas"][0],
            raw["distances"][0],
        ):
            results.append(self._make_result(nid, doc, dist, meta))

        return results

    def _make_result(
        self,
        nid:  str,
        doc:  str,
        dist: float,
        meta: dict,
    ) -> VectorResult:
        return VectorResult(
            node_id     = nid,
            standard_id = meta.get("standard_id", ""),
            ref         = meta.get("ref", ""),
            title       = meta.get("title", ""),
            document    = doc,
            distance    = dist,
            score       = max(0.0, 1.0 - dist),
            metadata    = meta,
        )

    def _build_where(
        self,
        role:      Optional[str]       = None,
        standards: Optional[list[str]] = None,
    ) -> Optional[dict]:
        """
        Build a ChromaDB metadata filter dict.
        Returns None if no filtering needed (avoids empty $and errors).
        """
        clauses = []

        if self.skip_informational:
            clauses.append({"is_informational": {"$eq": False}})

        if standards:
            if len(standards) == 1:
                clauses.append({"standard_id": {"$eq": standards[0]}})
            else:
                # ChromaDB $in operator for multiple standards
                clauses.append({"standard_id": {"$in": standards}})

        if not clauses:
            return None
        if len(clauses) == 1:
            return clauses[0]
        return {"$and": clauses}

    def _post_filter(
        self,
        results: list[VectorResult],
        role:    Optional[str],
    ) -> list[VectorResult]:
        """Post-query filter for role (can't always express in ChromaDB where)."""
        if not role:
            return results
        # Include results that apply to "all" or the specified role
        return [
            r for r in results
            if "all" in r.applies_to or role in r.applies_to
        ]
