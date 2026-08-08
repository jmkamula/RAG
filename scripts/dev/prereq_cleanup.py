"""
Ship 57' cleanup — drop dangling-ref prereq entries + dedupe (ref, std)
entries per file. Deterministic pass over the prereq corpus.

Dangling = prereq.ref does not resolve to any RequirementNode in Neo4j.
LLM formatting slips produce ~14 such entries in the current corpus
(malformed refs like 'GDPR:2016/679:Art.35', 'org_chart', bare
standard-ids). The curator can add cleaner prereqs later if warranted;
dropping is safer than trying to normalize the malformed strings.

Dedupe = collapse repeated (ref, standard_id) entries within one file,
keeping the first occurrence.

Idempotent. Run after each prereq bulk regeneration.

Usage:
    PYTHONPATH=/data/arioncomply python3 scripts/dev/prereq_cleanup.py [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent / "enrichment" / "prerequisites"


def _valid_refs_from_neo4j() -> set[str]:
    from neo4j import GraphDatabase
    d = GraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
        auth=(os.getenv("NEO4J_USER", "neo4j"),
              os.getenv("NEO4J_PASSWORD", "arionneo4j@2026")),
    )
    with d.session() as s:
        rows = s.run("MATCH (r:RequirementNode) RETURN r.ref AS ref").data()
    return {r["ref"] for r in rows if r.get("ref")}


def process_file(path: Path, valid_refs: set[str], dry_run: bool) -> tuple[int, int]:
    """Return (dangling_dropped, dup_dropped)."""
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        return 0, 0
    prereqs = data.get("prerequisites") or []
    if not isinstance(prereqs, list):
        return 0, 0

    dropped_dangling = 0
    dropped_dup = 0
    seen: set[tuple] = set()
    kept: list = []
    for p in prereqs:
        if not isinstance(p, dict):
            kept.append(p); continue
        pref = p.get("ref")
        pstd = p.get("standard_id")
        if pref not in valid_refs:
            dropped_dangling += 1
            continue
        key = (pref, pstd)
        if key in seen:
            dropped_dup += 1
            continue
        seen.add(key)
        kept.append(p)

    if (dropped_dangling or dropped_dup) and not dry_run:
        data["prerequisites"] = kept
        path.write_text(yaml.safe_dump(
            data, sort_keys=False, allow_unicode=True,
            default_flow_style=False, width=100,
        ))
    return dropped_dangling, dropped_dup


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    try:
        valid_refs = _valid_refs_from_neo4j()
    except Exception as e:
        print(f"FATAL: Neo4j unavailable ({e})", file=sys.stderr)
        sys.exit(1)
    print(f"Valid refs from Neo4j: {len(valid_refs)}")

    files = sorted(ROOT.rglob("*.yaml"))
    total_dangling = total_dup = files_changed = 0
    for f in files:
        d, u = process_file(f, valid_refs, args.dry_run)
        if d or u:
            files_changed += 1
            total_dangling += d
            total_dup += u

    verb = "would drop" if args.dry_run else "dropped"
    print(f"Files scanned:            {len(files)}")
    print(f"Files touched:            {files_changed}")
    print(f"Dangling entries {verb}: {total_dangling}")
    print(f"Duplicate entries {verb}: {total_dup}")


if __name__ == "__main__":
    main()
