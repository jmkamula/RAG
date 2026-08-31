#!/usr/bin/env python3
"""Provision a fresh ArionComply tenant.

Creates:
    - one row in `tenants`
    - one admin user in `users`
    - one row per enrolled framework in `tenant_standards`
    - baseline `client_facts` (GDPR controller + EU subjects by default)
    - one API key in `api_keys` (SHA-256 hash of a new random key; the
      raw key is printed ONCE at the end and never stored)
    - initial `posture_controls` rows (one per curated control in each
      enrolled standard, finding='Not assessed')

Idempotent-lite: refuses to overwrite an existing tenant with the same
slug. Use --recreate to soft-delete and re-provision.

Usage:
    python3 scripts/dev/create_tenant.py --name "Acme Corp"

    # More options:
    python3 scripts/dev/create_tenant.py \
        --name "Acme Corp" \
        --slug acme-corp \
        --industry technology \
        --country US \
        --cloud-only \
        --employee-count 150 \
        --frameworks ISO27001:2022 ISO27701:2019 GDPR:2016/679 \
        --admin-email founder@acme.example \
        --admin-name "Alex Founder"
"""
from __future__ import annotations

import argparse
import hashlib
import os
import secrets
import sys
import uuid
from typing import Optional

import psycopg2
from dotenv import load_dotenv
from neo4j import GraphDatabase


DEFAULT_FRAMEWORKS = ["ISO27001:2022", "GDPR:2016/679"]


def _slugify(name: str) -> str:
    s = "".join(c.lower() if c.isalnum() else "-" for c in name)
    s = "-".join(part for part in s.split("-") if part)
    return s[:64] or "tenant"


def _random_api_key(prefix: str = "arion") -> str:
    # arion_<32-hex> — matches the existing style; 128 bits of entropy
    return f"{prefix}_{secrets.token_hex(16)}"


def _hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def _curated_controls_for(std_id: str, neo_driver) -> list[dict]:
    """Return every curated control (RequirementNode with a
    SATISFIED_BY FulfilmentSpec) for the standard."""
    with neo_driver.session() as s:
        rows = s.run("""
            MATCH (rn:RequirementNode {standard_id: $s})
                  -[:SATISFIED_BY]->(:FulfilmentSpec)
            RETURN DISTINCT rn.ref AS ref, rn.title AS title
            ORDER BY rn.ref
        """, s=std_id).data()
    return rows


def _admin_dsn() -> str:
    """Return a DSN that connects as the schema-owner `arioncomply`
    role rather than the RLS-scoped `arioncomply_app`. Tenant
    provisioning inserts a NEW tenant row before the RLS context can
    be set, so it needs to run as the owner.

    Reuses the password from DATABASE_URL (same in most POC installs)
    unless overridden via ARION_OWNER_PW env.
    """
    from urllib.parse import urlparse
    app_dsn = os.getenv("DATABASE_URL", "")
    if not app_dsn:
        raise SystemExit("DATABASE_URL not set in env")
    u = urlparse(app_dsn)
    owner_pw = os.getenv("ARION_OWNER_PW") or (u.password or "")
    host = u.hostname or "127.0.0.1"
    port = u.port or 5432
    db   = (u.path or "/arioncomply_compliance").lstrip("/")
    return f"postgresql://arioncomply:{owner_pw}@{host}:{port}/{db}"


def provision(args) -> str:
    load_dotenv("/data/arioncomply/.env")
    pg = psycopg2.connect(_admin_dsn())
    pg.autocommit = False

    neo = GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")),
    )

    slug = args.slug or _slugify(args.name)

    try:
        with pg.cursor() as cur:
            cur.execute(
                "SELECT id FROM tenants WHERE slug = %s AND is_active = TRUE",
                (slug,),
            )
            existing = cur.fetchone()
            if existing and not args.recreate:
                raise SystemExit(
                    f"tenant with slug '{slug}' already exists (id {existing[0]}).\n"
                    f"Use --recreate to soft-delete + re-provision, or pick a "
                    f"different --slug."
                )
            if existing and args.recreate:
                # Soft-delete AND retire every unique-constrained field
                # so the fresh INSERTs below don't collide:
                #   - tenants.slug        (retired to <slug>-deleted-<id>)
                #   - users.email         (retired to deleted-<id>+<orig>)
                # Keeps the audit trail (rows preserved, is_active=FALSE)
                # while freeing the originals for reuse.
                dead_suffix = str(existing[0])[:8]
                dead_slug = f"{slug}-deleted-{dead_suffix}"
                print(f"  · soft-deleting existing tenant {existing[0]} (slug → {dead_slug})")
                cur.execute(
                    "UPDATE tenants SET is_active = FALSE, slug = %s WHERE id = %s",
                    (dead_slug, existing[0]),
                )
                cur.execute(
                    "UPDATE users SET email = 'deleted-' || %s || '+' || email "
                    "WHERE tenant_id = %s AND email NOT LIKE 'deleted-%%'",
                    (dead_suffix, existing[0]),
                )

            # ── 1. tenants row ────────────────────────────────────────
            tenant_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO tenants (
                    id, name, slug, sector, country, industry,
                    employee_count, cloud_only, subscription
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, 'free'
                )
            """, (tenant_id, args.name, slug, args.sector, args.country,
                  args.industry, args.employee_count, args.cloud_only))
            print(f"  ✓ tenant '{args.name}' (id {tenant_id[:8]}…, slug {slug})")

            # RLS context for downstream inserts
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,)
            )

            # ── 2. admin user ─────────────────────────────────────────
            user_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO users (id, tenant_id, email, full_name)
                VALUES (%s, %s, %s, %s)
            """, (user_id, tenant_id, args.admin_email, args.admin_name))
            print(f"  ✓ admin user: {args.admin_email}")

            # ── 3. enrolled frameworks ────────────────────────────────
            for std in args.frameworks:
                cur.execute("""
                    INSERT INTO tenant_standards (tenant_id, standard_id, status)
                    VALUES (%s, %s, 'implementing')
                    ON CONFLICT (tenant_id, standard_id) DO NOTHING
                """, (tenant_id, std))
                print(f"  ✓ enrolled in {std}")

            # ── 4. client_facts baseline ──────────────────────────────
            # Conservative GDPR-facing defaults: controller processing
            # personal data with EU + UK subjects. Tenant tunes via
            # the profile UI post-install.
            cur.execute("""
                INSERT INTO client_facts (
                    tenant_id, processes_personal_data,
                    eu_data_subjects, uk_data_subjects,
                    role_controller, role_processor, role_joint_controller,
                    special_category_data, criminal_conviction_data
                ) VALUES (%s, TRUE, TRUE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE)
            """, (tenant_id,))
            print(f"  ✓ baseline client_facts (GDPR controller + EU/UK subjects)")

            # ── 5. seed posture_controls (Not assessed) ───────────────
            n_seeded = 0
            for std in args.frameworks:
                ctrls = _curated_controls_for(std, neo)
                for c in ctrls:
                    node_id = f"{std}:{c['ref']}"
                    cur.execute("""
                        INSERT INTO posture_controls (
                            tenant_id, standard_id, control_ref, node_id,
                            finding, source
                        ) VALUES (%s, %s, %s, %s, 'Not assessed', 'Not assessed')
                        ON CONFLICT DO NOTHING
                    """, (tenant_id, std, c["ref"], node_id))
                n_seeded += len(ctrls)
            print(f"  ✓ seeded {n_seeded} posture_controls rows (Not assessed)")

            # ── 6. API key ────────────────────────────────────────────
            raw_key    = _random_api_key(prefix="arion")
            key_hash   = _hash_key(raw_key)
            key_prefix = raw_key[:11]  # e.g. "arion_dead0..."
            key_id     = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO api_keys (
                    id, tenant_id, user_id, key_hash, key_prefix,
                    name, scopes
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    ARRAY['chat','hitl','documents','posture']
                )
            """, (key_id, tenant_id, user_id, key_hash, key_prefix,
                  f"{args.name} — initial admin key"))
            print(f"  ✓ API key issued (name: '{args.name} — initial admin key')")

        pg.commit()
    except Exception:
        pg.rollback()
        raise
    finally:
        pg.close()
        neo.close()

    return raw_key


def main() -> None:
    p = argparse.ArgumentParser(
        description="Provision a fresh ArionComply tenant.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--name", required=True, help="Human-facing tenant name")
    p.add_argument("--slug", default=None, help="URL-safe slug (default: derived from name)")
    p.add_argument("--sector", default=None, help="Sector code (e.g. finance, healthcare)")
    p.add_argument("--industry", default=None)
    p.add_argument("--country", default="GB", help="ISO-3166 country code (default: GB)")
    p.add_argument("--employee-count", type=int, default=None)
    p.add_argument("--cloud-only", action="store_true",
                   help="Set cloud_only=TRUE (drives A.5.15:physical_rules N/A carve-out)")
    p.add_argument("--frameworks", nargs="*", default=DEFAULT_FRAMEWORKS,
                   help=f"Standards to enrol in (default: {' '.join(DEFAULT_FRAMEWORKS)})")
    p.add_argument("--admin-email", default="admin@example.com")
    p.add_argument("--admin-name",  default="Initial Admin")
    p.add_argument("--recreate", action="store_true",
                   help="Soft-delete existing tenant with the same slug + re-provision")
    args = p.parse_args()

    print(f"Provisioning ArionComply tenant '{args.name}'...")
    print()
    raw_key = provision(args)
    print()
    print("═" * 70)
    print("  API KEY (shown ONCE — copy this now, we don't store the raw value)")
    print("═" * 70)
    print()
    print(f"  {raw_key}")
    print()
    print("  Test it:")
    print(f"    curl -H 'X-API-Key: {raw_key}' http://127.0.0.1:8080/api/v1/dashboard/posture")
    print()


if __name__ == "__main__":
    sys.path.insert(0, "/data/arioncomply")
    main()
