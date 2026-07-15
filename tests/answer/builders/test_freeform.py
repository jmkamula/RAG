"""Unit tests for rag/answer/builders/freeform.py."""
import sys
import types as _types

from rag.answer.builders.freeform import build, _infer_framework, _dominant_framework
from rag.answer.types import FreeformPayload


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


class _FakeIntent:
    def __init__(self, question_type="unknown", cited_refs=None, raw_query=""):
        self.question_type = question_type
        self.cited_refs    = cited_refs or []
        self.raw_query     = raw_query


class _FakeEnumIntent:
    def __init__(self, qt_value, cited_refs=None, raw_query=""):
        self.question_type = _types.SimpleNamespace(value=qt_value)
        self.cited_refs    = cited_refs or []
        self.raw_query     = raw_query


def _tenant(scope=None, tenant_id="test-uuid", tenant_name="Test"):
    return _types.SimpleNamespace(
        tenant_id=tenant_id,
        tenant_name=tenant_name,
        scope=_types.SimpleNamespace(queryable_standards=scope or ["ISO27001:2022"]),
    )


# ── _infer_framework ─────────────────────────────────────────────────

def test_infer_gdpr_from_article_ref():
    return _ok(_infer_framework("Art.32") == "GDPR:2016/679")


def test_infer_iso_27001_from_annex_a():
    return _ok(_infer_framework("A.5.18") == "ISO27001:2022")


def test_infer_iso_27701_from_a_7_2_x():
    return _ok(_infer_framework("A.7.2.5") == "ISO27701:2019")


def test_infer_iso_27701_from_b_prefix():
    return _ok(_infer_framework("B.8.5.6") == "ISO27701:2019")


def test_infer_iso_isms_clause():
    return _ok(_infer_framework("9.2") == "ISO27001:2022")


def test_infer_unknown_ref():
    return _ok(_infer_framework("XYZ.1") == "")


# ── _dominant_framework ─────────────────────────────────────────────

def test_dominant_single_framework():
    return _ok(
        _dominant_framework(["ISO27001:2022", "ISO27001:2022"])
        == "ISO27001:2022",
    )


def test_dominant_majority():
    return _ok(
        _dominant_framework(["ISO27001:2022", "ISO27001:2022", "GDPR:2016/679"])
        == "ISO27001:2022",
    )


def test_dominant_tie_returns_none():
    return _ok(
        _dominant_framework(["ISO27001:2022", "GDPR:2016/679"]) is None,
    )


def test_dominant_empty_returns_none():
    return _ok(_dominant_framework([]) is None)


# ── build() ─────────────────────────────────────────────────────────

def test_build_empty_query_produces_payload():
    p = build(intent=None, tenant_context=None, resolver=None)
    return _ok(
        isinstance(p, FreeformPayload)
        and p.question_type == "unknown"
        and p.query == "",
    )


def test_build_with_intent_carries_query():
    intent = _FakeIntent(raw_query="what is our posture?")
    p = build(intent=intent, tenant_context=None, resolver=None)
    return _ok(p.query == "what is our posture?")


def test_build_extracts_question_type_from_enum():
    intent = _FakeEnumIntent(qt_value="POSTURE_CHECK")
    p = build(intent=intent, tenant_context=None, resolver=None)
    return _ok(p.question_type == "posture_check")


def test_build_extracts_subject_refs_from_cited():
    intent = _FakeIntent(cited_refs=["A.5.18", "Art.32"])
    p = build(intent=intent, tenant_context=None, resolver=None)
    refs = {r.ref: r.framework for r in p.subject_refs}
    return _ok(
        refs == {"A.5.18": "ISO27001:2022", "Art.32": "GDPR:2016/679"},
        f"refs={refs}",
    )


def test_build_ignores_none_in_cited_refs():
    intent = _FakeIntent(cited_refs=[None, "A.5.18", None])
    p = build(intent=intent, tenant_context=None, resolver=None)
    return _ok(
        len(p.subject_refs) == 1 and p.subject_refs[0].ref == "A.5.18",
    )


def test_build_carries_tenant_scope():
    intent = _FakeIntent(raw_query="q")
    tenant = _tenant(scope=["ISO27001:2022", "ISO27701:2019"])
    p = build(intent=intent, tenant_context=tenant, resolver=None)
    return _ok(
        p.tenant_id == "test-uuid"
        and p.frameworks_scope == ["ISO27001:2022", "ISO27701:2019"],
    )


def test_build_infers_framework_primary_from_cited():
    intent = _FakeIntent(cited_refs=["A.5.18", "A.5.15"])
    p = build(intent=intent, tenant_context=None, resolver=None)
    return _ok(p.framework_primary == "ISO27001:2022")


def test_build_records_reason_fallback():
    intent = _FakeIntent()
    p = build(intent=intent, tenant_context=None, resolver=None)
    return _ok(
        "no dedicated builder" in p.reason_fallback,
        f"reason={p.reason_fallback}",
    )


def test_build_records_provenance():
    intent = _FakeIntent()
    p = build(intent=intent, tenant_context=None, resolver=None)
    return _ok(p.signals_provenance == ["freeform_fallback"])


def test_build_latency_populated():
    p = build(intent=None, tenant_context=None, resolver=None)
    return _ok(p.build_latency_ms >= 0)


TESTS = [
    test_infer_gdpr_from_article_ref,
    test_infer_iso_27001_from_annex_a,
    test_infer_iso_27701_from_a_7_2_x,
    test_infer_iso_27701_from_b_prefix,
    test_infer_iso_isms_clause,
    test_infer_unknown_ref,
    test_dominant_single_framework,
    test_dominant_majority,
    test_dominant_tie_returns_none,
    test_dominant_empty_returns_none,
    test_build_empty_query_produces_payload,
    test_build_with_intent_carries_query,
    test_build_extracts_question_type_from_enum,
    test_build_extracts_subject_refs_from_cited,
    test_build_ignores_none_in_cited_refs,
    test_build_carries_tenant_scope,
    test_build_infers_framework_primary_from_cited,
    test_build_records_reason_fallback,
    test_build_records_provenance,
    test_build_latency_populated,
]


def main():
    print("─" * 70)
    print("  Ship 2.0 — freeform builder unit tests")
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
