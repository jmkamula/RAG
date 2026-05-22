"""
ArionComply migration runner — 2026-05-22 GDPR COVERED + B4 explicit_empty.

Executes scripts/migrations/2026_05_22_gdpr_covered_and_b4_explicit_empty.cypher
section by section against the configured Neo4j, with pre/post census on the
GDPR FulfilmentSpec curation_status distribution.

Idempotent: every section's WHERE clause filters on curation_status='uncurated',
so re-running on an already-migrated graph is a no-op.

Usage:
    python3 scripts/migrations/run_2026_05_22_gdpr_covered_and_b4_explicit_empty.py
    python3 scripts/migrations/run_2026_05_22_gdpr_covered_and_b4_explicit_empty.py --dry-run

Exit codes:
    0   migration completed (or already complete) and verified
    2   pre-flight failure (missing env, no GDPR data)
    3   post-flight verification failed
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CYPHER_FILE = Path(__file__).parent / "2026_05_22_gdpr_covered_and_b4_explicit_empty.cypher"

# Target end state for GDPR FulfilmentSpec curation_status distribution.
EXPECTED_GDPR_POST = {
    "curated":         5,
    "explicit_empty": 148,
    "uncurated":      150,
}


def gdpr_census(session) -> dict[str, int]:
    rows = session.run("""
        MATCH (n:RequirementNode {standard_id: 'GDPR:2016/679'})-[:SATISFIED_BY]->(f:FulfilmentSpec)
        RETURN coalesce(f.curation_status, '<null>') AS status, count(*) AS n
    """).data()
    return {row["status"]: row["n"] for row in rows}


def print_census(label: str, census: dict[str, int]) -> None:
    print(f"\n  {label}:")
    total = 0
    for k in sorted(census):
        print(f"    {k:18s} {census[k]:>4}")
        total += census[k]
    print(f"    {'total':18s} {total:>4}")


def load_sections(cypher_path: Path) -> list[tuple[str, str]]:
    """Parse the .cypher file into [(section_label, statement_body)].

    Sections are introduced by lines whose stripped form starts with
    '// SECTION' or '// FINAL VERIFICATION'. The body runs until the next ';'
    that terminates a statement. Pure-comment lines and blank lines inside
    the body are preserved (Neo4j ignores them) but trimmed in display.
    """
    raw = cypher_path.read_text()
    sections: list[tuple[str, str]] = []
    current_label: str | None = None
    current_body: list[str] = []

    section_re = re.compile(r"^//\s*(SECTION\s.+|FINAL VERIFICATION)\s*$")

    for line in raw.splitlines():
        stripped = line.strip()
        m = section_re.match(stripped)
        if m:
            # Starting a new section — flush the previous one if any
            if current_label is not None:
                body = "\n".join(current_body).strip()
                if body:
                    sections.append((current_label, body))
            current_label = m.group(1).strip()
            current_body = []
            continue
        if current_label is not None:
            current_body.append(line)

    if current_label is not None:
        body = "\n".join(current_body).strip()
        if body:
            sections.append((current_label, body))
    return sections


def execute_section(session, label: str, body: str) -> int | None:
    """Run one section. If it returns a count-style row, return that count."""
    # Strip the trailing ; if present — the driver doesn't want it.
    statement = body.rstrip()
    if statement.endswith(";"):
        statement = statement[:-1]
    result = session.run(statement)
    rows = result.data()
    # Sections RETURN one of:
    #   {'cluster': 'COVERED', 'n': 47}
    #   {'curation_status': 'curated', 'n': 5}   (verification)
    if rows and len(rows) == 1 and "n" in rows[0] and "cluster" in rows[0]:
        return rows[0]["n"]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Read state and print section plan; do not write")
    args = parser.parse_args()

    load_dotenv(REPO_ROOT / ".env")
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    if not (uri and user and password):
        print("ERROR: NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD not set in .env")
        return 2

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session() as s:
            print(f"Cypher file: {CYPHER_FILE.name}")
            print("Pre-flight GDPR census:")
            pre = gdpr_census(s)
            print_census("BEFORE", pre)

            if not pre or sum(pre.values()) == 0:
                print("\nERROR: no GDPR FulfilmentSpecs found — refusing to run.")
                return 2

            sections = load_sections(CYPHER_FILE)
            if not sections:
                print("\nERROR: parsed 0 sections from cypher file — check section markers.")
                return 2

            if args.dry_run:
                print(f"\n[DRY RUN] would execute {len(sections)} section(s):")
                for label, _ in sections:
                    print(f"  - {label}")
                return 0

            print(f"\nExecuting {len(sections)} section(s):")
            for label, body in sections:
                n = execute_section(s, label, body)
                tag = f" ({n} rows touched)" if n is not None else ""
                print(f"  -> {label}{tag}")

            print("\nPost-flight GDPR census:")
            post = gdpr_census(s)
            print_census("AFTER", post)

            # Compare against expected
            expected = EXPECTED_GDPR_POST
            mismatches = []
            for k, v in expected.items():
                if post.get(k, 0) != v:
                    mismatches.append((k, post.get(k, 0), v))
            if mismatches:
                print("\nWARNING: post-flight differs from expected distribution:")
                for k, actual, want in mismatches:
                    print(f"    {k:18s} actual={actual}  expected={want}  delta={actual - want:+d}")
                print("\n(This can be benign if the triage estimate was slightly off, but worth eyeballing.)")
                return 3

            print("\nMigration verified — distribution matches expected.")
            return 0
    finally:
        driver.close()


if __name__ == "__main__":
    sys.exit(main())
