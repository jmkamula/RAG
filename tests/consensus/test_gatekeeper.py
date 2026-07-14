"""Tests for the inline gatekeeper — bounded LLM arbiter.

Uses monkey-patched llm_client.call so tests are deterministic
without network access.
"""
import sys
import json

from rag.consensus.types      import SignalOutput, ConsensusResult, ConsensusConfig
from rag.consensus.gatekeeper import (
    gatekeep, gatekeeper_should_fire,
    _extract_json_object, _apply_decision,
)


CFG = ConsensusConfig()


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


def _sig(name, refs=None, question_type=None, framework=None, metadata=None, fired=True):
    return SignalOutput(
        name=name, refs=list(refs or []),
        question_type=question_type, framework=framework,
        metadata=metadata or {}, fired=fired,
    )


def _result(verdict="confident", refs=None, qt=None, fw=None, corr=2, conf=0.5):
    return ConsensusResult(
        verdict=verdict, refs=list(refs or []),
        question_type=qt, framework=fw,
        corroborators=corr, top_ref_confidence=conf,
    )


# ── Fake LLM ─────────────────────────────────────────────────────────

class _FakeResponse:
    def __init__(self, text="", ok=True, error=None, latency_ms=200):
        self.text       = text
        self.ok         = ok
        self.error      = error
        self.latency_ms = latency_ms


def _install_fake_llm(response_text: str, ok: bool = True):
    """Monkey-patch rag.llm_client.call to return a fixed response."""
    from rag import llm_client
    def _fake_call(**kwargs):
        return _FakeResponse(text=response_text, ok=ok)
    llm_client.call = _fake_call


def _uninstall_fake_llm():
    """Restore the real llm_client.call (import fresh module)."""
    import importlib
    from rag import llm_client
    importlib.reload(llm_client)


# ── Gatekeeper-should-fire logic ─────────────────────────────────────

def test_should_not_fire_when_no_signals():
    result = _result()
    signals = [_sig("retrieval", fired=False), _sig("explicit_refs", fired=False)]
    should, reason = gatekeeper_should_fire(result, signals, CFG)
    return _ok(not should and "no signals" in reason, f"reason={reason}")


def test_should_not_fire_on_hard_anchor_early_exit():
    # Simulate the run_consensus early-exit: retrieval marked skipped
    # with reason=cheap_consensus_hit, while B + C both fired.
    result = _result(verdict="confident", refs=["A.5.18"])
    signals = [
        _sig("explicit_refs",   refs=[("A.5.18", 1.0)]),
        _sig("curated_lexicon", refs=[("A.5.18", 0.3)], question_type="posture_check"),
        _sig("retrieval", fired=False,
             metadata={"skipped": True, "reason": "cheap_consensus_hit"}),
    ]
    should, reason = gatekeeper_should_fire(result, signals, CFG)
    return _ok(not should and "hard_anchor" in reason, f"reason={reason}")


def test_should_fire_when_signals_active_no_early_exit():
    result = _result(refs=["A.5.18"])
    signals = [
        _sig("retrieval", refs=[("A.5.18", 0.72)]),
        _sig("curated_lexicon", refs=[("A.5.18", 0.3)], question_type="posture_check"),
    ]
    should, reason = gatekeeper_should_fire(result, signals, CFG)
    return _ok(should, f"expected fire, reason={reason}")


# ── JSON extraction ──────────────────────────────────────────────────

def test_extract_plain_json():
    text = '{"decision":"approve","reason":"looks right"}'
    parsed = _extract_json_object(text)
    return _ok(
        parsed == {"decision": "approve", "reason": "looks right"},
        f"parsed={parsed}",
    )


def test_extract_json_with_code_fence():
    text = '```json\n{"decision":"reject","reason":"nope"}\n```'
    parsed = _extract_json_object(text)
    return _ok(
        parsed and parsed["decision"] == "reject",
        f"parsed={parsed}",
    )


def test_extract_json_with_leading_prose():
    text = 'Here is my answer:\n{"decision":"approve","reason":"ok"}'
    parsed = _extract_json_object(text)
    return _ok(parsed and parsed["decision"] == "approve", f"parsed={parsed}")


def test_extract_invalid_json_returns_none():
    return _ok(_extract_json_object("not json at all") is None)


def test_extract_empty_returns_none():
    return _ok(_extract_json_object("") is None)


# ── _apply_decision ──────────────────────────────────────────────────

def test_apply_approve_preserves_verdict():
    result = _result(verdict="confident", refs=["A.5.18"])
    updated = _apply_decision(result, {"decision": "approve", "reason": "ok"})
    return _ok(
        updated.verdict == "confident"
        and updated.refs == ["A.5.18"]
        and any("gatekeeper: approve" in n for n in updated.disagreement_notes),
        f"updated={updated}",
    )


def test_apply_reject_flips_to_insufficient():
    result = _result(verdict="confident", refs=["A.5.18"])
    updated = _apply_decision(result, {"decision": "reject", "reason": "nonsense"})
    return _ok(
        updated.verdict == "insufficient"
        and updated.llm_fallback_needed is True,
        f"verdict={updated.verdict}",
    )


def test_apply_modify_changes_question_type():
    result = _result(refs=["A.5.18"], qt="posture_check")
    updated = _apply_decision(
        result,
        {"decision": "modify", "question_type": "definition", "reason": "concept query"},
    )
    return _ok(updated.question_type == "definition", f"qt={updated.question_type}")


def test_apply_modify_changes_refs():
    result = _result(refs=["A.5.18"], qt="posture_check")
    updated = _apply_decision(
        result,
        {"decision": "modify", "refs": ["A.5.15", "A.5.18"], "reason": "reorder"},
    )
    return _ok(updated.refs == ["A.5.15", "A.5.18"], f"refs={updated.refs}")


def test_apply_modify_changes_framework():
    result = _result(refs=["A.5.18"], fw="ISO27001:2022")
    updated = _apply_decision(
        result,
        {"decision": "modify", "framework": "GDPR:2016/679", "reason": "user said GDPR"},
    )
    return _ok(updated.framework == "GDPR:2016/679", f"fw={updated.framework}")


def test_apply_modify_null_fields_keep_tentative():
    result = _result(refs=["A.5.18"], qt="posture_check", fw="ISO27001:2022")
    updated = _apply_decision(
        result,
        {"decision": "modify", "question_type": None, "refs": None, "framework": None,
         "reason": "no change needed"},
    )
    return _ok(
        updated.question_type == "posture_check"
        and updated.refs == ["A.5.18"]
        and updated.framework == "ISO27001:2022",
        f"updated={updated}",
    )


def test_apply_modify_rejects_invalid_question_type():
    result = _result(refs=["A.5.18"], qt="posture_check")
    updated = _apply_decision(
        result,
        {"decision": "modify", "question_type": "invented_type", "reason": "n/a"},
    )
    # Invalid qt should be dropped — tentative preserved
    return _ok(updated.question_type == "posture_check", f"qt={updated.question_type}")


def test_apply_modify_rejects_non_list_refs():
    result = _result(refs=["A.5.18"])
    updated = _apply_decision(
        result,
        {"decision": "modify", "refs": "A.5.15", "reason": "n/a"},   # string not list
    )
    return _ok(updated.refs == ["A.5.18"], f"refs={updated.refs}")


# ── Full gatekeep() with fake LLM ────────────────────────────────────

def test_gatekeep_approves_on_llm_approve():
    _install_fake_llm('{"decision":"approve","reason":"looks right"}')
    try:
        result = _result(refs=["A.5.18"], qt="posture_check")
        signals = [
            _sig("retrieval", refs=[("A.5.18", 0.72)]),
            _sig("curated_lexicon", refs=[("A.5.18", 0.3)], question_type="posture_check"),
        ]
        out = gatekeep("is A.5.18 compliant?", result, signals, CFG)
        return _ok(
            out.verdict == "confident"
            and any("gatekeeper: approve" in n for n in out.disagreement_notes),
            f"out={out}",
        )
    finally:
        _uninstall_fake_llm()


def test_gatekeep_rejects_flips_to_insufficient():
    _install_fake_llm('{"decision":"reject","reason":"nonsense query"}')
    try:
        result = _result(refs=["X.99.99"], qt="unknown")
        signals = [_sig("retrieval", refs=[("X.99.99", 0.15)])]
        out = gatekeep("asdfghjkl", result, signals, CFG)
        return _ok(
            out.verdict == "insufficient"
            and out.llm_fallback_needed is True,
            f"out={out}",
        )
    finally:
        _uninstall_fake_llm()


def test_gatekeep_modify_changes_question_type():
    _install_fake_llm(
        '{"decision":"modify","question_type":"definition",'
        '"refs":[],"reason":"definitional query"}'
    )
    try:
        result = _result(refs=["A.5.10"], qt="posture_check")
        signals = [_sig("retrieval", refs=[("A.5.10", 0.30)])]
        out = gatekeep("what is OFI?", result, signals, CFG)
        return _ok(
            out.question_type == "definition" and out.refs == [],
            f"qt={out.question_type} refs={out.refs}",
        )
    finally:
        _uninstall_fake_llm()


def test_gatekeep_returns_tentative_on_llm_failure():
    _install_fake_llm("", ok=False)
    try:
        result = _result(refs=["A.5.18"], qt="posture_check")
        signals = [_sig("retrieval", refs=[("A.5.18", 0.72)])]
        out = gatekeep("query", result, signals, CFG)
        # Tentative unchanged
        return _ok(
            out.verdict == "confident" and out.question_type == "posture_check",
            f"out={out}",
        )
    finally:
        _uninstall_fake_llm()


def test_gatekeep_returns_tentative_on_malformed_json():
    _install_fake_llm("garbage response no json here")
    try:
        result = _result(refs=["A.5.18"], qt="posture_check")
        signals = [_sig("retrieval", refs=[("A.5.18", 0.72)])]
        out = gatekeep("query", result, signals, CFG)
        return _ok(out.verdict == "confident", f"out={out}")
    finally:
        _uninstall_fake_llm()


def test_gatekeep_skips_on_hard_anchor_early_exit():
    # Should NOT invoke the LLM at all for hard-anchor cases
    invoked = {"count": 0}
    from rag import llm_client
    original = llm_client.call
    def _tracking_call(**kwargs):
        invoked["count"] += 1
        return _FakeResponse(text='{"decision":"approve","reason":"x"}')
    llm_client.call = _tracking_call
    try:
        result = _result(verdict="confident", refs=["A.5.18"])
        signals = [
            _sig("explicit_refs",   refs=[("A.5.18", 1.0)]),
            _sig("curated_lexicon", refs=[("A.5.18", 0.3)], question_type="posture_check"),
            _sig("retrieval", fired=False,
                 metadata={"skipped": True, "reason": "cheap_consensus_hit"}),
        ]
        out = gatekeep("A.5.18 access rights", result, signals, CFG)
        return _ok(
            invoked["count"] == 0 and out.verdict == "confident",
            f"invoked={invoked['count']}",
        )
    finally:
        llm_client.call = original


TESTS = [
    test_should_not_fire_when_no_signals,
    test_should_not_fire_on_hard_anchor_early_exit,
    test_should_fire_when_signals_active_no_early_exit,
    test_extract_plain_json,
    test_extract_json_with_code_fence,
    test_extract_json_with_leading_prose,
    test_extract_invalid_json_returns_none,
    test_extract_empty_returns_none,
    test_apply_approve_preserves_verdict,
    test_apply_reject_flips_to_insufficient,
    test_apply_modify_changes_question_type,
    test_apply_modify_changes_refs,
    test_apply_modify_changes_framework,
    test_apply_modify_null_fields_keep_tentative,
    test_apply_modify_rejects_invalid_question_type,
    test_apply_modify_rejects_non_list_refs,
    test_gatekeep_approves_on_llm_approve,
    test_gatekeep_rejects_flips_to_insufficient,
    test_gatekeep_modify_changes_question_type,
    test_gatekeep_returns_tentative_on_llm_failure,
    test_gatekeep_returns_tentative_on_malformed_json,
    test_gatekeep_skips_on_hard_anchor_early_exit,
]


def main():
    print("─" * 70)
    print("  Ship 1.5 gatekeeper unit tests")
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
