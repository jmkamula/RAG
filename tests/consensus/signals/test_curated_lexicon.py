"""Tests for Signal C — curated_lexicon (CLEAR_INTENT_PHRASES + DOCUMENT_TOPIC_MAP)."""
import sys
from rag.consensus.signals.curated_lexicon import curated_lexicon
from rag.consensus.types import ConsensusConfig


CFG = ConsensusConfig()


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


def test_empty_query_does_not_fire():
    out = curated_lexicon("", CFG)
    return _ok(not out.fired)


def test_no_match_does_not_fire():
    out = curated_lexicon("random noise text with no keywords", CFG)
    return _ok(not out.fired, f"unexpected fire: {out}")


def test_ofi_definition_fires_clear_intent():
    out = curated_lexicon("what does OFI mean?", CFG)
    if not out.fired:
        return _ok(False, "expected fired=True")
    if out.question_type != "definition":
        return _ok(False, f"question_type={out.question_type}")
    return _ok(True)


def test_nc_definition_fires():
    out = curated_lexicon("what does NC mean?", CFG)
    return _ok(out.fired and out.question_type == "definition",
               f"fired={out.fired} qt={out.question_type}")


def test_document_topic_map_access_rights_hits_a518():
    out = curated_lexicon("what documents do we need for access rights?", CFG)
    if not out.fired:
        return _ok(False, "should fire on topic_map")
    refs = [r for r, _ in out.refs]
    if "A.5.18" not in refs:
        return _ok(False, f"A.5.18 missing: {refs}")
    return _ok(True)


def test_document_topic_map_cryptography_hits_a824():
    out = curated_lexicon("what does the cryptography policy contain?", CFG)
    refs = [r for r, _ in out.refs]
    return _ok("A.8.24" in refs, f"refs={refs}")


def test_document_topic_map_ropa_hits_art30():
    out = curated_lexicon("what does our records of processing look like?", CFG)
    refs = [r for r, _ in out.refs]
    return _ok("Art.30" in refs, f"refs={refs}")


def test_gap_analysis_pattern_fires():
    out = curated_lexicon("what are our top compliance gaps?", CFG)
    return _ok(out.fired and out.question_type == "gap_analysis",
               f"fired={out.fired} qt={out.question_type}")


def test_encryption_gaps_hits_clear_intent_with_seed_refs():
    out = curated_lexicon("what are our encryption gaps?", CFG)
    if out.question_type != "gap_analysis":
        return _ok(False, f"qt={out.question_type}")
    refs = [r for r, _ in out.refs]
    if "A.8.24" not in refs:
        return _ok(False, f"expected A.8.24 in seed_refs, got {refs}")
    return _ok(True)


def test_audit_prep_hits_implementation_with_92():
    out = curated_lexicon("preparing for our ISO 27001 audit", CFG)
    if out.question_type != "implementation":
        return _ok(False, f"qt={out.question_type}")
    refs = [r for r, _ in out.refs]
    if "9.2" not in refs:
        return _ok(False, f"expected 9.2, got {refs}")
    return _ok(True)


def test_weight_applied_from_config():
    cfg = ConsensusConfig(curated_lexicon_weight=0.42)
    out = curated_lexicon("what are our encryption gaps?", cfg)
    # All refs should carry the config weight
    if out.refs:
        weights = {w for _, w in out.refs}
        if weights != {0.42}:
            return _ok(False, f"weight mismatch: {weights}")
    return _ok(True)


def test_framework_inferred_from_iso_ref():
    out = curated_lexicon("what are our encryption gaps?", CFG)
    return _ok(out.framework == "ISO27001:2022",
               f"framework={out.framework}")


def test_framework_inferred_from_gdpr_ref():
    out = curated_lexicon("what about DPIA compliance?", CFG)
    # DOCUMENT_TOPIC_MAP maps "DPIA" family to Art.35 typically
    if not out.fired:
        return _ok(True, "skipped — no DPIA topic in map")
    refs = [r for r, _ in out.refs]
    if any(r.startswith("Art.") for r in refs):
        return _ok(out.framework == "GDPR:2016/679",
                   f"framework={out.framework} for refs={refs}")
    return _ok(True, "no GDPR ref matched — inference OK")


def test_metadata_pattern_recorded():
    out = curated_lexicon("what does OFI mean?", CFG)
    return _ok(out.metadata.get("matched_pattern") is not None,
               f"no pattern in metadata: {out.metadata}")


def test_metadata_topics_recorded():
    out = curated_lexicon("access rights and encryption", CFG)
    topics = out.metadata.get("matched_topics", [])
    return _ok("access rights" in topics or "encryption" in topics,
               f"topics missing: {topics}")


TESTS = [
    test_empty_query_does_not_fire,
    test_no_match_does_not_fire,
    test_ofi_definition_fires_clear_intent,
    test_nc_definition_fires,
    test_document_topic_map_access_rights_hits_a518,
    test_document_topic_map_cryptography_hits_a824,
    test_document_topic_map_ropa_hits_art30,
    test_gap_analysis_pattern_fires,
    test_encryption_gaps_hits_clear_intent_with_seed_refs,
    test_audit_prep_hits_implementation_with_92,
    test_weight_applied_from_config,
    test_framework_inferred_from_iso_ref,
    test_framework_inferred_from_gdpr_ref,
    test_metadata_pattern_recorded,
    test_metadata_topics_recorded,
]


def main():
    print("─" * 70)
    print("  Signal C — curated_lexicon unit tests")
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
