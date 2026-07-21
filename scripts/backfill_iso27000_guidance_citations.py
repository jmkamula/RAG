"""
Ship 12'.c (2026-07-21) — append guidance citation stubs to
`business_description` on the 38 target ISO 27001 leaves.

Purpose
-------
Ship 12'.a audited the ISO 27000-family grounding gap: we cite
ISO 27002:2022 as authority for Annex A controls but have zero
grounding to 27003 (ISMS clause implementation guidance), 27004
(monitoring, measurement, analysis, evaluation), and 27005
(information security risk management).

Ship 12'.b enrolled the three standards in the `standards` table
+ output-gateway vocabulary. This script does the citation-stub
pass on existing 27001 leaves: appends a
`\n\n[Related guidance: ISO 27005:2022]` footer (or multi-family
variant) to each target leaf's `business_description`.

Scope: 38 unique leaves —
- 26 ISMS clauses  (4.x / 5.x / 6.x / 7.x / 8.x / 9.x / 10.x) → 27003
- 7 monitoring     (9.1 + A.5.22 + A.5.36 + A.5.37 + A.7.4 + A.8.15 + A.8.16) → 27004
- 14 risk-adjacent (6.1.x / 6.3 / 8.x / A.5.5 / A.5.7 / A.5.24 / A.5.29 / A.5.30 / A.7.5) → 27005
Overlaps handled: 9.1 gets 27003+27004; 6.1/6.1.x/6.3/8.x get 27003+27005.

Idempotent — running twice does nothing on the second pass. Uses
a fingerprint check for `[Related guidance:` in the existing text.

Not curator MUST-level content. This lands authority pointers so
Evidence Package prose, chat citation prompts, and future
generator arcs know which standards to consult when the source
texts land.

Usage
-----
    PYTHONPATH=/data/arioncomply python3 \
        scripts/backfill_iso27000_guidance_citations.py [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, List

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv("/data/arioncomply/.env")


_CITATION_MARKER = "[Related guidance:"


_LEAVES_27003_ONLY: List[str] = [
    "4.1", "4.2", "4.3", "4.4",
    "5.1", "5.2", "5.3",
    "6.2",
    "7.1", "7.2", "7.3", "7.4", "7.5",
    "9.2", "9.3",
    "10.1", "10.2",
]

_LEAVES_27003_AND_27005: List[str] = [
    "6.1", "6.1.1", "6.1.2", "6.1.3", "6.3",
    "8.1", "8.2", "8.3",
]

_LEAVES_27003_AND_27004: List[str] = [
    "9.1",
]

_LEAVES_27004_ONLY: List[str] = [
    "A.5.22", "A.5.36", "A.5.37",
    "A.7.4", "A.8.15", "A.8.16",
]

_LEAVES_27005_ONLY: List[str] = [
    "A.5.5", "A.5.7", "A.5.24", "A.5.29", "A.5.30", "A.7.5",
]


def _citation_for(guidance_ids: List[str]) -> str:
    """Render the citation footer for a given set of guidance
    standards. Ordered 27003 → 27004 → 27005 for readability."""
    order = ["ISO 27003:2017", "ISO 27004:2016", "ISO 27005:2022"]
    ordered = [g for g in order if g in guidance_ids]
    return f"\n\n[Related guidance: {' · '.join(ordered)}]"


def _build_target_map() -> Dict[str, str]:
    """Return {leaf_ref: citation_footer} keyed by control ref."""
    out: Dict[str, str] = {}
    for r in _LEAVES_27003_ONLY:
        out[r] = _citation_for(["ISO 27003:2017"])
    for r in _LEAVES_27003_AND_27005:
        out[r] = _citation_for(["ISO 27003:2017", "ISO 27005:2022"])
    for r in _LEAVES_27003_AND_27004:
        out[r] = _citation_for(["ISO 27003:2017", "ISO 27004:2016"])
    for r in _LEAVES_27004_ONLY:
        out[r] = _citation_for(["ISO 27004:2016"])
    for r in _LEAVES_27005_ONLY:
        out[r] = _citation_for(["ISO 27005:2022"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")),
    )

    targets = _build_target_map()
    print(f"Ship 12'.c backfill — {len(targets)} target leaves")
    if args.dry_run:
        print("(dry-run: no writes)")
    print()

    stats = {"updated": 0, "already_marked": 0, "missing_node": 0}
    with driver.session() as s:
        for ref, footer in sorted(targets.items()):
            node_id = f"ISO27001:2022:{ref}"
            row = s.run(
                "MATCH (n:RequirementNode {id: $id}) "
                "RETURN coalesce(n.business_description, '') AS bd, n.title AS title",
                id=node_id,
            ).single()
            if row is None:
                stats["missing_node"] += 1
                print(f"  ! {ref:8}  NODE NOT FOUND ({node_id})")
                continue

            current_bd: str = row["bd"] or ""
            title: str = row["title"] or ""

            if _CITATION_MARKER in current_bd:
                stats["already_marked"] += 1
                print(f"  · {ref:8}  already has citation footer")
                continue

            new_bd = (current_bd + footer).strip() if current_bd else footer.strip()

            if args.dry_run:
                stats["updated"] += 1
                print(f"  + {ref:8}  \"{title[:40]}\"  will append: {footer.strip()}")
                continue

            s.run(
                "MATCH (n:RequirementNode {id: $id}) "
                "SET n.business_description = $bd",
                id=node_id, bd=new_bd,
            )
            stats["updated"] += 1
            print(f"  + {ref:8}  \"{title[:40]}\"  appended {footer.strip()}")

    print()
    print(f"Updated:        {stats['updated']}")
    print(f"Already marked: {stats['already_marked']}")
    print(f"Missing node:   {stats['missing_node']}")
    return 0 if stats["missing_node"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
