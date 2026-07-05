"""
ArionComply — Neo4j subject / role_owner backfill (Phase 1)

Reads the role model metadata seeded in Postgres by schema_v60 and
propagates it onto Neo4j RequirementNode and EvidenceRequirement nodes:

  RequirementNode        → subject[], role_owner (from parent standard)
  EvidenceRequirement    → subject[], role_owner (from parent standard)

This is a one-shot backfill for Phase 1 of the framework role model
refactor (design conversation 2026-07-05). No behavior change — nodes
gain properties that Phase 2 (DEMONSTRATES propagation) and Phase 3
(role-aware extraction) will read.

Safe to re-run — writes are idempotent via SET (not MERGE-with-ON-CREATE).

Usage:
    PYTHONPATH=/data/arioncomply python3 scripts/backfill_neo4j_subject_role.py
    PYTHONPATH=/data/arioncomply python3 scripts/backfill_neo4j_subject_role.py --dry-run
"""
from __future__ import annotations
import argparse
import os
import sys

import psycopg2
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv("/data/arioncomply/.env")


def fetch_role_metadata(pg_conn) -> dict[str, dict]:
    """Return {standard_id: {role, subject, scope_type, mandate_source}}."""
    with pg_conn.cursor() as cur:
        cur.execute("""
            SELECT id, role, subject, scope_type, mandate_source
            FROM standards
            WHERE role IS NOT NULL
        """)
        rows = cur.fetchall()
    return {
        row[0]: {
            "role":           row[1],
            "subject":        list(row[2] or []),
            "scope_type":     row[3],
            "mandate_source": row[4],
        }
        for row in rows
    }


def backfill(driver, meta: dict[str, dict], dry_run: bool) -> None:
    for std_id, m in sorted(meta.items()):
        with driver.session() as s:
            counts = s.run(
                """
                MATCH (n) WHERE n.standard_id = $std_id
                  AND (n:RequirementNode OR n:EvidenceRequirement)
                RETURN labels(n) AS labels, count(*) AS c
                """,
                std_id=std_id,
            ).data()
            total = sum(r["c"] for r in counts)
            breakdown = ", ".join(f"{r['labels'][0]}={r['c']}" for r in counts)
            print(f"\n{std_id}: {total} nodes ({breakdown})")
            print(f"  role={m['role']}  subject={m['subject']}  "
                  f"scope_type={m['scope_type']}  mandate_source={m['mandate_source']}")

            if dry_run:
                continue

            result = s.run(
                """
                MATCH (n) WHERE n.standard_id = $std_id
                  AND (n:RequirementNode OR n:EvidenceRequirement)
                SET n.subject        = $subject,
                    n.role_owner     = $role,
                    n.scope_type     = $scope_type,
                    n.mandate_source = $mandate_source
                RETURN count(n) AS updated
                """,
                std_id=std_id,
                subject=m["subject"],
                role=m["role"],
                scope_type=m["scope_type"],
                mandate_source=m["mandate_source"],
            ).single()
            print(f"  ✓ updated {result['updated']} nodes")


def verify(driver) -> None:
    with driver.session() as s:
        print("\n── Verification ─────────────────────────────────────────────")
        rows = s.run(
            """
            MATCH (n:EvidenceRequirement)
            RETURN n.standard_id AS std, n.role_owner AS role,
                   n.subject AS subject, count(*) AS c
            ORDER BY std, role
            """
        ).data()
        for r in rows:
            print(f"  {r['std']:20s} role={r['role']!r:14s} "
                  f"subject={r['subject']!r:30s} count={r['c']}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pg_conn = psycopg2.connect(
        host="127.0.0.1",
        user="arioncomply",
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname="arioncomply_compliance",
    )
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")),
    )

    try:
        meta = fetch_role_metadata(pg_conn)
        if not meta:
            print("No role metadata found in standards table — run schema_v60 first.")
            return 1
        backfill(driver, meta, args.dry_run)
        if not args.dry_run:
            verify(driver)
    finally:
        pg_conn.close()
        driver.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
