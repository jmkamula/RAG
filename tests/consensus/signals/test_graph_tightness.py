"""Tests for Signal E — graph_tightness (pure ref-string clustering)."""
import sys
from rag.consensus.signals.graph_tightness import graph_tightness
from rag.consensus.types import ConsensusConfig


CFG = ConsensusConfig()


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


def test_empty_refs_does_not_fire():
    return _ok(not graph_tightness([], CFG).fired)


def test_single_ref_is_100pct_tight():
    out = graph_tightness(["A.5.18"], CFG)
    if not out.fired:
        return _ok(False, "expected fired=True")
    return _ok(
        out.metadata["majority_family"] == "A.5"
        and out.metadata["majority_share"] == 1.0
        and out.metadata["tight"] is True,
        f"metadata={out.metadata}",
    )


def test_all_same_family_is_tight():
    refs = ["A.5.15", "A.5.18", "A.5.16"]
    out = graph_tightness(refs, CFG)
    return _ok(
        out.metadata["majority_family"] == "A.5"
        and out.metadata["majority_share"] == 1.0
        and out.metadata["tight"] is True,
        f"metadata={out.metadata}",
    )


def test_mixed_families_majority():
    # 2 A.5.x, 1 A.8.x → majority A.5, tightness 2/3
    refs = ["A.5.15", "A.5.18", "A.8.24"]
    out = graph_tightness(refs, CFG)
    return _ok(
        out.metadata["majority_family"] == "A.5"
        and abs(out.metadata["majority_share"] - 2/3) < 0.01
        and out.metadata["tight"] is True,  # 2/3 > 0.5
        f"metadata={out.metadata}",
    )


def test_spread_across_many_families_not_tight():
    # 3 different families, no majority > 0.5
    refs = ["A.5.15", "A.7.4", "A.8.24"]
    out = graph_tightness(refs, CFG)
    return _ok(
        out.metadata["majority_share"] < 0.5,
        f"share={out.metadata['majority_share']}",
    )


def test_boost_on_majority_family_ref():
    refs = ["A.5.15", "A.5.18", "A.8.24"]
    out = graph_tightness(refs, CFG)
    refs_dict = dict(out.refs)
    return _ok(
        refs_dict["A.5.15"] == CFG.graph_tight_family_boost
        and refs_dict["A.5.18"] == CFG.graph_tight_family_boost,
        f"refs={out.refs}",
    )


def test_penalty_on_outlier_family_ref():
    refs = ["A.5.15", "A.5.18", "A.8.24"]
    out = graph_tightness(refs, CFG)
    refs_dict = dict(out.refs)
    return _ok(
        refs_dict["A.8.24"] == CFG.graph_spread_penalty,
        f"A.8.24 weight: {refs_dict.get('A.8.24')}",
    )


def test_first_seen_order_breaks_ties():
    # 2 families with equal count (1 each) — first-seen wins
    refs = ["A.5.18", "A.8.24"]
    out = graph_tightness(refs, CFG)
    return _ok(
        out.metadata["majority_family"] == "A.5",
        f"majority={out.metadata['majority_family']}",
    )


def test_gdpr_families_grouped():
    refs = ["Art.32", "Art.32.1.b", "Art.5.1.f"]
    out = graph_tightness(refs, CFG)
    fams = out.metadata["family_counts"]
    return _ok(
        fams.get("Art.32") == 2 and fams.get("Art.5") == 1,
        f"family_counts={fams}",
    )


def test_iso_27701_families():
    refs = ["A.7.2.4", "A.7.2.6", "B.8.5.6"]
    out = graph_tightness(refs, CFG)
    fams = out.metadata["family_counts"]
    return _ok(
        fams.get("A.7") == 2 and fams.get("B.8") == 1,
        f"family_counts={fams}",
    )


def test_isms_bare_clause_families():
    refs = ["9.1", "9.2", "6.1.2"]
    out = graph_tightness(refs, CFG)
    fams = out.metadata["family_counts"]
    # ISMS bare-clause family_of returns first segment (e.g. "9")
    return _ok(
        fams.get("9") == 2 and fams.get("6") == 1,
        f"family_counts={fams}",
    )


def test_all_families_recorded_in_metadata():
    refs = ["A.5.15", "A.5.18", "A.8.24", "Art.32"]
    out = graph_tightness(refs, CFG)
    fams = set(out.metadata["families_present"])
    return _ok(fams == {"A.5", "A.8", "Art.32"}, f"families={fams}")


def test_config_weights_override():
    cfg = ConsensusConfig(graph_tight_family_boost=0.30, graph_spread_penalty=-0.50)
    refs = ["A.5.15", "A.5.18", "A.8.24"]
    out = graph_tightness(refs, cfg)
    refs_dict = dict(out.refs)
    return _ok(
        refs_dict["A.5.15"] == 0.30 and refs_dict["A.8.24"] == -0.50,
        f"refs={out.refs}",
    )


TESTS = [
    test_empty_refs_does_not_fire,
    test_single_ref_is_100pct_tight,
    test_all_same_family_is_tight,
    test_mixed_families_majority,
    test_spread_across_many_families_not_tight,
    test_boost_on_majority_family_ref,
    test_penalty_on_outlier_family_ref,
    test_first_seen_order_breaks_ties,
    test_gdpr_families_grouped,
    test_iso_27701_families,
    test_isms_bare_clause_families,
    test_all_families_recorded_in_metadata,
    test_config_weights_override,
]


def main():
    print("─" * 70)
    print("  Signal E — graph_tightness unit tests")
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
