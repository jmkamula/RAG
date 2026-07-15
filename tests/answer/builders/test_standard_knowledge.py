"""Unit tests for rag/answer/builders/standard_knowledge.py."""
import sys
import types as _types

from rag.answer.builders.standard_knowledge import (
    build, _match_acronym, _extract_business_description,
    _ACRONYM_DEFINITIONS,
)
from rag.answer.types import StandardKnowledgePayload


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


class _FakeIntent:
    def __init__(self, question_type="definition", cited_refs=None, raw_query=""):
        self.question_type = question_type
        self.cited_refs    = cited_refs or []
        self.raw_query     = raw_query


class _FakeVectorResult:
    def __init__(self, ref="A.5.18", node_id="", title="", document=""):
        self.ref      = ref
        self.node_id  = node_id or f"ISO27001:2022:{ref}"
        self.title    = title
        self.document = document


class _FakeRetriever:
    def __init__(self, result=None):
        self._result = result
        self.calls   = 0

    def search_by_ref(self, ref):
        self.calls += 1
        if self._result and self._result.ref == ref:
            return self._result
        return None


def _tenant(scope=None):
    return _types.SimpleNamespace(
        tenant_id="test-uuid",
        tenant_name="Test",
        scope=_types.SimpleNamespace(queryable_standards=scope or ["ISO27001:2022"]),
    )


# ── _match_acronym ───────────────────────────────────────────────────

def test_match_ofi_uppercase():
    return _ok(_match_acronym("what is OFI?") == "OFI")


def test_match_ofi_lowercase():
    return _ok(_match_acronym("what does ofi mean?") == "OFI")


def test_match_nc_word_boundary():
    return _ok(_match_acronym("what does NC stand for?") == "NC")


def test_no_match_on_substring():
    # "ncr" contains "nc" but not word-bounded
    return _ok(_match_acronym("the ncr document") is None)


def test_no_match_in_random_text():
    return _ok(_match_acronym("random policy stuff") is None)


def test_first_match_wins():
    # If multiple acronyms appear, return the first
    m = _match_acronym("compare OFI and NC")
    return _ok(m in {"OFI", "NC"}, f"m={m}")


def test_all_documented_acronyms_matchable():
    """Every acronym in _ACRONYM_DEFINITIONS should be matchable."""
    missing = []
    for k in _ACRONYM_DEFINITIONS:
        if _match_acronym(f"what is {k}") != k:
            missing.append(k)
    return _ok(not missing, f"unmatched: {missing}")


# ── _extract_business_description ────────────────────────────────────

def test_extract_from_valid_chroma_doc():
    doc = (
        "ISO27001:2022 A.8.19: Installation of software on operational systems\n"
        "To ensure the integrity of operational systems and prevent "
        "exploitation of technical vulnerabilities.\n"
        "Text: additional obligation text\n"
        "Evidence: some evidence\n"
    )
    got = _extract_business_description(doc)
    return _ok(
        "ensure the integrity" in got and "Text:" not in got and "Evidence:" not in got,
        f"got={got!r}",
    )


def test_extract_empty_document():
    return _ok(_extract_business_description("") == "")


def test_extract_single_line_document():
    # Only a header, no body → empty
    return _ok(_extract_business_description("header line only") == "")


# ── build() ─────────────────────────────────────────────────────────

def test_build_acronym_only():
    intent = _FakeIntent(raw_query="what is OFI?")
    p = build(intent=intent, tenant_context=None, resolver=None)
    return _ok(
        isinstance(p, StandardKnowledgePayload)
        and p.acronym == "OFI"
        and p.expansion == "Opportunity for Improvement"
        and p.definition,
    )


def test_build_no_acronym_no_ref():
    intent = _FakeIntent(raw_query="tell me about compliance")
    p = build(intent=intent, tenant_context=None, resolver=None)
    return _ok(
        p.acronym is None and p.expansion is None
        and p.business_description == "",
    )


def test_build_with_cited_ref_infers_framework():
    intent = _FakeIntent(cited_refs=["A.5.18"], raw_query="what is A.5.18?")
    p = build(intent=intent, tenant_context=None, resolver=None)
    return _ok(
        len(p.subject_refs) == 1
        and p.subject_refs[0].ref == "A.5.18"
        and p.subject_refs[0].framework == "ISO27001:2022"
        and p.framework_primary == "ISO27001:2022",
        f"p={p}",
    )


def test_build_with_chroma_retriever_pulls_description():
    intent = _FakeIntent(cited_refs=["A.5.18"], raw_query="what is A.5.18?")
    doc = (
        "ISO27001:2022 A.5.18: Access rights\n"
        "Access to information and other associated assets shall be provisioned "
        "for authorized use consistent with a topic-specific policy on access.\n"
        "Text: obligation text\n"
    )
    retriever = _FakeRetriever(_FakeVectorResult(
        ref="A.5.18", title="Access rights", document=doc,
    ))
    p = build(intent=intent, tenant_context=None,
              resolver=None, chroma_retriever=retriever)
    return _ok(
        p.business_description
        and "Access to information" in p.business_description
        and p.subject_refs[0].title == "Access rights"
        and retriever.calls == 1,
        f"desc_len={len(p.business_description)} calls={retriever.calls}",
    )


def test_build_with_chroma_retriever_none_found():
    intent = _FakeIntent(cited_refs=["A.99.99"], raw_query="what is A.99.99?")
    retriever = _FakeRetriever(None)   # no result
    p = build(intent=intent, tenant_context=None,
              resolver=None, chroma_retriever=retriever)
    return _ok(
        p.business_description == ""
        and retriever.calls == 1,
    )


def test_build_carries_tenant_scope():
    intent = _FakeIntent(raw_query="what is ISMS?")
    tenant = _tenant(scope=["ISO27001:2022", "GDPR:2016/679"])
    p = build(intent=intent, tenant_context=tenant, resolver=None)
    return _ok(
        p.tenant_id == "test-uuid"
        and p.frameworks_scope == ["ISO27001:2022", "GDPR:2016/679"]
        and p.framework_primary == "ISO27001:2022",   # first in scope
        f"p.framework_primary={p.framework_primary}",
    )


def test_build_records_provenance():
    intent = _FakeIntent(cited_refs=["A.5.18"], raw_query="what is OFI?")
    p = build(intent=intent, tenant_context=None, resolver=None)
    return _ok(
        "acronym_definitions" in p.signals_provenance
        and "cited_refs" in p.signals_provenance,
        f"provenance={p.signals_provenance}",
    )


def test_build_question_type_is_definition():
    intent = _FakeIntent(raw_query="what is OFI?")
    p = build(intent=intent, tenant_context=None, resolver=None)
    return _ok(p.question_type == "definition")


def test_build_chroma_exception_silent_fail():
    class _RaisingRetriever:
        def search_by_ref(self, ref):
            raise RuntimeError("chroma down")
    intent = _FakeIntent(cited_refs=["A.5.18"], raw_query="what is A.5.18?")
    p = build(intent=intent, tenant_context=None,
              resolver=None, chroma_retriever=_RaisingRetriever())
    return _ok(
        p.business_description == "" and len(p.subject_refs) == 1,
        "silent-fail should still produce a payload",
    )


def test_build_latency_populated():
    p = build(intent=_FakeIntent(), tenant_context=None, resolver=None)
    return _ok(p.build_latency_ms >= 0)


TESTS = [
    test_match_ofi_uppercase,
    test_match_ofi_lowercase,
    test_match_nc_word_boundary,
    test_no_match_on_substring,
    test_no_match_in_random_text,
    test_first_match_wins,
    test_all_documented_acronyms_matchable,
    test_extract_from_valid_chroma_doc,
    test_extract_empty_document,
    test_extract_single_line_document,
    test_build_acronym_only,
    test_build_no_acronym_no_ref,
    test_build_with_cited_ref_infers_framework,
    test_build_with_chroma_retriever_pulls_description,
    test_build_with_chroma_retriever_none_found,
    test_build_carries_tenant_scope,
    test_build_records_provenance,
    test_build_question_type_is_definition,
    test_build_chroma_exception_silent_fail,
    test_build_latency_populated,
]


def main():
    print("─" * 70)
    print("  Ship 2.1 — standard_knowledge builder unit tests")
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
