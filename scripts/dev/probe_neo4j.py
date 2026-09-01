"""
scripts/dev/probe_neo4j.py — quick Neo4j data-parity check.

Runs against the local Neo4j (reads NEO4J_URI/USER/PASSWORD from
.env at the repo root, matches the loader script's pattern).
Reports totals + per-label counts + RequirementNode-per-standard
breakdown so you can compare against a known-good source.

Expected on a fresh install from the Ship 102' golden:
    totals: 8148 nodes, 14378 rels
    10 labels (RequirementNode, EvidenceRequirement, FulfilmentSpec,
    ChecklistItem, Template, ClientFact, Event, ObligationRule,
    ClassificationValue, ClassificationDimension)
    RequirementNode per standard:
        GDPR:2016/679      316
        ISO27001:2022      126
        ISO27701:2019       49

Usage:
    python3 scripts/dev/probe_neo4j.py
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(str(Path(__file__).parent.parent.parent / ".env"))
except ImportError:
    pass

from neo4j import GraphDatabase


def main() -> None:
    uri  = os.getenv("NEO4J_URI",      "bolt://127.0.0.1:7687")
    user = os.getenv("NEO4J_USER",     "neo4j")
    pw   = os.getenv("NEO4J_PASSWORD")
    if not pw:
        sys.exit("NEO4J_PASSWORD not set — check .env or export it")

    driver = GraphDatabase.driver(uri, auth=(user, pw))
    with driver.session() as s:
        n = s.run("MATCH (n) RETURN count(n) AS c").single()["c"]
        r = s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
        print(f"totals: nodes={n}  rels={r}  (Ship 102'.b golden: 8148 / 14378)")
        print()
        print("--- per-label counts ---")
        for row in s.run("CALL db.labels() YIELD label RETURN label ORDER BY label").data():
            label = row["label"]
            cnt = s.run(
                f"MATCH (n:`{label}`) RETURN count(n) AS c"
            ).single()["c"]
            print(f"  {label:30s}  {cnt}")
        print()
        print("--- RequirementNode per standard ---")
        for row in s.run(
            "MATCH (n:RequirementNode) "
            "RETURN n.standard_id AS s, count(n) AS c "
            "ORDER BY c DESC"
        ).data():
            print(f"  {row['s']:30s}  {row['c']}")
        print()
        print("--- top 10 relationship types ---")
        for row in s.run(
            "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType"
        ).data():
            rt = row["relationshipType"]
            cnt = s.run(
                f"MATCH ()-[r:`{rt}`]->() RETURN count(r) AS c"
            ).single()["c"]
            print(f"  {rt:30s}  {cnt}")
    driver.close()


if __name__ == "__main__":
    main()
