"""
ArionComply — Load DocumentRequirement and ChecklistItem nodes to Neo4j

Safe to re-run — uses MERGE so existing nodes are not duplicated.

Usage:
    python3 enrichment/documents/load_to_neo4j.py --dry-run
    python3 enrichment/documents/load_to_neo4j.py --verify
"""
from __future__ import annotations
import argparse
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from enrichment.documents.document_requirements import (
    ALL_DOCUMENT_REQUIREMENTS, DocumentRequirement
)


def load(uri: str, user: str, password: str, dry_run: bool = False) -> None:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))

    total_reqs = 0
    total_items = 0
    total_rels = 0
    missing_controls = []

    with driver.session() as s:

        for req in ALL_DOCUMENT_REQUIREMENTS:

            # ── Check RequirementNode exists ──────────────────────────────
            standard_id = req.standard_id
            node_id     = f"{standard_id}:{req.control_ref}"
            exists = s.run(
                "MATCH (n:RequirementNode {id: $id}) RETURN n.id",
                id=node_id
            ).single()

            if not exists:
                missing_controls.append(node_id)
                print(f"  ⚠ {node_id} — RequirementNode not found, skipping")
                continue

            # ── MERGE DocumentRequirement node ────────────────────────────
            if dry_run:
                print(f"\n[DRY RUN] DocumentRequirement: {req.id}")
                event_tag = f" ({req.trigger_event})" if req.trigger_event else ""
                print(f"  trigger: {req.trigger_type}{event_tag}")
                print(f"  must_contain: {len(req.must_contain)} items")
                print(f"  should_contain: {len(req.should_contain)} items")
            else:
                s.run("""
                    MERGE (r:DocumentRequirement {id: $id})
                    SET r.control_ref    = $control_ref,
                        r.standard_id   = $standard_id,
                        r.document_type = $document_type,
                        r.document_title= $document_title,
                        r.trigger_type  = $trigger_type,
                        r.trigger_event = $trigger_event,
                        r.description   = $description,
                        r.updated_at    = datetime()
                    RETURN r.id
                """,
                    id            = req.id,
                    control_ref   = req.control_ref,
                    standard_id   = req.standard_id,
                    document_type = req.document_type,
                    document_title= req.document_title,
                    trigger_type  = req.trigger_type,
                    trigger_event = req.trigger_event or "",
                    description   = req.description,
                ).consume()
                total_reqs += 1

            # ── MERGE REQUIRES_DOCUMENT relationship ──────────────────────
            if not dry_run:
                s.run("""
                    MATCH (n:RequirementNode {id: $node_id})
                    MATCH (r:DocumentRequirement {id: $req_id})
                    MERGE (n)-[:REQUIRES_DOCUMENT]->(r)
                """, node_id=node_id, req_id=req.id).consume()
                total_rels += 1

            # ── MERGE ChecklistItems ──────────────────────────────────────
            all_items = [
                (item, "must")
                for item in req.must_contain
            ] + [
                (item, "should")
                for item in req.should_contain
            ]

            for item, category in all_items:
                if dry_run:
                    gdpr_tag = " [GDPR]" if item.gdpr_aligned else ""
                    print(f"    [{category}] {item.text}{gdpr_tag}")
                else:
                    s.run("""
                        MERGE (i:ChecklistItem {id: $id})
                        SET i.text         = $text,
                            i.category     = $category,
                            i.gdpr_aligned = $gdpr_aligned,
                            i.rationale    = $rationale,
                            i.control_ref  = $control_ref,
                            i.updated_at   = datetime()
                        RETURN i.id
                    """,
                        id           = item.id,
                        text         = item.text,
                        category     = category,
                        gdpr_aligned = item.gdpr_aligned,
                        rationale    = item.rationale,
                        control_ref  = req.control_ref,
                    ).consume()

                    # Link to DocumentRequirement
                    rel_type = "MUST_CONTAIN" if category == "must" else "SHOULD_CONTAIN"
                    s.run(f"""
                        MATCH (r:DocumentRequirement {{id: $req_id}})
                        MATCH (i:ChecklistItem {{id: $item_id}})
                        MERGE (r)-[:{rel_type}]->(i)
                    """, req_id=req.id, item_id=item.id).consume()

                    # Link back to RequirementNode for traceability
                    s.run("""
                        MATCH (n:RequirementNode {id: $node_id})
                        MATCH (i:ChecklistItem {id: $item_id})
                        MERGE (i)-[:DERIVED_FROM]->(n)
                    """, node_id=node_id, item_id=item.id).consume()

                    total_items += 1

            if not dry_run:
                print(f"  ✓ {req.control_ref:12s} {req.trigger_type:15s} "
                      f"{len(req.must_contain)}M + {len(req.should_contain)}S items  "
                      f"{req.document_title}")

    driver.close()

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'─'*55}")
    if dry_run:
        print("[DRY RUN] No changes written to Neo4j")
    else:
        print(f"✓ DocumentRequirement nodes: {total_reqs}")
        print(f"✓ ChecklistItem nodes:       {total_items}")
        print(f"✓ REQUIRES_DOCUMENT rels:    {total_rels}")

    if missing_controls:
        print(f"\n⚠ {len(missing_controls)} controls not found in Neo4j:")
        for c in missing_controls:
            print(f"  {c}")


def verify(uri: str, user: str, password: str) -> None:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as s:
        stats = s.run("""
            MATCH (r:DocumentRequirement) WITH count(r) AS reqs
            MATCH (i:ChecklistItem)       WITH reqs, count(i) AS items
            MATCH ()-[:REQUIRES_DOCUMENT]->()  WITH reqs, items, count(*) AS req_rels
            MATCH ()-[:MUST_CONTAIN]->()       WITH reqs, items, req_rels, count(*) AS must_rels
            MATCH ()-[:SHOULD_CONTAIN]->()     WITH reqs, items, req_rels, must_rels, count(*) AS should_rels
            RETURN reqs, items, req_rels, must_rels, should_rels
        """).single()

        print(f"\nNeo4j verification:")
        print(f"  DocumentRequirement nodes: {stats['reqs']}")
        print(f"  ChecklistItem nodes:       {stats['items']}")
        print(f"  REQUIRES_DOCUMENT rels:    {stats['req_rels']}")
        print(f"  MUST_CONTAIN rels:         {stats['must_rels']}")
        print(f"  SHOULD_CONTAIN rels:       {stats['should_rels']}")

        # Check trigger type distribution
        by_trigger = s.run("""
            MATCH (r:DocumentRequirement)
            RETURN r.trigger_type AS trigger, count(r) AS cnt
            ORDER BY cnt DESC
        """)
        print(f"\n  By trigger type:")
        for row in by_trigger:
            print(f"    {row['trigger']:15s}: {row['cnt']}")

        # Check GDPR-aligned items
        gdpr = s.run("""
            MATCH (i:ChecklistItem {gdpr_aligned: true})
            RETURN count(i) AS cnt
        """).single()
        print(f"\n  GDPR-aligned checklist items: {gdpr['cnt']}")

    driver.close()


def main():
    parser = argparse.ArgumentParser(
        description="Load DocumentRequirement and ChecklistItem nodes to Neo4j"
    )
    parser.add_argument("--dry-run",  action="store_true")
    parser.add_argument("--verify",   action="store_true")
    parser.add_argument("--neo4j-uri",      default="bolt://127.0.0.1:7687")
    parser.add_argument("--neo4j-user",     default="neo4j")
    parser.add_argument("--neo4j-password", default=None)
    args = parser.parse_args()

    password = args.neo4j_password or os.getenv("NEO4J_PASSWORD", "arionneo4j@2026")

    print(f"Neo4j: {args.neo4j_uri}")
    print(f"Dry run: {args.dry_run}")
    print(f"Requirements: {len(ALL_DOCUMENT_REQUIREMENTS)}")

    load(args.neo4j_uri, args.neo4j_user, password, args.dry_run)

    if args.verify and not args.dry_run:
        verify(args.neo4j_uri, args.neo4j_user, password)


if __name__ == "__main__":
    main()
