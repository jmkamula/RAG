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
            _purge_test_api_keys(conn, TEST_TENANT_ID)
        except Exception:
            conn.rollback()
        finally:
            conn.close()


def _purge_test_api_keys(conn, tenant_id: str) -> None:
    """Surgical cleanup: delete rate-limit buckets + api_keys created
    by this test run for the throwaway test tenant, but LEAVE the
    tenant, user, and any audit-log rows in place.

    Why not delete the tenant? Audit-log tables (ai_call_log,
    chat_casefile_log, chat_consensus_log, intake_trace_log,
    fact_recompute_log) intentionally have no DELETE grant for
    arioncomply_app — they're append-only by
    [[feedback-rls-grant-parity]] design. The RAG pipeline invoked
    by /query tests writes to those tables, so tenant DELETE would
    fail on FK constraints.

    Approach: the tenant + user rows are idempotent (ON CONFLICT DO
    NOTHING on seed), so they persist across runs. Only api_keys +
    their rate-limit buckets need to be cleaned so the next run's
    unique-key-hash constraint isn't tripped."""
    with conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        cur.execute("""
            DELETE FROM api_rate_limit_bucket
             WHERE key_id IN (SELECT id FROM api_keys WHERE tenant_id=%s::uuid)
        """, (tenant_id,))
        cur.execute("DELETE FROM api_keys WHERE tenant_id=%s::uuid",
                    (tenant_id,))
    conn.commit()


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


def _post(path: str, payload: dict, key: str | None = None,
          timeout: int = 60) -> tuple[int, dict, dict]:
    """POST with a JSON body. Longer default timeout because /query
    can invoke the RAG pipeline (multi-second LLM call)."""
    req = urllib.request.Request(
        BASE + path,
        data    = json.dumps(payload).encode(),
        headers = {"Content-Type": "application/json"},
        method  = "POST",
    )
    if key is not None:
        req.add_header("X-API-Key", key)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
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


def _post_multipart(path: str, filename: str, content: bytes,
                    extra_fields: dict[str, str] | None = None,
                    key: str | None = None,
                    timeout: int = 60) -> tuple[int, dict, dict]:
    """POST multipart/form-data — used for /documents upload."""
    boundary = "----test-boundary-" + uuid.uuid4().hex
    parts: list[bytes] = []
    if extra_fields:
        for k, v in extra_fields.items():
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode())
    parts.append(content)
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    body = b"".join(parts)
    req = urllib.request.Request(
        BASE + path,
        data    = body,
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method  = "POST",
    )
    if key is not None:
        req.add_header("X-API-Key", key)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            resp_body = r.read().decode()
            status    = r.status
            headers   = dict(r.headers)
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode()
        status    = e.code
        headers   = dict(e.headers or {})
    try:
        body_json = json.loads(resp_body) if resp_body else {}
    except json.JSONDecodeError:
        body_json = {"raw": resp_body}
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


# ── Ship 4'.b: POST /query tests ──────────────────────────────────────

RAW_KEY_QUERY = "test_ext_key_ship4b_query_" + uuid.uuid4().hex[:8]


@contextmanager
def _test_state_query():
    """Fixture variant that additionally seeds a key with
    external:query scope so /query happy-path tests work.

    The internal RAG pipeline queries posture_controls scoped to the
    tenant. The throwaway test tenant has none, so /query answers
    will be sparse but the endpoint contract is exercised."""
    with _test_state() as (conn, seeds):
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            cur.execute("""
                INSERT INTO api_keys (tenant_id, user_id, key_hash, key_prefix,
                                      name, scopes, is_active)
                VALUES (%s::uuid, %s::uuid, %s, 'test_ext_', 'TEST query key',
                        ARRAY['external:query'], TRUE)
                RETURNING id::text
            """, (TEST_TENANT_ID, TEST_USER_ID, _sha256(RAW_KEY_QUERY)))
            query_id = cur.fetchone()[0]
        conn.commit()
        seeds["query_id"] = query_id
        yield conn, seeds


def test_query_missing_body_returns_422():
    """Empty POST body → Pydantic validation → 422 structured error."""
    with _test_state_query() as _:
        code, body, _h = _post("/api/external/v1/query", {}, key=RAW_KEY_QUERY)
        return _ok(
            code == 422
            and body.get("error", {}).get("code") == "invalid_input",
            f"code={code} body={body}",
        )


def test_query_empty_question_returns_422():
    """min_length=1 on QueryRequest.question — empty string rejected."""
    with _test_state_query() as _:
        code, body, _h = _post(
            "/api/external/v1/query", {"question": ""}, key=RAW_KEY_QUERY,
        )
        return _ok(
            code == 422 and body.get("error", {}).get("code") == "invalid_input",
            f"code={code} body={body}",
        )


def test_query_wrong_scope_returns_403():
    """/query requires external:query; a key with only external:status
    should get 403."""
    with _test_state_query() as _:
        code, body, _h = _post(
            "/api/external/v1/query", {"question": "hello?"},
            key=RAW_KEY_GOOD,   # has external:status but not external:query
        )
        return _ok(
            code == 403
            and "external:query" in (body.get("error", {}).get("message") or ""),
            f"code={code} body={body}",
        )


def test_query_happy_path_returns_structured_response():
    """Happy path: valid key with external:query + a real question →
    200 with the QueryResponse shape."""
    with _test_state_query() as _:
        code, body, headers = _post(
            "/api/external/v1/query",
            {"question": "what are our access rights gaps?"},
            key=RAW_KEY_QUERY,
        )
        return _ok(
            code == 200
            and isinstance(body.get("answer"), str) and len(body["answer"]) > 0
            and isinstance(body.get("citations"), list)
            and body.get("session_id", "").startswith("ext_")
            and isinstance(body.get("request_id"), str)
            and isinstance(body.get("latency_ms"), int)
            and body.get("latency_ms") > 0
            and body.get("needs_clarification") in (True, False)
            # Rate-limit headers on 200 (same as /status)
            and headers.get("x-ratelimit-limit") == "60",
            f"code={code} body_keys={list(body.keys())} headers={dict(headers)}",
        )


def test_query_session_id_echo_and_multi_turn():
    """Sending a session_id on turn 1 should be echoed on the response.
    Turn 2 with the same session_id should also succeed (state persists
    via the LangGraph checkpointer)."""
    with _test_state_query() as _:
        my_sid = "ship4b_test_" + uuid.uuid4().hex[:8]
        code1, body1, _h1 = _post(
            "/api/external/v1/query",
            {"question": "what are our access rights gaps?", "session_id": my_sid},
            key=RAW_KEY_QUERY,
        )
        if code1 != 200 or body1.get("session_id") != my_sid:
            return _ok(False, f"turn1 code={code1} body={body1}")
        code2, body2, _h2 = _post(
            "/api/external/v1/query",
            {"question": "what about A.5.18?", "session_id": my_sid},
            key=RAW_KEY_QUERY,
        )
        return _ok(
            code2 == 200 and body2.get("session_id") == my_sid,
            f"turn2 code={code2} sid={body2.get('session_id')}",
        )


def test_query_bad_session_id_returns_400():
    """session_id must be letters/digits/hyphens/underscores; SQL
    fragments / path traversal are rejected at the boundary."""
    with _test_state_query() as _:
        code, body, _h = _post(
            "/api/external/v1/query",
            {"question": "hello", "session_id": "'; DROP TABLE users; --"},
            key=RAW_KEY_QUERY,
        )
        return _ok(
            code == 400
            and body.get("error", {}).get("code") == "invalid_input",
            f"code={code} body={body}",
        )


TESTS += [
    test_query_missing_body_returns_422,
    test_query_empty_question_returns_422,
    test_query_wrong_scope_returns_403,
    test_query_happy_path_returns_structured_response,
    test_query_session_id_echo_and_multi_turn,
    test_query_bad_session_id_returns_400,
]


# ── Ship 4'.c: /posture endpoint tests ────────────────────────────────
# The test tenant (77777777-...) has no posture rows seeded, so happy-
# path responses return empty lists. We seed a couple of rows so the
# summary/filter logic gets exercised.

RAW_KEY_POSTURE = "test_ext_key_ship4c_posture_" + uuid.uuid4().hex[:8]


@contextmanager
def _test_state_posture():
    """Fixture variant: seeds a key with external:posture:read + 2
    posture_controls rows on the test tenant. Cleanup drops the
    posture rows so successive runs get a clean state."""
    with _test_state() as (conn, seeds):
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            cur.execute("""
                INSERT INTO api_keys (tenant_id, user_id, key_hash, key_prefix,
                                      name, scopes, is_active)
                VALUES (%s::uuid, %s::uuid, %s, 'test_ext_', 'TEST posture key',
                        ARRAY['external:posture:read'], TRUE)
                RETURNING id::text
            """, (TEST_TENANT_ID, TEST_USER_ID, _sha256(RAW_KEY_POSTURE)))
            key_id = cur.fetchone()[0]

            # Idempotent posture seed: 2 controls, distinct findings
            cur.execute("""
                INSERT INTO posture_controls
                    (tenant_id, standard_id, control_ref, node_id,
                     finding, confidence, is_active, gap_description)
                VALUES
                    (%s::uuid,'ISO27001:2022','A.5.18',
                     'ISO27001:2022:A.5.18','NC','high',TRUE,
                     'TEST: gap for A.5.18'),
                    (%s::uuid,'ISO27001:2022','A.5.15',
                     'ISO27001:2022:A.5.15','Comply','high',TRUE,
                     'TEST: policy in place')
                ON CONFLICT (tenant_id, standard_id, control_ref) WHERE is_active
                    DO UPDATE SET finding = EXCLUDED.finding
            """, (TEST_TENANT_ID, TEST_TENANT_ID))
        conn.commit()
        seeds["posture_key_id"] = key_id
        try:
            yield conn, seeds
        finally:
            with conn.cursor() as cur:
                cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                            (TEST_TENANT_ID,))
                cur.execute("""
                    DELETE FROM posture_controls
                     WHERE tenant_id=%s::uuid
                       AND control_ref IN ('A.5.18','A.5.15')
                       AND standard_id='ISO27001:2022'
                """, (TEST_TENANT_ID,))
            conn.commit()


def test_frameworks_happy_path():
    with _test_state_posture() as _:
        code, body, _h = _get("/api/external/v1/frameworks", key=RAW_KEY_POSTURE)
        return _ok(
            code == 200
            and isinstance(body.get("frameworks"), list)
            and any(fw.get("standard_id") == "ISO27001:2022"
                    for fw in body.get("frameworks", []))
            and body.get("tenant_id") == TEST_TENANT_ID,
            f"code={code} body={body}",
        )


def test_frameworks_scope_check():
    """Key without external:posture:read gets 403."""
    with _test_state_posture() as _:
        code, body, _h = _get("/api/external/v1/frameworks", key=RAW_KEY_GOOD)
        return _ok(
            code == 403 and "external:posture:read" in (body.get("error", {}).get("message") or ""),
            f"code={code} body={body}",
        )


def test_posture_snapshot_happy_path():
    with _test_state_posture() as _:
        code, body, headers = _get(
            "/api/external/v1/posture?standard_id=ISO27001:2022",
            key=RAW_KEY_POSTURE,
        )
        controls = body.get("controls", [])
        refs = {c["ref"] for c in controls if c.get("ref")}
        return _ok(
            code == 200
            and body.get("tenant_id") == TEST_TENANT_ID
            and "A.5.18" in refs and "A.5.15" in refs
            and body.get("summary", {}).get("total", 0) >= 2
            and body.get("summary", {}).get("NC", 0) >= 1
            and body.get("summary", {}).get("Comply", 0) >= 1
            and headers.get("x-ratelimit-limit") == "60",
            f"code={code} refs={refs} summary={body.get('summary')}",
        )


def test_posture_finding_filter():
    """finding=NC should return only NC rows."""
    with _test_state_posture() as _:
        code, body, _h = _get(
            "/api/external/v1/posture?standard_id=ISO27001:2022&finding=NC",
            key=RAW_KEY_POSTURE,
        )
        controls = body.get("controls", [])
        findings = {c.get("finding") for c in controls}
        return _ok(
            code == 200
            and findings == {"NC"}
            and any(c["ref"] == "A.5.18" for c in controls),
            f"findings={findings} controls_len={len(controls)}",
        )


def test_posture_bad_finding_returns_400():
    with _test_state_posture() as _:
        code, body, _h = _get(
            "/api/external/v1/posture?finding=WEIRD",
            key=RAW_KEY_POSTURE,
        )
        return _ok(
            code == 400 and body.get("error", {}).get("code") == "invalid_input",
            f"code={code} body={body}",
        )


def test_posture_bad_changed_since_returns_400():
    with _test_state_posture() as _:
        code, body, _h = _get(
            "/api/external/v1/posture?changed_since=notadate",
            key=RAW_KEY_POSTURE,
        )
        return _ok(
            code == 400 and body.get("error", {}).get("code") == "invalid_input",
            f"code={code} body={body}",
        )


def test_posture_drill_in_happy_path():
    with _test_state_posture() as _:
        code, body, _h = _get(
            "/api/external/v1/posture/A.5.18?standard_id=ISO27001:2022",
            key=RAW_KEY_POSTURE,
        )
        return _ok(
            code == 200
            and body.get("ref") == "A.5.18"
            and body.get("standard_id") == "ISO27001:2022"
            and body.get("finding") == "NC"
            and body.get("tenant_id") == TEST_TENANT_ID,
            f"code={code} body={body}",
        )


def test_posture_drill_in_unknown_ref_returns_404():
    with _test_state_posture() as _:
        code, body, _h = _get(
            "/api/external/v1/posture/A.99.99?standard_id=ISO27001:2022",
            key=RAW_KEY_POSTURE,
        )
        return _ok(
            code == 404
            and body.get("error", {}).get("code") == "not_found",
            f"code={code} body={body}",
        )


def test_posture_drill_in_missing_standard_id_returns_422():
    """standard_id is required — refs like Art.32 can exist across
    multiple frameworks. Fail loud rather than guess."""
    with _test_state_posture() as _:
        code, body, _h = _get(
            "/api/external/v1/posture/A.5.18",
            key=RAW_KEY_POSTURE,
        )
        return _ok(
            code == 422
            and body.get("error", {}).get("code") == "invalid_input",
            f"code={code} body={body}",
        )


TESTS += [
    test_frameworks_happy_path,
    test_frameworks_scope_check,
    test_posture_snapshot_happy_path,
    test_posture_finding_filter,
    test_posture_bad_finding_returns_400,
    test_posture_bad_changed_since_returns_400,
    test_posture_drill_in_happy_path,
    test_posture_drill_in_unknown_ref_returns_404,
    test_posture_drill_in_missing_standard_id_returns_422,
]


# ── Ship 4'.d: /notifications tests ───────────────────────────────────

RAW_KEY_NOTIF = "test_ext_key_ship4d_notif_" + uuid.uuid4().hex[:8]


@contextmanager
def _test_state_notifications():
    """Fixture: seeds a key with external:notifications:read + 4
    notifications with distinct kinds/severities so filter tests
    have data to work with. Teardown removes seeded rows."""
    with _test_state() as (conn, seeds):
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            cur.execute("""
                INSERT INTO api_keys (tenant_id, user_id, key_hash, key_prefix,
                                      name, scopes, is_active)
                VALUES (%s::uuid, %s::uuid, %s, 'test_ext_', 'TEST notif key',
                        ARRAY['external:notifications:read'], TRUE)
                RETURNING id::text
            """, (TEST_TENANT_ID, TEST_USER_ID, _sha256(RAW_KEY_NOTIF)))
            key_id = cur.fetchone()[0]

            # Seed 4 notifications: 2 high (unread), 1 medium (read),
            # 1 low (dismissed). Deterministic titles for lookup.
            cur.execute("""
                INSERT INTO tenant_notification
                    (tenant_id, kind, title, body, severity, related_control_ref)
                VALUES
                    (%s::uuid,'nc_surfaced','TEST-4d-1: unread high',    '','high',   'A.5.18'),
                    (%s::uuid,'nc_surfaced','TEST-4d-2: unread high 2',  '','high',   'A.6.4'),
                    (%s::uuid,'freshness_expiry','TEST-4d-3: read medium','','medium','A.5.15')
                RETURNING id::text
            """, (TEST_TENANT_ID, TEST_TENANT_ID, TEST_TENANT_ID))
            ids = [r[0] for r in cur.fetchall()]
            # Mark the medium one as read
            cur.execute("""
                UPDATE tenant_notification SET read_at = NOW()
                 WHERE id=%s::uuid
            """, (ids[2],))
            # 4th notification: low severity + dismissed
            cur.execute("""
                INSERT INTO tenant_notification
                    (tenant_id, kind, title, body, severity, dismissed_at)
                VALUES (%s::uuid,'auto_resolved','TEST-4d-4: dismissed low','','low', NOW())
                RETURNING id::text
            """, (TEST_TENANT_ID,))
            ids.append(cur.fetchone()[0])
        conn.commit()
        seeds["notif_key_id"] = key_id
        seeds["notif_ids"]    = ids
        try:
            yield conn, seeds
        finally:
            with conn.cursor() as cur:
                cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                            (TEST_TENANT_ID,))
                cur.execute("""
                    DELETE FROM tenant_notification
                     WHERE tenant_id=%s::uuid AND title LIKE 'TEST-4d-%%'
                """, (TEST_TENANT_ID,))
            conn.commit()


def test_notifications_list_happy_path():
    with _test_state_notifications() as _:
        code, body, _h = _get(
            "/api/external/v1/notifications", key=RAW_KEY_NOTIF,
        )
        titles = {n["title"] for n in body.get("notifications", [])}
        # Default: excludes dismissed, so we see 3 not 4
        return _ok(
            code == 200
            and body.get("summary", {}).get("total") == 3
            and body.get("summary", {}).get("unread") == 2   # 2 high, medium is read
            and body.get("summary", {}).get("urgent") == 2   # 2 unread + high
            and "TEST-4d-1: unread high" in titles
            and "TEST-4d-4: dismissed low" not in titles,
            f"code={code} summary={body.get('summary')} titles={titles}",
        )


def test_notifications_include_dismissed():
    with _test_state_notifications() as _:
        code, body, _h = _get(
            "/api/external/v1/notifications?include_dismissed=true",
            key=RAW_KEY_NOTIF,
        )
        titles = {n["title"] for n in body.get("notifications", [])}
        return _ok(
            code == 200
            and body.get("summary", {}).get("total") == 4
            and "TEST-4d-4: dismissed low" in titles,
            f"code={code} summary={body.get('summary')} titles={titles}",
        )


def test_notifications_unread_only():
    with _test_state_notifications() as _:
        code, body, _h = _get(
            "/api/external/v1/notifications?unread_only=true",
            key=RAW_KEY_NOTIF,
        )
        return _ok(
            code == 200
            and body.get("summary", {}).get("total") == 2
            and body.get("summary", {}).get("unread") == 2,
            f"code={code} summary={body.get('summary')}",
        )


def test_notifications_kind_filter():
    with _test_state_notifications() as _:
        code, body, _h = _get(
            "/api/external/v1/notifications?kind=nc_surfaced",
            key=RAW_KEY_NOTIF,
        )
        kinds = {n["kind"] for n in body.get("notifications", [])}
        return _ok(
            code == 200
            and kinds == {"nc_surfaced"}
            and body.get("summary", {}).get("total") == 2,
            f"kinds={kinds} summary={body.get('summary')}",
        )


def test_notifications_severity_filter():
    with _test_state_notifications() as _:
        code, body, _h = _get(
            "/api/external/v1/notifications?severity=medium",
            key=RAW_KEY_NOTIF,
        )
        return _ok(
            code == 200
            and body.get("summary", {}).get("total") == 1
            and body["notifications"][0]["severity"] == "medium",
            f"body={body}",
        )


def test_notifications_bad_kind_returns_400():
    with _test_state_notifications() as _:
        code, body, _h = _get(
            "/api/external/v1/notifications?kind=WEIRD_KIND",
            key=RAW_KEY_NOTIF,
        )
        return _ok(
            code == 400 and body.get("error", {}).get("code") == "invalid_input",
            f"code={code} body={body}",
        )


def test_notifications_bad_since_returns_400():
    with _test_state_notifications() as _:
        code, body, _h = _get(
            "/api/external/v1/notifications?since=notatimestamp",
            key=RAW_KEY_NOTIF,
        )
        return _ok(
            code == 400 and body.get("error", {}).get("code") == "invalid_input",
            f"code={code} body={body}",
        )


def test_notifications_scope_check():
    with _test_state_notifications() as _:
        code, body, _h = _get(
            "/api/external/v1/notifications", key=RAW_KEY_GOOD,
        )
        return _ok(
            code == 403
            and "external:notifications:read" in (body.get("error", {}).get("message") or ""),
            f"code={code} body={body}",
        )


def test_notifications_single_by_id():
    with _test_state_notifications() as (_conn, seeds):
        nid = seeds["notif_ids"][0]  # the first seeded notification
        code, body, _h = _get(
            f"/api/external/v1/notifications/{nid}", key=RAW_KEY_NOTIF,
        )
        return _ok(
            code == 200 and body.get("id") == nid,
            f"code={code} body={body}",
        )


def test_notifications_unknown_id_returns_404():
    with _test_state_notifications() as _:
        code, body, _h = _get(
            "/api/external/v1/notifications/00000000-0000-0000-0000-999999999999",
            key=RAW_KEY_NOTIF,
        )
        return _ok(
            code == 404 and body.get("error", {}).get("code") == "not_found",
            f"code={code} body={body}",
        )


def test_notifications_malformed_id_returns_400():
    with _test_state_notifications() as _:
        code, body, _h = _get(
            "/api/external/v1/notifications/not-a-uuid",
            key=RAW_KEY_NOTIF,
        )
        return _ok(
            code == 400 and body.get("error", {}).get("code") == "invalid_input",
            f"code={code} body={body}",
        )


TESTS += [
    test_notifications_list_happy_path,
    test_notifications_include_dismissed,
    test_notifications_unread_only,
    test_notifications_kind_filter,
    test_notifications_severity_filter,
    test_notifications_bad_kind_returns_400,
    test_notifications_bad_since_returns_400,
    test_notifications_scope_check,
    test_notifications_single_by_id,
    test_notifications_unknown_id_returns_404,
    test_notifications_malformed_id_returns_400,
]


# ── Ship 4'.e: /evidence + /documents tests ───────────────────────────

RAW_KEY_EVIDENCE_READ  = "test_ext_key_ship4e_read_"  + uuid.uuid4().hex[:8]
RAW_KEY_EVIDENCE_WRITE = "test_ext_key_ship4e_write_" + uuid.uuid4().hex[:8]


@contextmanager
def _test_state_evidence():
    """Fixture: seeds a client_documents row + a document_findings row
    on the test tenant + two api_keys (read + write scopes). Cleanup
    removes seeded rows + any documents uploaded during the test."""
    with _test_state() as (conn, seeds):
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            cur.execute("""
                INSERT INTO api_keys (tenant_id, user_id, key_hash, key_prefix,
                                      name, scopes, is_active)
                VALUES
                    (%s::uuid, %s::uuid, %s, 'test_ext_',
                     'TEST evidence-read key', ARRAY['external:evidence:read'], TRUE),
                    (%s::uuid, %s::uuid, %s, 'test_ext_',
                     'TEST evidence-write key', ARRAY['external:evidence:write','external:evidence:read'], TRUE)
                RETURNING id::text
            """, (TEST_TENANT_ID, TEST_USER_ID, _sha256(RAW_KEY_EVIDENCE_READ),
                  TEST_TENANT_ID, TEST_USER_ID, _sha256(RAW_KEY_EVIDENCE_WRITE)))
            _ids = [r[0] for r in cur.fetchall()]

            # Seed a client_documents row + a document_findings row that
            # references it, so /evidence has data to return.
            cur.execute("""
                INSERT INTO client_documents (
                    id, tenant_id, filename, evidence_type
                ) VALUES (
                    gen_random_uuid(), %s::uuid, 'TEST-4e-policy.docx', 'policy'
                )
                RETURNING id::text
            """, (TEST_TENANT_ID,))
            client_doc_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO document_findings (
                    tenant_id, document_id, control_ref, standard_id,
                    status, confidence, excerpt, inference_source
                ) VALUES (
                    %s::uuid, %s::uuid, 'A.5.18', 'ISO27001:2022',
                    'present', 'high', 'TEST-4e: access review Q1 2026',
                    'templated'
                )
                RETURNING id::text
            """, (TEST_TENANT_ID, client_doc_id))
            finding_id = cur.fetchone()[0]
        conn.commit()
        seeds["client_doc_id"] = client_doc_id
        seeds["finding_id"]    = finding_id
        try:
            yield conn, seeds
        finally:
            with conn.cursor() as cur:
                cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                            (TEST_TENANT_ID,))
                cur.execute("DELETE FROM document_findings WHERE tenant_id=%s::uuid",
                            (TEST_TENANT_ID,))
                cur.execute("DELETE FROM document_uploads WHERE tenant_id=%s::uuid",
                            (TEST_TENANT_ID,))
                cur.execute("DELETE FROM client_documents WHERE tenant_id=%s::uuid",
                            (TEST_TENANT_ID,))
            conn.commit()


def test_evidence_happy_path():
    with _test_state_evidence() as _:
        code, body, _h = _get(
            "/api/external/v1/evidence?control_ref=A.5.18&standard_id=ISO27001:2022",
            key=RAW_KEY_EVIDENCE_READ,
        )
        items = body.get("evidence", [])
        return _ok(
            code == 200
            and body.get("control_ref") == "A.5.18"
            and body.get("standard_id") == "ISO27001:2022"
            and body.get("count") >= 1
            and any(e.get("filename") == "TEST-4e-policy.docx" for e in items)
            and any(e.get("inference_source") == "templated" for e in items),
            f"code={code} body={body}",
        )


def test_evidence_scope_check():
    with _test_state_evidence() as _:
        code, body, _h = _get(
            "/api/external/v1/evidence?control_ref=A.5.18&standard_id=ISO27001:2022",
            key=RAW_KEY_GOOD,  # only external:status
        )
        return _ok(
            code == 403
            and "external:evidence:read" in (body.get("error", {}).get("message") or ""),
            f"code={code} body={body}",
        )


def test_evidence_missing_query_params_returns_422():
    with _test_state_evidence() as _:
        code, body, _h = _get(
            "/api/external/v1/evidence",  # no control_ref, no standard_id
            key=RAW_KEY_EVIDENCE_READ,
        )
        return _ok(
            code == 422 and body.get("error", {}).get("code") == "invalid_input",
            f"code={code} body={body}",
        )


def test_document_status_unknown_returns_404():
    with _test_state_evidence() as _:
        code, body, _h = _get(
            "/api/external/v1/documents/00000000-0000-0000-0000-999999999999",
            key=RAW_KEY_EVIDENCE_READ,
        )
        return _ok(
            code == 404 and body.get("error", {}).get("code") == "not_found",
            f"code={code} body={body}",
        )


def test_document_status_malformed_id_returns_400():
    with _test_state_evidence() as _:
        code, body, _h = _get(
            "/api/external/v1/documents/not-a-uuid",
            key=RAW_KEY_EVIDENCE_READ,
        )
        return _ok(
            code == 400 and body.get("error", {}).get("code") == "invalid_input",
            f"code={code} body={body}",
        )


def test_document_upload_happy_path():
    """Multipart upload of a small markdown doc. Returns pending
    immediately."""
    with _test_state_evidence() as _:
        content = b"# TEST 4e upload\n\nSmall test document for Ship 4'.e.\n"
        code, body, _h = _post_multipart(
            "/api/external/v1/documents",
            filename    = "TEST-4e-upload.md",
            content     = content,
            extra_fields= {"declared_standard_id": "ISO27001:2022"},
            key         = RAW_KEY_EVIDENCE_WRITE,
        )
        return _ok(
            code == 200
            and body.get("extraction_status") == "pending"
            and body.get("filename") == "TEST-4e-upload.md"
            and body.get("byte_size") == len(content)
            and body.get("upload_id"),
            f"code={code} body={body}",
        )


def test_document_upload_scope_check():
    """external:evidence:read alone doesn't grant write."""
    with _test_state_evidence() as _:
        code, body, _h = _post_multipart(
            "/api/external/v1/documents",
            filename= "TEST-4e-scope.md",
            content = b"hello",
            key     = RAW_KEY_EVIDENCE_READ,
        )
        return _ok(
            code == 403
            and "external:evidence:write" in (body.get("error", {}).get("message") or ""),
            f"code={code} body={body}",
        )


def test_document_upload_bad_extension_returns_400():
    with _test_state_evidence() as _:
        code, body, _h = _post_multipart(
            "/api/external/v1/documents",
            filename= "TEST-4e-bad.zip",
            content = b"not really a zip",
            key     = RAW_KEY_EVIDENCE_WRITE,
        )
        return _ok(
            code == 400 and body.get("error", {}).get("code") == "invalid_input",
            f"code={code} body={body}",
        )


def test_document_upload_dedup_returns_canonical():
    """Uploading the same content twice returns extraction_status
    'duplicate' + canonical_upload_id pointing at the first upload."""
    with _test_state_evidence() as _:
        content = b"# TEST 4e dedup\n\nContent A.\n" + uuid.uuid4().hex.encode()
        code1, body1, _h = _post_multipart(
            "/api/external/v1/documents",
            filename= "TEST-4e-dedup.md",
            content = content,
            key     = RAW_KEY_EVIDENCE_WRITE,
        )
        if code1 != 200:
            return _ok(False, f"first upload failed: {body1}")
        first_id = body1["upload_id"]
        code2, body2, _h = _post_multipart(
            "/api/external/v1/documents",
            filename= "TEST-4e-dedup-again.md",
            content = content,
            key     = RAW_KEY_EVIDENCE_WRITE,
        )
        return _ok(
            code2 == 200
            and body2.get("extraction_status") == "duplicate"
            and body2.get("canonical_upload_id") == first_id,
            f"code={code2} body={body2}",
        )


TESTS += [
    test_evidence_happy_path,
    test_evidence_scope_check,
    test_evidence_missing_query_params_returns_422,
    test_document_status_unknown_returns_404,
    test_document_status_malformed_id_returns_400,
    test_document_upload_happy_path,
    test_document_upload_scope_check,
    test_document_upload_bad_extension_returns_400,
    test_document_upload_dedup_returns_canonical,
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
