"""Unit tests for rag/answer/types.py — payload variants and helpers."""
import sys
from rag.answer.types import (
    RefRecord, PostureFacet, BridgeRecord, ChecklistItem,
    DocumentRequirement, GapEntry,
    AnswerPayloadBase, PostureStatusPayload, DocumentStatusPayload,
    RemediationGuidePayload, DocumentContentPayload,
    StandardKnowledgePayload, CrossFrameworkPayload, FreeformPayload,
    ValidationReport,
)


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


# ── RefRecord ────────────────────────────────────────────────────────

def test_refrecord_iso_flag():
    r = RefRecord(ref="A.5.18", framework="ISO27001:2022", title="Access rights")
    return _ok(r.is_iso and not r.is_gdpr and not r.is_27701,
               f"iso={r.is_iso} gdpr={r.is_gdpr} 27701={r.is_27701}")


def test_refrecord_gdpr_flag():
    r = RefRecord(ref="Art.32", framework="GDPR:2016/679", title="Security of processing")
    return _ok(r.is_gdpr and not r.is_iso, f"gdpr={r.is_gdpr}")


def test_refrecord_27701_flag():
    r = RefRecord(ref="A.7.2.5", framework="ISO27701:2019")
    return _ok(r.is_27701, f"27701={r.is_27701}")


# ── PostureFacet ─────────────────────────────────────────────────────

def test_posture_facet_defaults():
    r = RefRecord(ref="A.5.18", framework="ISO27001:2022")
    p = PostureFacet(ref=r, finding="NC")
    return _ok(
        p.finding == "NC"
        and p.evidence_summary == ""
        and p.engine_reason is None
        and p.partial_evidence is False,
        f"posture={p}",
    )


def test_posture_facet_full():
    r = RefRecord(ref="A.5.18", framework="ISO27001:2022")
    p = PostureFacet(
        ref=r, finding="OFI", evidence_summary="1 of 4 requirements met",
        engine_reason="1 of 4 requirements met", freshness_days=90,
        partial_evidence=True,
    )
    return _ok(p.partial_evidence and p.freshness_days == 90)


# ── BridgeRecord ─────────────────────────────────────────────────────

def test_bridge_record_defaults():
    src = RefRecord(ref="Art.32", framework="GDPR:2016/679")
    dst = RefRecord(ref="A.5.15", framework="ISO27001:2022")
    b = BridgeRecord(from_ref=src, to_ref=dst)
    return _ok(
        b.relationship == "IMPLEMENTS"
        and b.direction == "out"
        and b.posture is None,
        f"bridge={b}",
    )


# ── DocumentRequirement + ChecklistItem ─────────────────────────────

def test_document_requirement_shape():
    r = RefRecord(ref="A.5.18", framework="ISO27001:2022")
    item_m = ChecklistItem(item_id="i1", text="policy scope", category="must")
    item_s = ChecklistItem(item_id="i2", text="approval log", category="should")
    doc = DocumentRequirement(
        control=r, doc_title="Access Rights Procedure",
        evidence_type="procedure",
        must_contain=[item_m], should_contain=[item_s],
    )
    return _ok(
        doc.doc_title == "Access Rights Procedure"
        and len(doc.must_contain) == 1
        and doc.must_contain[0].category == "must",
    )


# ── GapEntry ─────────────────────────────────────────────────────────

def test_gap_entry_severity():
    r = RefRecord(ref="A.5.18", framework="ISO27001:2022")
    g = GapEntry(ref=r, severity="NC", what_missing="policy document",
                 priority_rank=1)
    return _ok(g.severity == "NC" and g.priority_rank == 1)


# ── Payload variants ────────────────────────────────────────────────

def test_posture_status_payload_variant_name():
    p = PostureStatusPayload(question_type="posture_check", query="q")
    return _ok(p.variant_name == "PostureStatusPayload",
               f"variant_name={p.variant_name}")


def test_document_status_payload_defaults():
    p = DocumentStatusPayload(question_type="document_status", query="q")
    return _ok(p.doc_alerts == [] and p.uploaded_docs == [])


def test_remediation_guide_payload_defaults():
    p = RemediationGuidePayload(question_type="gap_analysis", query="q")
    return _ok(
        p.nc_gaps == [] and p.ofi_gaps == [] and p.xfw_context == []
        and p.priority_order == [],
    )


def test_document_content_payload_defaults():
    p = DocumentContentPayload(question_type="document_content", query="q")
    return _ok(p.documents == [])


def test_standard_knowledge_payload_defaults():
    p = StandardKnowledgePayload(question_type="definition", query="q")
    return _ok(
        p.acronym is None and p.expansion is None
        and p.definition == "" and p.examples == [],
    )


def test_cross_framework_payload_defaults():
    p = CrossFrameworkPayload(question_type="cross_framework", query="q")
    return _ok(
        p.primary_posture is None and p.xfw_bridges == []
        and p.framework_map == {},
    )


def test_freeform_payload_defaults():
    p = FreeformPayload(question_type="unknown", query="q",
                        reason_fallback="no dedicated builder")
    return _ok(p.reason_fallback == "no dedicated builder")


# ── ValidationReport ────────────────────────────────────────────────

def test_validation_report_initial_pass():
    r = ValidationReport()
    return _ok(r.passed and r.violations == [] and r.warnings == [])


def test_validation_report_add_violation_flips_passed():
    r = ValidationReport()
    r.add_violation("bad")
    return _ok(not r.passed and r.violations == ["bad"])


def test_validation_report_add_warning_does_not_flip_passed():
    r = ValidationReport()
    r.add_warning("hmm")
    return _ok(r.passed and r.warnings == ["hmm"])


TESTS = [
    test_refrecord_iso_flag,
    test_refrecord_gdpr_flag,
    test_refrecord_27701_flag,
    test_posture_facet_defaults,
    test_posture_facet_full,
    test_bridge_record_defaults,
    test_document_requirement_shape,
    test_gap_entry_severity,
    test_posture_status_payload_variant_name,
    test_document_status_payload_defaults,
    test_remediation_guide_payload_defaults,
    test_document_content_payload_defaults,
    test_standard_knowledge_payload_defaults,
    test_cross_framework_payload_defaults,
    test_freeform_payload_defaults,
    test_validation_report_initial_pass,
    test_validation_report_add_violation_flips_passed,
    test_validation_report_add_warning_does_not_flip_passed,
]


def main():
    print("─" * 70)
    print("  Ship 2.0 — payload types unit tests")
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
