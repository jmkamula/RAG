"""
ArionComply — Load EvidenceRequirement and ChecklistItem nodes to Neo4j

Writes the four-layer model per control:
  RequirementNode -[:SATISFIED_BY]-> FulfilmentSpec
                                       -[:REQUIRES_EVIDENCE]-> EvidenceRequirement
                                                                 -[:MUST_CONTAIN|SHOULD_CONTAIN]-> ChecklistItem

Safe to re-run — uses MERGE everywhere. Sets curation_status='curated' on
specs it touches (since they're being populated with leaves here).

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
    ALL_EVIDENCE_REQUIREMENTS, EvidenceRequirement
)


def load(uri: str, user: str, password: str, dry_run: bool = False) -> None:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))

    total_reqs = 0
    total_items = 0
    total_rels = 0
    total_specs = 0
    missing_controls = []

    with driver.session() as s:

        for req in ALL_EVIDENCE_REQUIREMENTS:

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

            # ── MERGE EvidenceRequirement node ────────────────────────────
            if dry_run:
                print(f"\n[DRY RUN] EvidenceRequirement: {req.id}")
                event_tag = f" ({req.trigger_event})" if req.trigger_event else ""
                print(f"  trigger: {req.trigger_type}{event_tag}")
                print(f"  must_contain: {len(req.must_contain)} items")
                print(f"  should_contain: {len(req.should_contain)} items")
            else:
                s.run("""
                    MERGE (r:EvidenceRequirement {id: $id})
                    SET r.control_ref   = $control_ref,
                        r.standard_id   = $standard_id,
                        r.evidence_type = $evidence_type,
                        r.title         = $title,
                        r.trigger_type  = $trigger_type,
                        r.trigger_event = $trigger_event,
                        r.description   = $description,
                        r.updated_at    = datetime()
                    RETURN r.id
                """,
                    id            = req.id,
                    control_ref   = req.control_ref,
                    standard_id   = req.standard_id,
                    evidence_type = req.evidence_type,
                    title         = req.title,
                    trigger_type  = req.trigger_type,
                    trigger_event = req.trigger_event or "",
                    description   = req.description,
                ).consume()
                total_reqs += 1

            # ── MERGE FulfilmentSpec for this control (idempotent) ────────
            # Spec id is deterministic: 'spec:' + RequirementNode id.
            # If the migration has run, the spec already exists with
            # curation_status='uncurated' for non-curated controls; touching
            # it here promotes it to 'curated' since we're attaching leaves.
            if not dry_run:
                s.run("""
                    MATCH (n:RequirementNode {id: $node_id})
                    MERGE (fs:FulfilmentSpec {id: 'spec:' + n.id})
                      ON CREATE SET
                          fs.op              = 'ALL',
                          fs.applies_when    = NULL,
                          fs.curation_status = 'curated',
                          fs.updated_at      = datetime()
                      ON MATCH SET
                          fs.curation_status = 'curated',
                          fs.updated_at      = datetime()
                    MERGE (n)-[:SATISFIED_BY]->(fs)
                """, node_id=node_id).consume()
                total_specs += 1

            # ── MERGE REQUIRES_EVIDENCE relationship (spec → leaf) ────────
            if not dry_run:
                s.run("""
                    MATCH (n:RequirementNode {id: $node_id})-[:SATISFIED_BY]->(fs:FulfilmentSpec)
                    MATCH (r:EvidenceRequirement {id: $req_id})
                    MERGE (fs)-[edge:REQUIRES_EVIDENCE]->(r)
                      ON CREATE SET edge.role = $role
                """,
                    node_id = node_id,
                    req_id  = req.id,
                    role    = req.evidence_type,
                ).consume()
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

                    # Link to EvidenceRequirement
                    rel_type = "MUST_CONTAIN" if category == "must" else "SHOULD_CONTAIN"
                    s.run(f"""
                        MATCH (r:EvidenceRequirement {{id: $req_id}})
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
                      f"{req.title}")

    driver.close()

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'─'*55}")
    if dry_run:
        print("[DRY RUN] No changes written to Neo4j")
    else:
        print(f"✓ EvidenceRequirement nodes:    {total_reqs}")
        print(f"✓ FulfilmentSpec MERGE calls:   {total_specs}")
        print(f"✓ ChecklistItem nodes:          {total_items}")
        print(f"✓ REQUIRES_EVIDENCE rels:       {total_rels}")

    if missing_controls:
        print(f"\n⚠ {len(missing_controls)} controls not found in Neo4j:")
        for c in missing_controls:
            print(f"  {c}")


def verify(uri: str, user: str, password: str) -> None:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as s:
        stats = s.run("""
            MATCH (r:EvidenceRequirement) WITH count(r) AS reqs
            MATCH (i:ChecklistItem)       WITH reqs, count(i) AS items
            MATCH ()-[:REQUIRES_EVIDENCE]->() WITH reqs, items, count(*) AS req_rels
            MATCH ()-[:SATISFIED_BY]->()      WITH reqs, items, req_rels, count(*) AS sat_rels
            MATCH ()-[:MUST_CONTAIN]->()      WITH reqs, items, req_rels, sat_rels, count(*) AS must_rels
            MATCH ()-[:SHOULD_CONTAIN]->()    WITH reqs, items, req_rels, sat_rels, must_rels, count(*) AS should_rels
            RETURN reqs, items, req_rels, sat_rels, must_rels, should_rels
        """).single()

        print(f"\nNeo4j verification:")
        print(f"  EvidenceRequirement nodes: {stats['reqs']}")
        print(f"  ChecklistItem nodes:       {stats['items']}")
        print(f"  REQUIRES_EVIDENCE rels:    {stats['req_rels']}")
        print(f"  SATISFIED_BY rels:         {stats['sat_rels']}")
        print(f"  MUST_CONTAIN rels:         {stats['must_rels']}")
        print(f"  SHOULD_CONTAIN rels:       {stats['should_rels']}")

        # Check trigger type distribution
        by_trigger = s.run("""
            MATCH (r:EvidenceRequirement)
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
        description="Load EvidenceRequirement and ChecklistItem nodes to Neo4j"
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
    print(f"Requirements: {len(ALL_EVIDENCE_REQUIREMENTS)}")

    load(args.neo4j_uri, args.neo4j_user, password, args.dry_run)

    if args.verify and not args.dry_run:
        verify(args.neo4j_uri, args.neo4j_user, password)


if __name__ == "__main__":
    main()
