"""
Run leaf-driven scan back-bind across all available catalogs on a tenant.

Per [[leaf-scan-catalog-campaign-2026-06-14]]: scan inspects approved
unbound findings on tenant, attempts to bind each one to an unmet
checklist_item_id on the same control via fingerprint matching, and
persists new findings with inference_source='leaf_scan' (review_status
defaults to 'pending' for tenant Stage-1 review).

The scan is non-destructive: it never modifies existing findings, only
adds new ones. The new findings reference the same document_id and
include a [leaf-scan back-bind from finding <id>] marker on the excerpt.

Usage:
  PYTHONPATH=/data/arioncomply python3 scripts/run_leaf_scan.py [--dry] \
      [--tenant <uuid>] [--leaf <leaf_id>]
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import Counter

import psycopg2

from rag.intake.leaf_driven_scan import scan, persist


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("--tenant", default="00000000-0000-0000-0000-000000000001",
                   help="tenant UUID (default: arion demo)")
    p.add_argument("--leaf",   default=None,
                   help="restrict to a single leaf_id (default: all catalogs)")
    p.add_argument("--dry",    action="store_true",
                   help="report proposals, do not persist")
    args = p.parse_args()

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set", file=sys.stderr)
        return 1

    conn = psycopg2.connect(db_url)
    try:
        proposals = scan(conn, args.tenant, args.leaf)

        if not proposals:
            print("No proposals — no matchable unbound findings.")
            return 0

        by_control = Counter(p.control_ref for p in proposals)
        by_doc     = Counter(p.document_id for p in proposals)
        by_must    = Counter(p.must_id for p in proposals)

        print(f"Proposals: {len(proposals)}")
        print(f"Distinct controls: {len(by_control)}")
        print(f"Distinct docs:     {len(by_doc)}")
        print(f"Distinct MUSTs:    {len(by_must)}")
        print()
        print("Top-10 controls by proposals:")
        for ref, n in by_control.most_common(10):
            print(f"  {ref:<15s} {n}")
        print()

        if args.dry:
            print("DRY RUN — no rows written. Re-run without --dry to persist.")
            # Show a sample
            print("\nSample proposals (first 5):")
            for p in proposals[:5]:
                print(f"  {p.control_ref} -> {p.must_id}")
                print(f"    excerpt: {(p.excerpt or '')[:80]}...")
            return 0

        n = persist(conn, args.tenant, proposals)
        print(f"Persisted {n} new document_findings rows "
              f"(inference_source='leaf_scan', review_status='pending')")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
