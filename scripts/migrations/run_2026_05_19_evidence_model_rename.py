"""
ArionComply migration runner — 2026-05-19 evidence model rename.

Executes scripts/migrations/2026_05_19_evidence_model_rename.cypher phase by
phase against the configured Neo4j, asserting pre/post counts. Idempotent:
re-running on an already-migrated graph is a no-op (the .cypher phases are
all guarded; this runner verifies the end state matches expectations either
way).

Usage:
    python3 scripts/migrations/run_2026_05_19_evidence_model_rename.py
    python3 scripts/migrations/run_2026_05_19_evidence_model_rename.py --dry-run

Exit codes:
    0   migration completed (or already complete) and verified
    2   pre-flight inconsistency — refuses to run
    3   post-flight verification failed
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CYPHER_FILE = Path(__file__).with_suffix(".cypher").parent / "2026_05_19_evidence_model_rename.cypher"

EXPECTED_FRESH = {
    "DocumentRequirement":  18,
    "EvidenceRequirement":   0,
    "FulfilmentSpec":        0,
    "RequirementNode":     429,
    "REQUIRES_DOCUMENT":    21,
    "REQUIRES_EVIDENCE":     0,
    "SATISFIED_BY":          0,
}

EXPECTED_MIGRATED = {
    "DocumentRequirement":   0,
    "EvidenceRequirement":  18,
    "FulfilmentSpec":      429,
    "RequirementNode":     429,
    "REQUIRES_DOCUMENT":     0,
    "REQUIRES_EVIDENCE":    21,
    "SATISFIED_BY":        429,
}


def take_census(session) -> dict[str, int]:
    queries = {
        "DocumentRequirement":  "MATCH (n:DocumentRequirement)  RETURN count(n) AS c",
        "EvidenceRequirement":  "MATCH (n:EvidenceRequirement)  RETURN count(n) AS c",
        "FulfilmentSpec":       "MATCH (n:FulfilmentSpec)       RETURN count(n) AS c",
        "RequirementNode":      "MATCH (n:RequirementNode)      RETURN count(n) AS c",
        "REQUIRES_DOCUMENT":    "MATCH ()-[r:REQUIRES_DOCUMENT]->() RETURN count(r) AS c",
        "REQUIRES_EVIDENCE":    "MATCH ()-[r:REQUIRES_EVIDENCE]->() RETURN count(r) AS c",
        "SATISFIED_BY":         "MATCH ()-[r:SATISFIED_BY]->()      RETURN count(r) AS c",
    }
    return {k: session.run(q).single()["c"] for k, q in queries.items()}


def classify_state(census: dict[str, int]) -> str:
    if census == EXPECTED_FRESH:
        return "fresh"
    if census == EXPECTED_MIGRATED:
        return "migrated"
    return "inconsistent"


def print_census(label: str, census: dict[str, int]) -> None:
    print(f"\n  {label}:")
    for k, v in census.items():
        print(f"    {k:25s} {v:>4}")


def load_phases(cypher_path: Path) -> list[tuple[str, str]]:
    """Split the .cypher file on '// === PHASE' markers, returning [(label, body)]."""
    raw = cypher_path.read_text()
    phases: list[tuple[str, str]] = []
    current_label: str | None = None
    current_body: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("// === PHASE"):
            if current_label is not None:
                body = "\n".join(current_body).strip()
                if body:
                    phases.append((current_label, body))
            current_label = stripped[3:].strip()  # drop the '// ' prefix
            current_body = []
            continue
        if current_label is not None:
            current_body.append(line)
    if current_label is not None:
        body = "\n".join(current_body).strip()
        if body:
            phases.append((current_label, body))
    return phases


def execute_phase(session, label: str, body: str) -> None:
    print(f"  → {label}")
    session.run(body).consume()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Read state and print plan; do not write")
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
            print("Pre-flight census:")
            pre = take_census(s)
            print_census("BEFORE", pre)
            state = classify_state(pre)
            print(f"\n  state: {state}")

            if state == "inconsistent":
                print("\nERROR: graph is in an inconsistent state — neither fresh nor migrated.")
                print("Expected one of:")
                print_census("fresh", EXPECTED_FRESH)
                print_census("migrated", EXPECTED_MIGRATED)
                return 2

            if args.dry_run:
                print("\n[DRY RUN] would execute the following phases:")
                for label, _ in load_phases(CYPHER_FILE):
                    print(f"  - {label}")
                return 0

            if state == "fresh":
                print("\nExecuting migration phases:")
                for label, body in load_phases(CYPHER_FILE):
                    execute_phase(s, label, body)
            else:
                print("\nGraph already migrated — skipping phases, verifying end state only.")

            print("\nPost-flight census:")
            post = take_census(s)
            print_census("AFTER", post)
            if post != EXPECTED_MIGRATED:
                print("\nERROR: post-flight does not match expected migrated state.")
                print_census("expected", EXPECTED_MIGRATED)
                return 3

            # Sanity: every curated spec has at least one leaf
            curated_no_leaves = s.run("""
                MATCH (fs:FulfilmentSpec {curation_status: 'curated'})
                WHERE NOT (fs)-[:REQUIRES_EVIDENCE]->()
                RETURN fs.id AS id
            """).data()
            if curated_no_leaves:
                print(f"\nERROR: {len(curated_no_leaves)} curated specs have no leaves:")
                for row in curated_no_leaves:
                    print(f"    {row['id']}")
                return 3

            status_dist = s.run("""
                MATCH (fs:FulfilmentSpec)
                RETURN fs.curation_status AS status, count(*) AS n
                ORDER BY n DESC
            """).data()
            print("\n  FulfilmentSpec by curation_status:")
            for row in status_dist:
                print(f"    {row['status']:20s} {row['n']:>4}")

            print("\nMigration verified.")
            return 0
    finally:
        driver.close()


if __name__ == "__main__":
    sys.exit(main())
