"""
ArionComply — Holistic Neo4j Relationship Loader
Loads missing relationships from JSON source files without touching existing nodes.

What this adds:
  1. PART_OF    — hierarchy within standards (A.5.1 PART_OF A.5)
  2. IMPLEMENTS — cross-framework (ISO control IMPLEMENTS GDPR article)
  3. SUPPORTS   — cross-framework (ISO control SUPPORTS GDPR article)
  4. ENABLES    — cross-framework (ISO control ENABLES GDPR article)
  5. RELATED_TO — cross-framework (other relationships)

Safe to re-run — uses MERGE so no duplicates created.
Existing nodes and relationships are never deleted.

Usage:
  python3 load_graph_relationships.py --dry-run
  python3 load_graph_relationships.py
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime

NEO4J_URI  = os.getenv("NEO4J_URI",      "bolt://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USER",     "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "arionneo4j2026")

# Allowed relationship types (vocabulary alignment)
# Maps whatever is in the JSON → canonical Neo4j relationship type
_REL_MAP = {
    "PART_OF":    "PART_OF",
    "IMPLEMENTS": "IMPLEMENTS",
    "SUPPORTS":   "SUPPORTS",
    "ENABLES":    "ENABLES",
    "GOVERNANCE": "GOVERNANCE",
    "RELATED_TO": "RELATED_TO",
    # Aliases from older naming
    "IMPLEMENTS_GDPR": "IMPLEMENTS",
    "SUPPORTS_GDPR":   "SUPPORTS",
    "MAPS_TO":         "RELATED_TO",
    "REFERENCES":      "RELATED_TO",
}

def _canon_rel(raw: str) -> str:
    return _REL_MAP.get(raw.upper().strip(), "RELATED_TO")


def load_relationships(
    iso_path:  str,
    gdpr_path: str,
    driver,
    dry_run:   bool = False,
) -> dict:
    """
    Load PART_OF and cross-framework relationships from JSON source files.
    Returns counts dict.
    """
    counts = defaultdict(int)
    skipped_missing = []

    # ── 1. Get all existing RequirementNode ids ──────────────────────────────
    with driver.session() as s:
        existing = {
            r["id"] for r in s.run("MATCH (n:RequirementNode) RETURN n.id AS id")
        }
    print(f"  Found {len(existing)} existing RequirementNodes in graph")

    # ── 2. Collect all relationships to create ───────────────────────────────
    rels_to_create: list[tuple[str, str, str]] = []  # (src, rel_type, tgt)

    for path, label in [(iso_path, "ISO"), (gdpr_path, "GDPR")]:
        if not os.path.exists(path):
            print(f"  ⚠ {path} not found — skipping {label}")
            continue

        with open(path) as f:
            nodes = json.load(f)

        print(f"\n  Processing {label}: {len(nodes)} nodes from {os.path.basename(path)}")

        part_of_count    = 0
        crossfw_count    = 0
        missing_count    = 0

        for node in nodes:
            src_id = node.get("id", "")
            if not src_id:
                continue

            # ── PART_OF hierarchy (from edges array) ─────────────────────
            for edge in node.get("edges", []):
                tgt_id = edge.get("target_id", "")
                etype  = _canon_rel(edge.get("edge_type", "PART_OF"))

                if not tgt_id:
                    continue

                if src_id not in existing:
                    skipped_missing.append(src_id)
                    missing_count += 1
                    continue
                if tgt_id not in existing:
                    skipped_missing.append(tgt_id)
                    missing_count += 1
                    continue

                rels_to_create.append((src_id, etype, tgt_id))
                part_of_count += 1

            # ── Cross-framework relationships ─────────────────────────────
            for related_id, mapping in node.get("cross_framework_summary", {}).items():
                tgt_id = mapping.get("related_req_id", related_id)
                etype  = _canon_rel(mapping.get("relationship_type", "RELATED_TO"))

                if not tgt_id:
                    continue

                if src_id not in existing:
                    skipped_missing.append(src_id)
                    missing_count += 1
                    continue
                if tgt_id not in existing:
                    # GDPR nodes may not all be loaded — note but don't abort
                    skipped_missing.append(tgt_id)
                    missing_count += 1
                    continue

                rels_to_create.append((src_id, etype, tgt_id))
                crossfw_count += 1

        print(f"    PART_OF/hierarchy:  {part_of_count}")
        print(f"    Cross-framework:    {crossfw_count}")
        print(f"    Skipped (missing):  {missing_count}")

    # ── 3. Deduplicate ───────────────────────────────────────────────────────
    rels_unique = list(set(rels_to_create))
    print(f"\n  Total relationships to create: {len(rels_unique)} ({len(rels_to_create) - len(rels_unique)} duplicates removed)")

    # ── 4. Count by type ─────────────────────────────────────────────────────
    by_type = defaultdict(int)
    for _, rtype, _ in rels_unique:
        by_type[rtype] += 1
    for rtype, count in sorted(by_type.items()):
        print(f"    {rtype:20s} {count}")

    if dry_run:
        print("\n  [DRY RUN] — no changes written to Neo4j")
        return dict(by_type)

    # ── 5. Write to Neo4j in batches ─────────────────────────────────────────
    print(f"\n  Writing {len(rels_unique)} relationships to Neo4j...")
    created = defaultdict(int)
    errors  = 0
    batch   = []

    def flush_batch(session, batch):
        for src, rtype, tgt in batch:
            try:
                session.run(
                    f"""
                    MATCH (a:RequirementNode {{id: $src}})
                    MATCH (b:RequirementNode {{id: $tgt}})
                    MERGE (a)-[:{rtype}]->(b)
                    """,
                    src=src, tgt=tgt
                )
                created[rtype] += 1
            except Exception as e:
                nonlocal errors
                errors += 1
                if errors <= 5:
                    print(f"    ✗ {src} --[{rtype}]--> {tgt}: {e}")

    with driver.session() as s:
        for i, rel in enumerate(rels_unique):
            batch.append(rel)
            if len(batch) >= 100:
                flush_batch(s, batch)
                batch = []
                if (i + 1) % 500 == 0:
                    print(f"    ... {i+1}/{len(rels_unique)}")
        if batch:
            flush_batch(s, batch)

    print(f"\n  ✓ Created:")
    for rtype, count in sorted(created.items()):
        print(f"    {rtype:20s} {count}")
    if errors:
        print(f"  ✗ Errors: {errors}")

    return dict(created)


def verify(driver) -> None:
    """Print final graph state."""
    print("\n=== FINAL GRAPH STATE ===")
    with driver.session() as s:
        print("\nNodes:")
        for r in s.run(
            "CALL db.labels() YIELD label "
            "CALL { WITH label MATCH (n) WHERE label IN labels(n) RETURN count(n) AS c } "
            "RETURN label, c ORDER BY c DESC"
        ):
            print(f"  {r['label']:30s} {r['c']}")

        print("\nRelationships:")
        for r in s.run(
            "MATCH ()-[r]->() RETURN type(r) AS t, count(r) AS c ORDER BY c DESC"
        ):
            print(f"  {r['t']:30s} {r['c']}")

        print("\nRelationship patterns:")
        for r in s.run(
            "MATCH (a)-[r]->(b) "
            "RETURN DISTINCT labels(a)[0] AS f, type(r) AS t, labels(b)[0] AS to "
            "ORDER BY t, f"
        ):
            print(f"  {r['f']:25s} --[{r['t']}]--> {r['to']}")


def main():
    parser = argparse.ArgumentParser(description="Load missing Neo4j relationships")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without writing")
    parser.add_argument("--iso",  default="/data/arioncomply/iso_nodes_phase1.json")
    parser.add_argument("--gdpr", default="/data/arioncomply/gdpr_nodes_phase2.json")
    args = parser.parse_args()

    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

    print(f"ArionComply — Neo4j Relationship Loader")
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Neo4j: {NEO4J_URI}")
    print()

    counts = load_relationships(args.iso, args.gdpr, driver, dry_run=args.dry_run)

    if not args.dry_run:
        verify(driver)

    driver.close()
    print(f"\n✓ Done: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
