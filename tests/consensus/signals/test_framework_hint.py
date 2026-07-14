"""Tests for Signal F — framework_hint regex."""
import sys
from rag.consensus.signals.framework_hint import framework_hint
from rag.consensus.types import ConsensusConfig


CFG = ConsensusConfig()


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


def test_empty_query_does_not_fire():
    return _ok(not framework_hint("", CFG).fired)


def test_no_framework_mentioned_does_not_fire():
    out = framework_hint("what documents do we need for access rights?", CFG)
    return _ok(not out.fired)


def test_iso_27001_no_space():
    out = framework_hint("we implement ISO27001", CFG)
    return _ok(out.fired and out.framework == "ISO27001:2022",
               f"framework={out.framework}")


def test_iso_27001_with_space():
    out = framework_hint("we implement ISO 27001", CFG)
    return _ok(out.fired and out.framework == "ISO27001:2022")


def test_iso_27701_matches_before_27001():
    # Both 27701 and 27001 patterns in the query — 27701 should
    # match first (more specific)
    out = framework_hint("we implement ISO 27701 alongside ISO 27001", CFG)
    return _ok(out.framework == "ISO27701:2019",
               f"expected 27701, got {out.framework}")


def test_gdpr_matches():
    out = framework_hint("we operate under GDPR", CFG)
    return _ok(out.fired and out.framework == "GDPR:2016/679")


def test_pims_maps_to_27701():
    out = framework_hint("do we have PIMS in scope?", CFG)
    return _ok(out.framework == "ISO27701:2019", f"framework={out.framework}")


def test_nis2_variations():
    out1 = framework_hint("is NIS2 applicable?", CFG)
    out2 = framework_hint("is NIS 2 applicable?", CFG)
    return _ok(out1.framework == "NIS2:2022" and out2.framework == "NIS2:2022",
               f"NIS2={out1.framework} NIS 2={out2.framework}")


def test_dora_matches():
    out = framework_hint("we're subject to DORA", CFG)
    return _ok(out.framework == "DORA:2022")


def test_soc2_variations():
    out1 = framework_hint("we need SOC2 certification", CFG)
    out2 = framework_hint("we need SOC 2 certification", CFG)
    return _ok(out1.framework == "SOC2" and out2.framework == "SOC2")


def test_hipaa_matches():
    out = framework_hint("HIPAA covered entity questions", CFG)
    return _ok(out.framework == "HIPAA")


def test_multi_framework_query_returns_primary():
    out = framework_hint("GDPR fulfilled via ISO 27001 controls", CFG)
    # GDPR matches — first in pattern list is 27701, which doesn't
    # match here, so 27001 and GDPR both fire. Primary is the
    # first-matched-in-source-order token.
    return _ok(out.fired and out.framework in ("ISO27001:2022", "GDPR:2016/679"),
               f"framework={out.framework}")


def test_multi_framework_metadata_records_all():
    out = framework_hint("GDPR via ISO 27001", CFG)
    all_fw = out.metadata.get("all_frameworks", [])
    return _ok("GDPR:2016/679" in all_fw and "ISO27001:2022" in all_fw,
               f"all_frameworks={all_fw}")


def test_multi_framework_metadata_flag_set():
    out = framework_hint("GDPR via ISO 27001", CFG)
    return _ok(out.metadata.get("is_multi_framework") is True,
               f"flag={out.metadata.get('is_multi_framework')}")


def test_single_framework_metadata_flag_false():
    out = framework_hint("ISO 27001 only", CFG)
    return _ok(out.metadata.get("is_multi_framework") is False)


def test_iso_27002_maps_to_27001():
    # 27002 is 27001's guidance — same standard_id target
    out = framework_hint("ISO 27002 gives guidance", CFG)
    return _ok(out.framework == "ISO27001:2022", f"framework={out.framework}")


def test_word_boundary_no_false_positive():
    # "IGDPRoup" (a made-up word containing GDPR) should not match
    out = framework_hint("we're the IGDPRoup company", CFG)
    return _ok(not out.fired, f"unexpected match: {out}")


def test_matched_tokens_recorded():
    out = framework_hint("GDPR + ISO 27001", CFG)
    tokens = out.metadata.get("matched_tokens", [])
    return _ok(len(tokens) >= 1, f"tokens={tokens}")


TESTS = [
    test_empty_query_does_not_fire,
    test_no_framework_mentioned_does_not_fire,
    test_iso_27001_no_space,
    test_iso_27001_with_space,
    test_iso_27701_matches_before_27001,
    test_gdpr_matches,
    test_pims_maps_to_27701,
    test_nis2_variations,
    test_dora_matches,
    test_soc2_variations,
    test_hipaa_matches,
    test_multi_framework_query_returns_primary,
    test_multi_framework_metadata_records_all,
    test_multi_framework_metadata_flag_set,
    test_single_framework_metadata_flag_false,
    test_iso_27002_maps_to_27001,
    test_word_boundary_no_false_positive,
    test_matched_tokens_recorded,
]


def main():
    print("─" * 70)
    print("  Signal F — framework_hint unit tests")
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
