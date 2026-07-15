"""Unit tests for rag/answer/validator.py."""
import sys
import types as _types

from rag.answer.types import (
    RefRecord, PostureFacet, BridgeRecord, ChecklistItem,
    DocumentRequirement, GapEntry,
    PostureStatusPayload, DocumentStatusPayload,
    RemediationGuidePayload, DocumentContentPayload,
    StandardKnowledgePayload, CrossFrameworkPayload, FreeformPayload,
)
from rag.answer.validator import validate


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


def _iso_ref(ref="A.5.18", title="Access rights"):
    return RefRecord(ref=ref, framework="ISO27001:2022", title=title)


def _gdpr_ref(ref="Art.32", title="Security of processing"):
    return RefRecord(ref=ref, framework="GDPR:2016/679", title=title)


def _tenant(scope=None):
    """Mock tenant_context with scope.queryable_standards."""
    _s = _types.SimpleNamespace(queryable_standards=scope or ["ISO27001:2022", "GDPR:2016/679"])
    return _types.SimpleNamespace(scope=_s)


# ── subject_refs scope check ─────────────────────────────────────────

def test_valid_iso_ref_passes():
    p = PostureStatusPayload(
        question_type="posture_check", query="q",
        frameworks_scope=["ISO27001:2022"],
        subject_refs=[_iso_ref()],
        postures=[PostureFacet(ref=_iso_ref(), finding="NC")],
    )
    r = validate(p)
    return _ok(r.passed and not r.violations, f"violations={r.violations}")


def test_out_of_scope_ref_violates():
    # ISO ref but scope only has GDPR
    p = PostureStatusPayload(
        question_type="posture_check", query="q",
        frameworks_scope=["GDPR:2016/679"],
        subject_refs=[_iso_ref()],
    )
    r = validate(p)
    return _ok(
        not r.passed and any("not in tenant scope" in v for v in r.violations),
        f"violations={r.violations}",
    )


def test_scope_pulled_from_tenant_context():
    p = PostureStatusPayload(
        question_type="posture_check", query="q",
        subject_refs=[_iso_ref()],
        postures=[PostureFacet(ref=_iso_ref(), finding="NC")],
    )
    r = validate(p, tenant_context=_tenant(["ISO27001:2022"]))
    return _ok(r.passed, f"violations={r.violations}")


def test_empty_scope_is_permissive():
    """Empty scope = no restriction (fail-open for test contexts)."""
    p = PostureStatusPayload(
        question_type="posture_check", query="q",
        frameworks_scope=[],
        subject_refs=[_iso_ref()],
        postures=[PostureFacet(ref=_iso_ref(), finding="NC")],
    )
    r = validate(p)
    return _ok(r.passed, f"violations={r.violations}")


# ── xfw_bridges scope check ──────────────────────────────────────────

def test_bridges_in_scope_pass():
    b = BridgeRecord(from_ref=_gdpr_ref(), to_ref=_iso_ref())
    p = PostureStatusPayload(
        question_type="posture_check", query="q",
        frameworks_scope=["ISO27001:2022", "GDPR:2016/679"],
        subject_refs=[_gdpr_ref()],
        postures=[PostureFacet(ref=_gdpr_ref(), finding="NC")],
        xfw_bridges=[b],
    )
    r = validate(p)
    return _ok(r.passed and not r.violations)


def test_bridge_out_of_scope_violates():
    # Bridge to a framework not in tenant scope
    b = BridgeRecord(
        from_ref=_gdpr_ref(),
        to_ref=RefRecord(ref="SC-7", framework="SOC2"),
    )
    p = PostureStatusPayload(
        question_type="posture_check", query="q",
        frameworks_scope=["ISO27001:2022", "GDPR:2016/679"],
        subject_refs=[_gdpr_ref()],
        postures=[PostureFacet(ref=_gdpr_ref(), finding="NC")],
        xfw_bridges=[b],
    )
    r = validate(p)
    return _ok(
        not r.passed and any("xfw_bridge" in v for v in r.violations),
        f"violations={r.violations}",
    )


# ── cross_framework variant ──────────────────────────────────────────

def test_cross_framework_empty_bridges_warns():
    p = CrossFrameworkPayload(
        question_type="cross_framework", query="q",
        frameworks_scope=["ISO27001:2022", "GDPR:2016/679"],
        # no subject_refs, no xfw_bridges
    )
    r = validate(p)
    return _ok(
        r.passed and any("no xfw_bridges" in w for w in r.warnings),
        f"passed={r.passed} warnings={r.warnings}",
    )


def test_cross_framework_with_bridges_passes():
    b = BridgeRecord(from_ref=_gdpr_ref(), to_ref=_iso_ref())
    p = CrossFrameworkPayload(
        question_type="cross_framework", query="q",
        frameworks_scope=["ISO27001:2022", "GDPR:2016/679"],
        subject_refs=[_gdpr_ref()],
        primary_posture=PostureFacet(ref=_gdpr_ref(), finding="NC"),
        xfw_bridges=[b],
    )
    r = validate(p)
    return _ok(r.passed and not r.warnings, f"warnings={r.warnings}")


# ── remediation_guide variant ────────────────────────────────────────

def test_remediation_no_gaps_warns():
    p = RemediationGuidePayload(
        question_type="gap_analysis", query="q",
        frameworks_scope=["ISO27001:2022"],
    )
    r = validate(p)
    return _ok(r.passed and any("no gaps" in w for w in r.warnings))


def test_remediation_gap_out_of_scope_violates():
    p = RemediationGuidePayload(
        question_type="gap_analysis", query="q",
        frameworks_scope=["GDPR:2016/679"],
        nc_gaps=[GapEntry(ref=_iso_ref(), severity="NC")],
    )
    r = validate(p)
    return _ok(
        not r.passed and any("gap.ref" in v for v in r.violations),
        f"violations={r.violations}",
    )


# ── document_content variant ─────────────────────────────────────────

def test_document_content_no_docs_warns():
    p = DocumentContentPayload(
        question_type="document_content", query="q",
        frameworks_scope=["ISO27001:2022"],
    )
    r = validate(p)
    return _ok(r.passed and any("no documents" in w for w in r.warnings))


# ── standard_knowledge variant ───────────────────────────────────────

def test_standard_knowledge_empty_warns():
    p = StandardKnowledgePayload(
        question_type="definition", query="q",
        frameworks_scope=["ISO27001:2022"],
    )
    r = validate(p)
    return _ok(r.passed and any("empty prose" in w for w in r.warnings))


def test_standard_knowledge_with_acronym_passes():
    p = StandardKnowledgePayload(
        question_type="definition", query="q",
        frameworks_scope=["ISO27001:2022"],
        acronym="OFI", expansion="Opportunity for Improvement",
    )
    r = validate(p)
    return _ok(r.passed and not r.warnings)


# ── freeform variant ────────────────────────────────────────────────

def test_freeform_reason_becomes_warning():
    p = FreeformPayload(
        question_type="unknown", query="q",
        reason_fallback="no dedicated builder",
    )
    r = validate(p)
    return _ok(
        r.passed and any("no dedicated builder" in w for w in r.warnings),
        f"warnings={r.warnings}",
    )


TESTS = [
    test_valid_iso_ref_passes,
    test_out_of_scope_ref_violates,
    test_scope_pulled_from_tenant_context,
    test_empty_scope_is_permissive,
    test_bridges_in_scope_pass,
    test_bridge_out_of_scope_violates,
    test_cross_framework_empty_bridges_warns,
    test_cross_framework_with_bridges_passes,
    test_remediation_no_gaps_warns,
    test_remediation_gap_out_of_scope_violates,
    test_document_content_no_docs_warns,
    test_standard_knowledge_empty_warns,
    test_standard_knowledge_with_acronym_passes,
    test_freeform_reason_becomes_warning,
]


def main():
    print("─" * 70)
    print("  Ship 2.0 — validator unit tests")
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
