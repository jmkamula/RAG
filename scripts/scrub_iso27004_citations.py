"""
Ship 13'.a (2026-07-21) — scrub `ISO 27004:2016` from citation
footers on the 7 monitoring leaves affected by Ship 12'.c.

Rationale: Ship 12'.b enrolled 27004:2016 but the source PDF
available for curation is the 2009 first edition. Ship 13
skips 27004 to avoid citing wrong § pointers against the wrong
edition. This script surgically removes the 27004 mention
from the 7 leaves' `business_description` citation footer.

Mutations:
  9.1 leaf footer:  `[Related guidance: ISO 27003:2017 · ISO 27004:2016]`
                 →  `[Related guidance: ISO 27003:2017]`
  6 monitoring leaves (A.5.22 / A.5.36 / A.5.37 / A.7.4 /
    A.8.15 / A.8.16):
    footer was `[Related guidance: ISO 27004:2016]` (only 27004)
    → entire footer removed, including the preceding `\n\n`.

Idempotent — safe to re-run.

Usage:
    PYTHONPATH=/data/arioncomply python3 \
        scripts/scrub_iso27004_citations.py [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import re
import sys

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv("/data/arioncomply/.env")


_MONITORING_LEAVES = [
    "A.5.22", "A.5.36", "A.5.37",
    "A.7.4", "A.8.15", "A.8.16",
]
_MIXED_LEAF = "9.1"  # was 27003 + 27004

_RE_27004_INTERIOR = re.compile(r"\s*·\s*ISO 27004:2016\s*")
_RE_27004_ONLY_FOOTER = re.compile(
    r"\n\n\[Related guidance:\s*ISO 27004:2016\s*\]\s*$"
)


def _scrub_business_description(bd: str, ref: str) -> str | None:
    """Return the scrubbed BD, or None if no change needed."""
    if ref == _MIXED_LEAF:
        new_bd = _RE_27004_INTERIOR.sub("", bd)
        if new_bd == bd:
            return None
        return new_bd

    if ref in _MONITORING_LEAVES:
        new_bd = _RE_27004_ONLY_FOOTER.sub("", bd)
        if new_bd == bd:
            return None
        return new_bd.rstrip()

    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")),
    )

    targets = [_MIXED_LEAF] + _MONITORING_LEAVES
    print(f"Ship 13'.a — scrub 27004 from {len(targets)} leaves")
    if args.dry_run:
        print("(dry-run: no writes)")
    print()

    stats = {"updated": 0, "no_change": 0, "missing": 0}
    with driver.session() as s:
        for ref in targets:
            node_id = f"ISO27001:2022:{ref}"
            row = s.run(
                "MATCH (n:RequirementNode {id: $id}) "
                "RETURN coalesce(n.business_description, '') AS bd",
                id=node_id,
            ).single()
            if row is None:
                stats["missing"] += 1
                print(f"  ! {ref:8}  NODE NOT FOUND")
                continue

            current_bd = row["bd"] or ""
            new_bd = _scrub_business_description(current_bd, ref)

            if new_bd is None:
                stats["no_change"] += 1
                print(f"  · {ref:8}  no 27004 reference to scrub")
                continue

            if args.dry_run:
                stats["updated"] += 1
                delta = len(current_bd) - len(new_bd)
                print(f"  + {ref:8}  would trim {delta}c")
                continue

            s.run(
                "MATCH (n:RequirementNode {id: $id}) "
                "SET n.business_description = $bd",
                id=node_id, bd=new_bd,
            )
            stats["updated"] += 1
            delta = len(current_bd) - len(new_bd)
            print(f"  + {ref:8}  trimmed {delta}c")

    print()
    print(f"Updated:   {stats['updated']}")
    print(f"No change: {stats['no_change']}")
    print(f"Missing:   {stats['missing']}")
    return 0 if stats["missing"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
