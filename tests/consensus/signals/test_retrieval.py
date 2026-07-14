"""Tests for Signal A — retrieval (ChromaDB anchor).

Uses a fake retriever so tests are deterministic — no live ChromaDB.
"""
import sys
from dataclasses import dataclass, field

from rag.consensus.signals.retrieval import retrieve
from rag.consensus.types import ConsensusConfig


CFG = ConsensusConfig()


@dataclass
class _FakeResult:
    ref:         str
    score:       float
    standard_id: str = "ISO27001:2022"


@dataclass
class _FakeContext:
    results: list = field(default_factory=list)


class _FakeRetriever:
    """Mimics VectorRetriever.search — returns a preset result list."""
    def __init__(self, results, raises=None):
        self._results = results
        self._raises  = raises
        self.last_args = None

    def search(self, query, n=10, standards=None):
        self.last_args = (query, n, standards)
        if self._raises:
            raise self._raises
        return _FakeContext(results=self._results)


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


def test_none_retriever_does_not_fire():
    return _ok(not retrieve("access rights", None, cfg=CFG).fired)


def test_empty_query_does_not_fire():
    r = _FakeRetriever([])
    return _ok(not retrieve("", r, cfg=CFG).fired)


def test_empty_results_does_not_fire():
    r = _FakeRetriever([])
    out = retrieve("random noise", r, cfg=CFG)
    return _ok(not out.fired and out.metadata.get("empty") is True,
               f"metadata={out.metadata}")


def test_retriever_exception_captured_no_raise():
    r = _FakeRetriever([], raises=RuntimeError("chroma down"))
    out = retrieve("test", r, cfg=CFG)
    return _ok(
        not out.fired
        and out.metadata.get("error") == "RuntimeError"
        and "chroma down" in out.metadata.get("detail", ""),
        f"metadata={out.metadata}",
    )


def test_single_result_fires_with_score_as_weight():
    r = _FakeRetriever([_FakeResult("A.5.18", 0.72)])
    out = retrieve("access rights", r, cfg=CFG)
    if not out.fired:
        return _ok(False, "expected fired=True")
    if out.refs != [("A.5.18", 0.72)]:
        return _ok(False, f"refs={out.refs}")
    return _ok(True)


def test_top_k_ordered_by_score_desc():
    r = _FakeRetriever([
        _FakeResult("A.5.16", 0.51),
        _FakeResult("A.5.18", 0.72),
        _FakeResult("A.5.15", 0.68),
    ])
    out = retrieve("access rights", r, cfg=CFG)
    refs_ordered = [ref for ref, _ in out.refs]
    return _ok(refs_ordered == ["A.5.18", "A.5.15", "A.5.16"],
               f"refs order: {refs_ordered}")


def test_dedupe_by_ref_keeps_best_score():
    r = _FakeRetriever([
        _FakeResult("A.5.18", 0.72),
        _FakeResult("A.5.18", 0.85),   # duplicate — higher score
        _FakeResult("A.5.15", 0.60),
    ])
    out = retrieve("access rights", r, cfg=CFG)
    refs_dict = dict(out.refs)
    return _ok(
        refs_dict.get("A.5.18") == 0.85 and refs_dict.get("A.5.15") == 0.60,
        f"refs={out.refs}",
    )


def test_framework_majority_vote():
    r = _FakeRetriever([
        _FakeResult("A.5.18", 0.72, "ISO27001:2022"),
        _FakeResult("A.5.15", 0.68, "ISO27001:2022"),
        _FakeResult("Art.32", 0.51, "GDPR:2016/679"),
    ])
    out = retrieve("access rights", r, cfg=CFG)
    return _ok(out.framework == "ISO27001:2022", f"framework={out.framework}")


def test_framework_gdpr_majority():
    r = _FakeRetriever([
        _FakeResult("Art.32", 0.72, "GDPR:2016/679"),
        _FakeResult("Art.5.1.f", 0.68, "GDPR:2016/679"),
        _FakeResult("A.5.15", 0.51, "ISO27001:2022"),
    ])
    out = retrieve("data protection principles", r, cfg=CFG)
    return _ok(out.framework == "GDPR:2016/679")


def test_metadata_records_top_score_and_ref():
    r = _FakeRetriever([_FakeResult("A.5.18", 0.72), _FakeResult("A.5.15", 0.68)])
    out = retrieve("q", r, cfg=CFG)
    md = out.metadata
    return _ok(
        md["top_ref"] == "A.5.18"
        and md["top_score"] == 0.72
        and md["n_results"] == 2,
        f"metadata={md}",
    )


def test_metadata_flags_confidence_thresholds():
    r = _FakeRetriever([_FakeResult("A.5.18", 0.42)])
    out = retrieve("q", r, cfg=CFG)
    md = out.metadata
    return _ok(
        md["above_min_floor"] is True     # 0.42 > 0.20
        and md["above_confident"] is True # 0.42 > 0.35
        , f"metadata={md}",
    )


def test_metadata_flags_below_floor():
    r = _FakeRetriever([_FakeResult("A.5.18", 0.15)])
    out = retrieve("q", r, cfg=CFG)
    md = out.metadata
    return _ok(
        md["above_min_floor"] is False    # 0.15 < 0.20
        and md["above_confident"] is False,
        f"metadata={md}",
    )


def test_tie_band_size_reported():
    r = _FakeRetriever([
        _FakeResult("A.5.18", 0.72),
        _FakeResult("A.5.15", 0.70),      # within tie band
        _FakeResult("A.5.16", 0.68),      # within tie band
        _FakeResult("A.5.17", 0.55),      # outside tie band
    ])
    out = retrieve("q", r, cfg=CFG)
    return _ok(out.metadata["tie_band_size"] == 3,
               f"tie_band_size={out.metadata['tie_band_size']}")


def test_framework_votes_recorded():
    r = _FakeRetriever([
        _FakeResult("A.5.18", 0.72, "ISO27001:2022"),
        _FakeResult("A.5.15", 0.68, "ISO27001:2022"),
        _FakeResult("Art.32", 0.51, "GDPR:2016/679"),
    ])
    out = retrieve("q", r, cfg=CFG)
    votes = out.metadata["framework_votes"]
    return _ok(
        votes.get("ISO27001:2022") == 2
        and votes.get("GDPR:2016/679") == 1,
        f"votes={votes}",
    )


def test_standards_arg_passed_to_retriever():
    r = _FakeRetriever([_FakeResult("A.5.18", 0.72)])
    retrieve("q", r, standards=["ISO27001:2022"], cfg=CFG)
    return _ok(
        r.last_args[2] == ["ISO27001:2022"],
        f"standards not passed: {r.last_args}",
    )


def test_max_top_k_from_config():
    cfg = ConsensusConfig(max_top_k_retrieval=3)
    r = _FakeRetriever([_FakeResult("A.5.18", 0.72)])
    retrieve("q", r, cfg=cfg)
    return _ok(r.last_args[1] == 3, f"n arg not honoured: {r.last_args}")


TESTS = [
    test_none_retriever_does_not_fire,
    test_empty_query_does_not_fire,
    test_empty_results_does_not_fire,
    test_retriever_exception_captured_no_raise,
    test_single_result_fires_with_score_as_weight,
    test_top_k_ordered_by_score_desc,
    test_dedupe_by_ref_keeps_best_score,
    test_framework_majority_vote,
    test_framework_gdpr_majority,
    test_metadata_records_top_score_and_ref,
    test_metadata_flags_confidence_thresholds,
    test_metadata_flags_below_floor,
    test_tie_band_size_reported,
    test_framework_votes_recorded,
    test_standards_arg_passed_to_retriever,
    test_max_top_k_from_config,
]


def main():
    print("─" * 70)
    print("  Signal A — retrieval unit tests")
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
