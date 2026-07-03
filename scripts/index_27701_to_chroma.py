"""
Index the ISO 27701 RequirementNodes into their Chroma collection.

Existing 27001 + GDPR are indexed from source JSONs (iso_nodes_phase1.json /
gdpr_nodes_phase2.json). No such JSON exists for 27701 — the RequirementNode
shells live in Neo4j only. This script:

  1. Reads 27701 RequirementNodes from Neo4j
  2. Constructs RequirementNode objects
  3. Indexes them into COL_27701
  4. Refreshes COL_ALL (adds 27701 docs; leaves ISO/GDPR untouched)

Idempotent — run per curation batch.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv(str(Path(__file__).parent.parent / ".env"))

from vector.indexer import VectorIndexer, COL_27701, COL_ALL
from models.requirement_node import RequirementNode, NodeType, ObligationType


def fetch_27701_nodes(driver) -> list[RequirementNode]:
    """Read every ISO 27701 RequirementNode from Neo4j and construct
    RequirementNode dataclass instances the indexer accepts."""
    q = """
    MATCH (n:RequirementNode {standard_id: 'ISO27701:2019'})
    RETURN n ORDER BY n.ref
    """
    out: list[RequirementNode] = []
    with driver.session() as s:
        for record in s.run(q):
            n = dict(record["n"])
            applies_raw = n.get("applies_to", "['all']")
            if isinstance(applies_raw, str):
                applies_raw = applies_raw.strip("[]").replace("'", "").replace('"', "")
                applies_to = [x.strip() for x in applies_raw.split(",") if x.strip()]
            else:
                applies_to = list(applies_raw)
            out.append(RequirementNode(
                id                    = n["id"],
                standard_id           = n["standard_id"],
                ref                   = n["ref"],
                title                 = n.get("title", ""),
                node_type             = NodeType(n.get("node_type", "control")),
                obligation_text       = n.get("obligation_text", ""),
                obligation_type       = ObligationType(n.get("obligation_type", "risk_based")),
                applies_to            = applies_to,
                business_description  = n.get("business_description", ""),
            ))
    return out


def main():
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    pwd = os.getenv("NEO4J_PASSWORD")
    driver = GraphDatabase.driver(uri, auth=(user, pwd))

    print("Reading ISO 27701 nodes from Neo4j…")
    nodes = fetch_27701_nodes(driver)
    print(f"  {len(nodes)} nodes fetched.")

    driver.close()

    print()
    print("Indexing into ChromaDB…")

    provider = "openai" if os.getenv("OPENAI_API_KEY") else "fallback"
    indexer = VectorIndexer(
        persist_dir     = str(Path(__file__).parent.parent / "chroma_db"),
        provider        = provider,
        embedding_model = "text-embedding-3-small" if provider == "openai" else None,
    )

    # Idempotent upsert into COL_27701 (add-only; no reset)
    indexer._index_collection(COL_27701, nodes, "ISO27701:2019")

    # Upsert into COL_ALL (add-only)
    indexer._index_collection(COL_ALL, nodes, "all (27701 batch upsert)")

    print()
    print("Final collection counts:")
    for col, count in indexer.collection_stats().items():
        print(f"  {col:25s}: {count:4d} documents")


if __name__ == "__main__":
    main()
