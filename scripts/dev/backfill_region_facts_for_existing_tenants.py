"""
scripts/dev/backfill_region_facts_for_existing_tenants.py — Ship 114'.a.

Retroactively fills the client_facts region columns for tenants
provisioned before Ship 113'.a's region_of_country() derivation
landed (2026-09-04).

Handles the arionlabs-dr-01 case discovered during Ship 113' deploy:
Arion Networks s.r.o. had country=`Czechia` (free-text from Ship 104'
Quickstart) but every *_data_subjects column was FALSE — none of
the 6 regions were declared. Root cause: Ship 110'.b's original
derivation compared against `_EU_EEA_COUNTRIES` (ISO codes only)
and "Czechia" didn't match. Ship 112'.a fixed the normalization for
NEW tenants; Ship 113'.a added the 6-region derivation for NEW
tenants; existing tenants need this retroactive backfill.

For each active tenant with a client_facts row + no region column
declared in fact_source:
  1. Read tenants.country
  2. Normalize via _normalize_country() to ISO alpha-2
  3. Update tenants.country + client_facts.country to normalized
     value (if different from current)
  4. Derive region via region_of_country()
  5. Set the corresponding *_data_subjects column TRUE
  6. Add both country + region to fact_source as declared/derived
  7. Run derive_applicability() to update posture_controls

Idempotent — only touches tenants whose region columns are all at
default (no region marker in fact_source).

Uses ARION_OWNER_PW to bypass RLS (canonical scheme from Ship 111'.a).

Usage:
    PYTHONPATH=/data/arioncomply python3 \\
        scripts/dev/backfill_region_facts_for_existing_tenants.py [--dry-run]
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

from rag.onboarding.quickstart import _normalize_country
from rag.scoping.regions import REGION_COLUMN, region_of_country
from rag.scoping.applicability import derive_applicability


def _owner_conn():
    app_dsn = os.getenv("DATABASE_URL", "")
    if not app_dsn:
        sys.exit("DATABASE_URL not set")
    u = urlparse(app_dsn)
    owner_pw = os.getenv("ARION_OWNER_PW") or unquote(u.password or "")
    if not owner_pw:
        sys.exit("ARION_OWNER_PW not set")
    return psycopg2.connect(
        host     = u.hostname or "127.0.0.1",
        port     = u.port or 5432,
        user     = "arioncomply",
        password = owner_pw,
        dbname   = (u.path or "/arioncomply_compliance").lstrip("/"),
    )


def _fact_source_has_region(fact_source: dict) -> bool:
    """True if any *_data_subjects column has an entry in fact_source."""
    region_cols = set(REGION_COLUMN.values())
    return any(col in (fact_source or {}) for col in region_cols)


def _find_tenants_missing_region_derivation(conn) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT t.id::text, t.name, t.slug, t.country,
                   cf.country AS cf_country, cf.fact_source
              FROM tenants t
              JOIN client_facts cf ON cf.tenant_id = t.id
             WHERE t.is_active
             ORDER BY t.created_at
        """)
        rows = cur.fetchall()

    missing = []
    for tid, name, slug, tenant_country, cf_country, fact_source in rows:
        # If any region is already declared/derived → skip (idempotent)
        if _fact_source_has_region(fact_source or {}):
            continue
        # Need at least one country source to derive from
        source_country = tenant_country or cf_country
        if not source_country:
            continue
        missing.append({
            "tenant_id":       tid,
            "name":            name,
            "slug":            slug,
            "tenant_country":  tenant_country,
            "cf_country":      cf_country,
            "source_country":  source_country,
        })
    return missing


def _apply_backfill(conn, tenant: dict) -> tuple[str, str | None]:
    """Normalize country + set region column + fact_source markers.

    Returns (normalized_iso_code, region_key) — region_key is None
    for countries not mapped to any region bucket.
    """
    normalized = _normalize_country(tenant["source_country"]) or ""
    if not normalized:
        return ("", None)

    region_key = region_of_country(normalized)
    region_col = REGION_COLUMN[region_key] if region_key else None

    now = "now()"  # SQL now() — inline the marker time in the jsonb
    # Build fact_source patch. country always declared; region if we
    # got one.
    patch = {"country": {"source": "declared", "at": None}}
    if region_col:
        patch[region_col] = {"source": "derived", "from": "country", "at": None}

    with conn.cursor() as cur:
        # tenants.country update (if changed)
        if tenant["tenant_country"] != normalized:
            cur.execute("""
                UPDATE tenants SET country = %s
                 WHERE id = %s::uuid
            """, (normalized, tenant["tenant_id"]))

        # client_facts.country + region column + fact_source merge
        # Use SQL now() so the at timestamp matches the transaction.
        # Two-step: update the concrete columns, then merge fact_source
        # with a jsonb_build_object that carries a live now().
        if region_col:
            cur.execute(f"""
                UPDATE client_facts
                   SET country = %s,
                       {region_col} = TRUE,
                       fact_source = fact_source || jsonb_build_object(
                           'country',    jsonb_build_object('source','declared','at', now()::text),
                           %s,           jsonb_build_object('source','derived','from','country','at', now()::text)
                       )
                 WHERE tenant_id = %s::uuid
            """, (normalized, region_col, tenant["tenant_id"]))
        else:
            # Country normalized but no region mapping — still mark
            # country as declared for auditability.
            cur.execute("""
                UPDATE client_facts
                   SET country = %s,
                       fact_source = fact_source || jsonb_build_object(
                           'country', jsonb_build_object('source','declared','at', now()::text)
                       )
                 WHERE tenant_id = %s::uuid
            """, (normalized, tenant["tenant_id"]))

    return (normalized, region_key)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    conn = _owner_conn()
    try:
        missing = _find_tenants_missing_region_derivation(conn)
        if not missing:
            print("No tenants need region backfill — every active tenant "
                  "with a client_facts row already has a declared or "
                  "derived region.")
            return 0

        print(f"Found {len(missing)} tenant(s) missing region derivation:")
        for t in missing:
            normalized_preview = _normalize_country(t["source_country"])
            region_preview = region_of_country(normalized_preview or "")
            print(f"  · {t['name']!r}  ({t['tenant_id'][:8]})")
            print(f"      country source:    {t['source_country']!r}")
            print(f"      normalized preview: {normalized_preview!r}")
            print(f"      region preview:     {region_preview!r}")
        print()

        if args.dry_run:
            print("--dry-run — not applying anything")
            return 0

        for t in missing:
            normalized, region_key = _apply_backfill(conn, t)
            conn.commit()
            region_col = REGION_COLUMN[region_key] if region_key else "(none)"
            print(f"✓ {t['name']!r}: country={normalized!r} region_col={region_col!r}")

            # Trigger applicability derivation so downstream posture
            # gates + N/A flags update immediately.
            r = derive_applicability(conn, t["tenant_id"])
            conn.commit()
            print(f"    applicability: rules_fired={r.rules_fired} na_set={r.controls_na_set}")

        print()
        print(f"Region backfill complete — {len(missing)} tenant(s) updated.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
