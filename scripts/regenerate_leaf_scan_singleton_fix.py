#!/usr/bin/env python3
"""
Ship 28'.b — Bulk regeneration for the singleton fingerprint fix.

Walks db/must_fingerprints/*.yaml, checks Ship 17'.b's
`_is_auto_generated` marker (`# Auto-generated` in first 6 lines),
and re-emits every auto-generated file via the updated
gen_leaf_scan_catalog.py::_render_yaml (which now suppresses
redundant singleton keyword sets).

Hand-authored files are skipped based on the header marker.

Usage
    PYTHONPATH=/data/arioncomply python3 scripts/regenerate_leaf_scan_singleton_fix.py
    PYTHONPATH=/data/arioncomply python3 scripts/regenerate_leaf_scan_singleton_fix.py --dry-run
    PYTHONPATH=/data/arioncomply python3 scripts/regenerate_leaf_scan_singleton_fix.py --limit 5

Emits a summary: files touched / files skipped / files unchanged.
Read-only unless invoked without --dry-run (default is write mode
because that's the point of Ship 28'.b).
"""
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path

# ensure repo root on path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from neo4j import GraphDatabase
from scripts.gen_leaf_scan_catalog import (
    _fetch_leaves,
    _render_yaml,
    _catalog_filename,
)


CATALOG_DIR = ROOT / "db" / "must_fingerprints"
AUTO_GEN_MARKER = "# Auto-generated"


def _is_auto_generated(path: Path) -> bool:
    """Same discipline as Ship 17'.b — check first 6 lines for the
    marker string. Hand-authored files use different header prose
    (e.g. 'Reviewed-from-skeleton')."""
    try:
        with open(path, "r") as f:
            for _ in range(6):
                line = f.readline()
                if not line:
                    break
                if AUTO_GEN_MARKER in line:
                    return True
    except Exception:
        return False
    return False


def _target_from_file(path: Path) -> str | None:
    """Extract `target_evidence_requirement` from the YAML.

    Direct string parse — avoids yaml.safe_load overhead + handles
    files that don't strictly parse (rare)."""
    try:
        with open(path, "r") as f:
            for _ in range(30):  # target is in the first 20 lines
                line = f.readline()
                if not line:
                    break
                if line.startswith("target_evidence_requirement:"):
                    val = line.split(":", 1)[1].strip().strip('"').strip("'")
                    return val or None
    except Exception:
        return None
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true",
                    help="Don't write; report what would change.")
    ap.add_argument("--limit", type=int, default=0,
                    help="Only process the first N auto-generated files (for testing).")
    args = ap.parse_args()

    uri  = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    pw   = os.getenv("NEO4J_PASSWORD")
    if not (uri and user and pw):
        print("ERROR: NEO4J_URI/USER/PASSWORD not set", file=sys.stderr)
        return 1

    files = sorted(CATALOG_DIR.glob("*.yaml"))
    print(f"Found {len(files)} .yaml files in {CATALOG_DIR}")

    auto_gen_files = [f for f in files if _is_auto_generated(f)]
    print(f"Auto-generated (regeneratable): {len(auto_gen_files)}")
    print(f"Hand-authored (skipped):        {len(files) - len(auto_gen_files)}")

    if args.limit:
        auto_gen_files = auto_gen_files[:args.limit]
        print(f"Limited to first {len(auto_gen_files)} files (--limit)")
    print()

    neo = GraphDatabase.driver(uri, auth=(user, pw))
    n_written  = 0
    n_unchanged = 0
    n_skipped  = 0
    n_error    = 0

    try:
        for i, path in enumerate(auto_gen_files, 1):
            leaf_id = _target_from_file(path)
            if not leaf_id:
                print(f"  [{i:3d}/{len(auto_gen_files)}] SKIP (no target): {path.name}")
                n_skipped += 1
                continue

            leaves = _fetch_leaves(neo, control_ref=None, leaf_id=leaf_id)
            if not leaves:
                print(f"  [{i:3d}/{len(auto_gen_files)}] SKIP (no leaf in Neo4j): {path.name}")
                n_skipped += 1
                continue

            leaf = leaves[0]
            new_yaml = _render_yaml(leaf)
            existing = path.read_text() if path.exists() else ""
            if new_yaml == existing:
                n_unchanged += 1
                continue

            action = "would_write" if args.dry_run else "WROTE"
            if not args.dry_run:
                try:
                    path.write_text(new_yaml)
                except Exception as e:
                    print(f"  [{i:3d}/{len(auto_gen_files)}] ERROR: {path.name}: {e}")
                    n_error += 1
                    continue
            print(f"  [{i:3d}/{len(auto_gen_files)}] {action}: {path.name}")
            n_written += 1
    finally:
        neo.close()

    print()
    print("=" * 60)
    print(f"Files written:    {n_written}")
    print(f"Files unchanged:  {n_unchanged}")
    print(f"Files skipped:    {n_skipped}")
    print(f"Errors:           {n_error}")
    if args.dry_run:
        print("(dry-run — nothing written)")
    return 0 if n_error == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
