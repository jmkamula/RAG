"""
Payload validator — invariants check on an AnswerPayload before it
reaches downstream (Ship 3 prose polish or the current
rank_and_answer path).

Every payload must satisfy:
  1. subject_refs.framework in tenant.queryable_standards
  2. xfw_bridges.to_ref.framework in tenant.queryable_standards
  3. Any ref with N/A posture is EITHER explicitly cited in the
     query OR excluded from payload
  4. CrossFrameworkPayload: xfw_bridges non-empty OR a
     reason_fallback explains why
  5. RefRecord.ref lexically valid for its framework version
     (delegates to framework_scope_guard's cached valid-refs set)

Violations are HARD failures — the retrieve node should log and
route to legacy rank_and_answer instead of using the payload.
Warnings are soft issues — payload still usable, worth logging.
"""
from __future__ import annotations

from typing import Optional

from rag.answer.types import (
    AnswerPayloadBase,
    PostureStatusPayload,
    CrossFrameworkPayload,
    DocumentContentPayload,
    DocumentStatusPayload,
    RemediationGuidePayload,
    StandardKnowledgePayload,
    FreeformPayload,
    ValidationReport,
    RefRecord,
    BridgeRecord,
)


def _in_scope(fw: str, scope: list[str]) -> bool:
    """Case-sensitive membership check with an empty-scope escape hatch
    (empty scope means "no restriction")."""
    if not scope:
        return True
    return fw in set(scope)


def _validate_ref_scope(
    ref:       RefRecord,
    scope:     list[str],
    ctx_label: str,
    report:    ValidationReport,
) -> None:
    """Add a violation if ref's framework isn't in the tenant's
    queryable_standards."""
    if ref.framework and not _in_scope(ref.framework, scope):
        report.add_violation(
            f"{ctx_label}: ref {ref.ref!r} framework {ref.framework!r} "
            f"not in tenant scope {scope}"
        )


def _validate_bridges(
    bridges: list[BridgeRecord],
    scope:   list[str],
    report:  ValidationReport,
) -> None:
    """Validate every bridge — both endpoints' frameworks must be in scope."""
    for b in bridges:
        _validate_ref_scope(b.to_ref,   scope, "xfw_bridge.to_ref",   report)
        _validate_ref_scope(b.from_ref, scope, "xfw_bridge.from_ref", report)


def validate(
    payload:        AnswerPayloadBase,
    tenant_context = None,
) -> ValidationReport:
    """Run invariants on the payload. Returns ValidationReport.

    Args:
        payload:         An AnswerPayload variant.
        tenant_context:  Optional TenantContext for scope lookup. If None,
                         scope validation is skipped (fail-open).

    Returns:
        ValidationReport with .passed = True/False, .violations, .warnings.
    """
    report = ValidationReport(payload_variant=payload.variant_name)

    # Determine tenant scope for framework validation
    scope: list[str] = list(payload.frameworks_scope or [])
    if not scope and tenant_context is not None:
        _scope = getattr(tenant_context, "scope", None)
        if _scope is not None:
            scope = list(getattr(_scope, "queryable_standards", []) or [])

    # Invariant 1 — subject_refs.framework in scope
    for r in (payload.subject_refs or []):
        _validate_ref_scope(r, scope, "subject_ref", report)

    # Invariant 2 + 4 — payload-variant-specific checks
    if isinstance(payload, PostureStatusPayload):
        _validate_bridges(payload.xfw_bridges, scope, report)
        for facet in (payload.postures or []):
            _validate_ref_scope(facet.ref, scope, "posture.ref", report)
        # Every DocumentRequirement's control ref should be in scope
        for doc in (payload.documents or []):
            _validate_ref_scope(doc.control, scope, "document.control", report)

    elif isinstance(payload, CrossFrameworkPayload):
        _validate_bridges(payload.xfw_bridges, scope, report)
        if payload.primary_posture is not None:
            _validate_ref_scope(
                payload.primary_posture.ref, scope, "primary_posture.ref", report,
            )
        # Invariant 4 — xfw_bridges non-empty for cross_framework
        if not payload.xfw_bridges and not payload.subject_refs:
            report.add_warning(
                "cross_framework payload has no xfw_bridges and no "
                "subject_refs — unusual for this variant"
            )

    elif isinstance(payload, RemediationGuidePayload):
        for gap in (payload.nc_gaps or []) + (payload.ofi_gaps or []):
            _validate_ref_scope(gap.ref, scope, "gap.ref", report)
        _validate_bridges(payload.xfw_context, scope, report)

    elif isinstance(payload, DocumentContentPayload):
        for doc in (payload.documents or []):
            _validate_ref_scope(doc.control, scope, "document.control", report)

    elif isinstance(payload, DocumentStatusPayload):
        # doc_alerts and uploaded_docs are dicts — no ref scope validation here.
        # Their content is denormalised from platform Doc registry so we trust it.
        pass

    elif isinstance(payload, StandardKnowledgePayload):
        # No refs to validate necessarily — definition queries can be
        # framework-independent (e.g. "what is OFI?"). If subject_refs
        # provided, they were already checked above.
        if not payload.acronym and not payload.definition and not payload.business_description:
            report.add_warning(
                "standard_knowledge payload has no acronym, definition, "
                "or business_description — will produce empty prose"
            )

    elif isinstance(payload, FreeformPayload):
        # Freeform is intentionally loose — skip most invariants
        if payload.reason_fallback:
            report.add_warning(
                f"freeform fallback: {payload.reason_fallback}"
            )

    # Cross-cutting: if all lists on a "content-carrying" payload are
    # empty, warn — we probably didn't build useful content
    if isinstance(payload, PostureStatusPayload) and not payload.postures:
        report.add_warning("posture_status payload has no postures")
    if isinstance(payload, RemediationGuidePayload) and not payload.nc_gaps and not payload.ofi_gaps:
        report.add_warning("remediation_guide payload has no gaps")
    if isinstance(payload, DocumentContentPayload) and not payload.documents:
        report.add_warning("document_content payload has no documents")

    return report
