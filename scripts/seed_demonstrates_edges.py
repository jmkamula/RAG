"""
ArionComply — DEMONSTRATES edge seed (Phase 2a)

Adds DEMONSTRATES edges from PROGRAM/EXTENSION controls to OBLIGATION
controls, based on the existing cross-framework edges. This is the
deterministic replacement for xfw obligation propagation:

  Meaning:  source demonstrates target
  Direction: source role_owner ∈ {program, extension}
             target role_owner = obligation

Post-Phase 2b, when a source control has Comply/OFI posture, the
demonstrated obligation controls receive a propagated in-memory
posture (Phase 5 retires the legacy xfw layer).

Migration source (all cross-framework edges observed 2026-07-05):
  ISO27001 IMPLEMENTS/SUPPORTS/ENABLES/GOVERNANCE → GDPR:  149 edges
  ISO27701 IMPLEMENTS                             → GDPR:   86 edges
  ---
  Total:                                                    235 edges

The GDPR → ISO reverse edges (implements/supports back to ISO)
represent the auditor navigation direction ("for this GDPR article,
which ISO controls implement it") — NOT demonstration. They stay
as-is; they are read by the layered answer path.

The ISO27701 SUPPORTS ISO27001 edges (26) represent the `extends`
relationship at the control level. They stay as-is; they are what
the loader uses today to compute the extension→program dependency
graph.

Safe to re-run — MERGE is idempotent on the (source_id, target_id,
via_edge) tuple.

Usage:
    PYTHONPATH=/data/arioncomply python3 scripts/seed_demonstrates_edges.py
    PYTHONPATH=/data/arioncomply python3 scripts/seed_demonstrates_edges.py --dry-run
"""
from __future__ import annotations
import argparse
import os
import sys

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv("/data/arioncomply/.env")


# Source edge types we consider "demonstration-shaped" when going from
# a program/extension to an obligation. Every one of these expresses
# "the source control contributes to compliance with the target
# obligation" in the curated relationship catalog.
_DEMONSTRATION_EDGE_TYPES = ["IMPLEMENTS", "SUPPORTS", "ENABLES", "GOVERNANCE"]


def find_candidate_edges(driver) -> list[dict]:
    """Return every (source, target, via_edge, props) tuple that
    should become a DEMONSTRATES edge. Filters by role_owner so the
    direction is unambiguously PROGRAM/EXTENSION → OBLIGATION."""
    query = """
    MATCH (src:RequirementNode)-[r]->(tgt:RequirementNode)
    WHERE type(r) IN $edge_types
      AND src.role_owner IN ['program', 'extension']
      AND tgt.role_owner = 'obligation'
    RETURN
      src.id           AS src_id,
      src.standard_id  AS src_std,
      src.role_owner   AS src_role,
      tgt.id           AS tgt_id,
      tgt.standard_id  AS tgt_std,
      type(r)          AS via_edge,
      r.rationale      AS rationale,
      r.citation       AS citation,
      r.applies_when   AS applies_when,
      r.role           AS strength,
      r.managed_by     AS managed_by
    ORDER BY src.standard_id, tgt.id
    """
    with driver.session() as s:
        return list(s.run(query, edge_types=_DEMONSTRATION_EDGE_TYPES))


def create_demonstrates(driver, edges: list[dict], dry_run: bool) -> int:
    """Idempotent MERGE of DEMONSTRATES edges. Uniqueness key is
    (source, target, via_edge) so re-runs don't create duplicates and
    the provenance stays traceable back to the original edge."""
    created = 0
    with driver.session() as s:
        for e in edges:
            if dry_run:
                created += 1
                continue
            result = s.run(
                """
                MATCH (src:RequirementNode {id: $src_id})
                MATCH (tgt:RequirementNode {id: $tgt_id})
                MERGE (src)-[d:DEMONSTRATES {via_edge: $via_edge}]->(tgt)
                  ON CREATE SET
                      d.rationale       = $rationale,
                      d.citation        = $citation,
                      d.applies_when    = $applies_when,
                      d.strength        = $strength,
                      d.managed_by      = $managed_by,
                      d.src_standard    = $src_std,
                      d.tgt_standard    = $tgt_std,
                      d.subject_bridge  = 'cross_subject',
                      d.created_at      = datetime()
                  ON MATCH SET
                      d.rationale       = coalesce($rationale, d.rationale),
                      d.strength        = coalesce($strength, d.strength),
                      d.updated_at      = datetime()
                RETURN d.via_edge AS via
                """,
                src_id=e["src_id"],
                tgt_id=e["tgt_id"],
                via_edge=e["via_edge"],
                rationale=e["rationale"],
                citation=e["citation"],
                applies_when=e["applies_when"],
                strength=e["strength"],
                managed_by=e["managed_by"],
                src_std=e["src_std"],
                tgt_std=e["tgt_std"],
            ).single()
            if result:
                created += 1
    return created


def verify(driver) -> None:
    with driver.session() as s:
        print("\n── DEMONSTRATES edges by source → target standard ──")
        for r in s.run("""
            MATCH (src)-[d:DEMONSTRATES]->(tgt)
            RETURN
              src.standard_id AS src_std,
              tgt.standard_id AS tgt_std,
              d.via_edge      AS via,
              count(*)        AS c
            ORDER BY src_std, via
        """):
            print(f"  {r['src_std']:<15s} → {r['tgt_std']:<15s} "
                  f"via {r['via']:<11s} {r['c']}")

        total = s.run("MATCH ()-[d:DEMONSTRATES]->() RETURN count(d) AS c").single()["c"]
        print(f"\n  TOTAL: {total} DEMONSTRATES edges")

        # Direction check: any DEMONSTRATES that violates PROGRAM/EXTENSION → OBLIGATION?
        bad = s.run("""
            MATCH (src)-[d:DEMONSTRATES]->(tgt)
            WHERE NOT (src.role_owner IN ['program', 'extension']
                       AND tgt.role_owner = 'obligation')
            RETURN count(*) AS c
        """).single()["c"]
        if bad:
            print(f"\n  ⚠ {bad} DEMONSTRATES edges violate role direction — investigate")
        else:
            print("  ✓ all edges respect PROGRAM/EXTENSION → OBLIGATION direction")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")),
    )

    try:
        edges = find_candidate_edges(driver)
        print(f"Candidate edges (PROGRAM/EXTENSION → OBLIGATION): {len(edges)}")

        # Break down by via_edge
        by_via: dict[tuple, int] = {}
        for e in edges:
            k = (e["src_std"], e["via_edge"], e["tgt_std"])
            by_via[k] = by_via.get(k, 0) + 1
        for (src, via, tgt), c in sorted(by_via.items()):
            print(f"  {src:<15s} -{via:>12s}-> {tgt:<15s}  {c}")

        if args.dry_run:
            print("\n[dry-run] not writing")
            return 0

        created = create_demonstrates(driver, edges, args.dry_run)
        print(f"\n✓ processed {created} DEMONSTRATES edges (idempotent MERGE)")
        verify(driver)
    finally:
        driver.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
