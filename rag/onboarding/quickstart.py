"""
rag/onboarding/quickstart.py — first-tenant provisioning via UI Quickstart.

Ship 104'.a (2026-09-01).
Ship 110'.b (2026-09-03) — extends with client_facts initializer.

The bootstrap flow: when the API comes up on a fresh customer box
with zero tenants, the UI shows a Quickstart form on first visit.
The form POSTs to `/api/v1/quickstart` which creates a minimal-
shape tenant + admin user + API key with the standard runtime
scopes. Customer proceeds to the Get Started sidebar to enrol in
frameworks + upload documents. Deeper client_facts questionnaire
lives in Profile → About your organisation (Ship 110'.c).

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
  · one client_facts row initialised from Quickstart inputs, with
    fact_source markers so Ship 110'.d's applicability derivation
    can distinguish "tenant declared this" from "we assumed this"
  · NO framework enrolments (customer picks in Get Started)
  · NO posture_controls seed (populated when frameworks are enrolled)

Neo4j is not touched by quickstart — no per-tenant Neo4j data at
this stage of the flow.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import secrets
import uuid
from datetime import datetime, timezone
from urllib.parse import unquote, urlparse

import psycopg2


ADMIN_SCOPES = ["chat", "hitl", "documents", "posture"]


# EU/EEA country codes for eu_data_subjects derivation at Quickstart
# time. Tenant in an EU/EEA country → likely has EU data subjects
# → seed as derived (tenant can override in Profile if wrong).
_EU_EEA_COUNTRIES = frozenset({
    # EU (27)
    "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI",
    "FR", "GR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT",
    "NL", "PL", "PT", "RO", "SE", "SI", "SK",
    # EEA additions
    "IS", "LI", "NO",
})


# Ship 112'.a — display-name → ISO 3166-1 alpha-2 map.
#
# Ship 104's Quickstart form is free-text; before Ship 112'.b's
# dropdown lands, customers type whatever they want ("Czechia",
# "United Kingdom", "USA", etc.). Downstream code (this file's
# _EU_EEA_COUNTRIES membership check, applicability derivation)
# compares against ISO codes, so free-text display names silently
# fail the check.
#
# Fix: `_normalize_country()` accepts any of:
#   · ISO 3166-1 alpha-2 code       ("CZ")
#   · Common English display name    ("Czechia", "Czech Republic")
#   · Common variants                ("UK", "USA")
# and returns the ISO code. Unrecognised input is returned as-is so
# the caller still has _something_ to write.
#
# Keys are stored lowercased for case-insensitive lookup. Whitespace
# is trimmed before lookup.
_COUNTRY_NAME_TO_CODE: dict[str, str] = {
    # EU (27) + EEA (3)
    "austria": "AT",
    "belgium": "BE",
    "bulgaria": "BG",
    "cyprus": "CY",
    "czechia": "CZ", "czech republic": "CZ",
    "germany": "DE", "deutschland": "DE",
    "denmark": "DK",
    "estonia": "EE",
    "spain": "ES", "españa": "ES",
    "finland": "FI",
    "france": "FR",
    "greece": "GR",
    "croatia": "HR",
    "hungary": "HU",
    "ireland": "IE",
    "italy": "IT", "italia": "IT",
    "lithuania": "LT",
    "luxembourg": "LU",
    "latvia": "LV",
    "malta": "MT",
    "netherlands": "NL", "holland": "NL", "the netherlands": "NL",
    "poland": "PL",
    "portugal": "PT",
    "romania": "RO",
    "sweden": "SE",
    "slovenia": "SI",
    "slovakia": "SK",
    "iceland": "IS",
    "liechtenstein": "LI",
    "norway": "NO",
    # UK + North America + other common non-EU that customers land on
    "united kingdom": "GB", "uk": "GB", "great britain": "GB",
    "britain": "GB", "england": "GB", "scotland": "GB", "wales": "GB",
    "united states": "US", "united states of america": "US", "usa": "US",
    "america": "US", "u.s.": "US", "u.s.a.": "US",
    "canada": "CA",
    "australia": "AU",
    "new zealand": "NZ",
    "switzerland": "CH", "schweiz": "CH", "suisse": "CH",
    "japan": "JP",
    "brazil": "BR", "brasil": "BR",
    "india": "IN",
    "singapore": "SG",
    "south africa": "ZA",
}


def _normalize_country(raw: str | None) -> str:
    """Return canonical ISO 3166-1 alpha-2 country code for `raw`.

    Accepts:
      · Already-canonical 2-letter codes → returned upper-cased.
      · Known display names / common variants → mapped via
        _COUNTRY_NAME_TO_CODE (case-insensitive, whitespace-trimmed).
      · Unrecognised input → returned as-is (fail-open: caller still
        stores something, downstream derivation just silently skips).

    Empty input returns empty string so caller can apply its own
    default (e.g. "GB" in create_first_tenant).
    """
    if not raw:
        return ""
    stripped = raw.strip()
    if not stripped:
        return ""
    # Display name / variant lookup FIRST — catches 2-letter aliases
    # like "UK" that aren't valid ISO codes (UK maps to GB). Doing
    # the 2-letter shortcut first would return "UK" verbatim.
    key = stripped.lower()
    if key in _COUNTRY_NAME_TO_CODE:
        return _COUNTRY_NAME_TO_CODE[key]
    # Already a 2-letter code that wasn't in the alias map — assume
    # it's a valid ISO code and pass through upper-cased.
    if len(stripped) == 2 and stripped.isalpha():
        return stripped.upper()
    # Unknown — return as-is so the caller still writes _something_
    return stripped


def _now_iso() -> str:
    """UTC ISO-8601 timestamp for fact_source markers."""
    return datetime.now(timezone.utc).isoformat()


def _initial_client_facts(
    sector:     str | None,
    country:    str,
    cloud_only: bool,
) -> tuple[dict, dict]:
    """Return (declared_values, fact_source_markers) for the client_facts
    row created at Quickstart.

    Columns not in the returned dict keep their schema defaults (FALSE
    for booleans, NULL for text). Their absence from fact_source signals
    "not yet declared" — Ship 110'.d's applicability derivation treats
    absence as `default` and does NOT fire N/A rules for those facts.
    """
    now = _now_iso()
    values:  dict[str, object] = {}
    sources: dict[str, dict]   = {}

    # Ship 112'.a — normalize free-text country input to ISO alpha-2.
    # Ship 104's Quickstart form is free-text; "Czechia" / "United
    # Kingdom" / "USA" all get canonicalized here so the EU/EEA
    # derivation below works + so posture_controls filters that
    # compare against ISO codes downstream see a stable value.
    normalized_country = _normalize_country(country) or "GB"

    # Country is always set (defaults to "GB" in create_first_tenant)
    values["country"] = normalized_country
    sources["country"] = {"source": "declared", "at": now}

    # Sector: declared if the caller passed one
    if sector:
        values["sector"] = sector
        sources["sector"] = {"source": "declared", "at": now}

    # cloud_only checkbox is a direct question in the Quickstart form:
    # checked   → has_physical_premises=False + uses_cloud_services=True (declared)
    # unchecked → has_physical_premises=True (declared); uses_cloud_services
    #             stays at default (unknown — they didn't say either way)
    if cloud_only:
        values["has_physical_premises"] = False
        values["uses_cloud_services"]   = True
        sources["has_physical_premises"] = {"source": "declared", "at": now}
        sources["uses_cloud_services"]   = {"source": "declared", "at": now}
    else:
        values["has_physical_premises"] = True
        sources["has_physical_premises"] = {"source": "declared", "at": now}

    # Country-driven derivations. Tenant can override in Profile.
    ctry = normalized_country
    if ctry in _EU_EEA_COUNTRIES:
        values["eu_data_subjects"] = True
        sources["eu_data_subjects"] = {
            "source": "derived", "at": now, "from": "country",
        }
    if ctry == "GB":
        values["uk_data_subjects"] = True
        sources["uk_data_subjects"] = {
            "source": "derived", "at": now, "from": "country",
        }

    return values, sources


# ── DB connection ────────────────────────────────────────────────────
# Quickstart writes tenants + users + api_keys — all RLS-protected.
# arioncomply_app (the runtime pool) has GRANTs but the RLS policy
# on tenants filters it to (app.tenant_id = tenants.id). Without a
# set_config, the app role sees nothing. We connect as the schema
# owner `arioncomply` which bypasses RLS on tables it owns.
#
# NOTE: use keyword-arg connect, not a DSN string. urlparse does NOT
# URL-decode the password field — u.password returns 'P%40ng0%40mb3l3'
# literally when the URL contains '%40'. Round-tripping through a DSN
# string then double-encodes it and psycopg2 auths with the wrong
# value. Keyword args skip URL encoding entirely.

def _owner_conn():
    """Return a fresh psycopg2 connection as the arioncomply role."""
    app_dsn = os.getenv("DATABASE_URL", "")
    if not app_dsn:
        raise RuntimeError("DATABASE_URL not set")
    u = urlparse(app_dsn)
    # unquote to reverse the URL-encoding used by install.sh's .env writer
    # (e.g. 'P%40ng0%40mb3l3' → 'P@ng0@mb3l3').
    parsed_pw = unquote(u.password or "")
    owner_pw  = os.getenv("ARION_OWNER_PW") or parsed_pw
    return psycopg2.connect(
        host     = u.hostname or "127.0.0.1",
        port     = u.port or 5432,
        user     = "arioncomply",
        password = owner_pw,
        dbname   = (u.path or "/arioncomply_compliance").lstrip("/"),
    )


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
                # Ship 112'.a — normalize country to ISO alpha-2 for
                # tenants.country too (not just client_facts), so any
                # future code that reads tenants.country directly
                # (e.g. legacy call sites, admin UIs) sees a canonical
                # value. See _normalize_country docstring.
                tenant_id = str(uuid.uuid4())
                normalized_country = _normalize_country(country) or "GB"
                cur.execute("""
                    INSERT INTO tenants (
                        id, name, slug, sector, country, cloud_only, subscription
                    ) VALUES (%s, %s, %s, %s, %s, %s, 'free')
                """, (tenant_id, name, slug, sector, normalized_country, cloud_only))

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

                # 4. client_facts row — Ship 110'.b initializer.
                # Only columns we're actively declaring/deriving are
                # in the INSERT column list; the rest keep their schema
                # defaults (and stay absent from fact_source, which
                # signals "default" to Ship 110'.d's derivation).
                facts_values, facts_sources = _initial_client_facts(
                    sector=sector, country=country, cloud_only=cloud_only,
                )
                cols_sql     = ", ".join(facts_values.keys())
                placeholders = ", ".join(["%s"] * len(facts_values))
                cur.execute(
                    f"""
                    INSERT INTO client_facts (
                        tenant_id, {cols_sql}, fact_source
                    ) VALUES (%s, {placeholders}, %s::jsonb)
                    """,
                    (
                        tenant_id,
                        *facts_values.values(),
                        json.dumps(facts_sources),
                    ),
                )

            pg.commit()

            return {
                "tenant_id": tenant_id,
                "api_key":   raw_key,
                "slug":      slug,
            }

        except Exception:
            pg.rollback()
            raise
