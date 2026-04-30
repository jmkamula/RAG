"""
VectorIndexer — ChromaDB (dev) vector store for RequirementNodes.

Indexes all 433 nodes (ISO + GDPR) into ChromaDB using Anthropic's
voyage-3 embeddings via the Claude API.

Design decisions:
  - One collection per standard (iso27001_2022, gdpr_2016_679)
    → lets us filter by standard without metadata filtering overhead
  - Plus one combined collection (arioncombly_all)
    → used for cross-standard semantic search

  - Embedding strategy: to_vector_document() output
    → combines obligation_text + intent + evidence + gaps + xfw titles
    → richer than raw obligation text alone
    → cross-framework titles ensure "encryption" finds both
       ISO A.8.24 and GDPR Art.32.1.a

  - Metadata stored per document:
    → node_id, standard_id, ref, title, node_type,
       obligation_type, applies_to, chapter, theme,
       parse_confidence, has_xfw (bool), xfw_count
    → enables metadata filtering without re-embedding

  - Persistent store: ./chroma_db/  (relative to working dir)
    → switch to Qdrant for prod by swapping this module only

Usage:
    from vector.indexer import VectorIndexer
    indexer = VectorIndexer()
    indexer.index_all(iso_nodes, gdpr_nodes)
    # or
    indexer.index_all_from_json(
        iso_json  = "output/iso_phase1/iso_nodes_phase1.json",
        gdpr_json = "output/gdpr_phase2/gdpr_nodes_phase2.json",
    )
"""

from __future__ import annotations
import json
import time
import sys
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.requirement_node import RequirementNode


# ── Collection names ───────────────────────────────────────────────────────────

COL_ISO    = "iso27001_2022"
COL_GDPR   = "gdpr_2016_679"
COL_ALL    = "arioncombly_all"

COLLECTIONS = [COL_ISO, COL_GDPR, COL_ALL]


# ── Embedding functions ────────────────────────────────────────────────────────

class OpenAIEmbeddingFunction:
    """
    ChromaDB-compatible embedding function using OpenAI embeddings API.

    Default model: text-embedding-3-small (1536 dims, ~$0.01 for full index)
    Better model:  text-embedding-3-large (3072 dims, ~$0.04 for full index)

    Requires: OPENAI_API_KEY environment variable
    """

    def __init__(
        self,
        model:      str = "text-embedding-3-small",
        batch_size: int = 100,
        dimensions: int = None,   # None = use model default
    ):
        self.model      = model
        self.batch_size = batch_size
        self.dimensions = dimensions
        self._client    = None

    def name(self) -> str:
        dim_suffix = f"-{self.dimensions}" if self.dimensions else ""
        return f"openai-{self.model}{dim_suffix}"

    def embed_documents(self, input: list[str]) -> list[list[float]]:
        return self(input)

    def embed_query(self, input: list[str]) -> list[list[float]]:
        return self(input)

    def _get_client(self):
        if self._client is None:
            try:
                import openai, os
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise RuntimeError(
                        "OPENAI_API_KEY not set.\n"
                        "  export OPENAI_API_KEY=sk-..."
                    )
                self._client = openai.OpenAI(api_key=api_key)
            except ImportError:
                raise RuntimeError("openai package not installed: pip install openai")
        return self._client

    def __call__(self, input: list[str]) -> list[list[float]]:
        """Embed a batch of texts."""
        client     = self._get_client()
        embeddings = []

        for i in range(0, len(input), self.batch_size):
            batch = input[i:i + self.batch_size]
            # Truncate texts that exceed model token limit
            batch = [t[:8000] for t in batch]
            try:
                kwargs = dict(input=batch, model=self.model)
                if self.dimensions:
                    kwargs["dimensions"] = self.dimensions
                response = client.embeddings.create(**kwargs)
                # Sort by index to preserve batch order
                sorted_data = sorted(response.data, key=lambda x: x.index)
                embeddings.extend([e.embedding for e in sorted_data])
            except Exception as e:
                raise RuntimeError(f"OpenAI embedding API call failed: {e}")

            if i + self.batch_size < len(input):
                time.sleep(0.05)   # light rate-limit buffer

        # ChromaDB 1.x HTTP client requires numpy arrays, not plain lists
        try:
            import numpy as np
            return np.array(embeddings, dtype=float)
        except ImportError:
            return embeddings


class AnthropicEmbeddingFunction:
    """
    ChromaDB-compatible embedding function using Anthropic's voyage-3.
    Requires: ANTHROPIC_API_KEY environment variable
    """

    def __init__(self, model: str = "voyage-3", batch_size: int = 64):
        self.model      = model
        self.batch_size = batch_size
        self._client    = None

    def name(self) -> str:
        return f"anthropic-{self.model}"

    def embed_documents(self, input: list[str]) -> list[list[float]]:
        return self(input)

    def embed_query(self, input: list[str]) -> list[list[float]]:
        return self(input)

    def _get_client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic()
        return self._client

    def __call__(self, input: list[str]) -> list[list[float]]:
        client     = self._get_client()
        embeddings = []
        for i in range(0, len(input), self.batch_size):
            batch = input[i:i + self.batch_size]
            response = client.embeddings.create(model=self.model, input=batch)
            embeddings.extend([e.embedding for e in response.embeddings])
            if i + self.batch_size < len(input):
                time.sleep(0.1)
        try:
            import numpy as np
            return np.array(embeddings, dtype=float)
        except ImportError:
            return embeddings


class FallbackEmbeddingFunction:
    """
    Simple hash-based embedding for testing without an API key.
    NOT suitable for production — vectors are not semantically meaningful.
    Used only for CI / local smoke testing.
    """

    DIM = 256

    def name(self) -> str:
        return "fallback-hash-256"

    def embed_documents(self, input: list[str]) -> list[list[float]]:
        return self(input)

    def embed_query(self, input: list[str]) -> list[list[float]]:
        return self(input)

    def __call__(self, input: list[str]) -> list[list[float]]:
        import hashlib, math
        results = []
        for text in input:
            h = hashlib.sha256(text.encode()).hexdigest()
            # Deterministic pseudo-embedding from hash
            vec = []
            for j in range(0, min(len(h), self.DIM * 2), 2):
                val = int(h[j:j+2], 16) / 255.0 - 0.5
                vec.append(val)
            # Pad or trim to DIM
            while len(vec) < self.DIM:
                vec.append(0.0)
            vec = vec[:self.DIM]
            # L2-normalise
            norm = math.sqrt(sum(v*v for v in vec)) or 1.0
            results.append([v / norm for v in vec])
        return results
        try:
            import numpy as np
            return np.array(results, dtype=float)
        except ImportError:
            return results


# ── Metadata builder ───────────────────────────────────────────────────────────

def _build_metadata(node: RequirementNode) -> dict:
    """
    Extract indexable metadata from a node.
    ChromaDB metadata values must be str, int, float, or bool.
    Lists must be joined to strings.
    """
    applies_str = ",".join(node.applies_to or [])
    xfw_ids     = list(node.cross_framework_summary.keys())

    return {
        "node_id":         node.id,
        "standard_id":     node.standard_id,
        "ref":             node.ref,
        "title":           node.title[:200],          # trim long titles
        "node_type":       str(node.node_type.value if hasattr(node.node_type, 'value') else node.node_type),
        "obligation_type": str(node.obligation_type.value if hasattr(node.obligation_type, 'value') else node.obligation_type),
        "applies_to":      applies_str,
        "chapter":         node.chapter or "",
        "theme":           node.theme or "",
        "parse_confidence":str(node.parse_confidence.value if hasattr(node.parse_confidence, 'value') else node.parse_confidence),
        "has_evidence":    bool(node.evidence_requirements),
        "has_gaps":        bool(node.gap_indicators),
        "has_xfw":         bool(xfw_ids),
        "xfw_count":       len(xfw_ids),
        "xfw_ids":         ",".join(xfw_ids[:10]),    # first 10 for filter
        "parent_ref":      node.parent_ref or "",
        "is_informational": node.obligation_type.value == "informational"
                            if hasattr(node.obligation_type, 'value')
                            else node.obligation_type == "informational",
    }


# ── Main indexer ───────────────────────────────────────────────────────────────

class VectorIndexer:
    """
    Indexes RequirementNodes into ChromaDB.

    Args:
        persist_dir: Where ChromaDB stores its data.
                     Defaults to ./chroma_db relative to ingestion root.
        use_fallback_embeddings: If True, use hash-based embeddings instead
                     of Anthropic API. For testing only.
        embedding_model: Anthropic embedding model to use.
    """

    def __init__(
        self,
        persist_dir:             str  = None,
        provider:                str  = "openai",
        embedding_model:         str  = None,
        use_fallback_embeddings: bool = False,
        dimensions:              int  = None,
        chroma_host:             str  = None,
        chroma_port:             int  = 8000,
    ):
        """
        Two connection modes:

        1. PersistentClient (default) — local file-based ChromaDB:
              VectorIndexer(persist_dir="./chroma_db")

        2. HttpClient — connect to a running ChromaDB server:
              VectorIndexer(chroma_host="localhost", chroma_port=8000)
           or set env vars: CHROMA_HOST=localhost CHROMA_PORT=8000

        provider: "openai" | "anthropic" | "fallback"
        """
        import os
        host = chroma_host or os.getenv("CHROMA_HOST")

        if host:
            port = int(chroma_port or os.getenv("CHROMA_PORT", "8000"))
            # ChromaDB 1.x HttpClient — settings param optional
            try:
                self._chroma = chromadb.HttpClient(
                    host     = host,
                    port     = port,
                    settings = Settings(anonymized_telemetry=False),
                )
            except TypeError:
                # Older chromadb versions don't accept settings in HttpClient
                self._chroma = chromadb.HttpClient(host=host, port=port)
            self.persist_dir = f"http://{host}:{port}"
        else:
            self.persist_dir = persist_dir or str(
                Path(__file__).parent.parent / "chroma_db"
            )
            Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
            self._chroma = chromadb.PersistentClient(
                path     = self.persist_dir,
                settings = Settings(anonymized_telemetry=False),
            )

        if use_fallback_embeddings:
            provider = "fallback"

        self.provider = provider

        # Embedding function
        if provider == "fallback":
            self._embed_fn = FallbackEmbeddingFunction()
        elif provider == "anthropic":
            model = embedding_model or "voyage-3"
            self._embed_fn = AnthropicEmbeddingFunction(model=model)
        else:  # openai (default)
            model = embedding_model or "text-embedding-3-small"
            self._embed_fn = OpenAIEmbeddingFunction(
                model=model, dimensions=dimensions
            )

        # Stats
        self._stats: dict[str, int] = {}

    # ── Public API ─────────────────────────────────────────────────────────

    def index_all(
        self,
        iso_nodes:  list[RequirementNode],
        gdpr_nodes: list[RequirementNode],
        reset:      bool = False,
    ) -> dict:
        """
        Index all nodes into ChromaDB.

        Args:
            iso_nodes:  ISO 27001 RequirementNodes
            gdpr_nodes: GDPR RequirementNodes
            reset:      If True, drop and recreate all collections first.

        Returns:
            Stats dict with counts per collection.
        """
        if reset:
            self._reset_collections()

        print(f"Indexing {len(iso_nodes)} ISO + {len(gdpr_nodes)} GDPR nodes...")
        print(f"Persist dir: {self.persist_dir}")
        embed_label = {
            "fallback":   "fallback/hash (no API — not semantic)",
            "anthropic":  f"Anthropic {getattr(self._embed_fn, 'model', 'voyage-3')}",
            "openai":     f"OpenAI {getattr(self._embed_fn, 'model', 'text-embedding-3-small')}",
        }.get(self.provider, self.provider)
        print(f"Embedding:   {embed_label}")
        print()

        # Index per-standard collections
        t0 = time.time()
        self._index_collection(COL_ISO,  iso_nodes,  "ISO27001:2022")
        self._index_collection(COL_GDPR, gdpr_nodes, "GDPR:2016/679")

        # Index combined collection
        all_nodes = iso_nodes + gdpr_nodes
        self._index_collection(COL_ALL,  all_nodes,  "all")

        elapsed = time.time() - t0
        self._stats["total_elapsed_s"] = round(elapsed, 2)

        self._print_stats()
        return self._stats

    def index_all_from_json(
        self,
        iso_json:  str,
        gdpr_json: str,
        reset:     bool = False,
    ) -> dict:
        """Load nodes from JSON files and index them."""
        iso_nodes  = self._load_nodes(iso_json)
        gdpr_nodes = self._load_nodes(gdpr_json)
        return self.index_all(iso_nodes, gdpr_nodes, reset=reset)

    def collection_stats(self) -> dict:
        """Return count of documents in each collection."""
        stats = {}
        for name in COLLECTIONS:
            try:
                col = self._chroma.get_collection(name)
                stats[name] = col.count()
            except Exception:
                stats[name] = 0
        return stats

    def _get_collection_embedding_model(self) -> str | None:
        """
        Read the embedding function name from an existing collection.
        Returns e.g. 'openai-text-embedding-3-large' or None if not found.
        """
        for col_name in COLLECTIONS:
            try:
                col = self._chroma.get_collection(col_name)
                # ChromaDB stores the embedding function name in metadata
                meta = col.metadata or {}
                ef_name = meta.get("embedding_function_name", "")
                if ef_name:
                    return ef_name
            except Exception:
                pass
        return None

    def get_collection(self, name: str):
        """Return a ChromaDB collection by name, using the correct embedding function."""
        # Auto-detect if the stored collection used a different model
        try:
            existing = self._chroma.get_collection(name)
            stored_meta = existing.metadata or {}
            stored_ef   = stored_meta.get("embedding_function_name", "")
            current_ef  = self._embed_fn.name() if hasattr(self._embed_fn, "name") else ""

            if stored_ef and current_ef and stored_ef != current_ef:
                # Mismatch — rebuild the embed function to match what was indexed
                self._embed_fn = self._make_embed_fn_from_name(stored_ef)
        except Exception:
            pass

        return self._chroma.get_collection(
            name=name,
            embedding_function=self._embed_fn,
        )

    def _make_embed_fn_from_name(self, ef_name: str):
        """
        Reconstruct an embedding function from a stored name like
        'openai-text-embedding-3-large' or 'anthropic-voyage-3'.
        Also handles dimension suffixes like 'openai-text-embedding-3-large-3072'.
        """
        import re
        if ef_name.startswith("openai-"):
            model = ef_name[len("openai-"):]
            # Strip dimension suffix e.g. "-3072" or "-1536"
            model = re.sub(r'-\d+$', '', model)
            return OpenAIEmbeddingFunction(model=model)
        elif ef_name.startswith("anthropic-"):
            model = ef_name[len("anthropic-"):]
            model = re.sub(r'-\d+$', '', model)
            return AnthropicEmbeddingFunction(model=model)
        else:
            return FallbackEmbeddingFunction()

    # ── Internal ───────────────────────────────────────────────────────────

    def _index_collection(
        self,
        col_name:   str,
        nodes:      list[RequirementNode],
        label:      str,
    ) -> None:
        """Upsert nodes into a ChromaDB collection."""
        t0 = time.time()

        # Get or create collection
        col = self._chroma.get_or_create_collection(
            name=col_name,
            embedding_function=self._embed_fn,
            metadata={
                "hnsw:space": "cosine",
                "embedding_function_name": self._embed_fn.name(),
            },
        )

        # Filter out nodes with empty vector documents
        indexable = []
        skipped   = 0
        for node in nodes:
            doc = node.to_vector_document()
            if doc and len(doc.strip()) > 20:
                indexable.append((node, doc))
            else:
                skipped += 1

        if not indexable:
            print(f"  {col_name}: no indexable nodes")
            return

        # Prepare ChromaDB upsert batches
        BATCH = 100
        total_upserted = 0

        for i in range(0, len(indexable), BATCH):
            batch = indexable[i:i + BATCH]
            ids        = [n.id         for n, _ in batch]
            documents  = [doc          for _, doc in batch]
            metadatas  = [_build_metadata(n) for n, _ in batch]

            col.upsert(
                ids        = ids,
                documents  = documents,
                metadatas  = metadatas,
            )
            total_upserted += len(batch)

            if len(indexable) > BATCH:
                pct = 100 * total_upserted // len(indexable)
                print(f"  {col_name}: {total_upserted}/{len(indexable)} ({pct}%)",
                      end='\r')

        elapsed = time.time() - t0
        print(f"  {col_name:25s}: {total_upserted:4d} upserted"
              f"  ({skipped} skipped, {elapsed:.1f}s)")

        self._stats[col_name] = total_upserted
        self._stats[f"{col_name}_skipped"] = skipped

    def _reset_collections(self) -> None:
        """Drop all collections."""
        for name in COLLECTIONS:
            try:
                self._chroma.delete_collection(name)
                print(f"  Dropped collection: {name}")
            except Exception:
                pass

    def _load_nodes(self, json_path: str) -> list[RequirementNode]:
        """Load RequirementNode objects from a JSON export."""
        path = Path(json_path)
        if not path.exists():
            raise FileNotFoundError(f"Node JSON not found: {json_path}")

        with open(path) as f:
            data = json.load(f)

        nodes = []
        for d in data:
            try:
                node = RequirementNode.from_dict(d)
                nodes.append(node)
            except Exception as e:
                print(f"  Warning: could not load node {d.get('id', '?')}: {e}")

        print(f"  Loaded {len(nodes)} nodes from {path.name}")
        return nodes

    def _print_stats(self) -> None:
        print()
        print("Index complete:")
        for col in COLLECTIONS:
            count   = self._stats.get(col, 0)
            skipped = self._stats.get(f"{col}_skipped", 0)
            print(f"  {col:25s}: {count:4d} docs  ({skipped} skipped)")
        print(f"  Total time: {self._stats.get('total_elapsed_s', 0)}s")
