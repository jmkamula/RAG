"""Unit tests for rag/answer/dispatcher.py."""
import sys
import types as _types

from rag.answer.dispatcher import (
    dispatch_builder, register_builder, registered_taxonomies,
    _normalize_question_type,
)
from rag.answer.types import (
    AnswerPayloadBase, FreeformPayload, PostureStatusPayload,
)


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


class _FakeIntent:
    """Minimal QueryIntent-shaped fake."""
    def __init__(self, question_type="unknown", cited_refs=None, raw_query=""):
        self.question_type = question_type
        self.cited_refs    = cited_refs or []
        self.raw_query     = raw_query


class _FakeEnumIntent:
    """Fake with enum-shaped question_type."""
    def __init__(self, qt_value):
        self.question_type = _types.SimpleNamespace(value=qt_value)
        self.cited_refs    = []
        self.raw_query     = ""


def _clear_registry():
    """Test helper — dispatcher module-global registry."""
    from rag.answer import dispatcher
    dispatcher._BUILDERS.clear()


# ── _normalize_question_type ─────────────────────────────────────────

def test_normalize_none_intent():
    return _ok(_normalize_question_type(None) == "unknown")


def test_normalize_string_qt():
    intent = _FakeIntent(question_type="POSTURE_CHECK")
    return _ok(_normalize_question_type(intent) == "posture_check")


def test_normalize_enum_qt():
    intent = _FakeEnumIntent(qt_value="Definition")
    return _ok(_normalize_question_type(intent) == "definition")


# ── dispatch_builder — freeform fallback ─────────────────────────────

def test_dispatch_unknown_type_falls_to_freeform():
    _clear_registry()
    intent = _FakeIntent(question_type="unknown", raw_query="asdf")
    p = dispatch_builder(intent, None, None)
    return _ok(isinstance(p, FreeformPayload), f"got {type(p).__name__}")


def test_dispatch_taxonomy_without_builder_falls_to_freeform():
    _clear_registry()
    intent = _FakeIntent(question_type="posture_check")
    p = dispatch_builder(intent, None, None)
    # No registered builder for posture_check yet (until Ship 2.2)
    return _ok(isinstance(p, FreeformPayload))


def test_dispatch_uses_registered_builder():
    _clear_registry()
    def _fake_posture_builder(intent, tenant_context, resolver,
                              neo_driver=None, chroma_retriever=None):
        return PostureStatusPayload(
            question_type="posture_check", query=intent.raw_query,
        )
    register_builder("posture_check", _fake_posture_builder)
    intent = _FakeIntent(question_type="posture_check", raw_query="q1")
    p = dispatch_builder(intent, None, None)
    _clear_registry()
    return _ok(
        isinstance(p, PostureStatusPayload) and p.query == "q1",
        f"got {type(p).__name__}",
    )


def test_dispatch_builder_crash_falls_to_freeform():
    _clear_registry()
    def _crashy_builder(intent, tenant_context, resolver,
                        neo_driver=None, chroma_retriever=None):
        raise RuntimeError("simulated builder crash")
    register_builder("posture_check", _crashy_builder)
    intent = _FakeIntent(question_type="posture_check")
    p = dispatch_builder(intent, None, None)
    _clear_registry()
    return _ok(
        isinstance(p, FreeformPayload)
        and "RuntimeError" in (p.reason_fallback or ""),
        f"got {type(p).__name__} reason={p.reason_fallback if isinstance(p, FreeformPayload) else 'n/a'}",
    )


# ── registered_taxonomies ───────────────────────────────────────────

def test_registered_taxonomies_empty_initially():
    _clear_registry()
    return _ok(registered_taxonomies() == [])


def test_registered_taxonomies_lists_after_register():
    _clear_registry()
    register_builder("posture_check", lambda **kw: None)
    register_builder("definition", lambda **kw: None)
    got = registered_taxonomies()
    _clear_registry()
    return _ok(got == ["definition", "posture_check"], f"got {got}")


TESTS = [
    test_normalize_none_intent,
    test_normalize_string_qt,
    test_normalize_enum_qt,
    test_dispatch_unknown_type_falls_to_freeform,
    test_dispatch_taxonomy_without_builder_falls_to_freeform,
    test_dispatch_uses_registered_builder,
    test_dispatch_builder_crash_falls_to_freeform,
    test_registered_taxonomies_empty_initially,
    test_registered_taxonomies_lists_after_register,
]


def main():
    print("─" * 70)
    print("  Ship 2.0 — dispatcher unit tests")
    print("─" * 70)
    failures = 0
    for t in TESTS:
        try:
            ok, msg = t()
        except Exception as e:
            ok, msg = False, f"raised {type(e).__name__}: {e}"
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
