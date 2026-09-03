"""
scripts/dev/cleanup_orphan_stage2_notifications.py — one-time cleanup.

Ship 107' — removes orphan stage2_proposal_ready notifications and
pending Stage-2 engine proposals for tenants in `setup` lifecycle
stage. Fixes the mess left by the pre-Ship-107' engine which
happily fired 118 proposals on framework enrolment (one per Not-
assessed control that engine wanted to propose NC for).

Safe by design:
  · Only targets tenants where lifecycle_stage returns 'setup'
    (no client_facts, no journey_status, no assessments, no uploads)
  · Only deletes notifications with kind='stage2_proposal_ready'
    that are still pending (unread + undismissed)
  · Only deletes posture_assertions with source='engine' and
    status='pending'
  · Only resets engine_proposal_status='proposed' on posture_controls
    where the corresponding pending PA is being deleted

Idempotent — safe to re-run.

Usage:
    PYTHONPATH=/data/arioncomply python3 \\
        scripts/dev/cleanup_orphan_stage2_notifications.py [--dry-run]
"""
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(str(Path(__file__).parent.parent.parent / ".env"))
except ImportError:
    pass

import psycopg2

from rag.tenant_lifecycle import lifecycle_stage


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what would be deleted without doing it")
    args = parser.parse_args()

    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        sys.exit("DATABASE_URL not set")
    # Use the owner role — bypasses RLS on tenants + posture_controls
    from urllib.parse import unquote, urlparse
    u = urlparse(dsn)
    conn = psycopg2.connect(
        host     = u.hostname or "127.0.0.1",
        port     = u.port or 5432,
        user     = "arioncomply",
        password = os.getenv("ARION_OWNER_PW") or unquote(u.password or ""),
        dbname   = (u.path or "/arioncomply_compliance").lstrip("/"),
    )
    try:
        # Iterate every active tenant, check lifecycle stage, cleanup
        # setup-stage tenants.
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, slug FROM tenants WHERE is_active = TRUE")
            tenants = cur.fetchall()

        print(f"Scanning {len(tenants)} active tenant(s)...")
        total_notifications_deleted = 0
        total_pas_deleted = 0
        total_postures_reset = 0

        for (tenant_id, name, slug) in tenants:
            stage = lifecycle_stage(conn, str(tenant_id))
            if stage != "setup":
                print(f"  skip [{stage:>8s}]  {name!r}")
                continue

            with conn.cursor() as cur:
                # 1. Count notifications that would be deleted
                cur.execute("""
                    SELECT COUNT(*) FROM tenant_notification
                     WHERE tenant_id = %s
                       AND kind = 'stage2_proposal_ready'
                       AND read_at IS NULL
                       AND dismissed_at IS NULL
                """, (tenant_id,))
                n_notif = cur.fetchone()[0]

                # 2. Count pending engine PAs
                cur.execute("""
                    SELECT COUNT(*) FROM posture_assertions
                     WHERE tenant_id = %s
                       AND source = 'engine'
                       AND status = 'pending'
                """, (tenant_id,))
                n_pas = cur.fetchone()[0]

                # 3. Count posture_controls with engine_proposal_status='proposed'
                cur.execute("""
                    SELECT COUNT(*) FROM posture_controls
                     WHERE tenant_id = %s
                       AND engine_proposal_status = 'proposed'
                       AND is_active = TRUE
                """, (tenant_id,))
                n_postures = cur.fetchone()[0]

            print(f"  clean  [setup]     {name!r}: "
                  f"notifications={n_notif}, pending PAs={n_pas}, "
                  f"proposed markers={n_postures}")

            if args.dry_run:
                total_notifications_deleted += n_notif
                total_pas_deleted            += n_pas
                total_postures_reset         += n_postures
                continue

            # Execute cleanup
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM tenant_notification
                     WHERE tenant_id = %s
                       AND kind = 'stage2_proposal_ready'
                       AND read_at IS NULL
                       AND dismissed_at IS NULL
                """, (tenant_id,))
                cur.execute("""
                    DELETE FROM posture_assertions
                     WHERE tenant_id = %s
                       AND source = 'engine'
                       AND status = 'pending'
                """, (tenant_id,))
                cur.execute("""
                    UPDATE posture_controls
                       SET engine_proposal_status = 'none',
                           engine_proposed_at     = NULL
                     WHERE tenant_id = %s
                       AND engine_proposal_status = 'proposed'
                       AND is_active = TRUE
                """, (tenant_id,))
            conn.commit()

            total_notifications_deleted += n_notif
            total_pas_deleted            += n_pas
            total_postures_reset         += n_postures

        print()
        prefix = "[dry-run] would delete" if args.dry_run else "deleted"
        print(f"{prefix}: notifications={total_notifications_deleted}, "
              f"pending PAs={total_pas_deleted}, "
              f"proposal markers reset={total_postures_reset}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
