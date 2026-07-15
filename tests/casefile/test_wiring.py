"""
Integration tests for the Ship 2'.f wiring — rank_and_answer's
_casefile_flow path.

Mocks _call_llm so tests are deterministic without network access.
Verifies:
  * CASEFILE_ENABLED=1 dispatches to _casefile_flow
  * CASEFILE_ENABLED=0 (default) keeps legacy path
  * _casefile_flow builds a digest, calls the LLM, runs repair,
    returns a ComplianceAnswer with the repaired text
  * Repair events fire for missing refs
  * Feature-flag failure falls back to legacy path

Run: PYTHONPATH=/data/arioncomply python3 tests/casefile/test_wiring.py
"""
from __future__ import annotations

import os
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


# ── Env-flag tests ────────────────────────────────────────────────────

def test_uuid_shape_helper():
    return _ok(
        _is_uuid_shape("00000000-0000-0000-0000-000000000001")
        and not _is_uuid_shape("Arion Networks")
        and not _is_uuid_shape("")
        and not _is_uuid_shape(None)
    )


def test_flag_default_off_no_casefile_call():
    """With CASEFILE_ENABLED unset, rank_and_answer should NOT
    invoke _casefile_flow."""
    prev = os.environ.pop("CASEFILE_ENABLED", None)
    try:
        called = {"n": 0}

        llm = _make_llm("SELECTED_PRIMARY: 1\nSELECTED_XFW:\nA.5.18 [NC-DRAFT] gap.")
        orig_flow = llm._casefile_flow
        def _track(**kw):
            called["n"] += 1
            return orig_flow(**kw)
        llm._casefile_flow = _track

        # Legacy rank_and_answer needs many things; smoke via CASEFILE_ENABLED='0'
        # only verifies the dispatch check, not full legacy behaviour.
        # We use a try/except so if the legacy path errors on our fake
        # data, we still report the dispatch didn't happen.
        try:
            llm.rank_and_answer(
                query="q",
                nodes=[],
                posture={},
                intent=FakeQI(question_type=FakeQT("posture_check"), cited_refs=[]),
                tenant_name="",
                standards="ISO 27001",
            )
        except Exception:
            pass
        return _ok(called["n"] == 0, f"casefile_flow called {called['n']}× with flag off")
    finally:
        if prev is not None:
            os.environ["CASEFILE_ENABLED"] = prev


def test_flag_on_dispatches_to_casefile_flow():
    prev = os.environ.get("CASEFILE_ENABLED")
    os.environ["CASEFILE_ENABLED"] = "1"
    try:
        called = {"n": 0}

        # LLM response mimics a good answer for a NC finding
        response = "A.5.18 [NC-DRAFT] register is incomplete. Investigate access rights."
        llm = _make_llm(response)
        orig_flow = llm._casefile_flow
        def _track(**kw):
            called["n"] += 1
            return orig_flow(**kw)
        llm._casefile_flow = _track

        posture = _posture([("A.5.18", "NC", "unconfirmed")])
        node = N(node_id="ISO27001:2022:A.5.18", ref="A.5.18",
                 metadata={"obligation_text": "Access rights"})

        result = llm.rank_and_answer(
            query="what is our A.5.18 status?",
            nodes=[node],
            posture=posture,
            intent=FakeQI(question_type=FakeQT("posture_check"),
                          cited_refs=["A.5.18"]),
            tenant_name="",
            standards="ISO 27001",
            scope_standards=["ISO27001:2022"],
        )
        return _ok(
            called["n"] == 1 and isinstance(result, ComplianceAnswer),
            f"called={called['n']} type={type(result).__name__}",
        )
    finally:
        if prev is None:
            del os.environ["CASEFILE_ENABLED"]
        else:
            os.environ["CASEFILE_ENABLED"] = prev


# ── _casefile_flow direct tests ───────────────────────────────────────

def test_casefile_flow_preserves_perfect_answer():
    """Perfect LLM output — no repair events, no footers appended."""
    llm = _make_llm("A.5.18 [NC-DRAFT] register incomplete. Investigate.")
    posture = _posture([("A.5.18", "NC", "unconfirmed")])
    result = llm._casefile_flow(
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


def test_casefile_flow_repairs_missing_ref():
    """LLM drops A.5.18 — repair appends compliance-facts footer."""
    llm = _make_llm("There is an access-control issue that needs attention.")
    posture = _posture([("A.5.18", "NC", "unconfirmed")])
    result = llm._casefile_flow(
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


def test_casefile_flow_extracts_cited_refs():
    """cited_refs on the ComplianceAnswer should match what appears
    in the (possibly repaired) answer text."""
    llm = _make_llm("A.5.18 [NC-DRAFT] and A.5.15 [Comply] are both relevant.")
    posture = _posture([
        ("A.5.18", "NC",     "unconfirmed"),
        ("A.5.15", "Comply", "confirmed"),
    ])
    result = llm._casefile_flow(
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


def test_casefile_flow_returns_posture_findings():
    llm = _make_llm("A.5.18 [NC-DRAFT] gap.")
    posture = _posture([("A.5.18", "NC", "unconfirmed")])
    result = llm._casefile_flow(
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


def test_casefile_flow_splits_layers():
    """xfw nodes (with xfw_edges) should appear in xfw_refs, not primary."""
    llm = _make_llm("A.5.18 [NC-DRAFT] and Art.32 bridge.\n"
                    "↳ Bridges to ISO 27001 for Art.32: A.5.18 [NC-DRAFT]")
    posture = _posture([("A.5.18", "NC", "unconfirmed")])
    a518 = N(node_id="ISO27001:2022:A.5.18", ref="A.5.18",
             metadata={"obligation_text": "x"})
    art32 = N(node_id="GDPR:2016/679:Art.32", ref="Art.32",
              standard_id="GDPR:2016/679",
              xfw_edges=[E("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.18")])
    result = llm._casefile_flow(
        query="Art.32?",
        nodes=[a518, art32],
        posture=posture,
        intent=FakeQI(question_type=FakeQT("cross_framework"),
                      cited_refs=["Art.32"]),
        tenant_name="",
        scope_standards=["ISO27001:2022", "GDPR:2016/679"],
    )
    return _ok(
        "A.5.18" in result.primary_refs
        and "Art.32" in result.xfw_refs
        and "A.5.18" not in result.xfw_refs,
        f"prim={result.primary_refs} xfw={result.xfw_refs}",
    )


def test_casefile_flow_fallback_on_exception():
    """If _casefile_flow raises, rank_and_answer must fall back to
    the legacy path, not surface the exception to the caller."""
    prev = os.environ.get("CASEFILE_ENABLED")
    os.environ["CASEFILE_ENABLED"] = "1"
    try:
        llm = _make_llm("legacy answer path was taken")
        # Force _casefile_flow to blow up
        def _boom(**kw):
            raise RuntimeError("simulated flow crash")
        llm._casefile_flow = _boom

        # Legacy path needs valid inputs; use minimal fixture.
        # We only care that it DOESN'T raise.
        try:
            result = llm.rank_and_answer(
                query="q", nodes=[],
                posture={},
                intent=FakeQI(question_type=FakeQT("posture_check")),
                tenant_name="", standards="ISO 27001",
            )
            return _ok(True, "no exception surfaced")
        except Exception as e:
            # Legacy path may itself fail on empty inputs — that's a
            # separate issue. We only assert the case-file exception
            # was swallowed by the fallback.
            msg = str(e)
            return _ok(
                "simulated flow crash" not in msg,
                f"case-file exception leaked through: {msg}",
            )
    finally:
        if prev is None:
            del os.environ["CASEFILE_ENABLED"]
        else:
            os.environ["CASEFILE_ENABLED"] = prev


TESTS = [
    test_uuid_shape_helper,
    test_flag_default_off_no_casefile_call,
    test_flag_on_dispatches_to_casefile_flow,
    test_casefile_flow_preserves_perfect_answer,
    test_casefile_flow_repairs_missing_ref,
    test_casefile_flow_extracts_cited_refs,
    test_casefile_flow_returns_posture_findings,
    test_casefile_flow_splits_layers,
    test_casefile_flow_fallback_on_exception,
]


def main():
    print("─" * 70)
    print("  rank_and_answer casefile wiring tests")
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
