"""End-to-end tests for run_consensus — the public entry point.

Uses fake retriever + minimal tenant/session mocks. Tests the full
signal dispatch order + aggregator wiring.
"""
import sys
from dataclasses import dataclass, field
from typing import Any

from rag.consensus import run_consensus
from rag.consensus.types import ConsensusConfig


CFG = ConsensusConfig()


# ── Mocks ────────────────────────────────────────────────────────────

@dataclass
class _FakeVectorResult:
    ref:         str
    score:       float
    title:       str = ""
    standard_id: str = "ISO27001:2022"


@dataclass
class _FakeContext:
    results: list = field(default_factory=list)


class _FakeRetriever:
    def __init__(self, results):
        self._results = results
        self.calls    = 0
        self.last_args = None

    def search(self, query, n=10, standards=None):
        self.calls += 1
        self.last_args = (query, n, standards)
        return _FakeContext(results=self._results)


@dataclass
class _FakeScope:
    queryable_standards: list = field(default_factory=lambda: ["ISO27001:2022"])


@dataclass
class _FakeTenant:
    scope:   Any = field(default_factory=_FakeScope)
    posture: dict = field(default_factory=dict)


@dataclass
class _FakeSession:
    active_refs: list = field(default_factory=list)
    intent_type: Any = None


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


# ── Confident path — retrieval + curated agree ───────────────────────

def test_confident_natural_language_query():
    tenant = _FakeTenant(
        scope=_FakeScope(queryable_standards=["ISO27001:2022"]),
        posture={"A.5.18": {"finding": "NC"}},
    )
    r = _FakeRetriever([
        _FakeVectorResult("A.5.18", 0.72, "Access rights"),
        _FakeVectorResult("A.5.15", 0.65, "Access control"),
    ])
    result = run_consensus(
        "what documents do we need to address the access rights NC?",
        tenant_context      = tenant,
        session_context_arg = None,
        retriever           = r,
        cfg                 = CFG,
    )
    return _ok(
        result.verdict == "confident"
        and result.refs[0] == "A.5.18"
        and result.framework == "ISO27001:2022"
        and result.question_type == "document_inventory"
        and r.calls == 1,   # retrieval WAS called
        f"result={result}",
    )


def test_early_exit_when_explicit_ref_and_curated_agree():
    # Query has explicit ref A.5.18 AND matches curated topic
    # "access rights" (which maps to A.5.18 in DOCUMENT_TOPIC_MAP).
    # Both agree → retrieval should be SKIPPED.
    tenant = _FakeTenant(posture={"A.5.18": {"finding": "NC"}})
    r = _FakeRetriever([_FakeVectorResult("A.5.99", 0.99)])   # unused if skipped
    result = run_consensus(
        "A.5.18 access rights status",
        tenant_context      = tenant,
        session_context_arg = None,
        retriever           = r,
        cfg                 = CFG,
    )
    return _ok(
        result.verdict == "confident"
        and result.refs[0] == "A.5.18"
        and r.calls == 0,   # early exit — retrieval NOT called
        f"result={result} retrieval_calls={r.calls}",
    )


def test_no_early_exit_when_explicit_but_no_curated_hit():
    # Query has explicit ref but curated_lexicon doesn't hit —
    # retrieval SHOULD run to corroborate
    tenant = _FakeTenant()
    r = _FakeRetriever([_FakeVectorResult("A.5.18", 0.72)])
    result = run_consensus(
        "A.5.18 status",  # short query — no curated pattern likely to hit
        tenant_context      = tenant,
        retriever           = r,
        cfg                 = CFG,
    )
    return _ok(
        r.calls == 1,   # retrieval fires
        f"retrieval_calls={r.calls}",
    )


# ── Ambiguous path ───────────────────────────────────────────────────

def test_ambiguous_two_families_within_tie_band():
    tenant = _FakeTenant()
    r = _FakeRetriever([
        _FakeVectorResult("A.5.18", 0.72, "Access rights"),
        _FakeVectorResult("A.8.24", 0.71, "Cryptography"),
    ])
    result = run_consensus(
        "what should we look at?",   # vague query — no explicit ref, no curated hit
        tenant_context      = tenant,
        retriever           = r,
        cfg                 = CFG,
    )
    return _ok(
        result.verdict == "ambiguous" and result.clarification is not None,
        f"verdict={result.verdict}",
    )


# ── Insufficient path ────────────────────────────────────────────────

def test_insufficient_when_retrieval_below_floor():
    tenant = _FakeTenant()
    r = _FakeRetriever([_FakeVectorResult("A.5.18", 0.10)])   # below floor
    result = run_consensus(
        "random noise",
        tenant_context = tenant,
        retriever      = r,
        cfg            = CFG,
    )
    return _ok(
        result.verdict == "insufficient" and result.llm_fallback_needed is True,
        f"verdict={result.verdict}",
    )


def test_insufficient_when_no_retriever_and_no_hits():
    tenant = _FakeTenant()
    result = run_consensus(
        "random noise",
        tenant_context = tenant,
        retriever      = None,       # no retrieval available
        cfg            = CFG,
    )
    return _ok(
        result.verdict == "insufficient",
        f"verdict={result.verdict}",
    )


# ── Session context — deictic follow-up ──────────────────────────────

def test_session_context_provides_anchor():
    tenant = _FakeTenant()
    session = _FakeSession(active_refs=["A.5.18"])
    r = _FakeRetriever([])   # retrieval empty — session should still anchor
    result = run_consensus(
        "what about it?",     # deictic
        tenant_context      = tenant,
        session_context_arg = session,
        retriever           = r,
        cfg                 = CFG,
    )
    # Session_context contributed A.5.18 at weight 0.10 — below confident_floor,
    # but above min_floor. Should be confident (borderline).
    return _ok(
        result.refs and result.refs[0] == "A.5.18",
        f"refs={result.refs}",
    )


# ── Posture boost impacts ordering ───────────────────────────────────

def test_posture_nc_boost_moves_ref_up():
    tenant = _FakeTenant(
        posture={"A.5.15": {"finding": "NC"}},   # A.5.15 boosted; A.5.18 not
    )
    r = _FakeRetriever([
        _FakeVectorResult("A.5.18", 0.55, "Access rights"),
        _FakeVectorResult("A.5.15", 0.53, "Access control"),
    ])
    result = run_consensus(
        "should we look at access?",
        tenant_context = tenant,
        retriever      = r,
        cfg            = CFG,
    )
    # A.5.15 gets +0.15 posture boost → total ~0.68; A.5.18 stays ~0.55
    return _ok(
        result.refs[0] == "A.5.15",
        f"expected A.5.15 on top after posture boost, got {result.refs}",
    )


# ── Framework passthrough ────────────────────────────────────────────

def test_standards_from_tenant_scope_passed_to_retriever():
    tenant = _FakeTenant(scope=_FakeScope(queryable_standards=["ISO27701:2019"]))
    r = _FakeRetriever([_FakeVectorResult("A.7.2.4", 0.72, "", "ISO27701:2019")])
    run_consensus("anything", tenant_context=tenant, retriever=r, cfg=CFG)
    return _ok(
        r.last_args and r.last_args[2] == ["ISO27701:2019"],
        f"standards not propagated: {r.last_args}",
    )


# ── Latency recorded ─────────────────────────────────────────────────

def test_latency_ms_populated():
    tenant = _FakeTenant()
    r = _FakeRetriever([_FakeVectorResult("A.5.18", 0.72)])
    result = run_consensus("access rights", tenant_context=tenant, retriever=r, cfg=CFG)
    return _ok(result.latency_ms >= 0, f"latency={result.latency_ms}")


# ── Signal audit trail ───────────────────────────────────────────────

def test_all_signal_slots_populated_in_result():
    tenant = _FakeTenant()
    r = _FakeRetriever([_FakeVectorResult("A.5.18", 0.72)])
    result = run_consensus("A.5.18 status", tenant_context=tenant, retriever=r, cfg=CFG)
    names = {s.name for s in result.signals}
    expected = {
        "explicit_refs", "curated_lexicon", "framework_hint",
        "session_context", "retrieval", "graph_tightness", "posture_boost",
    }
    return _ok(
        expected.issubset(names),
        f"missing signals in result: expected {expected}, got {names}",
    )


def test_early_exit_still_records_retrieval_as_skipped():
    tenant = _FakeTenant()
    r = _FakeRetriever([_FakeVectorResult("A.5.99", 0.99)])
    result = run_consensus(
        "A.5.18 access rights",   # both B and C trigger + agree
        tenant_context = tenant, retriever = r, cfg = CFG,
    )
    ret_sig = next(s for s in result.signals if s.name == "retrieval")
    return _ok(
        not ret_sig.fired
        and ret_sig.metadata.get("skipped") is True
        and ret_sig.metadata.get("reason") == "cheap_consensus_hit",
        f"retrieval signal not marked skipped: {ret_sig}",
    )


# ── Tenant context is None-safe ──────────────────────────────────────

def test_none_tenant_does_not_crash():
    r = _FakeRetriever([_FakeVectorResult("A.5.18", 0.72)])
    result = run_consensus("A.5.18", tenant_context=None, retriever=r, cfg=CFG)
    # Should complete without crash — retrieval still fires,
    # posture_boost has no data
    return _ok(result.verdict in ("confident", "ambiguous", "insufficient"),
               f"verdict={result.verdict}")


TESTS = [
    test_confident_natural_language_query,
    test_early_exit_when_explicit_ref_and_curated_agree,
    test_no_early_exit_when_explicit_but_no_curated_hit,
    test_ambiguous_two_families_within_tie_band,
    test_insufficient_when_retrieval_below_floor,
    test_insufficient_when_no_retriever_and_no_hits,
    test_session_context_provides_anchor,
    test_posture_nc_boost_moves_ref_up,
    test_standards_from_tenant_scope_passed_to_retriever,
    test_latency_ms_populated,
    test_all_signal_slots_populated_in_result,
    test_early_exit_still_records_retrieval_as_skipped,
    test_none_tenant_does_not_crash,
]


def main():
    print("─" * 70)
    print("  run_consensus end-to-end tests")
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
