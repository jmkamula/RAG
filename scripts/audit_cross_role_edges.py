#!/usr/bin/env python3
"""
Ship 23'.a — Cross-role edge + text-enrichment audit.

Read-only Neo4j survey enumerating:
  1. For each RequirementNode, how many cross-role edges it has
     (DEMONSTRATES / IMPLEMENTS / SUPPORTS / GOVERNANCE to nodes in
     other standards).
  2. Coverage of the `cross_framework_summary` text-enrichment
     property.
  3. Per-family breakdowns (A.5.x / A.6.x / A.7.x / A.8.x / ISMS
     clauses) with unlinked-vs-linked counts.
  4. Sample of controls with the highest cross-role fanout (for
     spot-checking curation quality).

Usage
    PYTHONPATH=/data/arioncomply python3 scripts/audit_cross_role_edges.py
    PYTHONPATH=/data/arioncomply python3 scripts/audit_cross_role_edges.py --standard ISO27001:2022
    PYTHONPATH=/data/arioncomply python3 scripts/audit_cross_role_edges.py --json > /tmp/audit.json

Read-only; safe to run against production. No writes, no mutations.
"""
from __future__ import annotations
import argparse
import json
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv


CROSS_ROLE_EDGES = "DEMONSTRATES|IMPLEMENTS|SUPPORTS|GOVERNANCE"


def _driver():
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
    return GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")),
    )


def coverage_by_standard(session, standard: str | None = None) -> list[dict]:
    filt = "WHERE n.standard_id = $sid" if standard else ""
    rows = session.run(f"""
      MATCH (n:RequirementNode)
      {filt}
      OPTIONAL MATCH (n)-[r:{CROSS_ROLE_EDGES}]-(m:RequirementNode)
      WHERE m.standard_id <> n.standard_id
      WITH n.standard_id AS sid, n.ref AS ref, count(DISTINCT m) AS cross
      RETURN sid,
             count(*) AS total_nodes,
             sum(CASE WHEN cross > 0 THEN 1 ELSE 0 END) AS with_cross,
             sum(CASE WHEN cross = 0 THEN 1 ELSE 0 END) AS zero_cross,
             avg(cross) AS avg_cross_per_node,
             max(cross) AS max_cross
      ORDER BY total_nodes DESC
    """, sid=standard).data()
    return rows


def text_enrichment_coverage(session) -> list[dict]:
    return session.run("""
      MATCH (n:RequirementNode)
      RETURN n.standard_id AS sid,
             count(*) AS total,
             sum(CASE WHEN n.cross_framework_summary IS NOT NULL THEN 1 ELSE 0 END) AS with_prop,
             sum(CASE WHEN n.business_description IS NOT NULL THEN 1 ELSE 0 END) AS with_biz,
             sum(CASE WHEN n.obligation_text IS NOT NULL THEN 1 ELSE 0 END) AS with_oblig
      ORDER BY total DESC
    """).data()


def unlinked_by_family(session, standard: str) -> list[dict]:
    return session.run("""
      MATCH (n:RequirementNode {standard_id: $sid})
      OPTIONAL MATCH (n)-[r:DEMONSTRATES|IMPLEMENTS|SUPPORTS|GOVERNANCE]-(m:RequirementNode)
      WHERE m.standard_id <> n.standard_id
      WITH n, count(m) AS cross
      WITH
        CASE
          WHEN n.ref STARTS WITH 'A.5' THEN 'A.5.x (Organisational)'
          WHEN n.ref STARTS WITH 'A.6' THEN 'A.6.x (People)'
          WHEN n.ref STARTS WITH 'A.7' THEN 'A.7.x (Physical)'
          WHEN n.ref STARTS WITH 'A.8' THEN 'A.8.x (Technological)'
          WHEN n.ref STARTS WITH 'B.' THEN 'B.x (PIMS Processor)'
          WHEN n.ref STARTS WITH 'Art.' THEN 'Art.x (GDPR)'
          ELSE 'ISMS clauses (4-10)'
        END AS family,
        cross
      RETURN family,
             count(*) AS total,
             sum(CASE WHEN cross = 0 THEN 1 ELSE 0 END) AS unlinked,
             sum(CASE WHEN cross > 0 THEN 1 ELSE 0 END) AS linked
      ORDER BY unlinked DESC
    """, sid=standard).data()


def unlinked_nodes(session, standard: str, limit: int = 100) -> list[dict]:
    return session.run("""
      MATCH (n:RequirementNode {standard_id: $sid})
      OPTIONAL MATCH (n)-[r:DEMONSTRATES|IMPLEMENTS|SUPPORTS|GOVERNANCE]-(m:RequirementNode)
      WHERE m.standard_id <> n.standard_id
      WITH n, count(m) AS cross
      WHERE cross = 0
      RETURN n.ref AS ref, n.title AS title
      ORDER BY n.ref
      LIMIT $limit
    """, sid=standard, limit=limit).data()


def top_fanout_nodes(session, limit: int = 15) -> list[dict]:
    return session.run("""
      MATCH (n:RequirementNode)-[r:DEMONSTRATES|IMPLEMENTS|SUPPORTS|GOVERNANCE]-(m:RequirementNode)
      WHERE m.standard_id <> n.standard_id
      WITH n, count(DISTINCT m) AS cross
      RETURN n.standard_id AS sid, n.ref AS ref, n.title AS title, cross
      ORDER BY cross DESC, n.standard_id, n.ref
      LIMIT $limit
    """, limit=limit).data()


def edge_matrix(session) -> list[dict]:
    """Which cross-standard edge types are populated by which
    standard pairs? Reveals asymmetries (e.g. DEMONSTRATES only
    one-way)."""
    return session.run("""
      MATCH (a:RequirementNode)-[r:DEMONSTRATES|IMPLEMENTS|SUPPORTS|GOVERNANCE]->(b:RequirementNode)
      WHERE a.standard_id <> b.standard_id
      RETURN type(r) AS type, a.standard_id AS a_sid, b.standard_id AS b_sid, count(*) AS n
      ORDER BY n DESC
    """).data()


def _print_human(driver, args):
    with driver.session() as s:
        print("═" * 72)
        print(" Ship 23'.a — Cross-role edge + enrichment audit")
        print("═" * 72)
        print()
        print("── Cross-role edge coverage per standard ──────────────────────────")
        for r in coverage_by_standard(s, args.standard):
            pct = (r["with_cross"] / r["total_nodes"] * 100) if r["total_nodes"] else 0
            print(f"  {r['sid']:20s} "
                  f"total={r['total_nodes']:4d}  "
                  f"linked={r['with_cross']:4d} ({pct:5.1f}%)  "
                  f"unlinked={r['zero_cross']:4d}  "
                  f"avg={r['avg_cross_per_node']:.1f}  "
                  f"max={r['max_cross']}")
        print()

        print("── Text-enrichment coverage ────────────────────────────────────────")
        print(f"  {'standard':22s} {'total':>6s} {'cross_fw':>10s} {'biz_desc':>10s} {'oblig_text':>12s}")
        for r in text_enrichment_coverage(s):
            print(f"  {r['sid']:22s} {r['total']:6d} "
                  f"{r['with_prop']:10d} {r['with_biz']:10d} {r['with_oblig']:12d}")
        print()

        # Per-standard family breakdown
        stds_to_break_down = ([args.standard] if args.standard
                              else ["ISO27001:2022", "ISO27701:2019", "GDPR:2016/679"])
        for sid in stds_to_break_down:
            print(f"── {sid} — unlinked by family ─────────────────────────────")
            for r in unlinked_by_family(s, sid):
                pct = (r["unlinked"] / r["total"] * 100) if r["total"] else 0
                print(f"  {r['family']:28s} "
                      f"unlinked={r['unlinked']:3d}/{r['total']:3d} ({pct:5.1f}%)  "
                      f"linked={r['linked']}")
            print()

        print("── Top-fanout controls (highest cross-role reach) ─────────────────")
        for r in top_fanout_nodes(s):
            title = (r["title"] or "")[:50]
            print(f"  {r['sid']:22s} {r['ref']:10s} cross={r['cross']:3d}  {title}")
        print()

        print("── Cross-standard edge matrix ──────────────────────────────────────")
        print(f"  {'edge':16s} {'source':22s}   →  {'target':22s} count")
        for r in edge_matrix(s):
            print(f"  {r['type']:16s} {r['a_sid']:22s}   →  {r['b_sid']:22s} {r['n']}")


def _print_json(driver, args):
    with driver.session() as s:
        out = {
            "coverage_by_standard":   coverage_by_standard(s, args.standard),
            "text_enrichment":        text_enrichment_coverage(s),
            "top_fanout":             top_fanout_nodes(s, limit=30),
            "edge_matrix":            edge_matrix(s),
        }
        if args.standard:
            out["unlinked_nodes"] = unlinked_nodes(s, args.standard, limit=300)
            out["family_breakdown"] = unlinked_by_family(s, args.standard)
        else:
            out["family_breakdown"] = {}
            out["unlinked_nodes"]   = {}
            for sid in ("ISO27001:2022", "ISO27701:2019", "GDPR:2016/679"):
                out["family_breakdown"][sid] = unlinked_by_family(s, sid)
                out["unlinked_nodes"][sid]   = unlinked_nodes(s, sid, limit=300)
        print(json.dumps(out, indent=2, default=str))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--standard", help="Filter to one standard_id (e.g. ISO27001:2022)")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of human report")
    args = ap.parse_args()

    driver = _driver()
    try:
        (_print_json if args.json else _print_human)(driver, args)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
