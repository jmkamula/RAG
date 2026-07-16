"""
Tests for rag/api_types.py — FastAPI path-param validators + session_id
shape validator + thread_id builder.

Run: PYTHONPATH=/data/arioncomply python3 tests/test_api_types.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from rag.api_types import (
    build_thread_id, validate_session_id_shape,
)


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


# ── build_thread_id ───────────────────────────────────────────────────

def test_build_thread_id_uses_full_uuid():
    """Ship 2'.l: full UUID, not [:8] truncation."""
    tid = "00000000-0000-0000-0000-000000000001"
    sid = "my-session"
    result = build_thread_id(tid, sid)
    return _ok(result == f"{tid}:{sid}", result)


def test_build_thread_id_two_different_tenants_never_collide():
    """The main security property: two different tenants can never
    share a thread_id even with identical session_ids. Enforces the
    Ship 2'.l invariant against cross-tenant checkpoint reads."""
    t1 = "aaaaaaaa-0000-0000-0000-000000000001"
    t2 = "aaaaaaaa-0000-0000-0000-000000000002"   # same [:8] prefix
    sid = "same-session"
    thread_1 = build_thread_id(t1, sid)
    thread_2 = build_thread_id(t2, sid)
    return _ok(thread_1 != thread_2, f"collision! {thread_1} == {thread_2}")


# ── validate_session_id_shape ─────────────────────────────────────────

def test_shape_accepts_alphanum():
    return _ok(validate_session_id_shape("abc123"))


def test_shape_accepts_hyphens_and_underscores():
    return _ok(
        validate_session_id_shape("my-session-1")
        and validate_session_id_shape("my_session_1")
        and validate_session_id_shape("api_deadbeef")
    )


def test_shape_accepts_max_length_64():
    return _ok(validate_session_id_shape("x" * 64))


def test_shape_rejects_over_64():
    return _ok(not validate_session_id_shape("x" * 65))


def test_shape_rejects_empty():
    return _ok(not validate_session_id_shape(""))


def test_shape_rejects_none():
    return _ok(not validate_session_id_shape(None))


def test_shape_rejects_non_string():
    return _ok(not validate_session_id_shape(12345))


def test_shape_rejects_path_traversal():
    return _ok(not validate_session_id_shape("../../etc/passwd"))


def test_shape_rejects_sql_fragment():
    return _ok(not validate_session_id_shape("'; drop table users; --"))


def test_shape_rejects_spaces():
    return _ok(not validate_session_id_shape("hello world"))


def test_shape_rejects_special_chars():
    for c in ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")",
              "=", "+", "[", "]", "{", "}", "|", "\\", "/", ":",
              ";", "\"", "'", "<", ">", ",", ".", "?"]:
        if validate_session_id_shape(f"session{c}bad"):
            return _ok(False, f"accepted {c!r}")
    return _ok(True)


TESTS = [
    test_build_thread_id_uses_full_uuid,
    test_build_thread_id_two_different_tenants_never_collide,
    test_shape_accepts_alphanum,
    test_shape_accepts_hyphens_and_underscores,
    test_shape_accepts_max_length_64,
    test_shape_rejects_over_64,
    test_shape_rejects_empty,
    test_shape_rejects_none,
    test_shape_rejects_non_string,
    test_shape_rejects_path_traversal,
    test_shape_rejects_sql_fragment,
    test_shape_rejects_spaces,
    test_shape_rejects_special_chars,
]


def main():
    print("─" * 70)
    print("  api_types tests")
    print("─" * 70)
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
