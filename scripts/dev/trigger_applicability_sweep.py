"""
scripts/dev/trigger_applicability_sweep.py — Ship 118'.d.

Direct-DB utility that runs derive_applicability() for every active
tenant. Bypasses the HTTP layer entirely — connects as the arioncomply
owner role via ARION_OWNER_PW (canonical env-var scheme from Ship
111'.a).

Why this exists:
  · Per-arc deploy scripts (ship-N-poc-update.sh) sometimes want to
    kickstart the applicability audit log — either because Ship 118'.b
    just landed and the log is empty, or because they added new
    scoping rules that need to fire against the current state.
  · The HTTP path (POST /api/v1/admin/derive-applicability) needs an
    ARION_DEV_API_KEY. On some deploys — including the arionlabs-dr-01
    first Ship 118' rollout — that key isn't in .env, so the ship
    script's HTTP-based trigger silently skips.
  · This utility runs the same derive_applicability() code as the API
    endpoint, using the owner connection that Ship 111'.a canonicalised
    for backfill scripts. No key needed.

Idempotent — re-firing rules that produce the same result writes no
log rows (Ship 118'.b Lesson 215).

Usage:
    PYTHONPATH=/data/arioncomply python3 \\
        scripts/dev/trigger_applicability_sweep.py [--tenant SLUG_OR_UUID]

Env:
    DATABASE_URL    (from .env)
    ARION_OWNER_PW  (from .env; canonical since Ship 111'.a)

Output (one line per tenant):
    <name>  cleared=N na_set=N rules=[list]  → applicability_status_log +K rows
"""
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

try:
    from dotenv import load_dotenv
    load_dotenv(str(Path(__file__).parent.parent.parent / ".env"))
except ImportError:
    pass

import psycopg2

from rag.scoping.applicability import derive_applicability


def _owner_conn():
    app_dsn = os.getenv("DATABASE_URL", "")
    if not app_dsn:
        sys.exit("DATABASE_URL not set")
    u = urlparse(app_dsn)
    owner_pw = os.getenv("ARION_OWNER_PW") or unquote(u.password or "")
    if not owner_pw:
        sys.exit("ARION_OWNER_PW not set — Ship 111'.a should have stashed it in .env")
    return psycopg2.connect(
        host     = u.hostname or "127.0.0.1",
        port     = u.port or 5432,
        user     = "arioncomply",
        password = owner_pw,
        dbname   = (u.path or "/arioncomply_compliance").lstrip("/"),
    )


def _resolve_tenant(conn, tenant_arg: str) -> tuple[str, str]:
    """Return (tenant_id, tenant_name). Accepts a slug or a UUID."""
    with conn.cursor() as cur:
        # Try UUID first
        cur.execute("SELECT id::text, name FROM tenants WHERE id::text = %s LIMIT 1", (tenant_arg,))
        row = cur.fetchone()
        if row:
            return row[0], row[1]
        # Fall back to slug
        cur.execute("SELECT id::text, name FROM tenants WHERE slug = %s LIMIT 1", (tenant_arg,))
        row = cur.fetchone()
        if row:
            return row[0], row[1]
    sys.exit(f"tenant not found: {tenant_arg}")


def _all_active_tenants(conn) -> list[tuple[str, str]]:
    with conn.cursor() as cur:
        cur.execute("SELECT id::text, name FROM tenants WHERE is_active ORDER BY created_at")
        return [(row[0], row[1]) for row in cur.fetchall()]


def _count_log_rows(conn, tenant_id: str) -> int:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM applicability_status_log WHERE tenant_id = %s::uuid",
            (tenant_id,),
        )
        return cur.fetchone()[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tenant",
        help="One tenant slug or UUID. Default: every active tenant.",
    )
    args = parser.parse_args()

    conn = _owner_conn()
    try:
        targets = (
            [_resolve_tenant(conn, args.tenant)]
            if args.tenant
            else _all_active_tenants(conn)
        )
        if not targets:
            print("No active tenants — nothing to do.")
            return 0

        print(f"Firing derive_applicability() on {len(targets)} tenant(s):")
        for tid, name in targets:
            log_before = _count_log_rows(conn, tid)
            try:
                r = derive_applicability(conn, tid)
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"  {name!r}: FAILED — {e}")
                continue
            log_after = _count_log_rows(conn, tid)
            delta = log_after - log_before
            print(
                f"  {name!r}: cleared={r.controls_cleared} "
                f"na_set={r.controls_na_set} rules={r.rules_fired} "
                f"→ applicability_status_log +{delta} rows"
            )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
