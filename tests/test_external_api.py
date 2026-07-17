"""
Integration tests for the external API foundation (Ship 4'.a).

Exercises /api/external/v1/status against a throwaway test tenant
+ two seeded api_keys (one with the required scope, one without).

Test coverage:
  - 401 missing_api_key (no X-API-Key header)
  - 401 invalid_api_key (unknown key)
  - 401 invalid_api_key (inactive key)
  - 403 invalid_scope   (key without external:status)
  - 200 happy path      (correct scope + body shape + rate-limit headers)
  - 429 rate_limited    (61st request in the window trips)
  - Response headers    (X-RateLimit-Limit / -Remaining / -Reset)
  - Retry-After header on 429

The tests need a running API server on localhost:8080. Fixture
seeds/cleans DB rows only; the api_server itself is expected to
already be up.

Run:
    PYTHONPATH=/data/arioncomply python3 tests/test_external_api.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from contextlib import contextmanager
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

import psycopg2
from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")


BASE = os.getenv("EXTERNAL_API_BASE", "http://localhost:8080")

# Throwaway tenant + keys — distinct from the delivery/retention
# test tenants so parallel runs don't collide.
TEST_TENANT_ID  = "77777777-7777-7777-7777-777777777777"
TEST_USER_ID    = "77777777-7777-7777-7777-777777777788"
TEST_TENANT_NAME = "ArionComply External-API Test Tenant"

# The raw API keys used by tests. Kept short + prefixed 'test_' so
# they won't collide with anything else and they're obvious in logs.
RAW_KEY_GOOD    = "test_ext_key_ship4a_good_" + uuid.uuid4().hex[:8]
RAW_KEY_NOSCOPE = "test_ext_key_ship4a_none_" + uuid.uuid4().hex[:8]
RAW_KEY_INACTIVE= "test_ext_key_ship4a_dead_" + uuid.uuid4().hex[:8]


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def _db_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL not set")
    return url


def _connect():
    return psycopg2.connect(_db_url())


@contextmanager
def _test_state():
    """Seed a throwaway tenant + 3 api_keys with different scope /
    is_active settings. Cleans up on exit."""
    conn = _connect()
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            # Tenant
            cur.execute("""
                INSERT INTO tenants (id, name, slug, is_active)
                VALUES (%s::uuid, %s, %s, TRUE)
                ON CONFLICT (id) DO NOTHING
            """, (TEST_TENANT_ID, TEST_TENANT_NAME, "external-api-test-tenant"))
            # User (owner of the keys)
            cur.execute("""
                INSERT INTO users (id, tenant_id, email, full_name, is_active)
                VALUES (%s::uuid, %s::uuid, 'test-external@example.test',
                        'External API Test User', TRUE)
                ON CONFLICT (id) DO NOTHING
            """, (TEST_USER_ID, TEST_TENANT_ID))
            # Good key — has external:status scope
            cur.execute("""
                INSERT INTO api_keys (tenant_id, user_id, key_hash, key_prefix,
                                      name, scopes, is_active)
                VALUES (%s::uuid, %s::uuid, %s, 'test_ext_', 'TEST good key',
                        ARRAY['external:status'], TRUE)
                RETURNING id::text
            """, (TEST_TENANT_ID, TEST_USER_ID, _sha256(RAW_KEY_GOOD)))
            good_id = cur.fetchone()[0]
            # No-scope key — active but no external:* scope
            cur.execute("""
                INSERT INTO api_keys (tenant_id, user_id, key_hash, key_prefix,
                                      name, scopes, is_active)
                VALUES (%s::uuid, %s::uuid, %s, 'test_ext_', 'TEST no-scope key',
                        ARRAY['chat'], TRUE)
                RETURNING id::text
            """, (TEST_TENANT_ID, TEST_USER_ID, _sha256(RAW_KEY_NOSCOPE)))
            no_scope_id = cur.fetchone()[0]
            # Inactive key — has scope but is_active=false
            cur.execute("""
                INSERT INTO api_keys (tenant_id, user_id, key_hash, key_prefix,
                                      name, scopes, is_active)
                VALUES (%s::uuid, %s::uuid, %s, 'test_ext_', 'TEST inactive key',
                        ARRAY['external:status'], FALSE)
                RETURNING id::text
            """, (TEST_TENANT_ID, TEST_USER_ID, _sha256(RAW_KEY_INACTIVE)))
            inactive_id = cur.fetchone()[0]
        conn.commit()
        yield conn, {"good_id": good_id, "no_scope_id": no_scope_id,
                     "inactive_id": inactive_id}
    finally:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                            (TEST_TENANT_ID,))
                cur.execute("DELETE FROM api_rate_limit_bucket WHERE key_id IN "
                            "(SELECT id FROM api_keys WHERE tenant_id=%s::uuid)",
                            (TEST_TENANT_ID,))
                cur.execute("DELETE FROM api_keys WHERE tenant_id=%s::uuid",
                            (TEST_TENANT_ID,))
                cur.execute("DELETE FROM users WHERE tenant_id=%s::uuid",
                            (TEST_TENANT_ID,))
                cur.execute("DELETE FROM tenants WHERE id=%s::uuid",
                            (TEST_TENANT_ID,))
            conn.commit()
        except Exception:
            conn.rollback()
        finally:
            conn.close()


def _get(path: str, key: str | None = None) -> tuple[int, dict, dict]:
    """Return (status_code, body_dict, headers_dict) for the request.
    Never raises on 4xx — we test those explicitly."""
    req = urllib.request.Request(BASE + path)
    if key is not None:
        req.add_header("X-API-Key", key)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            body    = r.read().decode()
            status  = r.status
            headers = dict(r.headers)
    except urllib.error.HTTPError as e:
        body    = e.read().decode()
        status  = e.code
        headers = dict(e.headers or {})
    try:
        body_json = json.loads(body) if body else {}
    except json.JSONDecodeError:
        body_json = {"raw": body}
    return status, body_json, headers


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


# ── Tests ─────────────────────────────────────────────────────────────

def test_missing_key_returns_401_structured():
    with _test_state() as _:
        code, body, _headers = _get("/api/external/v1/status", key=None)
        return _ok(
            code == 401
            and body.get("error", {}).get("code") == "missing_api_key"
            and body.get("error", {}).get("request_id"),
            f"code={code} body={body}",
        )


def test_invalid_key_returns_401_structured():
    with _test_state() as _:
        code, body, _headers = _get(
            "/api/external/v1/status",
            key="not_a_real_key_" + uuid.uuid4().hex,
        )
        return _ok(
            code == 401
            and body.get("error", {}).get("code") == "invalid_api_key",
            f"code={code} body={body}",
        )


def test_inactive_key_returns_401():
    with _test_state() as _:
        code, body, _headers = _get(
            "/api/external/v1/status", key=RAW_KEY_INACTIVE)
        return _ok(
            code == 401
            and body.get("error", {}).get("code") == "invalid_api_key",
            f"code={code} body={body}",
        )


def test_no_scope_returns_403_structured():
    with _test_state() as _:
        code, body, _headers = _get(
            "/api/external/v1/status", key=RAW_KEY_NOSCOPE)
        return _ok(
            code == 403
            and body.get("error", {}).get("code") == "invalid_scope"
            and "external:status" in (body.get("error", {}).get("message") or ""),
            f"code={code} body={body}",
        )


def test_happy_path_returns_200_body_shape():
    with _test_state() as _:
        code, body, headers = _get(
            "/api/external/v1/status", key=RAW_KEY_GOOD)
        return _ok(
            code == 200
            and body.get("ok") is True
            and body.get("tenant_id") == TEST_TENANT_ID
            and body.get("tenant_display_name") == TEST_TENANT_NAME
            and isinstance(body.get("queryable_standards"), list)
            and "external:status" in (body.get("scopes") or [])
            and isinstance(body.get("rate_limit"), dict)
            and body["rate_limit"].get("limit") == 60
            and body.get("server_time"),
            f"code={code} body={body}",
        )


def test_rate_limit_headers_on_200():
    with _test_state() as _:
        code, _body, headers = _get(
            "/api/external/v1/status", key=RAW_KEY_GOOD)
        # Headers are lowercase from http lib
        return _ok(
            code == 200
            and headers.get("x-ratelimit-limit") == "60"
            and headers.get("x-ratelimit-remaining") is not None
            and headers.get("x-ratelimit-reset") is not None,
            f"headers={headers}",
        )


def test_rate_limit_trip_returns_429_with_retry_after():
    """Send 61 requests in one minute. The 61st should 429."""
    with _test_state() as _:
        # Reset the good key's bucket to be safe
        conn = _connect()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM api_rate_limit_bucket "
                        "WHERE key_id IN (SELECT id FROM api_keys "
                        "WHERE key_hash=%s)", (_sha256(RAW_KEY_GOOD),))
        conn.commit(); conn.close()

        trip_at = None
        for i in range(1, 62):
            code, _body, _h = _get("/api/external/v1/status", key=RAW_KEY_GOOD)
            if code == 429:
                trip_at = i
                break

        # Confirm 429 shape
        code, body, headers = _get("/api/external/v1/status", key=RAW_KEY_GOOD)
        return _ok(
            trip_at == 61
            and code == 429
            and body.get("error", {}).get("code") == "rate_limited"
            and int(headers.get("retry-after", "0")) > 0
            and headers.get("x-ratelimit-remaining") == "0",
            f"trip_at={trip_at} code={code} body={body} headers={headers}",
        )


TESTS = [
    test_missing_key_returns_401_structured,
    test_invalid_key_returns_401_structured,
    test_inactive_key_returns_401,
    test_no_scope_returns_403_structured,
    test_happy_path_returns_200_body_shape,
    test_rate_limit_headers_on_200,
    test_rate_limit_trip_returns_429_with_retry_after,
]


def main():
    print("─" * 70)
    print("  External API integration tests (Ship 4'.a)")
    print("  Base URL: " + BASE)
    print("─" * 70)
    # Precheck: is the server up?
    try:
        with urllib.request.urlopen(BASE + "/health", timeout=3) as r:
            r.read()
    except Exception as e:
        print(f"  [SKIP] API server not reachable at {BASE}: {e}")
        return 2

    failures = 0
    for t in TESTS:
        try:
            ok, msg = t()
        except Exception as e:
            import traceback
            ok = False
            msg = f"raised {type(e).__name__}: {e}\n{traceback.format_exc()}"
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {t.__name__}")
        if not ok:
            print(f"         {msg}")
            failures += 1
    print("─" * 70)
    print(f"  {len(TESTS) - failures}/{len(TESTS)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
