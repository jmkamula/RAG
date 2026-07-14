"""Tests for Signal G — session_context."""
import sys
from dataclasses import dataclass, field
from typing import Optional, Any
from rag.consensus.signals.session_context import session_context
from rag.consensus.types import ConsensusConfig


CFG = ConsensusConfig()


# Minimal mock — duck-typed for the signal's needs.
@dataclass
class _MockSession:
    active_refs: list = field(default_factory=list)
    intent_type: Any = None


class _FakeQuestionType:
    """Mimics classifier.QuestionType enum interface."""
    def __init__(self, value: str):
        self.value = value


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


def test_none_session_does_not_fire():
    return _ok(not session_context(None, CFG).fired)


def test_empty_active_refs_does_not_fire():
    out = session_context(_MockSession(active_refs=[]), CFG)
    return _ok(not out.fired)


def test_single_active_ref_fires_with_boost_weight():
    out = session_context(_MockSession(active_refs=["A.5.18"]), CFG)
    if not out.fired:
        return _ok(False, "expected fire")
    if out.refs != [("A.5.18", CFG.session_boost_weight)]:
        return _ok(False, f"refs={out.refs}")
    return _ok(True)


def test_multiple_active_refs_all_weighted():
    session = _MockSession(active_refs=["A.5.18", "A.5.15", "Art.32"])
    out = session_context(session, CFG)
    if len(out.refs) != 3:
        return _ok(False, f"expected 3 refs, got {out.refs}")
    weights = {w for _, w in out.refs}
    return _ok(weights == {CFG.session_boost_weight})


def test_framework_inferred_from_first_active_ref():
    out = session_context(_MockSession(active_refs=["Art.32"]), CFG)
    return _ok(out.framework == "GDPR:2016/679", f"framework={out.framework}")


def test_framework_inferred_iso_from_annex_a():
    out = session_context(_MockSession(active_refs=["A.5.18"]), CFG)
    return _ok(out.framework == "ISO27001:2022")


def test_intent_type_carried_over():
    session = _MockSession(
        active_refs=["A.5.18"],
        intent_type=_FakeQuestionType("posture_check"),
    )
    out = session_context(session, CFG)
    return _ok(out.question_type == "posture_check", f"qt={out.question_type}")


def test_intent_type_unknown_not_carried():
    session = _MockSession(
        active_refs=["A.5.18"],
        intent_type=_FakeQuestionType("unknown"),
    )
    out = session_context(session, CFG)
    return _ok(out.question_type is None, f"qt={out.question_type} should be None")


def test_intent_type_none_ok():
    # A session with active_refs but no prior intent_type — still fires,
    # just doesn't carry a question_type
    session = _MockSession(active_refs=["A.5.18"], intent_type=None)
    out = session_context(session, CFG)
    return _ok(out.fired and out.question_type is None)


def test_intent_type_string_value_works():
    # Sometimes intent_type is stored as raw string (not enum) — the
    # signal should handle both
    session = _MockSession(active_refs=["A.5.18"], intent_type="gap_analysis")
    out = session_context(session, CFG)
    return _ok(out.question_type == "gap_analysis", f"qt={out.question_type}")


def test_metadata_records_carried_qt():
    session = _MockSession(
        active_refs=["A.5.18", "A.5.15"],
        intent_type=_FakeQuestionType("document_content"),
    )
    out = session_context(session, CFG)
    return _ok(
        out.metadata["carried_question_type"] == "document_content"
        and out.metadata["active_refs_count"] == 2
        and out.metadata["top_active_ref"] == "A.5.18",
        f"metadata={out.metadata}",
    )


def test_config_weight_override_applied():
    cfg = ConsensusConfig(session_boost_weight=0.42)
    out = session_context(_MockSession(active_refs=["A.5.18"]), cfg)
    return _ok(out.refs == [("A.5.18", 0.42)], f"refs={out.refs}")


def test_no_active_refs_attribute_gracefully_skips():
    # Test resilience — an object without active_refs attribute
    class _NoRefs:
        pass
    out = session_context(_NoRefs(), CFG)
    return _ok(not out.fired)


TESTS = [
    test_none_session_does_not_fire,
    test_empty_active_refs_does_not_fire,
    test_single_active_ref_fires_with_boost_weight,
    test_multiple_active_refs_all_weighted,
    test_framework_inferred_from_first_active_ref,
    test_framework_inferred_iso_from_annex_a,
    test_intent_type_carried_over,
    test_intent_type_unknown_not_carried,
    test_intent_type_none_ok,
    test_intent_type_string_value_works,
    test_metadata_records_carried_qt,
    test_config_weight_override_applied,
    test_no_active_refs_attribute_gracefully_skips,
]


def main():
    print("─" * 70)
    print("  Signal G — session_context unit tests")
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
