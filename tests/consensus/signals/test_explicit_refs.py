"""Tests for Signal B — explicit_refs regex extraction.

Uses the same bespoke test runner pattern as tests/test_applies_when.py:
each test returns (ok, msg); the main block iterates and reports.
"""
import sys
from rag.consensus.signals.explicit_refs import explicit_refs
from rag.consensus.types import ConsensusConfig


CFG = ConsensusConfig()


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


def test_no_refs_in_query_does_not_fire():
    out = explicit_refs("what are our top compliance gaps?", CFG)
    if out.fired:
        return _ok(False, f"expected fired=False, got refs={out.refs}")
    return _ok(True)


def test_empty_query_does_not_fire():
    out = explicit_refs("", CFG)
    return _ok(not out.fired, f"empty query should not fire, got fired={out.fired}")


def test_single_iso_annex_a_ref_fires():
    out = explicit_refs("is A.5.18 compliant?", CFG)
    if not out.fired:
        return _ok(False, "expected fired=True")
    if out.refs != [("A.5.18", 1.00)]:
        return _ok(False, f"refs mismatch: {out.refs}")
    if out.framework != "ISO27001:2022":
        return _ok(False, f"framework={out.framework}")
    return _ok(True)


def test_single_gdpr_article_fires():
    out = explicit_refs("what is the status of Art.32?", CFG)
    if out.refs != [("Art.32", 1.00)] or out.framework != "GDPR:2016/679":
        return _ok(False, f"refs={out.refs} framework={out.framework}")
    return _ok(True)


def test_iso_27701_processor_ref_fires():
    out = explicit_refs("is B.8.5.6 in scope?", CFG)
    if out.refs != [("B.8.5.6", 1.00)] or out.framework != "ISO27701:2019":
        return _ok(False, f"refs={out.refs} framework={out.framework}")
    return _ok(True)


def test_bare_isms_clause_fires():
    out = explicit_refs("what does clause 9.2 require?", CFG)
    if out.refs != [("9.2", 1.00)] or out.framework != "ISO27001:2022":
        return _ok(False, f"refs={out.refs} framework={out.framework}")
    return _ok(True)


def test_multiple_refs_same_framework_dominant():
    out = explicit_refs("compare A.5.15 and A.8.24", CFG)
    refs = {r for r, _ in out.refs}
    if refs != {"A.5.15", "A.8.24"}:
        return _ok(False, f"refs={refs}")
    if out.framework != "ISO27001:2022":
        return _ok(False, f"framework={out.framework}")
    return _ok(True)


def test_multiple_refs_mixed_framework_no_dominant():
    out = explicit_refs("A.5.18 and Art.32 — mixed", CFG)
    refs = {r for r, _ in out.refs}
    if refs != {"A.5.18", "Art.32"}:
        return _ok(False, f"refs={refs}")
    # 1 ISO + 1 GDPR → tie, no dominant
    if out.framework is not None:
        return _ok(False, f"expected no framework on tie, got {out.framework}")
    return _ok(True)


def test_multiple_refs_mixed_but_dominant():
    out = explicit_refs("A.5.15 and A.5.18 alongside Art.32", CFG)
    if out.framework != "ISO27001:2022":
        return _ok(False, f"2 ISO + 1 GDPR should dominate ISO, got {out.framework}")
    return _ok(True)


def test_dedup_preserves_order():
    out = explicit_refs("A.5.18 A.5.18 then A.5.15", CFG)
    seq = [r for r, _ in out.refs]
    if seq != ["A.5.18", "A.5.15"]:
        return _ok(False, f"expected dedupped first-seen order, got {seq}")
    return _ok(True)


def test_gdpr_subarticle_still_gdpr():
    out = explicit_refs("Art.5.1.a — lawfulness", CFG)
    if not out.fired or out.refs[0][0] != "Art.5.1.a":
        return _ok(False, f"refs={out.refs}")
    if out.framework != "GDPR:2016/679":
        return _ok(False, f"framework={out.framework}")
    return _ok(True)


def test_weight_uses_config():
    cfg = ConsensusConfig(explicit_ref_weight=0.5)
    out = explicit_refs("A.5.18", cfg)
    if out.refs != [("A.5.18", 0.5)]:
        return _ok(False, f"refs={out.refs}")
    return _ok(True)


def test_metadata_carries_extracted_count():
    out = explicit_refs("A.5.15 and A.5.18 and A.5.16", CFG)
    if out.metadata.get("extracted_count") != 3:
        return _ok(False, f"metadata={out.metadata}")
    if out.metadata["framework_votes"]["A.5.15"] != "ISO27001:2022":
        return _ok(False, f"framework_votes={out.metadata['framework_votes']}")
    return _ok(True)


def test_ambiguous_a7_iso_vs_27701():
    out = explicit_refs("A.7.4 and A.7.2.4 both exist", CFG)
    refs = {r for r, _ in out.refs}
    if "A.7.4" not in refs or "A.7.2.4" not in refs:
        return _ok(False, f"refs={refs}")
    return _ok(True)


def test_no_false_positive_on_numbers_in_prose():
    out = explicit_refs("we hired 5 people last quarter", CFG)
    if out.fired:
        return _ok(False, f"bare 5 should not extract; got refs={out.refs}")
    return _ok(True)


def test_no_false_positive_on_11_x_out_of_range():
    # ISMS clauses are 4.1..10.9. 11.x is not valid.
    out = explicit_refs("consider 11.1 alongside A.5.18", CFG)
    refs = {r for r, _ in out.refs}
    if "A.5.18" not in refs:
        return _ok(False, f"A.5.18 missing: {refs}")
    if "11.1" in refs:
        return _ok(False, "11.1 extracted but out of ISMS range")
    return _ok(True)


TESTS = [
    test_no_refs_in_query_does_not_fire,
    test_empty_query_does_not_fire,
    test_single_iso_annex_a_ref_fires,
    test_single_gdpr_article_fires,
    test_iso_27701_processor_ref_fires,
    test_bare_isms_clause_fires,
    test_multiple_refs_same_framework_dominant,
    test_multiple_refs_mixed_framework_no_dominant,
    test_multiple_refs_mixed_but_dominant,
    test_dedup_preserves_order,
    test_gdpr_subarticle_still_gdpr,
    test_weight_uses_config,
    test_metadata_carries_extracted_count,
    test_ambiguous_a7_iso_vs_27701,
    test_no_false_positive_on_numbers_in_prose,
    test_no_false_positive_on_11_x_out_of_range,
]


def main():
    print("─" * 70)
    print("  Signal B — explicit_refs unit tests")
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
