"""Per-MUST advisory generation.

Translates the engine's per-leaf verdicts into actionable guidance for the
tenant: which fulfilment criteria (MUSTs) are covered, which are missing,
and what to upload/produce to close the gap.

Deterministic compose (no LLM). The data path:
  evaluate_one_control() → ControlVerdict with leaves[].items_recognised/unrecognised
  + Neo4j ChecklistItem.text per MUST (already in the verdict's leaf metadata
    via items_recognised/unrecognised, which are TEXTS not ids)
  + evidence_type per leaf → upload-hint template

Returns markdown.

Conditions for advisory to render:
  - Control's engine verdict is NC or OFI (Comply/N/A → no advisory)
  - At least one MUST is unmet across the control's leaves

Hook point: appended deterministically to chat answers for posture_check
queries that identify exactly one control.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

from .engine_runner import evaluate_one_control

logger = logging.getLogger(__name__)


# Lazy neo4j driver — created once per process the first time the advisory
# hook fires (chat doesn't already carry the driver in state). Cached on
# the module so subsequent calls reuse the connection.
_DRIVER = None


def _get_neo_driver():
    """Lazy neo4j driver creation. Returns None on any failure so the
    advisory hook silently no-ops rather than blocking the chat answer."""
    global _DRIVER
    if _DRIVER is not None:
        return _DRIVER
    try:
        from neo4j import GraphDatabase
        uri  = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        pw   = os.getenv("NEO4J_PASSWORD")
        if not (uri and user and pw):
            return None
        _DRIVER = GraphDatabase.driver(uri, auth=(user, pw))
        return _DRIVER
    except Exception as e:
        logger.warning("advisory: neo4j driver creation failed: %s", e)
        return None


# ── Upload-hint templates per evidence_type ──────────────────────────────────
#
# Each hint is a short action sentence pegged to the evidence shape. The
# tenant reading this sees: "produce X to satisfy this leaf". Phrased as
# concrete acts (update / upload / produce / document) rather than
# abstract recommendations.

_UPLOAD_HINTS: dict[str, str] = {
    "policy":
        "Update the policy document to articulate each missing element.",
    "procedure":
        "Document each missing step in the procedure document.",
    "matrix":
        "Update the controls matrix to cover each missing element.",
    "directive":
        "Update the management directive to articulate each missing element.",
    "manual":
        "Update the manual to articulate each missing element.",
    "isms_scope":
        "Update the ISMS scope statement to cover each missing element.",
    "statement_of_applicability":
        "Update the Statement of Applicability to cover each missing element.",

    "register":
        "Add or extend a register (spreadsheet / table) with a column or row per missing element.",
    "asset_register":
        "Add or extend the asset register with a column per missing element.",
    "contact_register":
        "Add or extend the contact register with a column per missing element.",
    "schedule_register":
        "Add or extend the schedule register with a column per missing element.",
    "nonconformity_register":
        "Add or extend the nonconformity register with a column per missing element.",
    "operating_procedures_register":
        "Add or extend the operating procedures register with a column per missing element.",
    "lawful_basis_register":
        "Add or extend the lawful basis register with a column per missing element.",

    "review_record":
        "Conduct a review and produce a review record covering each missing element.",
    "audit_report":
        "Conduct an audit and produce a report covering each missing element.",
    "management_review_minutes":
        "Capture management review minutes covering each missing input.",

    "approval":
        "Produce an approval record with the missing signature / scope details.",
    "approval_record":
        "Produce an approval record with the missing signature / scope details.",

    "revocation_record":
        "Capture per-event revocation records with fields for each missing element.",
    "disposal_record":
        "Capture per-disposal records with fields for each missing element.",
    "closure_record":
        "Capture per-closure records with fields for each missing element.",
    "exercise_record":
        "Capture per-exercise records with fields for each missing element.",
    "activation_record":
        "Capture per-activation records with fields for each missing element.",
    "non_return_record":
        "Capture per-non-return records with fields for each missing element.",
    "return_record":
        "Capture per-return records with fields for each missing element.",
    "application_record":
        "Capture per-application records with fields for each missing element.",
    "discovery_record":
        "Capture per-discovery records with fields for each missing element.",
    "monitoring_record":
        "Capture per-event monitoring records with fields for each missing element.",
    "communication_record":
        "Capture communication records covering each missing element (date, audience, channel).",
    "communication_evidence":
        "Capture communication evidence covering each missing element.",
    "configuration_record":
        "Capture per-system configuration records with fields for each missing element.",
    "risk_assessment_record":
        "Capture risk assessment records covering each missing element.",
    "risk_treatment_record":
        "Capture risk treatment records covering each missing element.",
    "breach_notification":
        "Capture breach notifications covering each missing required content element.",
    "intake_process":
        "Document the intake process covering each missing trigger / path.",

    "scope_note":
        "Add a scope-note section enumerating the missing elements.",
    "agreement_template":
        "Update the agreement template to include clauses for each missing element.",
    "configuration_baseline":
        "Update the configuration baseline to document each missing setting.",
    "classification_scheme":
        "Update the classification scheme to define each missing level / dimension.",
    "responsibility_matrix":
        "Update the responsibility matrix to allocate each missing role.",
    "segregation_matrix":
        "Update the segregation matrix to capture each missing conflict pair.",
    "lawful_basis_register":
        "Add or extend the lawful basis register with a column per missing element.",
    "plan":
        "Update the plan to articulate each missing element.",
    "management_directive":
        "Update the management directive to articulate each missing element.",
}

_DEFAULT_HINT = (
    "Produce evidence (document, record, or register) that articulates "
    "each missing element."
)


def _hint_for(evidence_type: str) -> str:
    return _UPLOAD_HINTS.get(evidence_type, _DEFAULT_HINT)


def _humanize_evidence_type(et: str) -> str:
    """Convert evidence_type to display form (underscores → spaces)."""
    return (et or "").replace("_", " ")


# ── Source-of-truth label per standard ───────────────────────────────────────

def _source_label(control_ref: str, standard_id: str) -> str:
    """Best-effort 'see X' citation for the standard the MUSTs derive from."""
    if standard_id.startswith("ISO27001"):
        # ISO 27001 controls draw implementation guidance from ISO 27002.
        # ISMS clauses (4-10) are in ISO 27001 directly.
        if control_ref and control_ref.startswith("A."):
            # Strip "A.": A.5.15 → 5.15
            sub = control_ref[2:]
            return f"Source: ISO/IEC 27002:2022 §{sub} implementation guidance."
        return f"Source: ISO/IEC 27001:2022 clause {control_ref}."
    if standard_id.startswith("GDPR"):
        return f"Source: GDPR {control_ref} (EU Regulation 2016/679) + EDPB guidance."
    return f"Source: {standard_id} {control_ref}."


# ── Main entry point ─────────────────────────────────────────────────────────

def build_per_must_advisory(
    pg_conn,
    tenant_id:    str,
    control_ref:  str,
    standard_id:  str = "ISO27001:2022",
    neo4j_driver = None,
) -> str:
    """Return markdown advisory for the given control, or "" if no advisory
    is warranted (Comply, N/A, no curated multi-leaf, or all MUSTs satisfied).

    Cost: one evaluate_one_control() call (Neo4j + Postgres). Acceptable on
    the chat path for posture_check queries that identify a single control.

    If neo4j_driver is None, lazily creates one from env vars. Returns ""
    on any failure (chat path must never break on advisory issues).
    """
    if not control_ref:
        return ""

    if neo4j_driver is None:
        neo4j_driver = _get_neo_driver()
        if neo4j_driver is None:
            return ""

    full_id = f"{standard_id}:{control_ref}"
    try:
        verdict = evaluate_one_control(pg_conn, neo4j_driver, tenant_id, full_id)
    except Exception as e:
        logger.warning("advisory: evaluate_one_control failed for %s: %s", full_id, e)
        return ""
    if verdict is None or not verdict.leaves:
        return ""

    # Only render advisory if the engine sees NC or OFI. Comply / N/A
    # control surfaces don't need advisory.
    posture = (verdict.posture or "").upper()
    if posture not in ("NC", "OFI"):
        return ""

    # Per-leaf sections
    leaf_sections: list[str] = []
    total_missing = 0

    for leaf in verdict.leaves:
        unrec = list(leaf.items_unrecognised or [])
        rec   = list(leaf.items_recognised or [])
        if not unrec:
            # Leaf fully satisfied; show as covered, no action needed
            continue
        total_missing += len(unrec)

        et_h = _humanize_evidence_type(leaf.evidence_type)
        leaf_ref_short = leaf.leaf_id.split(":")[-1].replace("_", " ")
        n_total = len(rec) + len(unrec)
        n_have  = len(rec)
        header  = (
            f"  - **{leaf_ref_short}** ({et_h}) — "
            f"{n_have}/{n_total} elements covered."
        )
        lines = [header]

        if rec:
            have_str = "; ".join(t[:80] for t in rec[:6])
            if len(rec) > 6:
                have_str += f"; (+{len(rec) - 6} more)"
            lines.append(f"    Have: {have_str}.")

        # Missing items (first N, then "+ M more" if very long)
        miss_show = unrec[:10]
        if len(unrec) > 10:
            miss_tail = f" (+{len(unrec) - 10} more)"
        else:
            miss_tail = ""

        lines.append("    Still needed:")
        for it in miss_show:
            lines.append(f"      - {it}")
        if miss_tail:
            lines.append(f"      - …{miss_tail}")

        lines.append(f"    To address: {_hint_for(leaf.evidence_type)}")
        leaf_sections.append("\n".join(lines))

    if not leaf_sections:
        return ""

    n_leaves = len(verdict.leaves)
    n_satisfied = sum(1 for l in verdict.leaves if not (l.items_unrecognised or []))
    n_partial   = sum(1 for l in verdict.leaves
                       if (l.items_unrecognised or []) and (l.items_recognised or []))

    header_line = (
        f"↳ **How to advance {control_ref}** "
        f"(currently {posture}; "
        f"{n_satisfied} of {n_leaves} leaves satisfied, {n_partial} partial)"
    )

    return (
        "\n\n"
        + header_line
        + "\n\n"
        + "\n\n".join(leaf_sections)
        + "\n\n"
        + _source_label(control_ref, standard_id)
    )
