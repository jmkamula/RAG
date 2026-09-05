"""
scripts/dev/print_snapshot_summary.py — Ship 118'.d fix.

Compact snapshot summary printer for per-arc deploy scripts. Runs
snapshot_posture() for every active tenant + prints one summary
block per tenant. Uses direct-DB (owner-role connection); no API
key needed.

Loads .env via python-dotenv (safe parser — handles values with
special characters that bash `source .env` chokes on).

Usage:
    PYTHONPATH=/data/arioncomply python3 \\
        scripts/dev/print_snapshot_summary.py [--tenant SLUG_OR_UUID]

Env (loaded from .env automatically):
    DATABASE_URL
    ARION_OWNER_PW
"""
from __future__ import annotations
import argparse
import os
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlparse

try:
    from dotenv import load_dotenv
    load_dotenv(str(Path(__file__).parent.parent.parent / ".env"))
except ImportError:
    pass

import psycopg2

from rag.posture.snapshot import snapshot_posture


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


def _resolve_tenant(conn, tenant_arg: str) -> list[tuple[str, str]]:
    with conn.cursor() as cur:
        cur.execute("SELECT id::text, name FROM tenants WHERE id::text = %s LIMIT 1", (tenant_arg,))
        row = cur.fetchone()
        if row:
            return [(row[0], row[1])]
        cur.execute("SELECT id::text, name FROM tenants WHERE slug = %s LIMIT 1", (tenant_arg,))
        row = cur.fetchone()
        if row:
            return [(row[0], row[1])]
    sys.exit(f"tenant not found: {tenant_arg}")


def _all_active_tenants(conn) -> list[tuple[str, str]]:
    with conn.cursor() as cur:
        cur.execute("SELECT id::text, name FROM tenants WHERE is_active ORDER BY created_at")
        return [(row[0], row[1]) for row in cur.fetchall()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tenant", help="One tenant slug or UUID. Default: every active tenant.")
    parser.add_argument("--as-of",  help="ISO date (YYYY-MM-DD). Default: now.")
    args = parser.parse_args()

    conn = _owner_conn()
    try:
        targets = _resolve_tenant(conn, args.tenant) if args.tenant else _all_active_tenants(conn)
        if not targets:
            print("No active tenants — nothing to summarize.")
            return 0

        for tid, name in targets:
            snap = snapshot_posture(conn, tid, as_of=args.as_of)
            by_f = Counter(c.finding for c in snap.controls)
            cov_app  = snap.coverage_notes["applicability_status"]["coverage"]
            cov_scop = snap.coverage_notes["scoping_facts"]["coverage"]
            print(f"  {name!r}: {snap.control_count} controls  findings={dict(by_f)}")
            print(f"    coverage: applicability={cov_app}  scoping={cov_scop}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
