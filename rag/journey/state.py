"""
rag/journey/state.py — compute the tenant onboarding journey state.

Anchor the tenant on the **next best action** based on:
  - Phase (Profile → Foundation → Operational → Annual)
  - Per-leaf MUST completion %
  - Anchor-template priority (the 20 hand-refined v2 templates)
  - Cascade value (leaves with many cross-references go first)
  - Quick wins (smaller MUSTs first within a tier)

Built on top of templates (db/templates) + posture data
(document_findings + tenant_must_overrides). The wizard's data sources
are intentionally read-only — completing actions still goes through
the normal upload + approval pipeline.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional


logger = logging.getLogger(__name__)


# The hand-refined anchor leaves (template_version=2). Order encodes the
# recommended foundation sequence. Tenants tackling Phase 1 work through
# these first. 20 ISO 27001/GDPR foundation anchors + 5 ISO 27701 privacy
# anchors interleaved where they naturally augment their 27001 sibling.
_ANCHOR_LEAVES: list[str] = [
    # ISMS foundation (clauses 4-10)
    "req:4.3:isms_scope",
    "req:5.2:information_security_policy",
    "req:5.3:isms_roles_authorities",
    "req:6.1.2:risk_assessment",
    "req:6.1.3:risk_treatment_plan",
    "req:6.1.3:statement_of_applicability",
    "req:7.5:document_control_policy",
    "req:9.2:internal_audit_programme",
    "req:9.3:management_review",
    "req:10.1:improvement_action_register",
    # Annex A operational
    "req:A.5.1:isp_policy",
    "req:A.5.9:asset_inventory",
    "req:A.5.15:access_control_policy",
    # ISO 27701 PIMS foundation — sits alongside the ISMS baseline
    "req:A.7.2.1:purpose_procedure",              # what purposes we process PII for
    "req:A.7.2.5:pia_procedure",                  # DPIA program (bridges Art.35)
    "req:A.5.18:access_rights_procedure",
    "req:A.7.3.6:acr_procedure",                  # subject rights ACR (bridges Art.15/16/17)
    "req:A.5.19:supplier_risk_procedure",
    "req:A.7.2.6:processor_contract_procedure",   # DPAs (bridges Art.28)
    "req:A.5.24:incident_response_procedure",
    "req:A.5.29:information_security_during_disruption",
    "req:A.6.3:security_awareness_programme",
    # Records + transfers foundation
    "req:A.7.2.8:pii_processing_ropa",            # controller RoPA (bridges Art.30)
    "req:Art.30:records_of_processing",
    "req:A.7.5.1:transfer_basis_procedure",       # Chap V basis
    # GDPR closing
    "req:Art.32:risk_appropriate_measures_register",
]


@dataclass
class LeafState:
    leaf_id:        str
    control_ref:    str
    standard_id:    str
    evidence_type:  str
    title:          str
    must_total:     int
    must_na:        int       # MUSTs marked N/A via tenant_must_overrides
    must_satisfied: int       # satisfied by an active+approved finding
    completion_pct: float     # (satisfied / max(1, total - na))
    is_anchor:      bool
    template_version: int     # 1 = auto-scaffold, 2 = hand-refined
    has_template:   bool      # does a row exist in the templates table?


@dataclass
class JourneyRecommendation:
    leaf_id:           str
    control_ref:       str
    title:             str
    why:               str                # human-readable reason
    must_total:        int
    must_satisfied:    int
    completion_pct:    float
    is_anchor:         bool
    template_url:      str
    download_url:      str


@dataclass
class JourneyState:
    tenant_id:          str

    # Phase
    phase:              str                # 'profile' | 'foundation' | 'operational' | 'annual'
    phase_name:         str                # human-readable
    phase_message:      str                # actionable framing

    # Profile
    profile_complete:   bool

    # Aggregate progress
    total_leaves:       int                # in-scope leaves
    leaves_complete:    int                # 100% complete
    posture_pct:        float              # weighted by MUSTs (satisfied / (total - na))

    # Anchor progress (Foundation)
    anchors_total:      int                # always 20
    anchors_complete:   int

    # Operational progress
    operational_total:  int                # non-anchor leaves
    operational_complete: int

    # Next-action queue (top 5)
    next_actions:       list[JourneyRecommendation] = field(default_factory=list)

    # Optional details
    annual_reviews_due: list[str]          = field(default_factory=list)

    # Full anchor list with per-anchor completion — surfaced on the
    # Get Started mode so tenants can browse the whole foundation
    # sequence + pick which anchor to work on next. Each dict shape:
    #   {control_ref, leaf_id, title, evidence_type, is_tabular,
    #    must_total, must_satisfied, completion_pct, download_urls,
    #    dashboard_url}
    # 2026-07-03 (Tier-4 companion — see [[dejargonize-ux-pass...]]).
    foundation_anchors: list[dict]         = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Phase determination
# ─────────────────────────────────────────────────────────────────────────────

def _determine_phase(
    profile_complete:    bool,
    anchors_complete:    int,
    anchors_total:       int,
    operational_complete: int,
    operational_total:    int,
) -> tuple[str, str, str]:
    """Return (phase, phase_name, phase_message)."""
    if not profile_complete:
        return (
            "profile",
            "Phase 0 — Profile",
            "Complete your organisation profile (5 min). This sets your "
            "in-scope obligations so you don't see controls that don't "
            "apply to you.",
        )
    if anchors_complete < anchors_total:
        remaining = anchors_total - anchors_complete
        return (
            "foundation",
            "Phase 1 — Foundation",
            f"Build the foundation policies + procedures. "
            f"{anchors_complete}/{anchors_total} foundation templates "
            f"complete; {remaining} to go. Each foundation document "
            f"unlocks several dependent controls.",
        )
    if operational_complete < operational_total:
        remaining = operational_total - operational_complete
        return (
            "operational",
            "Phase 2 — Operational",
            f"Build the operational records, registers, and procedures. "
            f"{operational_complete}/{operational_total} operational "
            f"templates complete; {remaining} to go.",
        )
    return (
        "annual",
        "Phase 3 — Annual Cycle",
        "All templates filled. Maintain compliance through periodic "
        "reviews driven by freshness cycles.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Bulk data fetchers
# ─────────────────────────────────────────────────────────────────────────────

def _fetch_all_leaves(neo4j_driver) -> list[dict]:
    """Pull every curated EvidenceRequirement + its MUST item ids.
    Single Cypher round-trip.
    """
    with neo4j_driver.session() as s:
        rows = s.run("""
            MATCH (er:EvidenceRequirement)
            OPTIONAL MATCH (er)-[:MUST_CONTAIN]->(item:ChecklistItem)
            RETURN er.id           AS leaf_id,
                   er.control_ref  AS control_ref,
                   er.standard_id  AS standard_id,
                   er.evidence_type AS evidence_type,
                   er.title        AS title,
                   collect(item.id) AS must_ids
        """).data()
    return rows


def _fetch_tenant_na_musts(pg_conn, tenant_id: str) -> set[str]:
    """All must_ids the tenant has marked applies=FALSE."""
    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        cur.execute("""
            SELECT must_id FROM tenant_must_overrides
             WHERE tenant_id = %s::uuid AND applies = FALSE
        """, (tenant_id,))
        return {r[0] for r in cur.fetchall()}


def _fetch_satisfied_must_ids(pg_conn, tenant_id: str) -> set[str]:
    """All checklist_item_ids satisfied for this tenant.

    Reads from posture_must_verdicts (SSoT) via the canonical reader
    (2026-08-11). Prior implementation was a direct document_findings
    query. Same semantics — engine's per-MUST recognition considers
    approved + active + present findings plus fresh cite-mode entries —
    but consumers converge on one source now.
    """
    from rag.posture.must_verdicts import read_satisfied_must_ids
    return read_satisfied_must_ids(pg_conn, tenant_id)


def _fetch_template_index(pg_conn) -> dict[str, dict]:
    """leaf_id → {template_version, must_count}."""
    with pg_conn.cursor() as cur:
        cur.execute("SELECT leaf_id, template_version, must_count FROM templates")
        return {
            r[0]: {"template_version": r[1], "must_count": r[2]}
            for r in cur.fetchall()
        }


def _is_profile_complete(pg_conn, tenant_id: str) -> bool:
    """ClientFacts marker — at minimum the personal-data + jurisdiction
    flags should be set deliberately."""
    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        cur.execute("""
            SELECT processes_personal_data, eu_data_subjects, uk_data_subjects,
                   role_controller, role_processor
              FROM client_facts
             WHERE tenant_id = %s::uuid
        """, (tenant_id,))
        row = cur.fetchone()
        if row is None:
            return False
        ppd, eu, uk, ctrl, proc = row
        # Profile considered "complete" when:
        #   - Personal-data flag set deliberately (T or F is fine; row exists)
        #   - At least one role set (controller / processor)
        # This is a minimum bar; tenants can refine ClientFacts further.
        return (ppd is not None) and (ctrl or proc)


# ─────────────────────────────────────────────────────────────────────────────
# Recommendation ranking
# ─────────────────────────────────────────────────────────────────────────────

def _pick_next_actions(
    leaf_states: list[LeafState],
    phase:       str,
    limit:       int = 5,
) -> list[JourneyRecommendation]:
    """Pick the top N recommended next actions for the current phase.

    Ranking rules per phase:
      - Foundation: anchor leaves only, in the documented anchor order,
        incomplete ones (< 100%) first
      - Operational: non-anchor leaves with a template; smaller MUST
        counts first (quick wins), then alphabetical by control_ref
      - Annual: leaves with completion=100% (skip — they're done) +
        leaves with freshness_days approaching (deferred to v2)
      - Profile: empty list (the recommendation is the profile itself)
    """
    if phase == "profile":
        return []

    # Build leaf_id → state map for quick lookup
    by_id = {ls.leaf_id: ls for ls in leaf_states}

    if phase == "foundation":
        # Walk the documented anchor order, return first N incomplete
        out = []
        for leaf_id in _ANCHOR_LEAVES:
            ls = by_id.get(leaf_id)
            if ls is None or ls.completion_pct >= 100.0:
                continue
            out.append(_to_recommendation(ls,
                why=f"Foundation document — step "
                    f"{_ANCHOR_LEAVES.index(leaf_id) + 1} "
                    f"in the recommended onboarding sequence."))
            if len(out) >= limit:
                break
        return out

    if phase == "operational":
        # Non-anchor + has-template + incomplete; quick wins first
        candidates = [
            ls for ls in leaf_states
            if not ls.is_anchor
            and ls.has_template
            and ls.completion_pct < 100.0
        ]
        candidates.sort(key=lambda ls: (ls.must_total, ls.control_ref))
        out = []
        for ls in candidates[:limit]:
            unsat = ls.must_total - ls.must_satisfied - ls.must_na
            out.append(_to_recommendation(ls,
                why=f"Operational document — {unsat} required "
                    f"element{'s' if unsat != 1 else ''} still to "
                    f"fill in. Smaller documents first build momentum."))
        return out

    # phase == 'annual'
    return []  # freshness-driven; v2


def _to_recommendation(ls: LeafState, why: str) -> JourneyRecommendation:
    return JourneyRecommendation(
        leaf_id        = ls.leaf_id,
        control_ref    = ls.control_ref,
        title          = ls.title,
        why            = why,
        must_total     = ls.must_total,
        must_satisfied = ls.must_satisfied,
        completion_pct = ls.completion_pct,
        is_anchor      = ls.is_anchor,
        template_url   = f"/api/v1/templates/{ls.leaf_id}",
        download_url   = f"/api/v1/templates/{ls.leaf_id}/download",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def compute_journey_state(
    pg_conn,
    neo4j_driver,
    tenant_id: str,
) -> JourneyState:
    """Compute the full journey state for one tenant. Reads-only."""
    anchor_set = set(_ANCHOR_LEAVES)

    # Bulk fetches — three round-trips total
    all_leaves     = _fetch_all_leaves(neo4j_driver)
    na_must_ids    = _fetch_tenant_na_musts(pg_conn, tenant_id)
    satisfied_ids  = _fetch_satisfied_must_ids(pg_conn, tenant_id)
    template_index = _fetch_template_index(pg_conn)

    # Build per-leaf state
    leaf_states: list[LeafState] = []
    for row in all_leaves:
        must_ids = [m for m in (row.get("must_ids") or []) if m]
        must_total     = len(must_ids)
        must_na        = sum(1 for m in must_ids if m in na_must_ids)
        must_satisfied = sum(1 for m in must_ids if m in satisfied_ids and m not in na_must_ids)
        denom          = max(1, must_total - must_na)
        completion_pct = round(100.0 * must_satisfied / denom, 1) if must_total > must_na else 100.0
        # Edge: if all MUSTs N/A, vacuously satisfied
        if must_total > 0 and must_na == must_total:
            completion_pct = 100.0
            must_satisfied = 0

        tinfo = template_index.get(row["leaf_id"], {})
        leaf_states.append(LeafState(
            leaf_id          = row["leaf_id"],
            control_ref      = row.get("control_ref") or "",
            standard_id      = row.get("standard_id") or "",
            evidence_type    = row.get("evidence_type") or "",
            title            = row.get("title") or row["leaf_id"],
            must_total       = must_total,
            must_na          = must_na,
            must_satisfied   = must_satisfied,
            completion_pct   = completion_pct,
            is_anchor        = row["leaf_id"] in anchor_set,
            template_version = tinfo.get("template_version", 0),
            has_template     = bool(tinfo),
        ))

    # Aggregates
    anchor_states      = [ls for ls in leaf_states if ls.is_anchor]
    operational_states = [ls for ls in leaf_states if not ls.is_anchor and ls.has_template]

    anchors_total       = len(_ANCHOR_LEAVES)
    anchors_complete    = sum(1 for ls in anchor_states if ls.completion_pct >= 100.0)
    operational_total   = len(operational_states)
    operational_complete = sum(1 for ls in operational_states if ls.completion_pct >= 100.0)

    total_leaves      = len(leaf_states)
    leaves_complete   = sum(1 for ls in leaf_states if ls.completion_pct >= 100.0)

    # Posture % — total satisfied MUSTs / total (in-scope) MUSTs
    total_must     = sum(ls.must_total - ls.must_na for ls in leaf_states)
    total_satis    = sum(ls.must_satisfied for ls in leaf_states)
    posture_pct    = round(100.0 * total_satis / max(1, total_must), 1)

    # Profile + phase
    profile_complete = _is_profile_complete(pg_conn, tenant_id)
    phase, phase_name, phase_message = _determine_phase(
        profile_complete,
        anchors_complete, anchors_total,
        operational_complete, operational_total,
    )

    next_actions = _pick_next_actions(leaf_states, phase)

    # Foundation anchor rollup — full ordered list with per-anchor
    # completion + shape hint (tabular vs narrative) so the Get
    # Started mode can render the whole sequence with the right
    # download button per shape. Skipped anchors (leaf_id not in
    # the catalog / no template) still surface with completion_pct
    # so the tenant sees the whole path.
    from rag.templates.answer_footer import _is_tabular
    foundation_anchors: list[dict] = []
    by_leaf_id = {ls.leaf_id: ls for ls in anchor_states}
    for seq_idx, anchor_leaf_id in enumerate(_ANCHOR_LEAVES, start=1):
        ls = by_leaf_id.get(anchor_leaf_id)
        if ls is None:
            continue
        is_tabular = _is_tabular(ls.evidence_type)
        base_url = f"/api/v1/templates/{ls.leaf_id}/download"
        if is_tabular:
            primary_fmt, primary_label = "xlsx", "Excel starter"
        else:
            primary_fmt, primary_label = "docx", "Word starter"
        foundation_anchors.append({
            "sequence":        seq_idx,
            "control_ref":     ls.control_ref,
            "leaf_id":         ls.leaf_id,
            "title":           ls.title,
            "evidence_type":   ls.evidence_type,
            "is_tabular":      is_tabular,
            "must_total":      ls.must_total,
            "must_satisfied":  ls.must_satisfied,
            "completion_pct":  ls.completion_pct,
            "primary_download": {
                "format": primary_fmt,
                "label":  primary_label,
                "url":    f"{base_url}?format={primary_fmt}",
            },
            "alt_downloads": [
                {"format": "md", "label": "Markdown",
                 "url": f"{base_url}?format=md"},
            ],
            "dashboard_url":   f"/#dashboard?control={ls.control_ref}",
        })

    return JourneyState(
        tenant_id            = tenant_id,
        phase                = phase,
        phase_name           = phase_name,
        phase_message        = phase_message,
        profile_complete     = profile_complete,
        total_leaves         = total_leaves,
        leaves_complete      = leaves_complete,
        posture_pct          = posture_pct,
        anchors_total        = anchors_total,
        anchors_complete     = anchors_complete,
        operational_total    = operational_total,
        operational_complete = operational_complete,
        next_actions         = next_actions,
        foundation_anchors   = foundation_anchors,
    )
