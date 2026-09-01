"""
db/baseline/load_neo4j_baseline.py — single loader for Neo4j golden.

Replaces the previous 5-loader chain (load_neo4j.py +
seed_27701_requirement_nodes.py + enrichment/relationships/
load_to_neo4j.py + load_graph_relationships.py + enrichment/
documents/load_to_neo4j.py) with one file that reads
`db/baseline/neo4j_baseline.json` and reproduces the entire graph
via MERGE.

Idempotent — running twice against a fresh Neo4j yields the same
result. Running against a partially-loaded Neo4j merges missing
nodes/edges; running against a fully-loaded Neo4j is a no-op.

Usage:
    NEO4J_PASSWORD=xxx python3 db/baseline/load_neo4j_baseline.py

Or from install.sh (called by step 8):
    NEO4J_PASSWORD="$NEO4J_PW" PYTHONPATH="$ARION_ROOT" \
        python3 db/baseline/load_neo4j_baseline.py

Ship 102'.b (2026-09-01).
"""
from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(str(Path(__file__).parent.parent.parent / ".env"))
except ImportError:
    pass

from neo4j import GraphDatabase
from neo4j.time import DateTime as Neo4jDateTime


BASELINE_JSON = Path(__file__).parent / "neo4j_baseline.json"
BATCH = 500  # tune upward if network round-trips dominate


def _deserialise(v):
    """Round-trip the __neo4j_datetime__ marker back to Neo4j DateTime."""
    if isinstance(v, dict):
        if "__neo4j_datetime__" in v:
            return Neo4jDateTime.from_iso_format(v["__neo4j_datetime__"])
        return {k: _deserialise(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_deserialise(x) for x in v]
    return v


def _cypher_key_predicate(key: dict) -> str:
    """Emit `{k1: $key_k1, k2: $key_k2}` for MERGE predicate."""
    return "{" + ", ".join(f"{k}: $key_{k}" for k in key) + "}"


def load(uri: str, user: str, password: str) -> None:
    with BASELINE_JSON.open() as f:
        data = json.load(f)

    meta = data["metadata"]
    nodes = data["nodes"]
    rels  = data["relationships"]

    print(f"Neo4j baseline snapshot: {meta['node_count']} nodes / "
          f"{meta['rel_count']} rels (generated {meta['generated_at']}, "
          f"git {meta['git_sha']})")

    driver = GraphDatabase.driver(uri, auth=(user, password))
    t0 = time.time()

    # ── 1. Nodes — MERGE each by (label, key). Set properties. ──
    #
    # We can't easily do UNWIND with dynamic labels in a single
    # Cypher query, so we group nodes by (label, key-field-tuple)
    # and emit one MERGE statement per group.
    from collections import defaultdict
    node_groups: dict[tuple[str, tuple[str, ...]], list[dict]] = defaultdict(list)
    for n in nodes:
        label = n["labels"][0]
        key_fields = tuple(sorted(n["key"].keys()))
        node_groups[(label, key_fields)].append(n)

    print(f"  · loading nodes ({len(nodes)} across "
          f"{len(node_groups)} (label,key-shape) groups)")
    total_nodes_loaded = 0
    with driver.session() as s:
        for (label, key_fields), group_nodes in node_groups.items():
            # UNWIND-based batch load. Each node contributes props + key values.
            batch = []
            for n in group_nodes:
                params = {"props": {k: _deserialise(v) for k, v in n["properties"].items()}}
                for k, v in n["key"].items():
                    params[f"key_{k}"] = _deserialise(v)
                batch.append(params)
                if len(batch) >= BATCH:
                    _flush_nodes(s, label, key_fields, batch)
                    total_nodes_loaded += len(batch)
                    batch = []
            if batch:
                _flush_nodes(s, label, key_fields, batch)
                total_nodes_loaded += len(batch)

    print(f"    {total_nodes_loaded} nodes upserted "
          f"in {time.time() - t0:.1f}s")

    # ── 2. Relationships — MATCH start/end by key, MERGE rel. ──
    #
    # Group by (rel_type, start_label, start_key_fields, end_label, end_key_fields)
    # so each MERGE can use static labels + a param bundle.
    rel_groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in rels:
        sk = tuple(sorted(r["start"]["key"].keys()))
        ek = tuple(sorted(r["end"]["key"].keys()))
        gk = (r["type"], r["start"]["label"], sk, r["end"]["label"], ek)
        rel_groups[gk].append(r)

    t1 = time.time()
    print(f"  · loading relationships ({len(rels)} across "
          f"{len(rel_groups)} (type,endpoints) groups)")
    total_rels_loaded = 0
    with driver.session() as s:
        for gk, group_rels in rel_groups.items():
            batch = []
            for r in group_rels:
                params = {"props": {k: _deserialise(v) for k, v in r["properties"].items()}}
                for k, v in r["start"]["key"].items():
                    params[f"a_key_{k}"] = _deserialise(v)
                for k, v in r["end"]["key"].items():
                    params[f"b_key_{k}"] = _deserialise(v)
                batch.append(params)
                if len(batch) >= BATCH:
                    _flush_rels(s, gk, batch)
                    total_rels_loaded += len(batch)
                    batch = []
            if batch:
                _flush_rels(s, gk, batch)
                total_rels_loaded += len(batch)

    print(f"    {total_rels_loaded} rels upserted in {time.time() - t1:.1f}s")

    driver.close()
    print(f"Total: {time.time() - t0:.1f}s")


def _flush_nodes(session, label: str, key_fields: tuple[str, ...], batch: list[dict]) -> None:
    key_preds = ", ".join(f"{k}: row.key_{k}" for k in key_fields)
    key_map   = ", ".join(f"key_{k}: n.key_{k}" for k in key_fields)
    query = f"""
        UNWIND $rows AS n
        WITH n, {{{key_map}, props: n.props}} AS row
        MERGE (x:`{label}` {{{key_preds}}})
        SET x += row.props
    """
    session.run(query, rows=batch).consume()


def _flush_rels(session, gk: tuple, batch: list[dict]) -> None:
    rel_type, a_lbl, a_key_fields, b_lbl, b_key_fields = gk
    a_preds = ", ".join(f"{k}: row.a_key_{k}" for k in a_key_fields)
    b_preds = ", ".join(f"{k}: row.b_key_{k}" for k in b_key_fields)
    a_key_map = ", ".join(f"a_key_{k}: n.a_key_{k}" for k in a_key_fields)
    b_key_map = ", ".join(f"b_key_{k}: n.b_key_{k}" for k in b_key_fields)
    query = f"""
        UNWIND $rows AS n
        WITH n, {{{a_key_map}, {b_key_map}, props: n.props}} AS row
        MATCH (a:`{a_lbl}` {{{a_preds}}})
        MATCH (b:`{b_lbl}` {{{b_preds}}})
        MERGE (a)-[r:`{rel_type}`]->(b)
        SET r += row.props
    """
    session.run(query, rows=batch).consume()


def main() -> None:
    uri  = os.getenv("NEO4J_URI",      "bolt://127.0.0.1:7687")
    user = os.getenv("NEO4J_USER",     "neo4j")
    pw   = os.getenv("NEO4J_PASSWORD")
    if not pw:
        sys.exit("NEO4J_PASSWORD not set — export it or put it in .env")
    load(uri, user, pw)


if __name__ == "__main__":
    main()
