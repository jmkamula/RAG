"""
ArionComply — Load Relationship Catalog to Neo4j

Idempotent (MERGE) + declarative orphan pruning: any edge of a
managed type in Neo4j but NOT in ALL_EDGES is deleted on each run.

Symmetric edges (PAIRS_WITH) are authored ONCE in the catalog;
loader writes both directions.

Usage:
    python3 enrichment/relationships/load_to_neo4j.py --dry-run
    python3 enrichment/relationships/load_to_neo4j.py --verify
    python3 enrichment/relationships/load_to_neo4j.py        # apply
"""
from __future__ import annotations
import argparse, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from enrichment.relationships.relationship_catalog import (
    ALL_EDGES,
    MANAGED_EDGE_TYPES,
    SYMMETRIC_EDGE_TYPES,
    RelationshipEdge,
)


def _edges_to_write(edges: list[RelationshipEdge]) -> list[tuple[str, str, str, dict]]:
    """Materialise the catalog into the per-edge writes we'll do.

    Returns: list of (source_node_id, target_node_id, edge_type, props_dict).
    Symmetric edges expand into TWO writes (a→b and b→a).
    """
    out: list[tuple[str, str, str, dict]] = []
    for e in edges:
        props = {
            "rationale":    e.rationale or "",
            "citation":     e.citation or "",
            "role":         e.role or "",
            "applies_when": e.applies_when or "",
            "managed_by":   "relationship_catalog",
        }
        out.append((e.source_node_id(), e.target_node_id(), e.edge_type, props))
        if e.edge_type in SYMMETRIC_EDGE_TYPES:
            out.append((e.target_node_id(), e.source_node_id(), e.edge_type, props))
    return out


def load(uri: str, user: str, password: str, dry_run: bool = False) -> None:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))

    writes = _edges_to_write(ALL_EDGES)
    total_merged   = 0
    total_pruned   = 0
    missing_nodes  = []  # (source_id, target_id, edge_type)

    with driver.session() as s:
        # ── PASS 1: MERGE every desired edge ─────────────────────────────
        for src_id, tgt_id, et, props in writes:
            if dry_run:
                print(f"[DRY RUN] {src_id} -[{et}]-> {tgt_id}  "
                      f"rationale={props['rationale'][:50]!r}")
                continue

            # Verify both endpoints exist; skip + record if not.
            exists = s.run(
                "MATCH (a:RequirementNode {id: $sid}), "
                "      (b:RequirementNode {id: $tid}) "
                "RETURN a.id AS aid, b.id AS bid",
                sid=src_id, tid=tgt_id,
            ).single()
            if not exists:
                missing_nodes.append((src_id, tgt_id, et))
                continue

            s.run(
                "MATCH (a:RequirementNode {id: $sid}) "
                "MATCH (b:RequirementNode {id: $tid}) "
                f"MERGE (a)-[r:`{et}`]->(b) "
                "SET r.rationale    = $rationale, "
                "    r.citation     = $citation, "
                "    r.role         = $role, "
                "    r.applies_when = $applies_when, "
                "    r.managed_by   = $managed_by, "
                "    r.updated_at   = datetime()",
                sid=src_id, tid=tgt_id, **props,
            ).consume()
            total_merged += 1

        # ── PASS 2: declarative orphan prune ─────────────────────────────
        # Any edge of a managed type carrying managed_by='relationship_catalog'
        # that's NOT in `writes` gets deleted. Strictly opt-in via the
        # managed_by tag so we never touch pre-existing edges of these
        # types that were created by other loaders.
        desired_keys = {(s, t, et) for (s, t, et, _) in writes}
        for et in MANAGED_EDGE_TYPES:
            current = s.run(
                f"MATCH (a:RequirementNode)-[r:`{et}`]->(b:RequirementNode) "
                "WHERE r.managed_by = 'relationship_catalog' "
                "RETURN a.id AS sid, b.id AS tid",
            ).data() if not dry_run else []
            for row in current:
                key = (row["sid"], row["tid"], et)
                if key not in desired_keys:
                    if dry_run:
                        print(f"[DRY RUN] PRUNE {row['sid']} -[{et}]-> {row['tid']}")
                        continue
                    s.run(
                        f"MATCH (a:RequirementNode {{id: $sid}})-[r:`{et}`]->"
                        f"      (b:RequirementNode {{id: $tid}}) "
                        "WHERE r.managed_by = 'relationship_catalog' "
                        "DELETE r",
                        sid=row["sid"], tid=row["tid"],
                    ).consume()
                    total_pruned += 1

    driver.close()

    print(f"\n{'─'*55}")
    if dry_run:
        print(f"[DRY RUN] {len(writes)} desired edges, no changes applied")
    else:
        print(f"  edges merged:        {total_merged}")
        print(f"  edges pruned:        {total_pruned}")
        if missing_nodes:
            print(f"  endpoints missing:   {len(missing_nodes)}")
            for s_, t_, et_ in missing_nodes[:10]:
                print(f"    {s_} -[{et_}]-> {t_}")
            if len(missing_nodes) > 10:
                print(f"    ... and {len(missing_nodes) - 10} more")


def verify(uri: str, user: str, password: str) -> None:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))
    print(f"\nRelationship-catalog Neo4j verification:")
    with driver.session() as s:
        for et in MANAGED_EDGE_TYPES:
            r = s.run(
                f"MATCH ()-[r:`{et}`]->() "
                "WHERE r.managed_by = 'relationship_catalog' "
                "RETURN count(r) AS c",
            ).single()
            print(f"  {et:18s}: {r['c']}")
    driver.close()


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv("/data/arioncomply/.env")
    uri      = os.getenv("NEO4J_URI")
    user     = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    if not all([uri, user, password]):
        print("ERROR: NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD not set")
        sys.exit(1)

    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify",  action="store_true")
    args = ap.parse_args()

    if args.verify:
        verify(uri, user, password)
    else:
        load(uri, user, password, dry_run=args.dry_run)
