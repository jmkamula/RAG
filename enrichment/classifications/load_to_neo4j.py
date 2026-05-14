"""
ArionComply — Load Classification vocabulary to Neo4j

Safe to re-run — uses MERGE on stable ids.

Loads ClassificationDimension and ClassificationValue nodes, plus
ALLOWS (Dimension → Value) and MANIFESTS_AS (Value → Event) edges.

A MANIFESTS_AS edge is only written if the target :Event node already exists
in Neo4j (events are loaded by enrichment/events/load_to_neo4j.py). Missing
events produce a warning, not a failure — the value still gets its other
edges, and the materialiser will simply see no obligation chain for that
value until the event is loaded.

Usage:
    python3 enrichment/classifications/load_to_neo4j.py --dry-run
    python3 enrichment/classifications/load_to_neo4j.py
    python3 enrichment/classifications/load_to_neo4j.py --verify
"""
from __future__ import annotations
import argparse, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from enrichment.classifications.classification_nodes import (
    ALL_DIMENSIONS,
    all_values,
)


def load(uri: str, user: str, password: str, dry_run: bool = False) -> None:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))

    total_dimensions = 0
    total_values     = 0
    total_allows     = 0
    total_manifests  = 0
    missing_events: list[tuple[str, str]] = []   # (value_id, event_id)

    with driver.session() as s:
        for dim in ALL_DIMENSIONS:

            if dry_run:
                print(f"\n[DRY RUN] Dimension: {dim.id}")
                print(f"  standard:      {dim.standard_id}")
                print(f"  dimension:     {dim.dimension}")
                print(f"  is_combinable: {dim.is_combinable}")
                print(f"  clause_ref:    {dim.clause_ref}")
                print(f"  values:        {len(dim.values)}")
                for v in dim.values:
                    binds = ", ".join(v.manifests_as) if v.manifests_as else "(label only)"
                    print(f"    {v.value:25s} → {binds}")
                continue

            # ── MERGE Dimension node ─────────────────────────────────────
            s.run("""
                MERGE (d:ClassificationDimension {id: $id})
                SET d.standard_id   = $standard_id,
                    d.dimension     = $dimension,
                    d.title         = $title,
                    d.description   = $description,
                    d.clause_ref    = $clause_ref,
                    d.is_combinable = $is_combinable
            """,
                id            = dim.id,
                standard_id   = dim.standard_id,
                dimension     = dim.dimension,
                title         = dim.title,
                description   = dim.description,
                clause_ref    = dim.clause_ref,
                is_combinable = dim.is_combinable,
            )
            total_dimensions += 1

            for v in dim.values:
                # ── MERGE Value node ─────────────────────────────────────
                s.run("""
                    MERGE (v:ClassificationValue {id: $id})
                    SET v.standard_id = $standard_id,
                        v.dimension   = $dimension,
                        v.value       = $value,
                        v.title       = $title,
                        v.description = $description
                """,
                    id          = v.id,
                    standard_id = v.standard_id,
                    dimension   = v.dimension,
                    value       = v.value,
                    title       = v.title,
                    description = v.description,
                )
                total_values += 1

                # ── MERGE ALLOWS edge (Dimension → Value) ────────────────
                s.run("""
                    MATCH (d:ClassificationDimension {id: $dim_id})
                    MATCH (v:ClassificationValue     {id: $val_id})
                    MERGE (d)-[:ALLOWS]->(v)
                """,
                    dim_id = dim.id,
                    val_id = v.id,
                )
                total_allows += 1

                # ── MERGE MANIFESTS_AS edges (Value → Event) ─────────────
                for event_id in v.manifests_as:
                    res = s.run("""
                        MATCH (v:ClassificationValue {id: $val_id})
                        MATCH (e:Event               {id: $event_id})
                        MERGE (v)-[:MANIFESTS_AS]->(e)
                        RETURN e.id AS bound
                    """,
                        val_id   = v.id,
                        event_id = event_id,
                    ).single()
                    if res is None:
                        missing_events.append((v.id, event_id))
                    else:
                        total_manifests += 1

            print(f"  ✓ {dim.standard_id}/{dim.dimension:20s} "
                  f"{len(dim.values)} values")

    driver.close()

    print(f"\n{'─'*55}")
    if dry_run:
        print("[DRY RUN] No changes written to Neo4j")
    else:
        print(f"✓ ClassificationDimension nodes: {total_dimensions}")
        print(f"✓ ClassificationValue     nodes: {total_values}")
        print(f"✓ ALLOWS                  rels:  {total_allows}")
        print(f"✓ MANIFESTS_AS            rels:  {total_manifests}")

    if missing_events:
        print(f"\n⚠ {len(missing_events)} MANIFESTS_AS edges not written "
              f"(target Event not in Neo4j):")
        for val_id, event_id in missing_events:
            print(f"  {val_id}  →  {event_id}")
        print("  (load events first: python3 enrichment/events/load_to_neo4j.py)")


def verify(uri: str, user: str, password: str) -> None:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as s:
        stats = s.run("""
            MATCH (d:ClassificationDimension) WITH count(d) AS dims
            MATCH (v:ClassificationValue)     WITH dims, count(v) AS vals
            MATCH ()-[a:ALLOWS]->()           WITH dims, vals, count(a) AS allows
            MATCH (:ClassificationValue)-[m:MANIFESTS_AS]->(:Event)
              WITH dims, vals, allows, count(m) AS manifests
            RETURN dims, vals, allows, manifests
        """).single()

        print(f"\nNeo4j verification:")
        print(f"  ClassificationDimension nodes: {stats['dims']}")
        print(f"  ClassificationValue     nodes: {stats['vals']}")
        print(f"  ALLOWS                  rels:  {stats['allows']}")
        print(f"  MANIFESTS_AS            rels:  {stats['manifests']}")

        by_dim = s.run("""
            MATCH (d:ClassificationDimension)-[:ALLOWS]->(v:ClassificationValue)
            OPTIONAL MATCH (v)-[:MANIFESTS_AS]->(e:Event)
            RETURN d.standard_id   AS std,
                   d.dimension     AS dim,
                   d.is_combinable AS comb,
                   count(DISTINCT v) AS vals,
                   count(DISTINCT e) AS events
            ORDER BY std, dim
        """)
        print(f"\n  By dimension:")
        for r in by_dim:
            print(f"    {r['std']:12s} {r['dim']:25s} "
                  f"comb={str(r['comb']):5s}  "
                  f"vals={r['vals']:2d}  events_bound={r['events']:2d}")

        # Full chain test: from a classification value, can we reach an obligation?
        chain = s.run("""
            MATCH (v:ClassificationValue {id: "classval:GDPR:breach_cia:confidentiality"})
                  -[:MANIFESTS_AS]->(e:Event)
                  -[:TRIGGERS_OBLIGATION]->(n:RequirementNode)
            RETURN e.id AS event, collect(DISTINCT n.id) AS obligations
        """).single()
        if chain:
            print(f"\n  Chain test — classval:GDPR:breach_cia:confidentiality:")
            print(f"    → {chain['event']}")
            for o in sorted(chain['obligations']):
                print(f"        ⇒ {o}")

    driver.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be loaded without writing")
    parser.add_argument("--verify",  action="store_true",
                        help="Verify Neo4j state matches expected counts")
    args = parser.parse_args()

    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

    uri      = os.getenv("NEO4J_URI")
    user     = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    if not (uri and user and password):
        sys.exit("Missing NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD env vars")

    if args.verify:
        verify(uri, user, password)
    else:
        load(uri, user, password, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
