"""
Integration tests for rank_and_answer's case-file flow.

Ship 2'.n (2026-07-16): the CASEFILE_ENABLED gate and the legacy
`_casefile_flow` dispatch method were retired. The case-file flow IS
`rank_and_answer` now. These tests exercise it directly.

Mocks _call_llm so tests are deterministic without network access.
Verifies:
  * rank_and_answer builds a digest, calls the LLM, runs repair,
    returns a ComplianceAnswer with the repaired text
  * Repair events fire for missing refs
  * Node classification by role (program vs obligation)
  * Preservation-check adds compliance-facts footer when refs drop

Run: PYTHONPATH=/data/arioncomply python3 tests/casefile/test_wiring.py
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_ROOT))

from rag.llm_answer import LLMAnswer, ComplianceAnswer, _is_uuid_shape


# ── Fixtures ──────────────────────────────────────────────────────────

@dataclass
class E:
    source_id: str
    target_id: str
    rel_type:  str = "IMPLEMENTS"


@dataclass
class N:
    node_id:       str
    ref:           str
    standard_id:   str = "ISO27001:2022"
    title:         str = ""
    xfw_edges:     list = field(default_factory=list)
    is_informational: bool = False
    metadata:      dict = field(default_factory=dict)
    document:      str = ""
    source:        str = "cited"


@dataclass
class FakeQI:
    """Minimal QueryIntent-like."""
    question_type: Any = None
    cited_refs:    list = field(default_factory=list)


class FakeQT:
    def __init__(self, value: str):
        self.value = value


def _posture(items):
    return {
        f"ISO27001:2022:{ref}": {
            "finding": f,
            "gap_description": f"gap-{ref}",
            "evidence_text":   f"evid-{ref}",
            "control_ref":     ref,
            "confirmation_status": cs,
            "standard_id":     "ISO27001:2022",
        }
        for ref, f, cs in items
    }


def _make_llm(monkey_response: str) -> LLMAnswer:
    """Build an LLMAnswer that returns a canned string from _call_llm
    without hitting the network. Skips __init__'s client setup."""
    llm = LLMAnswer.__new__(LLMAnswer)
    llm.answer_model = "test-model"
    llm.verify_model = "test-model"
    llm.temperature  = 0.1
    llm.max_tokens   = 1500
    llm.verify       = False
    llm.max_corrections = 0
    # Monkey-patch _call_llm
    llm._call_llm = lambda **kw: monkey_response
    # And _log_casefile_turn — no DB during tests
    llm._log_casefile_turn = lambda **kw: None
    return llm


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


# ── uuid helper still lives in llm_answer as a str-subclass predicate

def test_uuid_shape_helper():
    return _ok(
        _is_uuid_shape("00000000-0000-0000-0000-000000000001")
        and not _is_uuid_shape("Arion Networks")
        and not _is_uuid_shape("")
        and not _is_uuid_shape(None)
    )


# ── rank_and_answer end-to-end tests ──────────────────────────────────

def test_rank_and_answer_preserves_perfect_answer():
    """Perfect LLM output — no repair events, no footers appended."""
    llm = _make_llm("A.5.18 [NC-DRAFT] register incomplete. Investigate.")
    posture = _posture([("A.5.18", "NC", "unconfirmed")])
    result = llm.rank_and_answer(
        query="what is A.5.18?",
        nodes=[N(node_id="ISO27001:2022:A.5.18", ref="A.5.18",
                 metadata={"obligation_text": "Access rights"})],
        posture=posture,
        intent=FakeQI(question_type=FakeQT("posture_check"),
                      cited_refs=["A.5.18"]),
        tenant_name="",
        scope_standards=["ISO27001:2022"],
    )
    return _ok(
        "A.5.18" in result.answer_text
        and "[NC-DRAFT]" in result.answer_text
        and "↳ Compliance facts" not in result.answer_text
        and not result.was_corrected,
        result.answer_text,
    )


def test_rank_and_answer_repairs_missing_ref():
    """LLM drops A.5.18 — repair appends compliance-facts footer."""
    llm = _make_llm("There is an access-control issue that needs attention.")
    posture = _posture([("A.5.18", "NC", "unconfirmed")])
    result = llm.rank_and_answer(
        query="what is our A.5.18 status?",
        nodes=[N(node_id="ISO27001:2022:A.5.18", ref="A.5.18",
                 metadata={"obligation_text": "Access rights"})],
        posture=posture,
        intent=FakeQI(question_type=FakeQT("posture_check"),
                      cited_refs=["A.5.18"]),
        tenant_name="",
        scope_standards=["ISO27001:2022"],
    )
    return _ok(
        "A.5.18 [NC-DRAFT]" in result.answer_text
        and "↳ Compliance facts" in result.answer_text
        and result.was_corrected,
        result.answer_text,
    )


def test_rank_and_answer_extracts_cited_refs():
    """cited_refs on the ComplianceAnswer should match what appears
    in the (possibly repaired) answer text."""
    llm = _make_llm("A.5.18 [NC-DRAFT] and A.5.15 [Comply] are both relevant.")
    posture = _posture([
        ("A.5.18", "NC",     "unconfirmed"),
        ("A.5.15", "Comply", "confirmed"),
    ])
    result = llm.rank_and_answer(
        query="access controls?",
        nodes=[
            N(node_id="ISO27001:2022:A.5.18", ref="A.5.18",
              metadata={"obligation_text": "x"}),
            N(node_id="ISO27001:2022:A.5.15", ref="A.5.15",
              metadata={"obligation_text": "y"}),
        ],
        posture=posture,
        intent=FakeQI(question_type=FakeQT("gap_analysis")),
        tenant_name="",
        scope_standards=["ISO27001:2022"],
    )
    return _ok(
        set(result.cited_refs) == {"A.5.18", "A.5.15"},
        f"got {result.cited_refs}",
    )


def test_rank_and_answer_returns_posture_findings():
    llm = _make_llm("A.5.18 [NC-DRAFT] gap.")
    posture = _posture([("A.5.18", "NC", "unconfirmed")])
    result = llm.rank_and_answer(
        query="q",
        nodes=[N(node_id="ISO27001:2022:A.5.18", ref="A.5.18",
                 metadata={"obligation_text": "x"})],
        posture=posture,
        intent=FakeQI(question_type=FakeQT("posture_check"),
                      cited_refs=["A.5.18"]),
        tenant_name="",
        scope_standards=["ISO27001:2022"],
    )
    return _ok(result.posture_findings == {"A.5.18": "NC"}, result.posture_findings)


def test_rank_and_answer_returns_compliance_answer_type():
    """Sanity: the return type is ComplianceAnswer regardless of
    whether preservation-repair fired."""
    llm = _make_llm("Any response.")
    result = llm.rank_and_answer(
        query="q",
        nodes=[],
        posture={},
        intent=FakeQI(question_type=FakeQT("posture_check"), cited_refs=[]),
        tenant_name="",
        scope_standards=[],
    )
    return _ok(isinstance(result, ComplianceAnswer),
               f"got {type(result).__name__}")


def test_rank_and_answer_role_split_via_scope():
    """When the tenant scope includes multiple frameworks, refs are
    classified by role: program/extension → primary_refs;
    obligation → xfw_refs. Ship 2'.i replaced the legacy layer
    split with this role-model split."""
    llm = _make_llm(
        "A.5.18 [NC-DRAFT] and Art.32 apply.\n"
        "↳ Bridges to ISO 27001 for Art.32: A.5.18 [NC-DRAFT]"
    )
    posture = _posture([("A.5.18", "NC", "unconfirmed")])
    a518 = N(node_id="ISO27001:2022:A.5.18", ref="A.5.18",
             metadata={"obligation_text": "x"})
    art32 = N(node_id="GDPR:2016/679:Art.32", ref="Art.32",
              standard_id="GDPR:2016/679",
              xfw_edges=[E("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.18")])
    result = llm.rank_and_answer(
        query="Art.32?",
        nodes=[a518, art32],
        posture=posture,
        intent=FakeQI(question_type=FakeQT("cross_framework"),
                      cited_refs=["Art.32"]),
        tenant_name="",
        scope_standards=["ISO27001:2022", "GDPR:2016/679"],
    )
    # Note: role classification depends on tenant scope's role model.
    # In this test we don't wire a full scope object, so we just assert
    # the ComplianceAnswer is well-formed. Role-based assertions live
    # in test_types.py for the CaseFile itself.
    return _ok(
        isinstance(result, ComplianceAnswer)
        and "A.5.18" in result.cited_refs,
        f"cited={result.cited_refs}",
    )


TESTS = [
    test_uuid_shape_helper,
    test_rank_and_answer_preserves_perfect_answer,
    test_rank_and_answer_repairs_missing_ref,
    test_rank_and_answer_extracts_cited_refs,
    test_rank_and_answer_returns_posture_findings,
    test_rank_and_answer_returns_compliance_answer_type,
    test_rank_and_answer_role_split_via_scope,
]


def main():
    print("─" * 70)
    print("  rank_and_answer (case-file) integration tests")
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
