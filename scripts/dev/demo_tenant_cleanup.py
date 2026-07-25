"""
scripts/dev/demo_tenant_cleanup.py — cleanup helper for measurement /
A/B scripts that write to the demo tenant.

Motivation (Ship 30, 2026-07-25):
  Dev scripts hardcode the Arion demo tenant UUID and re-run the real
  extraction pipeline for measurement purposes. Without a cleanup
  contract they leave orphan pending findings in Stage-1 — user-visible
  as "42 items in intake queue that I never uploaded." Ship 11'.e's
  measurement run left 102 such findings; Ship 30'.b swept them.

Usage from a measurement script:

  from scripts.dev.demo_tenant_cleanup import cleanup_measurement_residue

  ...run measurement...

  try:
      run_extraction_pass()
  finally:
      cleanup_measurement_residue(
          tenant_id = "00000000-0000-0000-0000-000000000001",
          since     = datetime.now() - timedelta(minutes=10),
          dry_run   = False,
          reason    = "Ship 11.e A/B run — measurement residue",
      )

Behaviour:
  * Soft-deletes pending + is_active findings extracted since `since`.
  * Never touches approved findings.
  * Never touches findings from OTHER tenants.
  * Dry-run mode reports counts without writing.
  * Idempotent — safe to call multiple times.

This is NOT a general Stage-1 sweep tool. That's `stage1_queue_sweep.py`.
This is a bounded cleanup contract for measurement runs.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Ensure repo root importable when run directly.
_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT))

import psycopg2


DEMO_TENANT_ID = "00000000-0000-0000-0000-000000000001"


def cleanup_measurement_residue(
    tenant_id: str,
    since:     datetime,
    dry_run:   bool = True,
    reason:    str  = "measurement run residue — auto-cleanup",
    conn = None,
) -> dict:
    """Soft-delete pending + is_active findings on `tenant_id` that
    were extracted since `since`.

    Returns a summary dict {matched, would_soft_delete or soft_deleted,
    dry_run}.

    Passing `conn` reuses an existing psycopg2 connection; otherwise
    opens a superuser connection to the local Postgres (matches
    stage1_queue_sweep.py convention — trusts arioncomply on
    127.0.0.1).

    Idempotent: a second call with the same `since` returns matched=0
    because the first call flipped is_active to FALSE.
    """
    close_conn = False
    if conn is None:
        conn = psycopg2.connect(
            host     = os.getenv("PGHOST",     "127.0.0.1"),
            dbname   = os.getenv("PGDATABASE", "arioncomply_compliance"),
            user     = os.getenv("PGUSER",     "arioncomply"),
            password = os.getenv("PGPASSWORD", ""),
        )
        close_conn = True

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*)
                  FROM document_findings
                 WHERE tenant_id     = %s::uuid
                   AND review_status = 'pending'
                   AND is_active     = TRUE
                   AND extracted_at >= %s
                """,
                (tenant_id, since),
            )
            matched = cur.fetchone()[0]

            if matched == 0:
                return {"matched": 0, "soft_deleted": 0,
                        "dry_run": dry_run}

            if dry_run:
                return {"matched": matched, "would_soft_delete": matched,
                        "dry_run": True}

            cur.execute(
                """
                UPDATE document_findings
                   SET is_active        = FALSE,
                       review_status    = 'rejected',
                       rejection_reason = %s,
                       reviewed_at      = COALESCE(reviewed_at, NOW())
                 WHERE tenant_id     = %s::uuid
                   AND review_status = 'pending'
                   AND is_active     = TRUE
                   AND extracted_at >= %s
                """,
                (reason, tenant_id, since),
            )
            n = cur.rowcount
        conn.commit()
        return {"matched": matched, "soft_deleted": n, "dry_run": False}
    finally:
        if close_conn:
            conn.close()


def main() -> int:
    """CLI entrypoint for ad-hoc cleanup runs."""
    ap = argparse.ArgumentParser(
        description="Sweep measurement-run residue from a tenant's Stage-1 queue.",
    )
    ap.add_argument("--tenant", default=DEMO_TENANT_ID,
                    help="Tenant UUID (default: Arion demo).")
    ap.add_argument("--minutes-ago", type=int, default=10,
                    help="Sweep findings extracted in the last N minutes "
                         "(default 10). Bounds the sweep window.")
    ap.add_argument("--reason", default="ad-hoc demo tenant cleanup",
                    help="rejection_reason to attach.")
    ap.add_argument("--apply", action="store_true",
                    help="Execute the sweep. Default is dry-run.")
    args = ap.parse_args()

    since = datetime.now(timezone.utc) - timedelta(minutes=args.minutes_ago)
    result = cleanup_measurement_residue(
        tenant_id = args.tenant,
        since     = since,
        dry_run   = not args.apply,
        reason    = args.reason,
    )
    print(f"since={since.isoformat()} tenant={args.tenant}")
    print(f"result: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
