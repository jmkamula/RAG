"""
rag/onboarding/quickstart.py — first-tenant provisioning via UI Quickstart.

Ship 104'.a (2026-09-01).

The bootstrap flow: when the API comes up on a fresh customer box
with zero tenants, the UI shows a Quickstart form on first visit.
The form POSTs to `/api/v1/quickstart` which creates a minimal-
shape tenant + admin user + API key with the standard runtime
scopes. Customer proceeds to the Get Started sidebar to enrol in
frameworks + configure client_facts + upload documents.

Bootstrap-only design: once any active tenant exists, the endpoint
returns 409. This prevents anonymous callers from spawning tenants
on an already-provisioned box (multi-tenant SaaS would need a
different pattern with auth/rate-limits/verification; that's out
of scope for the on-prem PoC).

Minimal shape (compared to scripts/dev/create_tenant.py which
this file borrows from):
  · tenant row (with sector / country / cloud_only)
  · one admin user
  · one API key with scopes ['chat','hitl','documents','posture']
  · NO framework enrolments (customer picks in Get Started)
  · NO client_facts (customer configures in Get Started)
  · NO posture_controls seed (populated when frameworks are enrolled)

Neo4j is not touched by quickstart — no per-tenant Neo4j data at
this stage of the flow.
"""
from __future__ import annotations
import hashlib
import os
import re
import secrets
import uuid
from urllib.parse import quote_plus, urlparse

import psycopg2


ADMIN_SCOPES = ["chat", "hitl", "documents", "posture"]


# ── DB connection ────────────────────────────────────────────────────
# Quickstart writes tenants + users + api_keys — all RLS-protected.
# arioncomply_app (the runtime pool) has GRANTs but the RLS policy
# on tenants filters it to (app.tenant_id = tenants.id). Without a
# set_config, the app role sees nothing. We connect as the schema
# owner `arioncomply` which bypasses RLS on tables it owns.

def _owner_dsn() -> str:
    """Build a DSN that connects as the schema-owner `arioncomply`
    role. Reuses the password from DATABASE_URL — same password on
    most installs — unless overridden via ARION_OWNER_PW env."""
    app_dsn = os.getenv("DATABASE_URL", "")
    if not app_dsn:
        raise RuntimeError("DATABASE_URL not set")
    u = urlparse(app_dsn)
    owner_pw = os.getenv("ARION_OWNER_PW") or (u.password or "")
    host = u.hostname or "127.0.0.1"
    port = u.port or 5432
    db   = (u.path or "/arioncomply_compliance").lstrip("/")
    # URL-encode owner_pw so `@` etc in the password don't break parsing.
    return f"postgresql://arioncomply:{quote_plus(owner_pw)}@{host}:{port}/{db}"


def _owner_conn():
    return psycopg2.connect(_owner_dsn())


# ── Slug generation ─────────────────────────────────────────────────

_SLUG_RE = re.compile(r"[^a-z0-9]+")

def _slugify(name: str) -> str:
    s = _SLUG_RE.sub("-", name.strip().lower()).strip("-")
    return s or "tenant"


# ── API key ─────────────────────────────────────────────────────────

def _random_api_key(prefix: str = "arion") -> str:
    return f"{prefix}_{secrets.token_hex(16)}"


def _hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


# ── The two public functions the endpoints call ─────────────────────

def bootstrap_available() -> bool:
    """Return True iff there are zero active tenants (quickstart is
    the only way to create the first tenant; once one exists, the
    endpoint refuses).
    """
    with _owner_conn() as pg:
        with pg.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM tenants WHERE is_active = TRUE")
            return cur.fetchone()[0] == 0


def create_first_tenant(
    name:         str,
    admin_email:  str,
    admin_name:   str,
    sector:       str | None = None,
    country:      str = "GB",
    cloud_only:   bool = False,
) -> dict:
    """Provision the minimal-shape first tenant + admin user + API key.

    Returns a dict with:
        tenant_id  — UUID string
        api_key    — raw key, shown ONCE (only the SHA256 is stored)
        slug       — the derived (or explicit) slug

    Raises ValueError if a tenant with the derived slug already exists.
    Raises psycopg2 errors on DB failures (caller wraps into HTTP).
    """
    slug = _slugify(name)

    with _owner_conn() as pg:
        try:
            with pg.cursor() as cur:
                # Guard against slug collision (theoretically impossible
                # since bootstrap_available should've been True, but
                # belt-and-braces).
                cur.execute(
                    "SELECT 1 FROM tenants WHERE slug = %s AND is_active = TRUE",
                    (slug,),
                )
                if cur.fetchone():
                    raise ValueError(f"tenant with slug '{slug}' already exists")

                # 1. tenant row
                tenant_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO tenants (
                        id, name, slug, sector, country, cloud_only, subscription
                    ) VALUES (%s, %s, %s, %s, %s, %s, 'free')
                """, (tenant_id, name, slug, sector, country, cloud_only))

                # Set RLS context so the users + api_keys inserts satisfy
                # their tenant_id-scoped policies.
                cur.execute(
                    "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,)
                )

                # 2. admin user
                user_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO users (id, tenant_id, email, full_name)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, tenant_id, admin_email, admin_name))

                # 3. API key with standard runtime scopes
                raw_key    = _random_api_key(prefix="arion")
                key_hash   = _hash_key(raw_key)
                key_prefix = raw_key[:11]  # "arion_abcd0"
                key_id     = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO api_keys (
                        id, tenant_id, user_id, key_hash, key_prefix,
                        name, scopes
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    key_id, tenant_id, user_id, key_hash, key_prefix,
                    f"{name} — quickstart admin key",
                    ADMIN_SCOPES,
                ))

            pg.commit()

            return {
                "tenant_id": tenant_id,
                "api_key":   raw_key,
                "slug":      slug,
            }

        except Exception:
            pg.rollback()
            raise
