"""Tests for chat_consensus_log helpers.

Focused on the pure-Python helpers (JSON serialisation, sanitisation).
Live psql integration is covered by the wiring layer (Ship 1.12).
"""
import sys
import json

from rag.consensus.log import (
    _signal_to_json, _sanitize_metadata, _clarification_to_json,
)
from rag.consensus.types import (
    SignalOutput, Clarification, ClarificationOption,
)


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


def test_signal_serialisation_shape():
    sig = SignalOutput(
        name          = "retrieval",
        refs          = [("A.5.18", 0.72), ("A.5.15", 0.65)],
        question_type = "posture_check",
        framework     = "ISO27001:2022",
        metadata      = {"top_score": 0.72, "n_results": 5},
    )
    js = _signal_to_json(sig)
    # Refs serialised as [[ref, weight], ...] not tuples (tuples aren't JSON)
    return _ok(
        js["name"] == "retrieval"
        and js["refs"] == [["A.5.18", 0.72], ["A.5.15", 0.65]]
        and js["question_type"] == "posture_check"
        and js["framework"] == "ISO27001:2022"
        and js["fired"] is True
        and js["metadata"]["top_score"] == 0.72,
        f"js={js}",
    )


def test_signal_serialisation_is_json_dumps_safe():
    sig = SignalOutput(
        name = "explicit_refs",
        refs = [("A.5.18", 1.0)],
        metadata = {"framework_votes": {"A.5.18": "ISO27001:2022"}},
    )
    js = _signal_to_json(sig)
    # Must survive a full round-trip
    dumped = json.dumps(js)
    parsed = json.loads(dumped)
    return _ok(
        parsed["refs"] == [["A.5.18", 1.0]],
        f"round-trip failed: {parsed}",
    )


def test_sanitize_metadata_passes_plain_types():
    md = {"a": 1, "b": "hello", "c": [1, 2, 3], "d": {"nested": True}}
    out = _sanitize_metadata(md)
    return _ok(out == md, f"out={out}")


def test_sanitize_metadata_stringifies_exotic_types():
    class _Exotic:
        def __repr__(self): return "<exotic>"
    md = {"weird": _Exotic()}
    out = _sanitize_metadata(md)
    return _ok(isinstance(out["weird"], str), f"out={out}")


def test_sanitize_metadata_truncates_long_strings():
    class _Big:
        def __repr__(self): return "X" * 500
    md = {"big": _Big()}
    out = _sanitize_metadata(md)
    return _ok(len(out["big"]) <= 200, f"len={len(out['big'])}")


def test_clarification_none_returns_none():
    return _ok(_clarification_to_json(None) is None)


def test_clarification_serialised_shape():
    c = Clarification(
        kind     = "topic_ambiguity",
        question = "Do you mean X or Y?",
        options  = [
            ClarificationOption(ref="A.5.18", title="Access rights",
                                 framework="ISO27001:2022"),
            ClarificationOption(ref="A.8.24", title="Cryptography",
                                 framework="ISO27001:2022"),
        ],
    )
    js = _clarification_to_json(c)
    return _ok(
        js["kind"] == "topic_ambiguity"
        and js["question"] == "Do you mean X or Y?"
        and len(js["options"]) == 2
        and js["options"][0]["ref"] == "A.5.18"
        and js["options"][0]["title"] == "Access rights",
        f"js={js}",
    )


def test_full_result_shape_dumpable():
    """A more integration-ish test — full ConsensusResult signals
    should always be JSON-dumpable."""
    from rag.consensus.types import ConsensusResult
    result = ConsensusResult(
        verdict            = "confident",
        refs               = ["A.5.18", "A.5.15"],
        question_type      = "posture_check",
        framework          = "ISO27001:2022",
        top_ref_confidence = 0.87,
        corroborators      = 3,
        signals = [
            SignalOutput(name="explicit_refs", refs=[("A.5.18", 1.0)]),
            SignalOutput(name="curated_lexicon", refs=[("A.5.18", 0.3)],
                         question_type="posture_check"),
            SignalOutput(name="retrieval",
                         refs=[("A.5.18", 0.72), ("A.5.15", 0.65)],
                         metadata={
                             "titles_by_ref": {"A.5.18": "Access rights"},
                             "frameworks_by_ref": {"A.5.18": "ISO27001:2022"},
                             "framework_votes": {"ISO27001:2022": 2},
                         }),
        ],
        disagreement_notes = [],
        clarification      = None,
        latency_ms         = 220,
    )
    signals_js = [_signal_to_json(s) for s in result.signals]
    # Round-trip
    dumped = json.dumps(signals_js)
    parsed = json.loads(dumped)
    return _ok(len(parsed) == 3 and parsed[0]["name"] == "explicit_refs",
               f"parsed={parsed}")


TESTS = [
    test_signal_serialisation_shape,
    test_signal_serialisation_is_json_dumps_safe,
    test_sanitize_metadata_passes_plain_types,
    test_sanitize_metadata_stringifies_exotic_types,
    test_sanitize_metadata_truncates_long_strings,
    test_clarification_none_returns_none,
    test_clarification_serialised_shape,
    test_full_result_shape_dumpable,
]


def main():
    print("─" * 70)
    print("  chat_consensus_log helpers unit tests")
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
