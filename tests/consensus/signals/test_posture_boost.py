"""Tests for Signal D — posture_boost (tenant NC/OFI re-weight)."""
import sys
from rag.consensus.signals.posture_boost import posture_boost
from rag.consensus.types import ConsensusConfig


CFG = ConsensusConfig()


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


def test_empty_candidates_does_not_fire():
    return _ok(not posture_boost([], {"A.5.18": {"finding": "NC"}}, CFG).fired)


def test_none_posture_does_not_fire():
    return _ok(not posture_boost(["A.5.18"], None, CFG).fired)


def test_empty_posture_does_not_fire():
    return _ok(not posture_boost(["A.5.18"], {}, CFG).fired)


def test_nc_finding_boosted():
    posture = {"A.5.18": {"finding": "NC"}}
    out = posture_boost(["A.5.18"], posture, CFG)
    if not out.fired:
        return _ok(False, "expected fire")
    return _ok(out.refs == [("A.5.18", CFG.posture_boost_weight)],
               f"refs={out.refs}")


def test_ofi_finding_boosted():
    posture = {"A.5.18": {"finding": "OFI"}}
    out = posture_boost(["A.5.18"], posture, CFG)
    return _ok(out.refs == [("A.5.18", CFG.posture_boost_weight)])


def test_comply_finding_not_boosted():
    posture = {"A.5.18": {"finding": "Comply"}}
    out = posture_boost(["A.5.18"], posture, CFG)
    return _ok(not out.fired, f"unexpected boost on Comply: {out.refs}")


def test_na_finding_not_boosted():
    posture = {"A.5.18": {"finding": "N/A"}}
    out = posture_boost(["A.5.18"], posture, CFG)
    return _ok(not out.fired)


def test_not_yet_assessed_not_boosted():
    posture = {"A.5.18": {"finding": "Not yet assessed"}}
    out = posture_boost(["A.5.18"], posture, CFG)
    return _ok(not out.fired)


def test_partial_candidate_coverage():
    # Two candidates, only one has open finding
    posture = {"A.5.18": {"finding": "NC"}, "A.5.15": {"finding": "Comply"}}
    out = posture_boost(["A.5.18", "A.5.15"], posture, CFG)
    refs_dict = dict(out.refs)
    return _ok(
        "A.5.18" in refs_dict and "A.5.15" not in refs_dict,
        f"refs={out.refs}",
    )


def test_candidate_not_in_posture_ignored():
    posture = {"A.5.18": {"finding": "NC"}}
    out = posture_boost(["A.5.18", "A.9.99"], posture, CFG)
    refs_dict = dict(out.refs)
    return _ok(
        "A.5.18" in refs_dict and "A.9.99" not in refs_dict,
        f"refs={out.refs}",
    )


def test_multiple_boosted():
    posture = {"A.5.18": {"finding": "NC"}, "A.5.15": {"finding": "OFI"}}
    out = posture_boost(["A.5.18", "A.5.15"], posture, CFG)
    return _ok(len(out.refs) == 2)


def test_findings_by_ref_metadata():
    posture = {"A.5.18": {"finding": "NC"}, "A.5.15": {"finding": "OFI"}}
    out = posture_boost(["A.5.18", "A.5.15"], posture, CFG)
    md = out.metadata["findings_by_ref"]
    return _ok(
        md.get("A.5.18") == "NC" and md.get("A.5.15") == "OFI",
        f"findings_by_ref={md}",
    )


def test_raw_posture_shape_by_nodeid():
    # posture_loader keys are node_ids like "ISO27001:2022:A.5.18"
    posture = {
        "ISO27001:2022:A.5.18": {"control_ref": "A.5.18", "finding": "NC"},
        "ISO27001:2022:A.5.15": {"control_ref": "A.5.15", "finding": "Comply"},
    }
    out = posture_boost(["A.5.18", "A.5.15"], posture, CFG)
    refs_dict = dict(out.refs)
    return _ok(
        "A.5.18" in refs_dict and "A.5.15" not in refs_dict,
        f"refs={out.refs}",
    )


def test_config_weight_applied():
    cfg = ConsensusConfig(posture_boost_weight=0.42)
    posture = {"A.5.18": {"finding": "NC"}}
    out = posture_boost(["A.5.18"], posture, cfg)
    return _ok(out.refs == [("A.5.18", 0.42)], f"refs={out.refs}")


def test_no_boosted_returns_not_fired_with_reason():
    posture = {"A.5.18": {"finding": "Comply"}}
    out = posture_boost(["A.5.18"], posture, CFG)
    return _ok(
        not out.fired
        and out.metadata.get("n_boosted") == 0
        and "no open findings" in out.metadata.get("reason", ""),
        f"metadata={out.metadata}",
    )


def test_gdpr_article_ref_boosted():
    posture = {"Art.32": {"finding": "NC"}}
    out = posture_boost(["Art.32"], posture, CFG)
    return _ok(out.refs == [("Art.32", CFG.posture_boost_weight)])


TESTS = [
    test_empty_candidates_does_not_fire,
    test_none_posture_does_not_fire,
    test_empty_posture_does_not_fire,
    test_nc_finding_boosted,
    test_ofi_finding_boosted,
    test_comply_finding_not_boosted,
    test_na_finding_not_boosted,
    test_not_yet_assessed_not_boosted,
    test_partial_candidate_coverage,
    test_candidate_not_in_posture_ignored,
    test_multiple_boosted,
    test_findings_by_ref_metadata,
    test_raw_posture_shape_by_nodeid,
    test_config_weight_applied,
    test_no_boosted_returns_not_fired_with_reason,
    test_gdpr_article_ref_boosted,
]


def main():
    print("─" * 70)
    print("  Signal D — posture_boost unit tests")
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
