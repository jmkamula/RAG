#!/usr/bin/env python3
"""
Purge long-tail failed document_uploads rows.

Pairs with the cascade-on-success delete in api_server.upload_document —
that cascade handles failed rows the user eventually retries. This script
handles the never-retried tail.

Default behaviour: dry-run, report what *would* be deleted, exit 0.
Pass --apply to actually purge. --days N overrides the 30-day default.

Cron example (nightly at 03:30):
  30 3 * * * cd /data/arioncomply && \
      PYTHONPATH=. python3 scripts/purge_failed_uploads.py --apply >> \
      /var/log/arioncomply/purge_failed_uploads.log 2>&1
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.posture_loader import build_pg_conn


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=30,
                    help="Purge failed rows older than N days (default 30)")
    ap.add_argument("--apply", action="store_true",
                    help="Actually purge (default is dry-run)")
    args = ap.parse_args()

    conn = build_pg_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM fn_purge_failed_uploads(%s, %s)",
                (args.days, not args.apply),
            )
            rows = cur.fetchall()

        mode = "APPLY" if args.apply else "DRY-RUN"
        if not rows:
            print(f"[{mode}] No failed uploads older than {args.days} days.")
            return 0

        total = 0
        print(f"[{mode}] Failed-upload purge — threshold {args.days} days:")
        for tenant_id, candidate, purged, oldest, newest in rows:
            count = purged if args.apply else candidate
            total += count
            print(f"  tenant={tenant_id} rows={count} "
                  f"oldest={oldest.date() if oldest else '?'} "
                  f"newest={newest.date() if newest else '?'}")
        print(f"[{mode}] Total: {total}")

        if args.apply:
            conn.commit()
    finally:
        try:
            conn.close()
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
