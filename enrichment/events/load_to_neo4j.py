"""
ArionComply — Load Event nodes to Neo4j

Safe to re-run — uses MERGE.

Usage:
    python3 enrichment/events/load_to_neo4j.py --dry-run
    python3 enrichment/events/load_to_neo4j.py --verify
"""
from __future__ import annotations
import argparse, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from enrichment.events.event_nodes import ALL_EVENTS


def load(uri: str, user: str, password: str, dry_run: bool = False) -> None:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))

    total_events   = 0
    total_triggers = 0
    total_doc_rels = 0
    missing        = []

    with driver.session() as s:
        for event in ALL_EVENTS:

            if dry_run:
                print(f"\n[DRY RUN] Event: {event.id}")
                print(f"  category:  {event.category}")
                print(f"  deadline:  {event.legal_deadline or 'none'}")
                print(f"  severity:  {event.severity_default}")
                print(f"  triggers:  {len(event.triggers)}")
                for t in event.triggers:
                    print(f"    → {t.control_id}" +
                          (f" [{t.deadline}]" if t.deadline else ""))
                if event.requires_documents:
                    print(f"  documents: {event.requires_documents}")
                continue

            # ── MERGE Event node ──────────────────────────────────────────
            s.run("""
                MERGE (e:Event {id: $id})
                SET e.event_type       = $event_type,
                    e.category         = $category,
                    e.title            = $title,
                    e.description      = $description,
                    e.legal_deadline   = $legal_deadline,
                    e.severity_default = $severity_default,
                    e.updated_at       = datetime()
                RETURN e.id
            """,
                id               = event.id,
                event_type       = event.event_type,
                category         = event.category,
                title            = event.title,
                description      = event.description,
                legal_deadline   = event.legal_deadline or "",
                severity_default = event.severity_default,
            ).consume()
            total_events += 1

            # ── MERGE TRIGGERS_OBLIGATION relationships ────────────────────
            for trigger in event.triggers:
                exists = s.run(
                    "MATCH (n:RequirementNode {id: $id}) RETURN n.id",
                    id=trigger.control_id
                ).single()

                if not exists:
                    missing.append((event.event_type, trigger.control_id))
                    continue

                s.run("""
                    MATCH (e:Event {id: $event_id})
                    MATCH (n:RequirementNode {id: $control_id})
                    MERGE (e)-[r:TRIGGERS_OBLIGATION]->(n)
                    SET r.deadline  = $deadline,
                        r.rationale = $rationale,
                        r.mandatory = true
                """,
                    event_id   = event.id,
                    control_id = trigger.control_id,
                    deadline   = trigger.deadline or "",
                    rationale  = trigger.rationale,
                ).consume()
                total_triggers += 1

            # ── MERGE REQUIRES_DOCUMENT relationships ─────────────────────
            for doc_req_id in event.requires_documents:
                exists = s.run(
                    "MATCH (r:DocumentRequirement {id: $id}) RETURN r.id",
                    id=doc_req_id
                ).single()

                if not exists:
                    missing.append((event.event_type, doc_req_id))
                    continue

                s.run("""
                    MATCH (e:Event {id: $event_id})
                    MATCH (r:DocumentRequirement {id: $doc_req_id})
                    MERGE (e)-[:REQUIRES_DOCUMENT]->(r)
                """,
                    event_id   = event.id,
                    doc_req_id = doc_req_id,
                ).consume()
                total_doc_rels += 1

            print(f"  ✓ {event.event_type:40s} "
                  f"{len(event.triggers)} triggers  "
                  f"{len(event.requires_documents)} docs")

    driver.close()

    print(f"\n{'─'*55}")
    if dry_run:
        print("[DRY RUN] No changes written to Neo4j")
    else:
        print(f"✓ Event nodes:              {total_events}")
        print(f"✓ TRIGGERS_OBLIGATION rels: {total_triggers}")
        print(f"✓ REQUIRES_DOCUMENT rels:   {total_doc_rels}")

    if missing:
        print(f"\n⚠ {len(missing)} nodes not found:")
        for event_type, node_id in missing:
            print(f"  {node_id} (event: {event_type})")


def verify(uri: str, user: str, password: str) -> None:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as s:
        stats = s.run("""
            MATCH (e:Event) WITH count(e) AS events
            MATCH ()-[t:TRIGGERS_OBLIGATION]->() WITH events, count(t) AS trigs
            MATCH (e2:Event)-[:REQUIRES_DOCUMENT]->() WITH events, trigs, count(e2) AS doc_rels
            RETURN events, trigs, doc_rels
        """).single()

        print(f"\nNeo4j verification:")
        print(f"  Event nodes:              {stats['events']}")
        print(f"  TRIGGERS_OBLIGATION rels: {stats['trigs']}")
        print(f"  Event REQUIRES_DOCUMENT:  {stats['doc_rels']}")

        by_cat = s.run("""
            MATCH (e:Event)
            RETURN e.category AS cat, count(e) AS cnt
            ORDER BY cnt DESC
        """)
        print(f"\n  By category:")
        for r in by_cat:
            print(f"    {r['cat']:10s}: {r['cnt']}")

        # Test full chain — event → obligations → document requirements
        chain = s.run("""
            MATCH (e:Event {event_type: 'personal_data_breach'})
                  -[:TRIGGERS_OBLIGATION]->(n:RequirementNode)
            RETURN e.title AS event, collect(n.ref) AS controls
        """).single()
        if chain:
            print(f"\n  Chain test — {chain['event']}:")
            print(f"    Triggers: {sorted(chain['controls'])}")

    driver.close()


def main():
    parser = argparse.ArgumentParser(
        description="Load Event nodes to Neo4j"
    )
    parser.add_argument("--dry-run",        action="store_true")
    parser.add_argument("--verify",         action="store_true")
    parser.add_argument("--neo4j-uri",      default="bolt://127.0.0.1:7687")
    parser.add_argument("--neo4j-user",     default="neo4j")
    parser.add_argument("--neo4j-password", default=None)
    args = parser.parse_args()

    password = args.neo4j_password or os.getenv("NEO4J_PASSWORD", "arionneo4j@2026")
    print(f"Neo4j:    {args.neo4j_uri}")
    print(f"Dry run:  {args.dry_run}")
    print(f"Events:   {len(ALL_EVENTS)}")

    load(args.neo4j_uri, args.neo4j_user, password, args.dry_run)

    if args.verify and not args.dry_run:
        verify(args.neo4j_uri, args.neo4j_user, password)


if __name__ == "__main__":
    main()
