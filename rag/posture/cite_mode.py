"""
rag/posture/cite_mode.py — cite-mode predicates + helpers.

Single source of truth for "is this evidence_type cite-acceptable?" —
the question that drives whether the UI offers the Cite lane on a
leaf, and whether the engine should consider external_evidence_source
rows for it.

Authored-artefact evidence_types (policy / procedure / scope_note /
agreement_template / classification_scheme / charter / etc.) are
NOT cite-acceptable — they live in ArionComply as documents the
tenant authored. Operational-data evidence_types (register / record /
log / inventory / matrix / baseline) typically live in source systems
(Odoo HR, Okta, ServiceNow, OneTrust) and ARE cite-acceptable.

Allowlist + suffix design: an explicit set for known operational
types plus a suffix predicate for the long tail. New evidence_types
added during curation default to NOT cite-acceptable; cite mode is
opted-in deliberately per type.

See [[product-principle-evidence-stored-vs-cited]] for the full
product framing.
"""
from __future__ import annotations


# Operational evidence_types that live in source systems. Tenants
# typically cite these to Odoo HR / Okta / ServiceNow / OneTrust /
# DPO software / IRM tools / etc.
_CITE_ACCEPTABLE_EXACT: frozenset[str] = frozenset({
    # Registers + inventories
    "register",
    "asset_register",
    "contact_register",
    "lawful_basis_register",
    "data_flow_inventory",
    "records_of_processing",

    # Records — per-event entries from workflow / IRM / audit tools
    "review_record",
    "revocation_record",
    "communication_record",
    "monitoring_record",
    "approval_record",
    "audit_record",
    "configuration_record",
    "publication_record",
    "change_record",
    "discovery_record",
    "risk_assessment_record",
    "risk_treatment_record",
    "decision_record",

    # Logs
    "test_log",

    # Matrices — HR / PM tools
    "responsibility_matrix",
    "segregation_matrix",

    # Configuration — MDM / posture tools
    "configuration_baseline",

    # Approvals (workflow tools)
    "approval",

    # GDPR / privacy artefacts in DPO software
    "breach_notification",
    "dsar_response",

    # External-auditor deliverables
    "audit_report",

    # LMS-hosted training programmes
    "training_programme",

    # Risk-management artefacts (often in GRC tools)
    "risk_assessment",
})

# Suffix fallback for evidence_types not in the exact set.
# Authored-artefact types (policy, procedure, scope_note,
# statement_of_applicability, charter, agreement_template, etc.)
# don't end in any of these — they stay storage-only.
_CITE_ACCEPTABLE_SUFFIXES: tuple[str, ...] = (
    "_register",
    "_record",
    "_log",
    "_inventory",
    "_matrix",
    "_baseline",
)


def is_cite_acceptable(evidence_type: str) -> bool:
    """True when this evidence_type can be cited from an external system.

    Returns False for authored-artefact types (policy, procedure,
    scope_note, agreement_template, classification_scheme, etc.)
    that naturally live in ArionComply as uploaded documents.

    Returns True for operational-data types (register, record, log,
    inventory, matrix, baseline) that typically live in source
    systems.
    """
    if not evidence_type:
        return False
    et = evidence_type.strip().lower()
    if et in _CITE_ACCEPTABLE_EXACT:
        return True
    return any(et.endswith(s) for s in _CITE_ACCEPTABLE_SUFFIXES)


# ── Stale handling ──────────────────────────────────────────────────────────

def is_cite_fresh(last_verified_at, cadence_days: int, now=None) -> bool:
    """A cite is FRESH when last_verified_at is within (cadence_days +
    grace_days). Engine treats fresh cites as evidence-present.

    Grace formula: min(cadence_days * 10%, 30 days). So a 365-day
    cadence gets ~36 days of grace; a 30-day cadence gets 3 days.
    """
    if last_verified_at is None:
        return False
    from datetime import datetime, timezone, timedelta
    if now is None:
        now = datetime.now(timezone.utc)
    grace = min(int(cadence_days * 0.1), 30)
    deadline = last_verified_at + timedelta(days=cadence_days + grace)
    return now <= deadline


def next_review_due(last_verified_at, cadence_days: int):
    """Compute next_review_due (the YELLOW threshold — past this date,
    cite enters its grace period, after which it's stale/RED).

    Returns None when last_verified_at is None (cite has never been
    verified — still fresh by default until first verification clock
    starts? Decision: NO — unverified cites are not fresh. Engine
    won't count them until first verify.)
    """
    if last_verified_at is None:
        return None
    from datetime import timedelta
    return last_verified_at + timedelta(days=cadence_days)
