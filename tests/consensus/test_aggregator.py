"""Aggregator integration tests.

Constructs SignalOutputs directly and verifies the aggregator's
verdict / refs / question_type / framework / clarification.
"""
import sys
from rag.consensus.aggregator import aggregate
from rag.consensus.types import SignalOutput, ConsensusConfig


CFG = ConsensusConfig()


def _sig(name, refs=None, question_type=None, framework=None, metadata=None, fired=True):
    return SignalOutput(
        name          = name,
        refs          = list(refs or []),
        question_type = question_type,
        framework     = framework,
        metadata      = metadata or {},
        fired         = fired,
    )


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


# ── Empty / no-fire cases ────────────────────────────────────────────

def test_empty_signals_returns_insufficient():
    r = aggregate([], CFG)
    return _ok(
        r.verdict == "insufficient" and r.llm_fallback_needed is True,
        f"verdict={r.verdict}",
    )


def test_all_signals_not_fired_returns_insufficient():
    signals = [
        _sig("retrieval",       fired=False),
        _sig("explicit_refs",   fired=False),
        _sig("curated_lexicon", fired=False),
    ]
    r = aggregate(signals, CFG)
    return _ok(r.verdict == "insufficient")


def test_only_framework_hint_returns_insufficient():
    # F fires but doesn't emit refs — no ref to be confident about
    signals = [
        _sig("framework_hint", framework="ISO27001:2022"),
    ]
    r = aggregate(signals, CFG)
    return _ok(
        r.verdict == "insufficient" and r.framework == "ISO27001:2022",
        f"verdict={r.verdict} framework={r.framework}",
    )


# ── Confident verdict cases ──────────────────────────────────────────

def test_high_retrieval_score_plus_curated_confident():
    signals = [
        _sig("retrieval",       refs=[("A.5.18", 0.72), ("A.5.15", 0.65)],
                                framework="ISO27001:2022",
                                metadata={"titles_by_ref": {"A.5.18": "Access rights", "A.5.15": "Access control"}}),
        _sig("curated_lexicon", refs=[("A.5.18", 0.30)],
                                question_type="document_inventory"),
    ]
    r = aggregate(signals, CFG)
    return _ok(
        r.verdict == "confident"
        and r.refs[0] == "A.5.18"
        and r.corroborators >= 2
        and r.question_type == "document_inventory"
        and r.framework == "ISO27001:2022",
        f"result={r}",
    )


def test_explicit_ref_alone_still_confident():
    # Hard anchor: B alone with weight 1.0 clears the floor
    signals = [
        _sig("explicit_refs", refs=[("A.5.18", 1.00)], framework="ISO27001:2022"),
    ]
    r = aggregate(signals, CFG)
    # 1 corroborator but score way above floor — borderline confident
    return _ok(
        r.verdict == "confident"
        and r.refs[0] == "A.5.18"
        and r.framework == "ISO27001:2022",
        f"result={r}",
    )


def test_five_signals_agree_high_confidence():
    signals = [
        _sig("retrieval",       refs=[("A.5.18", 0.72)], framework="ISO27001:2022"),
        _sig("explicit_refs",   refs=[("A.5.18", 1.00)], framework="ISO27001:2022"),
        _sig("curated_lexicon", refs=[("A.5.18", 0.30)], question_type="posture_check"),
        _sig("session_context", refs=[("A.5.18", 0.10)]),
        _sig("posture_boost",   refs=[("A.5.18", 0.15)]),
        _sig("graph_tightness", refs=[("A.5.18", 0.05)]),
    ]
    r = aggregate(signals, CFG)
    return _ok(
        r.verdict == "confident" and r.corroborators == 6,
        f"corroborators={r.corroborators} verdict={r.verdict}",
    )


# ── Ambiguity cases ──────────────────────────────────────────────────

def test_two_families_within_tie_band_returns_ambiguous():
    # A.5.18 and A.8.24 tied and in different families
    signals = [
        _sig("retrieval",
             refs=[("A.5.18", 0.72), ("A.8.24", 0.71)],
             framework="ISO27001:2022",
             metadata={"titles_by_ref": {"A.5.18": "Access rights", "A.8.24": "Cryptography"}}),
    ]
    r = aggregate(signals, CFG)
    return _ok(
        r.verdict == "ambiguous"
        and r.clarification is not None
        and r.clarification.kind == "topic_ambiguity"
        and len(r.clarification.options) == 2,
        f"result={r}",
    )


def test_ambiguous_clarification_question_lists_titles():
    signals = [
        _sig("retrieval",
             refs=[("A.5.18", 0.72), ("A.8.24", 0.71)],
             metadata={"titles_by_ref": {"A.5.18": "Access rights", "A.8.24": "Cryptography"}}),
    ]
    r = aggregate(signals, CFG)
    q = r.clarification.question
    return _ok(
        "Access rights" in q and "Cryptography" in q,
        f"question={q!r}",
    )


def test_tied_refs_same_family_not_ambiguous():
    # A.5.15 and A.5.18 tied but both in A.5 family → not ambiguous
    signals = [
        _sig("retrieval",
             refs=[("A.5.18", 0.72), ("A.5.15", 0.71)],
             framework="ISO27001:2022"),
    ]
    r = aggregate(signals, CFG)
    return _ok(
        r.verdict == "confident",
        f"verdict={r.verdict} clarification={r.clarification}",
    )


def test_scores_outside_tie_band_not_ambiguous():
    # Big gap → confident on the top even if second is different family
    signals = [
        _sig("retrieval",
             refs=[("A.5.18", 0.72), ("A.8.24", 0.55)],   # gap > 0.05
             framework="ISO27001:2022"),
    ]
    r = aggregate(signals, CFG)
    return _ok(r.verdict == "confident", f"verdict={r.verdict}")


# ── Insufficient cases ───────────────────────────────────────────────

def test_below_min_floor_returns_insufficient():
    signals = [
        _sig("retrieval", refs=[("A.5.18", 0.15)], framework="ISO27001:2022"),
    ]
    r = aggregate(signals, CFG)
    return _ok(
        r.verdict == "insufficient" and r.llm_fallback_needed is True,
        f"verdict={r.verdict}",
    )


def test_borderline_between_floor_and_confident_is_confident():
    # Score above min_floor (0.20) but below confident_floor (0.35)
    signals = [
        _sig("retrieval", refs=[("A.5.18", 0.28)], framework="ISO27001:2022"),
    ]
    r = aggregate(signals, CFG)
    return _ok(
        r.verdict == "confident"
        and any("borderline" in n for n in r.disagreement_notes),
        f"verdict={r.verdict} notes={r.disagreement_notes}",
    )


# ── Question-type + framework priority ───────────────────────────────

def test_curated_lexicon_wins_question_type():
    signals = [
        _sig("retrieval",       refs=[("A.5.18", 0.50)], framework="ISO27001:2022"),
        _sig("curated_lexicon", refs=[("A.5.18", 0.30)], question_type="document_inventory"),
        _sig("session_context", refs=[("A.5.18", 0.10)], question_type="posture_check"),
    ]
    r = aggregate(signals, CFG)
    return _ok(
        r.question_type == "document_inventory",
        f"qt={r.question_type}",
    )


def test_session_context_carries_qt_when_curated_absent():
    signals = [
        _sig("retrieval",       refs=[("A.5.18", 0.50)], framework="ISO27001:2022"),
        _sig("session_context", refs=[("A.5.18", 0.10)], question_type="posture_check"),
    ]
    r = aggregate(signals, CFG)
    return _ok(r.question_type == "posture_check")


def test_explicit_refs_framework_beats_hint():
    signals = [
        _sig("explicit_refs",  refs=[("A.5.18", 1.00)], framework="ISO27001:2022"),
        _sig("framework_hint", framework="GDPR:2016/679"),
    ]
    r = aggregate(signals, CFG)
    # explicit_refs wins
    return _ok(r.framework == "ISO27001:2022", f"framework={r.framework}")


def test_framework_hint_used_when_no_explicit_refs():
    signals = [
        _sig("retrieval",      refs=[("A.5.18", 0.50)], framework="ISO27001:2022"),
        _sig("framework_hint", framework="GDPR:2016/679"),
    ]
    r = aggregate(signals, CFG)
    # explicit_refs not fired → framework_hint wins over retrieval
    return _ok(r.framework == "GDPR:2016/679", f"framework={r.framework}")


def test_framework_disagreement_note_recorded():
    signals = [
        _sig("retrieval",      refs=[("A.5.18", 0.50)], framework="ISO27001:2022"),
        _sig("framework_hint", framework="GDPR:2016/679"),
    ]
    r = aggregate(signals, CFG)
    return _ok(
        any("framework disagreement" in n for n in r.disagreement_notes),
        f"notes={r.disagreement_notes}",
    )


# ── Corroborator counting ────────────────────────────────────────────

def test_penalty_weight_does_not_count_as_corroboration():
    # graph_tightness penalty on outlier — should NOT count
    signals = [
        _sig("retrieval",       refs=[("A.5.18", 0.72)]),
        _sig("graph_tightness", refs=[("A.5.18", -0.10)]),   # penalty
    ]
    r = aggregate(signals, CFG)
    return _ok(
        r.corroborators == 1,   # only retrieval counts
        f"corroborators={r.corroborators}",
    )


def test_positive_boost_counts_as_corroboration():
    signals = [
        _sig("retrieval",       refs=[("A.5.18", 0.72)]),
        _sig("graph_tightness", refs=[("A.5.18", 0.05)]),   # boost
    ]
    r = aggregate(signals, CFG)
    return _ok(r.corroborators == 2, f"corroborators={r.corroborators}")


def test_same_signal_multiple_refs_counts_once_per_ref():
    # A signal listing A.5.18 twice via duplicate refs still counts
    # as 1 corroborator for A.5.18
    signals = [
        _sig("retrieval",       refs=[("A.5.18", 0.72)]),
        _sig("explicit_refs",   refs=[("A.5.18", 1.00), ("A.5.18", 1.00)]),
    ]
    r = aggregate(signals, CFG)
    return _ok(r.corroborators == 2)


# ── Score aggregation ────────────────────────────────────────────────

def test_scores_summed_across_signals():
    signals = [
        _sig("retrieval",     refs=[("A.5.18", 0.60)]),
        _sig("explicit_refs", refs=[("A.5.18", 1.00)]),
        _sig("posture_boost", refs=[("A.5.18", 0.15)]),
    ]
    r = aggregate(signals, CFG)
    return _ok(
        abs(r.top_ref_confidence - 1.75) < 0.001,
        f"top_ref_confidence={r.top_ref_confidence}",
    )


# ── LLM fallback flag ────────────────────────────────────────────────

def test_llm_fallback_disabled_by_config():
    cfg = ConsensusConfig(llm_fallback_enabled=False)
    r = aggregate([], cfg)
    return _ok(r.verdict == "insufficient" and r.llm_fallback_needed is False)


def test_llm_fallback_only_on_insufficient():
    # Confident verdict should not need LLM fallback
    signals = [
        _sig("retrieval",     refs=[("A.5.18", 0.72)]),
        _sig("explicit_refs", refs=[("A.5.18", 1.00)]),
    ]
    r = aggregate(signals, CFG)
    return _ok(r.llm_fallback_needed is False)


TESTS = [
    test_empty_signals_returns_insufficient,
    test_all_signals_not_fired_returns_insufficient,
    test_only_framework_hint_returns_insufficient,
    test_high_retrieval_score_plus_curated_confident,
    test_explicit_ref_alone_still_confident,
    test_five_signals_agree_high_confidence,
    test_two_families_within_tie_band_returns_ambiguous,
    test_ambiguous_clarification_question_lists_titles,
    test_tied_refs_same_family_not_ambiguous,
    test_scores_outside_tie_band_not_ambiguous,
    test_below_min_floor_returns_insufficient,
    test_borderline_between_floor_and_confident_is_confident,
    test_curated_lexicon_wins_question_type,
    test_session_context_carries_qt_when_curated_absent,
    test_explicit_refs_framework_beats_hint,
    test_framework_hint_used_when_no_explicit_refs,
    test_framework_disagreement_note_recorded,
    test_penalty_weight_does_not_count_as_corroboration,
    test_positive_boost_counts_as_corroboration,
    test_same_signal_multiple_refs_counts_once_per_ref,
    test_scores_summed_across_signals,
    test_llm_fallback_disabled_by_config,
    test_llm_fallback_only_on_insufficient,
]


def main():
    print("─" * 70)
    print("  Aggregator integration tests")
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
