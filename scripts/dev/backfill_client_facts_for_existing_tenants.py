"""
scripts/dev/backfill_client_facts_for_existing_tenants.py — Ship 111'.c.

Retroactively creates client_facts rows for tenants that were
provisioned BEFORE Ship 110'.b landed (2026-09-03). Pre-Ship-110'.b
`create_first_tenant()` only wrote to the `tenants` table; the
client_facts row is required for:

  · Ship 110'.c Profile "About your organisation" section to render
    with defaults instead of empty
  · Ship 110'.d applicability derivation to have facts to read
  · Ship 110'.e cascade engine gate to have applicability signals

Idempotent — only INSERTs rows for tenants that don't already have
one. Existing client_facts rows (e.g. Arion Networks dev demo) are
left untouched.

Uses the same `_initial_client_facts()` logic as Ship 110'.b's fresh-
tenant Quickstart path, so the retrofitted row is byte-shape-identical
to what a new tenant would get today. This is the "the stage at which
a client is shouldn't matter" property (Ship 110' Lesson 182): every
active tenant looks like a Ship 111'.c-vintage Quickstart tenant.

Usage:
    PYTHONPATH=/data/arioncomply python3 \\
        scripts/dev/backfill_client_facts_for_existing_tenants.py [--dry-run]

Auth: connects as `arioncomply` (owner role) via ARION_OWNER_PW,
which bypasses RLS on `tenants` + `client_facts` — the whole point of
Ship 111'.a putting ARION_OWNER_PW in .env.

Ship history:
    Ship 104'.a — Quickstart flow (no client_facts writer)
    Ship 110'.a — client_facts SSoT + fact_source + applicability_reason
    Ship 110'.b — Quickstart initializer (only affects NEW tenants)
    Ship 111'.c — this script (backfills EXISTING tenants)
"""
from __future__ import annotations
import argparse
import json
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

from rag.onboarding.quickstart import _initial_client_facts


def _owner_conn():
    """Connect as arioncomply owner role — bypasses RLS on tenants.

    Same connection helper shape as rag/onboarding/quickstart.py::
    _owner_conn — canonical env-var scheme (Ship 111'.a).
    """
    app_dsn = os.getenv("DATABASE_URL", "")
    if not app_dsn:
        sys.exit("DATABASE_URL not set — is /data/arioncomply/.env populated?")
    u = urlparse(app_dsn)
    owner_pw = os.getenv("ARION_OWNER_PW") or unquote(u.password or "")
    if not owner_pw:
        sys.exit("ARION_OWNER_PW not set — Ship 111'.a should have "
                 "stashed it in .env. Backfill missing owner pw via "
                 "the Step 1 backfill runbook.")
    return psycopg2.connect(
        host     = u.hostname or "127.0.0.1",
        port     = u.port or 5432,
        user     = "arioncomply",
        password = owner_pw,
        dbname   = (u.path or "/arioncomply_compliance").lstrip("/"),
    )


def _find_tenants_missing_client_facts(conn) -> list[dict]:
    """Return metadata for active tenants that lack a client_facts row."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT t.id::text, t.name, t.slug, t.sector, t.country, t.cloud_only
              FROM tenants t
              LEFT JOIN client_facts cf ON cf.tenant_id = t.id
             WHERE t.is_active
               AND cf.id IS NULL
             ORDER BY t.created_at
        """)
        return [
            {
                "tenant_id": row[0], "name": row[1], "slug": row[2],
                "sector": row[3], "country": row[4], "cloud_only": row[5],
            }
            for row in cur.fetchall()
        ]


def _insert_client_facts(conn, tenant: dict) -> tuple[list[str], list[str]]:
    """Run Ship 110'.b initializer against `tenant` and INSERT the row.
    Returns (declared_column_names, derived_column_names) for the log.
    """
    values, sources = _initial_client_facts(
        sector     = tenant["sector"],
        country    = tenant["country"] or "GB",
        cloud_only = bool(tenant["cloud_only"]),
    )
    cols_sql     = ", ".join(values.keys())
    placeholders = ", ".join(["%s"] * len(values))
    with conn.cursor() as cur:
        cur.execute(
            f"""
            INSERT INTO client_facts (
                tenant_id, {cols_sql}, fact_source
            ) VALUES (%s, {placeholders}, %s::jsonb)
            """,
            (
                tenant["tenant_id"],
                *values.values(),
                json.dumps(sources),
            ),
        )
    declared = [c for c, s in sources.items() if s["source"] == "declared"]
    derived  = [c for c, s in sources.items() if s["source"] == "derived"]
    return declared, derived


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what would be inserted, but do nothing")
    args = parser.parse_args()

    conn = _owner_conn()
    try:
        missing = _find_tenants_missing_client_facts(conn)
        if not missing:
            print("No tenants need backfill — every active tenant already "
                  "has a client_facts row.")
            return 0

        print(f"Found {len(missing)} tenant(s) missing client_facts:")
        for t in missing:
            print(f"  · {t['name']!r}  ({t['tenant_id'][:8]}, "
                  f"sector={t['sector']!r}, country={t['country']!r}, "
                  f"cloud_only={t['cloud_only']})")
        print()

        if args.dry_run:
            for t in missing:
                values, sources = _initial_client_facts(
                    sector=t["sector"], country=t["country"] or "GB",
                    cloud_only=bool(t["cloud_only"]),
                )
                declared = [c for c, s in sources.items() if s["source"] == "declared"]
                derived  = [c for c, s in sources.items() if s["source"] == "derived"]
                print(f"[dry-run] would insert client_facts for {t['name']!r}:")
                print(f"          declared: {declared}")
                print(f"          derived:  {derived}")
            return 0

        for t in missing:
            declared, derived = _insert_client_facts(conn, t)
            conn.commit()
            print(f"✓ inserted for {t['name']!r}")
            print(f"    declared: {declared}")
            print(f"    derived:  {derived}")

        # Post-condition sanity: nothing should be left missing.
        remaining = _find_tenants_missing_client_facts(conn)
        if remaining:
            print(f"WARN: {len(remaining)} tenant(s) still missing — see above for errors")
            return 1
        print()
        print(f"Backfill complete — {len(missing)} client_facts row(s) inserted.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
