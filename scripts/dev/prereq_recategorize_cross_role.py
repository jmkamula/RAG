"""
Re-categorize `cross_role` prerequisites that are actually same-framework.

Ship 57' cleanup — the gpt-4.1 generator interprets `cross_role` as
"cross-domain within the same framework" instead of the README's
"cross-role = different framework role". This deterministically rewrites
any `category: cross_role` entry whose prereq.standard_id matches the
target's standard_id back to `direct`. Substance untouched.

Idempotent + safe to run mid-bulk (the generator only writes files that
don't yet exist).

Usage:
    PYTHONPATH=/data/arioncomply python3 \\
        scripts/dev/prereq_recategorize_cross_role.py [--dry-run]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent / "enrichment" / "prerequisites"


def process_file(path: Path, dry_run: bool) -> tuple[int, list[str]]:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        return 0, []
    target_std = data.get("standard_id")
    prereqs = data.get("prerequisites") or []
    if not isinstance(prereqs, list):
        return 0, []

    n = 0
    samples: list[str] = []
    for p in prereqs:
        if not isinstance(p, dict):
            continue
        if p.get("category") != "cross_role":
            continue
        if p.get("standard_id") != target_std:
            continue
        p["category"] = "direct"
        n += 1
        samples.append(f"{p.get('ref')} ({target_std})")

    if n and not dry_run:
        path.write_text(yaml.safe_dump(
            data, sort_keys=False, allow_unicode=True,
            default_flow_style=False, width=100,
        ))
    return n, samples


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Report what would change without writing.")
    args = ap.parse_args()

    files = sorted(ROOT.rglob("*.yaml"))
    files_changed = 0
    total_rewrites = 0
    sample_lines: list[str] = []
    for f in files:
        n, samples = process_file(f, args.dry_run)
        if n:
            files_changed += 1
            total_rewrites += n
            if len(sample_lines) < 10:
                for s in samples[:2]:
                    sample_lines.append(f"  {f.relative_to(ROOT)}  cross_role→direct  {s}")

    verb = "would rewrite" if args.dry_run else "rewrote"
    print(f"Files scanned:    {len(files)}")
    print(f"Files {verb}: {files_changed}")
    print(f"Entries {verb}: {total_rewrites}")
    if sample_lines:
        print()
        print("Samples:")
        for line in sample_lines:
            print(line)


if __name__ == "__main__":
    main()
