"""
ArionComply — Evidence Requirements

Defines what evidence is required per control and what each artifact must
contain. Three trigger types:
  universal     → required for every client in scope
  profile_fact  → required when a client fact is true
  operational   → required when an event occurs

Each EvidenceRequirement links upward to a FulfilmentSpec (created by the
loader, one spec per RequirementNode) and downward to ChecklistItems via
MUST_CONTAIN / SHOULD_CONTAIN.

This is standards knowledge — shared across all tenants, version-controlled.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ChecklistItem:
    id:           str    # unique: "item:{control_ref}:{slug}"
    text:         str    # what to look for in the document
    category:     str    # "must" | "should"
    gdpr_aligned: bool   # True if this item is required for GDPR alignment specifically
    rationale:    str    # why this item is required


@dataclass
class EvidenceRequirement:
    id:               str          # "req:{control_ref}:{evidence_type_slug}"
    control_ref:      str          # "A.8.24"
    standard_id:      str          # "ISO27001:2022"
    evidence_type:    str          # "policy" | "procedure" | "dpa" | "audit_programme" etc.
    title:            str          # human-readable e.g. "Use of Cryptography Policy"
    trigger_type:     str          # "universal" | "profile_fact" | "operational"
                                   # profile_fact: required when ClientFact is True
                                   # the specific fact is encoded in ClientFacts/ObligationRule
                                   # not stored here — derived from obligation chain
                                   # operational: triggering event lives on the Event side
                                   # as Event.requires_evidence; (:Event)-[:REQUIRES_EVIDENCE]
                                   # ->(:RequirementNode) is the single source of truth.
    description:      str          # why this evidence is required
    freshness_days:   int | None   = None   # max age of latest matching artifact for the
                                            # leaf to count as fresh; None = no freshness
                                            # requirement. Read by leaf_evaluators._check_freshness.
    must_contain:     list[ChecklistItem] = field(default_factory=list)
    should_contain:   list[ChecklistItem] = field(default_factory=list)


# ── Derived specs (cross-control derivation) ──────────────────────────────────
# When a control is satisfied by *implementing* other controls (e.g. GDPR Art.32
# satisfied by ISO 27001 Annex A controls that supply the technical and
# organisational measures), use DerivedSpec instead of EvidenceRequirement.
#
# Three applies_when layers — see [[posture-engine-alignment-plan-2026-05-22]]:
#   DerivedSpec.applies_when   — does the deriving framework require this at all?
#   DerivedFrom.applies_when   — is this specific implementation needed for the tenant?
#   target spec's applies_when — does the source framework think the dep applies?
#
# A control is curated EITHER via EvidenceRequirement(s) OR via a DerivedSpec,
# never both. The loader fails loudly if it finds a conflict.

@dataclass
class DerivedFrom:
    """One DERIVES_FROM edge from a DerivedSpec to a target RequirementNode."""
    target_control_ref:  str               # "A.5.23"
    target_standard_id:  str               # "ISO27001:2022"
    role:                str               # display label, e.g. "cloud_data_protection"
    title:               str = ""          # human-readable, e.g. "Cloud services policy"
    applies_when:        str | None = None # narrower than target spec's applies_when
                                           # when the deriving framework needs broader scope
    scope_items:         list[str] | None = None
                                           # ChecklistItem ids that count toward this
                                           # derivation. None = all items count.


@dataclass
class DerivedSpec:
    """A FulfilmentSpec whose children include DERIVES_FROM edges to other controls.

    spec_id mirrors the loader's convention: 'spec:' + RequirementNode.id, where
    RequirementNode.id = '{standard_id}:{control_ref}'. So Art.32 → 'spec:GDPR:2016/679:Art.32'.
    The loader regenerates this from control_ref + standard_id and ignores the
    field if mis-set; keeping it explicit makes the curation file self-documenting."""
    spec_id:        str
    control_ref:    str
    standard_id:    str
    op:             str = "ALL"            # "ALL" | "ANY" | "AT_LEAST_N"
    n:              int | None = None      # for AT_LEAST_N
    title:          str = ""
    description:    str = ""
    applies_when:   str | None = None
    derives_from:   list[DerivedFrom] = field(default_factory=list)
    direct_evidence: list[EvidenceRequirement] = field(default_factory=list)


# ── Universal documents — ISO 27001 ───────────────────────────────────────────

REQ_ISMS_SCOPE = EvidenceRequirement(
    id            = "req:4.3:isms_scope",
    control_ref   = "4.3",
    standard_id   = "ISO27001:2022",
    evidence_type = "scope_statement",
    title= "ISMS Scope Statement",
    trigger_type  = "universal",
    description   = "Every ISO 27001 organisation must define and document the scope of its ISMS",
    must_contain  = [
        ChecklistItem("item:4.3:boundaries",        "Boundaries of the ISMS defined", "must", False, "Clause 4.3a"),
        ChecklistItem("item:4.3:interfaces",         "Interfaces and dependencies with other organisations", "must", False, "Clause 4.3b"),
        ChecklistItem("item:4.3:exclusions",         "Any exclusions with justification", "must", False, "Clause 4.3c"),
        ChecklistItem("item:4.3:locations",          "Physical and logical locations covered", "must", False, "Scope must be clear"),
        ChecklistItem("item:4.3:products_services",  "Products and services in scope", "must", False, "Scope must be clear"),
    ],
    should_contain= [
        ChecklistItem("item:4.3:stakeholders",  "Key interested parties referenced", "should", False, "Links to 4.2"),
        ChecklistItem("item:4.3:version",       "Version number and review date", "should", False, "Document control"),
    ],
)

REQ_ISMS_POLICY = EvidenceRequirement(
    id            = "req:5.2:information_security_policy",
    control_ref   = "5.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title= "Information Security Policy",
    trigger_type  = "universal",
    description   = "Top management must establish an information security policy appropriate to the organisation",
    must_contain  = [
        ChecklistItem("item:5.2:purpose",        "Appropriate to the purpose of the organisation", "must", False, "Clause 5.2a"),
        ChecklistItem("item:5.2:objectives",     "Information security objectives or framework for setting them", "must", False, "Clause 5.2b"),
        ChecklistItem("item:5.2:commitment_req", "Commitment to satisfy applicable requirements", "must", False, "Clause 5.2c"),
        ChecklistItem("item:5.2:commitment_imp", "Commitment to continual improvement of the ISMS", "must", False, "Clause 5.2d"),
        ChecklistItem("item:5.2:approved",       "Approved by top management", "must", False, "Management commitment"),
        ChecklistItem("item:5.2:communicated",   "Communicated within the organisation", "must", False, "Clause 5.2f"),
    ],
    should_contain= [
        ChecklistItem("item:5.2:available",   "Available to interested parties as appropriate", "should", False, "Clause 5.2g"),
        ChecklistItem("item:5.2:review_date", "Review date or frequency stated", "should", False, "Document control"),
    ],
)

REQ_RISK_ASSESSMENT = EvidenceRequirement(
    id            = "req:6.1.2:risk_assessment",
    control_ref   = "6.1.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "risk_assessment",
    title= "Information Security Risk Assessment",
    trigger_type  = "universal",
    description   = "Organisation must define and apply a risk assessment process",
    must_contain  = [
        ChecklistItem("item:6.1.2:criteria",         "Risk acceptance criteria defined", "must", False, "Clause 6.1.2a"),
        ChecklistItem("item:6.1.2:consistency",      "Consistent and comparable results produced", "must", False, "Clause 6.1.2b"),
        ChecklistItem("item:6.1.2:identification",   "Risks to confidentiality, integrity and availability identified", "must", False, "Clause 6.1.2c"),
        ChecklistItem("item:6.1.2:owners",           "Risk owners identified", "must", False, "Clause 6.1.2c"),
        ChecklistItem("item:6.1.2:consequences",     "Potential consequences analysed", "must", False, "Clause 6.1.2d"),
        ChecklistItem("item:6.1.2:likelihood",       "Realistic likelihood assessed", "must", False, "Clause 6.1.2d"),
        ChecklistItem("item:6.1.2:evaluation",       "Risks evaluated against acceptance criteria", "must", False, "Clause 6.1.2e"),
        ChecklistItem("item:6.1.2:personal_data",    "Personal data processing risks explicitly addressed", "must", True, "GDPR Art.32 alignment"),
    ],
    should_contain= [
        ChecklistItem("item:6.1.2:methodology",  "Methodology documented", "should", False, "Repeatability"),
        ChecklistItem("item:6.1.2:date",         "Assessment date and next review date", "should", False, "Document control"),
    ],
)

REQ_RISK_TREATMENT = EvidenceRequirement(
    id            = "req:6.1.3:risk_treatment_plan",
    control_ref   = "6.1.3",
    standard_id   = "ISO27001:2022",
    evidence_type = "risk_treatment_plan",
    title= "Risk Treatment Plan",
    trigger_type  = "universal",
    description   = "Organisation must select and implement risk treatment options",
    must_contain  = [
        ChecklistItem("item:6.1.3:options",      "Risk treatment options selected for each risk", "must", False, "Clause 6.1.3a"),
        ChecklistItem("item:6.1.3:controls",     "Controls determined", "must", False, "Clause 6.1.3b"),
        ChecklistItem("item:6.1.3:soa_ref",      "Reference to Statement of Applicability", "must", False, "Clause 6.1.3c"),
        ChecklistItem("item:6.1.3:residual",     "Residual risk identified", "must", False, "Clause 6.1.3e"),
        ChecklistItem("item:6.1.3:owners",       "Risk treatment owners identified", "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:6.1.3:timeline", "Target completion dates", "should", False, "Implementation tracking"),
    ],
)

REQ_INTERNAL_AUDIT = EvidenceRequirement(
    id            = "req:9.2:internal_audit_programme",
    control_ref   = "9.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "audit_programme",
    title= "Internal Audit Programme",
    trigger_type  = "universal",
    description   = "Organisation must conduct internal audits at planned intervals",
    must_contain  = [
        ChecklistItem("item:9.2:frequency",      "Audit frequency defined", "must", False, "Clause 9.2a"),
        ChecklistItem("item:9.2:scope",          "Audit scope covering all ISMS processes", "must", False, "Clause 9.2a"),
        ChecklistItem("item:9.2:criteria",       "Audit criteria defined", "must", False, "Clause 9.2b"),
        ChecklistItem("item:9.2:independence",   "Auditor independence and competence requirements", "must", False, "Clause 9.2c"),
        ChecklistItem("item:9.2:reporting",      "Reporting process to management defined", "must", False, "Clause 9.2d"),
        ChecklistItem("item:9.2:corrective",     "Corrective action follow-up process", "must", False, "Clause 9.2e"),
    ],
    should_contain= [
        ChecklistItem("item:9.2:schedule",   "Audit schedule for current period", "should", False, "Planning"),
        ChecklistItem("item:9.2:records",    "Record retention requirements", "should", False, "Evidence"),
    ],
)

REQ_MANAGEMENT_REVIEW = EvidenceRequirement(
    id            = "req:9.3:management_review",
    control_ref   = "9.3",
    standard_id   = "ISO27001:2022",
    evidence_type = "management_review_minutes",
    title= "Management Review Minutes",
    trigger_type  = "universal",
    description   = "Top management must review the ISMS at planned intervals",
    must_contain  = [
        ChecklistItem("item:9.3:audit_results",  "Internal audit results included", "must", False, "Clause 9.3.2a"),
        ChecklistItem("item:9.3:nonconf",        "Nonconformities and corrective actions status", "must", False, "Clause 9.3.2b"),
        ChecklistItem("item:9.3:monitoring",     "Monitoring and measurement results", "must", False, "Clause 9.3.2c"),
        ChecklistItem("item:9.3:objectives",     "Progress toward information security objectives", "must", False, "Clause 9.3.2d"),
        ChecklistItem("item:9.3:interested",     "Feedback from interested parties", "must", False, "Clause 9.3.2e"),
        ChecklistItem("item:9.3:decisions",      "Decisions and actions recorded", "must", False, "Clause 9.3.3"),
        ChecklistItem("item:9.3:approved",       "Approved by top management attendee", "must", False, "Management commitment"),
    ],
    should_contain= [
        ChecklistItem("item:9.3:date",       "Date of review", "should", False, "Document control"),
        ChecklistItem("item:9.3:attendees",  "Attendees listed", "should", False, "Accountability"),
    ],
)

# ── Universal — GDPR ──────────────────────────────────────────────────────────

REQ_PRIVACY_NOTICE_DIRECT = EvidenceRequirement(
    id            = "req:Art.13:privacy_notice",
    control_ref   = "Art.13",
    standard_id   = "GDPR:2016/679",
    evidence_type = "privacy_notice",
    title= "Privacy Notice (Data Collected Directly)",
    trigger_type  = "universal",
    description   = "Controllers must provide privacy notice when collecting personal data directly",
    must_contain  = [
        ChecklistItem("item:Art.13:identity",        "Identity and contact details of controller", "must", True, "Art.13.1a"),
        ChecklistItem("item:Art.13:dpo",             "DPO contact details if applicable", "must", True, "Art.13.1b"),
        ChecklistItem("item:Art.13:purposes",        "Purposes and legal basis for processing", "must", True, "Art.13.1c"),
        ChecklistItem("item:Art.13:legitimate",      "Legitimate interests if relied upon", "must", True, "Art.13.1d"),
        ChecklistItem("item:Art.13:recipients",      "Recipients or categories of recipients", "must", True, "Art.13.1e"),
        ChecklistItem("item:Art.13:retention",       "Retention period or criteria for determining it", "must", True, "Art.13.2a"),
        ChecklistItem("item:Art.13:rights",          "Data subject rights (access, rectification, erasure etc.)", "must", True, "Art.13.2b"),
        ChecklistItem("item:Art.13:withdrawal",      "Right to withdraw consent where applicable", "must", True, "Art.13.2c"),
        ChecklistItem("item:Art.13:complaint",       "Right to lodge complaint with supervisory authority", "must", True, "Art.13.2d"),
        ChecklistItem("item:Art.13:transfers",       "International transfers and safeguards if applicable", "must", True, "Art.13.1f"),
    ],
    should_contain= [
        ChecklistItem("item:Art.13:plain_language", "Written in plain, clear language", "should", True, "Art.12 readability requirement"),
        ChecklistItem("item:Art.13:layered",        "Layered or concise format used", "should", True, "Best practice"),
    ],
)

# ── GDPR Art.30 — Records of Processing — records_program spine (4-leaf) ─────
# Promoted 2026-05-28 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. New sixth spine candidate
# `records_program` (previously flagged as open question for records-only
# controls): register + maintenance_procedure + upstream_inventory +
# review_record. The register leaf id is preserved from the prior single-leaf
# definition; the three siblings are new.
# Authority: GDPR Art.30(1)(a-g) controller content, Art.30(2)(a-d) processor
# content, Art.30(3) form, Art.30(4) availability to supervisory authority;
# EDPB Position Paper on Art.30(5) derogations.

REQ_RECORDS_PROCESSING = EvidenceRequirement(
    id            = "req:Art.30:records_of_processing",
    control_ref   = "Art.30",
    standard_id   = "GDPR:2016/679",
    evidence_type = "records_of_processing",
    title         = "Records of Processing Activities (RoPA)",
    trigger_type  = "universal",
    description   = "Art.30 requires controllers (and where applicable, processors) to maintain a record of processing activities. The register is the live source of truth for what is processed, why, for whom, where it goes, and how long it is kept. Maintenance, the upstream data flow inventory and periodic review are sibling leaves",
    must_contain  = [
        ChecklistItem("item:Art.30:controller_name",   "Name and contact details of controller (and DPO/representative where appointed)", "must", True, "Art.30.1.a"),
        ChecklistItem("item:Art.30:purposes",          "Purposes of the processing stated per activity",                                   "must", True, "Art.30.1.b"),
        ChecklistItem("item:Art.30:categories_ds",     "Categories of data subjects per activity",                                         "must", True, "Art.30.1.c"),
        ChecklistItem("item:Art.30:categories_data",   "Categories of personal data per activity",                                         "must", True, "Art.30.1.c"),
        ChecklistItem("item:Art.30:recipients",        "Categories of recipients per activity (including processors and third parties)",   "must", True, "Art.30.1.d"),
        ChecklistItem("item:Art.30:transfers",         "Transfers to third countries or international organisations with safeguards identified", "must", True, "Art.30.1.e"),
        ChecklistItem("item:Art.30:retention",         "Envisaged time limits for erasure per category",                                   "must", True, "Art.30.1.f"),
        ChecklistItem("item:Art.30:security",          "General description of technical and organisational security measures",            "must", True, "Art.30.1.g"),
        ChecklistItem("item:Art.30:processor_records", "If the org also acts as processor, processor-side records per Art.30.2.a-d are included or kept as a parallel register", "must", True, "Art.30.2"),
    ],
    should_contain= [
        ChecklistItem("item:Art.30:maintained",        "Kept in written form (electronic acceptable)",                                     "should", True, "Art.30.3"),
        ChecklistItem("item:Art.30:availability",      "Available to the supervisory authority on request (export or read-only access path stated)", "should", True, "Art.30.4"),
        ChecklistItem("item:Art.30:reg_versioning",    "Versioning or change-log per activity so historical state can be reconstructed",   "should", True, "Audit defensibility"),
    ],
)

REQ_ART30_MAINTENANCE_PROCEDURE = EvidenceRequirement(
    id            = "req:Art.30:ropa_maintenance_procedure",
    control_ref   = "Art.30",
    standard_id   = "GDPR:2016/679",
    evidence_type = "procedure",
    title         = "RoPA Maintenance Procedure",
    trigger_type  = "universal",
    description   = "Art.30 implies an ongoing obligation — the register must reflect current reality. The maintenance procedure documents who keeps it current, what changes trigger an update, the path from trigger to register entry, and the link to other GDPR gates (Art.28 DPA on new processor, Art.35 DPIA on high-risk new purpose)",
    must_contain  = [
        ChecklistItem("item:Art.30:proc_maintainer",       "Named maintainer (DPO, privacy lead, or controller's designate) with documented responsibility for register accuracy", "must", True, "Accountability — Art.5.2"),
        ChecklistItem("item:Art.30:proc_triggers",         "Update triggers enumerated (new system, new purpose, new processor, new third-country transfer, retention change, DPIA outcome)", "must", True, "Art.30.1 — must reflect current state"),
        ChecklistItem("item:Art.30:proc_update_path",      "Path from trigger to register entry stated (who notifies, who reviews, who approves the entry)", "must", True, "Operational sufficiency"),
        ChecklistItem("item:Art.30:proc_dpa_gate",         "Linkage to Art.28 DPA process — adding a new processor cannot complete without DPA and register update",            "must", True, "Art.28 / Art.30.1.d coherence"),
        ChecklistItem("item:Art.30:proc_dpia_gate",        "Linkage to Art.35 DPIA — high-risk new processing requires DPIA before register entry is finalised",               "must", True, "Art.35 / Art.30 coherence"),
    ],
    should_contain= [
        ChecklistItem("item:Art.30:proc_processor_side",   "Processor-side update path stated if org also acts as processor (Art.30.2 records)",                                "should", True, "Art.30.2"),
        ChecklistItem("item:Art.30:proc_review_cadence",   "Cadence for ad-hoc review when no specific trigger fires (e.g. quarterly sweep)",                                   "should", True, "Preventive maintenance"),
        ChecklistItem("item:Art.30:proc_escalation",       "Escalation path if maintainer is unavailable or a trigger is missed",                                               "should", True, "Continuity"),
    ],
)

REQ_ART30_DATA_FLOW_INVENTORY = EvidenceRequirement(
    id            = "req:Art.30:data_flow_inventory",
    control_ref   = "Art.30",
    standard_id   = "GDPR:2016/679",
    evidence_type = "data_flow_inventory",
    title         = "Personal Data Flow Inventory",
    trigger_type  = "universal",
    description   = "The upstream data picture that feeds RoPA accuracy. Where the register is activity-centric (one row per processing activity), the data flow inventory is data-centric — which systems hold personal data, how data moves between them, who receives it, and which transfers cross borders. EDPB guidance treats data mapping as the foundation for accurate Art.30 records",
    must_contain  = [
        ChecklistItem("item:Art.30:dfi_systems",         "Systems holding personal data enumerated (production systems, SaaS, backups, analytics, archives)",                 "must", True, "Art.30.1.c-d foundation"),
        ChecklistItem("item:Art.30:dfi_flows",           "Data flows between systems documented (sources, destinations, integration mechanism)",                              "must", True, "Art.30.1.d foundation"),
        ChecklistItem("item:Art.30:dfi_recipients",      "External recipients identified per flow (processors, joint controllers, third parties) — feeds Art.30.1.d",        "must", True, "Art.30.1.d"),
        ChecklistItem("item:Art.30:dfi_transfers",       "Third-country transfers identified per flow with safeguards (SCCs, adequacy, BCRs) — feeds Art.30.1.e",             "must", True, "Art.30.1.e / Chapter V"),
        ChecklistItem("item:Art.30:dfi_retention",       "Retention period per system or per data category — feeds Art.30.1.f",                                               "must", True, "Art.30.1.f"),
    ],
    should_contain= [
        ChecklistItem("item:Art.30:dfi_asset_link",      "Cross-link to the asset/system inventory (ISO 27001 A.5.9) so the two registers stay aligned",                       "should", True, "Cross-control coherence"),
        ChecklistItem("item:Art.30:dfi_minimisation",    "Notes data minimisation review touchpoints (Art.5.1.c) — flows or fields flagged for reduction",                      "should", True, "Art.5.1.c linkage"),
        ChecklistItem("item:Art.30:dfi_visual",          "Visual representation (data flow diagram) accompanies the tabular inventory",                                         "should", True, "Auditor/reviewer clarity"),
    ],
)

REQ_ART30_ANNUAL_REVIEW = EvidenceRequirement(
    id              = "req:Art.30:ropa_annual_review",
    control_ref     = "Art.30",
    standard_id     = "GDPR:2016/679",
    evidence_type   = "review_record",
    title           = "RoPA Periodic Review Record",
    trigger_type    = "universal",
    description     = "Even with maintenance triggers in place, drift accumulates between RoPA and reality. An annual (or more frequent) review verifies each activity against current operations, propagates corrections back to the register, and produces auditable evidence that the register is not stale",
    freshness_days  = 365,
    must_contain    = [
        ChecklistItem("item:Art.30:rev_date",            "Review date within the planned interval (typically within 12 months of last review)", "must", True, "Periodic accuracy"),
        ChecklistItem("item:Art.30:rev_reviewer",        "Reviewer identity and role (DPO, privacy lead, or delegated equivalent)",              "must", True, "Accountability"),
        ChecklistItem("item:Art.30:rev_outcome",         "Per-activity outcome (no change / amended / retired) recorded",                        "must", True, "Auditable result"),
        ChecklistItem("item:Art.30:rev_register_update", "Changes propagated back to the live register with reference to this review",           "must", True, "Closes the loop"),
        ChecklistItem("item:Art.30:rev_gaps",            "Gaps identified (missing activity, outdated retention, undocumented transfer) with remediation owner and target date", "must", True, "Defect tracking"),
    ],
    should_contain  = [
        ChecklistItem("item:Art.30:rev_ad_hoc_triggers", "Ad-hoc review triggers listed (re-org, M&A, new processing line, new processor onboarded)",                            "should", True, "Change-driven review"),
        ChecklistItem("item:Art.30:rev_next_date",       "Next planned review date stated",                                                                                     "should", True, "Planning"),
        ChecklistItem("item:Art.30:rev_dfi_alignment",   "Cross-check against the data flow inventory recorded — both should describe the same reality",                        "should", True, "Cross-leaf coherence"),
    ],
)

# ── Profile-fact — cloud/processors ───────────────────────────────────────────

REQ_DPA = EvidenceRequirement(
    id            = "req:Art.28:data_processing_agreement",
    control_ref   = "Art.28",
    standard_id   = "GDPR:2016/679",
    evidence_type = "data_processing_agreement",
    title= "Data Processing Agreement (DPA)",
    trigger_type  = "profile_fact",
    description   = "Mandatory written contract with every processor under Art.28.3",
    must_contain  = [
        ChecklistItem("item:Art.28:instructions",    "Process only on documented controller instructions", "must", True, "Art.28.3a"),
        ChecklistItem("item:Art.28:confidentiality", "Confidentiality obligations on processor staff", "must", True, "Art.28.3b"),
        ChecklistItem("item:Art.28:security",        "Security measures per Art.32", "must", True, "Art.28.3c"),
        ChecklistItem("item:Art.28:subprocessors",   "Sub-processor restrictions and approval process", "must", True, "Art.28.3d"),
        ChecklistItem("item:Art.28:rights",          "Assistance with data subject rights", "must", True, "Art.28.3e"),
        ChecklistItem("item:Art.28:assistance",      "Assistance with Art.32-36 obligations", "must", True, "Art.28.3f"),
        ChecklistItem("item:Art.28:deletion",        "Deletion or return of data at end of service", "must", True, "Art.28.3g"),
        ChecklistItem("item:Art.28:audit",           "Audit rights and information to demonstrate compliance", "must", True, "Art.28.3h"),
    ],
    should_contain= [
        ChecklistItem("item:Art.28:breach_notif", "Breach notification timeline to controller", "should", True, "Best practice"),
        ChecklistItem("item:Art.28:transfers",    "Data transfer mechanisms if applicable", "should", True, "Chapter V"),
        ChecklistItem("item:Art.28:governing",    "Governing law and jurisdiction", "should", False, "Contract completeness"),
    ],
)

# ── Annex A.5.23 — InfoSec for use of cloud services — operational_process (4-leaf) ──
# Promoted 2026-05-31 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: operational_process → policy
# (primary) + register + review_record + revocation_record. trigger_type
# remains profile_fact — A.5.23 only fires for cloud-using tenants. The
# lifecycle-end slot is realised as exit-migration records — each cloud
# service exit is the supplier-equivalent of revocation. The policy leaf id is
# preserved; three siblings are new.
# Authority: ISO 27002:2022 § 5.23 implementation guidance.

REQ_CLOUD_SERVICES_POLICY = EvidenceRequirement(
    id            = "req:A.5.23:cloud_services_policy",
    control_ref   = "A.5.23",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Information Security for Use of Cloud Services Policy",
    trigger_type  = "profile_fact",
    description   = "A.5.23 requires a topic-specific policy on use of cloud services covering scope, risk management, selection, shared-responsibility split, incident handling and exit. The cloud service register, periodic posture review and exit-migration records are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.23:scope",                 "Scope of cloud services covered (IaaS / PaaS / SaaS, public / private / hybrid)",                                              "must", False, "27002:5.23a"),
        ChecklistItem("item:A.5.23:risk_management",       "How information security risks in cloud use will be managed (assessment + treatment approach)",                                "must", False, "27002:5.23b"),
        ChecklistItem("item:A.5.23:selection",             "Cloud service selection criteria",                                                                                              "must", False, "27002:5.23b"),
        ChecklistItem("item:A.5.23:responsibilities",      "Roles and responsibilities for cloud service use and management (internal)",                                                    "must", False, "27002:5.23c"),
        ChecklistItem("item:A.5.23:shared_responsibility", "Shared-responsibility model: which controls are CSP-managed vs customer-managed",                                               "must", False, "27002:5.23d"),
        ChecklistItem("item:A.5.23:controls_method",       "How CSP-side controls will be obtained, evaluated and used (attestation review, API checks, configuration discovery)",         "must", False, "27002:5.23e"),
        ChecklistItem("item:A.5.23:incidents",             "Procedures for handling cloud-related security incidents (link to A.5.24-27, support obligations from CSP)",                   "must", False, "27002:5.23f"),
        ChecklistItem("item:A.5.23:personal_data",         "How personal data in cloud storage is protected (encryption, location/sovereignty, sub-processor controls)",                   "must", True,  "GDPR Art.32 alignment"),
        ChecklistItem("item:A.5.23:industry_standards",    "Cloud agreements based on accepted industry standards for architecture and infrastructure",                                    "must", False, "27002:5.23 — agreements"),
        ChecklistItem("item:A.5.23:geographic_location",   "Geographic-location requirements for sensitive data in transit and at rest",                                                   "must", False, "27002:5.23 — geo controls"),
        ChecklistItem("item:A.5.23:forensic_support",      "Forensic / digital-evidence support expectations from the CSP",                                                                 "must", False, "27002:5.23 — forensics"),
        ChecklistItem("item:A.5.23:sub_processing",        "Sub-processing terms for cloud (CSP's own sub-processors, notification, approval)",                                             "must", False, "27002:5.23 — sub-processing"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.23:malware_protection",    "Malware monitoring/protection expectations stated for the cloud environment",                                                  "should", False, "27002:5.23 — malware"),
        ChecklistItem("item:A.5.23:backup_handover",       "CSP backup of data + config and handover obligations on termination",                                                          "should", False, "27002:5.23 — backup"),
    ],
)

REQ_CLOUD_SERVICE_REGISTER = EvidenceRequirement(
    id            = "req:A.5.23:cloud_service_register",
    control_ref   = "A.5.23",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Cloud Service Register",
    trigger_type  = "profile_fact",
    description   = "A.5.23 expects the org to know which cloud services are in use, where they store and process data, what classification of data they hold, what the shared-responsibility split looks like in practice, and what the agreement says. The register is the live source of truth — feeding the periodic posture review and exit-migration leaves",
    must_contain  = [
        ChecklistItem("item:A.5.23:reg_service",         "Each cloud service identified per row (provider, service name, deployment model)",                                              "must", False, "27002:5.23a — scope"),
        ChecklistItem("item:A.5.23:reg_classification",  "Data classification per service (which org-classification levels are processed)",                                                "must", False, "27002:5.23 — sensitive info"),
        ChecklistItem("item:A.5.23:reg_geo",             "Geographic location of data per service (region, sub-region)",                                                                   "must", False, "27002:5.23 — geo"),
        ChecklistItem("item:A.5.23:reg_responsibility",  "Shared-responsibility split recorded per service (what is CSP-managed, what is org-managed)",                                    "must", False, "27002:5.23d"),
        ChecklistItem("item:A.5.23:reg_owner",           "Named internal owner accountable per service (typically platform / SRE / business owner)",                                       "must", False, "Accountability"),
        ChecklistItem("item:A.5.23:reg_agreement",       "Reference to the agreement / contract in force per service (link to A.5.20 coverage register)",                                  "must", False, "Cross-control consistency"),
        ChecklistItem("item:A.5.23:reg_exit_readiness",  "Exit-plan readiness flag per service (Yes / No / Stale)",                                                                        "must", False, "27002:5.23 — exit"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.23:reg_subprocessors",   "Disclosed sub-processors per service tracked",                                                                                   "should", False, "27002:5.23 — sub-processing"),
        ChecklistItem("item:A.5.23:reg_attestation",     "Most recent CSP attestation / certification reference per service (with date)",                                                  "should", False, "27002:5.23 — CSP assurance"),
        ChecklistItem("item:A.5.23:reg_dependency_map",  "Business-process dependency map (which processes depend on which service)",                                                      "should", False, "Continuity awareness"),
    ],
)

REQ_CLOUD_POSTURE_REVIEW = EvidenceRequirement(
    id             = "req:A.5.23:cloud_posture_review",
    control_ref    = "A.5.23",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic Cloud Service Posture Review",
    trigger_type   = "profile_fact",
    description    = "A.5.23 expects ongoing monitoring, review and evaluation of cloud service use. The posture review captures the planned-interval check: refreshed CSP attestations, configuration-drift assessment against the shared-responsibility split, geographic-location compliance check, incident review, and resulting action items",
    freshness_days = 365,
    must_contain   = [
        ChecklistItem("item:A.5.23:rev_date",            "Review date within the planned interval",                                                                                       "must", False, "27002:5.23g — monitoring"),
        ChecklistItem("item:A.5.23:rev_reviewer",        "Reviewer identity (typically platform lead + InfoSec lead jointly)",                                                            "must", False, "Accountability"),
        ChecklistItem("item:A.5.23:rev_attestation",     "CSP attestation refresh checked per service (current vs stale)",                                                                "must", False, "27002:5.23 — CSP assurance"),
        ChecklistItem("item:A.5.23:rev_config_drift",    "Configuration-drift assessment against the shared-responsibility split (what the org owns is configured correctly)",            "must", False, "27002:5.23d,g"),
        ChecklistItem("item:A.5.23:rev_geo_compliance",  "Geographic-location compliance check (data has not silently drifted to non-approved regions)",                                  "must", False, "27002:5.23 — geo"),
        ChecklistItem("item:A.5.23:rev_incidents",       "Cloud-incidents in the period reviewed (own + CSP-disclosed)",                                                                  "must", False, "27002:5.23f"),
        ChecklistItem("item:A.5.23:rev_actions",         "Action items captured per service",                                                                                             "must", False, "27002:5.23g"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.23:rev_threat_intel",    "External threat-intel input considered (link to A.5.7)",                                                                        "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.23:rev_next_date",       "Next planned review date stated",                                                                                                "should", False, "Planning"),
    ],
)

REQ_CLOUD_EXIT_MIGRATION = EvidenceRequirement(
    id            = "req:A.5.23:exit_migration_record",
    control_ref   = "A.5.23",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Cloud Service Exit / Migration Records",
    trigger_type  = "profile_fact",
    description   = "A.5.23 requires exit strategies for cloud services and the CSP must support transition + data handover on termination. The exit-migration record evidences the actual execution: trigger captured, migration plan executed, data export and deletion confirmed, transition completed, with authoriser",
    must_contain  = [
        ChecklistItem("item:A.5.23:exit_trigger",        "Exit trigger captured (termination / replacement / CSP failure / business change)",                                              "must", False, "27002:5.23h"),
        ChecklistItem("item:A.5.23:exit_migration_plan", "Migration plan executed (data export, dependency-rewiring, replacement service stood up)",                                       "must", False, "27002:5.23h — transition"),
        ChecklistItem("item:A.5.23:exit_data_deletion",  "Data deletion confirmation from the CSP (attestation, log, or audit-trail evidence)",                                            "must", False, "27002:5.23 — handover"),
        ChecklistItem("item:A.5.23:exit_handover",       "Handover of configuration + data evidence (backup downloaded, config preserved)",                                                "must", False, "27002:5.23 — backup/handover"),
        ChecklistItem("item:A.5.23:exit_authoriser",     "Authoriser of the exit (or of the delay + risk acceptance)",                                                                     "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.23:exit_drill",          "Rolling exit-readiness drill (test exits without actually exiting, for critical services)",                                      "should", False, "Continuity preparedness"),
        ChecklistItem("item:A.5.23:exit_plan_freshness", "Per-service exit plan freshness target (re-test on agreement renewal or major service change)",                                  "should", False, "Drift control"),
    ],
)

REQ_ENCRYPTION_POLICY = EvidenceRequirement(
    id            = "req:A.8.24:encryption_policy",
    control_ref   = "A.8.24",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title= "Use of Cryptography Policy",
    trigger_type  = "universal",
    description   = "A.8.24 requires a policy on effective use of cryptography",
    must_contain  = [
        ChecklistItem("item:A.8.24:algorithms",      "Approved cryptographic algorithms listed", "must", False, "A.8.24a"),
        ChecklistItem("item:A.8.24:key_mgmt",        "Key management procedures defined", "must", False, "A.8.24b"),
        ChecklistItem("item:A.8.24:at_rest",         "Encryption requirements for data at rest", "must", False, "A.8.24c"),
        ChecklistItem("item:A.8.24:in_transit",      "Encryption requirements for data in transit", "must", False, "A.8.24c"),
        ChecklistItem("item:A.8.24:roles",           "Roles and responsibilities for cryptography", "must", False, "A.8.24e"),
        ChecklistItem("item:A.8.24:personal_data",   "Personal data explicitly scoped for encryption", "must", True, "GDPR Art.32.1a alignment"),
        ChecklistItem("item:A.8.24:pii_keys",        "Key management for PII encryption keys", "must", True, "GDPR Art.32.1a alignment"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.24:key_strength",  "Key length and strength requirements", "should", False, "A.8.24f"),
        ChecklistItem("item:A.8.24:exceptions",    "Exceptions process defined", "should", False, "Governance"),
        ChecklistItem("item:A.8.24:review",        "Review frequency stated", "should", False, "Document control"),
    ],
)

# ── Annex A.5.24 — Information security incident management planning ────────
# operational_process (4-leaf). Promoted 2026-05-31 from single-leaf to multi-
# leaf per [[curation-program-full-multi-leaf]]. Spine: operational_process →
# procedure + register + review_record + revocation_record (lifecycle-end).
#
# A.5.24 sits ABOVE the operational A.5.25-27 incident family
# ([[curation-phase-b-batch-4-2026-05-31]]) and A.5.28 evidence handling
# ([[curation-phase-b-batch-6-2026-05-31]]). A.5.24 is the strategic
# planning framework — the document that defines roles, authorities,
# communication paths, exercise cadence. A.5.25-27/28 operationalise it.
#
# Lifecycle-end variant: framework_exercise_record — per-tabletop/drill
# activation proof. Distinct from A.5.26's per-incident_closure_record:
# A.5.26 tracks REAL incidents, A.5.24 tracks READINESS EXERCISES.
# Position 16 in the catalogue.
#
# Review freshness 180d — IR readiness erodes between exercises and
# incidents. Same volatility family as A.5.25/A.5.26 (180d, batch 4),
# A.5.16/A.5.17 identity+credentials (180d, batches 12+13).
#
# `tested` SHOULD promoted to MUST → split across procedure (exercise
# cadence MUST) + dedicated lifecycle-end exercise_record leaf. Same
# SHOULD-promotion pattern observed in batches 12 (service_accounts) +
# 13 (mfa). The pattern: previously-soft expectations elevated when
# they're load-bearing for the control's effectiveness claim.
#
# Cross-control: per_data_breach personal-data MUST + notification MUST
# preserved as GDPR-required (gdpr_required=True flag). Extends the
# ISO × GDPR integration line from pii_overlay (batch 10) +
# legal_jurisdiction (batch 11) — third batch with GDPR-required MUSTs.
#
# Authority: ISO 27002:2022 § 5.24 a-g implementation guidance — roles,
# detection, assessment, response, evidence, lessons, communications.

REQ_A524_FRAMEWORK = EvidenceRequirement(
    id            = "req:A.5.24:incident_response_procedure",
    control_ref   = "A.5.24",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Information Security Incident Management Planning Framework",
    trigger_type  = "universal",
    description   = "A.5.24 requires the org to plan and prepare for incidents — not just react when they happen. The framework documents roles, authorities, detection-and-reporting paths, classification criteria, escalation thresholds, communication paths (internal + external + regulator), evidence-handling integration (A.5.28), lessons-learned integration (A.5.27), and exercise/test cadence. The IR team register, periodic program review and per-exercise activation record are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.24:roles",            "Roles and responsibilities defined (IR lead, deputies, comms lead, legal liaison, exec sponsor; named individuals or stable roles, not 'TBD')", "must", False, "27002:5.24a"),
        ChecklistItem("item:A.5.24:detection",        "Detection and reporting process (where reports come from — A.5.25 triage, monitoring/SOC, user reports, supplier notifications, A.5.7 threat intel)", "must", False, "27002:5.24b + cross-link to [[A.5.25]]"),
        ChecklistItem("item:A.5.24:assessment",       "Incident assessment and classification criteria (severity tiers; what triggers each tier; alignment with A.5.25 triage decision criteria)",         "must", False, "27002:5.24c + cross-link to [[A.5.25]]"),
        ChecklistItem("item:A.5.24:response",         "Response and escalation procedures (decision authority per severity tier; out-of-hours handling; cross-team coordination)",                         "must", False, "27002:5.24d"),
        ChecklistItem("item:A.5.24:personal_data",    "Step to determine if personal data breach occurred (DPIA-aware classification, controller/processor analysis)",                                     "must", True, "GDPR Art.33 alignment — 72hr notification trigger"),
        ChecklistItem("item:A.5.24:notification",     "Notification process for personal data breaches (supervisory authority < 72h; data subjects when high-risk; notification content per Art.33(3))",   "must", True, "GDPR Art.33/34 alignment"),
        ChecklistItem("item:A.5.24:evidence",         "Evidence collection and preservation requirements (cross-link to A.5.28 evidence-handling procedure; chain-of-custody mandatory from initiation)", "must", False, "27002:5.24e + cross-link to [[A.5.28]]"),
        ChecklistItem("item:A.5.24:exercise_cadence", "Exercise / test cadence stated explicitly (annual minimum, more frequent for high-risk org; promoted from SHOULD because untested plans degrade)",  "must", False, "27002:5.24 — preparation"),
        ChecklistItem("item:A.5.24:communications",   "External communication paths (regulator, legal, PR, law enforcement) with thresholds and named owners",                                              "must", False, "27002:5.24 — communication"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.24:lessons",          "Lessons learned process (cross-link to A.5.27 lessons register; how lessons feed back into framework revisions)",                                    "should", False, "Closing loop with [[A.5.27]]"),
        ChecklistItem("item:A.5.24:contacts",         "External contact list maintained (regulator, legal counsel, PR firm, forensic specialists, CSP support) with rotation review",                       "should", False, "Response effectiveness"),
        ChecklistItem("item:A.5.24:supplier_path",    "Supplier-driven incident path documented (A.5.21 supplier-side incidents trigger our framework even when we're not directly hit)",                  "should", False, "Cross-link to [[A.5.21]]"),
    ],
)

REQ_A524_IR_TEAM_REGISTER = EvidenceRequirement(
    id            = "req:A.5.24:incident_response_team_register",
    control_ref   = "A.5.24",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Incident Response Team Register",
    trigger_type  = "universal",
    description   = "A.5.24 requires the responders to be ready before the incident — half a team during a real incident is the failure mode. The register catalogues every named responder: name (or stable role), tier, on-call status, contact info (multiple channels), training currency, backup. It is the operational record that proves the team is staffed-and-trained, not just nominated on the org chart",
    must_contain  = [
        ChecklistItem("item:A.5.24:reg_member_id",        "Each IR team member captured with a unique identifier (employee or contractor id)",                                                          "must", False, "27002:5.24 — preparation"),
        ChecklistItem("item:A.5.24:reg_role",             "Role per row (ir_lead / deputy / comms / legal / forensic_specialist / technical_lead) — explicitly mapped to framework role taxonomy",        "must", False, "27002:5.24a"),
        ChecklistItem("item:A.5.24:reg_tier",             "Tier per row (primary / backup / escalation_only) — drives the activation order",                                                              "must", False, "27002:5.24 — preparation"),
        ChecklistItem("item:A.5.24:reg_contact",          "Contact info per row across multiple channels (phone + secondary phone + email + out-of-band channel for if corp comms are compromised)",     "must", False, "27002:5.24 — communication"),
        ChecklistItem("item:A.5.24:reg_oncall",           "On-call status per row (when in active rotation; how long; when next handover)",                                                                "must", False, "27002:5.24 — readiness"),
        ChecklistItem("item:A.5.24:reg_training_current", "Training-currency per row (last training date, training type; flagged when stale)",                                                              "must", False, "27002:5.24 — preparation"),
        ChecklistItem("item:A.5.24:reg_backup_named",     "Backup named per row (no single-person roles; rotation continuity guaranteed)",                                                                  "must", False, "27002:5.24 — preparation"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.24:reg_external_partner", "External-partner contacts captured alongside internal members (regulator points-of-contact, retained forensic firm contact)",                  "should", False, "Response continuity"),
        ChecklistItem("item:A.5.24:reg_dpia_competence",  "DPIA / data-protection competence flag per row (drives who handles the GDPR Art.33 path when personal data is in scope)",                       "should", False, "GDPR Art.33 readiness"),
    ],
)

REQ_A524_PROGRAM_REVIEW = EvidenceRequirement(
    id             = "req:A.5.24:framework_program_review",
    control_ref    = "A.5.24",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic Incident Management Framework Review",
    trigger_type   = "universal",
    description    = "The framework creates value only if it actually runs when incidents hit — exercise results that surface gaps, team coverage gaps, framework-vs-actual-response divergence, GDPR-72h-feasibility check all signal the framework is or isn't ready. The review captures the planned-interval check: exercise-result analysis, team-readiness audit, real-incident-vs-framework divergence analysis, GDPR-readiness verification, and resulting framework adjustments. Cadence tightened to 180 days — IR readiness erodes between exercises",
    freshness_days = 180,
    must_contain   = [
        ChecklistItem("item:A.5.24:rev_date",              "Review date within the planned 180-day interval",                                                                                            "must", False, "27002:5.24 — periodic"),
        ChecklistItem("item:A.5.24:rev_reviewer",          "Reviewer identity (CISO + IR lead + Data Protection Officer where personal data scope; Legal where regulator notification scope)",          "must", False, "Accountability"),
        ChecklistItem("item:A.5.24:rev_exercise_results",  "Exercise-result analysis (last N exercises reviewed; gaps surfaced; remediation per gap; ratio-of-exercises-completed vs planned)",         "must", False, "27002:5.24 — preparation effectiveness"),
        ChecklistItem("item:A.5.24:rev_team_readiness",    "Team-readiness audit (training currency across responders; coverage gaps where a tier is under-staffed; backup-named compliance)",          "must", False, "27002:5.24 — preparation"),
        ChecklistItem("item:A.5.24:rev_real_divergence",   "Real-incident vs framework divergence (where actual responses deviated from framework — was the framework too prescriptive, missing a path, or just unused?)", "must", False, "Framework effectiveness"),
        ChecklistItem("item:A.5.24:rev_gdpr_72h_feasibility","GDPR 72-hour feasibility check (when did the last personal-data incident notify? what was the gap to 72h? is the path actually under 72h?)", "must", True, "GDPR Art.33 — 72hr feasibility verification"),
        ChecklistItem("item:A.5.24:rev_actions",           "Action items captured (e.g. add new role, refresh communications playbook, expand exercise scope, tighten 72h path)",                       "must", False, "27002:5.24 — framework adjustments"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.24:rev_peer_practice",     "Peer/industry practice scan (notable incidents in the sector; how peers responded; lessons applicable)",                                     "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.24:rev_next_date",         "Next planned review date stated (within 180d of this review)",                                                                                "should", False, "Planning"),
    ],
)

REQ_A524_EXERCISE_RECORD = EvidenceRequirement(
    id            = "req:A.5.24:framework_exercise_record",
    control_ref   = "A.5.24",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Per-Exercise Framework Activation Record",
    trigger_type  = "universal",
    description   = "A.5.24 expects the framework to be exercised, not just written. The exercise record evidences each tabletop, simulation, live drill, or regulator-led exercise: exercise id, type, scenario, participants (link to IR team register), gaps identified, remediation actions, sign-off. One record per exercise, distinct from A.5.26's incident_closure_record (which tracks REAL incidents). This is per-DRILL evidence — the readiness proof",
    must_contain  = [
        ChecklistItem("item:A.5.24:ex_exercise_id",       "Exercise identifier per record (unique, sequenced)",                                                                                          "must", False, "27002:5.24 — traceability"),
        ChecklistItem("item:A.5.24:ex_type",              "Exercise type per record (tabletop / live_simulation / red_team_drill / regulator_led / partial_segment)",                                     "must", False, "27002:5.24 — preparation taxonomy"),
        ChecklistItem("item:A.5.24:ex_scenario",          "Scenario per record (what was simulated; severity; in-scope assets; threat-actor archetype)",                                                  "must", False, "27002:5.24 — preparation depth"),
        ChecklistItem("item:A.5.24:ex_participants",      "Participant list per record (links to IR team register entries; observers noted separately)",                                                  "must", False, "27002:5.24 + cross-link to register"),
        ChecklistItem("item:A.5.24:ex_gaps",              "Gaps identified per record (where the framework or team fell short; severity per gap)",                                                        "must", False, "27002:5.24 — preparation feedback"),
        ChecklistItem("item:A.5.24:ex_remediation",       "Remediation actions captured per record (each gap → action item with owner + due date; feeds the program review)",                            "must", False, "27002:5.24 — continuous improvement"),
        ChecklistItem("item:A.5.24:ex_signoff",           "Signoff per record (exercise lead + IR team lead + exec sponsor where high-tier exercise)",                                                   "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.24:ex_external_observer", "External observer noted per record where an independent party (auditor, peer org, regulator) attended (raises defensibility)",                "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.24:ex_lessons_feed",      "Lessons feed per record to A.5.27 lessons register where the exercise surfaced patterns worth retaining beyond this control",                  "should", False, "Closing loop with [[A.5.27]]"),
    ],
)

REQ_DATA_MASKING = EvidenceRequirement(
    id            = "req:A.8.11:data_masking_procedure",
    control_ref   = "A.8.11",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title= "Data Masking Procedure",
    trigger_type  = "universal",
    description   = "A.8.11 requires procedures for masking personal data in non-production environments",
    must_contain  = [
        ChecklistItem("item:A.8.11:scope",           "Scope — which systems/environments require masking", "must", False, "A.8.11a"),
        ChecklistItem("item:A.8.11:techniques",      "Masking techniques to be used (static/dynamic)", "must", False, "A.8.11b"),
        ChecklistItem("item:A.8.11:personal_data",   "Personal data explicitly covered including PII categories", "must", True, "GDPR alignment"),
        ChecklistItem("item:A.8.11:non_production",  "Non-production environments explicitly covered", "must", True, "Primary use case"),
        ChecklistItem("item:A.8.11:roles",           "Roles responsible for implementing masking", "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.11:testing",     "Verification that masking is effective", "should", False, "Quality assurance"),
        ChecklistItem("item:A.8.11:exceptions",  "Exception process for unmasked data", "should", False, "Governance"),
    ],
)

# ── Annex A.5.18 — Access rights — operational_process spine (4-leaf) ────────
# Originally promoted 2026-05-26 — A.5.18 was the FIRST control promoted to
# multi-leaf under [[curation-program-full-multi-leaf]] (the OG NC from
# case #1, the gap that started the whole curation arc).
#
# Style v2 alignment 2026-06-01 — Phase B batch 20, analogous to batch 7's
# A.5.1 alignment. NOT a promotion (A.5.18 was already 4-leaf), but brings
# A.5.18 up to A.5.16/A.5.17 identity-family modern conventions:
#   - Review freshness 365 → 180d (access drift is high-volume, matches the
#     A.5.16 / A.5.17 / A.5.25 / A.5.26 volatility family)
#   - rev_identity_pair MUST on revocation_record — bidirectional pairing
#     with A.5.16 identity revocation_record (closes "access revoked but
#     identity still active" gap, symmetric to A.5.17's identity pairing)
#   - rev_sla_met MUST on revocation_record — auditor-critical SLA proof
#     analogous to A.5.16's rev_sla_met (the "within 24h of role-change"
#     timeliness flag)
#   - rev_residual_cleanup MUST on revocation_record — analogous to A.5.16
#     (mailbox forwarding, file-share access transfer, group memberships)
#   - rev_orphan_check MUST on review — catches orphan access rights
#     (identities revoked but access not) — paired with A.5.16 review
#   - reg_idmgmt_link SHOULD → MUST — explicit linkage to A.5.16 identity
#     register, matching the identity-family bidirectional pairing pattern
#   - More elaborate descriptions matching modern Phase B style
# All 17 existing item-ids preserved; 6 new MUSTs + 3 new SHOULDs added.
# Closes the A.5 Organisational Controls arc — A.5.18 is the OG case #1
# control and the last A.5 control on the alignment list.
# Authority: ISO 27002:2022 § 5.18 implementation guidance items a-k.
# Cross-link to A.5.15 access control policy, A.5.16 identity management,
# A.5.17 authentication information, A.5.3 segregation of duties, A.6.5
# post-employment, A.8.2 privileged access rights.

REQ_A518_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.18:access_rights_procedure",
    control_ref   = "A.5.18",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Access Rights Management Procedure",
    trigger_type  = "universal",
    description   = "A.5.18 requires that access rights be provisioned, reviewed, modified and removed in accordance with the topic-specific policy on access control (A.5.15). The procedure documents the operational steps for grant, modification and revocation, the SLA targets for each operation, the handling of service accounts, and the linkage to identity management. The access rights register, periodic review and revocation record are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.18:asset_owner_authorization", "Asset owner authorization required before access is granted (named authoriser per asset class, not generic 'IT manager')",                                                          "must", False, "27002:5.18a"),
        ChecklistItem("item:A.5.18:least_privilege",           "Provisioning applies least privilege and segregation-of-duties checks (cross-link to A.5.3 segregation of duties — flagged combinations are blocked or compensated)",            "must", False, "27002:5.18b / A.5.3"),
        ChecklistItem("item:A.5.18:policy_reference",          "References the topic-specific access control policy (A.5.15) — drives consistency between policy and operational practice",                                                       "must", False, "27002:5.18c / A.5.15"),
        ChecklistItem("item:A.5.18:modification_path",         "Path for modification of access on role or responsibility change (joiner-mover-leaver flows; mover is the typically-missed leg)",                                                  "must", False, "27002:5.18g"),
        ChecklistItem("item:A.5.18:privileged_route",          "Privileged access requests route through the A.8.2 privileged-access process (separate intake, separate approval, separate logging)",                                            "must", False, "27002:5.18i / A.8.2"),
        ChecklistItem("item:A.5.18:sla_targets",               "SLA targets stated per operation (grant within X days, modification within Y days, revocation within Z hours of trigger — drives the rev_sla_met flag on revocation_record)",      "must", False, "27002:5.18d/g — timeliness"),
        ChecklistItem("item:A.5.18:service_account_handling",  "Service account / non-human identity handling stated (provisioning, owner attribution, periodic re-attestation — service accounts are the weakest spot in most access programs)", "must", False, "27002:5.18 — all identity classes"),
        ChecklistItem("item:A.5.18:identity_link",             "Explicit linkage to A.5.16 identity management (every access right attaches to a registered identity; no orphan access)",                                                          "must", False, "A.5.16 coherence"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.18:temporary_access",          "Temporary access provisions for time-bound tasks or third parties (expiry date mandatory; automated revocation at expiry)",                                                       "should", False, "27002:5.18e"),
        ChecklistItem("item:A.5.18:approval_retention",        "Retention period for approval evidence stated (drives the audit trail for who-approved-what-when)",                                                                                "should", False, "Accountability"),
        ChecklistItem("item:A.5.18:emergency_access",          "Emergency-access ('break-glass') procedure stated separately (pre-approved accounts with mandatory post-use justification + audit)",                                              "should", False, "Operational realism"),
    ],
)

REQ_A518_REGISTER = EvidenceRequirement(
    id            = "req:A.5.18:access_rights_register",
    control_ref   = "A.5.18",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Access Rights Register",
    trigger_type  = "universal",
    description   = "A.5.18 requires a central record of access rights — without a register, 'who has access to what' devolves to system-by-system queries that drift apart. The register is the live source of truth: every subject-to-asset right mapped, every grant authorised + dated + statused. It feeds the periodic review (which surveys it) and the revocation record (which closes rows out)",
    must_contain  = [
        ChecklistItem("item:A.5.18:reg_subject_asset",   "Subject-to-asset rights mapping (who has access to what — drives review and the orphan-access check)",                                                                            "must", False, "27002:5.18f"),
        ChecklistItem("item:A.5.18:reg_authoriser",      "Authoriser captured per grant (named individual, not generic role; drives accountability)",                                                                                       "must", False, "27002:5.18a, k"),
        ChecklistItem("item:A.5.18:reg_grant_date",      "Grant date captured per row (proves the grant happened in the right order — authorisation → grant, not reverse)",                                                                  "must", False, "27002:5.18k"),
        ChecklistItem("item:A.5.18:reg_status",          "Status field per row (active / suspended / revoked) — drives the review's orphan check and the revocation_record lifecycle close-out",                                              "must", False, "27002:5.18d, g"),
        ChecklistItem("item:A.5.18:reg_idmgmt_link",     "Linkage to A.5.16 identity-management register per row — every access right attaches to a registered identity (no orphan rights pointing to disabled or deleted identities)",       "must", False, "A.5.16 coherence — was SHOULD, promoted to MUST"),
        ChecklistItem("item:A.5.18:reg_last_verified",   "Last-verified date per row (when this access was last confirmed still needed — drives staleness detection between formal reviews)",                                                "must", False, "27002:5.18h — kept current"),
        ChecklistItem("item:A.5.18:reg_review_due",      "Next review-due date per row (drives the schedule for the periodic review leaf)",                                                                                                  "must", False, "27002:5.18h — planned intervals"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.18:reg_privileged_flag", "Privileged-access rows flagged for A.8.2 oversight (drives separate-tier review and tighter cadence for privileged subset)",                                                        "should", False, "A.8.2 linkage"),
        ChecklistItem("item:A.5.18:reg_temporary_flag",  "Temporary-access rows flagged with expiry date (drives automated cleanup; complements the procedure's temporary_access SHOULD)",                                                     "should", False, "Operational discipline"),
        ChecklistItem("item:A.5.18:reg_business_justification","Business justification stated per grant (why this access is needed — informs review decisions later)",                                                                          "should", False, "Audit defensibility"),
    ],
)

REQ_A518_REVIEW = EvidenceRequirement(
    id              = "req:A.5.18:access_rights_review",
    control_ref     = "A.5.18",
    standard_id     = "ISO27001:2022",
    evidence_type   = "review_record",
    title           = "Periodic Access Rights Review",
    trigger_type    = "universal",
    description     = "A.5.18 requires periodic review of access rights. Each review record captures the planned-interval review of subject-asset pairs in the register, the reviewer's identity, the outcome per subject, the orphan-access check, and any resulting modifications or revocations. Review freshness tightened to 180d for Style v2 alignment — access drift is high-volume, matches A.5.16 / A.5.17 / A.5.25 / A.5.26 volatility family",
    freshness_days  = 180,
    must_contain    = [
        ChecklistItem("item:A.5.18:rev_date",            "Review date within the planned interval (typically within 6 months of last review under the 180d cadence)",                                                                          "must", False, "27002:5.18h — periodic"),
        ChecklistItem("item:A.5.18:rev_reviewer",        "Reviewer identity and role recorded (asset owner + InfoSec lead jointly; reviewer must not be the same person who authorised the access)",                                            "must", False, "Accountability + independence"),
        ChecklistItem("item:A.5.18:rev_outcome",         "Outcome per reviewed subject (no change / amended / revoked) with rationale where amended or revoked",                                                                                "must", False, "27002:5.18h"),
        ChecklistItem("item:A.5.18:rev_actions",         "Action items closed where rights were amended or revoked (each modification or revocation traceable to a register row update + revocation_record where applicable)",                  "must", False, "27002:5.18h"),
        ChecklistItem("item:A.5.18:rev_coverage",        "Coverage stated — full register reviewed OR risk-tiered sampling with documented selection method; gaps flagged for next cycle",                                                       "must", False, "27002:5.18h — completeness"),
        ChecklistItem("item:A.5.18:rev_orphan_check",    "Orphan-access check — every register row reconciled against A.5.16 identity register; any rights attaching to disabled/deleted identities surfaced and revoked",                       "must", False, "A.5.16 coherence — orphan-prevention"),
        ChecklistItem("item:A.5.18:rev_privileged_check","Privileged-access subset reviewed with extra scrutiny (cross-link to A.8.2 privileged-access oversight; tighter cadence may apply for this slice)",                                  "must", False, "A.8.2 linkage"),
        ChecklistItem("item:A.5.18:rev_identity_pair",   "Identity-family pair check — A.5.16 identity register reviewed in parallel (or same cycle); pair-confirmation that no identity has stale access AND no access points to stale identity","must", False, "A.5.16 + A.5.17 family coherence"),
    ],
    should_contain  = [
        ChecklistItem("item:A.5.18:rev_sampling",        "Sampling approach declared if not full coverage of the register (selection method documented — risk-stratified, random, role-targeted)",                                            "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.18:rev_next_date",       "Next planned review date stated",                                                                                                                                                    "should", False, "Planning"),
        ChecklistItem("item:A.5.18:rev_ad_hoc_triggers", "Ad-hoc review triggers listed (org restructure, M&A, major access policy change, security incident affecting access controls)",                                                       "should", False, "Change-driven review"),
    ],
)

REQ_A518_REVOCATION = EvidenceRequirement(
    id            = "req:A.5.18:access_revocation_record",
    control_ref   = "A.5.18",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Access Revocation Records",
    trigger_type  = "universal",
    description   = "A.5.18 requires that access be removed on change of role, termination, or contract end. Revocation records evidence that those removals actually happened (not just were ordered) — one record per revocation event, traceable back to the register and to the originating trigger. SLA-met flag is auditor-critical — proves not just THAT access was revoked but that the revocation timestamp was within the stated SLA (the famous 'within 24h of role-change' timeliness promise). Identity-pair check enforces bidirectional A.5.16 ↔ A.5.18 lifecycle pairing — closes 'identity disabled but access lingers' gap",
    must_contain  = [
        ChecklistItem("item:A.5.18:rev_trigger",            "Revocation trigger captured (termination / role change / contract end / explicit revoke / incident-driven / temporary-expiry / orphan-cleanup)",                                       "must", False, "27002:5.18d, g — trigger taxonomy"),
        ChecklistItem("item:A.5.18:rev_date_recorded",      "Effective date per record (last working day OR contract expiry OR role-change effective date OR explicit revocation decision time)",                                                  "must", False, "Timeliness anchor"),
        ChecklistItem("item:A.5.18:rev_disabled_proof",     "Evidence access was actually disabled (system log entry, RBAC change attestation, confirmation from each affected system) — not just 'we asked'",                                       "must", False, "27002:5.18d — actually removed"),
        ChecklistItem("item:A.5.18:rev_authoriser",         "Authoriser of the revocation (named individual; for terminations the dual-signoff pattern of IT + HR/manager applies)",                                                              "must", False, "27002:5.18d"),
        ChecklistItem("item:A.5.18:rev_sla_met",            "SLA-met flag per record (yes / no_with_reason) — gap between effective and actual revocation timestamp must be within the procedure's stated SLA, or exception logged; auditor-critical proof of 'within 24h of role change' timeliness", "must", False, "27002:5.18d — auditor-critical SLA proof (matches A.5.16:rev_sla_met)"),
        ChecklistItem("item:A.5.18:rev_identity_pair",      "Identity-pair check per record — confirms A.5.16 identity revocation_record exists for the same identity (where the trigger is termination/contract-end) OR identity remains active (where trigger is role-change/explicit-revoke); closes the bidirectional lifecycle loop", "must", False, "A.5.16 + A.5.17 family coherence"),
        ChecklistItem("item:A.5.18:rev_residual_cleanup",   "Residual cleanup status per record (shared mailbox memberships removed or transferred, file-share access reassigned, distribution-list memberships cleared, OAuth tokens revoked, API keys rotated) — full lifecycle closure, not just primary RBAC revocation",                  "must", False, "27002:5.18 — full lifecycle closure"),
        ChecklistItem("item:A.5.18:rev_completeness",       "Completeness check per record — all access rights for the subject (from the register) accounted for (each row statused 'revoked' with its own evidence), not just the primary identity rights",                                                                                  "must", False, "27002:5.18 — completeness"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.18:rev_hr_link",            "Tied to HR off-boarding workflow (A.6.5 linkage) — termination trigger fires from HR system, not from manual IT request",                                                            "should", False, "A.6.5 linkage"),
        ChecklistItem("item:A.5.18:rev_timeliness",         "Timeliness target stated explicitly per trigger type (24h for termination, 5 days for role-change, immediate for incident-driven)",                                                  "should", False, "27002:5.18d — timeliness per trigger"),
        ChecklistItem("item:A.5.18:rev_post_disable_audit", "Post-disable verification window noted (30-day check that no stale access reappears via service-account chains or forgotten group memberships)",                                     "should", False, "Continual assurance"),
    ],
)

REQ_REMOTE_WORKING = EvidenceRequirement(
    id            = "req:A.6.7:remote_working_policy",
    control_ref   = "A.6.7",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title= "Remote Working Policy",
    trigger_type  = "profile_fact",
    description   = "A.6.7 requires a policy covering information security for remote working",
    must_contain  = [
        ChecklistItem("item:A.6.7:equipment",      "Approved equipment for remote working", "must", False, "A.6.7a"),
        ChecklistItem("item:A.6.7:physical",       "Physical security at remote location", "must", False, "A.6.7b"),
        ChecklistItem("item:A.6.7:network",        "Network security requirements (VPN etc.)", "must", False, "A.6.7c"),
        ChecklistItem("item:A.6.7:access",         "Access control requirements", "must", False, "A.6.7d"),
        ChecklistItem("item:A.6.7:personal_data",  "Handling of personal data when working remotely", "must", True, "GDPR alignment"),
        ChecklistItem("item:A.6.7:reporting",      "Incident reporting when working remotely", "must", False, "A.6.7e"),
    ],
    should_contain= [
        ChecklistItem("item:A.6.7:family",    "Rules regarding family/visitor access to work equipment", "should", False, "Practical guidance"),
        ChecklistItem("item:A.6.7:travel",    "Security when travelling", "should", False, "A.6.7f"),
    ],
)

REQ_SECURE_DEVELOPMENT = EvidenceRequirement(
    id            = "req:A.8.25:secure_development_policy",
    control_ref   = "A.8.25",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title= "Secure Development Lifecycle Policy",
    trigger_type  = "profile_fact",
    description   = "A.8.25 requires rules for secure development when organisation develops software",
    must_contain  = [
        ChecklistItem("item:A.8.25:principles",    "Security principles for software design", "must", False, "A.8.25a"),
        ChecklistItem("item:A.8.25:environments",  "Security of development environments", "must", False, "A.8.25b"),
        ChecklistItem("item:A.8.25:versioning",    "Version control requirements", "must", False, "A.8.25c"),
        ChecklistItem("item:A.8.25:security_req",  "Security requirements in development process", "must", False, "A.8.26 linkage"),
        ChecklistItem("item:A.8.25:testing",       "Security testing requirements", "must", False, "A.8.29 linkage"),
        ChecklistItem("item:A.8.25:personal_data", "Handling of personal data in development/test", "must", True, "GDPR — no real data in dev"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.25:training",  "Secure coding training requirements", "should", False, "A.8.28 linkage"),
        ChecklistItem("item:A.8.25:review",    "Code review requirements", "should", False, "Quality assurance"),
    ],
)

# ── Operational documents ─────────────────────────────────────────────────────

REQ_BREACH_NOTIFICATION = EvidenceRequirement(
    id            = "req:Art.33:breach_notification",
    control_ref   = "Art.33",
    standard_id   = "GDPR:2016/679",
    evidence_type = "breach_notification",
    title= "Personal Data Breach Notification to Supervisory Authority",
    trigger_type  = "operational",
    description   = "Art.33 requires notification to supervisory authority within 72 hours of becoming aware of a breach",
    must_contain  = [
        ChecklistItem("item:Art.33:nature",       "Nature of the breach including categories and approximate number of data subjects", "must", True, "Art.33.3a"),
        ChecklistItem("item:Art.33:dpo_contact",  "Contact details of DPO or other contact point", "must", True, "Art.33.3b"),
        ChecklistItem("item:Art.33:consequences", "Likely consequences of the breach", "must", True, "Art.33.3c"),
        ChecklistItem("item:Art.33:measures",     "Measures taken or proposed to address the breach", "must", True, "Art.33.3d"),
        ChecklistItem("item:Art.33:timing",       "Notified within 72 hours of becoming aware", "must", True, "Art.33.1"),
    ],
    should_contain= [
        ChecklistItem("item:Art.33:phased",   "If phased, reasons for delay and information provided in phases", "should", True, "Art.33.4"),
    ],
)

# ── GDPR Art.15 — Right of Access — gdpr_rights spine (4-leaf) ───────────────
# Promoted 2026-05-28 from single-leaf (operational only) to multi-leaf per
# [[curation-program-full-multi-leaf]]. The original `gdpr_rights_article`
# spine of (procedure, response_record) is expanded to four — adding a
# universal register and an annual process review around the operational
# response leaf. Use this shape for Art.15-22 (right-class articles).
#
# The response leaf id is preserved from the prior single-leaf definition;
# the three universal siblings are new. The response leaf is refreshed to
# cover Art.15.1.g (source), Art.15.1.h (automated decision-making) and
# Art.15.2 (transfer safeguards) — gaps in the prior content — and promotes
# Art.15.3 "copy" to MUST since the article says "shall provide".
# Authority: GDPR Art.15(1)(a-h), Art.15(2-4); Art.12(3) timing, Art.12(5)
# manifestly-unfounded, Art.12(6) identity verification; EDPB Guidelines
# 01/2022 on data subject rights — right of access.

REQ_DSAR_RESPONSE = EvidenceRequirement(
    id            = "req:Art.15:dsar_response",
    control_ref   = "Art.15",
    standard_id   = "GDPR:2016/679",
    evidence_type = "dsar_response",
    title         = "Data Subject Access Request Response",
    trigger_type  = "operational",
    description   = "Per-request evidence that a specific DSAR was answered in line with Art.15. Each response covers confirmation, the Art.15(1)(a-h) information set, third-country transfer safeguards under Art.15(2), the copy of personal data per Art.15(3), and was delivered within Art.12(3) timing",
    must_contain  = [
        ChecklistItem("item:Art.15:confirmation",         "Confirmation that personal data is or is not processed",                                "must", True, "Art.15.1 opening"),
        ChecklistItem("item:Art.15:purposes",             "Purposes of the processing",                                                            "must", True, "Art.15.1.a"),
        ChecklistItem("item:Art.15:categories",           "Categories of personal data concerned",                                                 "must", True, "Art.15.1.b"),
        ChecklistItem("item:Art.15:recipients",           "Recipients or categories of recipients (including any in third countries)",            "must", True, "Art.15.1.c"),
        ChecklistItem("item:Art.15:retention",            "Envisaged storage period or criteria used to determine it",                             "must", True, "Art.15.1.d"),
        ChecklistItem("item:Art.15:rights",               "Existence of rights to rectification, erasure, restriction and objection",              "must", True, "Art.15.1.e"),
        ChecklistItem("item:Art.15:complaint",            "Right to lodge a complaint with a supervisory authority",                               "must", True, "Art.15.1.f"),
        ChecklistItem("item:Art.15:source",               "Source of the personal data where not collected from the data subject (any available information)", "must", True, "Art.15.1.g"),
        ChecklistItem("item:Art.15:automated_decision",   "Existence of automated decision-making / profiling, with meaningful information on logic and consequences where applicable", "must", True, "Art.15.1.h / Art.22"),
        ChecklistItem("item:Art.15:transfer_safeguards",  "Where data is transferred to a third country or international organisation, the appropriate safeguards under Art.46",          "must", True, "Art.15.2"),
        ChecklistItem("item:Art.15:copy",                 "Copy of the personal data undergoing processing provided to the data subject",          "must", True, "Art.15.3"),
        ChecklistItem("item:Art.15:timing",               "Responded within one calendar month of receipt (extension flagged where applied)",      "must", True, "Art.12.3"),
    ],
    should_contain= [
        ChecklistItem("item:Art.15:format",               "Provided in a commonly used electronic format where the request was made electronically", "should", True, "Art.15.3"),
        ChecklistItem("item:Art.15:identity_check",       "Identity verification step recorded (proportionate to sensitivity per Art.12.6)",        "should", True, "Art.12.6"),
        ChecklistItem("item:Art.15:third_party_redaction","Where other people's rights would be affected, redaction or partial-response justification noted", "should", True, "Art.15.4"),
    ],
)

REQ_ART15_HANDLING_PROCEDURE = EvidenceRequirement(
    id            = "req:Art.15:dsar_handling_procedure",
    control_ref   = "Art.15",
    standard_id   = "GDPR:2016/679",
    evidence_type = "procedure",
    title         = "DSAR Handling Procedure",
    trigger_type  = "universal",
    description   = "Art.15 read with Art.12 implies a documented operational process — the procedure prescribes how access requests are received, verified, fulfilled, timed and exception-handled, regardless of whether any DSAR has yet occurred. The actual responses are the per-event response leaf",
    must_contain  = [
        ChecklistItem("item:Art.15:proc_intake",          "Intake channels for DSARs enumerated (web form, email, post, in-person) and a single point of receipt named", "must", True, "Operational sufficiency"),
        ChecklistItem("item:Art.15:proc_identity",        "Identity verification approach stated, proportionate to data sensitivity (reasonable doubts trigger, Art.12.6)", "must", True, "Art.12.6"),
        ChecklistItem("item:Art.15:proc_fulfillment",     "Fulfillment steps — who searches which systems against the data flow inventory to assemble the response",       "must", True, "Art.15.1 / Art.30 linkage"),
        ChecklistItem("item:Art.15:proc_timing",          "One-month timing clock from receipt, with the Art.12.3 two-month extension procedure (when justified, how notified)", "must", True, "Art.12.3"),
        ChecklistItem("item:Art.15:proc_format",          "Default response format (electronic where request was electronic, structured layout for readability)",          "must", True, "Art.15.3"),
        ChecklistItem("item:Art.15:proc_exceptions",      "Exception handling: manifestly unfounded/excessive requests (Art.12.5), and partial response where rights of others apply (Art.15.4)", "must", True, "Art.12.5 / Art.15.4"),
    ],
    should_contain= [
        ChecklistItem("item:Art.15:proc_inventory_link",  "Linkage to the data flow inventory (req:Art.30:data_flow_inventory) — fulfillment relies on knowing where personal data lives", "should", True, "Art.30 cross-control"),
        ChecklistItem("item:Art.15:proc_training",        "Front-line staff trained on DSAR recognition and routing (so a request in the wrong channel still reaches the procedure)",     "should", True, "EDPB 01/2022 — operational realism"),
        ChecklistItem("item:Art.15:proc_escalation",      "DPO or legal escalation path for unusual requests (mixed-rights, joint controllers, processor-held data)",                     "should", True, "Operational continuity"),
    ],
)

REQ_ART15_REGISTER = EvidenceRequirement(
    id            = "req:Art.15:dsar_register",
    control_ref   = "Art.15",
    standard_id   = "GDPR:2016/679",
    evidence_type = "register",
    title         = "DSAR Register",
    trigger_type  = "universal",
    description   = "Living log of every access request received and its handling. Distinct from the per-event response leaf: the register is the universal record showing the population of requests, status, and timing compliance — auditor-facing evidence that the procedure operates in practice",
    must_contain  = [
        ChecklistItem("item:Art.15:reg_received_date",    "Request received date (the start of the Art.12.3 clock) per row",                       "must", True, "Art.12.3 timing"),
        ChecklistItem("item:Art.15:reg_requester",        "Requester identity (verified) or pseudonymous reference where verification used a token",  "must", True, "Art.12.6"),
        ChecklistItem("item:Art.15:reg_scope",            "Scope of the request as understood (full Art.15 / specific data set / repeat copy)",     "must", True, "Operational clarity"),
        ChecklistItem("item:Art.15:reg_response_date",    "Date the response was issued",                                                             "must", True, "Art.12.3"),
        ChecklistItem("item:Art.15:reg_timing_flag",      "Timing compliance flag (within 1 month / extended per Art.12.3 / late)",                  "must", True, "Art.12.3"),
        ChecklistItem("item:Art.15:reg_outcome",          "Outcome per row (fulfilled / partial under Art.15.4 / refused under Art.12.5 with reason)", "must", True, "Art.12.5 / Art.15.4"),
    ],
    should_contain= [
        ChecklistItem("item:Art.15:reg_extension_reason", "Extension reason captured when Art.12.3 two-month extension was used",                    "should", True, "Art.12.3"),
        ChecklistItem("item:Art.15:reg_response_link",    "Linkage to the per-request response artifact (req:Art.15:dsar_response instance)",         "should", True, "Cross-leaf traceability"),
    ],
)

REQ_ART15_PROCESS_REVIEW = EvidenceRequirement(
    id              = "req:Art.15:dsar_process_review",
    control_ref     = "Art.15",
    standard_id     = "GDPR:2016/679",
    evidence_type   = "review_record",
    title           = "Periodic DSAR Process Review",
    trigger_type    = "universal",
    description     = "Periodic management review of DSAR handling effectiveness. Confirms the procedure produced timely, lawful responses across the year, identifies systemic defects (late responses, refusals, complaints to supervisory authority) and feeds corrective actions back into the procedure",
    freshness_days  = 365,
    must_contain    = [
        ChecklistItem("item:Art.15:rev_date",             "Review date within the planned interval (typically within 12 months of last review)", "must", True, "Periodic accuracy"),
        ChecklistItem("item:Art.15:rev_reviewer",         "Reviewer identity and role (DPO, privacy lead, or delegated equivalent)",              "must", True, "Accountability"),
        ChecklistItem("item:Art.15:rev_volume",           "Volume metric — number of DSARs received in the review period",                        "must", True, "Effectiveness measurement"),
        ChecklistItem("item:Art.15:rev_timing",           "Timing metric — percentage within one month, count of extensions used, count of late responses", "must", True, "Art.12.3 evidence"),
        ChecklistItem("item:Art.15:rev_defects",          "Defects identified (late responses, refusals, supervisory-authority complaints) referenced", "must", True, "Defect tracking"),
        ChecklistItem("item:Art.15:rev_corrective",       "Corrective actions to the procedure with owner and target date",                       "must", True, "Closes the loop"),
    ],
    should_contain  = [
        ChecklistItem("item:Art.15:rev_next_date",        "Next planned review date stated",                                                       "should", True, "Planning"),
        ChecklistItem("item:Art.15:rev_training_impl",    "Training implications captured where defects trace to staff awareness",                 "should", True, "EDPB 01/2022 — operational realism"),
        ChecklistItem("item:Art.15:rev_inventory_align",  "Cross-check that the data flow inventory remains aligned with what fulfillment actually queried", "should", True, "Art.30 cross-leaf coherence"),
    ],
)

# ── Annex A.5.1 — Policies for information security — policy_program (4-leaf) ─
# Originally curated as the FIRST multi-leaf spec in the codebase (legacy
# Style v1). Aligned 2026-05-31 to the Phase B policy_program convention
# (per [[curation-program-full-multi-leaf]]) — same shape as A.5.3/4/10/12/15
# from batch 2: policy + approval + communication_record + review_record.
#
# Alignment-only changes (no MUST/SHOULD churn — engine signature preserved):
#   - freshness_days = 365 added to the annual_review leaf (the original
#     spec had no freshness, so the review leaf never went stale even after
#     years; this matches the canonical policy_program convention)
#   - citation rationale strings updated from legacy "A.5.1 — defined" /
#     "A.5.1 — approved by management" form to the Phase B "27002:5.1 — …"
#     form, consistent with batches 1-6
#   - section header refreshed; original "commit 3 — first full multi-leaf
#     spec" comment retained for archaeology in this block heading
#
# MUST/SHOULD ids and counts are preserved exactly. Engine signature on
# tenant Arion stays OFI at 1/4 children satisfied (policy leaf 5/5;
# approval + communication + review leaves 0/3 each). Cases 33/34/36/38
# all locked to this verdict.
#
# Authority: ISO 27002:2022 § 5.1 — InfoSec policy defined, approved by
# management, published, communicated to relevant personnel and interested
# parties, reviewed at planned intervals or on significant change. Same
# policy PDF can satisfy this leaf AND clause 5.2's REQ_ISMS_POLICY at the
# same time (artefact ↔ leaf is many-to-many).

REQ_A51_ISP_POLICY = EvidenceRequirement(
    id            = "req:A.5.1:isp_policy",
    control_ref   = "A.5.1",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Information Security Policy (Annex A.5.1)",
    trigger_type  = "universal",
    description   = "A.5.1 requires an information security policy that defines principles, scope, and roles, and references topic-specific policies. Approval, communication and periodic review are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.1:scope",            "Scope of the policy defined (which assets, locations, personnel)",                "must", False, "27002:5.1 — defined"),
        ChecklistItem("item:A.5.1:principles",       "Information security principles and objectives stated",                            "must", False, "27002:5.1 — defined"),
        ChecklistItem("item:A.5.1:roles",            "Roles and responsibilities for information security",                              "must", False, "27002:5.1 — defined"),
        ChecklistItem("item:A.5.1:legal_compliance", "Commitment to legal, regulatory and contractual compliance",                       "must", False, "27002:5.1 — defined"),
        ChecklistItem("item:A.5.1:topic_refs",       "References to topic-specific policies that flow from this one (e.g. A.5.10 AUP, A.5.12 classification, A.6.4 disciplinary)", "must", False, "27002:5.1 — topic-specific policies"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.1:version",          "Version number and effective date",                                                "should", False, "Document control"),
        ChecklistItem("item:A.5.1:owner",            "Policy owner named (typically CISO or equivalent)",                                "should", False, "Accountability"),
    ],
)

REQ_A51_APPROVAL = EvidenceRequirement(
    id            = "req:A.5.1:management_approval",
    control_ref   = "A.5.1",
    standard_id   = "ISO27001:2022",
    evidence_type = "approval",
    title         = "Top Management Approval of InfoSec Policy",
    trigger_type  = "universal",
    description   = "A.5.1 requires top management to approve the InfoSec policy. The approval can live inside the policy as a signed cover page, in a board minute, or as a separate signed cover letter — any form that names a top-management signatory and a date",
    must_contain  = [
        ChecklistItem("item:A.5.1:approval_signatory", "Signatory at top-management level (CEO, board chair, or delegated equivalent)", "must", False, "27002:5.1 — approved by management"),
        ChecklistItem("item:A.5.1:approval_date",      "Approval date recorded",                                                          "must", False, "27002:5.1 — approved"),
        ChecklistItem("item:A.5.1:approval_target",    "Reference to the specific policy version being approved",                         "must", False, "27002:5.1 — approved"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.1:approval_authority", "Statement of the signatory's authority to approve (delegation chain if not CEO)","should", False, "Accountability"),
    ],
)

REQ_A51_COMMUNICATION = EvidenceRequirement(
    id            = "req:A.5.1:communication_record",
    control_ref   = "A.5.1",
    standard_id   = "ISO27001:2022",
    evidence_type = "communication_record",
    title         = "Information Security Policy Communication Record",
    trigger_type  = "universal",
    description   = "A.5.1 requires the policy to be published and communicated to relevant personnel. Evidence must show active distribution (date, audience, channel), not mere availability on an intranet",
    must_contain  = [
        ChecklistItem("item:A.5.1:comm_date",         "Date of publication/communication",                                                "must", False, "27002:5.1 — communicated"),
        ChecklistItem("item:A.5.1:comm_audience",     "Audience reached (all staff, scoped subset, or named groups)",                     "must", False, "27002:5.1 — communicated to relevant personnel"),
        ChecklistItem("item:A.5.1:comm_channel",      "Channel used (intranet publication, email, training session, town hall)",         "must", False, "27002:5.1 — communicated"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.1:comm_acknowledgment", "Acknowledgment of receipt and understanding by personnel (e.g. signed register, e-learning completion)", "should", False, "27002:5.1 — acknowledged"),
        ChecklistItem("item:A.5.1:comm_interested",   "Communication to relevant interested parties (contractors, suppliers) where appropriate", "should", False, "27002:5.1 — interested parties"),
    ],
)

REQ_A51_REVIEW = EvidenceRequirement(
    id              = "req:A.5.1:annual_review",
    control_ref     = "A.5.1",
    standard_id     = "ISO27001:2022",
    evidence_type   = "review_record",
    title           = "Periodic Information Security Policy Review Record",
    trigger_type    = "universal",
    description     = "A.5.1 requires the policy to be reviewed at planned intervals (typically annually) and after significant changes. The review record captures who reviewed it, when, and the outcome (unchanged / amended / retired). Annual cadence (365d) — master InfoSec policy is stable; topic-specific policies they reference may move faster",
    freshness_days  = 365,
    must_contain    = [
        ChecklistItem("item:A.5.1:review_date",       "Review date within the planned review interval (typically within 12 months of last review)", "must", False, "27002:5.1 — reviewed at planned intervals"),
        ChecklistItem("item:A.5.1:review_outcome",    "Outcome of the review (no change / amended to vN / retired)",                       "must", False, "27002:5.1 — reviewed"),
        ChecklistItem("item:A.5.1:review_reviewer",   "Reviewer identity and role",                                                         "must", False, "Accountability"),
    ],
    should_contain  = [
        ChecklistItem("item:A.5.1:review_triggers",   "List of significant-change triggers that should prompt an ad-hoc review",          "should", False, "27002:5.1 — review on significant change"),
        ChecklistItem("item:A.5.1:review_next_date",  "Next planned review date stated",                                                    "should", False, "Planning"),
    ],
)


# ── ISO 27001 Annex A.5 — Organizational Controls (Phase B bulk curation) ────
# Style v2 (2026-05-26) — supersedes the single-leaf rule locked 2026-05-22.
# See [[curation-program-full-multi-leaf]].
#   - MULTI-LEAF DEFAULT: every control gets a full FulfilmentSpec spine.
#     Five spines defined: policy_program / operational_process /
#     technical_control / gdpr_rights_article / gdpr_principle_article.
#     Single-leaf only with explicit justification in the description.
#   - Source of authority: ISO 27002:2022 implementation guidance for ISO;
#     article text + EDPB guidelines for GDPR. The rationale field carries the
#     citation (e.g. "27002:5.18a", "EDPB 4/2019 §3.2").
#   - Cross-references to sibling controls go in SHOULD items, never MUST.
#   - freshness_days per leaf type: review_record ~365; register and
#     event-driven records (revocation_record, response_record) no freshness;
#     configuration_baseline ~365 unless change-control rhythm is tighter.
#   - Item ids follow item:{control_ref}:{slug}.
# Calibration multi-leaf entries above: A.5.1 (policy_program) and A.5.18
# (operational_process — promoted 2026-05-26). Pre-v2 single-leaf entries
# below are flagged for re-curation when their spine pass comes through.

# ── Annex A.5.2 — Roles and responsibilities — policy_program spine (4-leaf) ─
# Promoted 2026-05-27 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: policy_program adapted for a
# governance wrapper — primary artefact is a responsibility_matrix (not a
# policy document), surrounded by the same approval + communication_record +
# review_record siblings as A.5.1. ISO 27001 Clause 5.3 makes management
# responsibility AND communication explicit obligations of top management;
# ISO 27002:2022 § 5.2 implementation guidance details the allocation content.
# The matrix alone is not sufficient evidence — approval, communication and
# review records are auditor-expected separately.

REQ_A52_RESPONSIBILITY_MATRIX = EvidenceRequirement(
    id            = "req:A.5.2:roles_and_responsibilities",
    control_ref   = "A.5.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "responsibility_matrix",
    title         = "Information Security Roles and Responsibilities Matrix",
    trigger_type  = "universal",
    description   = "A.5.2 requires information security roles and responsibilities to be defined and allocated according to organization needs. Evidence is a responsibility matrix (or equivalent section in the ISMS charter) enumerating roles, allocating them to named individuals or positions, and stating reporting lines. Approval, communication and periodic review of this allocation are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.2:roles_enumerated",      "Information security roles enumerated (CISO, ISMS Manager, Asset Owners, Risk Owners, Incident Manager, DPO where applicable)", "must", False, "27002:5.2a"),
        ChecklistItem("item:A.5.2:responsibilities",      "Responsibilities described per role (decision rights, oversight, execution)", "must", False, "27002:5.2b"),
        ChecklistItem("item:A.5.2:allocation",            "Allocation to named individuals or positions, not just abstract role labels", "must", False, "27002:5.2d / Clause 5.3"),
        ChecklistItem("item:A.5.2:reporting_lines",       "Reporting and escalation lines stated (who each role reports to)", "must", False, "27002:5.2f"),
        ChecklistItem("item:A.5.2:asset_owner_resp",      "Accountability for protection and risk management of specific assets assigned", "must", False, "27002:5.2g"),
        ChecklistItem("item:A.5.2:topic_alignment",       "Allocation covers ISMS operation, asset ownership, risk management, audits and security review topics", "must", False, "27002:5.2b"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.2:isp_link",              "Links back to the Information Security Policy (A.5.1)", "should", False, "Coherence with policy framework"),
        ChecklistItem("item:A.5.2:segregation_note",      "Notes conflicts to be resolved via segregation of duties (A.5.3)", "should", False, "27002:5.2i / A.5.3"),
        ChecklistItem("item:A.5.2:cloud_responsibilities","For cloud and external services, responsibilities split between the organization and the provider stated", "should", False, "27002:5.2k"),
        ChecklistItem("item:A.5.2:competency_link",       "Notes competency/training requirements per role (cross-ref A.6.3)", "should", False, "27002:5.2j / A.6.3"),
    ],
)

REQ_A52_APPROVAL = EvidenceRequirement(
    id            = "req:A.5.2:management_approval",
    control_ref   = "A.5.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "approval",
    title         = "Top Management Approval of Roles and Responsibilities Allocation",
    trigger_type  = "universal",
    description   = "Clause 5.3 makes the assignment of information-security roles and authorities a top-management responsibility. The approval can live inside the responsibility matrix as a signed cover page, in a board minute, or as a separate signed delegation — any form that names a top-management signatory, a date, and the specific allocation being approved",
    must_contain  = [
        ChecklistItem("item:A.5.2:approval_signatory", "Signatory at top-management level (CEO, board chair, or delegated equivalent)", "must", False, "Clause 5.3"),
        ChecklistItem("item:A.5.2:approval_date",      "Approval date recorded", "must", False, "Clause 5.3"),
        ChecklistItem("item:A.5.2:approval_target",    "Reference to the specific version of the responsibility matrix being approved", "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.2:approval_authority", "Statement of the signatory's authority to approve (delegation chain if not CEO)", "should", False, "Accountability"),
    ],
)

REQ_A52_COMMUNICATION = EvidenceRequirement(
    id            = "req:A.5.2:communication_record",
    control_ref   = "A.5.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "communication_record",
    title         = "Roles and Responsibilities Communication Record",
    trigger_type  = "universal",
    description   = "Clause 5.3 requires roles, responsibilities and authorities to be communicated within the organization. Evidence must show active distribution (date, audience, channel), not mere availability of the matrix on an intranet — affected role-holders need to actually know what they own",
    must_contain  = [
        ChecklistItem("item:A.5.2:comm_date",          "Date of publication/communication", "must", False, "Clause 5.3"),
        ChecklistItem("item:A.5.2:comm_audience",      "Audience reached (all staff or named role-holders)", "must", False, "Clause 5.3 — communicated within the organization"),
        ChecklistItem("item:A.5.2:comm_channel",       "Channel used (intranet publication, email, training session, onboarding pack)", "must", False, "Clause 5.3"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.2:comm_role_briefing", "Role-specific briefing or acknowledgement from named role-holders (CISO, asset owners, etc.)", "should", False, "Effectiveness"),
        ChecklistItem("item:A.5.2:comm_onboarding",    "Communication built into joiner onboarding so new role-holders are briefed on appointment", "should", False, "Sustained communication"),
    ],
)

REQ_A52_REVIEW = EvidenceRequirement(
    id            = "req:A.5.2:annual_review",
    control_ref   = "A.5.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "review_record",
    title         = "Periodic Roles and Responsibilities Review Record",
    trigger_type  = "universal",
    description   = "ISO 27002:2022 § 5.2 implementation guidance treats role allocation as needing periodic review to keep up with organizational change. The review record captures who reviewed the matrix, when, and the outcome (unchanged / re-allocated / new role introduced)",
    freshness_days= 365,
    must_contain  = [
        ChecklistItem("item:A.5.2:review_date",        "Review date within the planned review interval (typically within 12 months of last review)", "must", False, "27002:5.2 — periodic review"),
        ChecklistItem("item:A.5.2:review_outcome",     "Outcome of the review (no change / amended to vN / role added or removed)", "must", False, "27002:5.2"),
        ChecklistItem("item:A.5.2:review_reviewer",    "Reviewer identity and role", "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.2:review_triggers",    "List of significant-change triggers (reorg, new business line, key role departure) that should prompt an ad-hoc review", "should", False, "27002:5.2 — change-driven review"),
        ChecklistItem("item:A.5.2:review_next_date",   "Next planned review date stated", "should", False, "Planning"),
    ],
)

# ── Annex A.5.3 — Segregation of duties — policy_program 4-leaf ───────────────
# Promoted 2026-05-29 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. policy_program spine adapted as
# governance-wrapper: primary artefact is the segregation matrix (not a policy
# document), surrounded by approval + communication_record + review_record
# siblings. The matrix leaf id is preserved; the three siblings are new.
# Authority: ISO 27001 Clause 5.3 makes role assignment a top-management
# responsibility; ISO 27002:2022 § 5.3 implementation guidance details
# conflict identification and compensating controls.

REQ_A53_SEGREGATION_MATRIX = EvidenceRequirement(
    id            = "req:A.5.3:segregation_of_duties",
    control_ref   = "A.5.3",
    standard_id   = "ISO27001:2022",
    evidence_type = "segregation_matrix",
    title         = "Segregation of Duties Matrix",
    trigger_type  = "universal",
    description   = "A.5.3 requires conflicting duties and conflicting areas of responsibility to be segregated. The matrix identifies conflict pairs and the mechanism preventing one person from holding both. Approval, communication and periodic review are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.3:conflict_pairs",    "Conflicting duty pairs identified (e.g. requestor vs approver, developer vs production deployer, vendor relationship vs payment authorisation)", "must", False, "27002:5.3a"),
        ChecklistItem("item:A.5.3:separation_method", "Separation mechanism stated per pair (different people, different systems, four-eyes, time-bound role swaps)",                                  "must", False, "27002:5.3b"),
        ChecklistItem("item:A.5.3:compensating",      "Compensating controls where full separation is not feasible (small-team exceptions, supervisory review, automated logging)",                    "must", False, "27002:5.3c — small organisations"),
        ChecklistItem("item:A.5.3:coverage_scope",    "Scope of coverage stated (functional areas, systems, processes covered by the matrix)",                                                          "must", False, "27002:5.3"),
        ChecklistItem("item:A.5.3:owner",             "Named owner of the matrix accountable for its maintenance",                                                                                      "must", False, "Accountability — Clause 5.3"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.3:exception_process", "Exception process for temporary or unavoidable conflicts (e.g. on-call coverage breaking normal separation)",                                    "should", False, "Real-world flexibility"),
        ChecklistItem("item:A.5.3:a52_link",          "Cross-link to A.5.2 responsibility matrix — conflicts identified in A.5.2 inform A.5.3 separation decisions",                                    "should", False, "Cross-control coherence"),
    ],
)

REQ_A53_APPROVAL = EvidenceRequirement(
    id            = "req:A.5.3:management_approval",
    control_ref   = "A.5.3",
    standard_id   = "ISO27001:2022",
    evidence_type = "approval",
    title         = "Top Management Approval of Segregation Matrix",
    trigger_type  = "universal",
    description   = "Clause 5.3 makes assignment of conflicting-duty controls a top-management responsibility. The approval may be a signed cover page on the matrix, a board minute, or a delegated equivalent — any form that names a top-management signatory, a date, and the specific matrix version being approved",
    must_contain  = [
        ChecklistItem("item:A.5.3:approval_signatory", "Signatory at top-management level (CEO, board chair, or delegated equivalent)",       "must", False, "Clause 5.3"),
        ChecklistItem("item:A.5.3:approval_date",      "Approval date recorded",                                                              "must", False, "Clause 5.3"),
        ChecklistItem("item:A.5.3:approval_target",    "Reference to the specific version of the segregation matrix being approved",         "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.3:approval_authority", "Statement of the signatory's authority to approve (delegation chain if not CEO)",    "should", False, "Accountability"),
    ],
)

REQ_A53_COMMUNICATION = EvidenceRequirement(
    id            = "req:A.5.3:communication_record",
    control_ref   = "A.5.3",
    standard_id   = "ISO27001:2022",
    evidence_type = "communication_record",
    title         = "Segregation Matrix Communication Record",
    trigger_type  = "universal",
    description   = "Affected role-holders must know their conflicts and the separation mechanisms that apply to them — an approved-but-unknown matrix doesn't prevent anything. Evidence must show active distribution (date, audience, channel), not just availability of the matrix on an intranet",
    must_contain  = [
        ChecklistItem("item:A.5.3:comm_date",         "Date of publication/communication",                                                   "must", False, "Operational sufficiency"),
        ChecklistItem("item:A.5.3:comm_audience",     "Audience reached (affected role-holders or all relevant function leads)",             "must", False, "27002:5.3 — implemented"),
        ChecklistItem("item:A.5.3:comm_channel",      "Channel used (intranet publication, role-holder briefing, manager cascade)",          "must", False, "Operational sufficiency"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.3:comm_a64_link",     "Linkage into A.6.4 disciplinary process — non-compliance with separation has stated consequence", "should", False, "Enforcement"),
        ChecklistItem("item:A.5.3:comm_onboarding",   "Communication built into onboarding for new role-holders in affected positions",      "should", False, "Sustained communication"),
    ],
)

REQ_A53_REVIEW = EvidenceRequirement(
    id              = "req:A.5.3:periodic_review",
    control_ref     = "A.5.3",
    standard_id     = "ISO27001:2022",
    evidence_type   = "review_record",
    title           = "Periodic Segregation of Duties Review",
    trigger_type    = "universal",
    description     = "Org structure shifts (new roles, reorganisations, M&A) create new conflict pairs and obsolete old ones. The review captures who reviewed the matrix, when, and the outcome — and propagates corrections back to the matrix and compensating controls",
    freshness_days  = 365,
    must_contain    = [
        ChecklistItem("item:A.5.3:review_date",       "Review date within the planned interval",                                             "must", False, "27002:5.3 — periodic review"),
        ChecklistItem("item:A.5.3:review_reviewer",   "Reviewer identity and role (typically risk owner or compliance lead with input from function leads)", "must", False, "Accountability"),
        ChecklistItem("item:A.5.3:review_outcome",    "Outcome per conflict pair (no change / amended / retired / new pair added)",          "must", False, "27002:5.3"),
        ChecklistItem("item:A.5.3:review_actions",    "Actions captured where compensating controls failed in practice (operational incidents, audit findings)", "must", False, "27002:5.3c — risk-based"),
    ],
    should_contain  = [
        ChecklistItem("item:A.5.3:review_triggers",   "Ad-hoc triggers listed (reorg, M&A, new business line, key role departure) prompting unscheduled review", "should", False, "Change-driven review"),
        ChecklistItem("item:A.5.3:review_next_date",  "Next planned review date stated",                                                     "should", False, "Planning"),
    ],
)

# ── Annex A.5.4 — Management responsibilities — policy_program 4-leaf ─────────
# Promoted 2026-05-29 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. policy_program spine: management
# directive (the artefact requiring all personnel to apply InfoSec) +
# approval + communication_record + periodic review. The directive leaf id is
# preserved; three siblings are new.
# Authority: ISO 27002:2022 § 5.4 implementation guidance items a–e; Clause
# 5.1 leadership commitment overlays approval.

REQ_A54_MANAGEMENT_DIRECTIVE = EvidenceRequirement(
    id            = "req:A.5.4:management_responsibilities",
    control_ref   = "A.5.4",
    standard_id   = "ISO27001:2022",
    evidence_type = "management_directive",
    title         = "Management Directive on Information Security Compliance",
    trigger_type  = "universal",
    description   = "A.5.4 requires management to require all personnel to apply information security per the policy framework. The directive itself is the artefact — a mandate letter, board statement, or equivalent that binds personnel to InfoSec policies. Approval, communication and periodic review are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.4:mandate_statement", "Statement that personnel are required to apply InfoSec policies, topic-specific policies, and procedures", "must", False, "27002:5.4 — require"),
        ChecklistItem("item:A.5.4:scope_personnel",   "Applicability to all personnel (employees, contractors, third parties acting on behalf of the organisation)", "must", False, "27002:5.4 — all personnel"),
        ChecklistItem("item:A.5.4:policy_references", "Names or references the in-scope policies, topic-specific policies, and procedures",     "must", False, "27002:5.4 — in accordance with"),
        ChecklistItem("item:A.5.4:competence_link",   "Link to competence and training requirement (A.7.2 / Clause 7.2) so personnel know how to comply", "must", False, "27002:5.4d"),
        ChecklistItem("item:A.5.4:enforcement",       "Statement of consequence for non-compliance (link to HR disciplinary process — A.6.4)",  "must", False, "27002:5.4e"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.4:risk_awareness",    "Expectation that personnel report identified risks and incidents (link to A.6.8)",       "should", False, "27002:5.4 — awareness"),
        ChecklistItem("item:A.5.4:role_specifics",    "Role-specific responsibilities cross-referenced (A.5.2 responsibility matrix)",          "should", False, "Cross-control coherence"),
    ],
)

REQ_A54_APPROVAL = EvidenceRequirement(
    id            = "req:A.5.4:management_approval",
    control_ref   = "A.5.4",
    standard_id   = "ISO27001:2022",
    evidence_type = "approval",
    title         = "Top Management Approval of the InfoSec Directive",
    trigger_type  = "universal",
    description   = "Clause 5.1 leadership commitment requires top management to demonstrate active sponsorship of the ISMS — the directive's authority derives from that sponsorship. The approval may be a signed cover page on the directive, a board minute, or a delegated equivalent that names a top-management signatory, a date, and the specific directive version being approved",
    must_contain  = [
        ChecklistItem("item:A.5.4:approval_signatory", "Signatory at top-management level (CEO, board chair, or delegated equivalent)",        "must", False, "Clause 5.1"),
        ChecklistItem("item:A.5.4:approval_date",      "Approval date recorded",                                                               "must", False, "Clause 5.1"),
        ChecklistItem("item:A.5.4:approval_target",    "Reference to the specific version of the management directive being approved",        "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.4:approval_authority", "Statement of the signatory's authority (delegation chain if not CEO)",                "should", False, "Accountability"),
    ],
)

REQ_A54_COMMUNICATION = EvidenceRequirement(
    id            = "req:A.5.4:communication_record",
    control_ref   = "A.5.4",
    standard_id   = "ISO27001:2022",
    evidence_type = "communication_record",
    title         = "Management Directive Communication Record",
    trigger_type  = "universal",
    description   = "A directive that personnel haven't seen is not an applied directive. Evidence must show active distribution to all personnel and, critically, that new personnel are reached at onboarding — not just availability of the directive on an intranet",
    must_contain  = [
        ChecklistItem("item:A.5.4:comm_date",         "Date of publication/communication",                                                    "must", False, "Operational sufficiency"),
        ChecklistItem("item:A.5.4:comm_audience",     "Audience reached (all personnel, including contractors and third parties in scope)",   "must", False, "27002:5.4 — all personnel"),
        ChecklistItem("item:A.5.4:comm_channel",      "Channel used (all-hands briefing, intranet publication, manager cascade, training module)", "must", False, "Operational sufficiency"),
        ChecklistItem("item:A.5.4:comm_onboarding",   "Distribution at onboarding for new personnel evidenced (induction pack, mandatory module)", "must", False, "27002:5.4 — new-joiner coverage"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.4:comm_acknowledgement","Personnel acknowledgement captured (signature, e-attestation, training completion)", "should", False, "Reinforces personal accountability"),
        ChecklistItem("item:A.5.4:comm_refresh",      "Periodic re-acknowledgement referenced (annual at minimum)",                           "should", False, "Ongoing reinforcement"),
    ],
)

REQ_A54_REVIEW = EvidenceRequirement(
    id              = "req:A.5.4:periodic_review",
    control_ref     = "A.5.4",
    standard_id     = "ISO27001:2022",
    evidence_type   = "review_record",
    title           = "Periodic Review of the Management Directive",
    trigger_type    = "universal",
    description     = "The directive must stay aligned with the policy framework it references — when policies are renamed, retired, or added the directive becomes stale. Review captures who reviewed, when, and whether the policy references and enforcement linkages still hold",
    freshness_days  = 365,
    must_contain    = [
        ChecklistItem("item:A.5.4:review_date",       "Review date within the planned interval",                                              "must", False, "Periodic review"),
        ChecklistItem("item:A.5.4:review_reviewer",   "Reviewer identity and role (typically CISO or compliance lead, validated by top management)", "must", False, "Accountability"),
        ChecklistItem("item:A.5.4:review_outcome",    "Outcome captured (no change / amended / re-issued) and policy-reference drift checked", "must", False, "Periodic review"),
        ChecklistItem("item:A.5.4:review_actions",    "Actions captured where the directive needed amendment (policy reorg, scope change, new personnel categories)", "must", False, "Continual improvement"),
    ],
    should_contain  = [
        ChecklistItem("item:A.5.4:review_triggers",   "Ad-hoc triggers listed (major policy reorg, M&A, regulatory change) prompting unscheduled review", "should", False, "Change-driven review"),
        ChecklistItem("item:A.5.4:review_next_date",  "Next planned review date stated",                                                      "should", False, "Planning"),
    ],
)

# ── Annex A.5.5 — Authority contacts — records_program spine (4-leaf) ─────────
# Promoted 2026-05-29 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. records_program spine (ratified
# 2026-05-28 via Art.30) adapted for an ISO register control: register +
# maintenance procedure + applicable-authorities scope (the upstream that
# drives the register's entries) + annual review. The register leaf id is
# preserved from the prior single-leaf definition; the three siblings are new.
# Authority: ISO 27002:2022 § 5.5 implementation guidance items a–c.

REQ_A55_AUTHORITY_REGISTER = EvidenceRequirement(
    id            = "req:A.5.5:authority_contact_register",
    control_ref   = "A.5.5",
    standard_id   = "ISO27001:2022",
    evidence_type = "contact_register",
    title         = "Authority Contact Register",
    trigger_type  = "universal",
    description   = "A.5.5 requires the organization to establish and maintain contact with relevant authorities. The register is the live source of truth for which authorities apply, who to reach, and on what trigger. Maintenance, the applicable-authorities scope and periodic review are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.5:authorities_listed", "Relevant authorities enumerated (DPA, sectoral regulator, law enforcement, CERT/CSIRT)",                  "must", False, "27002:5.5a"),
        ChecklistItem("item:A.5.5:contact_details",    "Current contact details per authority (name/role, phone, email, address)",                                "must", False, "27002:5.5a — contact details"),
        ChecklistItem("item:A.5.5:escalation_criteria","Engagement criteria per authority (incident classes, regulatory deadlines that require contact)",         "must", False, "27002:5.5b"),
        ChecklistItem("item:A.5.5:last_verified",      "Last-verified date per entry (proves the entry is current)",                                              "must", False, "27002:5.5 — maintained"),
        ChecklistItem("item:A.5.5:owner",              "Named owner responsible for the register",                                                                "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.5:backup_contacts",       "Backup or secondary contacts per authority",                                                            "should", False, "Continuity at time of incident"),
        ChecklistItem("item:A.5.5:notification_templates","Notification templates referenced per authority type",                                                  "should", False, "Speed at time of incident"),
        ChecklistItem("item:A.5.5:jurisdiction_tag",      "Each authority tagged with the jurisdiction(s) that drove its inclusion (links back to the scope leaf)","should", False, "Cross-leaf coherence"),
    ],
)

REQ_A55_MAINTENANCE_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.5:authority_contact_maintenance_procedure",
    control_ref   = "A.5.5",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Authority Contact Maintenance Procedure",
    trigger_type  = "universal",
    description   = "A.5.5 requires authority contact to be maintained, not just established once. The procedure documents who keeps the register current, what triggers an update, how new authorities enter the register when scope changes, and the activation path when an incident requires engagement",
    must_contain  = [
        ChecklistItem("item:A.5.5:proc_maintainer",          "Named maintainer of the register (compliance lead, security manager, or designate)",                            "must", False, "Accountability — 27002:5.5"),
        ChecklistItem("item:A.5.5:proc_update_triggers",     "Update triggers enumerated (new jurisdiction, new service line, regulator reorganisation, contact-change alert)","must", False, "27002:5.5 — maintained"),
        ChecklistItem("item:A.5.5:proc_intake_path",         "Intake path for adding a new authority (driven from the applicable-authorities scope leaf)",                    "must", False, "Operational sufficiency"),
        ChecklistItem("item:A.5.5:proc_activation_path",     "Activation path — who contacts whom on which trigger (incident category, regulatory deadline)",                 "must", False, "27002:5.5b — when to contact"),
        ChecklistItem("item:A.5.5:proc_verification_cadence","Re-verification cadence for contact details (annual at minimum)",                                                "must", False, "27002:5.5 — maintained"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.5:proc_drill",          "Periodic tabletop or drill of the activation path (proves the contact path works under pressure)", "should", False, "Effectiveness check"),
        ChecklistItem("item:A.5.5:proc_template_link", "Links to notification templates kept beside the procedure",                                          "should", False, "Speed at time of incident"),
        ChecklistItem("item:A.5.5:proc_change_log",    "Change-log requirement for any register edit so the audit trail is preserved",                       "should", False, "Auditability"),
    ],
)

REQ_A55_APPLICABLE_AUTHORITIES_SCOPE = EvidenceRequirement(
    id            = "req:A.5.5:applicable_authorities_scope",
    control_ref   = "A.5.5",
    standard_id   = "ISO27001:2022",
    evidence_type = "scope_note",
    title         = "Applicable Authorities Scope",
    trigger_type  = "universal",
    description   = "The upstream that drives the register. Documents which authorities are relevant today and on what basis — jurisdictions of operation, sectoral obligations, types of personal data processed, critical-service classifications. ISO 27002:2022 § 5.5 expects the organisation to know which authorities apply before claiming to maintain contact with them",
    must_contain  = [
        ChecklistItem("item:A.5.5:scope_jurisdictions",       "Jurisdictions covered (HQ, places of business, customer locations) — each maps to one or more authorities",        "must", False, "27002:5.5a — relevant"),
        ChecklistItem("item:A.5.5:scope_sectoral",            "Sectoral obligations stated (finance, health, critical infrastructure, telecoms) driving sectoral regulators",     "must", False, "27002:5.5a — relevant authorities"),
        ChecklistItem("item:A.5.5:scope_personal_data",       "Personal-data processing flag → drives DPA inclusion per jurisdiction",                                              "must", False, "GDPR Art.51 / 27002:5.5"),
        ChecklistItem("item:A.5.5:scope_authority_categories","Authority categories mapped — supervisory (DPA), sectoral regulator, law enforcement, national CERT/CSIRT",          "must", False, "27002:5.5a"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.5:scope_legal_register_link", "Cross-link to the legal/regulatory register (A.5.31) — same drivers; the two should stay aligned",                  "should", False, "Cross-control coherence"),
        ChecklistItem("item:A.5.5:scope_change_monitoring",   "Source for change monitoring (legal counsel, regulator alerts) that triggers re-scoping",                            "should", False, "Currency"),
    ],
)

REQ_A55_REVIEW = EvidenceRequirement(
    id              = "req:A.5.5:authority_contact_review",
    control_ref     = "A.5.5",
    standard_id     = "ISO27001:2022",
    evidence_type   = "review_record",
    title           = "Periodic Authority Contact Review",
    trigger_type    = "universal",
    description     = "Periodic verification that the register is still accurate, the scope is still correct, and the maintenance procedure is being followed. ISO 27002:2022 § 5.5 expects contact to be maintained — drift between register and reality is the audit failure mode this leaf catches",
    freshness_days  = 365,
    must_contain    = [
        ChecklistItem("item:A.5.5:rev_date",            "Review date within the planned interval (typically within 12 months of last review)",                   "must", False, "27002:5.5 — maintained"),
        ChecklistItem("item:A.5.5:rev_reviewer",        "Reviewer identity and role recorded",                                                                    "must", False, "Accountability"),
        ChecklistItem("item:A.5.5:rev_per_entry",       "Per-entry outcome (verified / amended / removed) and the verification method used",                     "must", False, "27002:5.5 — maintained"),
        ChecklistItem("item:A.5.5:rev_scope_check",     "Cross-check against the applicable-authorities scope (any new jurisdiction or sector that should add an entry)", "must", False, "Cross-leaf coherence"),
        ChecklistItem("item:A.5.5:rev_register_update", "Changes propagated back to the live register with reference to this review",                              "must", False, "Closes the loop"),
    ],
    should_contain  = [
        ChecklistItem("item:A.5.5:rev_ad_hoc_triggers","Ad-hoc review triggers listed (re-org, new geography, new sectoral obligation)", "should", False, "Change-driven review"),
        ChecklistItem("item:A.5.5:rev_next_date",      "Next planned review date stated",                                                  "should", False, "Planning"),
    ],
)

# ── Annex A.5.6 — SIG contacts — records_program spine (4-leaf) ───────────────
# Promoted 2026-05-29 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. records_program spine: register of
# memberships + engagement procedure + risk-topic scope (the upstream that
# justifies which SIGs to join) + annual engagement review. The register leaf
# id is preserved; three siblings are new.
# Authority: ISO 27002:2022 § 5.6 implementation guidance — value-driven
# engagement, not just paid memberships.

REQ_A56_SIG_REGISTER = EvidenceRequirement(
    id            = "req:A.5.6:special_interest_group_register",
    control_ref   = "A.5.6",
    standard_id   = "ISO27001:2022",
    evidence_type = "contact_register",
    title         = "Special Interest Group and Professional Forum Register",
    trigger_type  = "universal",
    description   = "A.5.6 requires contact with special interest groups (SIGs), security forums, and professional associations. The register lists current memberships and engagements with the basis for each. Engagement procedure, the risk-topic scope (which threats/skills drive the membership choices) and annual review are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.6:sigs_listed",      "SIGs and forums enumerated (ISACs, ISC2/ISACA chapters, vendor security groups, sector-specific councils)", "must", False, "27002:5.6a"),
        ChecklistItem("item:A.5.6:basis_of_contact", "Basis of contact per entry (paid membership, subscription, named-individual attendance, community access)", "must", False, "27002:5.6 — contact"),
        ChecklistItem("item:A.5.6:topics_shared",    "Topics or threat categories that drive each engagement",                                                     "must", False, "27002:5.6b — keep current"),
        ChecklistItem("item:A.5.6:last_engaged",     "Last-engaged date per entry (event attended, briefing received, working group meeting)",                     "must", False, "27002:5.6 — maintain"),
        ChecklistItem("item:A.5.6:owner",            "Named owner responsible for the register",                                                                  "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.6:representative",  "Internal representative or point of contact per group",                                                       "should", False, "Accountability"),
        ChecklistItem("item:A.5.6:renewal_dates",   "Subscription or membership renewal dates tracked",                                                            "should", False, "Continuity of access"),
        ChecklistItem("item:A.5.6:topic_tag",       "Each entry tagged with the risk topics that drove inclusion (links back to the scope leaf)",                  "should", False, "Cross-leaf coherence"),
    ],
)

REQ_A56_ENGAGEMENT_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.6:sig_engagement_procedure",
    control_ref   = "A.5.6",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "SIG Engagement Procedure",
    trigger_type  = "universal",
    description   = "A.5.6 expects active engagement, not nominal membership. The procedure documents how SIGs are joined, how value is captured back into the organisation (intel sharing into threat-intelligence A.5.7, runbook updates, training inputs) and how dormant memberships are pruned",
    must_contain  = [
        ChecklistItem("item:A.5.6:proc_join_path",         "Path to join a new SIG (business case linked to risk-topic scope, approval, budget allocation)",        "must", False, "Operational sufficiency"),
        ChecklistItem("item:A.5.6:proc_attendance",        "Attendance/participation expectations per membership (minimum events, working groups, briefings)",      "must", False, "27002:5.6 — maintain"),
        ChecklistItem("item:A.5.6:proc_value_capture",     "Value-capture path — how intelligence/insights flow back (cross-link to A.5.7 threat-intel procedure)", "must", False, "27002:5.6b / A.5.7"),
        ChecklistItem("item:A.5.6:proc_disengagement",     "Disengagement path for dormant or low-value memberships (avoid paying for unused subscriptions)",         "must", False, "27002:5.6 — appropriate"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.6:proc_confidentiality",   "Confidentiality expectations when sharing internal info to SIGs (TLP labelling, NDA awareness)",        "should", False, "Information leakage avoidance"),
        ChecklistItem("item:A.5.6:proc_training_link",     "Link to training programme (A.6.3) for representatives who attend on behalf of the org",                "should", False, "Effectiveness"),
    ],
)

REQ_A56_RISK_TOPIC_SCOPE = EvidenceRequirement(
    id            = "req:A.5.6:risk_topic_scope",
    control_ref   = "A.5.6",
    standard_id   = "ISO27001:2022",
    evidence_type = "scope_note",
    title         = "SIG Engagement Risk-Topic Scope",
    trigger_type  = "universal",
    description   = "The upstream that drives the register. Documents the threat categories, technology stack components, sectoral concerns and skill domains that justify each SIG membership. ISO 27002:2022 § 5.6 expects engagement to be relevant — random or legacy memberships fail the test",
    must_contain  = [
        ChecklistItem("item:A.5.6:scope_threat_categories", "Threat categories prioritised (ransomware, supply-chain, insider, sector-specific) that justify SIG choices", "must", False, "27002:5.6 — relevant"),
        ChecklistItem("item:A.5.6:scope_tech_stack",        "Technology-stack components for which vendor/community SIGs are valuable (cloud, OS, network, OT/IoT)",      "must", False, "27002:5.6b"),
        ChecklistItem("item:A.5.6:scope_sectoral",          "Sectoral concerns (finance ISAC, health ISAC, critical infra forum) driving sector-specific memberships",      "must", False, "27002:5.6 — relevant"),
        ChecklistItem("item:A.5.6:scope_skill_domains",     "Professional development / skill domains (CISO peer groups, secure-coding communities) driving professional memberships","must", False, "27002:5.6"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.6:scope_threat_intel_link", "Cross-link to threat-intelligence procedure (A.5.7) — the two scopes should share drivers",                  "should", False, "Cross-control coherence"),
        ChecklistItem("item:A.5.6:scope_change_trigger",    "Trigger for re-scoping (new tech adoption, new sector entry, emerging threat class)",                         "should", False, "Currency"),
    ],
)

REQ_A56_REVIEW = EvidenceRequirement(
    id              = "req:A.5.6:sig_engagement_review",
    control_ref     = "A.5.6",
    standard_id     = "ISO27001:2022",
    evidence_type   = "review_record",
    title           = "Periodic SIG Engagement Review",
    trigger_type    = "universal",
    description     = "Periodic check that memberships are still earning their place. Each entry is reviewed for value delivered, currency of contact, and continued relevance against the risk-topic scope. Dormant memberships are pruned; gaps where a new SIG should be joined are flagged",
    freshness_days  = 365,
    must_contain    = [
        ChecklistItem("item:A.5.6:rev_date",            "Review date within the planned interval",                                                             "must", False, "27002:5.6 — maintain"),
        ChecklistItem("item:A.5.6:rev_reviewer",        "Reviewer identity and role recorded",                                                                  "must", False, "Accountability"),
        ChecklistItem("item:A.5.6:rev_per_entry",       "Per-entry outcome (continue / disengage / upgrade) with value-delivered notes (intel received, contributions made)", "must", False, "27002:5.6 — appropriate"),
        ChecklistItem("item:A.5.6:rev_scope_check",     "Cross-check against the risk-topic scope — any new threat or domain that should add a SIG",            "must", False, "Cross-leaf coherence"),
        ChecklistItem("item:A.5.6:rev_register_update", "Changes propagated back to the register",                                                              "must", False, "Closes the loop"),
    ],
    should_contain  = [
        ChecklistItem("item:A.5.6:rev_ad_hoc_triggers","Ad-hoc review triggers listed (key representative departure, new threat class, budget cycle)",         "should", False, "Change-driven review"),
        ChecklistItem("item:A.5.6:rev_next_date",      "Next planned review date stated",                                                                       "should", False, "Planning"),
    ],
)

# ── Annex A.5.7 — Threat intelligence — operational_process (4-leaf) ──────────
# Promoted 2026-05-31 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: operational_process → procedure
# + register + review_record + revocation_record (lifecycle-end). The
# lifecycle-end slot is realised as the per-product intelligence record — the
# actual deliverable (IOC list, threat briefing, advisory) that proves the
# program is producing value tied to named consumers. Program review tightened
# to 180d (same rationale as A.5.25 + A.5.26 — detection landscape volatility:
# feed quality shifts, IOC libraries age within weeks, new TTPs emerge inside
# the quarter). The procedure leaf id is preserved; three siblings are new.
# Authority: ISO 27002:2022 § 5.7 implementation guidance (three layers —
# strategic / tactical / operational; activities — sources, collection,
# analysis, communication, sharing).

REQ_A57_THREAT_INTELLIGENCE_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.7:threat_intelligence_procedure",
    control_ref   = "A.5.7",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Threat Intelligence Programme Procedure",
    trigger_type  = "universal",
    description   = "A.5.7 requires information about information security threats to be collected and analysed to produce threat intelligence across strategic, tactical and operational layers. The procedure documents sources, collection cadence, analysis approach, the three intelligence layers, distribution to named consumers, and the feedback loop into risk and operational controls. The feed register, periodic program review and per-product intelligence records are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.7:sources",          "Threat intelligence sources enumerated (open-source feeds, vendor feeds, ISACs, government advisories, paid intel services)", "must", False, "27002:5.7 — sources establishment"),
        ChecklistItem("item:A.5.7:layers",           "Three intelligence layers covered: strategic (sector/long-term), tactical (attacker methodologies/TTPs), operational (specific attack details/IOCs)", "must", False, "27002:5.7 — three layers"),
        ChecklistItem("item:A.5.7:collection_cadence","Collection cadence stated per source (continuous, daily, weekly)", "must", False, "27002:5.7 — collection"),
        ChecklistItem("item:A.5.7:analysis_approach","Analysis approach defined (relevance to org assets, integrity verification, completeness, correlation, prioritisation)", "must", False, "27002:5.7 — analysis"),
        ChecklistItem("item:A.5.7:products",         "Intelligence products defined per layer (IOC lists, TTP signatures, threat briefings, sector advisories)", "must", False, "27002:5.7 — produce threat intelligence"),
        ChecklistItem("item:A.5.7:distribution",     "Distribution path to named consumers (security ops, IT/network, risk owners, exec briefing)", "must", False, "27002:5.7 — communication"),
        ChecklistItem("item:A.5.7:control_use",      "Use into technical controls (firewall blocklists, IDS rules, EDR indicators, vulnerability prioritisation)", "must", False, "27002:5.7 — informed defensive action"),
        ChecklistItem("item:A.5.7:risk_feedback",    "Feedback loop into the risk register / risk assessment (intel that surfaces new exposures triggers reassessment)", "must", False, "27002:5.7 — informed risk treatment"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.7:sharing",          "Outbound intelligence sharing path (ISAC contributions, peer briefings)", "should", False, "27002:5.7 — sharing of analysed intel"),
        ChecklistItem("item:A.5.7:exercise_input",   "Use into exercises / tabletop scenarios (intel informs realistic scenarios)", "should", False, "27002:5.7 — exercise planning"),
        ChecklistItem("item:A.5.7:product_retention","Retention period for intelligence products stated (often shorter than other compliance records — IOC libraries age fast)", "should", False, "Audit + lookback proportional to relevance"),
    ],
)

REQ_A57_FEED_REGISTER = EvidenceRequirement(
    id            = "req:A.5.7:threat_intel_feed_register",
    control_ref   = "A.5.7",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Threat Intelligence Feed Register",
    trigger_type  = "universal",
    description   = "A.5.7 requires a curated set of sources, not an ad-hoc list. The feed register catalogues every active intelligence source with metadata that allows the program review to assess which feeds deliver value: source name, layer, owner inside the org, last received signal, cost, signal/noise rating. Decommissioned feeds are retained with end-date for traceability",
    must_contain  = [
        ChecklistItem("item:A.5.7:reg_source_id",      "Each active source captured with a unique identifier",                                                                  "must", False, "27002:5.7 — sources"),
        ChecklistItem("item:A.5.7:reg_layer",          "Intelligence layer per row (strategic / tactical / operational)",                                                       "must", False, "27002:5.7 — three layers"),
        ChecklistItem("item:A.5.7:reg_owner",          "Internal owner per row accountable for the source (renewal, escalation, value assessment)",                             "must", False, "Accountability"),
        ChecklistItem("item:A.5.7:reg_last_received",  "Last-received timestamp per row (stale-feed detection)",                                                                "must", False, "27002:5.7 — collection cadence verified"),
        ChecklistItem("item:A.5.7:reg_cost",           "Cost per row (paid feeds vs free) — required for value review",                                                          "must", False, "Program economics"),
        ChecklistItem("item:A.5.7:reg_signal_rating",  "Signal/noise rating per row (high/medium/low) updated at each program review",                                          "must", False, "27002:5.7 — relevance"),
        ChecklistItem("item:A.5.7:reg_internal_input", "Internal sources captured alongside external (e.g. A.5.6 SIG-membership outputs, internal IR observations)",            "must", False, "27002:5.7 — internal/external balance"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.7:reg_decommissioned", "Decommissioned sources retained with end-date and reason (audit trail)",                                                 "should", False, "Operational discipline"),
        ChecklistItem("item:A.5.7:reg_contact",        "Contact per row (vendor support, ISAC liaison)",                                                                         "should", False, "Operational continuity"),
    ],
)

REQ_A57_PROGRAM_REVIEW = EvidenceRequirement(
    id             = "req:A.5.7:threat_intel_program_review",
    control_ref    = "A.5.7",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic Threat Intelligence Program Review",
    trigger_type   = "universal",
    description    = "The threat intelligence program creates value only if it closes the loop into defensive action — feeds get retired when stale, consumer feedback drives product changes, and analysis effort tracks the threats relevant to the org. The review captures the planned-interval check: feed-value analysis, products delivered, consumer feedback, missed-event analysis, and resulting program adjustments. Cadence tightened to 180 days — detection landscape volatility outpaces annual cycles",
    freshness_days = 180,
    must_contain   = [
        ChecklistItem("item:A.5.7:rev_date",              "Review date within the planned 180-day interval",                                                                    "must", False, "27002:5.7 — periodic"),
        ChecklistItem("item:A.5.7:rev_reviewer",          "Reviewer identity (program owner + InfoSec lead jointly)",                                                            "must", False, "Accountability"),
        ChecklistItem("item:A.5.7:rev_feed_value",        "Feed-value analysis per source (which feeds delivered actionable IOCs / advisories; which were dropped)",            "must", False, "27002:5.7 — sources curation"),
        ChecklistItem("item:A.5.7:rev_products_delivered","Products delivered count and distribution evidenced (proves the program ran, not just the procedure existed)",      "must", False, "27002:5.7 — produce threat intelligence"),
        ChecklistItem("item:A.5.7:rev_consumer_feedback", "Consumer feedback collected from named consumers (sec ops, A.5.21 supplier risk, A.5.25 detection, exec briefing)", "must", False, "27002:5.7 — communication effectiveness"),
        ChecklistItem("item:A.5.7:rev_missed",            "Missed-event analysis (events surfaced by A.5.25 triage or A.5.27 lessons that intel didn't flag in advance)",       "must", False, "Closing the loop with [[A.5.25]] / [[A.5.27]]"),
        ChecklistItem("item:A.5.7:rev_actions",           "Action items captured for the program (e.g. add new feed, retire stale source, tune analysis cadence)",              "must", False, "27002:5.7 — program adjustments"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.7:rev_landscape",         "External threat-landscape snapshot considered (industry reports, vendor briefings)",                                 "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.7:rev_next_date",         "Next planned review date stated (within 180d of this review)",                                                       "should", False, "Planning"),
    ],
)

REQ_A57_INTEL_PRODUCT_RECORD = EvidenceRequirement(
    id            = "req:A.5.7:intel_product_record",
    control_ref   = "A.5.7",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Per-Product Intelligence Records",
    trigger_type  = "universal",
    description   = "A.5.7 expects intelligence to actually reach consumers and inform defensive action — not just be produced and filed. The per-product record evidences each delivered artefact: product id, layer, source feeds aggregated, named consumer(s), distribution date, action taken downstream (firewall rule pushed / IDS signature added / risk register entry / exec briefing). One record per published product, traceable back to the feed register and forward to the consumer's control",
    must_contain  = [
        ChecklistItem("item:A.5.7:prod_id",            "Product identifier per record (unique, sequenced)",                                                                    "must", False, "27002:5.7 — produce threat intelligence"),
        ChecklistItem("item:A.5.7:prod_layer",         "Intelligence layer per record (strategic / tactical / operational)",                                                   "must", False, "27002:5.7 — three layers"),
        ChecklistItem("item:A.5.7:prod_sources",       "Source feeds aggregated per record (links to feed register entries)",                                                  "must", False, "27002:5.7 — sources traceability"),
        ChecklistItem("item:A.5.7:prod_consumer",      "Named consumer(s) per record (sec ops, IT/network, risk owners, exec briefing)",                                       "must", False, "27002:5.7 — communication"),
        ChecklistItem("item:A.5.7:prod_distribution",  "Distribution date and channel per record (email, ticket, briefing)",                                                   "must", False, "27002:5.7 — delivered"),
        ChecklistItem("item:A.5.7:prod_action_taken",  "Action taken downstream per record (firewall rule / IDS signature / risk register entry / control update / no-op)",   "must", False, "27002:5.7 — informed defensive action"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.7:prod_effectiveness", "Effectiveness check planned or recorded (post-distribution validation that the product drove the intended action)",   "should", False, "Continual improvement"),
        ChecklistItem("item:A.5.7:prod_retention_end", "Retention end-date noted (IOC libraries age fast — old products marked for archive/disposal)",                          "should", False, "Operational discipline"),
    ],
)

# ── Annex A.5.8 — Information security in project management — operational_process (4-leaf) ──
# Promoted 2026-05-31 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: operational_process → procedure
# + register + review_record + revocation_record (lifecycle-end). The
# lifecycle-end slot is realised as the per-project closure security signoff
# — the gate evidence proving each project handed over to operations with
# security accountability transferred and residual risks accepted. The
# procedure leaf id is preserved; three siblings are new.
#
# Review freshness 365d — project management methodologies are stable.
# Unlike detection/IR (180d) where the underlying landscape moves fast,
# the gate framework + roles + deliverables here change only when the org
# adopts a new PM methodology or learns a structural lesson. Annual cadence
# with project owners + InfoSec + Legal jointly is right-sized.
#
# Cross-control: register references A.8.25/A.8.26 SDLC outputs where the
# project involves software development; closure_record links to A.5.20
# supplier agreements (project-driven contracts) and A.5.23 cloud register
# (cloud-shaped projects) — encoded as MUST items inline.
#
# Authority: ISO 27002:2022 § 5.8 implementation guidance (integrate at
# project initiation, throughout the lifecycle, on closure; risk assessment
# + acceptance per project; defined responsibilities; clear deliverables).

REQ_A58_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.8:project_management_security_integration",
    control_ref   = "A.5.8",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Information Security in Project Management Procedure",
    trigger_type  = "universal",
    description   = "A.5.8 requires information security to be integrated into project management across the full lifecycle: initiation, requirements, design/build, pre-go-live assessment, closure handover. The procedure documents gates, deliverables, roles, tiering rules and acceptance criteria. The project register, periodic program review and per-project closure record are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.8:initiation_gate",       "Security gate at project initiation (risk assessment, classification of information, scope of personal data if applicable)",  "must", False, "27002:5.8 — integrated at initiation"),
        ChecklistItem("item:A.5.8:requirements",          "Security requirements captured in project plan / requirements document (functional + non-functional, including data protection)", "must", False, "27002:5.8 — integrated"),
        ChecklistItem("item:A.5.8:assessment_pre_golive", "Security assessment before go-live (pen test, control verification, residual-risk acceptance)",                                  "must", False, "27002:5.8 — throughout lifecycle"),
        ChecklistItem("item:A.5.8:role",                  "Information security role defined in the project governance (advisor / reviewer / gate-owner with veto authority where warranted)", "must", False, "27002:5.8 — defined responsibilities"),
        ChecklistItem("item:A.5.8:closure_signoff",       "Project closure security sign-off step (handover to operations; outstanding-risk transfer documented)",                            "must", False, "27002:5.8 — closure"),
        ChecklistItem("item:A.5.8:acceptance_criteria",   "Risk-acceptance criteria stated (when residual risk forces escalation; named approver per tier)",                                  "must", False, "27002:5.8 — risk acceptance per project"),
        ChecklistItem("item:A.5.8:change_control",        "In-project change control step (scope/security-impact changes during build trigger re-assessment, not late-detection)",            "must", False, "27002:5.8 — throughout lifecycle"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.8:tiering",               "Project tiering (which projects need full vs lightweight security review; criteria based on data sensitivity, regulatory scope, third-party exposure)", "should", False, "27002:5.8 — proportionality"),
        ChecklistItem("item:A.5.8:templates",             "Standard project templates referenced (security sections in initiation pack, requirements template, closure checklist)",          "should", False, "Consistency"),
        ChecklistItem("item:A.5.8:agile_integration",     "Adaptation for agile/iterative delivery (continuous security touchpoints rather than waterfall gates only)",                      "should", False, "Modern delivery practice"),
    ],
)

REQ_A58_PROJECT_REGISTER = EvidenceRequirement(
    id            = "req:A.5.8:project_security_register",
    control_ref   = "A.5.8",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Project Security Register",
    trigger_type  = "universal",
    description   = "A.5.8 requires every project to be visible to the security function — invisible projects are the ones that miss gates. The register catalogues every in-scope project: id, name, security tier, current stage, owner, InfoSec liaison, planned closure date, status. It is the operational record that proves the gate process is actually applied org-wide, not just on the projects InfoSec happens to hear about",
    must_contain  = [
        ChecklistItem("item:A.5.8:reg_project_id",        "Each in-scope project captured with a unique identifier",                                                                       "must", False, "27002:5.8 — visibility"),
        ChecklistItem("item:A.5.8:reg_tier",              "Security tier per row (drives which gates apply — full / lightweight / waived-with-justification)",                            "must", False, "27002:5.8 — proportionality"),
        ChecklistItem("item:A.5.8:reg_stage",             "Current stage per row (initiation / requirements / build / pre-go-live / live / closed) updated as gates are passed",          "must", False, "27002:5.8 — lifecycle tracking"),
        ChecklistItem("item:A.5.8:reg_owner",             "Project owner per row (named individual accountable for delivery + security)",                                                  "must", False, "Accountability"),
        ChecklistItem("item:A.5.8:reg_infosec_liaison",   "InfoSec liaison per row (named individual reviewing this project's security gates)",                                            "must", False, "27002:5.8 — defined responsibilities"),
        ChecklistItem("item:A.5.8:reg_sdlc_link",         "SDLC link per row where project involves software development (cross-ref to A.8.25 / A.8.26 outputs)",                          "must", False, "27002:5.8 + cross-link to [[A.8.25]] / [[A.8.26]]"),
        ChecklistItem("item:A.5.8:reg_planned_closure",   "Planned closure date per row (drives the closure-gate trigger)",                                                                 "must", False, "Operational discipline"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.8:reg_supplier_link",     "Supplier-agreement link per row where project triggers new third-party contracts (cross-ref to A.5.20)",                       "should", False, "Closing loop with [[A.5.20]]"),
        ChecklistItem("item:A.5.8:reg_cloud_link",        "Cloud-service link per row where project introduces a new cloud service (cross-ref to A.5.23 cloud register)",                  "should", False, "Closing loop with [[A.5.23]]"),
    ],
)

REQ_A58_PROGRAM_REVIEW = EvidenceRequirement(
    id             = "req:A.5.8:project_security_program_review",
    control_ref    = "A.5.8",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic Project-Security Program Review",
    trigger_type   = "universal",
    description    = "The gate process creates value only if it's catching things — projects with skipped gates, late-detected security issues, and tiering-misclassifications all signal the program is leaking. The review captures the planned-interval check: gate-skip rate, late-detection analysis, tier-mix shifts, InfoSec capacity vs project demand, and resulting program adjustments. Annual cadence — methodology stability outweighs short-cycle drift",
    freshness_days = 365,
    must_contain   = [
        ChecklistItem("item:A.5.8:rev_date",              "Review date within the planned annual interval",                                                                                "must", False, "27002:5.8 — periodic"),
        ChecklistItem("item:A.5.8:rev_reviewer",          "Reviewer identity (InfoSec lead + PMO/project office head jointly)",                                                            "must", False, "Accountability"),
        ChecklistItem("item:A.5.8:rev_gate_skip",         "Gate-skip rate analysed (projects that bypassed gates; root cause and remediation per skip)",                                    "must", False, "27002:5.8 — assurance"),
        ChecklistItem("item:A.5.8:rev_late_detection",    "Late-detection analysis (security issues surfaced at or after go-live that should have been caught earlier)",                    "must", False, "Program effectiveness"),
        ChecklistItem("item:A.5.8:rev_tiering",           "Tiering audit (sample of projects re-tiered to validate the tier criteria are still calibrated to actual risk)",                "must", False, "27002:5.8 — proportionality calibration"),
        ChecklistItem("item:A.5.8:rev_capacity",          "InfoSec capacity vs project pipeline reviewed (gates fail silently when reviewer capacity is exhausted)",                       "must", False, "27002:5.8 — sustainable defined responsibilities"),
        ChecklistItem("item:A.5.8:rev_actions",           "Action items captured for the program (e.g. update templates, retrain PMs, tighten tiering criteria, add reviewer capacity)",   "must", False, "27002:5.8 — program adjustments"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.8:rev_methodology",       "Methodology check (does the gate model still fit the org's delivery mix — waterfall vs agile vs hybrid)",                       "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.8:rev_next_date",         "Next planned review date stated",                                                                                                "should", False, "Planning"),
    ],
)

REQ_A58_CLOSURE_RECORD = EvidenceRequirement(
    id            = "req:A.5.8:project_security_closure_record",
    control_ref   = "A.5.8",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Per-Project Security Closure Record",
    trigger_type  = "universal",
    description   = "A.5.8 expects each project to formally close out security — not just go-live and dissolve the team. The closure record evidences the handover gate: project id, gates passed, outstanding risks transferred to operations with named owner, security artefacts archived, and final signoff. One record per closed project, traceable back to the project register and through to operational ownership",
    must_contain  = [
        ChecklistItem("item:A.5.8:cls_project_ref",       "Project identifier per record (links to project register)",                                                                    "must", False, "27002:5.8 — traceability"),
        ChecklistItem("item:A.5.8:cls_gates_passed",      "Gates-passed summary per record (which gates closed and when; gaps explicitly noted with risk acceptance)",                     "must", False, "27002:5.8 — lifecycle closure"),
        ChecklistItem("item:A.5.8:cls_residual_risks",    "Residual-risk register transfer per record (outstanding risks named, accepted by named operational owner with date)",          "must", False, "27002:5.8 — risk acceptance + transfer"),
        ChecklistItem("item:A.5.8:cls_artefacts_archived","Security artefacts archived per record (threat model, pen-test report, DPIA where applicable, exception register)",            "must", False, "Audit defensibility"),
        ChecklistItem("item:A.5.8:cls_signoff",           "Final signoff per record (project sponsor + InfoSec gate-owner + operational owner — three-way)",                              "must", False, "27002:5.8 — closure handover"),
        ChecklistItem("item:A.5.8:cls_closure_date",      "Closure date recorded",                                                                                                          "must", False, "Operational discipline"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.8:cls_supplier_handover", "Supplier-agreement handover per record where project introduced new third-party contracts (operational owner takes A.5.22 review duty)", "should", False, "Closing loop with [[A.5.22]]"),
        ChecklistItem("item:A.5.8:cls_lessons_link",      "Lessons-learned link per record where project surfaced patterns worth feeding into A.5.27 lessons register",                    "should", False, "Closing loop with [[A.5.27]]"),
    ],
)

# ── Annex A.5.9 — Asset inventory — records_program spine (4-leaf) ────────────
# Promoted 2026-05-29 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. records_program spine: the asset
# register + lifecycle procedure + discovery/onboarding upstream + periodic
# reconciliation review. The register leaf id is preserved; three siblings new.
# Deviation from default freshness model: the register keeps freshness=90
# (asset state drifts daily; the register itself must show evidence of active
# maintenance), and the reconciliation review carries its own freshness=90
# (quarterly reconciliation against discovery scans). This is stricter than
# the records_program default — justified because asset inventory is the
# foundation for half the Annex A controls and stale rows cascade into A.5.12
# classification gaps, A.8.16 monitoring gaps, A.8.20 network mapping gaps.
# Authority: ISO 27002:2022 § 5.9 implementation guidance.

REQ_A59_ASSET_REGISTER = EvidenceRequirement(
    id            = "req:A.5.9:asset_inventory",
    control_ref   = "A.5.9",
    standard_id   = "ISO27001:2022",
    evidence_type = "asset_register",
    title         = "Inventory of Information and Associated Assets",
    trigger_type  = "universal",
    description   = "A.5.9 requires an inventory of information and associated assets — including owners — developed and maintained. The register is the live record. Lifecycle procedure, the discovery/onboarding upstream and reconciliation review are sibling leaves",
    freshness_days = 90,
    must_contain  = [
        ChecklistItem("item:A.5.9:asset_records",   "Asset records exist (information assets, software, hardware, services, cloud resources)",            "must", False, "27002:5.9a"),
        ChecklistItem("item:A.5.9:owner_per_asset", "Owner named per asset (individual or role accountable for protection and risk decisions)",          "must", False, "27002:5.9d — including owners"),
        ChecklistItem("item:A.5.9:classification",  "Classification per asset (links to the A.5.12 classification scheme)",                              "must", False, "27002:5.9c / A.5.12"),
        ChecklistItem("item:A.5.9:location",        "Location or hosting system where the asset resides (data centre, cloud region, endpoint pool)",     "must", False, "27002:5.9b"),
        ChecklistItem("item:A.5.9:last_updated",    "Last-updated date per record (proves the register is actively maintained, not snapshotted)",       "must", False, "27002:5.9 — maintained"),
        ChecklistItem("item:A.5.9:asset_type",      "Asset type tag (information / software / hardware / service / facility) so type-specific controls can be applied", "must", False, "27002:5.9 — categorisation"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.9:lifecycle_status","Lifecycle status per asset (active, retired, in-procurement, in-disposal)",                          "should", False, "Operational completeness"),
        ChecklistItem("item:A.5.9:dependencies",    "Dependency or relationship to other assets (supports A.8.x topology and risk mapping)",              "should", False, "Risk traceability"),
        ChecklistItem("item:A.5.9:dfi_link",        "Cross-link to GDPR Art.30 data flow inventory where the asset holds personal data",                  "should", False, "Cross-control coherence"),
    ],
)

REQ_A59_LIFECYCLE_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.9:asset_lifecycle_procedure",
    control_ref   = "A.5.9",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Asset Lifecycle Management Procedure",
    trigger_type  = "universal",
    description   = "A.5.9 requires the register to be maintained — the lifecycle procedure documents how assets enter, change and leave the register. Covers procurement intake, ownership transfer, classification at creation/change, retirement and disposal handoff (A.7.14 / A.8.10)",
    must_contain  = [
        ChecklistItem("item:A.5.9:proc_intake",        "Intake path — every new asset (procured, built, granted) is registered before going operational",                "must", False, "27002:5.9 — develop"),
        ChecklistItem("item:A.5.9:proc_ownership",     "Ownership assignment rules (who can be an owner, transfer process on role change)",                              "must", False, "27002:5.9d / Clause 5.3"),
        ChecklistItem("item:A.5.9:proc_classification","Classification at creation and on material change (cross-link to A.5.12)",                                       "must", False, "27002:5.9c / A.5.12"),
        ChecklistItem("item:A.5.9:proc_retirement",    "Retirement and disposal handoff (status set to retired, disposal handled per A.7.14/A.8.10, register row archived)","must", False, "27002:5.9 / A.7.14 / A.8.10"),
        ChecklistItem("item:A.5.9:proc_maintainer",    "Named maintainer of the register and escalation path when intake fails",                                          "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.9:proc_shadow_it",     "Shadow-IT handling — unregistered assets discovered in scans are blocked, registered, or removed",                "should", False, "Drift prevention"),
        ChecklistItem("item:A.5.9:proc_cloud_provision","Cloud-provisioning hooks (IaC pipelines auto-register infra; manual creations require a register entry first)", "should", False, "Cloud completeness"),
    ],
)

REQ_A59_DISCOVERY_UPSTREAM = EvidenceRequirement(
    id            = "req:A.5.9:asset_discovery_upstream",
    control_ref   = "A.5.9",
    standard_id   = "ISO27001:2022",
    evidence_type = "discovery_record",
    title         = "Asset Discovery and Onboarding Upstream",
    trigger_type  = "universal",
    description   = "The upstream that feeds the register. Where the lifecycle procedure covers intake of known new assets, the discovery upstream documents how the org finds assets it didn't already know about — network scans, cloud-tenant inventory APIs, procurement export, endpoint-management exports — and how those feeds reconcile into the register",
    must_contain  = [
        ChecklistItem("item:A.5.9:disc_sources",        "Discovery sources enumerated (network scan tool, CSPM tool, EDR/MDM inventory, procurement system, license database)", "must", False, "27002:5.9 — develop"),
        ChecklistItem("item:A.5.9:disc_cadence",        "Discovery cadence per source (continuous / daily / weekly)",                                                          "must", False, "27002:5.9 — maintained"),
        ChecklistItem("item:A.5.9:disc_reconciliation", "Reconciliation rule — discovered-but-not-in-register entries are flagged for owner assignment and classification",   "must", False, "Closes the discovery loop"),
        ChecklistItem("item:A.5.9:disc_scope_coverage", "Coverage statement — what categories of assets each source covers and where gaps exist (e.g., personal devices, OT)", "must", False, "27002:5.9 — completeness"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.9:disc_a812_link",      "Cross-link to A.8.12 (data leakage prevention) or A.8.20 (network mapping) where those scans double as discovery",  "should", False, "Cross-control coherence"),
        ChecklistItem("item:A.5.9:disc_gap_remediation","Process for closing coverage gaps (procuring new tools, mandating registration in ungovernable zones)",              "should", False, "Continuous improvement"),
    ],
)

REQ_A59_RECONCILIATION_REVIEW = EvidenceRequirement(
    id              = "req:A.5.9:asset_reconciliation_review",
    control_ref     = "A.5.9",
    standard_id     = "ISO27001:2022",
    evidence_type   = "review_record",
    title           = "Periodic Asset Inventory Reconciliation",
    trigger_type    = "universal",
    description     = "Periodic reconciliation of the register against discovery feeds. The cadence is quarterly (freshness=90) because asset drift is daily and the register's value collapses fast without reconciliation. Annual review is insufficient for this control. Outputs feed back into the register and into procurement / cloud-provisioning hooks",
    freshness_days  = 90,
    must_contain    = [
        ChecklistItem("item:A.5.9:rev_date",            "Reconciliation date within the planned interval (typically within 90 days of last reconciliation)",                "must", False, "27002:5.9 — maintained"),
        ChecklistItem("item:A.5.9:rev_reviewer",        "Reviewer identity and role recorded",                                                                                "must", False, "Accountability"),
        ChecklistItem("item:A.5.9:rev_per_source",      "Per-source delta — what each discovery source surfaced vs what the register held (additions, removals, mismatches)","must", False, "27002:5.9 — develop and maintain"),
        ChecklistItem("item:A.5.9:rev_unassigned_owner","Treatment of unassigned-owner rows (owner assignment forced or row retired)",                                        "must", False, "27002:5.9d"),
        ChecklistItem("item:A.5.9:rev_register_update", "Register updated as a result of the reconciliation with reference to this review",                                  "must", False, "Closes the loop"),
    ],
    should_contain  = [
        ChecklistItem("item:A.5.9:rev_classification_check","Classification sampling check — are A.5.12 classifications still appropriate for the asset's actual use",       "should", False, "A.5.12 / drift catch"),
        ChecklistItem("item:A.5.9:rev_next_date",       "Next planned reconciliation date stated",                                                                            "should", False, "Planning"),
    ],
)

# ── Annex A.5.10 — Acceptable use — policy_program 4-leaf ─────────────────────
# Promoted 2026-05-29 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. policy_program spine: AUP + approval +
# communication_record + periodic review. The policy leaf id is preserved; the
# three siblings are new. Acceptable-use cases hinge on the user having seen
# and acknowledged the rules, so the communication leaf is load-bearing.
# Authority: ISO 27002:2022 § 5.10 implementation guidance.

REQ_A510_POLICY = EvidenceRequirement(
    id            = "req:A.5.10:acceptable_use_policy",
    control_ref   = "A.5.10",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Acceptable Use Policy",
    trigger_type  = "universal",
    description   = "A.5.10 requires rules for acceptable use and procedures for handling information and associated assets. The AUP covers both general principles and the handling rules per asset/information class. Approval, communication and periodic review are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.10:scope",              "Scope of the policy (which assets, which users — employees / contractors / third parties — which information classes)", "must", False, "27002:5.10 — scope"),
        ChecklistItem("item:A.5.10:acceptable_uses",    "Acceptable use rules stated (work purposes, identified personal-use boundaries, BYOD where applicable)",               "must", False, "27002:5.10a"),
        ChecklistItem("item:A.5.10:prohibited_uses",    "Prohibited use rules stated (unlawful, harmful, security-bypassing activities, unauthorised software)",                "must", False, "27002:5.10b"),
        ChecklistItem("item:A.5.10:handling_procedures","Handling procedures per information class (storage, transmission, retention, disposal) aligned with A.5.12",          "must", False, "27002:5.10 — handling"),
        ChecklistItem("item:A.5.10:monitoring",         "Monitoring expectations stated transparently (what the org may inspect, under what conditions)",                       "must", False, "27002:5.10c — monitoring transparency"),
        ChecklistItem("item:A.5.10:enforcement",        "Enforcement and disciplinary consequences referenced (link to A.6.4 disciplinary process)",                            "must", False, "27002:5.10 — implemented"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.10:byod",             "BYOD provisions where personal devices are used for work",                                                                "should", False, "Modern workforce"),
        ChecklistItem("item:A.5.10:social_media",     "Social media usage and corporate-information disclosure rules",                                                          "should", False, "Reputational risk"),
        ChecklistItem("item:A.5.10:remote_work",      "Remote and teleworking provisions where physical environment is outside the org's control",                              "should", False, "27002:5.10 — context"),
    ],
)

REQ_A510_APPROVAL = EvidenceRequirement(
    id            = "req:A.5.10:management_approval",
    control_ref   = "A.5.10",
    standard_id   = "ISO27001:2022",
    evidence_type = "approval",
    title         = "Management Approval of the Acceptable Use Policy",
    trigger_type  = "universal",
    description   = "AUPs are enforceable only when management has explicitly approved them — the approval establishes the authority behind the disciplinary consequences. The approval names a signatory at the appropriate management level, a date, and the specific policy version",
    must_contain  = [
        ChecklistItem("item:A.5.10:approval_signatory", "Signatory at appropriate management level (typically CISO or HR director, with top-management endorsement)",   "must", False, "Clause 5.1 + 5.10"),
        ChecklistItem("item:A.5.10:approval_date",      "Approval date recorded",                                                                                       "must", False, "Clause 5.1"),
        ChecklistItem("item:A.5.10:approval_target",    "Reference to the specific version of the AUP being approved",                                                  "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.10:approval_authority", "Statement of the signatory's authority (delegation chain if not top-management)",                              "should", False, "Accountability"),
    ],
)

REQ_A510_COMMUNICATION = EvidenceRequirement(
    id            = "req:A.5.10:communication_record",
    control_ref   = "A.5.10",
    standard_id   = "ISO27001:2022",
    evidence_type = "communication_record",
    title         = "Acceptable Use Policy Communication Record",
    trigger_type  = "universal",
    description   = "AUP enforcement requires the user to have been informed of the rules — courts and tribunals routinely hinge on this. Evidence must show active distribution and, ideally, individual acknowledgement (signature, click-through, training completion) — not just availability on an intranet",
    must_contain  = [
        ChecklistItem("item:A.5.10:comm_date",         "Date of publication/communication",                                                          "must", False, "Operational sufficiency"),
        ChecklistItem("item:A.5.10:comm_audience",     "Audience reached (all in-scope users, including new joiners and contractors)",               "must", False, "27002:5.10 — all relevant personnel"),
        ChecklistItem("item:A.5.10:comm_channel",      "Channel used (mandatory training module, intranet publication with notification, signature campaign)", "must", False, "Operational sufficiency"),
        ChecklistItem("item:A.5.10:comm_acknowledgement","User-level acknowledgement captured (e-signature, training completion record, click-through)", "must", False, "Enforceability — burden of proof"),
        ChecklistItem("item:A.5.10:comm_onboarding",   "Distribution at onboarding for new personnel evidenced (induction pack, mandatory module)",  "must", False, "27002:5.10 — new joiners"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.10:comm_refresh",      "Periodic re-acknowledgement (annual at minimum) referenced",                                 "should", False, "Sustained communication"),
        ChecklistItem("item:A.5.10:comm_translations", "Translations or language considerations where the workforce is multilingual",                "should", False, "Accessibility"),
    ],
)

REQ_A510_REVIEW = EvidenceRequirement(
    id              = "req:A.5.10:periodic_review",
    control_ref     = "A.5.10",
    standard_id     = "ISO27001:2022",
    evidence_type   = "review_record",
    title           = "Periodic Acceptable Use Policy Review",
    trigger_type    = "universal",
    description     = "AUPs decay fast — new technologies (AI tools, new collaboration platforms), new regulations (data residency), and new threat patterns (social engineering vectors) all require policy updates. Review captures who reviewed, when, and whether the rules still cover the actual use patterns",
    freshness_days  = 365,
    must_contain    = [
        ChecklistItem("item:A.5.10:review_date",       "Review date within the planned interval",                                                  "must", False, "Periodic review"),
        ChecklistItem("item:A.5.10:review_reviewer",   "Reviewer identity and role (typically CISO with HR and legal input)",                       "must", False, "Accountability"),
        ChecklistItem("item:A.5.10:review_outcome",    "Outcome captured (no change / amended / re-issued) with rationale per amendment",          "must", False, "Periodic review"),
        ChecklistItem("item:A.5.10:review_use_patterns","Use-pattern check — new technologies or behaviours that need explicit rules added",       "must", False, "Drift catch"),
    ],
    should_contain  = [
        ChecklistItem("item:A.5.10:review_triggers",   "Ad-hoc triggers listed (new technology rollout, incident lessons-learned, regulatory change)", "should", False, "Change-driven review"),
        ChecklistItem("item:A.5.10:review_next_date",  "Next planned review date stated",                                                          "should", False, "Planning"),
    ],
)

# ── Annex A.5.11 — Return of assets — operational_process (4-leaf) ────────────
# Promoted 2026-05-31 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: operational_process → procedure
# + register + review_record + revocation_record (lifecycle-end). The
# lifecycle-end slot is realised as the per-leaver completion signoff —
# the verified return record (or documented non-return + risk acceptance)
# that closes each individual offboarding event. The procedure leaf id is
# preserved; three siblings are new.
#
# Review freshness 365d — HR offboarding methodology is stable. Unlike
# detection/IR (180d) where landscape moves fast, the asset-return process
# changes only when the org's workforce model shifts (e.g. fully-remote
# adoption, contractor-heavy shift, BYOD policy change). Annual cadence
# with HR + IT + InfoSec jointly is right-sized. Same rationale family as
# A.5.8 project security, A.5.28 evidence handling.
#
# Cross-control: register references A.5.9 asset register (which assets
# the person had); data-handling MUST cross-links to A.8.10 information
# deletion; the broader offboarding sequence touches A.6.5 (post-
# termination responsibilities) — encoded inline as MUST/SHOULD items.
#
# Authority: ISO 27002:2022 § 5.11 implementation guidance — return upon
# termination of employment / change of role / end of contract; cover
# physical + logical assets; documentation; data preservation prior to
# return; risk-based handling of unreturned items.

REQ_A511_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.11:return_of_assets_procedure",
    control_ref   = "A.5.11",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Return of Assets Procedure",
    trigger_type  = "universal",
    description   = "A.5.11 requires personnel to return all organisational assets upon change or termination. The procedure documents the trigger events, asset checklist (physical + logical), verification step, data preservation and wipe, role accountability and exception handling. The leaver register, periodic program review and per-leaver return record are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.11:triggers",          "Triggers enumerated (termination, role change, contract end, change of agreement, end of secondment)",     "must", False, "27002:5.11 — upon change or termination"),
        ChecklistItem("item:A.5.11:asset_checklist",   "Checklist of asset types to be returned — physical (laptops, mobile devices, badges, tokens) and logical (corp credentials, data on personal devices)", "must", False, "27002:5.11 — all organizational assets"),
        ChecklistItem("item:A.5.11:verification",      "Verification step signed by both the returning party and the receiving role (IT/manager) with itemised confirmation", "must", False, "27002:5.11 — return"),
        ChecklistItem("item:A.5.11:data_preservation", "Data preservation step BEFORE wipe (org information on the asset must be captured / migrated, not just deleted)", "must", False, "27002:5.11 — preservation of organisational information"),
        ChecklistItem("item:A.5.11:data_handling",     "Data wipe / sanitisation step for assets carrying organisational information (cross-link to A.8.10 deletion)",     "must", False, "27002:5.11 — data handling + cross-link to [[A.8.10]]"),
        ChecklistItem("item:A.5.11:owner",             "Owner of the procedure (typically HR + IT joint with InfoSec sign-off authority)",                                  "must", False, "Accountability"),
        ChecklistItem("item:A.5.11:non_return_path",   "Non-return path defined (when assets cannot be physically returned — remote staff, lost device, contractor dispute — alternative attestation + risk acceptance)", "must", False, "27002:5.11 — risk-based handling of unreturned items"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.11:timeline",          "Timeline stated (e.g. assets returned by last working day; data return ahead of access revocation)",                "should", False, "Timeliness"),
        ChecklistItem("item:A.5.11:exception_process", "Exception process for outstanding assets (work-from-home, contractor delays, lost-in-transit)",                     "should", False, "Real-world friction"),
        ChecklistItem("item:A.5.11:contractor_variant","Contractor variant documented where standard employee path doesn't apply (third-party offboarding, project closure)", "should", False, "Workforce-model coverage"),
    ],
)

REQ_A511_LEAVER_REGISTER = EvidenceRequirement(
    id            = "req:A.5.11:leaver_return_register",
    control_ref   = "A.5.11",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Leaver Asset Return Register",
    trigger_type  = "universal",
    description   = "A.5.11 requires every triggered return event to be tracked — invisible leavers are the ones who walk out with assets. The register catalogues every in-flight return: leaver id, trigger type, departure/effective date, asset list (linked to A.5.9 asset register), current status, owner. It is the operational record that proves the return process is actually applied every time, not just on the leavers HR happens to remember to log",
    must_contain  = [
        ChecklistItem("item:A.5.11:reg_leaver_id",     "Each leaver/role-changer captured with a unique identifier (employee or contractor id; do not store sensitive PII beyond what HR retains)", "must", False, "27002:5.11 — visibility"),
        ChecklistItem("item:A.5.11:reg_trigger_type",  "Trigger type per row (termination / role_change / contract_end / secondment_end / agreement_change)",                "must", False, "27002:5.11 — trigger taxonomy"),
        ChecklistItem("item:A.5.11:reg_effective_date","Effective date per row (last working day or role-change date — drives return-deadline calculations)",                 "must", False, "Timeline anchor"),
        ChecklistItem("item:A.5.11:reg_asset_list",    "Per-leaver asset list (link to A.5.9 asset register entries assigned to this person)",                                 "must", False, "27002:5.11 + cross-link to [[A.5.9]]"),
        ChecklistItem("item:A.5.11:reg_status",        "Status per row (pending / in_progress / complete / exception / written_off) updated as items are returned",          "must", False, "Operational discipline"),
        ChecklistItem("item:A.5.11:reg_owner",         "Return owner per row (typically the leaver's line manager + IT custody handler)",                                     "must", False, "Accountability"),
        ChecklistItem("item:A.5.11:reg_access_revoke", "Access-revocation timestamp per row (when corp accounts/SSO/credentials were disabled — should align with effective date)", "must", False, "27002:5.11 — logical asset handling"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.11:reg_data_preserved","Data-preserved flag per row (org information migrated/captured before wipe)",                                          "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.11:reg_byod_flag",     "BYOD flag per row where leaver used personal device (drives different wipe path — selective MDM removal vs full wipe)", "should", False, "Workforce-model coverage"),
    ],
)

REQ_A511_PROGRAM_REVIEW = EvidenceRequirement(
    id             = "req:A.5.11:return_program_review",
    control_ref    = "A.5.11",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic Asset-Return Program Review",
    trigger_type   = "universal",
    description    = "The return process creates value only if it actually closes — unreturned-asset rates, delayed-access-revocation incidents, BYOD-wipe failures all signal the program is leaking. The review captures the planned-interval check: unreturned rate, access-revocation latency, exception/write-off analysis, workforce-model coverage, and resulting program adjustments. Annual cadence — HR methodology stability",
    freshness_days = 365,
    must_contain   = [
        ChecklistItem("item:A.5.11:rev_date",            "Review date within the planned annual interval",                                                                    "must", False, "27002:5.11 — periodic"),
        ChecklistItem("item:A.5.11:rev_reviewer",        "Reviewer identity (HR head + IT head + InfoSec lead jointly)",                                                       "must", False, "Accountability"),
        ChecklistItem("item:A.5.11:rev_unreturned_rate", "Unreturned-asset rate analysed (count of leavers with status=exception or written_off; root cause per cluster)",      "must", False, "Program effectiveness"),
        ChecklistItem("item:A.5.11:rev_revoke_latency",  "Access-revocation latency analysed (gap between effective_date and access_revoke_timestamp; investigate outliers)", "must", False, "27002:5.11 — timeliness of logical handling"),
        ChecklistItem("item:A.5.11:rev_byod_health",     "BYOD-wipe health check (sample of recent BYOD leavers re-verified for selective-wipe success or org-data presence)", "must", False, "Workforce-model coverage"),
        ChecklistItem("item:A.5.11:rev_writeoff_audit",  "Write-off audit (any leaver row written off — was risk acceptance appropriately authorised? what value was lost?)",  "must", False, "Risk discipline"),
        ChecklistItem("item:A.5.11:rev_actions",         "Action items captured (e.g. tighten access-revoke automation, expand asset checklist, retrain managers)",            "must", False, "27002:5.11 — program adjustments"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.11:rev_workforce_shift", "Workforce-model shift considered (e.g. step-change in remote-work proportion or contractor mix that changes risk surface)", "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.11:rev_next_date",       "Next planned review date stated",                                                                                    "should", False, "Planning"),
    ],
)

REQ_A511_RETURN_RECORD = EvidenceRequirement(
    id            = "req:A.5.11:per_leaver_return_record",
    control_ref   = "A.5.11",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Per-Leaver Asset Return Record",
    trigger_type  = "universal",
    description   = "A.5.11 expects each leaver/role-changer to have a closed-out return event — either confirmed return with verification OR documented non-return with risk-accepted write-off. The per-leaver record evidences the actual closure: leaver id, items returned (with itemised verification), items not returned (with reason + write-off authoriser), access-revocation confirmation, dual signoff, closure date. One record per leaver row, traceable back to the register",
    must_contain  = [
        ChecklistItem("item:A.5.11:rec_leaver_ref",      "Leaver identifier per record (links to leaver register)",                                                            "must", False, "27002:5.11 — traceability"),
        ChecklistItem("item:A.5.11:rec_items_returned",  "Itemised list of returned items per record (matched against the leaver's asset list from A.5.9)",                    "must", False, "27002:5.11 — return verification"),
        ChecklistItem("item:A.5.11:rec_items_unreturned","Itemised list of NOT-returned items per record (with reason: lost / damaged / kept-by-agreement / dispute)",        "must", False, "27002:5.11 — risk-based handling"),
        ChecklistItem("item:A.5.11:rec_writeoff_auth",   "Write-off authoriser per record where applicable (proportional to asset value; InfoSec sign-off for data-bearing devices)", "must", False, "Risk discipline"),
        ChecklistItem("item:A.5.11:rec_access_confirmed","Access-revocation confirmed per record (corp accounts disabled, SSO removed, credentials rotated)",                  "must", False, "27002:5.11 — logical asset handling"),
        ChecklistItem("item:A.5.11:rec_dual_signoff",    "Dual signoff per record (returning party + receiving role) — captured even when in-person handover isn't possible (remote attestation)", "must", False, "27002:5.11 — verification"),
        ChecklistItem("item:A.5.11:rec_closure_date",    "Closure date recorded",                                                                                                "must", False, "Operational discipline"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.11:rec_data_attestation","Data-deletion attestation per record where leaver-personal-device held org data (BYOD scenarios — selective-MDM removal proof or screenshot evidence)", "should", False, "BYOD coverage"),
        ChecklistItem("item:A.5.11:rec_post_close_review","Post-closure verification window noted (e.g. 30-day check that no stale access reappears)",                          "should", False, "Continual assurance"),
    ],
)

# ── Annex A.5.12 — Information classification — policy_program 4-leaf ─────────
# Promoted 2026-05-29 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. policy_program spine: classification
# scheme + approval + communication_record + periodic review. The scheme leaf
# id is preserved; three siblings are new. Classification is the upstream of
# A.5.13 (labelling) and A.5.10 (handling rules), so the communication leaf
# must reach not just data owners but every person who creates information.
# Authority: ISO 27002:2022 § 5.12 implementation guidance.

REQ_A512_SCHEME = EvidenceRequirement(
    id            = "req:A.5.12:information_classification_scheme",
    control_ref   = "A.5.12",
    standard_id   = "ISO27001:2022",
    evidence_type = "classification_scheme",
    title         = "Information Classification Scheme",
    trigger_type  = "universal",
    description   = "A.5.12 requires information to be classified per the organisation's security needs across confidentiality, integrity, availability, and interested-party requirements. The scheme defines levels and handling implications. Approval, communication and periodic review are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.12:levels_defined",     "Classification levels defined (e.g. Public / Internal / Confidential / Restricted)",                       "must", False, "27002:5.12 — classified"),
        ChecklistItem("item:A.5.12:cia_dimensions",     "Each level addresses confidentiality, integrity, and availability dimensions",                            "must", False, "27002:5.12 — based on C/I/A"),
        ChecklistItem("item:A.5.12:level_definitions",  "Definition and indicative examples per level",                                                            "must", False, "27002:5.12 — needs of the organisation"),
        ChecklistItem("item:A.5.12:handling_per_level", "Handling implications per level (links to A.5.13 labelling, A.5.10 acceptable use, A.5.14 transfer)",     "must", False, "27002:5.12 — security needs"),
        ChecklistItem("item:A.5.12:classification_authority","Decision authority for classifying information (owner-led by default)",                              "must", False, "27002:5.12 — classified"),
        ChecklistItem("item:A.5.12:default_class",      "Default classification for unclassified information (typically 'Internal' as fail-safe)",                  "must", False, "27002:5.12 — pragmatic adoption"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.12:interested_parties", "Considerations for interested-party requirements (regulator-imposed classifications, contract-imposed)", "should", False, "Completeness"),
        ChecklistItem("item:A.5.12:declassification",   "Declassification or reclassification process",                                                            "should", False, "Lifecycle"),
        ChecklistItem("item:A.5.12:aggregation",        "Aggregation rule (combined low-class data items that, in aggregate, warrant higher class)",               "should", False, "Realistic threat model"),
    ],
)

REQ_A512_APPROVAL = EvidenceRequirement(
    id            = "req:A.5.12:management_approval",
    control_ref   = "A.5.12",
    standard_id   = "ISO27001:2022",
    evidence_type = "approval",
    title         = "Management Approval of the Classification Scheme",
    trigger_type  = "universal",
    description   = "Classification determines handling, transfer, retention and disposal across most other A.5 / A.8 controls — disagreement on the scheme cascades into operational failure. Approval establishes the canonical scheme and the authority behind override decisions",
    must_contain  = [
        ChecklistItem("item:A.5.12:approval_signatory", "Signatory at appropriate management level (typically CISO or data-protection lead, with top-management endorsement)", "must", False, "Clause 5.1 + 5.12"),
        ChecklistItem("item:A.5.12:approval_date",      "Approval date recorded",                                                                                              "must", False, "Clause 5.1"),
        ChecklistItem("item:A.5.12:approval_target",    "Reference to the specific version of the classification scheme being approved",                                       "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.12:approval_authority", "Statement of the signatory's authority (delegation chain if not top-management)",                                     "should", False, "Accountability"),
    ],
)

REQ_A512_COMMUNICATION = EvidenceRequirement(
    id            = "req:A.5.12:communication_record",
    control_ref   = "A.5.12",
    standard_id   = "ISO27001:2022",
    evidence_type = "communication_record",
    title         = "Classification Scheme Communication Record",
    trigger_type  = "universal",
    description   = "Every information creator (i.e. every employee) needs to know which level applies and how to classify their output — an unknown scheme produces unclassified information by default, which collapses A.5.13 and A.5.10 downstream. Evidence must show active distribution and ideally individual training completion",
    must_contain  = [
        ChecklistItem("item:A.5.12:comm_date",         "Date of publication/communication",                                                                                   "must", False, "Operational sufficiency"),
        ChecklistItem("item:A.5.12:comm_audience",     "Audience reached (all information creators, owners, custodians — broader than just data owners)",                     "must", False, "27002:5.12 — all relevant personnel"),
        ChecklistItem("item:A.5.12:comm_channel",      "Channel used (mandatory training module, classification guide, role-specific workshops)",                              "must", False, "Operational sufficiency"),
        ChecklistItem("item:A.5.12:comm_training",     "Classification training completion captured at user level (proves users can apply the scheme)",                       "must", False, "Operational fitness"),
        ChecklistItem("item:A.5.12:comm_onboarding",   "Distribution at onboarding for new personnel evidenced (induction pack, mandatory module)",                            "must", False, "27002:5.12 — new joiners"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.12:comm_refresh",      "Periodic refresher referenced (annual at minimum, especially after scheme amendments)",                                "should", False, "Sustained communication"),
        ChecklistItem("item:A.5.12:comm_practical_aids","Practical aids referenced (decision tree, sensitivity-label automation, examples library)",                           "should", False, "Adoption"),
    ],
)

REQ_A512_REVIEW = EvidenceRequirement(
    id              = "req:A.5.12:periodic_review",
    control_ref     = "A.5.12",
    standard_id     = "ISO27001:2022",
    evidence_type   = "review_record",
    title           = "Periodic Classification Scheme Review",
    trigger_type    = "universal",
    description     = "Classification schemes are the foundation of handling controls — a stale scheme produces stale handling. Review checks whether the levels still match the actual sensitivity gradient, whether new categories have emerged (e.g. AI training corpora), and whether downstream controls (A.5.13, A.5.10, A.5.14) still align",
    freshness_days  = 365,
    must_contain    = [
        ChecklistItem("item:A.5.12:review_date",       "Review date within the planned interval",                                                                              "must", False, "Periodic review"),
        ChecklistItem("item:A.5.12:review_reviewer",   "Reviewer identity and role (typically CISO with data-protection and business-line input)",                              "must", False, "Accountability"),
        ChecklistItem("item:A.5.12:review_outcome",    "Outcome captured (no change / amended / re-issued) with rationale per amendment",                                       "must", False, "Periodic review"),
        ChecklistItem("item:A.5.12:review_downstream", "Downstream-control alignment checked (A.5.13 labelling rules, A.5.10 handling rules, A.5.14 transfer still consistent)","must", False, "Cross-control coherence"),
    ],
    should_contain  = [
        ChecklistItem("item:A.5.12:review_triggers",   "Ad-hoc triggers listed (M&A, new regulator-imposed classes, new business line with novel sensitivities)",               "should", False, "Change-driven review"),
        ChecklistItem("item:A.5.12:review_next_date",  "Next planned review date stated",                                                                                       "should", False, "Planning"),
    ],
)

# ── Annex A.5.13 — Labelling of information — operational_process (4-leaf) ────
# Promoted 2026-05-31 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: operational_process → procedure
# + register + review_record + revocation_record (lifecycle-end). The
# lifecycle-end slot is realised as the per-platform/system labelling
# enablement record — proves labelling was actually extended to each new
# system as the org's information estate grew, not just retained on the
# legacy set. The procedure leaf id is preserved; three siblings are new.
#
# Review freshness 365d — labelling program reviews on the SAME cadence
# as A.5.12 classification (the parent scheme). Labelling cascades from
# classification; reviewing labelling out of sync with the scheme produces
# misaligned controls. Same rationale family as A.5.8 / A.5.11 / A.5.28
# (stable underlying methodology).
#
# Cross-control: register references A.5.12 classification levels (which
# levels are deployed); procedure references A.7.10 storage media for the
# physical-media marking rule path; automation overlaps with A.8.11 data
# masking tooling stack. Encoded as MUST/SHOULD items inline.
#
# Authority: ISO 27002:2022 § 5.13 implementation guidance — procedures
# covering digital and physical labelling; level-appropriate marking;
# persistence across transformations; training; legacy-handling rules.

REQ_A513_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.13:information_labelling_procedure",
    control_ref   = "A.5.13",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Information Labelling Procedure",
    trigger_type  = "universal",
    description   = "A.5.13 requires procedures for information labelling aligned with the classification scheme defined in A.5.12. The procedure documents per-level marking conventions, automated tooling rules, persistence requirements, training links, and legacy-asset handling. The coverage register, periodic program review and per-platform application record are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.13:visual_marks",      "Visual marking conventions per classification level (headers, watermarks, banners, footers)",                       "must", False, "27002:5.13 — labelling"),
        ChecklistItem("item:A.5.13:metadata_tags",     "Digital metadata tags or sensitivity labels (e.g. Microsoft Purview / Google labels / equivalent) per level",        "must", False, "27002:5.13 — labelling"),
        ChecklistItem("item:A.5.13:physical_media",    "Physical media labelling rules (paper documents, removable storage, archive boxes; cross-link to A.7.10)",          "must", False, "27002:5.13 + cross-link to [[A.7.10]]"),
        ChecklistItem("item:A.5.13:label_persistence", "Label persistence on copying, export, transformation (PDF print, file format conversion, copy-paste into new container)", "must", False, "27002:5.13 — implemented"),
        ChecklistItem("item:A.5.13:training_ref",      "References training so personnel know how to apply labels (cross-link to A.5.12 classification training)",          "must", False, "27002:5.13 — implemented"),
        ChecklistItem("item:A.5.13:scheme_alignment",  "Alignment with the A.5.12 classification scheme stated explicitly (level names match; level count matches; semantics match)", "must", False, "27002:5.13 + cross-link to [[A.5.12]]"),
        ChecklistItem("item:A.5.13:pii_overlay",       "PII / personal-data overlay rule where applicable (additional labelling beyond confidentiality level — e.g. 'Contains PII' footer for GDPR compliance)", "must", False, "27002:5.13 + GDPR alignment"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.13:legacy_handling",   "Handling of legacy unlabelled assets (default-classify rule with retro-labelling timeline)",                          "should", False, "Pragmatic adoption"),
        ChecklistItem("item:A.5.13:automation",        "Automation / tooling references where labelling is auto-applied (DLP, sensitivity-label policies)",                  "should", False, "Scalability"),
        ChecklistItem("item:A.5.13:external_handling", "Handling of inbound third-party documents that arrive unlabelled (default-classify and add internal label)",         "should", False, "Real-world coverage"),
    ],
)

REQ_A513_COVERAGE_REGISTER = EvidenceRequirement(
    id            = "req:A.5.13:labelling_coverage_register",
    control_ref   = "A.5.13",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Labelling Coverage Register",
    trigger_type  = "universal",
    description   = "A.5.13 requires every information-storing platform to actually apply labels — the systems where labelling isn't enabled are the ones where classified info leaks out. The register catalogues every in-scope information platform: system id, scope, labelling-enabled flag, automation level (manual/assisted/automatic), coverage %, owner. It is the operational record that proves labelling is org-wide, not just on the platforms IT remembered to configure",
    must_contain  = [
        ChecklistItem("item:A.5.13:reg_system_id",     "Each in-scope information system captured with a unique identifier (file shares, M365 tenants, drive backends, ticketing systems, code repos with sensitive data)", "must", False, "27002:5.13 — visibility"),
        ChecklistItem("item:A.5.13:reg_scope",         "Scope per row (which content classes this system stores — e.g. customer data, HR records, source code, financial)",      "must", False, "Coverage analysis"),
        ChecklistItem("item:A.5.13:reg_enabled_flag",  "Labelling-enabled flag per row (yes / partial / no — with remediation date if not yes)",                                  "must", False, "27002:5.13 — applied"),
        ChecklistItem("item:A.5.13:reg_automation",    "Automation level per row (manual / assisted / automatic; drives which gaps need user training vs config)",              "must", False, "27002:5.13 — implemented"),
        ChecklistItem("item:A.5.13:reg_coverage_pct",  "Coverage percentage per row (% of items in this system that carry a label — sampled or auto-measured)",                "must", False, "Program effectiveness"),
        ChecklistItem("item:A.5.13:reg_owner",         "System owner per row (named individual accountable for labelling on this platform)",                                     "must", False, "Accountability"),
        ChecklistItem("item:A.5.13:reg_classification_levels", "Classification levels deployed per row (links to A.5.12 scheme — sometimes a system only uses a subset)",      "must", False, "27002:5.13 + cross-link to [[A.5.12]]"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.13:reg_dlp_policy",    "DLP policy link per row where applicable (sensitivity-label-driven DLP rules wired to the system)",                    "should", False, "Defence-in-depth"),
        ChecklistItem("item:A.5.13:reg_external_ingress","External-ingress flag per row where docs arrive from outside (triggers the external_handling SHOULD path)",          "should", False, "Real-world coverage"),
    ],
)

REQ_A513_PROGRAM_REVIEW = EvidenceRequirement(
    id             = "req:A.5.13:labelling_program_review",
    control_ref    = "A.5.13",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic Labelling Program Review",
    trigger_type   = "universal",
    description    = "The labelling program creates value only if labels actually stick across the estate — systems where coverage drops, transformations that strip labels, training gaps where users mis-apply, and new platforms that came online without labelling enabled all signal the program is leaking. The review captures the planned-interval check: coverage-trend analysis, drop-detection, scheme-alignment audit, training-effectiveness sample, and resulting program adjustments. Annual cadence — cascades from A.5.12 classification scheme review",
    freshness_days = 365,
    must_contain   = [
        ChecklistItem("item:A.5.13:rev_date",             "Review date within the planned annual interval",                                                                     "must", False, "27002:5.13 — periodic"),
        ChecklistItem("item:A.5.13:rev_reviewer",         "Reviewer identity (InfoSec + Data Protection Officer where PII overlays apply jointly)",                            "must", False, "Accountability"),
        ChecklistItem("item:A.5.13:rev_coverage_trend",   "Coverage-trend analysis (per-system coverage % delta since last review; investigate any drop)",                     "must", False, "Program effectiveness"),
        ChecklistItem("item:A.5.13:rev_persistence_audit","Persistence audit (sample of transformed/exported items re-checked — does the label survive copy/export/conversion?)", "must", False, "27002:5.13 — persistence"),
        ChecklistItem("item:A.5.13:rev_scheme_alignment", "Scheme-alignment audit (labels in active systems match A.5.12 levels; drift triggers re-mapping)",                    "must", False, "27002:5.13 + cross-link to [[A.5.12]]"),
        ChecklistItem("item:A.5.13:rev_training_sample",  "Training-effectiveness sample (small sample of newly created items per level — labelled correctly?)",                "must", False, "27002:5.13 — implemented"),
        ChecklistItem("item:A.5.13:rev_actions",          "Action items captured (e.g. extend labelling to platform X, tighten automation, refresh training module, address drop)", "must", False, "27002:5.13 — program adjustments"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.13:rev_tooling_landscape","Tooling-landscape check (vendor releases, new sensitivity-label features, capability gaps the program should consider)", "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.13:rev_next_date",        "Next planned review date stated",                                                                                    "should", False, "Planning"),
    ],
)

REQ_A513_APPLICATION_RECORD = EvidenceRequirement(
    id            = "req:A.5.13:labelling_application_record",
    control_ref   = "A.5.13",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Per-Platform Labelling Application Record",
    trigger_type  = "universal",
    description   = "A.5.13 expects labelling to be applied as the org's information estate grows — every new platform that stores information of any classification level should be brought into scope, not just the platforms IT happened to configure first. The application record evidences each enablement event: platform id, scope, enablement method, coverage verification, training rollout, owner. One record per platform/system onboarding (or major re-config), traceable back to the coverage register",
    must_contain  = [
        ChecklistItem("item:A.5.13:app_system_ref",    "Platform identifier per record (links to coverage register entry)",                                                   "must", False, "27002:5.13 — traceability"),
        ChecklistItem("item:A.5.13:app_scope",         "Scope per record (which content classes the platform stores)",                                                         "must", False, "27002:5.13 — applied"),
        ChecklistItem("item:A.5.13:app_method",        "Enablement method per record (sensitivity-label policy deployed / DLP rule wired / manual-tagging training given)",   "must", False, "27002:5.13 — implemented"),
        ChecklistItem("item:A.5.13:app_coverage_check","Coverage verification per record (sample re-checked post-enablement; legacy items remediated)",                       "must", False, "Program assurance"),
        ChecklistItem("item:A.5.13:app_training",      "Training rollout per record (users of this platform completed labelling refresher; new-joiner integration noted)",   "must", False, "27002:5.13 — implemented"),
        ChecklistItem("item:A.5.13:app_owner",         "Owner per record (platform owner accepts ongoing accountability for labelling on this system)",                       "must", False, "Accountability"),
        ChecklistItem("item:A.5.13:app_enablement_date","Enablement date recorded",                                                                                             "must", False, "Operational discipline"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.13:app_dlp_wired",     "DLP-rule-wired flag per record where the platform supports DLP enforcement of labels",                                 "should", False, "Defence-in-depth"),
        ChecklistItem("item:A.5.13:app_legacy_done",   "Legacy-asset remediation completion noted per record (pre-existing items retro-labelled within the timeline)",         "should", False, "Pragmatic adoption"),
    ],
)

# ── Annex A.5.14 — Information transfer — policy_program (4-leaf) ─────────────
# Promoted 2026-05-31 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: policy_program → policy +
# approval + communication_record + review_record. Same shape as the
# batch-2 policy_program family (A.5.10 AUP, A.5.12 classification,
# A.5.15 access control). The policy leaf id is preserved; three siblings
# are new.
#
# ISO 27002:2022 § 5.14 says the control may be satisfied by "rules,
# procedures or agreements" — the org may pick the artefact form. Arion
# satisfies via policy (per the existing single-leaf framing and live
# finding). The transfer-agreements path (for frequent counterparties)
# remains a SHOULD on the policy and cross-links to A.5.20 supplier
# agreements where applicable.
#
# Review freshness 365d — same cadence as the rest of the policy_program
# family. Information-transfer rules track classification scheme (A.5.12),
# cross-border legal landscape, and new tech rollouts — none of these
# move faster than annually.
#
# Cross-control: scheme_alignment cross-links to A.5.12; transfer-agreement
# SHOULD cross-links to A.5.20; cross-border jurisdiction MUST aligns with
# GDPR Art.44-49 international-transfer chapter.
#
# Authority: ISO 27002:2022 § 5.14 implementation guidance — rules for
# all transfer facility types (electronic/physical/verbal); authorisation
# requirements; classification-aware protections; jurisdictional + legal
# considerations; transfer agreements with external parties.

REQ_A514_POLICY = EvidenceRequirement(
    id            = "req:A.5.14:information_transfer_policy",
    control_ref   = "A.5.14",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Information Transfer Policy",
    trigger_type  = "universal",
    description   = "A.5.14 requires rules, procedures or agreements covering all transfer facilities within the organisation and to/from external parties. The policy documents electronic/physical/verbal transfer rules, authorisation thresholds, classification-aware protections, jurisdictional considerations and approved-channel lists. Approval, communication and periodic review are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.14:electronic_transfer",  "Rules for electronic transfers (email, file transfer, cloud sharing, APIs) with encryption requirements per classification level",                  "must", False, "27002:5.14 — transfer facilities"),
        ChecklistItem("item:A.5.14:physical_media",       "Rules for physical media transfers (removable storage, paper documents, post/courier — tamper-evident packaging where appropriate)",              "must", False, "27002:5.14 — all transfer facility types"),
        ChecklistItem("item:A.5.14:verbal_visual",        "Rules for verbal and visual transfers (calls, screen-shares, in-person discussions in public spaces, conference talks where sensitive info may appear)", "must", False, "27002:5.14 — all transfer facility types"),
        ChecklistItem("item:A.5.14:internal_vs_external", "Distinction between internal and external transfer requirements (within-org transfers may have lighter controls than out-bound to third parties)",      "must", False, "27002:5.14 — within the organisation and between"),
        ChecklistItem("item:A.5.14:authorisation",        "Authorisation requirements for transfers above defined classification levels (who approves, for which level, for which counterparty)",                "must", False, "27002:5.14 — rules"),
        ChecklistItem("item:A.5.14:legal_jurisdiction",   "Legal and jurisdictional considerations (cross-border transfers, data sovereignty, GDPR Art.44-49 international-transfer mechanisms)",                  "must", False, "27002:5.14 + GDPR Chap V"),
        ChecklistItem("item:A.5.14:scheme_alignment",     "Alignment with the A.5.12 classification scheme stated explicitly (transfer protections per level — cascade from parent scheme)",                       "must", False, "27002:5.14 + cross-link to [[A.5.12]]"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.14:transfer_agreements",  "Standard transfer agreements with frequent counterparties referenced (cross-link to A.5.20 supplier agreements path where the counterparty is also a supplier)", "should", False, "Efficiency + cross-link to [[A.5.20]]"),
        ChecklistItem("item:A.5.14:approved_channels",    "Approved channel list (e.g. encrypted email, sanctioned file-sharing platforms, MFT solutions) per classification level",                              "should", False, "User clarity"),
        ChecklistItem("item:A.5.14:emergency_path",       "Emergency / out-of-band transfer path (when standard channels are unavailable — break-glass procedure with post-hoc authorisation)",                   "should", False, "Real-world coverage"),
    ],
)

REQ_A514_APPROVAL = EvidenceRequirement(
    id            = "req:A.5.14:management_approval",
    control_ref   = "A.5.14",
    standard_id   = "ISO27001:2022",
    evidence_type = "approval",
    title         = "Management Approval of Information Transfer Policy",
    trigger_type  = "universal",
    description   = "Transfer-policy authority is needed when rules are enforced against users (refusing to send / requiring encryption) or against external counterparties (mandating agreements before disclosure). Management approval establishes the legitimate authority for the policy and the consequences of violation. Approval names a signatory at the appropriate management level, a date, and the specific policy version",
    must_contain  = [
        ChecklistItem("item:A.5.14:approval_signatory",  "Signatory at appropriate management level (typically CISO with executive endorsement; CIO co-sign where transfer mechanisms involve IT systems)", "must", False, "27002:5.14 + clause 5.1"),
        ChecklistItem("item:A.5.14:approval_date",       "Approval date recorded",                                                                                                                          "must", False, "Clause 5.1"),
        ChecklistItem("item:A.5.14:approval_target",     "Reference to the specific version of the transfer policy being approved",                                                                          "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.14:approval_authority",  "Statement of the signatory's authority (delegation chain if not top-management; legal department consultation noted if cross-border scope)",       "should", False, "Accountability + cross-border defence"),
    ],
)

REQ_A514_COMMUNICATION = EvidenceRequirement(
    id            = "req:A.5.14:communication_record",
    control_ref   = "A.5.14",
    standard_id   = "ISO27001:2022",
    evidence_type = "communication_record",
    title         = "Information Transfer Policy Communication Record",
    trigger_type  = "universal",
    description   = "Transfer-policy enforcement requires every personnel who could initiate a transfer (which is essentially everyone) to have been informed of the rules — channel choices, encryption requirements, classification gates and external-party disclosure obligations only work if people know about them. Evidence must show active distribution and ideally individual acknowledgement (signature, click-through, training completion), not mere intranet availability",
    must_contain  = [
        ChecklistItem("item:A.5.14:comm_date",          "Date of publication/communication",                                                                                                                "must", False, "Operational sufficiency"),
        ChecklistItem("item:A.5.14:comm_audience",      "Audience reached (all in-scope users, including new joiners; targeted refresh for users who handle sensitive transfers frequently)",              "must", False, "27002:5.14 — relevant personnel"),
        ChecklistItem("item:A.5.14:comm_channel",       "Channel used (mandatory training module, intranet publication with notification, signature campaign)",                                              "must", False, "Operational sufficiency"),
        ChecklistItem("item:A.5.14:comm_acknowledgement","User-level acknowledgement captured (e-signature, training completion record, click-through)",                                                     "must", False, "Enforceability — burden of proof"),
        ChecklistItem("item:A.5.14:comm_onboarding",    "Distribution at onboarding for new personnel evidenced (induction pack, mandatory module covering transfer rules + approved channels)",            "must", False, "27002:5.14 — sustained communication"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.14:comm_refresh",       "Periodic re-acknowledgement (annual at minimum) referenced",                                                                                       "should", False, "Sustained communication"),
        ChecklistItem("item:A.5.14:comm_scenario_examples","Scenario-based examples included in training (e.g. external auditor data request, supplier integration handover, regulator response)",           "should", False, "Practical effectiveness"),
    ],
)

REQ_A514_REVIEW = EvidenceRequirement(
    id              = "req:A.5.14:periodic_review",
    control_ref     = "A.5.14",
    standard_id     = "ISO27001:2022",
    evidence_type   = "review_record",
    title           = "Periodic Information Transfer Policy Review",
    trigger_type    = "universal",
    description     = "Transfer policies decay as the technology landscape shifts (new collaboration platforms, new AI tools that exfiltrate by design), as the legal landscape shifts (cross-border data flow rulings, regulator guidance), and as the org's transfer mix shifts (new supplier integrations, new regulatory reporting). The review captures the periodic check: technology check, legal-landscape scan, transfer-mix audit, training-effectiveness sample, and resulting program adjustments",
    freshness_days  = 365,
    must_contain    = [
        ChecklistItem("item:A.5.14:review_date",         "Review date within the planned interval",                                                                                                          "must", False, "Periodic review"),
        ChecklistItem("item:A.5.14:review_reviewer",     "Reviewer identity and role (CISO + Data Protection Officer + Legal jointly where cross-border transfers are in scope)",                              "must", False, "Accountability"),
        ChecklistItem("item:A.5.14:review_outcome",      "Outcome captured (no change / amended / re-issued) with rationale per amendment",                                                                   "must", False, "Periodic review"),
        ChecklistItem("item:A.5.14:review_tech_check",   "Technology check — new transfer mechanisms in use (AI assistants, new collab platforms, new file-sharing tools) that need explicit rules added",   "must", False, "27002:5.14 — keep current"),
        ChecklistItem("item:A.5.14:review_legal_scan",   "Legal-landscape scan (cross-border ruling updates, regulator guidance, sectoral rules that touch transfers — GDPR Chap V, sector schemes)",       "must", False, "27002:5.14 + GDPR Chap V"),
    ],
    should_contain  = [
        ChecklistItem("item:A.5.14:review_triggers",     "Ad-hoc triggers listed (new tooling rollout, regulator action against peer, incident lessons-learned involving a transfer breach)",                "should", False, "Change-driven review"),
        ChecklistItem("item:A.5.14:review_next_date",    "Next planned review date stated",                                                                                                                  "should", False, "Planning"),
    ],
)

# ── Annex A.5.15 — Access control — policy_program 4-leaf ─────────────────────
# Promoted 2026-05-29 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. policy_program spine: access control
# policy + approval + communication_record + periodic review. The policy leaf
# id is preserved; three siblings are new. The policy states the principles
# (RBAC, least privilege, need-to-know); the provisioning *procedure* lives
# at A.5.18 and is curated separately when A.5.18 promotes.
# Authority: ISO 27002:2022 § 5.15 implementation guidance.

REQ_A515_POLICY = EvidenceRequirement(
    id            = "req:A.5.15:access_control_policy",
    control_ref   = "A.5.15",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Access Control Policy",
    trigger_type  = "universal",
    description   = "A.5.15 requires rules controlling physical and logical access based on business and information security requirements. The policy states the principles and decision rules; the provisioning procedure (lifecycle) lives at A.5.18. Approval, communication and periodic review are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.15:physical_rules",   "Physical access rules (premises, server rooms, restricted areas)",                                                "must", False, "27002:5.15 — physical access"),
        ChecklistItem("item:A.5.15:logical_rules",    "Logical access rules (systems, applications, network segments)",                                                  "must", False, "27002:5.15 — logical access"),
        ChecklistItem("item:A.5.15:rbac",             "Role-based access control as the default model with stated exceptions (attribute-based, individual grants)",      "must", False, "27002:5.15 — business requirements"),
        ChecklistItem("item:A.5.15:least_privilege",  "Principle of least privilege stated",                                                                              "must", False, "27002:5.15 — security requirements"),
        ChecklistItem("item:A.5.15:need_to_know",     "Principle of need-to-know stated",                                                                                 "must", False, "27002:5.15 — security requirements"),
        ChecklistItem("item:A.5.15:authorisation",    "Authorisation rules — who can authorise access at which level (cross-link to A.5.18 procedure)",                  "must", False, "27002:5.15 — established"),
        ChecklistItem("item:A.5.15:segregation_link", "Cross-link to A.5.3 segregation of duties — access decisions respect documented separation",                       "must", False, "Cross-control coherence"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.15:emergency_access", "Emergency / break-glass access provisions (with mandatory after-the-fact justification)",                          "should", False, "Operational continuity"),
        ChecklistItem("item:A.5.15:third_party",      "Third-party / contractor access rules referenced (link to A.5.19 supplier relationships)",                          "should", False, "Coverage"),
        ChecklistItem("item:A.5.15:review_cadence",   "Periodic access review cadence stated (typically quarterly for privileged, annual otherwise — link to A.5.18)",   "should", False, "Drift prevention"),
    ],
)

REQ_A515_APPROVAL = EvidenceRequirement(
    id            = "req:A.5.15:management_approval",
    control_ref   = "A.5.15",
    standard_id   = "ISO27001:2022",
    evidence_type = "approval",
    title         = "Management Approval of the Access Control Policy",
    trigger_type  = "universal",
    description   = "Access decisions are the most-audited control area in ISMS audits — the approval makes the principles explicit and authoritative. Names a signatory at the appropriate management level, a date, and the specific policy version",
    must_contain  = [
        ChecklistItem("item:A.5.15:approval_signatory", "Signatory at appropriate management level (typically CISO with IT / business endorsement)",  "must", False, "Clause 5.1 + 5.15"),
        ChecklistItem("item:A.5.15:approval_date",      "Approval date recorded",                                                                      "must", False, "Clause 5.1"),
        ChecklistItem("item:A.5.15:approval_target",    "Reference to the specific version of the access control policy being approved",              "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.15:approval_authority", "Statement of the signatory's authority (delegation chain if not top-management)",            "should", False, "Accountability"),
    ],
)

REQ_A515_COMMUNICATION = EvidenceRequirement(
    id            = "req:A.5.15:communication_record",
    control_ref   = "A.5.15",
    standard_id   = "ISO27001:2022",
    evidence_type = "communication_record",
    title         = "Access Control Policy Communication Record",
    trigger_type  = "universal",
    description   = "Access-granting decision-makers (managers, system owners, IT admins) and access-holders both need to know the rules. The policy's most common failure mode is mid-level managers granting access by default without checking the principles — communication must reach them specifically",
    must_contain  = [
        ChecklistItem("item:A.5.15:comm_date",         "Date of publication/communication",                                                                "must", False, "Operational sufficiency"),
        ChecklistItem("item:A.5.15:comm_audience",     "Audience reached (decision-makers — managers, system owners, IT admins — plus all access-holders)", "must", False, "27002:5.15 — relevant parties"),
        ChecklistItem("item:A.5.15:comm_channel",      "Channel used (manager briefing, IT admin training, intranet publication)",                          "must", False, "Operational sufficiency"),
        ChecklistItem("item:A.5.15:comm_decision_makers","Decision-maker awareness specifically captured (manager training, system-owner briefing)",         "must", False, "Targeted communication"),
        ChecklistItem("item:A.5.15:comm_onboarding",   "Onboarding coverage — new managers and admins receive the policy as part of role induction",        "must", False, "27002:5.15 — sustained"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.15:comm_refresh",      "Periodic refresher referenced (annual at minimum)",                                                "should", False, "Sustained communication"),
        ChecklistItem("item:A.5.15:comm_a518_link",    "Tie-in with A.5.18 provisioning training — decision-makers know both the rules and the workflow",   "should", False, "Coherent rollout"),
    ],
)

REQ_A515_REVIEW = EvidenceRequirement(
    id              = "req:A.5.15:periodic_review",
    control_ref     = "A.5.15",
    standard_id     = "ISO27001:2022",
    evidence_type   = "review_record",
    title           = "Periodic Access Control Policy Review",
    trigger_type    = "universal",
    description     = "Access control policies decay as the IT estate grows — new systems, new cloud services, new federated identity sources all stress the policy. Review checks whether the rules still cover the actual estate, whether least-privilege is still operationalised correctly, and whether downstream A.5.18 provisioning is aligned",
    freshness_days  = 365,
    must_contain    = [
        ChecklistItem("item:A.5.15:review_date",       "Review date within the planned interval",                                                          "must", False, "Periodic review"),
        ChecklistItem("item:A.5.15:review_reviewer",   "Reviewer identity and role (typically CISO with IT and identity-management input)",                "must", False, "Accountability"),
        ChecklistItem("item:A.5.15:review_outcome",    "Outcome captured (no change / amended / re-issued) with rationale per amendment",                  "must", False, "Periodic review"),
        ChecklistItem("item:A.5.15:review_estate",     "Estate-alignment check — new systems / cloud services added since last review reflected in policy", "must", False, "Drift catch"),
        ChecklistItem("item:A.5.15:review_a518_link",  "A.5.18 provisioning procedure cross-checked for alignment with policy changes",                    "must", False, "Cross-control coherence"),
    ],
    should_contain  = [
        ChecklistItem("item:A.5.15:review_triggers",   "Ad-hoc triggers listed (M&A, new identity provider, major SaaS adoption, access-related incident)", "should", False, "Change-driven review"),
        ChecklistItem("item:A.5.15:review_next_date",  "Next planned review date stated",                                                                  "should", False, "Planning"),
    ],
)

# ── Annex A.5.16 — Identity management — operational_process (4-leaf) ─────────
# Promoted 2026-05-31 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: operational_process →
# procedure + register + review_record + revocation_record (lifecycle-end).
# The lifecycle-end slot is realised as the per-identity revocation record
# — proves each identity was actually disabled within the stated timeliness
# contract (the famous "X was disabled within 24h of last day" promise
# that auditors regularly test).
#
# Review freshness 180d — identity drift is high-volume. Joiners, leavers,
# role changes, contractor onboarding/offboarding, service-account churn
# all accumulate continuously. Waiting a full year between meta-reviews
# leaves too much drift. Same volatility family as A.5.25/A.5.26 detection
# landscape (180d) and A.5.21 ICT supply chain (180d).
#
# Cross-control: register integrates with HR for joiner/leaver triggers;
# triggers from A.5.11 leaver register cascade to identity revocation_
# record; identity attestation cycle ties to A.5.18 access rights review;
# service-account governance promoted from SHOULD to MUST (it's the
# weakest spot in most orgs' identity hygiene).
#
# Distinct from A.5.17 (authentication information) which covers
# credentials and their lifecycle; A.5.16 is about the identity object
# itself, A.5.17 is about how identities prove themselves.
#
# Authority: ISO 27002:2022 § 5.16 implementation guidance — full
# identity lifecycle management (creation/modification/suspension/
# termination); timeliness; accountability; unique identity per person;
# service-account governance; periodic attestation.

REQ_A516_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.16:identity_management_procedure",
    control_ref   = "A.5.16",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Identity Lifecycle Management Procedure",
    trigger_type  = "universal",
    description   = "A.5.16 requires the full lifecycle of identities to be managed — creation, modification, suspension, termination — across human, contractor, service, shared and non-human account types. The procedure documents each lifecycle step, timeliness expectations, ownership chain (HR triggers, IT executes, manager approves), and the connection to authentication-information lifecycle in A.5.17. The identity register, periodic program review and per-identity revocation record are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.16:creation",          "Identity creation steps (verification of person, naming convention, initial entitlements — least-privilege at issuance)",         "must", False, "27002:5.16 — lifecycle creation"),
        ChecklistItem("item:A.5.16:modification",      "Modification steps for role changes (add/remove entitlements; same-day or next-business-day SLA)",                                "must", False, "27002:5.16 — lifecycle modification"),
        ChecklistItem("item:A.5.16:suspension",        "Suspension steps for leave of absence, risk events (under investigation), or extended inactivity (auto-suspend at N days idle)",  "must", False, "27002:5.16 — lifecycle suspension"),
        ChecklistItem("item:A.5.16:termination",       "Termination steps with stated deactivation timeline (e.g. within 24h of last day; immediate on involuntary termination)",         "must", False, "27002:5.16 — lifecycle termination"),
        ChecklistItem("item:A.5.16:unique_identity",   "Unique identity per person (no shared user accounts for individuals; named accountability)",                                       "must", False, "27002:5.16 — managed"),
        ChecklistItem("item:A.5.16:ownership",         "Ownership of each lifecycle phase (HR triggers from leaver register; IT executes; manager approves; InfoSec oversight)",          "must", False, "Accountability + cross-link to [[A.5.11]]"),
        ChecklistItem("item:A.5.16:service_accounts",  "Service / shared / non-human account governance (named human owner, expiry, scope, monitoring) — promoted from SHOULD because this is the weakest spot in most identity hygiene programs", "must", False, "27002:5.16 — managed (all identity types)"),
        ChecklistItem("item:A.5.16:authn_link",        "Cross-reference to A.5.17 authentication-information lifecycle (credential issuance and revocation are paired with identity events)", "must", False, "27002:5.16 + cross-link to [[A.5.17]]"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.16:attestation",       "Periodic identity attestation cadence (e.g. annual recertification of each identity by its owner) referenced",                    "should", False, "Drift prevention + cross-link to [[A.5.18]]"),
        ChecklistItem("item:A.5.16:contractor_path",   "Contractor-specific path documented (fixed expiry, automatic disable; no manual extension without re-approval)",                  "should", False, "High-risk workforce segment"),
        ChecklistItem("item:A.5.16:emergency_disable", "Emergency-disable path (break-glass deactivation when standard SLA is too slow — e.g. immediate revocation on incident escalation)", "should", False, "Real-world coverage"),
    ],
)

REQ_A516_IDENTITY_REGISTER = EvidenceRequirement(
    id            = "req:A.5.16:identity_register",
    control_ref   = "A.5.16",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Identity Register",
    trigger_type  = "universal",
    description   = "A.5.16 requires every identity to be visible to the security function — invisible identities are the ones that go stale, get reused, or persist past their owner's departure. The register catalogues every active identity (human + service + shared + non-human): identity id, type, owner, status, created/modified/last-used timestamps. It is the operational record that proves identity hygiene is org-wide, not just on the systems IT remembered to onboard to the IAM platform",
    must_contain  = [
        ChecklistItem("item:A.5.16:reg_identity_id",     "Each active identity captured with a unique identifier (employee id, contractor id, service-account id, shared-account id)", "must", False, "27002:5.16 — visibility"),
        ChecklistItem("item:A.5.16:reg_identity_type",   "Identity type per row (human_employee / human_contractor / service / shared / system_account) — drives policy variant applied", "must", False, "27002:5.16 — managed (all types)"),
        ChecklistItem("item:A.5.16:reg_owner",          "Named owner per row (human owner accountable for THIS identity — even for service accounts, must be a human)",                "must", False, "Accountability"),
        ChecklistItem("item:A.5.16:reg_status",         "Status per row (active / suspended / disabled / pending_termination) updated as lifecycle events fire",                       "must", False, "27002:5.16 — lifecycle tracking"),
        ChecklistItem("item:A.5.16:reg_created_modified","Created and last-modified timestamps per row",                                                                                "must", False, "Audit trail"),
        ChecklistItem("item:A.5.16:reg_last_used",      "Last-used timestamp per row (drives auto-suspend at N days idle; orphan detection)",                                          "must", False, "27002:5.16 — drift detection"),
        ChecklistItem("item:A.5.16:reg_hr_link",        "HR-record link per row for human identities (joiner/leaver triggers cascade automatically — no manual sync)",                "must", False, "27002:5.16 + cross-link to [[A.5.11]]"),
        ChecklistItem("item:A.5.16:reg_service_expiry", "Expiry date per row for service / shared / temporary identities (forces deliberate renewal rather than indefinite drift)",   "must", False, "27002:5.16 — managed (service-account discipline)"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.16:reg_attestation_due","Next attestation date per row (drives the periodic recertification cycle)",                                                  "should", False, "Drift prevention"),
        ChecklistItem("item:A.5.16:reg_risk_tag",       "Risk tag per row where the identity has elevated privileges or sensitive scope (drives faster-cadence review)",              "should", False, "Risk-based attention"),
    ],
)

REQ_A516_PROGRAM_REVIEW = EvidenceRequirement(
    id             = "req:A.5.16:identity_program_review",
    control_ref    = "A.5.16",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic Identity-Management Program Review",
    trigger_type   = "universal",
    description    = "The identity program creates value only if the lifecycle actually closes — orphan accounts, lingering contractor access, stale service credentials, missed termination SLAs all signal the program is leaking. The review captures the planned-interval check: orphan analysis, SLA-miss analysis, service-account hygiene audit, contractor expiry verification, and resulting program adjustments. Cadence tightened to 180 days — identity drift is high-volume",
    freshness_days = 180,
    must_contain   = [
        ChecklistItem("item:A.5.16:rev_date",            "Review date within the planned 180-day interval",                                                                            "must", False, "27002:5.16 — periodic"),
        ChecklistItem("item:A.5.16:rev_reviewer",        "Reviewer identity (IT identity-lead + HR partner + InfoSec lead jointly)",                                                    "must", False, "Accountability"),
        ChecklistItem("item:A.5.16:rev_orphan_analysis", "Orphan analysis (identities without active HR record / business reason; remediation per orphan)",                            "must", False, "27002:5.16 — drift catch"),
        ChecklistItem("item:A.5.16:rev_termination_sla", "Termination-SLA analysis (gap between leaver effective_date and identity_revocation date; outliers investigated)",          "must", False, "27002:5.16 — timeliness"),
        ChecklistItem("item:A.5.16:rev_service_hygiene", "Service-account hygiene audit (sample of service accounts re-validated: owner still employed, scope still appropriate, expiry not lapsed)", "must", False, "27002:5.16 — service-account discipline"),
        ChecklistItem("item:A.5.16:rev_contractor_expiry","Contractor-expiry verification (audit that expired contractor identities are actually disabled, not just flagged)",         "must", False, "27002:5.16 — fixed-expiry enforcement"),
        ChecklistItem("item:A.5.16:rev_actions",         "Action items captured (e.g. tighten auto-suspend threshold, expand HR-cascade automation, retire shared accounts)",          "must", False, "27002:5.16 — program adjustments"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.16:rev_iam_tooling",     "IAM tooling check (vendor releases, new capabilities like just-in-time access; capability gaps to consider)",                "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.16:rev_next_date",       "Next planned review date stated (within 180d of this review)",                                                                "should", False, "Planning"),
    ],
)

REQ_A516_REVOCATION_RECORD = EvidenceRequirement(
    id            = "req:A.5.16:identity_revocation_record",
    control_ref   = "A.5.16",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Per-Identity Revocation Record",
    trigger_type  = "universal",
    description   = "A.5.16 expects every identity termination to be evidenced — not just procedurally promised. The revocation record evidences each disable/remove event: identity id, trigger type, effective date, actual revocation timestamp, SLA-met flag, dual signoff, residual-cleanup status (mailbox forwarding, file-share access transfer). One record per terminated identity, traceable back to the identity register and to the originating trigger (A.5.11 leaver register, contractor expiry, security event)",
    must_contain  = [
        ChecklistItem("item:A.5.16:rev_identity_ref",    "Identity identifier per record (links to identity register entry)",                                                          "must", False, "27002:5.16 — traceability"),
        ChecklistItem("item:A.5.16:rev_trigger_type",    "Trigger type per record (termination / contract_end / suspension_to_disable / incident_revocation / orphan_cleanup)",        "must", False, "27002:5.16 — trigger taxonomy"),
        ChecklistItem("item:A.5.16:rev_effective_date",  "Effective date per record (last working day OR contract expiry OR incident decision time)",                                   "must", False, "Timeliness anchor"),
        ChecklistItem("item:A.5.16:rev_actual_timestamp","Actual revocation timestamp per record (drives SLA-met calculation)",                                                         "must", False, "27002:5.16 — timeliness verification"),
        ChecklistItem("item:A.5.16:rev_sla_met",         "SLA-met flag per record (yes / no_with_reason — gap between effective and actual must be within stated SLA, or exception logged)", "must", False, "27002:5.16 — auditor-critical SLA proof"),
        ChecklistItem("item:A.5.16:rev_dual_signoff",    "Dual signoff per record (IT identity-owner + HR or hiring manager — captures even when in-person handover impossible)",     "must", False, "Accountability"),
        ChecklistItem("item:A.5.16:rev_residual_cleanup","Residual-cleanup status per record (mailbox forwarding configured, file-share access transferred or revoked, group memberships cleared)", "must", False, "27002:5.16 — full lifecycle closure"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.16:rev_post_disable_audit","Post-disable verification window noted (e.g. 30-day check that no stale access reappears via service-account chains)",     "should", False, "Continual assurance"),
        ChecklistItem("item:A.5.16:rev_credential_link", "Cross-reference to A.5.17 credential-revocation record (paired event; both must complete to close the loop)",               "should", False, "Closing loop with [[A.5.17]]"),
    ],
)

# ── Annex A.5.17 — Authentication information — operational_process (4-leaf) ──
# Promoted 2026-05-31 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: operational_process →
# procedure + register + review_record + revocation_record (lifecycle-end).
# Naturally PAIRED with A.5.16 identity management ([[curation-phase-b-
# batch-12-2026-05-31]]) — A.5.16 governs the identity *object*, A.5.17
# governs how each identity *proves* itself (credentials, factors,
# tokens). Each identity event in A.5.16 typically has a paired credential
# event in A.5.17.
#
# Review freshness 180d — credential hygiene churns continuously (rotation
# cycles, breach disclosures triggering forced rotations, MFA enrolment
# campaigns, factor-class additions/deprecations). Same volatility family
# as A.5.16 (180d) and A.5.25/A.5.26 detection landscape.
#
# Lifecycle-end variant: credential_revocation_record — per-credential
# disable/reissue proof. Pairs structurally with A.5.16's identity
# revocation_record (position 14). This adds **position 15** to the
# variant catalogue: per-credential lifecycle closure. Both records may
# fire from the same trigger (e.g. employee termination → identity
# revoked AND all their credentials revoked) but they are separate
# records because credentials can have independent lifecycles
# (credential rotation, lost-token reissue, factor downgrade) without
# changing the identity itself.
#
# MFA promoted from SHOULD to MUST — same rationale as service_accounts
# in A.5.16 (the previously-soft expectation is now first-class).
#
# Authority: ISO 27002:2022 § 5.17 implementation guidance — allocation
# of authentication info; management (transmission, storage, complexity,
# rotation); reset/recovery; personnel responsibilities (handling,
# reporting compromise); multi-factor where appropriate.

REQ_A517_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.17:authentication_information_procedure",
    control_ref   = "A.5.17",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Authentication Information Management Procedure",
    trigger_type  = "universal",
    description   = "A.5.17 requires authentication information (passwords, tokens, keys, certificates, biometric data) to be allocated and managed by a controlled process, with personnel advised on appropriate handling. The procedure documents allocation, transmission, storage, complexity/rotation, reset/recovery, user advisory, MFA expectations and the connection to identity lifecycle in A.5.16. The credential register, periodic program review and per-credential revocation record are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.17:allocation",        "Initial allocation method for authentication information per credential type (in-person, secure channel, ephemeral link, hardware-token enrolment)", "must", False, "27002:5.17 — allocation"),
        ChecklistItem("item:A.5.17:transmission",      "Transmission method requirements (out-of-band, encrypted, never on the same channel as the identity itself; never via plain email)",                "must", False, "27002:5.17 — management process"),
        ChecklistItem("item:A.5.17:complexity",        "Password / credential complexity and rotation requirements (length, character classes, history, max-age — risk-tiered per scope)",                     "must", False, "27002:5.17 — management"),
        ChecklistItem("item:A.5.17:storage",           "Storage requirements (hashed + salted with modern algorithm — argon2/scrypt/bcrypt; vaulted in secrets manager; never plaintext anywhere)",            "must", False, "27002:5.17 — management"),
        ChecklistItem("item:A.5.17:reset",             "Reset / recovery process with identity re-verification (out-of-band; no static security questions; rate-limited)",                                     "must", False, "27002:5.17 — management"),
        ChecklistItem("item:A.5.17:user_advisory",     "Advisory guidance to personnel on protecting their authentication information (no sharing, no re-use, password-manager guidance, compromise reporting path)", "must", False, "27002:5.17 — advising personnel"),
        ChecklistItem("item:A.5.17:mfa",               "Multi-factor authentication mandated for in-scope access (admin accounts, remote access, sensitive data access) — promoted from SHOULD because MFA is no longer optional baseline", "must", False, "27002:5.17 — modern baseline"),
        ChecklistItem("item:A.5.17:identity_link",     "Cross-reference to A.5.16 identity lifecycle (credential issuance follows identity creation; credential revocation follows identity termination; pairing enforced not optional)", "must", False, "27002:5.17 + cross-link to [[A.5.16]]"),
        ChecklistItem("item:A.5.17:compromise_response","Compromise-response path (when a credential is reported or detected compromised — forced rotation, identity-level investigation, scope expansion check)", "must", False, "27002:5.17 — handle compromise"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.17:factor_classes",    "Authentication factor classes documented (knowledge / possession / inherence) and which combinations satisfy MFA per access tier",                     "should", False, "Risk-based mapping"),
        ChecklistItem("item:A.5.17:passwordless",      "Passwordless / phishing-resistant authentication noted where deployed (FIDO2, passkeys) — direction-of-travel statement",                              "should", False, "Modern direction"),
        ChecklistItem("item:A.5.17:break_glass",       "Break-glass credentials documented separately (emergency-only accounts with sealed-envelope or vault-with-audit access)",                              "should", False, "Operational continuity"),
    ],
)

REQ_A517_CREDENTIAL_REGISTER = EvidenceRequirement(
    id            = "req:A.5.17:credential_register",
    control_ref   = "A.5.17",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Credential Register",
    trigger_type  = "universal",
    description   = "A.5.17 requires every credential type to be visible — secret-sprawl is the failure mode where ad-hoc credentials proliferate outside the central vault, escape rotation, and persist past their owner. The register catalogues every credential type deployed: type id, scope, vault location, rotation cadence, MFA factors required, owner. It is the operational record that proves credential governance covers ALL credentials in use, not just the ones IT remembered to onboard to the password manager",
    must_contain  = [
        ChecklistItem("item:A.5.17:reg_credential_type", "Each credential type captured with a unique identifier (user_password / admin_password / api_key / service_token / cert / mfa_factor / break_glass)", "must", False, "27002:5.17 — visibility"),
        ChecklistItem("item:A.5.17:reg_scope",           "Scope per row (which systems/identities use this credential type)",                                                                                  "must", False, "27002:5.17 — managed"),
        ChecklistItem("item:A.5.17:reg_vault",           "Storage vault per row (named secrets manager / KMS / cert store — never 'spreadsheet' or 'config file' for production credentials)",                "must", False, "27002:5.17 — storage"),
        ChecklistItem("item:A.5.17:reg_rotation_cadence","Rotation cadence per row (manual N-days / automated / on-event-only with stated trigger types)",                                                     "must", False, "27002:5.17 — rotation"),
        ChecklistItem("item:A.5.17:reg_mfa_required",    "MFA factor requirement per row where applicable (which factor classes; tied to access tier)",                                                       "must", False, "27002:5.17 — MFA mandate"),
        ChecklistItem("item:A.5.17:reg_owner",           "Named owner per row (human owner accountable for this credential type — covers governance, escalation, retirement decisions)",                       "must", False, "Accountability"),
        ChecklistItem("item:A.5.17:reg_identity_link",   "Identity-register linkage per row (which identity types use this credential type — closes the loop with A.5.16)",                                  "must", False, "27002:5.17 + cross-link to [[A.5.16]]"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.17:reg_last_rotated",    "Last-rotated timestamp per row where applicable (drives drift detection — stale-rotation alert)",                                                    "should", False, "Drift prevention"),
        ChecklistItem("item:A.5.17:reg_phishing_resistant","Phishing-resistant flag per row where the credential is phishing-resistant (FIDO2, passkeys, hardware-token) vs phishable (SMS, password)",       "should", False, "Modern direction tracking"),
    ],
)

REQ_A517_PROGRAM_REVIEW = EvidenceRequirement(
    id             = "req:A.5.17:authentication_program_review",
    control_ref    = "A.5.17",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic Authentication-Information Program Review",
    trigger_type   = "universal",
    description    = "The credential program creates value only if credentials actually rotate, MFA actually enrols, vault discipline actually holds and compromise responses actually fire. The review captures the planned-interval check: rotation-compliance audit, MFA enrolment coverage, vault-discipline audit (secrets outside the vault), compromise-response sample, and resulting program adjustments. Cadence tightened to 180 days — credential hygiene churns continuously",
    freshness_days = 180,
    must_contain   = [
        ChecklistItem("item:A.5.17:rev_date",             "Review date within the planned 180-day interval",                                                                          "must", False, "27002:5.17 — periodic"),
        ChecklistItem("item:A.5.17:rev_reviewer",         "Reviewer identity (IT identity-lead + InfoSec lead jointly; vault custodian where vault discipline is in scope)",          "must", False, "Accountability"),
        ChecklistItem("item:A.5.17:rev_rotation_compliance","Rotation-compliance audit (sample of credentials past their rotation cadence; root cause per stale credential)",         "must", False, "27002:5.17 — rotation enforcement"),
        ChecklistItem("item:A.5.17:rev_mfa_coverage",     "MFA enrolment coverage audit (% of in-scope identities with MFA enrolled; gap analysis per uncovered identity type)",      "must", False, "27002:5.17 — MFA mandate verification"),
        ChecklistItem("item:A.5.17:rev_vault_discipline", "Vault-discipline audit (sample of production systems re-checked: are credentials in the vault, or in config files / spreadsheets / chat history?)", "must", False, "27002:5.17 — storage discipline"),
        ChecklistItem("item:A.5.17:rev_compromise_sample","Compromise-response sample (recent compromise events re-examined: was rotation forced? was scope expansion checked?)",     "must", False, "27002:5.17 — compromise response"),
        ChecklistItem("item:A.5.17:rev_actions",          "Action items captured (e.g. expand MFA to remaining identity types, automate rotation for service tokens, retire phishable factors)", "must", False, "27002:5.17 — program adjustments"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.17:rev_phishing_progression","Phishing-resistance progression review (delta in phishing-resistant credential ratio since last review; roadmap to higher coverage)", "should", False, "Modern direction tracking"),
        ChecklistItem("item:A.5.17:rev_next_date",        "Next planned review date stated (within 180d of this review)",                                                              "should", False, "Planning"),
    ],
)

REQ_A517_REVOCATION_RECORD = EvidenceRequirement(
    id            = "req:A.5.17:credential_revocation_record",
    control_ref   = "A.5.17",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Per-Credential Revocation / Reissue Record",
    trigger_type  = "universal",
    description   = "A.5.17 expects every credential revocation to be evidenced — credentials issued and never retired are the basis of every credential-stuffing risk that materialises years later. The revocation record evidences each disable/reissue event: credential ref, trigger type, effective time, actual revocation timestamp, replacement issued (if applicable), residual-access-cleanup. One record per credential event, paired with the corresponding A.5.16 identity revocation record where the trigger is identity-level. Independent records fire for credential-only events (rotation, lost-token reissue, factor downgrade)",
    must_contain  = [
        ChecklistItem("item:A.5.17:rev_credential_ref",  "Credential identifier per record (links to credential register entry; specific instance, not just type)",                  "must", False, "27002:5.17 — traceability"),
        ChecklistItem("item:A.5.17:rev_trigger_type",    "Trigger type per record (identity_termination / rotation_due / compromise_detected / lost_token / factor_change / decommission)", "must", False, "27002:5.17 — trigger taxonomy"),
        ChecklistItem("item:A.5.17:rev_effective_time",  "Effective time per record (when the revocation needed to take effect — immediate for compromise, end-of-day for rotation)", "must", False, "Timeliness anchor"),
        ChecklistItem("item:A.5.17:rev_actual_timestamp","Actual revocation timestamp per record (drives the SLA-met calculation analogous to A.5.16; compromise revocations have tighter SLA)", "must", False, "27002:5.17 — timeliness"),
        ChecklistItem("item:A.5.17:rev_replacement",     "Replacement-issued status per record where applicable (rotation replaces credential; compromise may force forced re-enrolment, not just rotation)", "must", False, "27002:5.17 — continuity"),
        ChecklistItem("item:A.5.17:rev_residual_check",  "Residual-access check per record (sessions invalidated, refresh tokens revoked, cached credentials purged — not just the credential record disabled)", "must", False, "27002:5.17 — full revocation"),
        ChecklistItem("item:A.5.17:rev_identity_pair",   "Cross-reference to paired A.5.16 identity revocation record where this credential revocation was identity-triggered (closes the loop)", "must", False, "27002:5.17 + cross-link to [[A.5.16]]"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.17:rev_scope_expansion", "Scope-expansion check per compromise record (if a credential was compromised, what else might the actor have accessed? — surfaces lateral-movement concerns to A.5.25/A.5.26)", "should", False, "Closing loop with [[A.5.25]] / [[A.5.26]]"),
        ChecklistItem("item:A.5.17:rev_post_revoke_audit","Post-revocation verification window noted (e.g. 7-day check that no stale auth attempts using the revoked credential succeed)",         "should", False, "Continual assurance"),
    ],
)

# ── Annex A.5.19 — InfoSec in supplier relationships — operational_process (4-leaf) ──
# Promoted 2026-05-31 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: operational_process → procedure
# + register + review_record + revocation_record. "Revocation" is realised
# here as supplier-offboarding records (data return, access removal, transition
# completion). The procedure leaf id is preserved; three siblings are new.
# Authority: ISO 27002:2022 § 5.19 implementation guidance items a–n.

REQ_A519_SUPPLIER_RISK_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.19:supplier_risk_procedure",
    control_ref   = "A.5.19",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Supplier Information Security Risk Management Procedure",
    trigger_type  = "universal",
    description   = "A.5.19 requires processes and procedures to manage information security risks arising from supplier relationships. The procedure documents how supplier types are identified, how selection happens, how due diligence is conducted, how monitoring is run, and how requirements get into the agreement (A.5.20). The supplier register, periodic review and offboarding records are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.19:supplier_types",       "Supplier types identified and documented (ICT services, ICT infrastructure components, logistics, utilities, financial, etc.)", "must", False, "27002:5.19a"),
        ChecklistItem("item:A.5.19:selection_criteria",   "Selection and evaluation criteria based on sensitivity of information and services (risk analysis, references, attestations)",  "must", False, "27002:5.19b,c"),
        ChecklistItem("item:A.5.19:risk_rules",           "InfoSec rules per supplier type / access type with minimum requirements",                                                       "must", False, "27002:5.19d,g,h"),
        ChecklistItem("item:A.5.19:due_diligence",        "Due diligence steps before engagement (questionnaire, attestation review, audit)",                                              "must", False, "27002:5.19c"),
        ChecklistItem("item:A.5.19:ongoing_monitoring",   "Ongoing monitoring approach (periodic reassessment, event-triggered review, third-party reports)",                              "must", False, "27002:5.19e,i"),
        ChecklistItem("item:A.5.19:agreement_handoff",    "Conditions under which security requirements get into the supplier agreement (handoff to A.5.20)",                              "must", False, "27002:5.19l"),
        ChecklistItem("item:A.5.19:training_personnel",   "Training of own personnel on appropriate engagement and information exchange with suppliers",                                   "must", False, "27002:5.19k"),
        ChecklistItem("item:A.5.19:incident_joint_mgmt",  "Incident and contingency handling jointly with the supplier",                                                                   "must", False, "27002:5.19n"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.19:tiering_model",        "Tiering model with concrete criteria (data sensitivity, dependency, financial exposure)",                                       "should", False, "27002:5.19b — risk-proportionate"),
        ChecklistItem("item:A.5.19:questionnaire_ref",    "Reference to standard supplier security questionnaire",                                                                         "should", False, "Consistency"),
        ChecklistItem("item:A.5.19:resilience_plan",      "Backup or alternative supplier processes / treatment of supplier disruption",                                                   "should", False, "27002:5.19j"),
    ],
)

REQ_A519_REGISTER = EvidenceRequirement(
    id            = "req:A.5.19:supplier_register",
    control_ref   = "A.5.19",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Supplier Register",
    trigger_type  = "universal",
    description   = "A.5.19 requires the org to know who its suppliers are, what they provide, the nature of access they hold, and their risk classification. The register is the live source of truth — feeding the periodic review and offboarding leaves",
    must_contain  = [
        ChecklistItem("item:A.5.19:reg_inventory",        "Each supplier captured: identity, products/services, criticality",                                                              "must", False, "27002:5.19a — types"),
        ChecklistItem("item:A.5.19:reg_supplier_type",    "Supplier type per row (ICT service / ICT infra component / logistics / utilities / etc.)",                                      "must", False, "27002:5.19a"),
        ChecklistItem("item:A.5.19:reg_access_type",      "Access type per row (logical / physical / network / application / app-to-app)",                                                 "must", False, "27002:5.19g"),
        ChecklistItem("item:A.5.19:reg_classification",   "Risk classification (tier or category) per row",                                                                                 "must", False, "27002:5.19b,d"),
        ChecklistItem("item:A.5.19:reg_owner",            "Named internal owner accountable per supplier (relationship owner + InfoSec contact)",                                          "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.19:reg_critical_flag",    "Critical-supplier flag (drives audit + continuity scrutiny — link to A.5.29 / A.5.30)",                                          "should", False, "27002:5.19j"),
        ChecklistItem("item:A.5.19:reg_subsupplier",      "Disclosed sub-suppliers / fourth parties tracked per row",                                                                       "should", False, "Supply-chain depth"),
    ],
)

REQ_A519_REVIEW = EvidenceRequirement(
    id             = "req:A.5.19:portfolio_review",
    control_ref    = "A.5.19",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic Supplier Portfolio Review",
    trigger_type   = "universal",
    description    = "A.5.19 expects periodic review of the supplier portfolio — to refresh risk classifications, re-test selection criteria, and confirm that monitoring and training arrangements still fit the supplier mix",
    freshness_days = 365,
    must_contain   = [
        ChecklistItem("item:A.5.19:rev_date",             "Review date within the planned interval",                                                                                       "must", False, "27002:5.19e — periodic"),
        ChecklistItem("item:A.5.19:rev_reviewer",         "Reviewer identity and role (typically procurement + InfoSec lead)",                                                              "must", False, "Accountability"),
        ChecklistItem("item:A.5.19:rev_outcome",          "Outcome per supplier or per tier (no change / re-tiered / added / removed)",                                                     "must", False, "27002:5.19e"),
        ChecklistItem("item:A.5.19:rev_actions",          "Action items captured where monitoring or training arrangements need adjustment",                                                "must", False, "27002:5.19i,k"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.19:rev_triggers",         "Ad-hoc triggers (M&A, market events, new business line, supplier incident) prompting unscheduled review",                        "should", False, "Change-driven review"),
        ChecklistItem("item:A.5.19:rev_next_date",        "Next planned review date stated",                                                                                                "should", False, "Planning"),
    ],
)

REQ_A519_OFFBOARDING = EvidenceRequirement(
    id            = "req:A.5.19:offboarding_record",
    control_ref   = "A.5.19",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Supplier Offboarding Records",
    trigger_type  = "universal",
    description   = "A.5.19 requires that transitions at the end of a supplier relationship are managed — anything that needs to move (information, processing facilities, access) does move. Offboarding records evidence that those transitions actually happened: data returned/destroyed, access removed, lessons captured. One record per offboarding event, traceable back to the supplier register",
    must_contain  = [
        ChecklistItem("item:A.5.19:off_trigger",          "Offboarding trigger captured (termination / non-renewal / supplier failure / re-tendering)",                                     "must", False, "27002:5.19m"),
        ChecklistItem("item:A.5.19:off_data_return",      "Data return or destruction evidence (with attestation from supplier where applicable)",                                          "must", False, "27002:5.19m"),
        ChecklistItem("item:A.5.19:off_access_removal",   "Logical and physical access removal evidence (link to A.5.18 / A.7.2)",                                                          "must", False, "27002:5.19m"),
        ChecklistItem("item:A.5.19:off_transition",       "Transition completion evidence (operational handover, replacement supplier engaged where applicable)",                          "must", False, "27002:5.19m"),
        ChecklistItem("item:A.5.19:off_authoriser",       "Authoriser of the offboarding decision",                                                                                         "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.19:off_timeliness",       "Timeliness target stated (e.g., access removed within 5 business days of contract end)",                                        "should", False, "Operational sufficiency"),
        ChecklistItem("item:A.5.19:off_lessons",          "Lessons-learned link feeding back into the procedure or selection criteria",                                                    "should", False, "Continual improvement"),
    ],
)

# ── Annex A.5.20 — Security in supplier agreements — operational_process (4-leaf) ──
# Promoted 2026-05-31 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: operational_process → primary
# artefact + register + review_record + revocation_record, adapted for an
# agreement-template control: the template *is* the primary artefact, the
# coverage register tracks which supplier got which template version, and the
# deviation register fills the lifecycle-end slot — every softened or omitted
# clause is the supplier "exiting" the standard template path. The template
# leaf id is preserved; three siblings are new.
# Authority: ISO 27002:2022 § 5.20 implementation guidance items a–r.

REQ_A520_SUPPLIER_AGREEMENT_TEMPLATE = EvidenceRequirement(
    id            = "req:A.5.20:supplier_agreement_security_template",
    control_ref   = "A.5.20",
    standard_id   = "ISO27001:2022",
    evidence_type = "agreement_template",
    title         = "Supplier Agreement Security Requirements Template",
    trigger_type  = "universal",
    description   = "A.5.20 requires information security requirements to be established and agreed with each supplier based on the relationship type. The template is the standard clause set attached to supplier agreements; the coverage register, periodic template review and deviation register are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.20:minimum_requirements", "Minimum security requirements (controls baseline, certifications expected)",                                                    "must", False, "27002:5.20a,g"),
        ChecklistItem("item:A.5.20:classification_map",   "Information classification mapping (org scheme → supplier scheme where they differ)",                                            "must", False, "27002:5.20b"),
        ChecklistItem("item:A.5.20:legal_compliance",     "Legal, statutory, regulatory, contractual obligations (data protection, IP, copyright)",                                        "must", False, "27002:5.20c,p"),
        ChecklistItem("item:A.5.20:data_handling",        "Data handling requirements (encryption at rest and in transit, location/sovereignty)",                                          "must", False, "27002:5.20a — security requirements"),
        ChecklistItem("item:A.5.20:acceptable_use",       "Acceptable + unacceptable use rules stated",                                                                                    "must", False, "27002:5.20e"),
        ChecklistItem("item:A.5.20:authorized_personnel", "Named or role-defined authorized personnel + conditions for access",                                                            "must", False, "27002:5.20f"),
        ChecklistItem("item:A.5.20:incident_notification","Incident notification clause with timeline (e.g. within 24h of detection) + collaboration during remediation",                  "must", False, "27002:5.20h"),
        ChecklistItem("item:A.5.20:training_awareness",   "Training and awareness requirements specific to information and access",                                                        "must", False, "27002:5.20i"),
        ChecklistItem("item:A.5.20:subprocessor_limits",  "Sub-processor / fourth-party restrictions, approval process and propagation of requirements",                                   "must", False, "27002:5.20j"),
        ChecklistItem("item:A.5.20:incident_contacts",    "Security incident contacts named on each side",                                                                                 "must", False, "27002:5.20k"),
        ChecklistItem("item:A.5.20:screening",            "Screening / vetting requirements for supplier personnel (where applicable)",                                                    "must", False, "27002:5.20l"),
        ChecklistItem("item:A.5.20:audit_rights",         "Audit rights (right to audit; accept attestations like ISO 27001 / SOC 2 in lieu)",                                             "must", False, "27002:5.20m,o"),
        ChecklistItem("item:A.5.20:defect_resolution",    "Defect resolution and conflict resolution processes",                                                                          "must", False, "27002:5.20n"),
        ChecklistItem("item:A.5.20:termination_return",   "Termination obligations: data return/destruction, transition arrangements, handover of records",                                "must", False, "27002:5.20q,r"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.20:security_sla",         "Security-specific SLAs (e.g. patching cadence, MFA requirements, vulnerability remediation timelines)",                          "should", False, "Measurable accountability"),
        ChecklistItem("item:A.5.20:tier_variants",        "Variant clause sets per supplier tier",                                                                                          "should", False, "Proportionality"),
    ],
)

REQ_A520_COVERAGE_REGISTER = EvidenceRequirement(
    id            = "req:A.5.20:coverage_register",
    control_ref   = "A.5.20",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Supplier Agreement Coverage Register",
    trigger_type  = "universal",
    description   = "An approved template alone does not protect the org — each supplier agreement must actually carry the relevant clauses. The coverage register tracks, per supplier, the template version applied, the date the agreement was signed, the agreement term, and the supplier tier — so it is auditable that the agreed clauses are in force",
    must_contain  = [
        ChecklistItem("item:A.5.20:cov_template_version", "Template version applied per supplier",                                                                                        "must", False, "27002:5.20 — agreed"),
        ChecklistItem("item:A.5.20:cov_signed_date",      "Signed-date of the active agreement per supplier",                                                                              "must", False, "Accountability"),
        ChecklistItem("item:A.5.20:cov_term",             "Agreement term and renewal/expiry date per row",                                                                                "must", False, "Lifecycle"),
        ChecklistItem("item:A.5.20:cov_tier",             "Supplier tier per row (drives which clause variant is required)",                                                               "must", False, "Proportionality"),
        ChecklistItem("item:A.5.20:cov_owner",            "Named owner accountable for the agreement (typically procurement or legal partner)",                                            "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.20:cov_subprocessors",    "Approved sub-processors per supplier tracked (link to A.5.19 supplier register)",                                               "should", False, "27002:5.20j"),
        ChecklistItem("item:A.5.20:cov_jurisdiction",     "Governing jurisdiction per agreement",                                                                                          "should", False, "27002:5.20c,p"),
    ],
)

REQ_A520_REVIEW = EvidenceRequirement(
    id             = "req:A.5.20:template_review",
    control_ref    = "A.5.20",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic Supplier Agreement Template Review",
    trigger_type   = "universal",
    description    = "The supplier agreement template ages: regulations change, threat landscape shifts, internal control baselines evolve. The periodic review captures who reviewed it, when, what changed, and the re-papering plan for existing supplier agreements that need to catch up",
    freshness_days = 365,
    must_contain   = [
        ChecklistItem("item:A.5.20:rev_date",             "Review date within the planned interval",                                                                                       "must", False, "27002:5.20 — periodic"),
        ChecklistItem("item:A.5.20:rev_reviewer",         "Reviewer identity (legal + InfoSec lead jointly)",                                                                              "must", False, "Accountability"),
        ChecklistItem("item:A.5.20:rev_regulatory",       "Regulatory changes considered (data protection, sector-specific obligations)",                                                  "must", False, "27002:5.20c,p"),
        ChecklistItem("item:A.5.20:rev_threat_landscape", "Threat-landscape changes considered (e.g. emergent incident-notification expectations)",                                        "must", False, "27002:5.20 — keep current"),
        ChecklistItem("item:A.5.20:rev_outcome",          "Outcome (no change / amended; version increment if amended)",                                                                   "must", False, "27002:5.20"),
        ChecklistItem("item:A.5.20:rev_repapering",       "Re-papering plan for existing supplier agreements that need to catch up to a new template version",                              "must", False, "Operational sufficiency"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.20:rev_external_input",   "External counsel or industry-benchmark input considered",                                                                       "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.20:rev_next_date",        "Next planned review date stated",                                                                                                "should", False, "Planning"),
    ],
)

REQ_A520_DEVIATIONS = EvidenceRequirement(
    id            = "req:A.5.20:deviation_register",
    control_ref   = "A.5.20",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Supplier Agreement Deviation Register",
    trigger_type  = "universal",
    description   = "Where a supplier successfully negotiates softer terms than the template (or omits a clause entirely), the org needs an auditable record: which clause, which supplier, the reason, the compensating control, the approver. This is the lifecycle-end slot of operational_process applied to agreements: each deviation is the supplier 'exiting' the standard template path",
    must_contain  = [
        ChecklistItem("item:A.5.20:dev_clause",           "Clause deviated from per row (identified by template section)",                                                                 "must", False, "Audit defensibility"),
        ChecklistItem("item:A.5.20:dev_supplier",         "Supplier identifier per row (link to A.5.19 supplier register)",                                                                "must", False, "Accountability"),
        ChecklistItem("item:A.5.20:dev_reason",           "Reason for the deviation captured (commercial necessity, market constraint, supplier capability)",                              "must", False, "Audit defensibility"),
        ChecklistItem("item:A.5.20:dev_compensating",     "Compensating control stated (monitoring, contractual remedy, alternative requirement)",                                         "must", False, "Risk-based"),
        ChecklistItem("item:A.5.20:dev_approver",         "Approver of the deviation, at level proportional to residual risk",                                                              "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.20:dev_expiry",           "Expiry / re-papering target date for each deviation (so deviations age out rather than persist indefinitely)",                  "should", False, "Drift control"),
        ChecklistItem("item:A.5.20:dev_reassessment",     "Trigger for reassessment when supplier or risk circumstances change",                                                            "should", False, "Change-driven"),
    ],
)

# ── Annex A.5.21 — InfoSec in the ICT supply chain — operational_process (4-leaf) ──
# Promoted 2026-05-31 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: operational_process → procedure
# + register + review_record + revocation_record. The lifecycle-end slot is
# realised as EOL replacement records — each ICT component reaching end-of-life
# is the supply-chain equivalent of revocation. The procedure leaf id is
# preserved; three siblings are new.
# Authority: ISO 27002:2022 § 5.21 implementation guidance items a–i.

REQ_A521_ICT_SUPPLY_CHAIN = EvidenceRequirement(
    id            = "req:A.5.21:ict_supply_chain_procedure",
    control_ref   = "A.5.21",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "ICT Supply Chain Information Security Procedure",
    trigger_type  = "universal",
    description   = "A.5.21 requires processes to manage information security risks in the ICT products and services supply chain. The procedure covers sourcing, integrity verification, sub-supplier visibility, requirements propagation and identification of critical components. The component register, periodic review and EOL-replacement records are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.21:sourcing_controls",        "Sourcing controls (approved vendor list, banned-vendor list, country-of-origin considerations)",                            "must", False, "27002:5.21a"),
        ChecklistItem("item:A.5.21:requirements_propagation", "ICT service / product suppliers required to propagate requirements through their sub-contractors / component suppliers",   "must", False, "27002:5.21b,c"),
        ChecklistItem("item:A.5.21:monitoring_validation",    "Monitoring and validation methods for conformance to stated security requirements",                                          "must", False, "27002:5.21d"),
        ChecklistItem("item:A.5.21:critical_components",      "Identification of critical components needing special scrutiny (especially when outsourced)",                                "must", False, "27002:5.21e"),
        ChecklistItem("item:A.5.21:traceability",             "Traceability of critical components through the supply chain (end-to-end provenance)",                                       "must", False, "27002:5.21f"),
        ChecklistItem("item:A.5.21:integrity_verification",   "Component integrity verification on delivery (signed firmware, signed packages, hash verification)",                         "must", False, "27002:5.21g"),
        ChecklistItem("item:A.5.21:subsupplier_visibility",   "Sub-supplier visibility expectations (disclosure of components, fourth-party listing)",                                      "must", False, "27002:5.21b,c"),
        ChecklistItem("item:A.5.21:patching_expectations",    "Support and patching expectations stated for each ICT product/service",                                                      "must", False, "27002:5.21i"),
        ChecklistItem("item:A.5.21:incident_sharing",         "Rules for sharing information about supply chain issues or compromises with suppliers and within own group",                "must", False, "27002:5.21h"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.21:secure_development",       "Secure development practice expectations for software vendors",                                                              "should", False, "Vendor maturity bar"),
        ChecklistItem("item:A.5.21:sbom_expectation",         "SBOM expectations for software components and infrastructure",                                                              "should", False, "Modern supply-chain hygiene"),
    ],
)

REQ_A521_REGISTER = EvidenceRequirement(
    id            = "req:A.5.21:ict_component_register",
    control_ref   = "A.5.21",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "ICT Component / Vendor Register",
    trigger_type  = "universal",
    description   = "A.5.21 requires the org to know which ICT components are in use, who supplies them, which are critical, when they reach end-of-life, and what sub-suppliers stand behind them. The register is the live source of truth — feeding the periodic review and EOL-replacement leaves",
    must_contain  = [
        ChecklistItem("item:A.5.21:reg_component",        "Component / service identified per row (vendor, product, version)",                                                              "must", False, "27002:5.21e — track"),
        ChecklistItem("item:A.5.21:reg_critical_flag",    "Critical-component flag per row (drives 27002:5.21e scrutiny)",                                                                  "must", False, "27002:5.21e"),
        ChecklistItem("item:A.5.21:reg_eol_date",         "End-of-support / end-of-life date per row",                                                                                      "must", False, "27002:5.21i"),
        ChecklistItem("item:A.5.21:reg_subsupplier",      "Disclosed sub-suppliers / fourth parties per row",                                                                               "must", False, "27002:5.21b,c"),
        ChecklistItem("item:A.5.21:reg_owner",            "Named internal owner per component (typically architecture or platform team)",                                                   "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.21:reg_sbom_ref",         "SBOM hash / version reference per software component",                                                                           "should", False, "Modern supply-chain hygiene"),
        ChecklistItem("item:A.5.21:reg_vendor_check",     "Approved-vendor / banned-vendor list check stamp per row",                                                                       "should", False, "27002:5.21a"),
    ],
)

REQ_A521_REVIEW = EvidenceRequirement(
    id             = "req:A.5.21:supply_chain_review",
    control_ref    = "A.5.21",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic ICT Supply Chain Review",
    trigger_type   = "universal",
    description    = "ICT supply chains are volatile — vendor M&A, EOL pipelines, new vulnerability disclosures and sub-supplier shifts can move risk significantly inside a year. The review record captures the planned-interval review of the component register, the vendor-maturity assessment, the EOL pipeline and the resulting action items",
    freshness_days = 180,
    must_contain   = [
        ChecklistItem("item:A.5.21:rev_date",             "Review date within the planned interval",                                                                                       "must", False, "27002:5.21 — periodic"),
        ChecklistItem("item:A.5.21:rev_reviewer",         "Reviewer identity (typically architecture lead + InfoSec lead)",                                                                "must", False, "Accountability"),
        ChecklistItem("item:A.5.21:rev_eol_pipeline",     "EOL pipeline review (which components reach EOL in the next planning horizon, replacement status)",                              "must", False, "27002:5.21i"),
        ChecklistItem("item:A.5.21:rev_maturity",         "Vendor maturity review (recent attestations, incidents, sub-supplier disclosures)",                                              "must", False, "27002:5.21d"),
        ChecklistItem("item:A.5.21:rev_actions",          "Action items captured per critical component (e.g. tighten monitoring, push for upgrade, replan replacement)",                  "must", False, "27002:5.21d,i"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.21:rev_threat_intel",     "External threat intelligence input considered (link to A.5.7)",                                                                  "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.21:rev_next_date",        "Next planned review date stated",                                                                                                "should", False, "Planning"),
    ],
)

REQ_A521_EOL_REPLACEMENT = EvidenceRequirement(
    id            = "req:A.5.21:eol_replacement_record",
    control_ref   = "A.5.21",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "ICT Component End-of-Life Replacement Records",
    trigger_type  = "universal",
    description   = "A.5.21 requires components to be replaced before they reach end-of-life or end-of-support, or compensated for with stated controls if that is unavoidable. The replacement record evidences the actual execution: replacement selected (with sourcing controls re-applied), the cutover date, and post-replacement verification — or, where replacement was delayed, the compensating controls and risk acceptance",
    must_contain  = [
        ChecklistItem("item:A.5.21:eol_trigger",          "EOL trigger per record (vendor announcement / contract end / vulnerability-driven decommission)",                               "must", False, "27002:5.21i"),
        ChecklistItem("item:A.5.21:eol_replacement",      "Replacement component selected and sourcing controls re-applied",                                                              "must", False, "27002:5.21a,i"),
        ChecklistItem("item:A.5.21:eol_cutover",          "Cutover date executed (or compensating controls + risk acceptance where replacement was delayed)",                             "must", False, "27002:5.21i"),
        ChecklistItem("item:A.5.21:eol_verification",     "Post-replacement verification (integrity-verification, functional acceptance)",                                                "must", False, "27002:5.21g — assurance"),
        ChecklistItem("item:A.5.21:eol_authoriser",       "Authoriser of the replacement (or of the delay + risk acceptance)",                                                             "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.21:eol_forecast",         "Rolling 12-month EOL forecast linked back to the component register",                                                           "should", False, "Planning"),
        ChecklistItem("item:A.5.21:eol_lessons",          "Lessons-learned from the replacement feeding back to the procedure (e.g. sourcing-control gaps)",                              "should", False, "Continual improvement"),
    ],
)

# ── Annex A.5.22 — Monitoring, review and change management of supplier services
#                   — operational_process (4-leaf) ─────────────────────────────
# Promoted 2026-05-31 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: operational_process → primary
# artefact + register + review_record + revocation_record, adapted for a
# review-record-shaped control: the per-supplier review record is the primary
# artefact, the schedule register tracks the calendar of upcoming reviews, the
# program meta-review evaluates the review program itself, and the change-
# response log fills the lifecycle-end slot — each supplier-side change
# (network/tech/location/sub-contractor/re-tendering) is the lifecycle event
# requiring documented response. The review-record leaf id is preserved; three
# siblings are new.
# Authority: ISO 27002:2022 § 5.22 implementation guidance items a–k.

REQ_A522_SUPPLIER_REVIEW = EvidenceRequirement(
    id             = "req:A.5.22:supplier_review_record",
    control_ref    = "A.5.22",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Supplier Information Security Review Records",
    trigger_type   = "universal",
    description    = "A.5.22 requires regular monitoring, review and evaluation of supplier information security practices and service delivery. Each review record evidences the activity for one supplier in one period: performance monitored, reports reviewed, audit conducted, incidents and audit-trails examined, corrective actions tracked. The schedule register, program meta-review and change-response log are sibling leaves",
    freshness_days = 365,
    must_contain   = [
        ChecklistItem("item:A.5.22:rev_scope",            "Scope of review (security practices, service delivery, changes since last review)",                                            "must", False, "27002:5.22a,b"),
        ChecklistItem("item:A.5.22:rev_performance",      "Service performance monitored against agreement (SLAs, incidents, breaches)",                                                  "must", False, "27002:5.22a"),
        ChecklistItem("item:A.5.22:rev_reports",          "Supplier-provided service reports reviewed + progress meetings held",                                                          "must", False, "27002:5.22b"),
        ChecklistItem("item:A.5.22:rev_audit",            "Audit conducted (own audit or independent attestation accepted) with follow-up on issues",                                     "must", False, "27002:5.22c"),
        ChecklistItem("item:A.5.22:rev_incidents",        "Information exchanged about InfoSec incidents; joint review documented",                                                      "must", False, "27002:5.22d"),
        ChecklistItem("item:A.5.22:rev_audit_trails",     "Supplier audit trails / event records reviewed (operational problems, failures, disruption)",                                 "must", False, "27002:5.22e"),
        ChecklistItem("item:A.5.22:rev_problems",         "Identified problems / incidents managed through to resolution",                                                                "must", False, "27002:5.22f"),
        ChecklistItem("item:A.5.22:rev_subsupplier",      "Supplier's own supplier relationships reviewed (sub-supplier / fourth-party oversight)",                                       "must", False, "27002:5.22g"),
        ChecklistItem("item:A.5.22:rev_continuity",       "Supplier continuity capability verified (link to A.5.29 / A.5.30)",                                                            "must", False, "27002:5.22h"),
        ChecklistItem("item:A.5.22:rev_compliance",       "Supplier's compliance-review / enforcement responsibilities confirmed",                                                        "must", False, "27002:5.22i"),
        ChecklistItem("item:A.5.22:rev_corrective",       "Corrective actions raised for deficiencies, tracked to closure",                                                                "must", False, "27002:5.22j"),
        ChecklistItem("item:A.5.22:rev_findings",         "Findings recorded per review with severity",                                                                                    "must", False, "27002:5.22 — record"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.22:metrics",              "KPIs / metrics tracked per supplier (incidents, SLA breaches, time-to-remediate)",                                              "should", False, "Measurable monitoring"),
        ChecklistItem("item:A.5.22:attestations_accepted","Third-party attestations accepted in lieu of direct audit (with criteria)",                                                     "should", False, "Efficiency"),
    ],
)

REQ_A522_SCHEDULE_REGISTER = EvidenceRequirement(
    id            = "req:A.5.22:review_schedule_register",
    control_ref   = "A.5.22",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Supplier Review Schedule Register",
    trigger_type  = "universal",
    description   = "A.5.22 expects the review activity to be regular — without a schedule, 'regular' becomes 'whenever someone remembers'. The schedule register is the calendar: per supplier, the planned cadence (proportional to tier), the last review date, the next review date, and the owner",
    must_contain  = [
        ChecklistItem("item:A.5.22:sch_cadence",          "Cadence per supplier (proportional to tier — high-tier monthly, low-tier annually, etc.)",                                     "must", False, "27002:5.22 — regularly"),
        ChecklistItem("item:A.5.22:sch_last_review",      "Last review date per row",                                                                                                      "must", False, "Audit defensibility"),
        ChecklistItem("item:A.5.22:sch_next_review",      "Next review date per row",                                                                                                      "must", False, "Planning"),
        ChecklistItem("item:A.5.22:sch_owner",            "Named owner accountable for executing the review per row",                                                                      "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.22:sch_delta",            "Scheduled-vs-completed delta tracked (so missed reviews surface)",                                                              "should", False, "Operational discipline"),
        ChecklistItem("item:A.5.22:sch_tier_link",        "Linkage to A.5.19 supplier register tier (drives cadence)",                                                                     "should", False, "Cross-control consistency"),
    ],
)

REQ_A522_PROGRAM_REVIEW = EvidenceRequirement(
    id             = "req:A.5.22:program_meta_review",
    control_ref    = "A.5.22",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic Supplier Review Program Meta-Review",
    trigger_type   = "universal",
    description    = "The review program itself needs review — are we covering enough of the portfolio, is the cadence right, are findings being closed, is the program returning value? The meta-review evidences the periodic self-assessment of the program and the resulting adjustments",
    freshness_days = 365,
    must_contain   = [
        ChecklistItem("item:A.5.22:pgm_date",             "Meta-review date within the planned interval",                                                                                  "must", False, "27002:5.22 — periodic"),
        ChecklistItem("item:A.5.22:pgm_reviewer",         "Reviewer identity (program owner + InfoSec lead jointly)",                                                                      "must", False, "Accountability"),
        ChecklistItem("item:A.5.22:pgm_coverage",         "Coverage rate (fraction of supplier portfolio reviewed in period, by tier)",                                                    "must", False, "Operational discipline"),
        ChecklistItem("item:A.5.22:pgm_closure",          "Findings-closure rate (open / aged / closed) across the portfolio",                                                              "must", False, "Operational discipline"),
        ChecklistItem("item:A.5.22:pgm_outcome",          "Cadence-adjustment decisions or scope-adjustment decisions (tighten / loosen / re-tier)",                                       "must", False, "27002:5.22a,j"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.22:pgm_benchmark",        "External benchmarking or industry-practice input considered",                                                                   "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.22:pgm_next_date",        "Next planned meta-review date stated",                                                                                          "should", False, "Planning"),
    ],
)

REQ_A522_CHANGE_RESPONSE = EvidenceRequirement(
    id            = "req:A.5.22:change_response_log",
    control_ref   = "A.5.22",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Supplier Service Change Response Log",
    trigger_type  = "universal",
    description   = "A.5.22 requires the org to manage changes in supplier service delivery — network/tech changes, new dev tools, location changes, change of sub-contractors, re-tendering. Each change is evidenced by a log entry: change type captured, impact assessed, treatment decided, with escalation to termination where findings warrant",
    must_contain  = [
        ChecklistItem("item:A.5.22:chg_type",             "Change type captured (network / technology / dev tools / location / sub-contractor / re-tendering)",                            "must", False, "27002:5.22k"),
        ChecklistItem("item:A.5.22:chg_impact",           "Impact assessment on InfoSec arrangements (which controls affected, which threats opened or closed)",                          "must", False, "27002:5.22k"),
        ChecklistItem("item:A.5.22:chg_treatment",        "Treatment decided (accept / mitigate / re-paper agreement / terminate relationship)",                                          "must", False, "27002:5.22k"),
        ChecklistItem("item:A.5.22:chg_escalation",       "Escalation criteria for findings — when a finding terminates the relationship",                                                "must", False, "27002:5.22j,k"),
        ChecklistItem("item:A.5.22:chg_authoriser",       "Authoriser of the treatment decision (proportional to residual risk)",                                                          "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.22:chg_regulatory",       "Regulatory-notification check (where the change triggers a regulator-notify obligation)",                                       "should", False, "27002:5.22 — compliance"),
        ChecklistItem("item:A.5.22:chg_lessons",          "Lessons-learned feeding back to the procedure or template (link to A.5.19 / A.5.20)",                                          "should", False, "Continual improvement"),
    ],
)

# ── Annex A.5.25 — Assessment of and decision on InfoSec events
#                   — operational_process (4-leaf) ──────────────────────────────
# Promoted 2026-05-31 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: operational_process → procedure
# + register + review_record + revocation_record (lifecycle-end). The
# lifecycle-end slot is realised as the per-event triage decision record —
# each event closes as either an incident (handed off to A.5.26), a false
# positive (closed with reason), or a filed-for-trend near-miss. The
# procedure leaf id is preserved; three siblings are new.
# Authority: ISO 27002:2022 § 5.25 implementation guidance, with cross-
# references to § 5.24 (incident planning umbrella) and § 5.26 (response).

REQ_A525_EVENT_TRIAGE = EvidenceRequirement(
    id            = "req:A.5.25:event_assessment_procedure",
    control_ref   = "A.5.25",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Security Event Assessment and Triage Procedure",
    trigger_type  = "universal",
    description   = "A.5.25 requires the organization to assess information security events and decide whether to categorise them as incidents. The procedure documents detection sources, assessment criteria, decision authority, classification scale and handoff to incident response (A.5.26). The event triage log, periodic triage-program review and per-event triage decision record are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.25:detection_sources",   "Detection sources enumerated (monitoring, user reports, third parties)",                                                       "must", False, "27002:5.25 — events"),
        ChecklistItem("item:A.5.25:assessment_criteria", "Assessment criteria (impact, scope, certainty) for classifying severity",                                                       "must", False, "27002:5.25 — categorising"),
        ChecklistItem("item:A.5.25:decision_authority",  "Decision authority named (who decides event vs incident vs false positive)",                                                    "must", False, "27002:5.25 — decision"),
        ChecklistItem("item:A.5.25:classification_scale","Classification scale used (event, near-miss, incident with severity)",                                                          "must", False, "27002:5.25 — agreed classification scheme"),
        ChecklistItem("item:A.5.25:triage_timeline",     "Timeline for triage decision after detection",                                                                                  "must", False, "27002:5.25 — assess and decide"),
        ChecklistItem("item:A.5.25:handoff",             "Handoff to incident response process (A.5.26) when classified as incident",                                                     "must", False, "27002:5.25 — incidents"),
        ChecklistItem("item:A.5.25:correlation",         "Correlation / aggregation of events for trend identification (links to A.8.16 monitoring)",                                     "must", False, "27002:5.25 — correlation"),
        ChecklistItem("item:A.5.25:competent_access",    "Competent personnel given access to event/incident/weakness records",                                                           "must", False, "27002:5.25 — competent personnel"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.25:severity_matrix",     "Severity matrix with concrete examples",                                                                                        "should", False, "Consistency across triagers"),
        ChecklistItem("item:A.5.25:automation",          "Automation or playbook references for common event types",                                                                      "should", False, "Scalability"),
        ChecklistItem("item:A.5.25:legal_advisory",      "Considers who may need to be informed (legal, operational, comms) even at triage stage",                                        "should", False, "27002:5.25 — informing"),
    ],
)

REQ_A525_TRIAGE_LOG = EvidenceRequirement(
    id            = "req:A.5.25:event_triage_log",
    control_ref   = "A.5.25",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Security Event Triage Log",
    trigger_type  = "universal",
    description   = "A.5.25 expects records of events, incidents and weaknesses to be maintained and accessible to competent personnel. The triage log is the live source of truth — every triaged event, its classification, decision and owner — feeding the periodic review and the per-event triage-decision records",
    must_contain  = [
        ChecklistItem("item:A.5.25:log_event_id",        "Each event captured with a unique identifier and detection timestamp",                                                          "must", False, "27002:5.25 — records of events"),
        ChecklistItem("item:A.5.25:log_source",          "Detection source per row (which monitoring system / user / third party reported it)",                                            "must", False, "27002:5.25 — events"),
        ChecklistItem("item:A.5.25:log_classification",  "Classification per row (event / near-miss / incident / false positive) with severity",                                           "must", False, "27002:5.25 — categorised"),
        ChecklistItem("item:A.5.25:log_decision",        "Triage decision per row (close as false positive / file as near-miss / escalate to A.5.26)",                                    "must", False, "27002:5.25 — decision"),
        ChecklistItem("item:A.5.25:log_owner",           "Named triager per row (accountability)",                                                                                        "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.25:log_fp_tag",          "False-positive flag tracked separately (drives calibration in the program review)",                                             "should", False, "Calibration"),
        ChecklistItem("item:A.5.25:log_trend_tag",       "Trend / correlation tag where related events should be grouped",                                                                "should", False, "27002:5.25 — correlation"),
    ],
)

REQ_A525_PROGRAM_REVIEW = EvidenceRequirement(
    id             = "req:A.5.25:triage_program_review",
    control_ref    = "A.5.25",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic Event Triage Program Review",
    trigger_type   = "universal",
    description    = "The triage program drifts when detection sources change, attack patterns evolve, or false-positive volume creeps. The review captures who reviewed the program, when, and the resulting calibration of detection sources, assessment criteria and classification scale",
    freshness_days = 180,
    must_contain   = [
        ChecklistItem("item:A.5.25:rev_date",            "Review date within the planned interval",                                                                                      "must", False, "27002:5.25 — periodic"),
        ChecklistItem("item:A.5.25:rev_reviewer",        "Reviewer identity (SecOps lead + InfoSec lead jointly)",                                                                       "must", False, "Accountability"),
        ChecklistItem("item:A.5.25:rev_fp_rate",         "False-positive rate analysed across the period",                                                                                "must", False, "Calibration"),
        ChecklistItem("item:A.5.25:rev_missed",          "Missed-event analysis (events surfaced via lessons-learned that triage didn't catch)",                                          "must", False, "Closing the loop with A.5.27"),
        ChecklistItem("item:A.5.25:rev_calibration",     "Calibration outcome (detection sources / criteria / scale adjusted with rationale)",                                            "must", False, "27002:5.25 — keep current"),
        ChecklistItem("item:A.5.25:rev_actions",         "Action items captured (e.g. add monitoring source, adjust severity threshold)",                                                 "must", False, "27002:5.25"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.25:rev_threat_intel",    "External threat intelligence input considered (link to A.5.7)",                                                                "should", False, "Detection landscape volatility"),
        ChecklistItem("item:A.5.25:rev_next_date",       "Next planned review date stated",                                                                                              "should", False, "Planning"),
    ],
)

REQ_A525_DECISION_RECORD = EvidenceRequirement(
    id            = "req:A.5.25:triage_decision_record",
    control_ref   = "A.5.25",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Per-Event Triage Decision Records",
    trigger_type  = "universal",
    description   = "Every triaged event must close — as a false positive, as a near-miss filed for trend tracking, or by escalation to incident response (A.5.26). The decision record evidences the actual closure: which event, what was decided, the rationale, the authority, and the handoff link where applicable",
    must_contain  = [
        ChecklistItem("item:A.5.25:dec_event_ref",       "Event identifier per record (links back to the triage log row)",                                                                "must", False, "27002:5.25 — documented decision"),
        ChecklistItem("item:A.5.25:dec_outcome",         "Decision outcome captured (false positive / filed near-miss / escalated to incident)",                                          "must", False, "27002:5.25 — decision"),
        ChecklistItem("item:A.5.25:dec_rationale",       "Rationale stated (criteria-based reasoning, not just a binary outcome)",                                                        "must", False, "Audit defensibility"),
        ChecklistItem("item:A.5.25:dec_authority",       "Triage decision authority per record (named role or person)",                                                                   "must", False, "27002:5.25 — decision authority"),
        ChecklistItem("item:A.5.25:dec_handoff",         "Where escalated: handoff reference into A.5.26 incident register",                                                              "must", False, "27002:5.25 — incidents"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.25:dec_timeliness",      "Timeliness target met (decision within stated triage timeline)",                                                                "should", False, "Operational discipline"),
        ChecklistItem("item:A.5.25:dec_retro_flag",      "Retroactive-review flag where a closed event was later reopened (drives missed-event analysis in the program review)",          "should", False, "Closes loop with [[A.5.27]]"),
    ],
)

# ── Annex A.5.26 — Response to InfoSec incidents — operational_process (4-leaf) ──
# Promoted 2026-05-31 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: operational_process → procedure
# + register + review_record + revocation_record (lifecycle-end). The
# lifecycle-end slot is realised as the per-incident closure record — each
# incident closes with documented root cause, recovery validation and handoff
# to A.5.27 lessons-learned. The procedure leaf id is preserved; three
# siblings are new.
# Authority: ISO 27002:2022 § 5.26 implementation guidance items a–i, with
# cross-references to § 5.24 (planning), § 5.25 (triage), § 5.27 (lessons),
# § 5.28 (evidence handling).

REQ_A526_INCIDENT_RESPONSE_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.26:incident_response_procedure",
    control_ref   = "A.5.26",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Incident Response Procedure",
    trigger_type  = "universal",
    description   = "A.5.26 requires documented procedures for responding to information security incidents end-to-end. The procedure covers roles, containment, investigation, eradication and recovery, communication, evidence collection, action logging and closure. The incident register, periodic IR-program review and per-incident closure record are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.26:roles",                "Roles and responsibilities for incident response defined (Incident Manager, security team, comms lead, legal)",               "must", False, "27002:5.26 — coordination"),
        ChecklistItem("item:A.5.26:containment",          "Containment steps documented (immediate actions to limit damage)",                                                            "must", False, "27002:5.26a"),
        ChecklistItem("item:A.5.26:investigation",        "Investigation steps defined (root cause analysis, timeline reconstruction)",                                                  "must", False, "27002:5.26h"),
        ChecklistItem("item:A.5.26:eradication",          "Eradication and recovery steps documented (restore secure state)",                                                            "must", False, "27002:5.26e"),
        ChecklistItem("item:A.5.26:communication",        "Internal and external communication criteria specified (who is informed, when, by whom)",                                     "must", False, "27002:5.26c,g"),
        ChecklistItem("item:A.5.26:evidence_collection", "Evidence collection step embedded in response (links to A.5.28 evidence-handling procedure)",                                  "must", False, "27002:5.26b"),
        ChecklistItem("item:A.5.26:action_logging",       "All response decisions and actions logged (for evidence preservation and post-incident review)",                              "must", False, "27002:5.26f"),
        ChecklistItem("item:A.5.26:post_review",          "Post-incident review step required after closure (handoff to A.5.27 lessons-learned)",                                        "must", False, "27002:5.26 — closing + § 5.27"),
        ChecklistItem("item:A.5.26:classification_link", "References incident classification used at triage (links to A.5.25)",                                                          "must", False, "27002:5.25 → 5.26 handoff"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.26:authority_contacts",   "References authority/regulator contact list (links to A.5.5)",                                                                "should", False, "Some incidents trigger external notification"),
        ChecklistItem("item:A.5.26:exercise_freq",        "Tabletop or simulation frequency stated (semi-annual or more often)",                                                          "should", False, "Validates the procedure works under pressure"),
        ChecklistItem("item:A.5.26:nominated_contact",    "Nominated incident-handling contact named (for internal + supplier-side reporting)",                                          "should", False, "27002:5.26 — coordination"),
    ],
)

REQ_A526_INCIDENT_REGISTER = EvidenceRequirement(
    id            = "req:A.5.26:incident_register",
    control_ref   = "A.5.26",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Information Security Incident Register",
    trigger_type  = "universal",
    description   = "A.5.26 expects incidents to be tracked from detection through closure, with the trail of actions preserved. The incident register is the live master record — every incident, its severity, status, owner, and the key lifecycle dates (detection, containment, eradication, recovery, closure) — feeding the periodic IR-program review and the per-incident closure records",
    must_contain  = [
        ChecklistItem("item:A.5.26:reg_incident_id",     "Each incident captured with a unique identifier (links to A.5.25 triage decision)",                                            "must", False, "27002:5.26 — recording"),
        ChecklistItem("item:A.5.26:reg_severity",        "Severity per row (per the classification scale used at triage)",                                                                "must", False, "27002:5.26 — coordination by severity"),
        ChecklistItem("item:A.5.26:reg_status",          "Status per row (open / contained / eradicated / recovered / closed)",                                                          "must", False, "27002:5.26e"),
        ChecklistItem("item:A.5.26:reg_owner",           "Named Incident Manager / owner per row",                                                                                       "must", False, "Accountability"),
        ChecklistItem("item:A.5.26:reg_lifecycle_dates", "Lifecycle dates per row: detected / contained / eradicated / recovered / closed",                                              "must", False, "27002:5.26 — log of decisions"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.26:reg_impact_flag",     "Public-facing or regulator-relevant impact flag per row (drives notification path)",                                            "should", False, "External notification triggers"),
        ChecklistItem("item:A.5.26:reg_evidence_link",   "Reference to evidence package per row (link to A.5.28 evidence store)",                                                        "should", False, "Forensic preservation"),
    ],
)

REQ_A526_IR_REVIEW = EvidenceRequirement(
    id             = "req:A.5.26:ir_program_review",
    control_ref    = "A.5.26",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic Incident Response Program Review",
    trigger_type   = "universal",
    description    = "IR readiness erodes between exercises and between incidents. The review records the planned-interval check of the program: MTTC/MTTR trends, exercise outcomes, procedure currency against threat landscape, and the resulting calibration of roles, runbooks and contact lists",
    freshness_days = 180,
    must_contain   = [
        ChecklistItem("item:A.5.26:rev_date",            "Review date within the planned interval",                                                                                      "must", False, "27002:5.26 — periodic"),
        ChecklistItem("item:A.5.26:rev_reviewer",        "Reviewer identity (Incident Manager + InfoSec lead jointly)",                                                                  "must", False, "Accountability"),
        ChecklistItem("item:A.5.26:rev_metrics",         "MTTC / MTTR / containment-success metrics analysed across the period",                                                          "must", False, "27002:5.26 — improvement"),
        ChecklistItem("item:A.5.26:rev_exercise",        "Tabletop / simulation outcomes reviewed (or scheduled-but-not-yet-run noted)",                                                  "must", False, "27002:5.26 — exercises"),
        ChecklistItem("item:A.5.26:rev_procedure_currency","Procedure currency assessed against threat landscape + new control changes",                                                  "must", False, "27002:5.26 — keep current"),
        ChecklistItem("item:A.5.26:rev_actions",         "Action items captured (e.g. revise containment runbook, refresh contact list, schedule exercise)",                              "must", False, "27002:5.26"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.26:rev_benchmark",       "External benchmarking input considered (industry IR-metrics references)",                                                       "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.26:rev_next_date",       "Next planned review date stated",                                                                                              "should", False, "Planning"),
    ],
)

REQ_A526_CLOSURE_RECORD = EvidenceRequirement(
    id            = "req:A.5.26:incident_closure_record",
    control_ref   = "A.5.26",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Per-Incident Closure Records",
    trigger_type  = "universal",
    description   = "A.5.26 requires incidents to close with documented outcomes that feed § 5.27 lessons-learned. The closure record evidences the actual close: which incident, the root cause, the containment effectiveness, the recovery validation, and the handoff to lessons-learned. One record per incident, traceable back to the incident register",
    must_contain  = [
        ChecklistItem("item:A.5.26:cls_incident_ref",    "Incident identifier per record (links to the incident register)",                                                              "must", False, "27002:5.26 — recording"),
        ChecklistItem("item:A.5.26:cls_root_cause",      "Root cause captured (technical + organisational contributors)",                                                                "must", False, "27002:5.26h"),
        ChecklistItem("item:A.5.26:cls_containment_eff", "Containment effectiveness assessed (did the actions taken actually limit damage)",                                              "must", False, "27002:5.26a"),
        ChecklistItem("item:A.5.26:cls_recovery_valid",  "Recovery validation evidenced (system returned to secure state; verified, not just attempted)",                                  "must", False, "27002:5.26e"),
        ChecklistItem("item:A.5.26:cls_lessons_handoff", "Handoff reference into A.5.27 lessons register",                                                                                "must", False, "27002:5.26 → 5.27"),
        ChecklistItem("item:A.5.26:cls_authoriser",      "Closure authority per record (named role)",                                                                                    "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.26:cls_external_notif",  "External notifications made per record (regulators, customers, suppliers)",                                                    "should", False, "27002:5.26 — communication"),
        ChecklistItem("item:A.5.26:cls_evidence_archive","Evidence package archived per record (link to A.5.28 evidence store)",                                                          "should", False, "Forensic preservation"),
    ],
)

# ── Annex A.5.27 — Learning from InfoSec incidents — operational_process (4-leaf) ──
# Promoted 2026-05-31 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: operational_process → procedure
# + register + review_record + revocation_record (lifecycle-end). The
# lifecycle-end slot is realised as the per-lesson improvement-action record
# — the actual control update / training change / procedure amendment that
# closes the loop A.5.26 → A.5.27 → strengthened controls. The procedure
# leaf id is preserved; three siblings are new.
# Authority: ISO 27002:2022 § 5.27 implementation guidance items a–f.

REQ_A527_LESSONS_LEARNED = EvidenceRequirement(
    id            = "req:A.5.27:lessons_learned_procedure",
    control_ref   = "A.5.27",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Lessons Learned from Information Security Incidents",
    trigger_type  = "universal",
    description   = "A.5.27 requires knowledge from incidents to be used to strengthen and improve information security controls, update risk assessments, refresh incident plans, and update training. The procedure documents capture, action assignment, pattern analysis, root-cause typing and feedback into the broader control framework. The lessons register, periodic program review and per-lesson improvement-action record are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.27:trigger",             "Post-incident review trigger (every incident above a threshold, or all incidents)",                                            "must", False, "27002:5.27 — mechanism"),
        ChecklistItem("item:A.5.27:capture_format",      "Lessons capture format (what worked, what didn't, root causes, control gaps)",                                                "must", False, "27002:5.27 — knowledge"),
        ChecklistItem("item:A.5.27:actions",             "Action items assigned to owners with target dates",                                                                            "must", False, "27002:5.27a — strengthen controls"),
        ChecklistItem("item:A.5.27:tracking",            "Tracking actions to closure with status updates",                                                                              "must", False, "27002:5.27a"),
        ChecklistItem("item:A.5.27:feedback_loop",       "Feedback loop into risk register, control catalogue, and training programmes",                                                "must", False, "27002:5.27a,b,d"),
        ChecklistItem("item:A.5.27:risk_register_update","Risk-assessment update step where lessons reveal previously-unrecognised exposures",                                            "must", False, "27002:5.27b"),
        ChecklistItem("item:A.5.27:pattern_analysis",    "Recurring-pattern analysis (lessons compared across incidents to find systemic causes)",                                       "must", False, "27002:5.27e"),
        ChecklistItem("item:A.5.27:root_cause_typing",   "Root-cause typing (e.g. multiple incidents traced to lack of patching, MFA gaps)",                                              "must", False, "27002:5.27f"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.27:kb_update",           "Knowledge base or runbook update step",                                                                                        "should", False, "Captured knowledge stays useful"),
        ChecklistItem("item:A.5.27:training_refresh",    "Training refresh step where lessons reveal awareness gaps",                                                                    "should", False, "27002:5.27d"),
        ChecklistItem("item:A.5.27:ir_plan_update",      "Incident management plan / procedure update step where lessons reveal procedural gaps",                                        "should", False, "27002:5.27c"),
    ],
)

REQ_A527_LESSONS_REGISTER = EvidenceRequirement(
    id            = "req:A.5.27:lessons_register",
    control_ref   = "A.5.27",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Lessons Learned Register",
    trigger_type  = "universal",
    description   = "A.5.27 requires lessons to be captured and acted on — without a register the action items disappear into someone's mailbox. The register tracks per-lesson: the source incident, root-cause type, control or training affected, owner, status, action due date and closure date. It feeds the periodic program review and the per-lesson improvement-action records",
    must_contain  = [
        ChecklistItem("item:A.5.27:reg_lesson_id",       "Each lesson captured with a unique identifier",                                                                                 "must", False, "27002:5.27 — knowledge"),
        ChecklistItem("item:A.5.27:reg_source_incident", "Source incident reference per row (links to A.5.26 incident register)",                                                        "must", False, "27002:5.27 — from incidents"),
        ChecklistItem("item:A.5.27:reg_root_cause_type", "Root-cause type per row (drives recurring-pattern analysis)",                                                                  "must", False, "27002:5.27f"),
        ChecklistItem("item:A.5.27:reg_target",          "Target per row (which control / training / procedure is affected)",                                                            "must", False, "27002:5.27a"),
        ChecklistItem("item:A.5.27:reg_owner",           "Named owner accountable for the action per row",                                                                                "must", False, "Accountability"),
        ChecklistItem("item:A.5.27:reg_status",          "Status per row (open / in-progress / closed / accepted)",                                                                       "must", False, "27002:5.27a — tracking"),
        ChecklistItem("item:A.5.27:reg_due_closed",      "Action due date + closure date per row",                                                                                       "must", False, "Operational discipline"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.27:reg_pattern_link",    "Pattern link per row where the lesson is part of a recurring cluster",                                                          "should", False, "27002:5.27e"),
        ChecklistItem("item:A.5.27:reg_risk_update_ref", "Risk register update reference per row where applicable",                                                                       "should", False, "27002:5.27b"),
    ],
)

REQ_A527_LESSONS_REVIEW = EvidenceRequirement(
    id             = "req:A.5.27:lessons_program_review",
    control_ref    = "A.5.27",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic Lessons-Learned Program Review",
    trigger_type   = "universal",
    description    = "The lessons program creates value only if it closes the loop — actions actually get done, lessons reduce repeat incidents, and the patterns drive systemic improvements. The review captures the planned-interval check: action-closure rate, repeat-incident detection, training-impact evidence, feedback-loop effectiveness and resulting program adjustments",
    freshness_days = 365,
    must_contain   = [
        ChecklistItem("item:A.5.27:rev_date",            "Review date within the planned interval",                                                                                      "must", False, "27002:5.27 — periodic"),
        ChecklistItem("item:A.5.27:rev_reviewer",        "Reviewer identity (program owner + InfoSec lead jointly)",                                                                     "must", False, "Accountability"),
        ChecklistItem("item:A.5.27:rev_closure_rate",    "Action-closure rate analysed (open / aged / closed) against targets",                                                          "must", False, "27002:5.27a"),
        ChecklistItem("item:A.5.27:rev_repeat",          "Repeat-incident analysis (lessons that should have prevented later incidents — did they?)",                                    "must", False, "27002:5.27a,e"),
        ChecklistItem("item:A.5.27:rev_training_impact", "Training-impact evidence reviewed where lessons drove curriculum changes",                                                      "must", False, "27002:5.27d"),
        ChecklistItem("item:A.5.27:rev_actions",         "Action items captured for the program (e.g. tighten root-cause typing, expand pattern scope)",                                  "must", False, "27002:5.27"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.27:rev_benchmark",       "External benchmark or industry-practice input considered",                                                                      "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.27:rev_next_date",       "Next planned review date stated",                                                                                              "should", False, "Planning"),
    ],
)

REQ_A527_IMPROVEMENT_RECORD = EvidenceRequirement(
    id            = "req:A.5.27:improvement_action_record",
    control_ref   = "A.5.27",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Per-Lesson Improvement Action Records",
    trigger_type  = "universal",
    description   = "A.5.27 expects lessons to actually strengthen and improve controls — not just be captured in a register. The improvement-action record evidences the actual loop-closure: which lesson, what was changed (control updated / training added / procedure amended / risk formally accepted), proof of the change, authoriser and closure date. One record per closed lesson, traceable back to the lessons register and through to the source incident",
    must_contain  = [
        ChecklistItem("item:A.5.27:imp_lesson_ref",      "Lesson identifier per record (links to lessons register)",                                                                     "must", False, "27002:5.27 — knowledge applied"),
        ChecklistItem("item:A.5.27:imp_action_type",     "Action type captured (control updated / training added / procedure amended / risk accepted)",                                  "must", False, "27002:5.27a,c,d"),
        ChecklistItem("item:A.5.27:imp_evidence",        "Evidence of change (control configuration diff, training-record entry, procedure-revision link, risk-register entry)",         "must", False, "27002:5.27a — actual improvement"),
        ChecklistItem("item:A.5.27:imp_authoriser",      "Authoriser per record (proportional to scope of the change)",                                                                  "must", False, "Accountability"),
        ChecklistItem("item:A.5.27:imp_closure_date",    "Closure date recorded",                                                                                                         "must", False, "27002:5.27a — tracking"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.27:imp_effectiveness",   "Effectiveness check planned or done (post-update validation that the change actually addressed the root cause)",                "should", False, "Continual improvement"),
        ChecklistItem("item:A.5.27:imp_regression",      "Regression-prevention check (where the change replaced a previous control, verify the prior failure mode no longer applies)",  "should", False, "Operational discipline"),
    ],
)

# ── Annex A.5.28 — Collection of evidence — operational_process (4-leaf) ──────
# Promoted 2026-05-31 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: operational_process → procedure
# + register + review_record + revocation_record (lifecycle-end). Closes the
# incident-evidence triangle alongside A.5.25-27: A.5.26 closure_record's
# evidence-archive SHOULD now resolves to a custody register entry; A.5.28's
# disposal_record proves the chain-of-custody was maintained to legitimate end
# (regulator/court handover OR retention-driven destruction).
#
# Review freshness 365d — unlike A.5.25/A.5.26/A.5.7, evidence handling is
# forensic discipline that does NOT churn with the threat landscape: legal
# admissibility rules, retention obligations and forensic methodology are
# stable on a 12-month cadence. Annual review is appropriate.
#
# Authority: ISO 27002:2022 § 5.28 implementation guidance (identification,
# collection, acquisition, preservation; chain of custody; integrity
# verification; competent personnel; liaison with external authorities;
# jurisdictional considerations; storage security).

REQ_A528_EVIDENCE_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.28:evidence_collection_procedure",
    control_ref   = "A.5.28",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Evidence Identification, Collection, Acquisition, and Preservation Procedure",
    trigger_type  = "universal",
    description   = "A.5.28 requires procedures for identification, collection, acquisition, and preservation of evidence related to information security events. The procedure documents the four lifecycle steps (identification → acquisition → preservation → handover/disposal), chain of custody enforcement, integrity verification, competent personnel requirements, and liaison paths with external authorities (law enforcement, regulators). The custody register, periodic program review and per-package disposal record are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.28:identification",     "Identification step (what counts as evidence — logs, images, physical media, witness statements, network captures)",            "must", False, "27002:5.28 — identification"),
        ChecklistItem("item:A.5.28:acquisition",        "Acquisition method per evidence type (disk imaging, log export, memory capture, photographic, statement)",                      "must", False, "27002:5.28 — acquisition"),
        ChecklistItem("item:A.5.28:integrity",          "Integrity verification step (cryptographic hashes recorded at acquisition; verified at each custody handover)",                   "must", False, "27002:5.28 — preservation"),
        ChecklistItem("item:A.5.28:chain_of_custody",   "Chain-of-custody enforcement (who, what, when, where stored, signature/handover record at every transfer)",                       "must", False, "27002:5.28 — preservation"),
        ChecklistItem("item:A.5.28:preservation",       "Preservation method (read-only/write-blocked storage, secure vault, environmental controls)",                                     "must", False, "27002:5.28 — preservation"),
        ChecklistItem("item:A.5.28:competence",         "Competent personnel requirements (who is authorised to collect/handle evidence; certification expectations)",                     "must", False, "27002:5.28 — internal procedures + competence"),
        ChecklistItem("item:A.5.28:liaison",            "Liaison path with external authorities (law enforcement, regulators) — who initiates, what is required",                          "must", False, "27002:5.28 — external authorities"),
        ChecklistItem("item:A.5.28:retention",          "Retention period stated, driven by legal/regulatory obligations and case status (open investigations override default schedule)", "must", False, "27002:5.28 — preservation lifecycle"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.28:legal_admissibility",   "Legal admissibility considerations (jurisdictional rules, multi-jurisdiction scenarios)",                                       "should", False, "Evidence usable in court / regulatory"),
        ChecklistItem("item:A.5.28:third_party_forensics", "Third-party forensic engagement path (when to engage, sealed-container handover, return-to-custody on completion)",             "should", False, "Operational flexibility"),
        ChecklistItem("item:A.5.28:incident_link",         "Cross-reference to A.5.26 incident-response procedure (evidence-collection step at containment)",                                "should", False, "Closing the loop with [[A.5.26]]"),
    ],
)

REQ_A528_CUSTODY_REGISTER = EvidenceRequirement(
    id            = "req:A.5.28:evidence_custody_register",
    control_ref   = "A.5.28",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Evidence Custody Register",
    trigger_type  = "universal",
    description   = "A.5.28 requires that the integrity and provenance of every evidence package be demonstrable on demand. The custody register catalogues every evidence package handled: id, source incident, evidence type, acquisition method, acquisition hash, current custodian, current location, retention end-date, status (active/handed-over/disposed). It is the operational record that proves chain of custody at audit time",
    must_contain  = [
        ChecklistItem("item:A.5.28:reg_package_id",      "Each evidence package captured with a unique identifier",                                                                       "must", False, "27002:5.28 — identification + traceability"),
        ChecklistItem("item:A.5.28:reg_source_incident", "Source incident reference per row (links to A.5.26 incident register)",                                                          "must", False, "Closes loop with [[A.5.26]]"),
        ChecklistItem("item:A.5.28:reg_evidence_type",   "Evidence type per row (log export / disk image / memory capture / physical media / statement / photograph)",                    "must", False, "27002:5.28 — categorisation"),
        ChecklistItem("item:A.5.28:reg_acquisition_hash","Acquisition hash per row (cryptographic fingerprint recorded at point of collection)",                                          "must", False, "27002:5.28 — integrity"),
        ChecklistItem("item:A.5.28:reg_custodian",       "Current custodian per row (named individual or sealed-storage location)",                                                       "must", False, "27002:5.28 — preservation"),
        ChecklistItem("item:A.5.28:reg_location",        "Current location per row (vault id / cloud bucket reference / external-party receipt id)",                                      "must", False, "27002:5.28 — storage"),
        ChecklistItem("item:A.5.28:reg_status",          "Status per row (active / handed-over / disposed) with date of last transition",                                                  "must", False, "Operational discipline"),
        ChecklistItem("item:A.5.28:reg_retention_end",   "Retention end-date per row (drives the disposal_record trigger)",                                                                "must", False, "27002:5.28 — preservation lifecycle"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.28:reg_handover_log",    "Per-handover signature trail (immutable append-only — every transfer logs both releasing and receiving custodian)",            "should", False, "Forensic best practice"),
        ChecklistItem("item:A.5.28:reg_jurisdiction",    "Jurisdiction tag per row where evidence may cross borders (drives admissibility considerations)",                                "should", False, "Multi-jurisdiction handling"),
    ],
)

REQ_A528_PROGRAM_REVIEW = EvidenceRequirement(
    id             = "req:A.5.28:evidence_program_review",
    control_ref    = "A.5.28",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic Evidence-Handling Program Review",
    trigger_type   = "universal",
    description    = "The evidence-handling program creates value only if it actually holds up — chain-of-custody integrity must survive scrutiny by regulators and counsel. The review captures the planned-interval check: integrity-verification results, custody-incident analysis, competence/training status of authorised personnel, alignment with current legal-admissibility standards, and resulting program adjustments. Annual cadence — evidence-handling discipline is forensically stable",
    freshness_days = 365,
    must_contain   = [
        ChecklistItem("item:A.5.28:rev_date",            "Review date within the planned annual interval",                                                                                "must", False, "27002:5.28 — periodic"),
        ChecklistItem("item:A.5.28:rev_reviewer",        "Reviewer identity (InfoSec lead + legal/compliance counsel jointly)",                                                           "must", False, "Accountability"),
        ChecklistItem("item:A.5.28:rev_integrity_audit", "Integrity-verification audit (sample of register rows re-hashed; mismatches investigated)",                                     "must", False, "27002:5.28 — preservation integrity"),
        ChecklistItem("item:A.5.28:rev_custody_incidents","Custody-incident analysis (any broken-seal events, missing-handover signatures, unauthorised access flagged for review)",      "must", False, "27002:5.28 — chain of custody"),
        ChecklistItem("item:A.5.28:rev_competence",      "Competence/training status of authorised personnel reviewed (certifications current, new staff onboarded properly)",            "must", False, "27002:5.28 — competence"),
        ChecklistItem("item:A.5.28:rev_legal_alignment", "Alignment-with-current-legal-standards check (jurisdictional updates, regulator guidance, case law shifts considered)",          "must", False, "27002:5.28 — admissibility"),
        ChecklistItem("item:A.5.28:rev_actions",         "Action items captured for the program (e.g. retrain on new tooling, update jurisdiction tagging, refresh legal-counsel input)", "must", False, "27002:5.28 — program adjustments"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.28:rev_external_input",  "External benchmark or industry-practice input considered (peer review, forensic-community guidance)",                           "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.28:rev_next_date",       "Next planned review date stated",                                                                                                "should", False, "Planning"),
    ],
)

REQ_A528_DISPOSAL_RECORD = EvidenceRequirement(
    id            = "req:A.5.28:evidence_disposal_record",
    control_ref   = "A.5.28",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Per-Package Evidence Disposal / Handover Record",
    trigger_type  = "universal",
    description   = "A.5.28 requires that the chain of custody be demonstrable end-to-end — including the *end* of the chain. The disposal record evidences the legitimate closure of each evidence package: either external handover (to law enforcement, regulator, opposing counsel) with receipt OR retention-driven destruction with witness + method + final hash. One record per closed package, traceable back to the custody register and through to the source incident",
    must_contain  = [
        ChecklistItem("item:A.5.28:disp_package_ref",    "Package identifier per record (links to custody register)",                                                                    "must", False, "27002:5.28 — traceability"),
        ChecklistItem("item:A.5.28:disp_closure_type",   "Closure type per record (external_handover / retention_destruction / case_closed_internal)",                                    "must", False, "27002:5.28 — preservation lifecycle"),
        ChecklistItem("item:A.5.28:disp_authoriser",     "Authoriser per record (proportional to closure type — counsel sign-off required for external handover)",                       "must", False, "Accountability"),
        ChecklistItem("item:A.5.28:disp_method",         "Closure method per record (sealed-handover with receipt OR secure-destruction method with witness)",                            "must", False, "27002:5.28 — secure handling"),
        ChecklistItem("item:A.5.28:disp_final_hash",     "Final hash per record (handover destination hash matches register hash OR pre-destruction hash logged)",                         "must", False, "27002:5.28 — integrity at end"),
        ChecklistItem("item:A.5.28:disp_closure_date",   "Closure date recorded",                                                                                                          "must", False, "Operational discipline"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.28:disp_receipt",        "External handover receipt scanned/attached per record (where closure_type = external_handover)",                                 "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.28:disp_witness",        "Witness identity per destruction record (independent of authoriser where possible)",                                            "should", False, "Operational discipline"),
    ],
)

# ── Annex A.5.29 — Information security during disruption — operational_process (4-leaf) ──
# Promoted 2026-05-31 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: operational_process →
# plan (primary) + register + review_record + revocation_record
# (lifecycle-end). A.5.29's primary artefact is the continuity-security
# plan (the security annex to the BCP) — like A.5.14 used policy as
# primary, A.5.29 uses plan. The spine accommodates non-procedure primary
# leaves.
#
# Lifecycle-end variant: plan_activation_record — per-activation proof
# covering BOTH real disruptions AND scheduled tests (type field
# distinguishes). Position 17 in the catalogue. Distinct from A.5.24's
# exercise_record which only tracks DRILLS (never real incidents) —
# A.5.29's plan can fire either way; the activation_record handles both.
#
# Review freshness 180d — disruption landscape shifts (new cyber threats,
# new supplier dependencies, new infrastructure). Same volatility family
# as A.5.24 IR planning (180d, batch 14), A.5.25/A.5.26 incident family
# (180d, batch 4).
#
# Cross-control: scenarios MUST cross-links to A.5.7 threat-intel
# (cyber-attack scenarios); communication MUST cross-links to A.5.24
# IR framework (overlap when disruption is incident-driven); restoration
# MUST cross-links to A.5.30 ICT readiness (mechanical recovery path).
# bcp_integration SHOULD preserved (broader BCP framework outside
# scope).
#
# Authority: ISO 27002:2022 § 5.29 implementation guidance — maintain
# info security at an APPROPRIATE LEVEL (graceful degradation, not
# all-or-nothing); fallback/compensating measures; communication paths;
# restoration after disruption ends; test schedule.

REQ_A529_PLAN = EvidenceRequirement(
    id            = "req:A.5.29:information_security_during_disruption",
    control_ref   = "A.5.29",
    standard_id   = "ISO27001:2022",
    evidence_type = "plan",
    title         = "Information Security During Disruption Plan",
    trigger_type  = "universal",
    description   = "A.5.29 requires planning to maintain information security at an APPROPRIATE LEVEL during disruption — graceful degradation, not all-or-nothing. The plan documents disruption scenarios, controls that must keep operating, fallback / compensating measures, communication paths, and restoration steps. The scenario register, periodic program review and per-activation record are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.29:scenarios",           "Disruption scenarios considered (cyber attack [link to A.5.7 threat intel], natural event, supplier failure [link to A.5.21], regulatory action, key-personnel loss)", "must", False, "27002:5.29 — scenario coverage"),
        ChecklistItem("item:A.5.29:must_continue",       "Security controls that must continue operating during disruption (named explicitly — encryption, access control, audit logging at minimum)",                          "must", False, "27002:5.29 — maintain information security"),
        ChecklistItem("item:A.5.29:degradation_levels",  "Acceptable degradation levels stated (which controls can drop to compensating, which must hold at full — risk-tiered)",                                                 "must", False, "27002:5.29 — appropriate level (graceful degradation)"),
        ChecklistItem("item:A.5.29:fallback",            "Fallback / compensating security measures when primary controls fail (per-control: what replaces it, what residual risk it accepts)",                                  "must", False, "27002:5.29 — appropriate level"),
        ChecklistItem("item:A.5.29:communication",       "Communication during disruption (internal personnel, external customers, regulators, suppliers; out-of-band channels when corp comms compromised)",                    "must", False, "27002:5.29 — plan + cross-link to [[A.5.24]]"),
        ChecklistItem("item:A.5.29:restoration",         "Restoration of normal security controls after disruption ends (sequenced, verified — re-encryption, audit-log replay, access-control reactivation)",                  "must", False, "27002:5.29 — maintain + cross-link to [[A.5.30]]"),
        ChecklistItem("item:A.5.29:activation_authority","Activation authority defined (who declares the plan active; who declares it stood down; criteria for each)",                                                            "must", False, "27002:5.29 — preparation discipline"),
        ChecklistItem("item:A.5.29:test_schedule",       "Test schedule for the plan (cadence stated; promoted from SHOULD because untested continuity plans fail when actually needed)",                                        "must", False, "27002:5.29 — preparation effectiveness"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.29:bcp_integration",     "Integration with the broader Business Continuity Plan (this is the security ANNEX to the BCP — BCP itself is out of scope)",                                          "should", False, "Coherence with BCP framework"),
        ChecklistItem("item:A.5.29:residual_risk",       "Residual-risk register for disruption scenarios where degradation creates accepted exposure (named risk owner per scenario)",                                          "should", False, "Risk discipline"),
        ChecklistItem("item:A.5.29:third_party",         "Third-party-dependent controls flagged (where the plan relies on supplier action — cross-link to A.5.22 review)",                                                       "should", False, "Cross-link to [[A.5.22]]"),
    ],
)

REQ_A529_SCENARIO_REGISTER = EvidenceRequirement(
    id            = "req:A.5.29:disruption_scenario_register",
    control_ref   = "A.5.29",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Disruption Scenario Register",
    trigger_type  = "universal",
    description   = "A.5.29 requires the plan to cover all relevant scenarios — invisible scenarios are the ones that hit unprepared. The register catalogues every in-scope disruption scenario: scenario id, type, severity tier, in-scope controls, fallback path, last-test date, owner. It is the operational record that proves the plan actually covers the org's risk landscape, not just the easy scenarios",
    must_contain  = [
        ChecklistItem("item:A.5.29:reg_scenario_id",    "Each in-scope scenario captured with a unique identifier",                                                                                                  "must", False, "27002:5.29 — scenario coverage"),
        ChecklistItem("item:A.5.29:reg_type",           "Scenario type per row (cyber_attack / natural_event / supplier_failure / regulatory_action / personnel_loss / infrastructure_failure)",                     "must", False, "27002:5.29 — scenario taxonomy"),
        ChecklistItem("item:A.5.29:reg_severity",       "Severity tier per row (tier_1_full_disruption / tier_2_partial / tier_3_localised) — drives the activation path",                                          "must", False, "27002:5.29 — tier-based response"),
        ChecklistItem("item:A.5.29:reg_in_scope_ctrls", "In-scope controls per row (which security controls this scenario specifically impacts; cross-link to A.5.9 asset register for assets at risk)",            "must", False, "27002:5.29 — scope analysis + cross-link to [[A.5.9]]"),
        ChecklistItem("item:A.5.29:reg_fallback",       "Fallback path per row (which compensating measure activates; what residual risk it accepts)",                                                              "must", False, "27002:5.29 — appropriate level"),
        ChecklistItem("item:A.5.29:reg_last_tested",    "Last-tested date per row (drives stale-scenario detection — scenarios not exercised in N months flag for refresh)",                                        "must", False, "27002:5.29 — preparation cadence"),
        ChecklistItem("item:A.5.29:reg_owner",          "Named owner per row (accountable for keeping this scenario's plan section current)",                                                                       "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.29:reg_recovery_target","Recovery target per row where applicable (RTO/RPO for ICT scenarios — cross-link to A.5.30)",                                                              "should", False, "Cross-link to [[A.5.30]]"),
        ChecklistItem("item:A.5.29:reg_supplier_dep",   "Supplier dependency flag per row where the fallback relies on a specific supplier",                                                                         "should", False, "Cross-link to [[A.5.22]]"),
    ],
)

REQ_A529_PROGRAM_REVIEW = EvidenceRequirement(
    id             = "req:A.5.29:continuity_program_review",
    control_ref    = "A.5.29",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic Continuity-Security Program Review",
    trigger_type   = "universal",
    description    = "The continuity plan creates value only when actually exercised — scenarios that go stale, fallbacks that wouldn't actually work, communication paths that have changed all signal the plan is drifting. The review captures the planned-interval check: scenario-currency audit, test-result analysis, fallback-validity check, real-disruption divergence analysis, and resulting plan adjustments. Cadence tightened to 180 days — disruption landscape shifts",
    freshness_days = 180,
    must_contain   = [
        ChecklistItem("item:A.5.29:rev_date",              "Review date within the planned 180-day interval",                                                                                                       "must", False, "27002:5.29 — periodic"),
        ChecklistItem("item:A.5.29:rev_reviewer",          "Reviewer identity (CISO + BCP-program owner + Legal where regulatory comms scope; supplier-management lead where supplier-dep scenarios in scope)",     "must", False, "Accountability"),
        ChecklistItem("item:A.5.29:rev_scenario_currency", "Scenario-currency audit (each scenario in the register re-validated: still plausible? still relevant? new scenarios that should be added?)",            "must", False, "27002:5.29 — scenario freshness"),
        ChecklistItem("item:A.5.29:rev_test_results",      "Test-result analysis (last N tests reviewed; gaps surfaced; remediation per gap; ratio of scenarios tested vs total)",                                  "must", False, "27002:5.29 — preparation effectiveness"),
        ChecklistItem("item:A.5.29:rev_fallback_validity", "Fallback-validity check (sample of fallbacks re-validated: would they actually work? are dependencies still in place? are owners still in role?)",       "must", False, "27002:5.29 — appropriate level verification"),
        ChecklistItem("item:A.5.29:rev_real_divergence",   "Real-disruption divergence analysis (where actual disruptions diverged from the plan — what was missing? what assumed? what proved unnecessary?)",      "must", False, "Plan effectiveness"),
        ChecklistItem("item:A.5.29:rev_actions",           "Action items captured (e.g. add scenario, retire stale fallback, refresh communication paths, expand test scope)",                                       "must", False, "27002:5.29 — plan adjustments"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.29:rev_industry_practice", "Industry-practice scan (notable disruptions in the sector; how peers handled; lessons applicable to our plan)",                                          "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.29:rev_next_date",         "Next planned review date stated (within 180d of this review)",                                                                                            "should", False, "Planning"),
    ],
)

REQ_A529_ACTIVATION_RECORD = EvidenceRequirement(
    id            = "req:A.5.29:plan_activation_record",
    control_ref   = "A.5.29",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Per-Activation Plan Record",
    trigger_type  = "universal",
    description   = "A.5.29 expects the plan to be ACTIVATED — not just written. The activation record evidences each invocation: activation id, type (real_disruption / scheduled_test / partial_drill), scenario triggered, scope of degradation, duration, gaps surfaced, restoration status, sign-off. One record per activation, covering BOTH real disruptions AND scheduled tests (type field distinguishes). Real activations cross-reference A.5.26 incident_register where the disruption was incident-driven",
    must_contain  = [
        ChecklistItem("item:A.5.29:act_activation_id",   "Activation identifier per record (unique, sequenced)",                                                                                                       "must", False, "27002:5.29 — traceability"),
        ChecklistItem("item:A.5.29:act_type",            "Activation type per record (real_disruption / scheduled_test / partial_drill / regulator_led_exercise)",                                                     "must", False, "27002:5.29 — coverage taxonomy"),
        ChecklistItem("item:A.5.29:act_scenario_ref",    "Triggered scenario reference per record (links to scenario register entry)",                                                                                  "must", False, "27002:5.29 + cross-link to register"),
        ChecklistItem("item:A.5.29:act_scope",           "Scope of degradation per record (which controls dropped to fallback; which held at full; expected vs actual)",                                                "must", False, "27002:5.29 — appropriate level verification"),
        ChecklistItem("item:A.5.29:act_duration",        "Duration per record (start time, end time, restoration time)",                                                                                                "must", False, "27002:5.29 — timeline"),
        ChecklistItem("item:A.5.29:act_gaps",            "Gaps surfaced per record (where the plan or controls fell short; severity per gap)",                                                                          "must", False, "27002:5.29 — improvement feedback"),
        ChecklistItem("item:A.5.29:act_restoration",     "Restoration status per record (all controls back to normal; outstanding remediation items tracked)",                                                          "must", False, "27002:5.29 — maintain after disruption ends"),
        ChecklistItem("item:A.5.29:act_signoff",         "Signoff per record (activation-authority + CISO; exec sponsor where tier-1 disruption)",                                                                      "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.29:act_incident_link",   "Cross-reference to A.5.26 incident register where the activation was incident-driven (real disruptions tied to incidents)",                                  "should", False, "Closing loop with [[A.5.26]]"),
        ChecklistItem("item:A.5.29:act_lessons_feed",    "Lessons feed per record to A.5.27 lessons register where the activation surfaced patterns worth retaining beyond this control",                              "should", False, "Closing loop with [[A.5.27]]"),
    ],
)

# ── Annex A.5.30 — ICT readiness for business continuity — operational_process (4-leaf) ──
# Promoted 2026-05-31 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. Spine: operational_process →
# plan (primary) + register + review_record + revocation_record
# (lifecycle-end). **NATURAL PAIR with A.5.29** ([[curation-phase-b-
# batch-15-2026-05-31]]) — A.5.29 is the security annex to the BCP
# (what security controls hold during disruption); A.5.30 is the
# mechanical ICT recovery layer (what infrastructure comes back up,
# in what order, to what RTO/RPO).
#
# Lifecycle-end variant: HYBRID recovery_record — covers BOTH real
# recovery events AND scheduled tests (same hybrid pattern introduced
# in A.5.29 batch 15). Position 18 in the catalogue. Type field
# distinguishes real_recovery / scheduled_test / partial_drill.
#
# Review freshness 180d — same as A.5.29 (sister control). The ICT
# landscape shifts continuously (new services, vendor changes, cloud-
# pattern migrations); waiting a full year between meta-reviews lets
# RTO/RPO commitments drift out of alignment with reality.
#
# **Freshness convention change**: legacy spec had freshness_days=365
# on the plan leaf. Moved to the review_record leaf for consistency
# with the rest of the op_process spine convention (A.5.7, A.5.8,
# A.5.11, A.5.13, A.5.16, A.5.17, A.5.24, A.5.28, A.5.29 all have
# freshness ONLY on the review). The plan itself doesn't expire; the
# review cycle is what catches staleness. Behavioural impact on
# existing tenants: nil (Arion's only A.5.30 evidence is a hand-
# entered Comply finding; no uploaded plan evidence to be affected).
#
# Cross-control: register references A.5.9 asset register (assets
# under recovery); recovery_record's act_disruption_link cross-
# references A.5.29 activation_record (BCP-driven recovery events).
# Heavy mutual-link wiring with A.5.29 — the two controls together
# define the org's complete continuity stance.
#
# Authority: ISO 27002:2022 § 5.30 implementation guidance — planned,
# implemented, maintained, and tested ICT readiness; BIA-derived
# RTO/RPO targets; recovery procedures; backup + failover; test
# records.

REQ_A530_PLAN = EvidenceRequirement(
    id            = "req:A.5.30:ict_readiness_for_business_continuity",
    control_ref   = "A.5.30",
    standard_id   = "ISO27001:2022",
    evidence_type = "plan",
    title         = "ICT Readiness for Business Continuity Plan",
    trigger_type  = "universal",
    description   = "A.5.30 requires ICT readiness to be planned, implemented, maintained, and tested per business continuity objectives. The plan documents per-service RTO/RPO targets (BIA-derived), recovery procedures, backup arrangements, failover/redundancy provisions, and test cadence. The service register, periodic program review and per-recovery event record are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.30:rto_rpo",             "Recovery Time and Recovery Point Objectives per ICT service (BIA-derived; RTO = how long can it be down; RPO = how much data loss is acceptable)",     "must", False, "27002:5.30 — business continuity objectives"),
        ChecklistItem("item:A.5.30:recovery_procedures", "Recovery procedures documented per ICT service (step-by-step, runbook-style — not 'restart the system' aspirational text)",                              "must", False, "27002:5.30 — ICT readiness"),
        ChecklistItem("item:A.5.30:backup",              "Backup arrangements (frequency aligned to RPO, retention, geographic separation, restore tested and verified)",                                          "must", False, "27002:5.30 — implemented"),
        ChecklistItem("item:A.5.30:failover",            "Failover / redundancy arrangements for critical services (active-active / active-passive / cold-standby per service tier)",                              "must", False, "27002:5.30 — readiness"),
        ChecklistItem("item:A.5.30:test_records",        "Test cadence and records (last test date per service, outcome, gaps identified, remediation status)",                                                    "must", False, "27002:5.30 — tested"),
        ChecklistItem("item:A.5.30:bia_link",            "BIA-link explicit (RTO/RPO targets traceable to the Business Impact Assessment — not arbitrarily chosen numbers; cross-link to A.5.29 scenario register)", "must", False, "27002:5.30 — BIA derivation"),
        ChecklistItem("item:A.5.30:bcp_alignment",       "Alignment with A.5.29 disruption-security plan stated explicitly (this is the ICT mechanical layer; A.5.29 is the security-annex layer; both must reconcile)", "must", False, "27002:5.30 + cross-link to [[A.5.29]]"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.30:scenario_coverage",   "Test scenarios cover BOTH partial-failure AND full-outage cases (most orgs only test partial — auditor-tested concern)",                                "should", False, "Test realism"),
        ChecklistItem("item:A.5.30:communication_tree",  "Communication tree for ICT outages (who is informed, escalation thresholds, status-page update cadence)",                                                  "should", False, "Coordination"),
        ChecklistItem("item:A.5.30:third_party_recovery","Third-party-dependent recovery noted (where recovery relies on supplier action — cross-link to A.5.22 supplier review)",                                   "should", False, "Cross-link to [[A.5.22]]"),
    ],
)

REQ_A530_SERVICE_REGISTER = EvidenceRequirement(
    id            = "req:A.5.30:ict_service_register",
    control_ref   = "A.5.30",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "ICT Service Continuity Register",
    trigger_type  = "universal",
    description   = "A.5.30 requires every in-scope ICT service to have a defined recovery posture — invisible services are the ones that don't come back when the org needs them. The register catalogues every in-scope ICT service: service id, criticality tier, RTO/RPO targets, dependencies, recovery owner, last-tested date. It is the operational record that proves the plan covers the org's ACTUAL service inventory, not just the easy-to-restore subset",
    must_contain  = [
        ChecklistItem("item:A.5.30:reg_service_id",      "Each in-scope ICT service captured with a unique identifier",                                                                                              "must", False, "27002:5.30 — visibility"),
        ChecklistItem("item:A.5.30:reg_criticality",     "Criticality tier per row (tier_1_mission_critical / tier_2_business_critical / tier_3_supporting) — drives RTO/RPO selection",                            "must", False, "27002:5.30 — BIA tiering"),
        ChecklistItem("item:A.5.30:reg_rto_rpo",         "RTO/RPO targets per row (specific numeric values, not 'best effort')",                                                                                     "must", False, "27002:5.30 — business continuity objectives"),
        ChecklistItem("item:A.5.30:reg_dependencies",    "Service dependencies per row (upstream + downstream — recovery order matters; recover dependencies first)",                                                "must", False, "27002:5.30 — readiness coordination"),
        ChecklistItem("item:A.5.30:reg_recovery_owner",  "Named recovery owner per row (technical lead accountable for the service's recovery, not just IT generally)",                                              "must", False, "Accountability"),
        ChecklistItem("item:A.5.30:reg_last_tested",     "Last-tested date per row (drives stale-test detection — services not tested in N months flag for refresh)",                                                "must", False, "27002:5.30 — preparation cadence"),
        ChecklistItem("item:A.5.30:reg_asset_link",      "Asset-link per row (cross-link to A.5.9 asset register entries that constitute this service)",                                                              "must", False, "27002:5.30 + cross-link to [[A.5.9]]"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.30:reg_supplier_dep",    "Supplier dependency flag per row where recovery depends on supplier action (cross-link to A.5.21 / A.5.22)",                                              "should", False, "Cross-link to [[A.5.22]]"),
        ChecklistItem("item:A.5.30:reg_data_residency",  "Data residency note per row where backup geographic separation has jurisdictional implications (cross-link to A.5.14 transfer policy)",                  "should", False, "Cross-link to [[A.5.14]]"),
    ],
)

REQ_A530_PROGRAM_REVIEW = EvidenceRequirement(
    id             = "req:A.5.30:ict_program_review",
    control_ref    = "A.5.30",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic ICT Readiness Program Review",
    trigger_type   = "universal",
    description    = "The ICT continuity plan creates value only if RTO/RPO commitments actually hold under test — services that fall out of compliance, dependencies that have shifted, backup restores that fail, test scenarios that have gone stale all signal the plan is drifting. The review captures the planned-interval check: RTO/RPO compliance audit, dependency-currency check, restore-success-rate analysis, scenario-coverage audit, and resulting plan adjustments. Cadence tightened to 180 days — ICT landscape shifts continuously",
    freshness_days = 180,
    must_contain   = [
        ChecklistItem("item:A.5.30:rev_date",              "Review date within the planned 180-day interval",                                                                                                       "must", False, "27002:5.30 — periodic"),
        ChecklistItem("item:A.5.30:rev_reviewer",          "Reviewer identity (CTO/IT-ops head + BCP-program owner + InfoSec lead jointly; CFO sign-off where critical-service RTO has financial impact)",        "must", False, "Accountability"),
        ChecklistItem("item:A.5.30:rev_rto_compliance",    "RTO/RPO compliance audit (sample of services re-tested; gap to target per service; root cause per gap)",                                                "must", False, "27002:5.30 — objectives verification"),
        ChecklistItem("item:A.5.30:rev_dependency_check",  "Dependency-currency check (sample of services where dependency map re-validated against current reality; shifts flagged for plan update)",              "must", False, "27002:5.30 — readiness coordination"),
        ChecklistItem("item:A.5.30:rev_restore_success",   "Restore-success-rate analysis (last N restores attempted; success rate; failed restores investigated)",                                                  "must", False, "27002:5.30 — backup verification"),
        ChecklistItem("item:A.5.30:rev_scenario_coverage", "Scenario-coverage audit (which scenarios from A.5.29 register actually tested via real recovery; which still untested; remediation plan per gap)",        "must", False, "27002:5.30 + cross-link to [[A.5.29]]"),
        ChecklistItem("item:A.5.30:rev_actions",           "Action items captured (e.g. add new service, tighten RTO for service that consistently misses, retire stale scenario, refresh test schedule)",          "must", False, "27002:5.30 — plan adjustments"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.30:rev_cloud_posture",     "Cloud-provider posture noted (where ICT readiness depends on hyperscaler features — AZ failover, region replication; their SLA changes affect ours)", "should", False, "Cross-link to [[A.5.23]]"),
        ChecklistItem("item:A.5.30:rev_next_date",         "Next planned review date stated (within 180d of this review)",                                                                                            "should", False, "Planning"),
    ],
)

REQ_A530_RECOVERY_RECORD = EvidenceRequirement(
    id            = "req:A.5.30:ict_recovery_record",
    control_ref   = "A.5.30",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Per-Recovery Event Record",
    trigger_type  = "universal",
    description   = "A.5.30 expects recovery to be EVIDENCED — not just promised. The recovery record evidences each event: recovery id, type (real_recovery / scheduled_test / partial_drill), services in scope, RTO/RPO targets, actual recovery time, success status, gaps surfaced, sign-off. HYBRID variant (like A.5.29) — covers BOTH real recovery events AND scheduled tests via type field. Real recoveries cross-reference A.5.29 activation_record (BCP-driven events) and A.5.26 incident_register (incident-driven recovery)",
    must_contain  = [
        ChecklistItem("item:A.5.30:rec_recovery_id",       "Recovery event identifier per record (unique, sequenced)",                                                                                              "must", False, "27002:5.30 — traceability"),
        ChecklistItem("item:A.5.30:rec_type",              "Recovery type per record (real_recovery / scheduled_test / partial_drill / chaos_engineering_test)",                                                    "must", False, "27002:5.30 — coverage taxonomy"),
        ChecklistItem("item:A.5.30:rec_services",          "Services in scope per record (links to service register entries)",                                                                                       "must", False, "27002:5.30 + cross-link to register"),
        ChecklistItem("item:A.5.30:rec_rto_target",        "RTO target per record (what was committed)",                                                                                                              "must", False, "27002:5.30 — objectives"),
        ChecklistItem("item:A.5.30:rec_actual_time",       "Actual recovery time per record (drives the RTO-met calculation; gap to target if missed)",                                                              "must", False, "27002:5.30 — objectives verification"),
        ChecklistItem("item:A.5.30:rec_success_status",    "Success status per record (rto_met / rto_missed_with_reason / partial_recovery_acceptable / failed)",                                                    "must", False, "27002:5.30 — auditor-critical objective achievement proof"),
        ChecklistItem("item:A.5.30:rec_gaps",              "Gaps surfaced per record (where recovery fell short; severity per gap)",                                                                                  "must", False, "27002:5.30 — improvement feedback"),
        ChecklistItem("item:A.5.30:rec_signoff",           "Signoff per record (recovery owner + BCP-program owner; exec sponsor where critical-service real recovery)",                                              "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.30:rec_disruption_link",   "Cross-reference to A.5.29 plan_activation_record where this recovery was BCP-driven (closes loop)",                                                       "should", False, "Closing loop with [[A.5.29]]"),
        ChecklistItem("item:A.5.30:rec_lessons_feed",      "Lessons feed per record to A.5.27 lessons register where recovery surfaced patterns worth retaining beyond this control",                                "should", False, "Closing loop with [[A.5.27]]"),
    ],
)

# ── Annex A.5.31 — Legal / regulatory register — records_program spine (4-leaf) ─
# Promoted 2026-05-29 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. records_program spine: the register
# of applicable obligations + maintenance procedure + applicable-obligations
# scope (jurisdictions + services + customers that drive which laws apply) +
# semi-annual review (freshness=180 retained from the prior single-leaf
# because regulatory change cadence is faster than annual). The register leaf
# id is preserved; three siblings new.
# Authority: ISO 27002:2022 § 5.31 implementation guidance. Cross-link to
# A.5.5 (authority contacts) — same drivers, separate registers.

REQ_A531_OBLIGATIONS_REGISTER = EvidenceRequirement(
    id            = "req:A.5.31:legal_regulatory_register",
    control_ref   = "A.5.31",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Legal, Statutory, Regulatory and Contractual Requirements Register",
    trigger_type  = "universal",
    description   = "A.5.31 requires applicable legal, statutory, regulatory and contractual requirements relevant to information security to be identified, documented and kept up to date. The register enumerates them and maps each to the compliance approach. Maintenance procedure, applicable-obligations scope and periodic review are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.31:laws_listed",        "Applicable laws and regulations enumerated (GDPR, sectoral, jurisdictional, transfer regimes)",          "must", False, "27002:5.31a"),
        ChecklistItem("item:A.5.31:jurisdictions",      "Jurisdictions covered explicitly per entry (HQ, places of operation, customer locations, data residency)","must", False, "27002:5.31a — relevant"),
        ChecklistItem("item:A.5.31:contractual",        "Contractual obligations summarised (customer contracts, regulator agreements, sectoral codes)",          "must", False, "27002:5.31c"),
        ChecklistItem("item:A.5.31:compliance_approach","Approach for compliance per item (how the obligation is met, which controls/policies/processes evidence it)","must", False, "27002:5.31b"),
        ChecklistItem("item:A.5.31:owner_per_item",     "Owner named per requirement (who tracks change and compliance)",                                          "must", False, "Accountability"),
        ChecklistItem("item:A.5.31:last_verified",      "Last-verified or last-reviewed date per entry",                                                            "must", False, "27002:5.31 — kept up to date"),
        ChecklistItem("item:A.5.31:obligation_type",    "Obligation type tag (statutory / regulatory / contractual / sectoral-code) to drive review cadence",       "must", False, "27002:5.31 — categorisation"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.31:evidence_links",    "Links to evidence of compliance per requirement (policies, audit reports, certifications)",                "should", False, "Audit traceability"),
        ChecklistItem("item:A.5.31:change_monitoring", "Source for change monitoring per entry (legal counsel, regulator alerts, industry feed)",                  "should", False, "Currency"),
        ChecklistItem("item:A.5.31:authority_link",    "Each entry tagged with the authority(ies) responsible — cross-link to A.5.5 authority register",            "should", False, "Cross-control coherence"),
    ],
)

REQ_A531_MAINTENANCE_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.31:obligations_register_maintenance_procedure",
    control_ref   = "A.5.31",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Legal/Regulatory Register Maintenance Procedure",
    trigger_type  = "universal",
    description   = "A.5.31 expects the register to be 'kept up to date'. The procedure documents who keeps it current, what triggers an update (new regulation, regulator guidance, customer contract change, jurisdiction expansion), and the intake path from trigger to register entry",
    must_contain  = [
        ChecklistItem("item:A.5.31:proc_maintainer",       "Named maintainer (compliance lead, legal counsel, or designate) with documented responsibility for register accuracy", "must", False, "Accountability — 27002:5.31"),
        ChecklistItem("item:A.5.31:proc_update_triggers",  "Update triggers enumerated (new law/regulation, regulator guidance, new customer contract, new jurisdiction, sectoral code change)", "must", False, "27002:5.31 — kept up to date"),
        ChecklistItem("item:A.5.31:proc_intake_path",      "Intake path from trigger to register entry (who flags, who interprets, who classifies, who confirms compliance approach)", "must", False, "Operational sufficiency"),
        ChecklistItem("item:A.5.31:proc_change_assessment","Impact-assessment step when an obligation changes — affected controls and policies identified, gap actions opened",       "must", False, "27002:5.31b — approach to meet"),
        ChecklistItem("item:A.5.31:proc_authority_sync",   "Authority-contact sync — adding an obligation that introduces a new regulator triggers A.5.5 register update",            "must", False, "A.5.5 coherence"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.31:proc_legal_review",     "Legal review step before a new entry is finalised (internal or external counsel approval)",                              "should", False, "Interpretation accuracy"),
        ChecklistItem("item:A.5.31:proc_horizon_scan",     "Horizon-scanning cadence for upcoming obligations (proposed legislation, pending regulator decisions)",                   "should", False, "Forward-looking compliance"),
    ],
)

REQ_A531_APPLICABLE_OBLIGATIONS_SCOPE = EvidenceRequirement(
    id            = "req:A.5.31:applicable_obligations_scope",
    control_ref   = "A.5.31",
    standard_id   = "ISO27001:2022",
    evidence_type = "scope_note",
    title         = "Applicable Obligations Scope",
    trigger_type  = "universal",
    description   = "The upstream that drives the register. Documents the business activity surfaces — jurisdictions, services, customer types, data categories, sectoral classifications — that determine which obligations apply. ISO 27002:2022 § 5.31 expects organisations to know their applicability before listing obligations",
    must_contain  = [
        ChecklistItem("item:A.5.31:scope_jurisdictions",   "Jurisdictions covered (HQ, places of business, customer locations, data residency, transfer destinations)",            "must", False, "27002:5.31a"),
        ChecklistItem("item:A.5.31:scope_services",        "Services offered (regulated activities — payments, health data processing, telco, AI systems under upcoming regimes)",  "must", False, "27002:5.31 — relevant"),
        ChecklistItem("item:A.5.31:scope_customer_types",  "Customer types driving contractual obligations (regulated industries, government, B2C consumers)",                      "must", False, "27002:5.31c — contractual"),
        ChecklistItem("item:A.5.31:scope_data_categories", "Personal/sensitive/regulated data categories processed (drives GDPR, HIPAA, sectoral data laws)",                        "must", False, "GDPR/sectoral linkage"),
        ChecklistItem("item:A.5.31:scope_sectoral_class",  "Sectoral classification (NIS2 essential/important, DORA financial-entity, critical-infrastructure designation, etc.)",  "must", False, "27002:5.31 — applicability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.31:scope_authority_link",  "Cross-link to A.5.5 applicable-authorities scope — same drivers; shared updates",                                       "should", False, "Cross-control coherence"),
        ChecklistItem("item:A.5.31:scope_change_drivers",  "Trigger list for re-scoping (new geography, new service line, M&A, change in customer mix)",                            "should", False, "Currency"),
    ],
)

REQ_A531_REVIEW = EvidenceRequirement(
    id              = "req:A.5.31:obligations_register_review",
    control_ref     = "A.5.31",
    standard_id     = "ISO27001:2022",
    evidence_type   = "review_record",
    title           = "Periodic Legal/Regulatory Register Review",
    trigger_type    = "universal",
    description     = "Periodic verification that the register still reflects current obligations and that the compliance approach for each is still adequate. The cadence is semi-annual (freshness=180) because regulatory change is faster than annual; this matches the prior single-leaf freshness signal",
    freshness_days  = 180,
    must_contain    = [
        ChecklistItem("item:A.5.31:rev_date",            "Review date within the planned interval (within 6 months of last review)",                                      "must", False, "27002:5.31 — kept up to date"),
        ChecklistItem("item:A.5.31:rev_reviewer",        "Reviewer identity and role recorded (compliance lead with legal-counsel sign-off where material)",              "must", False, "Accountability"),
        ChecklistItem("item:A.5.31:rev_per_entry",       "Per-entry outcome (verified / amended / retired / new added) with compliance-approach still-adequate confirmation","must", False, "27002:5.31b"),
        ChecklistItem("item:A.5.31:rev_scope_check",     "Cross-check against the applicable-obligations scope — any new applicability that should add entries",          "must", False, "Cross-leaf coherence"),
        ChecklistItem("item:A.5.31:rev_horizon",         "Forward-looking section — obligations entering force in the next 12-24 months that need preparation",            "must", False, "Forward-looking compliance"),
        ChecklistItem("item:A.5.31:rev_register_update", "Changes propagated back to the live register with reference to this review",                                     "must", False, "Closes the loop"),
    ],
    should_contain  = [
        ChecklistItem("item:A.5.31:rev_ad_hoc_triggers", "Ad-hoc review triggers listed (major regulator action, court ruling, customer contract restructure)",          "should", False, "Change-driven review"),
        ChecklistItem("item:A.5.31:rev_next_date",       "Next planned review date stated",                                                                                "should", False, "Planning"),
    ],
)

# ── Annex A.5.32 — Intellectual property — records_program (adapted, 4-leaf) ──
# Promoted 2026-05-29 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. records_program spine adapted — A.5.32
# has both procedural and inventory aspects, so the procedure leaf stays
# alongside the inventory leaf rather than the inventory being the sole
# primary: protection procedure (existing leaf, refined to procedural items
# only) + licensed-software & IPR inventory (the register, new) + acquired-
# works upstream + annual IPR audit. The procedure leaf id is preserved;
# three siblings new. Some items move from the procedure leaf into the new
# inventory leaf (licensed_inventory, renewal_tracking) where they more
# naturally belong.
# Authority: ISO 27002:2022 § 5.32 implementation guidance.

REQ_A532_PROTECTION_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.32:intellectual_property_procedure",
    control_ref   = "A.5.32",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Intellectual Property Rights Protection Procedure",
    trigger_type  = "universal",
    description   = "A.5.32 requires appropriate procedures to protect IPR — both the organisation's own and third parties'. The procedure documents usage controls, third-party respect mechanisms, employee-creation rules and the linkage to acquisition. The licensed/IPR inventory, the acquired-works upstream and the annual audit are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.32:scope_iprs",         "Scope of IPRs covered (software licences, trademarks, copyrights, patents, trade secrets, AI model weights / training data where applicable)", "must", False, "27002:5.32 — IPR scope"),
        ChecklistItem("item:A.5.32:usage_controls",     "Usage controls preventing unlicensed software installation (allow-listing, MDM/EDR enforcement, procurement gate)",                              "must", False, "27002:5.32 — appropriate procedures"),
        ChecklistItem("item:A.5.32:third_party_respect","Third-party IPR respect (citation, attribution, royalty payment, open-source licence compliance)",                                                "must", False, "27002:5.32 — protect IPR"),
        ChecklistItem("item:A.5.32:employee_creations", "Employee-creations rule (work-product ownership, open-source contribution policy, prior-IP carve-out)",                                            "must", False, "27002:5.32 — protect"),
        ChecklistItem("item:A.5.32:incident_handling",  "Handling path for suspected IPR infringement (internal report, takedown, internal remediation, cease-and-desist response)",                       "must", False, "27002:5.32 — protect"),
        ChecklistItem("item:A.5.32:owner",              "Named owner of the procedure (typically legal/IT lead jointly)",                                                                                  "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.32:training_link",      "Cross-link to A.6.3 awareness — staff training on IPR (especially open-source and AI-tool usage)",                                                "should", False, "Effectiveness"),
        ChecklistItem("item:A.5.32:bring_your_own",     "Bring-your-own-licence handling (personal licences brought into a business context, freelancer-supplied software)",                              "should", False, "Real-world coverage"),
    ],
)

REQ_A532_LICENSED_INVENTORY = EvidenceRequirement(
    id            = "req:A.5.32:licensed_software_ipr_inventory",
    control_ref   = "A.5.32",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Licensed Software and IPR Inventory",
    trigger_type  = "universal",
    description   = "The register at the heart of IPR protection. Without an inventory of what's licensed, what's open-source, what's internally created, A.5.32 enforcement is theoretical. The inventory tracks entitlements, expiry, attribution obligations and ownership for each entry",
    must_contain  = [
        ChecklistItem("item:A.5.32:licensed_inventory",  "Inventory of licensed commercial software with entitlements (seats / cores / sites) and expiry per licence",                                     "must", False, "27002:5.32 — protect"),
        ChecklistItem("item:A.5.32:opensource_inventory","Open-source components inventory with licence type per component (drives attribution and obligation handling — feeds SBOM)",                     "must", False, "27002:5.32 — third-party IPR"),
        ChecklistItem("item:A.5.32:owned_ipr",           "Organisation-owned IPR entries (trademarks, patents, trade secrets, copyrighted works) with status and protection scope",                       "must", False, "27002:5.32 — own IPR"),
        ChecklistItem("item:A.5.32:asset_link",          "Linkage to A.5.9 asset register — each licensed item is also an information asset; the two registers must not drift",                            "must", False, "A.5.9 coherence"),
        ChecklistItem("item:A.5.32:owner_per_entry",     "Named owner per entry (procurement / legal / engineering lead) responsible for renewal and compliance",                                          "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.32:renewal_tracking",    "Renewal dates tracked with lead-time alerts (so expiring licences are renewed before lapse)",                                                    "should", False, "Continuity of use"),
        ChecklistItem("item:A.5.32:sbom_link",           "Link to SBOM tooling output for open-source components (A.8.29 secure-development linkage)",                                                      "should", False, "Tool-driven currency"),
    ],
)

REQ_A532_ACQUIRED_WORKS_UPSTREAM = EvidenceRequirement(
    id            = "req:A.5.32:acquired_works_upstream",
    control_ref   = "A.5.32",
    standard_id   = "ISO27001:2022",
    evidence_type = "intake_process",
    title         = "Acquired Works Intake Upstream",
    trigger_type  = "universal",
    description   = "The upstream that feeds the inventory. Where the procedure covers ongoing protection and the inventory holds the current state, the intake upstream documents how new IPR enters the org — software procurement, open-source dependency adoption, third-party content licensing, M&A IPR transfer — and how each route results in an inventory entry",
    must_contain  = [
        ChecklistItem("item:A.5.32:intake_procurement", "Procurement intake — every commercial software purchase routes through licence review and inventory registration before deployment",            "must", False, "Operational sufficiency"),
        ChecklistItem("item:A.5.32:intake_opensource",  "Open-source adoption path — dependency additions pass a licence-compatibility gate; results recorded in the inventory",                          "must", False, "27002:5.32 — third-party"),
        ChecklistItem("item:A.5.32:intake_content",     "Third-party content licensing (images, fonts, datasets, AI training data) — intake confirms permitted use and records terms",                    "must", False, "27002:5.32 — protect IPR"),
        ChecklistItem("item:A.5.32:intake_ma",          "M&A or contractor-handover intake — IPR transferred in is inventoried and ownership re-confirmed",                                                "must", False, "27002:5.32 — completeness"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.32:intake_block_path",  "Block path for non-compliant intake (e.g., GPL component in a closed-source product) — rejection and alternatives sourcing process",            "should", False, "Drift prevention"),
        ChecklistItem("item:A.5.32:intake_a519_link",   "Cross-link to A.5.19 supplier risk — supplier-supplied IPR follows the supplier-onboarding flow",                                                 "should", False, "Cross-control coherence"),
    ],
)

REQ_A532_AUDIT_REVIEW = EvidenceRequirement(
    id              = "req:A.5.32:ipr_audit_review",
    control_ref     = "A.5.32",
    standard_id     = "ISO27001:2022",
    evidence_type   = "review_record",
    title           = "Periodic IPR and Licence Audit",
    trigger_type    = "universal",
    description     = "Periodic audit reconciling deployed software / used content against the inventory and licence entitlements. Catches drift the intake and procedure leaves miss — over-deployment of seat-limited licences, expired licences still in use, missing attribution, undeclared open-source components",
    freshness_days  = 365,
    must_contain    = [
        ChecklistItem("item:A.5.32:audit_cadence",      "Audit date within the planned interval (typically annual; more frequent if a vendor audit risk is high)",                                        "must", False, "Drift prevention"),
        ChecklistItem("item:A.5.32:audit_reviewer",     "Reviewer identity and role (procurement / legal / engineering)",                                                                                  "must", False, "Accountability"),
        ChecklistItem("item:A.5.32:audit_entitlement",  "Entitlement check — deployed seats/cores vs licence allowance per commercial entry, exceptions remediated",                                      "must", False, "27002:5.32 — protect"),
        ChecklistItem("item:A.5.32:audit_opensource",   "Open-source attribution and licence-obligation check (NOTICE files, source-availability where required)",                                          "must", False, "27002:5.32 — third-party IPR"),
        ChecklistItem("item:A.5.32:audit_expiry",       "Expired/expiring licences flagged and renewal or removal completed",                                                                              "must", False, "Continuity / drift"),
        ChecklistItem("item:A.5.32:audit_inventory_update","Inventory updated as a result of the audit with reference to this review",                                                                     "must", False, "Closes the loop"),
    ],
    should_contain  = [
        ChecklistItem("item:A.5.32:audit_dr_test",      "Disposal of unused licences considered (cost optimisation alongside compliance)",                                                                  "should", False, "Adjacent value"),
        ChecklistItem("item:A.5.32:audit_next_date",    "Next planned audit date stated",                                                                                                                    "should", False, "Planning"),
    ],
)

# ── Annex A.5.33 — Protection of records — records_program spine (4-leaf) ─────
# Promoted 2026-06-01 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. records_program spine — pairs naturally
# with the A.5.5/A.5.6/A.5.9/A.5.31/A.5.32 records-family from batch 1
# ([[curation-phase-b-batch-1-2026-05-29]]). Shape: procedure (the policy
# that classifies records, sets protection-by-class, and defines disposal) +
# register (the records schedule listing every record class with retention,
# driver, owner, protection class, last-verified) + scope (the upstream that
# determines what counts as a "record" — record categories, legal/regulatory
# drivers, business activities) + annual review (freshness=365 — records
# management methodology is stable, like A.5.5/A.5.6/A.5.31's annual cadence
# for stable-doctrine records-family controls; A.5.31 is the exception at
# 180d only because regulatory change cadence drives it).
#
# Item-id preservation: SPEC_ART_5_1_E (GDPR Art.5.1.e storage limitation
# derivation) references four A.5.33 items by id —
# item:A.5.33:records_schedule, :retention_periods, :retention_drivers,
# :disposal. All four MUST stay present after promotion; first three
# relocate to the register leaf (their natural home), :disposal stays in
# the procedure leaf (it's a procedure step, not a register row).
# Authority: ISO 27002:2022 § 5.33 implementation guidance — classification,
# protection requirements per class, retention with legal drivers, disposal,
# legal hold. Cross-link to A.5.34 (PII protection), A.5.12 (classification
# scheme), A.8.10 (information deletion).

REQ_A533_RECORDS_PROTECTION_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.33:records_protection_policy",
    control_ref   = "A.5.33",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Records Retention and Protection Policy",
    trigger_type  = "universal",
    description   = "A.5.33 requires records to be protected from loss, destruction, falsification, unauthorized access, and unauthorized release. The policy/procedure documents how records are classified, what protection is applied per class, how disposal is carried out at end of retention, and how legal-hold overrides operate. The records schedule (per-class register), records-categories scope (upstream that determines what counts as a 'record') and periodic review are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.33:protection_requirements","Protection requirements per record class (access control, encryption at rest, immutability where needed, integrity verification — protects against loss, destruction, falsification, unauthorized access and release)", "must", False, "27002:5.33 — protect from loss, destruction, falsification, unauthorized access and release"),
        ChecklistItem("item:A.5.33:classification_scheme", "Records classification scheme stated (record classes and the protection class assigned to each — cross-link to A.5.12 classification of information)", "must", False, "27002:5.33 — classification"),
        ChecklistItem("item:A.5.33:disposal",         "Disposal procedure at end of retention (secure destruction method per media type, certificate of destruction, witness for high-sensitivity classes — cross-link to A.8.10 information deletion)", "must", False, "27002:5.33 — secure disposal"),
        ChecklistItem("item:A.5.33:format_guidance",  "Format-specific protection guidance (paper vs digital vs hybrid records; storage media handled — cloud objects, immutable WORM stores, optical media, physical archives)", "must", False, "27002:5.33 — storage media"),
        ChecklistItem("item:A.5.33:legal_hold",       "Legal-hold provisions overriding normal retention (litigation hold, regulatory investigation hold, who can invoke, how it's released)", "must", False, "27002:5.33 — litigation readiness"),
        ChecklistItem("item:A.5.33:owner",            "Named owner of the procedure (typically records manager / legal counsel / InfoSec lead jointly)", "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.33:proc_pii_overlay",     "PII overlay — records containing PII inherit additional GDPR Art.5.1.e storage-limitation constraints (cross-link to A.5.34 + Art.5.1.e)", "should", False, "ISO × GDPR integration"),
        ChecklistItem("item:A.5.33:proc_asset_link",      "Cross-link to A.5.9 asset register — records are information assets; protection class must reconcile",                                       "should", False, "Cross-control coherence"),
        ChecklistItem("item:A.5.33:proc_change_log",      "Change-log requirement for policy edits (audit trail for retention-period or protection changes)",                                          "should", False, "Auditability"),
    ],
)

REQ_A533_RECORDS_SCHEDULE_REGISTER = EvidenceRequirement(
    id            = "req:A.5.33:records_schedule_register",
    control_ref   = "A.5.33",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Records Schedule (Per-Class Retention and Protection Register)",
    trigger_type  = "universal",
    description   = "The operational register at the heart of A.5.33. Without a records schedule listing every record class with retention, driver, owner and protection assignment, the policy is theoretical. The schedule is queried at audit time to demonstrate that the organisation knows what records it holds, why it holds them, and for how long",
    must_contain  = [
        ChecklistItem("item:A.5.33:records_schedule",  "Records inventory or schedule listing every record class the organisation holds (HR records, financial records, customer records, contract records, security/audit logs, processing-activity records, system records, training records, incident records, etc.)", "must", False, "27002:5.33 — records"),
        ChecklistItem("item:A.5.33:retention_periods", "Retention period per record class (concrete duration — years/months, with start-trigger and end-trigger defined)",                                                                                                                                                            "must", False, "27002:5.33 — retention"),
        ChecklistItem("item:A.5.33:retention_drivers", "Legal/regulatory driver per retention period stated (statute, regulator guidance, contractual obligation, business need — never an arbitrary number)",                                                                                                                       "must", False, "27002:5.33 — legal driver"),
        ChecklistItem("item:A.5.33:reg_protection_class","Protection class per record class (which classification + protection profile from the procedure applies) — drives the access-control / encryption / immutability decision",                                                                                              "must", False, "27002:5.33 — protection per class"),
        ChecklistItem("item:A.5.33:reg_owner_per_class","Owner per record class (named role responsible for the class — HR for personnel records, Finance for financial records, etc.)",                                                                                                                                            "must", False, "Accountability"),
        ChecklistItem("item:A.5.33:reg_last_verified", "Last-verified date per class (proves the entry is current; missing dates surface stale classes at review)",                                                                                                                                                                  "must", False, "27002:5.33 — kept current"),
        ChecklistItem("item:A.5.33:reg_storage_location","Storage location per class (system / repository / physical archive — needed at disposal and at legal-hold invocation)",                                                                                                                                                   "must", False, "27002:5.33 — storage media"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.33:reg_pii_flag",      "PII flag per class (drives GDPR Art.5.1.e storage-limitation overlay — cross-link to the procedure's PII overlay)",                                                                                                                                                          "should", False, "ISO × GDPR integration"),
        ChecklistItem("item:A.5.33:reg_legal_hold_flag","Active legal-hold flag per class (rows currently under hold are visible at-a-glance)",                                                                                                                                                                                       "should", False, "Litigation readiness"),
        ChecklistItem("item:A.5.33:reg_volume",         "Approximate volume per class (drives prioritisation when storage costs or e-discovery demand it)",                                                                                                                                                                          "should", False, "Operational realism"),
    ],
)

REQ_A533_RECORDS_CATEGORIES_SCOPE = EvidenceRequirement(
    id            = "req:A.5.33:records_categories_scope",
    control_ref   = "A.5.33",
    standard_id   = "ISO27001:2022",
    evidence_type = "scope_note",
    title         = "Records Categories Scope",
    trigger_type  = "universal",
    description   = "The upstream that drives the schedule. Documents the business activities, legal/regulatory drivers, and data categories that determine what counts as a 'record' for the organisation. ISO 27002:2022 § 5.33 expects organisations to know which records they need to keep before claiming to protect them. Drift between the scope and the schedule is the audit failure mode this leaf catches — it surfaces missing classes (e.g., 'we started processing health data; where are the HIPAA records?')",
    must_contain  = [
        ChecklistItem("item:A.5.33:scope_business_activities","Business activities considered (HR/employment, finance/tax, sales/customer, operations/security, regulated activities — each may generate distinct record classes)",                          "must", False, "27002:5.33 — applicability"),
        ChecklistItem("item:A.5.33:scope_legal_drivers",      "Legal/regulatory drivers enumerated (statutes mandating record-keeping: corporate law, tax law, employment law, sectoral regulations, GDPR Art.30, AML, etc.) — cross-link to A.5.31 register","must", False, "27002:5.33 — legal driver"),
        ChecklistItem("item:A.5.33:scope_data_categories",    "Personal/sensitive/regulated data categories handled (drives PII overlay and special-category retention)",                                                                                     "must", False, "GDPR/sectoral linkage"),
        ChecklistItem("item:A.5.33:scope_jurisdictions",      "Jurisdictions covered (each may impose different minimum-retention or right-to-erasure constraints — HQ, places of business, data-residency destinations)",                                    "must", False, "27002:5.33 — relevant"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.33:scope_obligations_link", "Cross-link to A.5.31 applicable-obligations scope — same drivers, separate registers; the two should stay aligned",                          "should", False, "Cross-control coherence"),
        ChecklistItem("item:A.5.33:scope_change_drivers",   "Trigger list for re-scoping (new geography, new service line, M&A, new regulated activity — adding scope must trigger a schedule update)",   "should", False, "Currency"),
    ],
)

REQ_A533_REVIEW = EvidenceRequirement(
    id              = "req:A.5.33:records_program_review",
    control_ref     = "A.5.33",
    standard_id     = "ISO27001:2022",
    evidence_type   = "review_record",
    title           = "Periodic Records Protection Program Review",
    trigger_type    = "universal",
    description     = "Periodic verification that the schedule reflects the scope, the procedure still matches the protection requirements per class, and disposal/legal-hold discipline is being followed. ISO 27002:2022 § 5.33 expects records protection to be maintained — drift between schedule and reality (new classes emerging, retention periods overrun, disposals not happening) is the audit failure mode this leaf catches. Annual cadence (freshness=365) matches the stable doctrine of records-management methodology",
    freshness_days  = 365,
    must_contain    = [
        ChecklistItem("item:A.5.33:rev_date",              "Review date within the planned interval (typically within 12 months of last review)",                                                                                                                            "must", False, "27002:5.33 — maintained"),
        ChecklistItem("item:A.5.33:rev_reviewer",          "Reviewer identity and role recorded (records manager / compliance lead with legal-counsel sign-off where material)",                                                                                              "must", False, "Accountability"),
        ChecklistItem("item:A.5.33:rev_schedule_check",    "Per-class outcome (verified / amended / retired / new added) with retention-still-adequate and protection-class-still-adequate confirmation",                                                                     "must", False, "27002:5.33 — kept current"),
        ChecklistItem("item:A.5.33:rev_scope_check",       "Cross-check against the records-categories scope — any new business activity / legal driver / data category that should add classes",                                                                              "must", False, "Cross-leaf coherence"),
        ChecklistItem("item:A.5.33:rev_disposal_audit",    "Disposal audit — sample of classes past retention end-date confirmed disposed (certificate of destruction present) or held under documented legal hold; overruns flagged for remediation",                        "must", False, "27002:5.33 — disposal discipline"),
        ChecklistItem("item:A.5.33:rev_legal_hold_status", "Active legal-hold status reviewed (which classes/rows currently held, by whom, on what basis, expected release trigger) — stale unreleased holds remediated",                                                      "must", False, "27002:5.33 — litigation readiness"),
        ChecklistItem("item:A.5.33:rev_register_update",   "Changes propagated back to the live schedule with reference to this review",                                                                                                                                       "must", False, "Closes the loop"),
    ],
    should_contain  = [
        ChecklistItem("item:A.5.33:rev_ad_hoc_triggers", "Ad-hoc review triggers listed (new regulator action, new sector entry, M&A, legal-hold invocation pattern shift)", "should", False, "Change-driven review"),
        ChecklistItem("item:A.5.33:rev_next_date",       "Next planned review date stated",                                                                                  "should", False, "Planning"),
    ],
)

# ── Annex A.5.34 — PII protection — records_program spine (4-leaf) ────────────
# Promoted 2026-06-01 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. records_program spine — natural pair
# with A.5.33 ([[curation-phase-b-batch-17-2026-06-01]]). A.5.33 protects the
# *records* (any record class — HR, finance, audit logs); A.5.34 protects
# the *PII subset* of those records with privacy-law overlays. Shape:
# policy/procedure (the privacy/PIMS policy with principles, controls, DSAR
# rights, breach handling) + register (the PII processing inventory — what
# PII categories, where, lawful basis per processing, retention, owner) +
# scope (the upstream — applicable privacy laws, jurisdictions, data subject
# categories, regulated activities) + annual review (freshness=365 — privacy
# program review is the doctrine cadence; matches A.5.33's records-family
# default and A.5.35/A.5.36's existing annual cadence).
#
# Item-id preservation: TWO DerivedSpecs reference A.5.34 items by id —
#   1. SPEC_ART_25 (Data protection by design/default) uses:
#      :applicable_laws, :pii_inventory, :retention_minimisation,
#      :security_controls_ref
#   2. SPEC_ART_24 (Responsibility of the controller) uses:
#      :applicable_laws, :lawful_basis, :data_subject_rights,
#      :security_controls_ref, :breach_handling
# Combined: ALL 7 MUST item ids from the prior single-leaf must stay present
# (overlap on :applicable_laws + :security_controls_ref). After promotion:
# six MUSTs stay on the policy leaf (applicable_laws, lawful_basis,
# data_subject_rights, retention_minimisation, security_controls_ref,
# breach_handling — the policy IS where these concepts live); :pii_inventory
# relocates to the register leaf (its natural home — it's the catalog of
# processing activities, not a policy clause).
# Authority: ISO 27002:2022 § 5.34 implementation guidance. Cross-link to
# GDPR Art.5/24/25/30/32/33/34, ISO/IEC 27701 PIMS, EDPB Guidelines.

REQ_A534_PRIVACY_PII_POLICY = EvidenceRequirement(
    id            = "req:A.5.34:privacy_and_pii_protection_policy",
    control_ref   = "A.5.34",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Privacy and PII Protection Policy",
    trigger_type  = "universal",
    description   = "A.5.34 requires identification of and compliance with privacy and PII protection requirements per applicable law, regulation, and contract. The policy (PIMS-aligned where ISO/IEC 27701 is in scope) names the applicable privacy laws, states the lawful basis discipline, enables data subject rights, sets retention/minimisation, links to the operational security controls applied to PII, and documents breach handling. The PII processing register, privacy applicability scope and periodic program review are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.34:applicable_laws",      "Applicable privacy laws identified (GDPR, UK GDPR, regional equivalents, sectoral privacy laws — HIPAA, LGPD, PIPEDA, CCPA, etc.) — each named, not just 'privacy laws'",                                                          "must", False, "27002:5.34 — applicable laws and regulations"),
        ChecklistItem("item:A.5.34:lawful_basis",         "Lawful basis discipline (lawful basis identified per processing activity — consent, contract, legal obligation, vital interests, public task, legitimate interests; where law requires)",                                          "must", False, "27002:5.34 — applicable laws / GDPR Art.6"),
        ChecklistItem("item:A.5.34:data_subject_rights",  "Data subject rights enabled (access, rectification, erasure, portability, restriction, objection where applicable; intake path + response SLAs documented — cross-link to GDPR Art.12-22 and DSAR procedure)",                   "must", False, "27002:5.34 — preservation of privacy"),
        ChecklistItem("item:A.5.34:retention_minimisation","Retention and data minimisation requirements (collect only what's necessary; retain only as long as needed; cross-link to A.5.33 records schedule and GDPR Art.5.1.c/e)",                                                        "must", False, "27002:5.34 — preservation of privacy / GDPR Art.5.1.c+e"),
        ChecklistItem("item:A.5.34:security_controls_ref","References security controls applied to PII (links to A.8.x technical controls — encryption A.8.24, access control A.5.15/A.8.3, logging A.8.15/A.8.16, pseudonymisation A.8.11; satisfies GDPR Art.32 integration with Art.5.1.f)","must", False, "27002:5.34 — protection of PII / GDPR Art.32"),
        ChecklistItem("item:A.5.34:breach_handling",      "Breach handling reference (cross-link to A.5.24/A.5.26 incident family + GDPR Art.33 supervisory-authority notification within 72h + GDPR Art.34 data-subject notification where high risk)",                                      "must", False, "27002:5.34 — applicable laws / GDPR Art.33-34"),
        ChecklistItem("item:A.5.34:transfer_restrictions","Cross-border transfer discipline (which transfers happen, on what legal basis — SCCs / adequacy / BCRs / derogations; cross-link to A.5.14 transfer policy + GDPR Art.44-49)",                                                    "must", False, "27002:5.34 — preservation of privacy / GDPR Chap V"),
        ChecklistItem("item:A.5.34:owner",                "Named owner of the privacy program (DPO where law requires; Privacy Officer or InfoSec lead where DPO is not mandatory; named individual, not a generic 'Privacy Team')",                                                        "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.34:dpia_process",      "PIA / DPIA process reference for high-risk processing (cross-link to GDPR Art.35 + EDPB Guidelines on DPIA — when to trigger, who reviews, supervisory-authority consultation path)",                                                "should", False, "Pre-emptive risk handling"),
        ChecklistItem("item:A.5.34:dpo_role",          "DPO designation note (mandatory under GDPR Art.37 for public authorities, large-scale special-category processing, large-scale systematic monitoring; voluntary otherwise — captured here regardless of mandate)",                  "should", False, "Accountability"),
        ChecklistItem("item:A.5.34:training_link",     "Cross-link to A.6.3 awareness — privacy/PII training for staff who process personal data (consent capture, DSAR handling, breach reporting)",                                                                                       "should", False, "Effectiveness"),
        ChecklistItem("item:A.5.34:pims_alignment",    "ISO/IEC 27701 (PIMS) alignment note where applicable — extends the ISMS into a Privacy Information Management System; references the 27701 PII-controller / PII-processor controls applied",                                          "should", False, "27701 integration where in scope"),
    ],
)

REQ_A534_PII_PROCESSING_REGISTER = EvidenceRequirement(
    id            = "req:A.5.34:pii_processing_register",
    control_ref   = "A.5.34",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "PII Processing Register",
    trigger_type  = "universal",
    description   = "The operational catalog of every processing activity involving PII — what categories, whose, on what legal basis, retained how long, owned by whom, protected how, transferred where. Often shared with (or extended from) the GDPR Art.30 Records of Processing (RoPA) — same operational artefact serves both ISO A.5.34 and GDPR Art.30. Without this register, the privacy policy is theoretical; with it, A.5.34 / Art.30 / Art.25 / Art.5 can all be evidenced from a single source",
    must_contain  = [
        ChecklistItem("item:A.5.34:pii_inventory",         "PII categories enumerated per processing activity (basic identifiers, contact data, financial, health, biometric, special-category — GDPR Art.9 / sectoral equivalents); links to GDPR Art.30 RoPA",                                  "must", False, "27002:5.34 — protection of PII / GDPR Art.30.1.c"),
        ChecklistItem("item:A.5.34:reg_data_subjects",     "Data subject categories per processing activity (customers, employees, prospects, minors, vulnerable groups — drives extra-safeguard decisions)",                                                                                    "must", False, "27002:5.34 — relevant / GDPR Art.30.1.c"),
        ChecklistItem("item:A.5.34:reg_purposes",          "Processing purposes stated per activity (specific, explicit, legitimate — not 'business operations'; cross-link to GDPR Art.5.1.b purpose limitation)",                                                                              "must", False, "GDPR Art.30.1.b + Art.5.1.b"),
        ChecklistItem("item:A.5.34:reg_lawful_basis",      "Lawful basis recorded per activity (matches the policy's discipline — consent / contract / legal obligation / vital interests / public task / legitimate interests, with special-category Art.9 basis where applicable)",            "must", False, "GDPR Art.6 + Art.9"),
        ChecklistItem("item:A.5.34:reg_retention",         "Retention period per activity (concrete duration with start/end triggers; cross-link to A.5.33 records schedule — no arbitrary numbers)",                                                                                            "must", False, "GDPR Art.30.1.f + A.5.33 coherence"),
        ChecklistItem("item:A.5.34:reg_owner_per_activity","Owner per processing activity (named role responsible for the activity — HR for employee processing, Sales for prospect processing, etc.)",                                                                                          "must", False, "Accountability"),
        ChecklistItem("item:A.5.34:reg_controls_applied", "Security controls applied per activity (encryption at rest/in transit, access control class, pseudonymisation where used — cross-link to A.8.x and GDPR Art.32)",                                                                    "must", False, "GDPR Art.30.1.g + Art.32"),
        ChecklistItem("item:A.5.34:reg_transfers",        "Cross-border transfers per activity (destination jurisdictions + legal mechanism — SCCs / adequacy / BCRs / derogations; explicit 'none' where applicable)",                                                                          "must", False, "GDPR Art.30.1.e + Chap V"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.34:reg_ropa_link",          "Direct link to GDPR Art.30 RoPA register where the two are kept as one artefact — saves duplication, prevents drift",                                                                                                                "should", False, "Cross-control coherence"),
        ChecklistItem("item:A.5.34:reg_dpia_status",        "DPIA status per activity (required / completed / not required with rationale) — drives high-risk processing reviews",                                                                                                                "should", False, "GDPR Art.35"),
        ChecklistItem("item:A.5.34:reg_last_verified",      "Last-verified date per activity (proves the entry is current; missing dates surface stale activities at review)",                                                                                                                     "should", False, "27002:5.34 — maintained"),
    ],
)

REQ_A534_PRIVACY_APPLICABILITY_SCOPE = EvidenceRequirement(
    id            = "req:A.5.34:privacy_applicability_scope",
    control_ref   = "A.5.34",
    standard_id   = "ISO27001:2022",
    evidence_type = "scope_note",
    title         = "Privacy Applicability Scope",
    trigger_type  = "universal",
    description   = "The upstream that drives the policy and the register. Documents the privacy laws applicable to the organisation, the jurisdictions where data subjects live and where processing happens, the data subject categories the org touches, and the regulated activities that pull in sectoral privacy regimes. ISO 27002:2022 § 5.34 expects organisations to know which privacy regimes apply before claiming compliance — drift between scope and register is the audit failure mode this leaf catches",
    must_contain  = [
        ChecklistItem("item:A.5.34:scope_privacy_laws",      "Applicable privacy laws enumerated per jurisdiction (GDPR for EU/EEA, UK GDPR for UK, CCPA for California residents, LGPD for Brazil, PIPEDA for Canada, sectoral laws — HIPAA, GLBA, FERPA where relevant)",                       "must", False, "27002:5.34 — applicable laws + relevance"),
        ChecklistItem("item:A.5.34:scope_jurisdictions",     "Jurisdictions covered (HQ + places of business + data subject residency + processing locations + transfer destinations — each may impose distinct privacy obligations)",                                                            "must", False, "27002:5.34 — relevance"),
        ChecklistItem("item:A.5.34:scope_data_subjects",     "Data subject categories the organisation touches (customers, employees, prospects, suppliers' staff, minors, healthcare patients, financial-services clients — drives extra-safeguard rules)",                                       "must", False, "27002:5.34 — protection of PII"),
        ChecklistItem("item:A.5.34:scope_regulated_activities","Regulated activities pulling in sectoral privacy regimes (healthcare → HIPAA, financial → GLBA/PSD2/DORA-privacy overlap, telco → ePrivacy, public sector → FERPA/government-records laws, advertising/profiling → ePrivacy)",      "must", False, "27002:5.34 — applicable laws"),
        ChecklistItem("item:A.5.34:scope_controller_role",   "Controller vs Processor vs Joint Controller status per processing context (drives different obligation sets — Art.24-31 for controllers, Art.28 for processors, Art.26 for joint controllers)",                                       "must", False, "GDPR Art.24-28"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.34:scope_obligations_link",  "Cross-link to A.5.31 applicable-obligations scope — privacy laws are a subset; the two should share drivers and stay aligned",                                                                                                       "should", False, "Cross-control coherence"),
        ChecklistItem("item:A.5.34:scope_change_drivers",    "Trigger list for re-scoping (new geography, new service line entering a regulated sector, M&A bringing new data subject categories, new transfer destinations)",                                                                     "should", False, "Currency"),
    ],
)

REQ_A534_PROGRAM_REVIEW = EvidenceRequirement(
    id              = "req:A.5.34:privacy_program_review",
    control_ref     = "A.5.34",
    standard_id     = "ISO27001:2022",
    evidence_type   = "review_record",
    title           = "Periodic Privacy and PII Protection Program Review",
    trigger_type    = "universal",
    description     = "Periodic verification that the policy still matches applicable law, the register reflects current processing reality, DSARs are being responded to within SLA, breaches were handled per Art.33/34, transfers still have valid legal mechanisms, and DPIAs are completed where required. ISO 27002:2022 § 5.34 + GDPR's accountability principle (Art.5.2 + Art.24) expect the privacy program to be MAINTAINED — drift between policy and reality is the audit failure mode this leaf catches. Annual cadence (freshness=365) matches A.5.35 independent review + A.5.36 compliance review + A.5.33 records-family default",
    freshness_days  = 365,
    must_contain    = [
        ChecklistItem("item:A.5.34:rev_date",               "Review date within the planned interval (typically within 12 months of last review)",                                                                                                                                                "must", False, "27002:5.34 — maintained / GDPR Art.5.2"),
        ChecklistItem("item:A.5.34:rev_reviewer",           "Reviewer identity and role recorded (DPO or Privacy Officer + InfoSec lead jointly; legal-counsel sign-off where law has shifted materially)",                                                                                       "must", False, "Accountability"),
        ChecklistItem("item:A.5.34:rev_register_check",     "Per-activity outcome (verified / amended / retired / new added) with lawful-basis-still-valid and retention-still-adequate confirmation",                                                                                            "must", False, "27002:5.34 — kept current"),
        ChecklistItem("item:A.5.34:rev_scope_check",        "Cross-check against the privacy applicability scope — any new jurisdiction, regulated activity, data subject category that should add register entries",                                                                              "must", False, "Cross-leaf coherence"),
        ChecklistItem("item:A.5.34:rev_dsar_metrics",       "DSAR metrics review (volumes, response times against SLA, refusal/extension rates, complaints to supervisory authority) — operational privacy health",                                                                                 "must", False, "GDPR Art.12.3 + Art.15-22 compliance"),
        ChecklistItem("item:A.5.34:rev_breach_history",     "Breach history for the period (every personal-data breach in scope confirmed handled per Art.33 72h notification + Art.34 data-subject notification where required; lessons fed into A.5.27)",                                       "must", False, "GDPR Art.33-34"),
        ChecklistItem("item:A.5.34:rev_transfer_validity",  "Transfer-mechanism validity check (SCCs current edition, adequacy decisions still standing — e.g. Schrems shifts, BCRs unchanged) — flag stale mechanisms for remediation",                                                            "must", False, "GDPR Chap V"),
        ChecklistItem("item:A.5.34:rev_dpia_review",        "DPIA completion status reviewed (any high-risk processing without a completed DPIA flagged; DPIAs older than 24 months refreshed where processing material to lifecycle changed)",                                                    "must", False, "GDPR Art.35"),
        ChecklistItem("item:A.5.34:rev_register_update",    "Changes propagated back to the live register with reference to this review",                                                                                                                                                          "must", False, "Closes the loop"),
    ],
    should_contain  = [
        ChecklistItem("item:A.5.34:rev_ad_hoc_triggers", "Ad-hoc review triggers listed (Schrems-style adequacy shift, new regulator enforcement action in scope sector, M&A, large-scale breach in industry)",                                                                                  "should", False, "Change-driven review"),
        ChecklistItem("item:A.5.34:rev_next_date",       "Next planned review date stated",                                                                                                                                                                                                       "should", False, "Planning"),
    ],
)

# ── Annex A.5.35 — Independent review of InfoSec — records_program spine
#                   review-record-as-primary (4-leaf) ─────────────────────────
# Promoted 2026-06-01 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. records_program spine adapted as
# review-record-as-primary variant — same shape as A.5.22 supplier review
# ([[curation-phase-b-batch-3-2026-05-31]]). Shape: review_record (the
# independent review report) + schedule_register (the calendar of planned
# reviews) + program_meta_review (annual self-check of the review program)
# + finding_response_register (per-finding lifecycle from raised → response
# → closed). Per-report freshness=365 preserved on the primary leaf.
# Authority: ISO 27002:2022 § 5.35 — reviewed independently at planned
# intervals or on significant change; covers people, processes, technology.

REQ_A535_INDEPENDENT_REVIEW_REPORT = EvidenceRequirement(
    id             = "req:A.5.35:independent_review_report",
    control_ref    = "A.5.35",
    standard_id    = "ISO27001:2022",
    evidence_type  = "audit_report",
    title          = "Independent Information Security Review Report",
    trigger_type   = "universal",
    description    = "A.5.35 requires the organisation's approach to information security to be reviewed independently at planned intervals (or on significant change). Each review report evidences the activity for one review cycle: reviewer independence demonstrated, scope covering people/processes/technology, findings recorded with severity, recommendations stated, management response documented. The review schedule register, program meta-review and finding-response register are sibling leaves",
    freshness_days = 365,
    must_contain   = [
        ChecklistItem("item:A.5.35:independence",          "Independence of the reviewer demonstrated (separate function, external auditor, or rotating internal reviewer with no operational ownership of the reviewed areas)",                              "must", False, "27002:5.35 — reviewed independently"),
        ChecklistItem("item:A.5.35:scope",                 "Scope covers people, processes, and technologies (not just one dimension — auditor-defensible reviews must touch all three)",                                                                  "must", False, "27002:5.35 — including people, processes and technologies"),
        ChecklistItem("item:A.5.35:review_date",           "Review date and period covered (start/end of the review activity + observation window)",                                                                                                          "must", False, "27002:5.35 — planned intervals"),
        ChecklistItem("item:A.5.35:findings",              "Findings listed with severity (concrete, evidenced, traceable to the underlying observation — not just generic recommendations)",                                                                "must", False, "27002:5.35 — review"),
        ChecklistItem("item:A.5.35:recommendations",       "Recommendations stated (with priority and owner suggestion — actionable, not abstract)",                                                                                                          "must", False, "27002:5.35 — review"),
        ChecklistItem("item:A.5.35:management_response",   "Management response to findings (accept / remediate / transfer / risk-accept with rationale); response is documented IN the report, not deferred",                                                "must", False, "Closes the loop"),
        ChecklistItem("item:A.5.35:significant_change_check","Significant-change trigger check stated (whether this review was triggered by planned cadence OR by a significant change — M&A, major architectural shift, regulatory upheaval, major breach)","must", False, "27002:5.35 — planned intervals or on significant change"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.35:reviewer_credentials",  "External auditor accreditation or internal reviewer qualifications stated (CISA, ISO 27001 LA/LI, sector-specific credentials)",                                                                "should", False, "Reviewer credibility"),
        ChecklistItem("item:A.5.35:prior_review_compare",  "Comparison or movement from prior review's findings (open / closed / aged) — proves the program returns value across cycles",                                                                    "should", False, "Progress tracking"),
        ChecklistItem("item:A.5.35:executive_summary",     "Executive summary section addressed to leadership (audit-defensible communication of overall posture, not just the detailed findings list)",                                                     "should", False, "Stakeholder communication"),
    ],
)

REQ_A535_REVIEW_SCHEDULE_REGISTER = EvidenceRequirement(
    id            = "req:A.5.35:review_schedule_register",
    control_ref   = "A.5.35",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Independent Review Schedule Register",
    trigger_type  = "universal",
    description   = "A.5.35 expects reviews at planned intervals — without a schedule, 'planned' becomes 'when leadership asks for it'. The schedule register is the calendar of upcoming independent reviews: which scope areas, what cadence, which reviewer or selection mechanism, last review date, next review date",
    must_contain  = [
        ChecklistItem("item:A.5.35:sch_cadence",           "Planned cadence stated (annual is the doctrine baseline; risk-tier or scope-area may drive tighter cadences for hot domains)",                                       "must", False, "27002:5.35 — planned intervals"),
        ChecklistItem("item:A.5.35:sch_scope_areas",       "Scope areas planned (the ISMS may be reviewed end-to-end annually OR sliced across cycles — both acceptable; the slicing is documented)",                              "must", False, "27002:5.35 — including people, processes and technologies"),
        ChecklistItem("item:A.5.35:sch_reviewer_selection","Reviewer selection mechanism (external rotation, internal independence criteria, audit-firm framework agreement) — drives the independence guarantee",                 "must", False, "27002:5.35 — reviewed independently"),
        ChecklistItem("item:A.5.35:sch_last_review",       "Last review date recorded (proves the schedule is anchored in reality, not aspirational)",                                                                              "must", False, "Audit defensibility"),
        ChecklistItem("item:A.5.35:sch_next_review",       "Next review date stated (per scope area where sliced)",                                                                                                                "must", False, "Planning"),
        ChecklistItem("item:A.5.35:sch_owner",             "Named owner accountable for executing the schedule (typically CISO / InfoSec lead with management sponsor)",                                                            "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.35:sch_change_triggers",   "Ad-hoc change triggers documented (M&A, major architectural shift, regulatory upheaval, major breach) — fires reviews outside the planned cadence",                  "should", False, "27002:5.35 — on significant change"),
        ChecklistItem("item:A.5.35:sch_delta",             "Scheduled-vs-completed delta tracked (so missed reviews surface)",                                                                                                    "should", False, "Operational discipline"),
    ],
)

REQ_A535_PROGRAM_META_REVIEW = EvidenceRequirement(
    id             = "req:A.5.35:review_program_meta_review",
    control_ref    = "A.5.35",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic Independent Review Program Meta-Review",
    trigger_type   = "universal",
    description    = "The review program itself needs review — are we picking reviewers that stay genuinely independent, is the cadence right, are findings closing, do reviews surface real issues or have they become rubber-stamps? The meta-review evidences periodic self-assessment of the review program and resulting adjustments",
    freshness_days = 365,
    must_contain   = [
        ChecklistItem("item:A.5.35:pgm_date",              "Meta-review date within the planned interval",                                                                                                                       "must", False, "27002:5.35 — periodic"),
        ChecklistItem("item:A.5.35:pgm_reviewer",          "Reviewer identity (program owner + InfoSec lead jointly + audit committee chair where applicable)",                                                                  "must", False, "Accountability"),
        ChecklistItem("item:A.5.35:pgm_independence_check","Independence-discipline check — did the actual reviewers meet the criteria? rotation worked? any reviewer reviewing their own area?",                                "must", False, "27002:5.35 — reviewed independently"),
        ChecklistItem("item:A.5.35:pgm_coverage",          "Coverage check — did the schedule actually run? all planned scope areas reviewed?",                                                                                  "must", False, "27002:5.35 — planned intervals"),
        ChecklistItem("item:A.5.35:pgm_closure",           "Findings-closure rate across the program (open / aged / closed)",                                                                                                    "must", False, "Operational discipline"),
        ChecklistItem("item:A.5.35:pgm_outcome",           "Cadence-adjustment or scope-adjustment decisions (tighten / loosen / re-tier / change reviewer pool)",                                                                "must", False, "27002:5.35 — adjustments"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.35:pgm_benchmark",         "External benchmarking or industry-practice input considered",                                                                                                        "should", False, "Audit defensibility"),
        ChecklistItem("item:A.5.35:pgm_next_date",         "Next planned meta-review date stated",                                                                                                                                "should", False, "Planning"),
    ],
)

REQ_A535_FINDING_RESPONSE_REGISTER = EvidenceRequirement(
    id            = "req:A.5.35:finding_response_register",
    control_ref   = "A.5.35",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Independent Review Finding Response Register",
    trigger_type  = "universal",
    description   = "A.5.35 requires management response to findings — but the response promise is theoretical without a per-finding lifecycle tracker. The register catalogues every finding from every independent review: severity, owner, agreed treatment, target date, closure status. This is the audit-defensibility artefact: 'show me what you did with the findings from the 2024 review' has a one-table answer",
    must_contain  = [
        ChecklistItem("item:A.5.35:fr_finding_id",         "Per-finding unique identifier traceable back to the source review report",                                                                                          "must", False, "27002:5.35 — review"),
        ChecklistItem("item:A.5.35:fr_severity",           "Severity recorded per finding (matches the report's severity classification)",                                                                                        "must", False, "27002:5.35 — review"),
        ChecklistItem("item:A.5.35:fr_owner",              "Named owner per finding (named individual, not generic team) with target closure date",                                                                              "must", False, "Accountability"),
        ChecklistItem("item:A.5.35:fr_treatment",          "Agreed treatment per finding (accept / remediate / transfer with rationale; mirrors the management response committed in the report)",                                "must", False, "Closes the loop"),
        ChecklistItem("item:A.5.35:fr_status",             "Current status per finding (open / in-progress / closed / aged-overdue) with last-updated date",                                                                     "must", False, "Operational discipline"),
        ChecklistItem("item:A.5.35:fr_closure_evidence",   "Closure evidence reference per closed finding (link to the artefact that proves the finding was addressed — control change, policy update, training delivered)",      "must", False, "Audit defensibility"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.35:fr_aging_alerts",       "Aged-overdue alerting (notification when target date passes without closure)",                                                                                       "should", False, "Operational discipline"),
        ChecklistItem("item:A.5.35:fr_cross_review_link",  "Cross-link to A.5.36 compliance-review nonconformity register where the two are kept as one artefact (common in mature programs)",                                  "should", False, "Cross-control coherence"),
    ],
)


# ── Annex A.5.36 — Compliance review records — records_program spine
#                   review-record-as-primary (4-leaf) ─────────────────────────
# Promoted 2026-06-01 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. records_program spine adapted as
# review-record-as-primary variant — SAME SHAPE as A.5.35 ([[curation-phase-
# b-batch-19-2026-06-01]]) batch-mate. A.5.35 reviews the InfoSec FUNCTION
# (people/process/tech) independently; A.5.36 reviews COMPLIANCE WITH the
# org's policies/rules/standards (different scope, same operational shape).
# Pairing: the two reviews often share infrastructure (reviewer pool, finding
# register), encoded via the `fr_cross_review_link` SHOULD on both registers.
# Per-record freshness=365 preserved on the primary leaf.
# Authority: ISO 27002:2022 § 5.36 — InfoSec policy + topic-specific policies
# + rules + standards reviewed regularly.

REQ_A536_COMPLIANCE_REVIEW_RECORD = EvidenceRequirement(
    id             = "req:A.5.36:compliance_review_record",
    control_ref    = "A.5.36",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Compliance Review Records (Policies, Rules, Standards)",
    trigger_type   = "universal",
    description    = "A.5.36 requires regular review of compliance with the InfoSec policy, topic-specific policies, rules and standards. Each review record evidences the activity for one cycle: schedule honoured, scope covered, method used, findings recorded, corrective actions opened. The schedule register, program meta-review and nonconformity register are sibling leaves",
    freshness_days = 365,
    must_contain   = [
        ChecklistItem("item:A.5.36:schedule",              "Schedule honoured for this cycle (each planned policy/rule/standard actually reviewed in the period; gaps flagged for next cycle)",                                "must", False, "27002:5.36 — regularly reviewed"),
        ChecklistItem("item:A.5.36:scope",                 "Scope of this cycle (which policies / rules / standards were reviewed — typically a slice of the full catalogue if rotated across cycles)",                          "must", False, "27002:5.36 — InfoSec policy + topic-specific policies + rules + standards"),
        ChecklistItem("item:A.5.36:method",                "Method used per item (control sampling, formal audit, automated check, attestation, walkthrough); rationale for method choice given the item type",                  "must", False, "27002:5.36 — reviewed"),
        ChecklistItem("item:A.5.36:findings",              "Findings recorded per review with severity (compliance vs. nonconformity vs. opportunity-for-improvement; concrete, evidenced)",                                      "must", False, "27002:5.36 — review"),
        ChecklistItem("item:A.5.36:corrective_actions",    "Corrective actions opened per nonconformity finding (with owner, target date) — feeds the nonconformity register",                                                  "must", False, "Closes the loop"),
        ChecklistItem("item:A.5.36:owner",                 "Named owner of this review cycle (the person who ran it — typically compliance lead or designate)",                                                                  "must", False, "Accountability"),
        ChecklistItem("item:A.5.36:review_date",           "Review date and period covered (start/end of the review activity)",                                                                                                  "must", False, "27002:5.36 — regularly"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.36:continuous_compliance", "Continuous-compliance monitoring tooling output considered (where used — config drift, control health checks, CSPM signal)",                                          "should", False, "Scale and timeliness"),
        ChecklistItem("item:A.5.36:method_evidence",       "Method evidence retained (sample selection notes, attestation responses, audit working papers) for audit defensibility",                                                "should", False, "Audit defensibility"),
    ],
)

REQ_A536_REVIEW_SCHEDULE = EvidenceRequirement(
    id            = "req:A.5.36:compliance_review_schedule",
    control_ref   = "A.5.36",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Compliance Review Schedule",
    trigger_type  = "universal",
    description   = "A.5.36 expects regular review — without a schedule, 'regular' becomes 'when something goes wrong'. The schedule register is the calendar: every in-scope policy/rule/standard, the planned cadence per item (proportional to risk and change rate), the last review date and the next review date",
    must_contain  = [
        ChecklistItem("item:A.5.36:sch_full_catalogue",    "Full catalogue of in-scope items enumerated (InfoSec policy + every topic-specific policy + rules + applicable standards — completeness is the integrity check)",   "must", False, "27002:5.36 — InfoSec policy + topic-specific policies + rules + standards"),
        ChecklistItem("item:A.5.36:sch_cadence",           "Cadence per item (annual baseline; tighter for high-risk or fast-changing items — e.g. acceptable use, access control)",                                            "must", False, "27002:5.36 — regularly"),
        ChecklistItem("item:A.5.36:sch_method_planned",    "Planned method per item (which items use sampling vs audit vs automated check)",                                                                                    "must", False, "27002:5.36 — reviewed"),
        ChecklistItem("item:A.5.36:sch_last_review",       "Last review date per item",                                                                                                                                          "must", False, "Audit defensibility"),
        ChecklistItem("item:A.5.36:sch_next_review",       "Next review date per item",                                                                                                                                          "must", False, "Planning"),
        ChecklistItem("item:A.5.36:sch_owner",             "Named owner per item (reviewer accountable for the next cycle)",                                                                                                      "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.36:sch_change_triggers",   "Ad-hoc change triggers documented (policy edit, regulator action, incident affecting a policy area) — fires reviews outside the planned cadence",                  "should", False, "Change-driven review"),
        ChecklistItem("item:A.5.36:sch_delta",             "Scheduled-vs-completed delta tracked (so missed reviews surface)",                                                                                                  "should", False, "Operational discipline"),
    ],
)

REQ_A536_PROGRAM_META_REVIEW = EvidenceRequirement(
    id             = "req:A.5.36:compliance_program_meta_review",
    control_ref    = "A.5.36",
    standard_id    = "ISO27001:2022",
    evidence_type  = "review_record",
    title          = "Periodic Compliance Review Program Meta-Review",
    trigger_type   = "universal",
    description    = "The compliance review program itself needs review — is the catalogue current, is the method choice right, are findings being closed, are continuous-compliance signals being used effectively? The meta-review evidences periodic self-assessment and the resulting adjustments",
    freshness_days = 365,
    must_contain   = [
        ChecklistItem("item:A.5.36:pgm_date",              "Meta-review date within the planned interval",                                                                                                                       "must", False, "27002:5.36 — periodic"),
        ChecklistItem("item:A.5.36:pgm_reviewer",          "Reviewer identity (compliance program owner + InfoSec lead jointly)",                                                                                               "must", False, "Accountability"),
        ChecklistItem("item:A.5.36:pgm_catalogue_check",   "Catalogue currency check — did new policies / rules / standards land without entering the schedule? are retired items still scheduled?",                            "must", False, "27002:5.36 — InfoSec policy + topic-specific policies + rules + standards"),
        ChecklistItem("item:A.5.36:pgm_coverage",          "Coverage check — did the schedule actually run? what fraction of catalogue reviewed in period?",                                                                    "must", False, "27002:5.36 — regularly"),
        ChecklistItem("item:A.5.36:pgm_closure",           "Findings-closure rate across the program (open / aged / closed)",                                                                                                    "must", False, "Operational discipline"),
        ChecklistItem("item:A.5.36:pgm_method_review",     "Method effectiveness review — are the chosen methods surfacing real nonconformities, or is the program rubber-stamping?",                                            "must", False, "27002:5.36 — adjustments"),
        ChecklistItem("item:A.5.36:pgm_outcome",           "Cadence-adjustment or method-adjustment decisions (tighten / loosen / change method per item type)",                                                                  "must", False, "27002:5.36 — adjustments"),
    ],
    should_contain = [
        ChecklistItem("item:A.5.36:pgm_a535_alignment",    "Alignment check with A.5.35 independent review program (shared reviewer pool? shared finding register? leverage opportunities)",                                  "should", False, "Cross-control coherence"),
        ChecklistItem("item:A.5.36:pgm_next_date",         "Next planned meta-review date stated",                                                                                                                              "should", False, "Planning"),
    ],
)

REQ_A536_NONCONFORMITY_REGISTER = EvidenceRequirement(
    id            = "req:A.5.36:nonconformity_register",
    control_ref   = "A.5.36",
    standard_id   = "ISO27001:2022",
    evidence_type = "revocation_record",
    title         = "Compliance Nonconformity Register",
    trigger_type  = "universal",
    description   = "A.5.36 requires corrective actions tracked to closure — but the corrective-action promise is theoretical without a per-NC lifecycle tracker. The nonconformity register catalogues every NC raised: severity, owner, agreed corrective action, target date, closure status, root cause. This is the audit-defensibility artefact paired with the review records",
    must_contain  = [
        ChecklistItem("item:A.5.36:nc_id",                 "Per-NC unique identifier traceable back to the source review record",                                                                                              "must", False, "27002:5.36 — review"),
        ChecklistItem("item:A.5.36:nc_severity",           "Severity recorded per NC (matches the review record's severity classification)",                                                                                    "must", False, "27002:5.36 — review"),
        ChecklistItem("item:A.5.36:nc_owner",              "Named owner per NC (named individual, not generic team) with target closure date",                                                                                  "must", False, "Accountability"),
        ChecklistItem("item:A.5.36:nc_corrective_action",  "Corrective action stated per NC (the specific change committed — policy update, control implementation, training delivery)",                                        "must", False, "Closes the loop"),
        ChecklistItem("item:A.5.36:nc_status",             "Current status per NC (open / in-progress / closed / aged-overdue / risk-accepted-with-exception) with last-updated date",                                          "must", False, "Operational discipline"),
        ChecklistItem("item:A.5.36:nc_closure_evidence",   "Closure evidence reference per closed NC (link to the artefact that proves the NC was addressed)",                                                                  "must", False, "Audit defensibility"),
        ChecklistItem("item:A.5.36:nc_root_cause",         "Root cause noted per NC where determined (drives systemic improvements vs point fixes)",                                                                            "must", False, "Continual improvement"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.36:nc_exception_register", "Exception register integration — risk-accepted NCs with expiry date (so 'we accept this' doesn't drift into 'we forgot this')",                                    "should", False, "Realistic operations"),
        ChecklistItem("item:A.5.36:nc_aging_alerts",       "Aged-overdue alerting (notification when target date passes without closure)",                                                                                       "should", False, "Operational discipline"),
        ChecklistItem("item:A.5.36:nc_cross_review_link",  "Cross-link to A.5.35 independent-review finding register where the two are kept as one artefact",                                                                    "should", False, "Cross-control coherence"),
    ],
)


# ── Annex A.5.37 — Documented operating procedures — records_program spine
#                   register-as-primary (4-leaf) ──────────────────────────────
# Promoted 2026-06-01 from single-leaf to multi-leaf per
# [[curation-program-full-multi-leaf]]. records_program spine — same shape as
# A.5.9 asset_register ([[curation-phase-b-batch-1-2026-05-29]]). Shape:
# register (the procedures catalogue) + maintenance_procedure (how procedures
# are created/reviewed/updated) + scope (which facilities/systems need a
# procedure) + program_review (annual review of the catalogue). Register leaf
# id is preserved.
# Authority: ISO 27002:2022 § 5.37 — operating procedures documented and
# made available to personnel who need them. Closes the A.5.3x block —
# A.5.37 is the final A.5 organisational control.

REQ_A537_OPERATING_PROCEDURES_REGISTER = EvidenceRequirement(
    id            = "req:A.5.37:operating_procedures_register",
    control_ref   = "A.5.37",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Documented Operating Procedures Register",
    trigger_type  = "universal",
    description   = "A.5.37 requires operating procedures for information processing facilities to be documented and made available to personnel who need them. The register is the live catalogue: every procedure listed with the facility/system it covers, the owner, version, last-updated and review-due dates, and the availability mechanism. Maintenance procedure, applicable-facilities scope and periodic review are sibling leaves",
    must_contain  = [
        ChecklistItem("item:A.5.37:procedure_inventory",   "Inventory of operating procedures (which facilities/systems they cover — backup, restore, patching, on-call response, change deployment, monitoring response, capacity, log-handling, etc.)",     "must", False, "27002:5.37 — documented"),
        ChecklistItem("item:A.5.37:scope_coverage",        "Scope coverage stated (every information processing facility represented — gaps surface where a facility exists without a documented procedure)",                                                "must", False, "27002:5.37 — information processing facilities"),
        ChecklistItem("item:A.5.37:availability",          "Availability mechanism stated per procedure (where personnel find them — intranet location, runbook system, wiki path with permissions, code-of-conduct package)",                              "must", False, "27002:5.37 — made available to personnel"),
        ChecklistItem("item:A.5.37:owner_per_procedure",   "Ownership per procedure (named role or individual responsible for currency — the operator who runs the procedure, not 'IT')",                                                                      "must", False, "27002:5.37 — documented"),
        ChecklistItem("item:A.5.37:version_control",       "Version control per procedure with last-updated date and review-due date (drives the review leaf)",                                                                                                "must", False, "27002:5.37 — documented"),
        ChecklistItem("item:A.5.37:audience_per_procedure","Intended audience per procedure (which personnel 'need' the procedure — drives access permissions and training links)",                                                                            "must", False, "27002:5.37 — personnel who need them"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.37:template_adherence",    "Template adherence flag per procedure (consistent shape across the catalogue — purpose / scope / prerequisites / steps / verification / rollback)",                                                "should", False, "Reviewability"),
        ChecklistItem("item:A.5.37:emergency_flag",        "Emergency-use flag per procedure (procedures needed under pressure — DR, incident response — get higher visibility and tighter currency)",                                                       "should", False, "Operational realism"),
        ChecklistItem("item:A.5.37:related_controls_link", "Cross-link to related controls per procedure (A.5.24/A.5.26 incident, A.5.29 disruption, A.5.30 ICT recovery, A.8.x technical controls)",                                                          "should", False, "Cross-control coherence"),
    ],
)

REQ_A537_MAINTENANCE_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.37:procedures_maintenance_procedure",
    control_ref   = "A.5.37",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Operating Procedures Maintenance Procedure",
    trigger_type  = "universal",
    description   = "A.5.37 expects procedures to be documented AND kept available — both require maintenance. The procedure documents who keeps the register and procedures current, what triggers an update (system change, control change, finding-driven update, exercise outcome), and the lifecycle from draft → review → publish → retire",
    must_contain  = [
        ChecklistItem("item:A.5.37:proc_maintainer",       "Named maintainer of the register (typically operations lead with InfoSec partner) accountable for catalogue currency",                                                                          "must", False, "Accountability"),
        ChecklistItem("item:A.5.37:proc_update_triggers",  "Update triggers enumerated (system change A.8.32 → procedure update, control change, finding from A.5.35/A.5.36 review, exercise outcome from A.5.24/A.5.29, operator-reported error)",            "must", False, "27002:5.37 — documented + current"),
        ChecklistItem("item:A.5.37:proc_review_path",      "Review path before publication (peer review by other operators, InfoSec sign-off for procedures touching security controls)",                                                                    "must", False, "Operational sufficiency"),
        ChecklistItem("item:A.5.37:proc_retire_path",      "Retirement path for obsolete procedures (system decommissioned, procedure superseded) — retired procedures are archived, not deleted",                                                            "must", False, "Auditability"),
        ChecklistItem("item:A.5.37:proc_template",         "Template definition stated (purpose / scope / prerequisites / steps / verification / rollback / contacts) — drives consistent shape",                                                              "must", False, "Reviewability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.37:proc_runbook_drill",    "Runbook-drill cadence — periodic exercise of selected procedures (especially emergency-use ones) so they're verified actionable under pressure",                                                  "should", False, "Effectiveness check"),
        ChecklistItem("item:A.5.37:proc_change_log",       "Change-log requirement for procedure edits (so the audit trail is preserved across versions)",                                                                                                    "should", False, "Auditability"),
    ],
)

REQ_A537_APPLICABLE_FACILITIES_SCOPE = EvidenceRequirement(
    id            = "req:A.5.37:applicable_facilities_scope",
    control_ref   = "A.5.37",
    standard_id   = "ISO27001:2022",
    evidence_type = "scope_note",
    title         = "Applicable Information Processing Facilities Scope",
    trigger_type  = "universal",
    description   = "The upstream that drives the register. Documents the information processing facilities the organisation operates — what counts as a 'facility' (production systems, staging where production data is touched, key SaaS environments, on-prem infrastructure). ISO 27002:2022 § 5.37 expects every facility to have a documented procedure — drift between scope and register is the audit failure mode this leaf catches",
    must_contain  = [
        ChecklistItem("item:A.5.37:scope_systems",         "Systems in scope enumerated (production applications, databases, key infrastructure components — drives 'which facilities need a procedure')",                                                  "must", False, "27002:5.37 — information processing facilities"),
        ChecklistItem("item:A.5.37:scope_saas",            "Key SaaS environments where the org operates the configuration (M365, Salesforce, ServiceNow, etc.) — even SaaS-hosted facilities need operating procedures for the org-side operator",          "must", False, "27002:5.37 — relevant"),
        ChecklistItem("item:A.5.37:scope_facility_classes","Facility classes / categories (compute, storage, network, security tooling, identity, observability) — drives template variations and operator personas",                                       "must", False, "27002:5.37 — facilities"),
        ChecklistItem("item:A.5.37:scope_asset_link",      "Cross-link to A.5.9 asset register — every information asset that is a facility should map to one or more procedures",                                                                            "must", False, "A.5.9 coherence"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.37:scope_change_drivers",  "Trigger list for re-scoping (new system entering production, SaaS adoption, M&A bringing new facilities, decommission)",                                                                          "should", False, "Currency"),
        ChecklistItem("item:A.5.37:scope_emergency_set",   "Emergency-use subset identified (which facilities need procedures available even when normal tooling is down — DR scenarios)",                                                                    "should", False, "Operational realism"),
    ],
)

REQ_A537_PROGRAM_REVIEW = EvidenceRequirement(
    id              = "req:A.5.37:procedures_program_review",
    control_ref     = "A.5.37",
    standard_id     = "ISO27001:2022",
    evidence_type   = "review_record",
    title           = "Periodic Operating Procedures Program Review",
    trigger_type    = "universal",
    description     = "Periodic verification that the register reflects the facility scope, procedures are still accurate (not just 'documented' but matching reality), availability mechanisms still work (operators can actually find them), and the maintenance procedure is being followed. Annual cadence (freshness=365) matches the records-family default — operational procedure methodology is stable, individual procedures get updated continuously via maintenance",
    freshness_days  = 365,
    must_contain    = [
        ChecklistItem("item:A.5.37:rev_date",              "Review date within the planned interval (typically within 12 months of last review)",                                                                                                              "must", False, "27002:5.37 — documented + current"),
        ChecklistItem("item:A.5.37:rev_reviewer",          "Reviewer identity and role recorded (operations lead + InfoSec lead jointly)",                                                                                                                    "must", False, "Accountability"),
        ChecklistItem("item:A.5.37:rev_register_check",    "Per-procedure outcome (verified / amended / retired / new added) with availability-mechanism-still-works confirmation",                                                                            "must", False, "27002:5.37 — documented + available"),
        ChecklistItem("item:A.5.37:rev_scope_check",       "Cross-check against the applicable-facilities scope — any new system / SaaS environment / facility class that should add procedures",                                                                "must", False, "Cross-leaf coherence"),
        ChecklistItem("item:A.5.37:rev_accuracy_sample",   "Accuracy sampling — operator walked through a sample procedure end-to-end? procedure matches current system reality (UI screenshots current, commands work, dependencies still valid)",            "must", False, "27002:5.37 — operations"),
        ChecklistItem("item:A.5.37:rev_emergency_review",  "Emergency-use procedure review — confirmed available and accurate for DR/incident scenarios (these are the procedures where stale = catastrophic)",                                                "must", False, "Operational realism"),
        ChecklistItem("item:A.5.37:rev_register_update",   "Changes propagated back to the live register with reference to this review",                                                                                                                       "must", False, "Closes the loop"),
    ],
    should_contain  = [
        ChecklistItem("item:A.5.37:rev_ad_hoc_triggers", "Ad-hoc review triggers listed (major incident exposing procedure gap, M&A, major system migration)",                                                                                                "should", False, "Change-driven review"),
        ChecklistItem("item:A.5.37:rev_next_date",       "Next planned review date stated",                                                                                                                                                                    "should", False, "Planning"),
    ],
)


# ── ISO 27001 Annex A.6 — People Controls (Phase B bulk curation, 2026-05-22)
# A.6.7 (Remote Working Policy) already exists as REQ_REMOTE_WORKING further
# up in the file. The 7 entries below cover the rest of Annex A.6.

REQ_A61_SCREENING = EvidenceRequirement(
    id            = "req:A.6.1:screening_procedure",
    control_ref   = "A.6.1",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Personnel Screening Procedure",
    trigger_type  = "universal",
    description   = "A.6.1 requires background verification checks on candidates and ongoing checks proportional to role risk. Evidence is a screening procedure covering scope, timing, proportionality, and legal considerations",
    must_contain  = [
        ChecklistItem("item:A.6.1:check_types",      "Types of checks defined (identity, employment history, education, criminal record where lawful, financial where role-relevant)", "must", False, "A.6.1 — background verification checks"),
        ChecklistItem("item:A.6.1:timing",           "Timing — pre-joining checks plus ongoing checks where applicable", "must", False, "A.6.1 — prior to joining the organization and on an ongoing basis"),
        ChecklistItem("item:A.6.1:proportionality", "Proportionality stated by role, information classification accessed, and perceived risk", "must", False, "A.6.1 — proportional to business requirements, classification of information, perceived risks"),
        ChecklistItem("item:A.6.1:legal_consideration","Legal, regulatory, and ethical constraints applied per jurisdiction", "must", False, "A.6.1 — applicable laws, regulations and ethics"),
        ChecklistItem("item:A.6.1:decision_authority","Decision authority named (who accepts or rejects screening outcomes)", "must", False, "Accountability"),
        ChecklistItem("item:A.6.1:retention",        "Retention rules for screening results (often short retention for negative results)", "must", False, "A.6.1 — applicable laws"),
    ],
    should_contain= [
        ChecklistItem("item:A.6.1:rescreen_triggers","Re-screening triggers (significant role change, escalated access)", "should", False, "Ongoing relevance"),
        ChecklistItem("item:A.6.1:third_party_use", "Third-party screening provider contracts and oversight", "should", False, "Common pattern"),
    ],
)

REQ_A62_EMPLOYMENT_TERMS = EvidenceRequirement(
    id            = "req:A.6.2:employment_terms_template",
    control_ref   = "A.6.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "agreement_template",
    title         = "Employment Contract Information Security Terms",
    trigger_type  = "universal",
    description   = "A.6.2 requires employment contractual agreements to state both personnel's and the organization's information security responsibilities. Evidence is the standard contract template (or annex) carrying these clauses",
    must_contain  = [
        ChecklistItem("item:A.6.2:personnel_responsibilities","Personnel's information security responsibilities stated", "must", False, "A.6.2 — personnel's responsibilities"),
        ChecklistItem("item:A.6.2:organization_responsibilities","Organization's information security responsibilities stated (training, tools, protection of personal data)", "must", False, "A.6.2 — organization's responsibilities"),
        ChecklistItem("item:A.6.2:policy_reference",         "Reference to InfoSec policy and topic-specific policies binding the personnel (A.5.1, A.5.10)", "must", False, "A.6.2 — for information security"),
        ChecklistItem("item:A.6.2:duration",                 "Duration of obligations stated (during employment and any surviving obligations — links to A.6.5)", "must", False, "Audit clarity"),
        ChecklistItem("item:A.6.2:signature",                "Signature requirement before employment commences", "must", False, "A.6.2 — contractual agreements"),
    ],
    should_contain= [
        ChecklistItem("item:A.6.2:aup_link",                 "Links to Acceptable Use Policy (A.5.10) by reference", "should", False, "Cross-control consistency"),
        ChecklistItem("item:A.6.2:disciplinary_link",        "Links to disciplinary process (A.6.4) by reference", "should", False, "Enforcement clarity"),
    ],
)

REQ_A63_SECURITY_AWARENESS = EvidenceRequirement(
    id            = "req:A.6.3:security_awareness_programme",
    control_ref   = "A.6.3",
    standard_id   = "ISO27001:2022",
    evidence_type = "training_programme",
    title         = "Information Security Awareness, Education and Training Programme",
    trigger_type  = "universal",
    description   = "A.6.3 requires personnel and relevant interested parties to receive appropriate awareness, education, and training, with regular updates as policies and procedures change. Evidence is a training programme description plus delivery records",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:A.6.3:scope_audience",     "Scope and audience defined (all personnel + relevant interested parties such as contractors)", "must", False, "A.6.3 — personnel of the organization and relevant interested parties"),
        ChecklistItem("item:A.6.3:curriculum",         "Curriculum aligned to job functions (general awareness for all, deeper modules per role)", "must", False, "A.6.3 — as relevant for their job function"),
        ChecklistItem("item:A.6.3:onboarding",         "Initial training on onboarding before access to information assets", "must", False, "A.6.3 — appropriate education and training"),
        ChecklistItem("item:A.6.3:refresh_cadence",    "Refresh cadence (typically annual) plus update on significant policy changes", "must", False, "A.6.3 — regular updates"),
        ChecklistItem("item:A.6.3:awareness_mechanisms","Awareness mechanisms beyond formal training (newsletters, phishing simulations, posters)", "must", False, "A.6.3 — awareness"),
        ChecklistItem("item:A.6.3:training_records",   "Training records (who completed what, when) for audit", "must", False, "Auditability"),
    ],
    should_contain= [
        ChecklistItem("item:A.6.3:role_specific_deep","Role-specific deep dives (developers, admins, finance, HR)", "should", False, "Proportionality"),
        ChecklistItem("item:A.6.3:effectiveness_metrics","Effectiveness measurement (quiz pass rates, phishing simulation click rates trend)", "should", False, "Continuous improvement"),
    ],
)

REQ_A64_DISCIPLINARY_PROCESS = EvidenceRequirement(
    id            = "req:A.6.4:disciplinary_process",
    control_ref   = "A.6.4",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Information Security Disciplinary Process",
    trigger_type  = "universal",
    description   = "A.6.4 requires a formalized, communicated disciplinary process for personnel and interested parties who violate information security policy. Evidence is a documented procedure (typically owned jointly with HR)",
    must_contain  = [
        ChecklistItem("item:A.6.4:formalised",         "Formalised in writing with HR / legal review", "must", False, "A.6.4 — formalized"),
        ChecklistItem("item:A.6.4:violation_scope",    "Scope of violations covered (policy breach, negligence, deliberate misuse)", "must", False, "A.6.4 — information security policy violation"),
        ChecklistItem("item:A.6.4:investigation_step","Investigation step before action, with right of explanation", "must", False, "Procedural fairness"),
        ChecklistItem("item:A.6.4:decision_authority","Decision authority named (HR + line management + legal as appropriate)", "must", False, "Accountability"),
        ChecklistItem("item:A.6.4:action_range",      "Range of actions defined (verbal warning, written warning, suspension, termination, legal referral)", "must", False, "A.6.4 — take actions"),
        ChecklistItem("item:A.6.4:communicated",      "Communicated to personnel and interested parties (in employment contract, code of conduct, intranet)", "must", False, "A.6.4 — communicated"),
    ],
    should_contain= [
        ChecklistItem("item:A.6.4:contributory_factors","Consideration of contributory factors (intent, recurrence, impact)", "should", False, "Proportionality"),
        ChecklistItem("item:A.6.4:appeals",            "Appeals or review process", "should", False, "Fair process"),
    ],
)

REQ_A65_POST_EMPLOYMENT = EvidenceRequirement(
    id            = "req:A.6.5:post_employment_responsibilities",
    control_ref   = "A.6.5",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Post-Employment / Role-Change Information Security Responsibilities",
    trigger_type  = "universal",
    description   = "A.6.5 requires surviving information security responsibilities after termination or change of employment to be defined, enforced, and communicated. Evidence is a procedure (often part of offboarding) covering what obligations persist and for how long",
    must_contain  = [
        ChecklistItem("item:A.6.5:surviving_duties", "Surviving duties enumerated (confidentiality, IP protection, non-disparagement, non-poach where lawful)", "must", False, "A.6.5 — duties that remain valid"),
        ChecklistItem("item:A.6.5:duration",         "Duration of each obligation (often indefinite for confidentiality, time-limited for others)", "must", False, "A.6.5 — remain valid after termination"),
        ChecklistItem("item:A.6.5:communication",    "Communication mechanism to leavers (exit briefing, reminder letter, signed acknowledgment)", "must", False, "A.6.5 — communicated"),
        ChecklistItem("item:A.6.5:enforcement",      "Enforcement approach (legal action, breach of contract, regulatory referral)", "must", False, "A.6.5 — enforced"),
        ChecklistItem("item:A.6.5:role_change_scope","Coverage of role change within the organization, not just termination", "must", False, "A.6.5 — termination or change of employment"),
    ],
    should_contain= [
        ChecklistItem("item:A.6.5:exit_interview_checklist","Exit interview / role-change checklist with info-security touchpoints", "should", False, "Operational handle"),
        ChecklistItem("item:A.6.5:contractor_parallel","Equivalent process for contractors and interested parties", "should", False, "Comprehensive coverage"),
    ],
)

REQ_A66_NDA = EvidenceRequirement(
    id            = "req:A.6.6:nda_template",
    control_ref   = "A.6.6",
    standard_id   = "ISO27001:2022",
    evidence_type = "agreement_template",
    title         = "Confidentiality / Non-Disclosure Agreement Template",
    trigger_type  = "universal",
    description   = "A.6.6 requires confidentiality or non-disclosure agreements appropriate to the organization's information protection needs, regularly reviewed, and signed by personnel and relevant interested parties. Evidence is the NDA template plus a signed-by tracking record",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:A.6.6:parties_covered",  "Parties covered (employees, contractors, suppliers, visitors with access to sensitive info)", "must", False, "A.6.6 — personnel and other relevant interested parties"),
        ChecklistItem("item:A.6.6:info_classes",     "Information classes protected (links to A.5.12 classification)", "must", False, "A.6.6 — protection of information"),
        ChecklistItem("item:A.6.6:duration",         "Duration of confidentiality obligation (typically post-termination indefinite for trade secrets)", "must", False, "A.6.6 — needs for protection"),
        ChecklistItem("item:A.6.6:return_destruction","Return or destruction obligation at end of relationship", "must", False, "A.6.6 — protection"),
        ChecklistItem("item:A.6.6:signature_requirement","Signature requirement enforced before access granted", "must", False, "A.6.6 — signed"),
        ChecklistItem("item:A.6.6:last_reviewed",    "Last-reviewed date on the template (review evidence)", "must", False, "A.6.6 — regularly reviewed"),
    ],
    should_contain= [
        ChecklistItem("item:A.6.6:jurisdiction_remedies","Jurisdiction and remedies clauses", "should", False, "Enforceability"),
        ChecklistItem("item:A.6.6:variant_tiers",    "Tiered NDA variants (employee, contractor, supplier, M&A counterparty)", "should", False, "Proportionality"),
    ],
)

REQ_A68_EVENT_REPORTING = EvidenceRequirement(
    id            = "req:A.6.8:event_reporting_procedure",
    control_ref   = "A.6.8",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Information Security Event Reporting Procedure",
    trigger_type  = "universal",
    description   = "A.6.8 requires the organization to provide a mechanism for personnel to report observed or suspected information security events through appropriate channels in a timely manner. Evidence is a documented reporting procedure",
    must_contain  = [
        ChecklistItem("item:A.6.8:channels",         "Multiple reporting channels offered (email, hotline, portal, manager, ticket system)", "must", False, "A.6.8 — appropriate channels"),
        ChecklistItem("item:A.6.8:audience",         "Procedure addresses all personnel (employees, contractors, third parties)", "must", False, "A.6.8 — mechanism for personnel"),
        ChecklistItem("item:A.6.8:what_to_report",   "What to report — observed events, suspected events, near-misses (no judgement required at reporting stage)", "must", False, "A.6.8 — observed or suspected"),
        ChecklistItem("item:A.6.8:timeliness",       "Timeliness expectation (e.g. as soon as practicable, within N hours of awareness)", "must", False, "A.6.8 — timely manner"),
        ChecklistItem("item:A.6.8:no_blame",         "No-blame / non-retaliation statement encourages honest reporting", "must", False, "Reporting culture"),
        ChecklistItem("item:A.6.8:handoff_to_triage","Handoff to triage process (A.5.25) on receipt", "must", False, "Closes the loop"),
    ],
    should_contain= [
        ChecklistItem("item:A.6.8:anonymity_option", "Anonymous reporting option for sensitive cases", "should", False, "Maximises reporting"),
        ChecklistItem("item:A.6.8:awareness_promotion","Periodic awareness reminders about the channel (links to A.6.3 training programme)", "should", False, "Channel discoverability"),
    ],
)


# ── ISO 27001 Annex A.7 — Physical Controls (Phase B bulk curation, 2026-05-22)
# All 14 A.7 controls were uncurated prior to this batch.

REQ_A71_PHYSICAL_PERIMETERS = EvidenceRequirement(
    id            = "req:A.7.1:physical_security_perimeters",
    control_ref   = "A.7.1",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Physical Security Perimeters Policy",
    trigger_type  = "universal",
    description   = "A.7.1 requires security perimeters to be defined and used to protect areas containing information and associated assets. Evidence is a policy (often part of a Physical Security Policy) defining perimeter types and the areas they protect",
    must_contain  = [
        ChecklistItem("item:A.7.1:perimeter_inventory","Inventory of perimeters defined (which physical boundaries exist)", "must", False, "A.7.1 — security perimeters defined"),
        ChecklistItem("item:A.7.1:area_classification","Classification of areas inside each perimeter (general office, secure area, server room, restricted)", "must", False, "A.7.1 — protect areas"),
        ChecklistItem("item:A.7.1:barrier_types",      "Barrier types per perimeter class (walls, fences, locked doors, mantraps)", "must", False, "A.7.1 — used to protect"),
        ChecklistItem("item:A.7.1:access_points",      "Access points designated per perimeter (which doors are entry/exit, which are emergency-only)", "must", False, "A.7.1 — defined"),
        ChecklistItem("item:A.7.1:owner",              "Owner named for physical security at each site", "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.7.1:drawings",           "Floor plans or perimeter drawings referenced", "should", False, "Audit clarity"),
        ChecklistItem("item:A.7.1:logical_integration","Integration with logical access decisions (which logical privileges require entry to which perimeter)", "should", False, "Cross-domain consistency"),
    ],
)

REQ_A72_PHYSICAL_ENTRY = EvidenceRequirement(
    id            = "req:A.7.2:physical_entry_procedure",
    control_ref   = "A.7.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Physical Entry Controls Procedure",
    trigger_type  = "universal",
    description   = "A.7.2 requires secure areas to be protected by appropriate entry controls and access points. Evidence is a procedure covering authorisation, entry mechanisms, visitor handling, and review",
    must_contain  = [
        ChecklistItem("item:A.7.2:authorisation_list","Authorisation list per secure area (who is permitted, by role or name)", "must", False, "A.7.2 — entry controls"),
        ChecklistItem("item:A.7.2:entry_mechanism", "Entry mechanism stated per area (badge, biometric, mechanical key)", "must", False, "A.7.2 — appropriate entry controls"),
        ChecklistItem("item:A.7.2:visitor_process", "Visitor handling (escort requirement, sign-in log, temporary badge, host accountability)", "must", False, "A.7.2 — access points"),
        ChecklistItem("item:A.7.2:deliveries",      "Delivery / loading area handling (drop zones, no direct access to secure areas)", "must", False, "A.7.2 — appropriate entry controls"),
        ChecklistItem("item:A.7.2:emergency_egress","Emergency egress provisions (panic bars, post-incident accountability)", "must", False, "Life safety"),
        ChecklistItem("item:A.7.2:periodic_review", "Periodic access list review (links to A.5.18)", "must", False, "Drift prevention"),
    ],
    should_contain= [
        ChecklistItem("item:A.7.2:tailgating",      "Anti-tailgating measures (mantraps, awareness, observed entry)", "should", False, "Common attack vector"),
        ChecklistItem("item:A.7.2:exception",       "Exception handling process for one-off access needs", "should", False, "Operational flexibility"),
    ],
)

REQ_A73_OFFICES_ROOMS = EvidenceRequirement(
    id            = "req:A.7.3:offices_rooms_facilities_procedure",
    control_ref   = "A.7.3",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Securing Offices, Rooms and Facilities Procedure",
    trigger_type  = "universal",
    description   = "A.7.3 requires physical security to be designed and implemented for offices, rooms, and facilities. Evidence is a procedure covering room classification, locking, signage, and key/card management",
    must_contain  = [
        ChecklistItem("item:A.7.3:room_classification","Classification of rooms (general, restricted, secure, high-security)", "must", False, "A.7.3 — designed and implemented"),
        ChecklistItem("item:A.7.3:locking_standards","Locking standards per classification (mechanical, electronic, audit logging)", "must", False, "A.7.3 — physical security"),
        ChecklistItem("item:A.7.3:signage",         "Signage and visibility minimisation (no advertising of sensitive areas)", "must", False, "A.7.3 — designed"),
        ChecklistItem("item:A.7.3:key_management",  "Key/card lifecycle management (issue, return, lost-card revocation)", "must", False, "A.7.3 — implemented"),
        ChecklistItem("item:A.7.3:occupancy_controls","Occupancy controls (max people in secure rooms, lone-worker rules)", "must", False, "A.7.3 — designed"),
    ],
    should_contain= [
        ChecklistItem("item:A.7.3:shared_building", "Considerations for shared buildings (other tenants, common corridors)", "should", False, "Common real-world setup"),
        ChecklistItem("item:A.7.3:fit_out",         "Fit-out / construction security requirements (walls to slab, no gaps above ceiling)", "should", False, "Often overlooked"),
    ],
)

REQ_A74_PHYSICAL_MONITORING = EvidenceRequirement(
    id            = "req:A.7.4:physical_security_monitoring",
    control_ref   = "A.7.4",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Physical Security Monitoring Procedure",
    trigger_type  = "universal",
    description   = "A.7.4 requires premises to be continuously monitored for unauthorized physical access. Evidence is a procedure covering monitoring scope, detection systems, response, and retention",
    must_contain  = [
        ChecklistItem("item:A.7.4:monitoring_scope","Monitoring scope stated (premises perimeter, secure areas, equipment rooms)", "must", False, "A.7.4 — premises monitored"),
        ChecklistItem("item:A.7.4:detection_systems","Detection systems listed (CCTV, intrusion detection, access control logs, alarms)", "must", False, "A.7.4 — monitored for unauthorized access"),
        ChecklistItem("item:A.7.4:continuous_24x7","24/7 / continuous monitoring approach (manned, automated, hybrid)", "must", False, "A.7.4 — continuously monitored"),
        ChecklistItem("item:A.7.4:alert_response","Alert response procedure (who is notified, escalation, on-site response)", "must", False, "A.7.4 — monitored"),
        ChecklistItem("item:A.7.4:retention",      "Retention of footage and access logs (period, secure storage)", "must", False, "A.7.4 — monitored"),
    ],
    should_contain= [
        ChecklistItem("item:A.7.4:siem_integration","Integration with SIEM / incident response (A.5.26)", "should", False, "Cross-control consistency"),
        ChecklistItem("item:A.7.4:privacy_balance","Privacy considerations for monitoring of personnel (data protection compliance)", "should", False, "Legal balance"),
    ],
)

REQ_A75_ENVIRONMENTAL_THREATS = EvidenceRequirement(
    id            = "req:A.7.5:environmental_threats_procedure",
    control_ref   = "A.7.5",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Protection Against Physical and Environmental Threats Procedure",
    trigger_type  = "universal",
    description   = "A.7.5 requires protection against physical and environmental threats (natural disasters, intentional acts, unintentional damage). Evidence is a procedure covering threat assessment, protection measures, detection, and response",
    must_contain  = [
        ChecklistItem("item:A.7.5:threat_assessment","Threat assessment per site (fire, flood, earthquake, civil unrest, power, vandalism)", "must", False, "A.7.5 — natural disasters, intentional or unintentional threats"),
        ChecklistItem("item:A.7.5:protection_per_threat","Protection measures stated per identified threat", "must", False, "A.7.5 — designed and implemented"),
        ChecklistItem("item:A.7.5:detection",     "Detection systems (smoke, heat, water leak, temperature, motion)", "must", False, "A.7.5 — protection"),
        ChecklistItem("item:A.7.5:response",      "Response procedures per threat type (evacuation, suppression, shutdown)", "must", False, "A.7.5 — implemented"),
        ChecklistItem("item:A.7.5:recovery",      "Recovery from environmental incidents (cleanup, salvage, post-incident assessment)", "must", False, "A.7.5 — protection"),
    ],
    should_contain= [
        ChecklistItem("item:A.7.5:location_risk", "Location-specific risk profile referenced (seismic zone, floodplain, climate)", "should", False, "Proportionality"),
        ChecklistItem("item:A.7.5:insurance",     "Insurance considerations and coverage referenced", "should", False, "Residual risk handling"),
    ],
)

REQ_A76_WORKING_IN_SECURE_AREAS = EvidenceRequirement(
    id            = "req:A.7.6:working_in_secure_areas_procedure",
    control_ref   = "A.7.6",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Working in Secure Areas Procedure",
    trigger_type  = "universal",
    description   = "A.7.6 requires security measures for working in secure areas to be designed and implemented. Evidence is a procedure stating the additional rules that apply inside secure areas",
    must_contain  = [
        ChecklistItem("item:A.7.6:secure_area_definition","Secure area definition (which areas are 'secure' per A.7.1 classification)", "must", False, "A.7.6 — secure areas"),
        ChecklistItem("item:A.7.6:device_restrictions","Restrictions on personal devices, recording, photography", "must", False, "A.7.6 — security measures"),
        ChecklistItem("item:A.7.6:escort_third_parties","Escort requirements when third parties present", "must", False, "A.7.6 — security measures"),
        ChecklistItem("item:A.7.6:clean_entry_exit","Clean entry/exit (search procedure if classification warrants, sign-out of materials)", "must", False, "A.7.6 — designed and implemented"),
    ],
    should_contain= [
        ChecklistItem("item:A.7.6:vacant_rules", "Vacant-area rules (lock-out, alarm activation)", "should", False, "Off-hours risk"),
        ChecklistItem("item:A.7.6:work_permits","Work-permit system for non-routine activities in secure areas", "should", False, "Operational control"),
    ],
)

REQ_A77_CLEAR_DESK_SCREEN = EvidenceRequirement(
    id            = "req:A.7.7:clear_desk_clear_screen_policy",
    control_ref   = "A.7.7",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Clear Desk and Clear Screen Policy",
    trigger_type  = "universal",
    description   = "A.7.7 requires clear-desk rules for papers and removable media plus clear-screen rules for information processing facilities. Evidence is a policy stating both rules and enforcement",
    must_contain  = [
        ChecklistItem("item:A.7.7:clear_desk_rule",  "Clear-desk rule for papers and removable media when desk unattended", "must", False, "A.7.7 — clear desk rules for papers and removable storage media"),
        ChecklistItem("item:A.7.7:clear_screen_rule","Clear-screen rule (screen lock on leaving, automatic lockout after N minutes)", "must", False, "A.7.7 — clear screen rules"),
        ChecklistItem("item:A.7.7:removable_media",  "Removable media handling rules (locked away when unattended)", "must", False, "A.7.7 — removable storage media"),
        ChecklistItem("item:A.7.7:locked_storage",   "Locked storage requirements per classification level (links to A.5.12)", "must", False, "A.7.7 — appropriately enforced"),
        ChecklistItem("item:A.7.7:enforcement",      "Enforcement approach (spot checks, awareness, sanctions)", "must", False, "A.7.7 — appropriately enforced"),
    ],
    should_contain= [
        ChecklistItem("item:A.7.7:meeting_rooms",    "Specific rules for meeting rooms and shared spaces", "should", False, "Common gap"),
        ChecklistItem("item:A.7.7:printer_rules",    "Printer / multifunction device rules (pull-print, collect immediately)", "should", False, "Often-leaked artefacts"),
    ],
)

REQ_A78_EQUIPMENT_SITING = EvidenceRequirement(
    id            = "req:A.7.8:equipment_siting_procedure",
    control_ref   = "A.7.8",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Equipment Siting and Protection Procedure",
    trigger_type  = "universal",
    description   = "A.7.8 requires equipment to be sited securely and protected. Evidence is a procedure stating siting principles per equipment class and protection measures",
    must_contain  = [
        ChecklistItem("item:A.7.8:siting_principles","Siting principles (away from public view if processing classified, restricted access, environmental controls)", "must", False, "A.7.8 — sited securely"),
        ChecklistItem("item:A.7.8:tamper_resistance","Tamper-resistance / detection measures for sensitive equipment", "must", False, "A.7.8 — protected"),
        ChecklistItem("item:A.7.8:cable_management","Cable management to prevent accidental damage or interception (links to A.7.12)", "must", False, "A.7.8 — protected"),
        ChecklistItem("item:A.7.8:visibility",      "Visibility minimisation (screens not facing windows, no labels indicating contents)", "must", False, "A.7.8 — sited securely"),
    ],
    should_contain= [
        ChecklistItem("item:A.7.8:hsm_specifics",   "Specific guidance for high-value equipment (HSMs, server racks, key safes)", "should", False, "Proportionality"),
        ChecklistItem("item:A.7.8:eating_drinking", "Rules on food/drink near equipment", "should", False, "Common cause of incidental damage"),
    ],
)

REQ_A79_OFF_PREMISES = EvidenceRequirement(
    id            = "req:A.7.9:off_premises_assets_policy",
    control_ref   = "A.7.9",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Security of Assets Off-Premises Policy",
    trigger_type  = "universal",
    description   = "A.7.9 requires off-site assets to be protected. Evidence is a policy covering scope, protection measures, theft/loss reporting, and registration",
    must_contain  = [
        ChecklistItem("item:A.7.9:scope",            "Scope (laptops, mobile devices, removable media, equipment taken off-premises)", "must", False, "A.7.9 — off-site assets"),
        ChecklistItem("item:A.7.9:encryption",       "Encryption requirements for off-premises information storage", "must", False, "A.7.9 — protected"),
        ChecklistItem("item:A.7.9:theft_loss_report","Theft/loss reporting requirement with timeline (links to A.6.8)", "must", False, "A.7.9 — protected"),
        ChecklistItem("item:A.7.9:travel_restrictions","Travel restrictions or extra precautions for high-risk jurisdictions", "must", False, "A.7.9 — protected"),
        ChecklistItem("item:A.7.9:registration",     "Registration / sign-out of equipment before removal from premises", "must", False, "A.7.9 — off-site assets"),
        ChecklistItem("item:A.7.9:return_procedures","Return procedures and post-return inspection", "must", False, "A.7.9 — protected"),
    ],
    should_contain= [
        ChecklistItem("item:A.7.9:home_office_link", "Reference to remote working policy (A.6.7) where home is the off-premises location", "should", False, "Cross-control consistency"),
        ChecklistItem("item:A.7.9:conference_travel","Specific guidance for conferences and customer-site visits", "should", False, "Common operational case"),
    ],
)

REQ_A710_STORAGE_MEDIA = EvidenceRequirement(
    id            = "req:A.7.10:storage_media_procedure",
    control_ref   = "A.7.10",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Storage Media Lifecycle Procedure",
    trigger_type  = "universal",
    description   = "A.7.10 requires storage media to be managed through their lifecycle (acquisition, use, transportation, disposal) per the classification scheme and handling requirements. Evidence is a media lifecycle procedure",
    must_contain  = [
        ChecklistItem("item:A.7.10:acquisition",  "Acquisition controls (approved media types, sourcing controls)", "must", False, "A.7.10 — acquisition"),
        ChecklistItem("item:A.7.10:use_controls", "Use controls (encryption, classification labels per A.5.13, allowed-use rules)", "must", False, "A.7.10 — use"),
        ChecklistItem("item:A.7.10:transport",    "Transport rules (encryption in transit, courier requirements, chain of custody)", "must", False, "A.7.10 — transportation"),
        ChecklistItem("item:A.7.10:disposal",     "Disposal controls (links to A.7.14 secure disposal procedure)", "must", False, "A.7.10 — disposal"),
        ChecklistItem("item:A.7.10:inventory",    "Inventory of removable media issued (who holds what)", "must", False, "A.7.10 — life cycle"),
    ],
    should_contain= [
        ChecklistItem("item:A.7.10:individual_tracking","Individual media tracking via serial or asset tag", "should", False, "Loss detection"),
        ChecklistItem("item:A.7.10:legacy_exception", "Exception process for legacy media that cannot meet current controls", "should", False, "Pragmatic transition"),
    ],
)

REQ_A711_SUPPORTING_UTILITIES = EvidenceRequirement(
    id            = "req:A.7.11:supporting_utilities_procedure",
    control_ref   = "A.7.11",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Supporting Utilities Continuity Procedure",
    trigger_type  = "universal",
    description   = "A.7.11 requires information processing facilities to be protected from power failures and other supporting-utility disruptions. Evidence is a procedure covering critical utilities, redundancy, monitoring, and testing",
    must_contain  = [
        ChecklistItem("item:A.7.11:critical_utilities","Critical utilities identified (power, cooling, water, communications, gas where relevant)", "must", False, "A.7.11 — supporting utilities"),
        ChecklistItem("item:A.7.11:redundancy",       "Redundancy / backup arrangements per utility (UPS, generator, dual-feed, redundant cooling)", "must", False, "A.7.11 — protected from power failures and other disruptions"),
        ChecklistItem("item:A.7.11:monitoring",       "Monitoring with alerting for utility status", "must", False, "A.7.11 — protected"),
        ChecklistItem("item:A.7.11:maintenance",      "Maintenance contracts with provider SLAs", "must", False, "A.7.11 — protected"),
        ChecklistItem("item:A.7.11:testing",          "Periodic testing arrangements (UPS run-time tests, generator tests)", "must", False, "Continuity validation"),
    ],
    should_contain= [
        ChecklistItem("item:A.7.11:alternate_site",   "Alternate-site considerations where redundancy unachievable on-site", "should", False, "Higher-resilience option"),
        ChecklistItem("item:A.7.11:vendor_sla_review","Periodic vendor SLA review for utility providers", "should", False, "Drift prevention"),
    ],
)

REQ_A712_CABLING_SECURITY = EvidenceRequirement(
    id            = "req:A.7.12:cabling_security_procedure",
    control_ref   = "A.7.12",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Cabling Security Procedure",
    trigger_type  = "universal",
    description   = "A.7.12 requires cables carrying power, data, or supporting information services to be protected from interception, interference, or damage. Evidence is a procedure covering cable routing, separation, labelling, and inspection",
    must_contain  = [
        ChecklistItem("item:A.7.12:routing",          "Cable routing principles (conduits, protected paths, away from public areas)", "must", False, "A.7.12 — protected from damage"),
        ChecklistItem("item:A.7.12:separation",       "Separation of power and data cables to reduce interference", "must", False, "A.7.12 — interference"),
        ChecklistItem("item:A.7.12:labelling",        "Cable and patch-panel labelling for traceability", "must", False, "A.7.12 — protected"),
        ChecklistItem("item:A.7.12:tamper_evidence",  "Tamper-evident protection where sensitive data is carried (locked cabinets, sealed runs)", "must", False, "A.7.12 — interception"),
        ChecklistItem("item:A.7.12:patch_panel_security","Patch panel / IDF / MDF physical security", "must", False, "A.7.12 — protected"),
    ],
    should_contain= [
        ChecklistItem("item:A.7.12:encrypted_backbone","Encrypted backbone or MACsec on segments crossing low-trust zones", "should", False, "Defense in depth"),
        ChecklistItem("item:A.7.12:periodic_inspection","Periodic physical inspection schedule", "should", False, "Drift prevention"),
    ],
)

REQ_A713_EQUIPMENT_MAINTENANCE = EvidenceRequirement(
    id            = "req:A.7.13:equipment_maintenance_procedure",
    control_ref   = "A.7.13",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Equipment Maintenance Procedure",
    trigger_type  = "universal",
    description   = "A.7.13 requires equipment to be maintained correctly to ensure availability, integrity, and confidentiality of information. Evidence is a procedure covering schedules, authorised providers, supervision, and post-maintenance verification",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:A.7.13:schedule",        "Maintenance schedule per equipment class with intervals", "must", False, "A.7.13 — maintained correctly"),
        ChecklistItem("item:A.7.13:authorised_providers","Authorised maintenance providers list with security expectations", "must", False, "A.7.13 — maintained"),
        ChecklistItem("item:A.7.13:supervision",     "Supervision requirements when maintenance involves access to sensitive information", "must", False, "A.7.13 — confidentiality of information"),
        ChecklistItem("item:A.7.13:offsite_maintenance","Asset-removal controls when equipment goes offsite for maintenance (data removal, escrow, return verification)", "must", False, "A.7.13 — integrity, confidentiality"),
        ChecklistItem("item:A.7.13:post_verification","Post-maintenance verification (functional test, integrity check)", "must", False, "A.7.13 — availability, integrity"),
    ],
    should_contain= [
        ChecklistItem("item:A.7.13:predictive_maint","Predictive maintenance based on monitoring data", "should", False, "Modern practice"),
        ChecklistItem("item:A.7.13:provider_criteria","Provider selection criteria documented", "should", False, "Supply chain hygiene"),
    ],
)

REQ_A714_SECURE_DISPOSAL = EvidenceRequirement(
    id            = "req:A.7.14:secure_disposal_procedure",
    control_ref   = "A.7.14",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Secure Disposal and Re-Use of Equipment Procedure",
    trigger_type  = "universal",
    description   = "A.7.14 requires equipment containing storage media to be verified for data and licensed-software removal before disposal or re-use. Evidence is a disposal procedure covering verification, certificates, chain of custody, and approved providers",
    must_contain  = [
        ChecklistItem("item:A.7.14:scope",            "Scope (all equipment containing any form of storage media)", "must", False, "A.7.14 — equipment containing storage media"),
        ChecklistItem("item:A.7.14:verification",     "Verification of data removal (overwrite, degauss, physical destruction) per classification", "must", False, "A.7.14 — sensitive data has been removed or securely overwritten"),
        ChecklistItem("item:A.7.14:software_removal", "Licensed software removal step before disposal or re-use", "must", False, "A.7.14 — licensed software has been removed"),
        ChecklistItem("item:A.7.14:certificate",      "Certificate of destruction obtained where applicable", "must", False, "Auditability"),
        ChecklistItem("item:A.7.14:chain_of_custody", "Chain of custody from collection to disposal", "must", False, "A.7.14 — securely"),
        ChecklistItem("item:A.7.14:approved_providers","Approved disposal providers list with security expectations", "must", False, "A.7.14 — securely"),
    ],
    should_contain= [
        ChecklistItem("item:A.7.14:destruction_method","Destruction method matched to data classification (shred/melt/degauss for highest)", "should", False, "Proportionality"),
        ChecklistItem("item:A.7.14:internal_vs_external","Decision criteria for in-house vs external disposal", "should", False, "Operational pragmatism"),
    ],
)


# ── ISO 27001 Annex A.8 — Technological Controls (Phase B, 2026-05-22) ───────
# A.8.11 / A.8.24 / A.8.25 already exist further up in the file as
# REQ_DATA_MASKING / REQ_ENCRYPTION_POLICY / REQ_SECURE_DEVELOPMENT.
# The 31 entries below cover the rest of Annex A.8.

REQ_A81_USER_ENDPOINTS = EvidenceRequirement(
    id            = "req:A.8.1:user_endpoint_devices_policy",
    control_ref   = "A.8.1",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "User Endpoint Devices Policy",
    trigger_type  = "universal",
    description   = "A.8.1 requires protection of information stored on, processed by, or accessible via user endpoint devices. Evidence is a policy (often the MDM / endpoint security policy) covering required protections per device class",
    must_contain  = [
        ChecklistItem("item:A.8.1:scope",         "Scope (corporate-owned, BYOD, contractor devices) defined", "must", False, "A.8.1 — user end point devices"),
        ChecklistItem("item:A.8.1:encryption",    "Full-disk or storage encryption required", "must", False, "A.8.1 — protected"),
        ChecklistItem("item:A.8.1:malware",       "Anti-malware / EDR required and maintained current (links to A.8.7)", "must", False, "A.8.1 — protected"),
        ChecklistItem("item:A.8.1:patch_level",   "Patch level / OS-version requirements stated", "must", False, "A.8.1 — protected"),
        ChecklistItem("item:A.8.1:authentication","Authentication and screen-lock requirements (links to A.7.7)", "must", False, "A.8.1 — accessible via end point devices"),
        ChecklistItem("item:A.8.1:remote_wipe",   "Remote wipe / lock capability for lost or stolen devices", "must", False, "A.8.1 — protected"),
        ChecklistItem("item:A.8.1:mdm_enrollment","MDM enrolment required before access to corporate information", "must", False, "A.8.1 — protected"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.1:jailbreak_detection","Jailbreak / root detection where mobile", "should", False, "Compromise signal"),
        ChecklistItem("item:A.8.1:app_controls",  "Application allowlisting / blocklisting on managed endpoints", "should", False, "Reduces attack surface"),
    ],
)

# ── Annex A.8.2 — Privileged access rights — technical_control spine (4-leaf) ──
# Promoted 2026-05-26 from single-leaf per [[curation-program-full-multi-leaf]].
# Spine: technical_control → configuration_baseline + procedure +
# monitoring_record + review_record (here as recertification, freshness 180
# days because § 8.2 calls for more frequent review than regular access).
# Authority: ISO 27002:2022 § 8.2 implementation guidance, items a–k.

REQ_A82_BASELINE = EvidenceRequirement(
    id            = "req:A.8.2:privileged_access_baseline",
    control_ref   = "A.8.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "configuration_baseline",
    title         = "Privileged Access Baseline",
    trigger_type  = "universal",
    description   = "A.8.2 requires identification of users needing privileged access per system and restriction of access to system-administration tools. The baseline defines the privileged role catalogue, the systems in scope, the strong-authentication configuration, and the PAM tooling boundaries — the configuration state against which the procedure operates",
    must_contain  = [
        ChecklistItem("item:A.8.2:bl_role_catalogue",       "Privileged role catalogue per system (which roles exist, what they grant)", "must", False, "27002:8.2a"),
        ChecklistItem("item:A.8.2:bl_systems_in_scope",     "Systems and processes in scope for privileged access governance",          "must", False, "27002:8.2a, g"),
        ChecklistItem("item:A.8.2:bl_strong_auth",          "Strong authentication required for all privileged access (MFA enforced)",  "must", False, "27002:8.2h"),
        ChecklistItem("item:A.8.2:bl_admin_tools_restricted", "Access to system-administration tools restricted to privileged roles only", "must", False, "27002:8.2g"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.2:bl_pam_tool",             "PAM tooling configured (vaulting, session recording)",                     "should", False, "Modern baseline"),
        ChecklistItem("item:A.8.2:bl_jit_capability",       "Just-in-time / time-bound elevation capability available",                 "should", False, "Reduces standing privilege"),
    ],
)

REQ_A82_PROCEDURE = EvidenceRequirement(
    id            = "req:A.8.2:privileged_access_procedure",
    control_ref   = "A.8.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Privileged Access Management Procedure",
    trigger_type  = "universal",
    description   = "A.8.2 requires the allocation and use of privileged access rights to be restricted and managed on a need-to-use, event-by-event basis with formal authorisation. The procedure documents provisioning, use, expiry and deprovisioning of privileged access — the operational counterpart to the baseline",
    must_contain  = [
        ChecklistItem("item:A.8.2:proc_need_to_use",       "Privileged access granted on need-to-use, event-by-event basis (less than or equal to the period needed)", "must", False, "27002:8.2b"),
        ChecklistItem("item:A.8.2:proc_authorisation",     "Formal authorisation process before privileged access is granted or changed", "must", False, "27002:8.2c, i"),
        ChecklistItem("item:A.8.2:proc_separate_accounts", "Separate accounts mandated for administrative actions (admin account distinct from daily-use)", "must", False, "27002:8.2f"),
        ChecklistItem("item:A.8.2:proc_expiry",            "Expiry rules defined for privileged access rights",                          "must", False, "27002:8.2d"),
        ChecklistItem("item:A.8.2:proc_accountability",    "Users acknowledge accountability for their privileged access (e.g. signed acceptable-use)", "must", False, "27002:8.2e"),
        ChecklistItem("item:A.8.2:proc_break_glass",       "Break-glass account governance (sealed credentials, post-use review)",       "must", False, "Emergency access without weak ongoing exposure"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.2:proc_routine_separation","Procedure prohibits routine non-privileged tasks under a privileged account", "should", False, "27002:8.2f"),
        ChecklistItem("item:A.8.2:proc_revocation_path",   "Revocation path on role change / termination (links to A.5.18 revocation records)", "should", False, "A.5.18 linkage"),
    ],
)

REQ_A82_ACTIVITY_LOG = EvidenceRequirement(
    id            = "req:A.8.2:privileged_activity_log",
    control_ref   = "A.8.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "monitoring_record",
    title         = "Privileged Activity Log",
    trigger_type  = "universal",
    description   = "A.8.2 requires audit logs of privileged actions. The activity log captures who performed which privileged action, when, on which system — the continuous evidence stream that the procedure was applied (and that anomalies surface for review)",
    must_contain  = [
        ChecklistItem("item:A.8.2:log_who",            "Identity of the privileged user captured per action",                "must", False, "27002:8.2j"),
        ChecklistItem("item:A.8.2:log_what",           "Action performed captured (command / change / access)",             "must", False, "27002:8.2j"),
        ChecklistItem("item:A.8.2:log_when",           "Timestamp captured per action",                                      "must", False, "27002:8.2j"),
        ChecklistItem("item:A.8.2:log_retention",      "Log retention period defined and enforced",                          "must", False, "A.8.15 linkage"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.2:log_anomaly_alert",  "Anomaly alerting configured (unusual hours, unusual scope)",         "should", False, "Modern baseline"),
        ChecklistItem("item:A.8.2:log_tamper_protect", "Log integrity protection (write-once / SIEM forwarding)",            "should", False, "Defensible evidence"),
    ],
)

REQ_A82_RECERTIFICATION = EvidenceRequirement(
    id              = "req:A.8.2:privileged_access_recertification",
    control_ref     = "A.8.2",
    standard_id     = "ISO27001:2022",
    evidence_type   = "review_record",
    title           = "Privileged Access Recertification",
    trigger_type    = "universal",
    description     = "A.8.2 calls for periodic review of privileged access — typically more frequent than the general access review at A.5.18 (this curation sets freshness at 180 days; tenants with high-risk processing may run quarterly). The recertification record evidences that each privileged grant was re-confirmed by the asset owner",
    freshness_days  = 180,
    must_contain    = [
        ChecklistItem("item:A.8.2:rc_date",            "Recertification date within the planned interval (≤180 days since last)",  "must", False, "27002:8.2k"),
        ChecklistItem("item:A.8.2:rc_reviewer",        "Reviewer identity (asset owner or delegated authority)",                    "must", False, "Accountability"),
        ChecklistItem("item:A.8.2:rc_per_account",     "Per-privileged-account outcome (re-confirmed / amended / revoked)",         "must", False, "27002:8.2k"),
        ChecklistItem("item:A.8.2:rc_actions",         "Revocation/modification actions completed for non-reconfirmed access",      "must", False, "27002:8.2k"),
    ],
    should_contain  = [
        ChecklistItem("item:A.8.2:rc_role_change_trigger", "Role-change events trigger ad-hoc recertification outside the interval", "should", False, "27002:8.2g"),
        ChecklistItem("item:A.8.2:rc_next_date",           "Next planned recertification date stated",                              "should", False, "Planning"),
    ],
)

REQ_A83_INFORMATION_ACCESS_RESTRICTION = EvidenceRequirement(
    id            = "req:A.8.3:information_access_restriction_procedure",
    control_ref   = "A.8.3",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Information Access Restriction Procedure",
    trigger_type  = "universal",
    description   = "A.8.3 requires access to information and associated assets to be restricted per the topic-specific access control policy (A.5.15). Evidence is a procedure implementing that policy across systems",
    must_contain  = [
        ChecklistItem("item:A.8.3:per_system_matrix","Access matrix per system / repository (who can do what)", "must", False, "A.8.3 — restricted"),
        ChecklistItem("item:A.8.3:enforcement",  "Enforcement mechanism stated (ACLs, RBAC, ABAC, identity provider)", "must", False, "A.8.3 — restricted"),
        ChecklistItem("item:A.8.3:policy_link",  "Link to access control policy (A.5.15) and identity management (A.5.16)", "must", False, "A.8.3 — accordance with topic-specific policy"),
        ChecklistItem("item:A.8.3:authorisation","Authorisation workflow for granting and revoking access", "must", False, "A.8.3 — restricted"),
        ChecklistItem("item:A.8.3:recertification","Periodic recertification cadence (links to A.5.18)", "must", False, "Drift prevention"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.3:classification_driven","Classification-driven restriction (sensitive info → stronger controls)", "should", False, "Proportionality"),
        ChecklistItem("item:A.8.3:cloud_extensions","Cloud-specific extensions (SaaS app permissions, IAM)", "should", False, "Modern environment"),
    ],
)

REQ_A84_SOURCE_CODE_ACCESS = EvidenceRequirement(
    id            = "req:A.8.4:source_code_access_procedure",
    control_ref   = "A.8.4",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Source Code, Development Tools and Library Access Procedure",
    trigger_type  = "universal",
    description   = "A.8.4 requires read and write access to source code, development tools, and software libraries to be appropriately managed. Evidence is a procedure covering repository access, code review, and dependency management",
    must_contain  = [
        ChecklistItem("item:A.8.4:repo_inventory", "Inventory of code repositories and their classification", "must", False, "A.8.4 — source code"),
        ChecklistItem("item:A.8.4:rbac",           "Role-based access (read, write, admin) per repository", "must", False, "A.8.4 — read and write access"),
        ChecklistItem("item:A.8.4:branch_protection","Branch protection / code review requirements before merge to protected branches", "must", False, "A.8.4 — appropriately managed"),
        ChecklistItem("item:A.8.4:secrets_rules",  "Rules preventing secrets in source code (scanning, vaulting)", "must", False, "A.8.4 — appropriately managed"),
        ChecklistItem("item:A.8.4:dependency_mgmt","Third-party library and dependency management (allowlists, version pinning, vulnerability scanning)", "must", False, "A.8.4 — software libraries"),
        ChecklistItem("item:A.8.4:tools_access",   "Access to development tools and CI/CD systems restricted", "must", False, "A.8.4 — development tools"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.4:signed_commits", "Signed commits / provenance tracking", "should", False, "Supply chain hygiene"),
        ChecklistItem("item:A.8.4:offboarding",    "Repository access offboarding aligned with A.5.16 identity termination", "should", False, "Common gap"),
    ],
)

REQ_A85_SECURE_AUTHENTICATION = EvidenceRequirement(
    id            = "req:A.8.5:secure_authentication_policy",
    control_ref   = "A.8.5",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Secure Authentication Policy",
    trigger_type  = "universal",
    description   = "A.8.5 requires secure authentication technologies and procedures to be implemented based on the access control policy. Evidence is an authentication policy stating factor requirements per risk level",
    must_contain  = [
        ChecklistItem("item:A.8.5:factor_requirements","Authentication factor requirements per risk level / access tier", "must", False, "A.8.5 — based on information access restrictions"),
        ChecklistItem("item:A.8.5:password_policy","Password policy (length, complexity, expiry where applicable, breach-list checking)", "must", False, "A.8.5 — secure authentication"),
        ChecklistItem("item:A.8.5:mfa_scope",      "MFA scope (where required by access policy and risk)", "must", False, "A.8.5 — secure authentication"),
        ChecklistItem("item:A.8.5:secure_transmission","Secure transmission requirements (TLS, no plaintext credentials)", "must", False, "A.8.5 — secure authentication"),
        ChecklistItem("item:A.8.5:session_management","Session management (timeout, re-authentication for sensitive actions)", "must", False, "A.8.5 — implemented"),
        ChecklistItem("item:A.8.5:lockout",        "Lockout / throttling for failed authentication attempts", "must", False, "A.8.5 — secure"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.5:passwordless",   "Direction toward passwordless / phishing-resistant authentication", "should", False, "Modern best practice"),
        ChecklistItem("item:A.8.5:adaptive",       "Adaptive / risk-based authentication where deployed", "should", False, "Modern best practice"),
    ],
)

REQ_A86_CAPACITY_MANAGEMENT = EvidenceRequirement(
    id            = "req:A.8.6:capacity_management_procedure",
    control_ref   = "A.8.6",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Capacity Management Procedure",
    trigger_type  = "universal",
    description   = "A.8.6 requires resource use to be monitored and adjusted in line with current and expected capacity requirements. Evidence is a procedure covering monitored resources, thresholds, and forecasting",
    must_contain  = [
        ChecklistItem("item:A.8.6:monitored_resources","Resources monitored (CPU, memory, storage, network, database connections, licences)", "must", False, "A.8.6 — use of resources monitored"),
        ChecklistItem("item:A.8.6:current_vs_expected","Current vs expected capacity requirements documented", "must", False, "A.8.6 — current and expected capacity"),
        ChecklistItem("item:A.8.6:thresholds",      "Alert thresholds for action (warning, critical)", "must", False, "A.8.6 — adjusted in line"),
        ChecklistItem("item:A.8.6:forecasting",     "Forecasting approach for growth (historical trend, business-driven)", "must", False, "A.8.6 — expected capacity"),
        ChecklistItem("item:A.8.6:escalation",      "Escalation when thresholds breached (procurement, scale-out)", "must", False, "A.8.6 — adjusted"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.6:automation",      "Auto-scaling automation where deployed", "should", False, "Modern cloud-native baseline"),
        ChecklistItem("item:A.8.6:dr_integration",  "Integration with continuity planning (A.5.30 ICT readiness)", "should", False, "Capacity is part of resilience"),
    ],
)

REQ_A87_MALWARE_PROTECTION = EvidenceRequirement(
    id            = "req:A.8.7:malware_protection_procedure",
    control_ref   = "A.8.7",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Protection Against Malware Procedure",
    trigger_type  = "universal",
    description   = "A.8.7 requires protection against malware to be implemented and supported by appropriate user awareness. Evidence is a procedure covering anti-malware deployment, update cadence, and integration with awareness",
    must_contain  = [
        ChecklistItem("item:A.8.7:tools_deployed",  "Anti-malware / EDR tools deployed across endpoints, servers, mail systems", "must", False, "A.8.7 — protection against malware implemented"),
        ChecklistItem("item:A.8.7:update_cadence",  "Signature / threat-intelligence update cadence (continuous or hourly preferred)", "must", False, "A.8.7 — implemented"),
        ChecklistItem("item:A.8.7:scope",           "Scope (endpoints, file servers, email gateways, web traffic)", "must", False, "A.8.7 — implemented"),
        ChecklistItem("item:A.8.7:detection_handling","Detection handling (quarantine, incident creation, link to A.5.26)", "must", False, "A.8.7 — implemented"),
        ChecklistItem("item:A.8.7:user_awareness",  "User awareness component (links to A.6.3 training programme)", "must", False, "A.8.7 — supported by appropriate user awareness"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.7:behavioral_detection","Behavioral / heuristic detection beyond signature", "should", False, "Modern threat landscape"),
        ChecklistItem("item:A.8.7:sandboxing",      "Sandboxing of suspicious attachments / executables", "should", False, "Defense in depth"),
    ],
)

REQ_A88_TECHNICAL_VULNERABILITIES = EvidenceRequirement(
    id            = "req:A.8.8:vulnerability_management_procedure",
    control_ref   = "A.8.8",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Technical Vulnerability Management Procedure",
    trigger_type  = "universal",
    description   = "A.8.8 requires information about technical vulnerabilities to be obtained, the organization's exposure evaluated, and appropriate measures taken. Evidence is a vulnerability management procedure covering intel sources, scanning, triage, and remediation SLAs",
    freshness_days = 90,
    must_contain  = [
        ChecklistItem("item:A.8.8:intel_sources",   "Intelligence sources (vendor advisories, CVE feeds, ISACs)", "must", False, "A.8.8 — information about vulnerabilities obtained"),
        ChecklistItem("item:A.8.8:asset_coverage",  "Asset coverage stated (links to A.5.9 asset inventory)", "must", False, "A.8.8 — exposure evaluated"),
        ChecklistItem("item:A.8.8:scanning_cadence","Vulnerability scanning cadence per asset class", "must", False, "A.8.8 — exposure evaluated"),
        ChecklistItem("item:A.8.8:triage",          "Triage approach (CVSS, exploitability, asset criticality)", "must", False, "A.8.8 — evaluated"),
        ChecklistItem("item:A.8.8:remediation_sla", "Remediation SLA per severity (critical, high, medium, low)", "must", False, "A.8.8 — appropriate measures taken"),
        ChecklistItem("item:A.8.8:exceptions",      "Exception register for accepted vulnerabilities with expiry", "must", False, "A.8.8 — appropriate measures"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.8:patch_prioritisation","Patch prioritisation factoring exploitability + business impact", "should", False, "Pragmatic vs CVSS-only"),
        ChecklistItem("item:A.8.8:zero_day_handling","Zero-day handling procedure (compensating controls, monitoring)", "should", False, "When patches aren't available"),
    ],
)

REQ_A89_CONFIGURATION_MANAGEMENT = EvidenceRequirement(
    id            = "req:A.8.9:configuration_management_procedure",
    control_ref   = "A.8.9",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Configuration Management Procedure",
    trigger_type  = "universal",
    description   = "A.8.9 requires configurations (including security configurations) of hardware, software, services, and networks to be established, documented, implemented, monitored, and reviewed. Evidence is a configuration management procedure",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:A.8.9:baseline_configs","Baseline configurations documented per asset class", "must", False, "A.8.9 — established and documented"),
        ChecklistItem("item:A.8.9:hardening_standards","Hardening standards referenced (CIS, vendor guides, internal baselines)", "must", False, "A.8.9 — security configurations"),
        ChecklistItem("item:A.8.9:deployment",      "Deployment process applying baseline configurations consistently", "must", False, "A.8.9 — implemented"),
        ChecklistItem("item:A.8.9:drift_detection", "Drift detection from baseline (monitoring)", "must", False, "A.8.9 — monitored"),
        ChecklistItem("item:A.8.9:periodic_review", "Periodic review of baselines (technology updates, threat changes)", "must", False, "A.8.9 — reviewed"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.9:iac_pipelines",   "Infrastructure-as-code pipelines for repeatable deployment", "should", False, "Modern practice"),
        ChecklistItem("item:A.8.9:approved_deviations","Approved-deviation register for systems unable to meet baseline", "should", False, "Reality of mixed estates"),
    ],
)

REQ_A810_INFORMATION_DELETION = EvidenceRequirement(
    id            = "req:A.8.10:information_deletion_procedure",
    control_ref   = "A.8.10",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Information Deletion Procedure",
    trigger_type  = "universal",
    description   = "A.8.10 requires information stored in systems, devices, or media to be deleted when no longer required. Evidence is a procedure linking retention triggers, deletion methods, and verification",
    must_contain  = [
        ChecklistItem("item:A.8.10:retention_trigger","Retention trigger (links to A.5.33 records protection)", "must", False, "A.8.10 — when no longer required"),
        ChecklistItem("item:A.8.10:deletion_methods","Deletion methods per media / system type (logical delete, overwrite, crypto-erase)", "must", False, "A.8.10 — deleted"),
        ChecklistItem("item:A.8.10:verification",   "Verification of deletion (audit log entry, sample re-read)", "must", False, "A.8.10 — deleted"),
        ChecklistItem("item:A.8.10:records",        "Records of deletion (what, when, by whom)", "must", False, "Auditability"),
        ChecklistItem("item:A.8.10:scope_systems",  "Scope covers backups and replicas, not only primary systems", "must", False, "A.8.10 — any other storage media"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.10:automated_retention","Automated retention enforcement where supported", "should", False, "Scale"),
        ChecklistItem("item:A.8.10:legal_hold",     "Legal-hold integration overriding deletion", "should", False, "Litigation readiness"),
    ],
)

REQ_A812_DLP = EvidenceRequirement(
    id            = "req:A.8.12:data_leakage_prevention_procedure",
    control_ref   = "A.8.12",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Data Leakage Prevention Procedure",
    trigger_type  = "universal",
    description   = "A.8.12 requires DLP measures to be applied to systems, networks, and devices processing or transmitting sensitive information. Evidence is a procedure covering channels in scope, classification-driven rules, and alert handling",
    must_contain  = [
        ChecklistItem("item:A.8.12:scope",          "Scope of sensitive information categories covered (links to A.5.12 classification)", "must", False, "A.8.12 — sensitive information"),
        ChecklistItem("item:A.8.12:channels",       "DLP controls per channel (email, web, endpoint, cloud, removable media)", "must", False, "A.8.12 — systems, networks and any other devices"),
        ChecklistItem("item:A.8.12:classification_driven","Classification-driven enforcement (different rules per classification level)", "must", False, "A.8.12 — sensitive information"),
        ChecklistItem("item:A.8.12:alert_handling", "Alert handling (triage, investigation, link to A.5.26)", "must", False, "A.8.12 — measures applied"),
        ChecklistItem("item:A.8.12:incident_link",  "Incident response integration when leakage confirmed", "must", False, "A.8.12 — measures"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.12:user_education", "User education on what triggers DLP (links to A.6.3)", "should", False, "Reduces friction + false positives"),
        ChecklistItem("item:A.8.12:tuning",         "False-positive tuning process", "should", False, "Operational sustainability"),
    ],
)

REQ_A813_BACKUP = EvidenceRequirement(
    id            = "req:A.8.13:backup_policy",
    control_ref   = "A.8.13",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Information Backup Policy and Restore Test Records",
    trigger_type  = "universal",
    description   = "A.8.13 requires backup copies of information, software, and systems to be maintained and regularly tested per the backup policy. Evidence is a backup policy plus restore test records",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:A.8.13:scope",        "Scope (which information, software, systems are backed up)", "must", False, "A.8.13 — backup copies"),
        ChecklistItem("item:A.8.13:frequency",    "Frequency per asset class (continuous, daily, weekly)", "must", False, "A.8.13 — maintained"),
        ChecklistItem("item:A.8.13:retention",    "Retention period per asset class", "must", False, "A.8.13 — maintained"),
        ChecklistItem("item:A.8.13:storage",      "Storage location and separation (offsite or air-gapped copy)", "must", False, "A.8.13 — maintained"),
        ChecklistItem("item:A.8.13:encryption",   "Encryption of backups (at rest, in transit)", "must", False, "A.8.13 — maintained"),
        ChecklistItem("item:A.8.13:restore_test", "Restore testing cadence stated", "must", False, "A.8.13 — regularly tested"),
        ChecklistItem("item:A.8.13:last_restore","Last restore test date and outcome recorded", "must", False, "A.8.13 — regularly tested"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.13:three_two_one","3-2-1 backup rule (3 copies, 2 media, 1 offsite) or equivalent", "should", False, "Established baseline"),
        ChecklistItem("item:A.8.13:rpo_alignment","Recovery point objective alignment (links to A.5.30)", "should", False, "Continuity coherence"),
    ],
)

REQ_A814_REDUNDANCY = EvidenceRequirement(
    id            = "req:A.8.14:redundancy_plan",
    control_ref   = "A.8.14",
    standard_id   = "ISO27001:2022",
    evidence_type = "plan",
    title         = "Redundancy of Information Processing Facilities Plan",
    trigger_type  = "universal",
    description   = "A.8.14 requires information processing facilities to be implemented with redundancy sufficient to meet availability requirements. Evidence is a redundancy plan covering critical services, approach per service, and test records",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:A.8.14:critical_services","Critical service identification with availability requirements", "must", False, "A.8.14 — availability requirements"),
        ChecklistItem("item:A.8.14:redundancy_approach","Redundancy approach per service (active-active, active-passive, cold standby)", "must", False, "A.8.14 — redundancy sufficient"),
        ChecklistItem("item:A.8.14:failover_testing","Failover testing cadence and last test outcome", "must", False, "A.8.14 — sufficient to meet"),
        ChecklistItem("item:A.8.14:monitoring",   "Monitoring of redundant components (so failures are detected before failover needed)", "must", False, "A.8.14 — implemented"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.14:cross_az",     "Cross-AZ / cross-region considerations for cloud-hosted facilities", "should", False, "Modern hosting reality"),
        ChecklistItem("item:A.8.14:sla_implications","SLA implications for redundant vs single-instance services", "should", False, "Honest commitment"),
    ],
)

REQ_A815_LOGGING = EvidenceRequirement(
    id            = "req:A.8.15:logging_policy",
    control_ref   = "A.8.15",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Logging Policy",
    trigger_type  = "universal",
    description   = "A.8.15 requires logs of activities, exceptions, faults, and other relevant events to be produced, stored, protected, and analysed. Evidence is a logging policy stating scope, content, retention, protection, and analysis",
    must_contain  = [
        ChecklistItem("item:A.8.15:scope",        "Scope (which systems, applications, network elements emit logs)", "must", False, "A.8.15 — logs produced"),
        ChecklistItem("item:A.8.15:content",      "Required log content (who, what, when, where, success/failure)", "must", False, "A.8.15 — record activities, exceptions, faults"),
        ChecklistItem("item:A.8.15:retention",    "Retention period per log class", "must", False, "A.8.15 — stored"),
        ChecklistItem("item:A.8.15:protection",   "Protection from tampering (append-only, hashing, separation of duties)", "must", False, "A.8.15 — protected"),
        ChecklistItem("item:A.8.15:central_collection","Centralised collection (SIEM or log aggregator)", "must", False, "A.8.15 — analysed"),
        ChecklistItem("item:A.8.15:analysis",     "Analysis approach (manual review, correlation, alerting) (links to A.8.16)", "must", False, "A.8.15 — analysed"),
        ChecklistItem("item:A.8.15:time_sync",    "Time synchronisation requirement (links to A.8.17) so logs correlate", "must", False, "A.8.15 — relevant events"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.15:log_integrity","Log integrity verification (hashing, signing)", "should", False, "Forensic-grade"),
        ChecklistItem("item:A.8.15:legal_hold",   "Legal-hold integration overriding retention", "should", False, "Litigation readiness"),
    ],
)

REQ_A816_MONITORING_ACTIVITIES = EvidenceRequirement(
    id            = "req:A.8.16:monitoring_activities_procedure",
    control_ref   = "A.8.16",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Monitoring Activities Procedure",
    trigger_type  = "universal",
    description   = "A.8.16 requires networks, systems, and applications to be monitored for anomalous behaviour and appropriate actions taken. Evidence is a monitoring procedure with detection methods, alert routing, and incident integration",
    must_contain  = [
        ChecklistItem("item:A.8.16:scope",         "Scope (networks, systems, applications, cloud services)", "must", False, "A.8.16 — networks, systems and applications"),
        ChecklistItem("item:A.8.16:detection_methods","Detection methods (signature, anomaly, threat intel, behavioural)", "must", False, "A.8.16 — anomalous behaviour"),
        ChecklistItem("item:A.8.16:alert_routing", "Alert routing to security operations / on-call", "must", False, "A.8.16 — appropriate actions taken"),
        ChecklistItem("item:A.8.16:triage_criteria","Triage criteria for separating events from incidents (links to A.5.25)", "must", False, "A.8.16 — evaluate potential incidents"),
        ChecklistItem("item:A.8.16:incident_link", "Incident response handoff (A.5.26) when triage confirms incident", "must", False, "A.8.16 — potential incidents"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.16:siem_use_cases","SIEM use case catalogue with coverage map", "should", False, "Measurable monitoring"),
        ChecklistItem("item:A.8.16:threat_hunting","Threat-hunting cadence for proactive detection", "should", False, "Modern maturity bar"),
    ],
)

REQ_A817_CLOCK_SYNC = EvidenceRequirement(
    id            = "req:A.8.17:clock_synchronization_procedure",
    control_ref   = "A.8.17",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Clock Synchronization Procedure",
    trigger_type  = "universal",
    description   = "A.8.17 requires the clocks of information processing systems to be synchronized to approved time sources. Evidence is a procedure naming approved sources and the synchronisation arrangement",
    must_contain  = [
        ChecklistItem("item:A.8.17:approved_sources","Approved time sources named (stratum-1 NTP, GPS, vendor-provided)", "must", False, "A.8.17 — approved time sources"),
        ChecklistItem("item:A.8.17:protocol",       "Synchronisation protocol (NTP, PTP) and security where supported (NTS, authenticated NTP)", "must", False, "A.8.17 — synchronized"),
        ChecklistItem("item:A.8.17:scope",          "Scope (servers, network devices, endpoints, containers)", "must", False, "A.8.17 — information processing systems"),
        ChecklistItem("item:A.8.17:monitoring",     "Monitoring of sync status (alert on drift, source loss)", "must", False, "A.8.17 — synchronized"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.17:stratum_hierarchy","Stratum hierarchy documented (internal vs external sources)", "should", False, "Topology clarity"),
        ChecklistItem("item:A.8.17:source_security","Security of the NTP feed itself (authenticated, signed)", "should", False, "Defense in depth"),
    ],
)

REQ_A818_PRIVILEGED_UTILITY_PROGRAMS = EvidenceRequirement(
    id            = "req:A.8.18:privileged_utility_programs_procedure",
    control_ref   = "A.8.18",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Privileged Utility Programs Procedure",
    trigger_type  = "universal",
    description   = "A.8.18 requires the use of utility programs capable of overriding system and application controls to be restricted and tightly controlled. Evidence is a procedure covering inventory, authorisation, JIT access, and logging",
    must_contain  = [
        ChecklistItem("item:A.8.18:inventory",     "Inventory of utility programs that can override controls (debuggers, sysinternals, low-level admin tools)", "must", False, "A.8.18 — utility programs that can override"),
        ChecklistItem("item:A.8.18:authorisation", "Authorisation required for use of each utility program", "must", False, "A.8.18 — restricted"),
        ChecklistItem("item:A.8.18:jit_access",    "Just-in-time access where possible", "must", False, "A.8.18 — tightly controlled"),
        ChecklistItem("item:A.8.18:logging",       "Logging of all uses (links to A.8.15)", "must", False, "A.8.18 — tightly controlled"),
        ChecklistItem("item:A.8.18:periodic_review","Periodic review of who has access and whether still needed", "must", False, "Drift prevention"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.18:removal_where_unnecessary","Removal of utility programs from systems where not needed", "should", False, "Attack-surface reduction"),
    ],
)

REQ_A819_SOFTWARE_INSTALLATION = EvidenceRequirement(
    id            = "req:A.8.19:software_installation_procedure",
    control_ref   = "A.8.19",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Software Installation on Operational Systems Procedure",
    trigger_type  = "universal",
    description   = "A.8.19 requires procedures and measures to securely manage software installation on operational systems. Evidence is a procedure covering approved-software list, approval workflow, integrity verification, and post-install verification",
    must_contain  = [
        ChecklistItem("item:A.8.19:approved_list", "Approved software list maintained", "must", False, "A.8.19 — securely manage"),
        ChecklistItem("item:A.8.19:approval_workflow","Approval workflow for new software (security review, licence check, integration test)", "must", False, "A.8.19 — securely manage"),
        ChecklistItem("item:A.8.19:integrity",     "Integrity / signing verification before installation", "must", False, "A.8.19 — securely"),
        ChecklistItem("item:A.8.19:privileged_role","Installation by privileged role only", "must", False, "A.8.19 — securely manage"),
        ChecklistItem("item:A.8.19:post_install",  "Post-install verification (functional test, vulnerability scan)", "must", False, "A.8.19 — securely manage"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.19:inventory_tooling","Software inventory tooling for ongoing visibility", "should", False, "Drift detection"),
        ChecklistItem("item:A.8.19:allowlisting",  "Allowlisting on operational systems where supported", "should", False, "Strong baseline"),
    ],
)

REQ_A820_NETWORKS_SECURITY = EvidenceRequirement(
    id            = "req:A.8.20:networks_security_policy",
    control_ref   = "A.8.20",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Networks Security Policy",
    trigger_type  = "universal",
    description   = "A.8.20 requires networks and network devices to be secured, managed, and controlled to protect information in systems and applications. Evidence is a network security policy stating architecture principles, perimeters, monitoring, and change control",
    must_contain  = [
        ChecklistItem("item:A.8.20:scope",          "Scope (corporate LAN, WAN, wireless, cloud VPCs, partner connections)", "must", False, "A.8.20 — networks"),
        ChecklistItem("item:A.8.20:architecture",   "Security architecture principles (defense-in-depth, segmentation, fail-safe)", "must", False, "A.8.20 — secured, managed and controlled"),
        ChecklistItem("item:A.8.20:zones",          "Perimeter and zone definitions (links to A.8.22 segregation)", "must", False, "A.8.20 — controlled"),
        ChecklistItem("item:A.8.20:monitoring",     "Monitoring of network activity (links to A.8.16)", "must", False, "A.8.20 — controlled"),
        ChecklistItem("item:A.8.20:change_control", "Change control for network devices (links to A.8.32)", "must", False, "A.8.20 — managed"),
        ChecklistItem("item:A.8.20:periodic_review","Periodic architecture review", "must", False, "A.8.20 — managed"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.20:zero_trust",     "Direction toward zero-trust principles", "should", False, "Modern best practice"),
        ChecklistItem("item:A.8.20:network_as_code","Network configuration as code", "should", False, "Repeatability"),
    ],
)

REQ_A821_NETWORK_SERVICES = EvidenceRequirement(
    id            = "req:A.8.21:network_services_security_procedure",
    control_ref   = "A.8.21",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Security of Network Services Procedure",
    trigger_type  = "universal",
    description   = "A.8.21 requires security mechanisms, service levels, and service requirements of network services to be identified, implemented, and monitored. Evidence is a procedure covering the service catalogue, controls, and monitoring",
    must_contain  = [
        ChecklistItem("item:A.8.21:catalogue",   "Catalogue of network services in use (managed services, ISPs, CDNs, DNS providers)", "must", False, "A.8.21 — network services"),
        ChecklistItem("item:A.8.21:security_mechanisms","Security mechanisms required per service (encryption, authentication, integrity)", "must", False, "A.8.21 — security mechanisms"),
        ChecklistItem("item:A.8.21:service_levels","Service-level requirements stated (availability, latency, support response)", "must", False, "A.8.21 — service levels"),
        ChecklistItem("item:A.8.21:monitoring",  "Monitoring of service delivery against requirements", "must", False, "A.8.21 — monitored"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.21:vendor_governance","Vendor-managed network services governance (links to A.5.19, A.5.20)", "should", False, "Supplier-side oversight"),
    ],
)

REQ_A822_NETWORK_SEGREGATION = EvidenceRequirement(
    id            = "req:A.8.22:network_segregation_policy",
    control_ref   = "A.8.22",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Network Segregation Policy",
    trigger_type  = "universal",
    description   = "A.8.22 requires groups of information services, users, and information systems to be segregated in the organization's networks. Evidence is a segregation policy stating zones, inter-zone rules, and enforcement",
    must_contain  = [
        ChecklistItem("item:A.8.22:rationale",   "Rationale for segregation (sensitivity, function, trust level)", "must", False, "A.8.22 — segregated"),
        ChecklistItem("item:A.8.22:zone_model",  "Zone model (e.g. DMZ, internal, restricted, OT, dev/test/prod)", "must", False, "A.8.22 — groups segregated"),
        ChecklistItem("item:A.8.22:flow_rules",  "Inter-zone flow rules (default deny, explicit allowlist)", "must", False, "A.8.22 — segregated"),
        ChecklistItem("item:A.8.22:enforcement", "Enforcement points (firewall, ACL, security group, identity-aware proxy)", "must", False, "A.8.22 — segregated"),
        ChecklistItem("item:A.8.22:exception",   "Exception process for cross-zone access needs", "must", False, "Operational reality"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.22:micro_segmentation","Micro-segmentation considerations (east-west traffic control)", "should", False, "Modern direction"),
    ],
)

REQ_A823_WEB_FILTERING = EvidenceRequirement(
    id            = "req:A.8.23:web_filtering_procedure",
    control_ref   = "A.8.23",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Web Filtering Procedure",
    trigger_type  = "universal",
    description   = "A.8.23 requires access to external websites to be managed to reduce exposure to malicious content. Evidence is a procedure covering filtering scope, blocked categories, override workflow, and monitoring",
    must_contain  = [
        ChecklistItem("item:A.8.23:scope",        "Filtering scope (corporate-managed devices, on-network traffic, BYOD where in scope)", "must", False, "A.8.23 — access to external websites"),
        ChecklistItem("item:A.8.23:categories",   "Category-based blocking (malware, phishing, illegal content, anonymisers)", "must", False, "A.8.23 — reduce exposure to malicious content"),
        ChecklistItem("item:A.8.23:override",     "Block-page UX with override / business-justification workflow", "must", False, "A.8.23 — managed"),
        ChecklistItem("item:A.8.23:monitoring",   "Monitoring of attempted access to blocked sites (link to A.8.16)", "must", False, "A.8.23 — managed"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.23:tls_inspection","TLS inspection considerations (privacy balance, exclusions)", "should", False, "Operational trade-off"),
        ChecklistItem("item:A.8.23:byod_scope",   "BYOD coverage strategy (proxy enforcement, off-network behaviour)", "should", False, "Realistic scope"),
    ],
)

REQ_A826_APP_SECURITY_REQUIREMENTS = EvidenceRequirement(
    id            = "req:A.8.26:application_security_requirements_procedure",
    control_ref   = "A.8.26",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Application Security Requirements Procedure",
    trigger_type  = "universal",
    description   = "A.8.26 requires information security requirements to be identified, specified, and approved when developing or acquiring applications. Evidence is a procedure embedding security requirements in the SDLC and acquisition process",
    must_contain  = [
        ChecklistItem("item:A.8.26:requirements_step","Security requirements gathering step at project initiation (links to A.5.8)", "must", False, "A.8.26 — identified, specified"),
        ChecklistItem("item:A.8.26:requirement_types","Categories of requirements (auth, data protection, logging, error handling, integrations)", "must", False, "A.8.26 — information security requirements"),
        ChecklistItem("item:A.8.26:approval",      "Approval authority for requirements before development / procurement proceeds", "must", False, "A.8.26 — approved"),
        ChecklistItem("item:A.8.26:traceability",  "Traceability from requirements into design, code, and test cases", "must", False, "A.8.26 — specified"),
        ChecklistItem("item:A.8.26:exception",     "Exception process for requirements that cannot be met", "must", False, "Pragmatic adoption"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.26:threat_modeling","Threat modeling reference at design phase", "should", False, "Proactive control identification"),
        ChecklistItem("item:A.8.26:security_stories","Security stories integrated into agile backlog", "should", False, "Modern delivery"),
    ],
)

REQ_A827_ARCHITECTURE_PRINCIPLES = EvidenceRequirement(
    id            = "req:A.8.27:secure_architecture_principles_policy",
    control_ref   = "A.8.27",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Secure System Architecture and Engineering Principles",
    trigger_type  = "universal",
    description   = "A.8.27 requires principles for engineering secure systems to be established, documented, maintained, and applied to development activities. Evidence is a policy enumerating principles and their application",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:A.8.27:principles",   "Principles enumerated (defense in depth, least privilege, fail-safe defaults, separation of concerns, complete mediation)", "must", False, "A.8.27 — principles established"),
        ChecklistItem("item:A.8.27:application",  "Application to information system development activities defined", "must", False, "A.8.27 — applied to development activities"),
        ChecklistItem("item:A.8.27:documented",   "Principles documented in accessible form for engineers", "must", False, "A.8.27 — documented"),
        ChecklistItem("item:A.8.27:maintenance",  "Maintenance cadence stated (review as technologies and threats evolve)", "must", False, "A.8.27 — maintained"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.27:reference_arch","Reference architecture patterns embedding the principles", "should", False, "Concrete guidance"),
        ChecklistItem("item:A.8.27:tm_integration","Threat modelling methodology integration", "should", False, "Closes design loop"),
    ],
)

REQ_A828_SECURE_CODING = EvidenceRequirement(
    id            = "req:A.8.28:secure_coding_policy",
    control_ref   = "A.8.28",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Secure Coding Standards",
    trigger_type  = "universal",
    description   = "A.8.28 requires secure coding principles to be applied to software development. Evidence is a secure coding standards policy stating language-specific guidance, common vulnerability prevention, and review requirements",
    must_contain  = [
        ChecklistItem("item:A.8.28:language_standards","Language-specific coding standards (e.g. Python, Java, JavaScript, Go)", "must", False, "A.8.28 — secure coding principles"),
        ChecklistItem("item:A.8.28:vulnerability_prevention","Common vulnerability prevention guidance (OWASP Top 10, CWE Top 25)", "must", False, "A.8.28 — secure coding"),
        ChecklistItem("item:A.8.28:code_review",  "Code review requirement before merge for production code", "must", False, "A.8.28 — applied"),
        ChecklistItem("item:A.8.28:sast",         "Automated static analysis (SAST) in CI pipeline", "must", False, "A.8.28 — applied"),
        ChecklistItem("item:A.8.28:secrets_in_code","Secrets management — no secrets in code, vaulting required", "must", False, "A.8.28 — secure coding"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.28:dependency_scanning","Dependency / SCA scanning enabled", "should", False, "Supply chain hygiene"),
        ChecklistItem("item:A.8.28:training",     "Secure coding training for developers (links to A.6.3)", "should", False, "People dimension"),
    ],
)

REQ_A829_SECURITY_TESTING = EvidenceRequirement(
    id            = "req:A.8.29:security_testing_procedure",
    control_ref   = "A.8.29",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Security Testing in Development and Acceptance Procedure",
    trigger_type  = "universal",
    description   = "A.8.29 requires security testing processes to be defined and implemented in the development lifecycle. Evidence is a procedure covering test types, lifecycle gates, acceptance criteria, and defect handling",
    must_contain  = [
        ChecklistItem("item:A.8.29:test_types",    "Test types covered (SAST, DAST, IAST, dependency scanning, manual / penetration testing)", "must", False, "A.8.29 — security testing processes"),
        ChecklistItem("item:A.8.29:lifecycle_gates","Test gates in lifecycle (per-commit, pre-merge, pre-release, post-deployment)", "must", False, "A.8.29 — development life cycle"),
        ChecklistItem("item:A.8.29:acceptance",    "Acceptance criteria (severity thresholds that block release)", "must", False, "A.8.29 — acceptance"),
        ChecklistItem("item:A.8.29:defect_handling","Defect handling (creation, triage, fix, retest)", "must", False, "A.8.29 — implemented"),
        ChecklistItem("item:A.8.29:retesting",     "Retesting after remediation step", "must", False, "A.8.29 — implemented"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.29:pen_test_cadence","Third-party penetration testing cadence (typically annual + on significant change)", "should", False, "Independent assurance"),
        ChecklistItem("item:A.8.29:bug_bounty",    "Bug bounty / responsible disclosure programme", "should", False, "Continuous external testing"),
    ],
)

REQ_A830_OUTSOURCED_DEVELOPMENT = EvidenceRequirement(
    id            = "req:A.8.30:outsourced_development_procedure",
    control_ref   = "A.8.30",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Outsourced Development Governance Procedure",
    trigger_type  = "universal",
    description   = "A.8.30 requires the organization to direct, monitor, and review activities related to outsourced system development. Evidence is a procedure covering security requirements in contracts, code controls, and oversight",
    must_contain  = [
        ChecklistItem("item:A.8.30:contractual_security","Security requirements in development contracts (links to A.5.20)", "must", False, "A.8.30 — direct"),
        ChecklistItem("item:A.8.30:code_ownership","Code ownership, escrow, and intellectual property terms", "must", False, "A.8.30 — direct"),
        ChecklistItem("item:A.8.30:delivered_code_testing","Security testing of delivered code (links to A.8.29)", "must", False, "A.8.30 — review"),
        ChecklistItem("item:A.8.30:source_code_controls","Source code access controls for the outsourcing vendor (links to A.8.4)", "must", False, "A.8.30 — direct"),
        ChecklistItem("item:A.8.30:incident_notification","Incident notification obligation in contract (vendor must notify within agreed window)", "must", False, "A.8.30 — monitor"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.30:maturity_assessment","Vendor security maturity assessment before engagement (links to A.5.19)", "should", False, "Risk-based vendor selection"),
        ChecklistItem("item:A.8.30:review_meetings","Regular review meetings during engagement", "should", False, "Active monitoring"),
    ],
)

REQ_A831_ENVIRONMENT_SEPARATION = EvidenceRequirement(
    id            = "req:A.8.31:environment_separation_procedure",
    control_ref   = "A.8.31",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Development, Test, and Production Environment Separation Procedure",
    trigger_type  = "universal",
    description   = "A.8.31 requires development, testing, and production environments to be separated and secured. Evidence is a procedure stating how environments are separated, what data flows between them, and access controls",
    must_contain  = [
        ChecklistItem("item:A.8.31:distinct_environments","Distinct environments enumerated (dev, test, staging, production) with their purpose", "must", False, "A.8.31 — separated"),
        ChecklistItem("item:A.8.31:network_separation","Network and identity separation between environments", "must", False, "A.8.31 — separated"),
        ChecklistItem("item:A.8.31:data_handling","Data handling rules between environments (no raw production data in dev; links to A.8.33)", "must", False, "A.8.31 — secured"),
        ChecklistItem("item:A.8.31:promotion_process","Promotion / deployment process between environments (links to A.8.32 change management)", "must", False, "A.8.31 — secured"),
        ChecklistItem("item:A.8.31:per_env_access","Access controls per environment (dev access ≠ prod access)", "must", False, "A.8.31 — secured"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.31:ephemeral",   "Ephemeral environments where supported", "should", False, "Modern practice"),
        ChecklistItem("item:A.8.31:iac",         "Infrastructure-as-code for environment reproducibility", "should", False, "Consistency"),
    ],
)

REQ_A832_CHANGE_MANAGEMENT = EvidenceRequirement(
    id            = "req:A.8.32:change_management_procedure",
    control_ref   = "A.8.32",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Change Management Procedure",
    trigger_type  = "universal",
    description   = "A.8.32 requires changes to information processing facilities and information systems to be subject to change management procedures. Evidence is a documented change management procedure",
    must_contain  = [
        ChecklistItem("item:A.8.32:scope",         "Scope of changes covered (which kinds of changes require formal CM)", "must", False, "A.8.32 — changes subject to change management"),
        ChecklistItem("item:A.8.32:approval",      "Change approval workflow (CAB or equivalent)", "must", False, "A.8.32 — change management procedures"),
        ChecklistItem("item:A.8.32:risk_assessment","Risk assessment per change", "must", False, "A.8.32 — change management"),
        ChecklistItem("item:A.8.32:rollback",      "Rollback plan required per change", "must", False, "A.8.32 — change management"),
        ChecklistItem("item:A.8.32:emergency",     "Emergency change provisions with post-hoc review", "must", False, "Operational reality"),
        ChecklistItem("item:A.8.32:pir",           "Post-implementation review for significant changes", "must", False, "Learning loop"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.32:change_windows","Defined change windows for non-emergency changes", "should", False, "Predictability"),
        ChecklistItem("item:A.8.32:ci_integration","CI/CD pipeline integration for low-risk automated changes", "should", False, "Modern velocity"),
    ],
)

REQ_A833_TEST_INFORMATION = EvidenceRequirement(
    id            = "req:A.8.33:test_information_procedure",
    control_ref   = "A.8.33",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Test Information Management Procedure",
    trigger_type  = "universal",
    description   = "A.8.33 requires test information to be selected, protected, and managed appropriately. Evidence is a procedure covering selection, masking, protection, and lifecycle of test data",
    must_contain  = [
        ChecklistItem("item:A.8.33:selection",     "Selection criteria (synthetic preferred; production-derived only when masked)", "must", False, "A.8.33 — appropriately selected"),
        ChecklistItem("item:A.8.33:masking",       "Masking requirements when production-derived data must be used", "must", False, "A.8.33 — protected"),
        ChecklistItem("item:A.8.33:protection",    "Protection equivalent to production where the data warrants it", "must", False, "A.8.33 — protected"),
        ChecklistItem("item:A.8.33:access_controls","Access controls on test data (not all developers see everything)", "must", False, "A.8.33 — managed"),
        ChecklistItem("item:A.8.33:lifecycle",     "Lifecycle (provisioning, refresh, deletion at end of need)", "must", False, "A.8.33 — managed"),
        ChecklistItem("item:A.8.33:pii_constraint","No live PII in lower environments unless masked / pseudonymised", "must", False, "A.8.33 — protected"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.33:synthetic_tooling","Synthetic data generation tooling preferred over masking", "should", False, "Reduces residual risk"),
        ChecklistItem("item:A.8.33:dpia_consideration","DPIA / privacy considerations when PII involved", "should", False, "Privacy compliance"),
    ],
)

REQ_A834_AUDIT_TESTING_PROTECTION = EvidenceRequirement(
    id            = "req:A.8.34:audit_testing_protection_procedure",
    control_ref   = "A.8.34",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Protection of Information Systems During Audit Testing Procedure",
    trigger_type  = "universal",
    description   = "A.8.34 requires audit tests and assurance activities involving operational systems to be planned and agreed between the tester and appropriate management. Evidence is a procedure covering pre-authorization, scope agreement, and impact management",
    must_contain  = [
        ChecklistItem("item:A.8.34:pre_authorisation","Pre-authorisation required before any audit testing on operational systems", "must", False, "A.8.34 — planned and agreed"),
        ChecklistItem("item:A.8.34:scope_agreement","Written scope agreement (what is in scope, what is out)", "must", False, "A.8.34 — agreed"),
        ChecklistItem("item:A.8.34:time_windows", "Time windows agreed (avoid peak business hours, change-freeze periods)", "must", False, "A.8.34 — planned"),
        ChecklistItem("item:A.8.34:rollback",     "Rollback procedure stated for any change introduced during testing", "must", False, "A.8.34 — protection of information systems"),
        ChecklistItem("item:A.8.34:evidence",     "Evidence preservation (logs, results) maintained per legal/regulatory requirements", "must", False, "A.8.34 — assessment of operational systems"),
        ChecklistItem("item:A.8.34:stakeholder_notification","Stakeholder notification (affected teams, on-call, customer if material)", "must", False, "A.8.34 — agreed between the tester and management"),
        ChecklistItem("item:A.8.34:performance_impact","Performance impact considered and limited", "must", False, "A.8.34 — protection"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.34:dedicated_accounts","Dedicated test accounts used (rather than reuse of real users)", "should", False, "Attribution clarity"),
        ChecklistItem("item:A.8.34:meta_audit",   "Audit-of-the-audit logs (record of testing activities)", "should", False, "Accountability of testers"),
    ],
)


# ── ISO 27001 Clauses 4-10 (Phase B, 2026-05-22) ─────────────────────────────
# Management-system clauses. Already curated above: 4.3 (ISMS scope), 5.2 (ISP),
# 6.1.2 (risk assessment process), 6.1.3 (risk treatment process), 9.2 (internal
# audit), 9.3 (management review). The 19 entries below cover the remaining
# leaf-bearing clauses. Pure structural parents (4, 5, 6, 6.1, 7, 8, 9, 10) are
# set to explicit_empty via a Cypher migration after this loader runs.

REQ_C41_CONTEXT_ISSUES = EvidenceRequirement(
    id            = "req:4.1:context_issues_register",
    control_ref   = "4.1",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Internal and External Issues Register",
    trigger_type  = "universal",
    description   = "Clause 4.1 requires the organization to determine external and internal issues relevant to its ISMS purpose and outcomes. Evidence is a documented register of issues, periodically refreshed",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:4.1:internal_issues",    "Internal issues documented (organizational culture, governance, contracts, capabilities, technologies)", "must", False, "Clause 4.1 — internal issues"),
        ChecklistItem("item:4.1:external_issues",    "External issues documented (regulatory, market, threat landscape, social, technology trends)", "must", False, "Clause 4.1 — external issues"),
        ChecklistItem("item:4.1:relevance_to_ismsm","Relevance to the ISMS intended outcomes stated per issue", "must", False, "Clause 4.1 — affect ability to achieve outcomes"),
        ChecklistItem("item:4.1:review_trigger",     "Review trigger (planned interval and significant change)", "must", False, "Implicit currency requirement"),
        ChecklistItem("item:4.1:owner",              "Named owner of the register (typically ISMS Manager)", "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:4.1:framework",          "Framework reference (SWOT, PESTLE, or equivalent)", "should", False, "Repeatable shape"),
        ChecklistItem("item:4.1:risk_link",          "Link from issues to the risk assessment (6.1.2)", "should", False, "Closes the planning loop"),
    ],
)

REQ_C42_INTERESTED_PARTIES = EvidenceRequirement(
    id            = "req:4.2:interested_parties_register",
    control_ref   = "4.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Interested Parties and Requirements Register",
    trigger_type  = "universal",
    description   = "Clause 4.2 requires the organization to determine interested parties relevant to the ISMS and their requirements. Evidence is a register listing parties, their requirements, and which the ISMS will address",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:4.2:parties_listed",   "Interested parties listed (regulators, customers, suppliers, personnel, shareholders, communities)", "must", False, "Clause 4.2 — interested parties relevant"),
        ChecklistItem("item:4.2:requirements",     "Requirements per party documented (legal, regulatory, contractual, business expectations)", "must", False, "Clause 4.2 — relevant requirements"),
        ChecklistItem("item:4.2:addressed",        "Which requirements the ISMS will address (and how)", "must", False, "Clause 4.2 — addressed through the ISMS"),
        ChecklistItem("item:4.2:review_trigger",   "Review trigger (planned interval and significant change)", "must", False, "Implicit currency requirement"),
        ChecklistItem("item:4.2:owner",            "Named owner of the register", "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:4.2:legal_voluntary",  "Distinction between legal/regulatory requirements and voluntary commitments", "should", False, "Risk and priority clarity"),
        ChecklistItem("item:4.2:scope_link",       "Link to ISMS scope (4.3) for traceability", "should", False, "Cross-clause coherence"),
    ],
)

REQ_C44_ISMS = EvidenceRequirement(
    id            = "req:4.4:isms_manual",
    control_ref   = "4.4",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Information Security Management System Manual / Charter",
    trigger_type  = "universal",
    description   = "Clause 4.4 requires the organization to establish, implement, maintain, and continually improve an ISMS including its processes and their interactions. Evidence is the ISMS manual / charter document describing the system as a whole",
    must_contain  = [
        ChecklistItem("item:4.4:scope_ref",         "Reference to ISMS scope statement (4.3)", "must", False, "Clause 4.4 — establish"),
        ChecklistItem("item:4.4:processes",         "ISMS processes enumerated (planning, operation, evaluation, improvement)", "must", False, "Clause 4.4 — processes needed"),
        ChecklistItem("item:4.4:interactions",      "Interactions between processes described (inputs, outputs, sequence)", "must", False, "Clause 4.4 — their interactions"),
        ChecklistItem("item:4.4:governance",        "Governance structure (ownership, decision rights, escalation)", "must", False, "Clause 4.4 — maintain"),
        ChecklistItem("item:4.4:improvement_intent","Continual improvement statement and mechanism", "must", False, "Clause 4.4 — continually improve"),
    ],
    should_contain= [
        ChecklistItem("item:4.4:process_map",       "Process map or diagram showing interactions", "should", False, "Audit clarity"),
        ChecklistItem("item:4.4:references_iso",    "References ISO 27001:2022 clause structure", "should", False, "Auditor navigation"),
    ],
)

REQ_C51_LEADERSHIP_COMMITMENT = EvidenceRequirement(
    id            = "req:5.1:leadership_commitment_directive",
    control_ref   = "5.1",
    standard_id   = "ISO27001:2022",
    evidence_type = "management_directive",
    title         = "Top Management Leadership and Commitment Statement",
    trigger_type  = "universal",
    description   = "Clause 5.1 requires top management to demonstrate leadership and commitment. Evidence is a signed directive or letter from top management addressing all the demonstrations listed in clause 5.1 a-h",
    must_contain  = [
        ChecklistItem("item:5.1:policy_objectives_strategy","Policy and objectives compatible with strategic direction", "must", False, "Clause 5.1 a)"),
        ChecklistItem("item:5.1:integration",       "ISMS integrated into business processes", "must", False, "Clause 5.1 b)"),
        ChecklistItem("item:5.1:resources",         "Resources for the ISMS made available", "must", False, "Clause 5.1 c)"),
        ChecklistItem("item:5.1:importance_communicated","Importance of effective ISMS and conformance communicated", "must", False, "Clause 5.1 d)"),
        ChecklistItem("item:5.1:outcomes_achieved", "Ensuring the ISMS achieves its intended outcomes", "must", False, "Clause 5.1 e)"),
        ChecklistItem("item:5.1:direct_and_support","Directing and supporting persons contributing to ISMS effectiveness", "must", False, "Clause 5.1 f)"),
        ChecklistItem("item:5.1:continual_improvement","Promoting continual improvement", "must", False, "Clause 5.1 g)"),
        ChecklistItem("item:5.1:support_other_mgmt","Supporting other relevant management roles in demonstrating their leadership", "must", False, "Clause 5.1 h)"),
        ChecklistItem("item:5.1:signed_dated",      "Signed by top management with date", "must", False, "Authenticity"),
    ],
    should_contain= [
        ChecklistItem("item:5.1:periodic_reaffirm","Periodic reaffirmation (e.g. on each annual planning cycle)", "should", False, "Currency"),
    ],
)

REQ_C53_ISMS_ROLES = EvidenceRequirement(
    id            = "req:5.3:isms_roles_authorities",
    control_ref   = "5.3",
    standard_id   = "ISO27001:2022",
    evidence_type = "responsibility_matrix",
    title         = "ISMS Roles, Responsibilities and Authorities",
    trigger_type  = "universal",
    description   = "Clause 5.3 requires top management to ensure ISMS-related responsibilities and authorities are assigned and communicated. Evidence is a responsibility matrix at the management-system level (distinct from A.5.2 operational roles)",
    must_contain  = [
        ChecklistItem("item:5.3:isms_conformance",  "Role assigned for ensuring the ISMS conforms to ISO 27001:2022", "must", False, "Clause 5.3 a)"),
        ChecklistItem("item:5.3:performance_reporting","Role assigned for reporting on ISMS performance to top management", "must", False, "Clause 5.3 b)"),
        ChecklistItem("item:5.3:authorities_assigned","Authorities assigned for each role (decision rights, sign-off authority)", "must", False, "Clause 5.3 — authorities assigned"),
        ChecklistItem("item:5.3:communicated",      "Roles communicated within the organization", "must", False, "Clause 5.3 — communicated"),
    ],
    should_contain= [
        ChecklistItem("item:5.3:org_chart_link",    "Integration with the organizational chart", "should", False, "Visibility"),
        ChecklistItem("item:5.3:a52_consistency",   "Consistency with A.5.2 operational security roles", "should", False, "Cross-control coherence"),
    ],
)

REQ_C611_RISK_OPPORTUNITY_PLANNING = EvidenceRequirement(
    id            = "req:6.1.1:risk_opportunity_planning",
    control_ref   = "6.1.1",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "ISMS Risk and Opportunity Planning Procedure",
    trigger_type  = "universal",
    description   = "Clause 6.1.1 requires the organization to consider issues (4.1) and requirements (4.2) and determine risks and opportunities. Evidence is a planning procedure linking inputs to actions",
    must_contain  = [
        ChecklistItem("item:6.1.1:issues_input",     "Issues from 4.1 considered as planning input", "must", False, "Clause 6.1.1 — issues referred to in 4.1"),
        ChecklistItem("item:6.1.1:requirements_input","Requirements from 4.2 considered as planning input", "must", False, "Clause 6.1.1 — requirements referred to in 4.2"),
        ChecklistItem("item:6.1.1:risks_identified", "Risks identified that need to be addressed for ISMS to achieve intended outcomes", "must", False, "Clause 6.1.1 — risks that need to be addressed"),
        ChecklistItem("item:6.1.1:opportunities",    "Opportunities identified to enhance ISMS effectiveness", "must", False, "Clause 6.1.1 — opportunities"),
        ChecklistItem("item:6.1.1:actions_planned",  "Actions planned to address risks and opportunities", "must", False, "Clause 6.1.1 — actions to address"),
        ChecklistItem("item:6.1.1:integration",      "Integration of planned actions into ISMS processes", "must", False, "Clause 6.1.1 — integrated into ISMS processes"),
        ChecklistItem("item:6.1.1:evaluation",       "Evaluation of effectiveness of planned actions", "must", False, "Clause 6.1.1 — evaluate effectiveness"),
    ],
    should_contain= [
        ChecklistItem("item:6.1.1:risk_assessment_link","Link to risk assessment process (6.1.2)", "should", False, "Closes the planning loop"),
    ],
)

REQ_C62_SECURITY_OBJECTIVES = EvidenceRequirement(
    id            = "req:6.2:security_objectives_register",
    control_ref   = "6.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Information Security Objectives Register",
    trigger_type  = "universal",
    description   = "Clause 6.2 requires information security objectives to be established at relevant functions and levels. Evidence is a documented register of objectives, owners, measurement, and refresh cycle",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:6.2:objectives_stated", "Objectives stated at relevant functions and levels", "must", False, "Clause 6.2 — established at relevant functions and levels"),
        ChecklistItem("item:6.2:consistent_with_policy","Consistency with the InfoSec policy (5.2)", "must", False, "Clause 6.2 a)"),
        ChecklistItem("item:6.2:measurable",        "Measurable where practicable (KPI defined)", "must", False, "Clause 6.2 b)"),
        ChecklistItem("item:6.2:requirements_considered","Applicable information security requirements considered, plus results of risk assessment / treatment", "must", False, "Clause 6.2 c)"),
        ChecklistItem("item:6.2:communicated",      "Objectives communicated to relevant personnel", "must", False, "Clause 6.2 d)"),
        ChecklistItem("item:6.2:updated",           "Updated as appropriate (review trigger stated)", "must", False, "Clause 6.2 e)"),
        ChecklistItem("item:6.2:planning",          "Planning to achieve objectives (what, resources, who, when, evaluation)", "must", False, "Clause 6.2 planning"),
    ],
    should_contain= [
        ChecklistItem("item:6.2:target_dates",      "Target dates per objective", "should", False, "Concrete commitment"),
        ChecklistItem("item:6.2:kpi_dashboard",     "KPI dashboard linked", "should", False, "Visibility"),
    ],
)

REQ_C63_PLANNING_OF_CHANGES = EvidenceRequirement(
    id            = "req:6.3:isms_change_planning",
    control_ref   = "6.3",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Planning of Changes to the ISMS Procedure",
    trigger_type  = "universal",
    description   = "Clause 6.3 requires changes to the ISMS to be carried out in a planned manner. Evidence is a procedure for managing ISMS-level changes (distinct from A.8.32 technical change management)",
    must_contain  = [
        ChecklistItem("item:6.3:change_identification","Identification trigger for ISMS-level changes (scope, policy, risk criteria, structural)", "must", False, "Clause 6.3 — determines the need for changes"),
        ChecklistItem("item:6.3:planning_required", "Planning required before significant changes (purpose, consequences, integrity considerations)", "must", False, "Clause 6.3 — planned manner"),
        ChecklistItem("item:6.3:impact_consideration","Consideration of impact on ISMS effectiveness", "must", False, "Clause 6.3 — planned manner"),
        ChecklistItem("item:6.3:approval",          "Approval authority before implementation", "must", False, "Clause 6.3 — planned"),
    ],
    should_contain= [
        ChecklistItem("item:6.3:a832_link",         "Link to A.8.32 for technical change management of the underlying ICT", "should", False, "Cross-control coherence"),
    ],
)

REQ_C71_RESOURCES = EvidenceRequirement(
    id            = "req:7.1:isms_resources_record",
    control_ref   = "7.1",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "ISMS Resource Allocation Record",
    trigger_type  = "universal",
    description   = "Clause 7.1 requires the organization to determine and provide resources needed for ISMS establishment, implementation, maintenance, and improvement. Evidence is a record showing financial, human, infrastructure, and technology resources committed",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:7.1:financial",    "Financial resources allocated (budget for ISMS activities)", "must", False, "Clause 7.1 — resources needed"),
        ChecklistItem("item:7.1:human",        "Human resources assigned (headcount, roles, time allocation)", "must", False, "Clause 7.1 — resources"),
        ChecklistItem("item:7.1:infrastructure","Infrastructure provided (premises, equipment, transport)", "must", False, "Clause 7.1 — resources"),
        ChecklistItem("item:7.1:technology",   "Technology platforms supporting the ISMS (GRC tool, document repo, training platform)", "must", False, "Clause 7.1 — resources"),
    ],
    should_contain= [
        ChecklistItem("item:7.1:budget_link",  "Reference to organization budget where ISMS spend appears", "should", False, "Visibility"),
    ],
)

REQ_C72_COMPETENCE = EvidenceRequirement(
    id            = "req:7.2:competence_record",
    control_ref   = "7.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "ISMS Competence Record",
    trigger_type  = "universal",
    description   = "Clause 7.2 requires the organization to determine necessary competence of persons whose work affects ISMS performance and ensure they are competent. Evidence is a competence record mapping role → required competence → actual competence",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:7.2:required_competence","Required competence defined per role affecting ISMS performance", "must", False, "Clause 7.2 a)"),
        ChecklistItem("item:7.2:basis_of_competence","Basis of competence (education, training, experience) recorded per person", "must", False, "Clause 7.2 b)"),
        ChecklistItem("item:7.2:gap_actions",      "Actions taken to close competence gaps (training, hiring, mentoring) where applicable", "must", False, "Clause 7.2 c)"),
        ChecklistItem("item:7.2:effectiveness",    "Evaluation that competence actions were effective", "must", False, "Clause 7.2 c)"),
        ChecklistItem("item:7.2:documented",       "Documented information retained as evidence of competence", "must", False, "Clause 7.2 d)"),
    ],
    should_contain= [
        ChecklistItem("item:7.2:training_matrix",  "Training matrix per role", "should", False, "Operational view"),
    ],
)

REQ_C73_AWARENESS = EvidenceRequirement(
    id            = "req:7.3:isms_awareness_evidence",
    control_ref   = "7.3",
    standard_id   = "ISO27001:2022",
    evidence_type = "training_programme",
    title         = "ISMS Awareness Evidence",
    trigger_type  = "universal",
    description   = "Clause 7.3 requires persons doing work under the organization's control to be aware of the InfoSec policy, their contribution to ISMS effectiveness, and consequences of nonconformity. Evidence is awareness material plus completion / acknowledgement records (distinct from A.6.3 operational awareness training)",
    must_contain  = [
        ChecklistItem("item:7.3:policy_awareness", "Awareness of the InfoSec policy", "must", False, "Clause 7.3 a)"),
        ChecklistItem("item:7.3:contribution",     "Awareness of contribution to ISMS effectiveness (including benefits of improved performance)", "must", False, "Clause 7.3 b)"),
        ChecklistItem("item:7.3:nonconformity_consequences","Awareness of consequences of not conforming to ISMS requirements", "must", False, "Clause 7.3 c)"),
        ChecklistItem("item:7.3:completion_records","Records of completion / acknowledgement per person", "must", False, "Evidence preservation"),
    ],
    should_contain= [
        ChecklistItem("item:7.3:a63_link",         "Integration with A.6.3 operational awareness training programme", "should", False, "Cross-control coherence"),
    ],
)

REQ_C74_COMMUNICATION = EvidenceRequirement(
    id            = "req:7.4:isms_communication_procedure",
    control_ref   = "7.4",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "ISMS Communication Procedure",
    trigger_type  = "universal",
    description   = "Clause 7.4 requires the organization to determine the need for internal and external ISMS communications. Evidence is a procedure stating what, when, with whom, how, and by whom",
    must_contain  = [
        ChecklistItem("item:7.4:what",          "What is communicated (policy, objectives, performance, incidents, changes)", "must", False, "Clause 7.4 a)"),
        ChecklistItem("item:7.4:when",          "When communication occurs (planned cadences and event triggers)", "must", False, "Clause 7.4 b)"),
        ChecklistItem("item:7.4:with_whom",     "With whom (internal audiences and external interested parties)", "must", False, "Clause 7.4 c)"),
        ChecklistItem("item:7.4:how",           "How (channels, formats, escalation paths)", "must", False, "Clause 7.4 d)"),
        ChecklistItem("item:7.4:responsibility","Who is responsible for each communication", "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:7.4:plan",          "Communication plan document referenced", "should", False, "Concrete artefact"),
    ],
)

REQ_C75_DOCUMENTED_INFORMATION = EvidenceRequirement(
    id            = "req:7.5:document_control_policy",
    control_ref   = "7.5",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Documented Information Control Policy",
    trigger_type  = "universal",
    description   = "Clause 7.5 requires the ISMS to include documented information required by ISO 27001 and information determined by the organization to be necessary. Evidence is a document control policy covering creation, updating, control, retention, and accessibility",
    must_contain  = [
        ChecklistItem("item:7.5:iso_required_docs","ISO 27001:2022 required documented information enumerated", "must", False, "Clause 7.5 — documented information required by this document"),
        ChecklistItem("item:7.5:org_defined",     "Organization-determined necessary documented information identified", "must", False, "Clause 7.5 — necessary for the effectiveness"),
        ChecklistItem("item:7.5:creation_update", "Creation and update process (identification, format, review, approval)", "must", False, "Clause 7.5.2 — creating and updating"),
        ChecklistItem("item:7.5:control",         "Control of documented information (distribution, access, retrieval, retention, disposition)", "must", False, "Clause 7.5.3 — control of documented information"),
        ChecklistItem("item:7.5:legibility",      "Protection from loss of legibility, loss of integrity, unauthorised use", "must", False, "Clause 7.5.3 — protected"),
        ChecklistItem("item:7.5:external_docs",   "Control of documented information of external origin determined necessary", "must", False, "Clause 7.5.3 — control external origin"),
    ],
    should_contain= [
        ChecklistItem("item:7.5:format_standards","Format standards for ISMS documents (templates, naming)", "should", False, "Consistency"),
        ChecklistItem("item:7.5:accessibility",   "Accessibility provisions for personnel needing documents", "should", False, "Usability"),
    ],
)

REQ_C81_OPERATIONAL_PLANNING = EvidenceRequirement(
    id            = "req:8.1:operational_planning_procedure",
    control_ref   = "8.1",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Operational Planning and Control Procedure",
    trigger_type  = "universal",
    description   = "Clause 8.1 requires the organization to plan, implement, and control processes to meet requirements and implement Clause 6 actions. Evidence is an operational planning procedure",
    must_contain  = [
        ChecklistItem("item:8.1:criteria_established","Criteria established for ISMS-relevant processes", "must", False, "Clause 8.1 — establishing criteria"),
        ChecklistItem("item:8.1:controls_implemented","Controls implemented per the criteria", "must", False, "Clause 8.1 — implementing control"),
        ChecklistItem("item:8.1:documented_info",     "Documented information retained as evidence the processes were carried out as planned", "must", False, "Clause 8.1 — documented information"),
        ChecklistItem("item:8.1:outsourced_control",  "Outsourced processes determined and controlled (links to A.5.19/A.5.20)", "must", False, "Clause 8.1 — outsourced processes"),
        ChecklistItem("item:8.1:changes_managed",     "Changes to planned processes managed (link to 6.3)", "must", False, "Clause 8.1 — change control"),
    ],
    should_contain= [
        ChecklistItem("item:8.1:c6_action_link",     "Traceability from Clause 6 actions to operational implementation", "should", False, "Planning-to-doing"),
    ],
)

REQ_C82_OPERATIONAL_RISK_ASSESSMENT = EvidenceRequirement(
    id            = "req:8.2:operational_risk_assessment_record",
    control_ref   = "8.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "risk_assessment_record",
    title         = "Operational Risk Assessment Records",
    trigger_type  = "universal",
    description   = "Clause 8.2 requires risk assessments to be performed at planned intervals or on significant change, using the criteria from 6.1.2. Evidence is a record (or set of records) of completed assessments with dates",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:8.2:planned_interval",     "Planned interval observed (typically annual or more frequent for higher-risk environments)", "must", False, "Clause 8.2 — planned intervals"),
        ChecklistItem("item:8.2:significant_change",   "Significant-change trigger for ad-hoc reassessments documented", "must", False, "Clause 8.2 — when significant changes are proposed or occur"),
        ChecklistItem("item:8.2:last_assessment",      "Last assessment date recorded", "must", False, "Currency"),
        ChecklistItem("item:8.2:criteria_applied",     "Criteria from 6.1.2 a) applied during assessment", "must", False, "Clause 8.2 — criteria established in 6.1.2 a"),
        ChecklistItem("item:8.2:results_documented",   "Results documented and retained", "must", False, "Clause 8.2 — retain documented information"),
    ],
    should_contain= [
        ChecklistItem("item:8.2:comparison_to_prior",  "Comparison or movement from prior assessment", "should", False, "Trend visibility"),
    ],
)

REQ_C83_OPERATIONAL_RISK_TREATMENT = EvidenceRequirement(
    id            = "req:8.3:operational_risk_treatment_record",
    control_ref   = "8.3",
    standard_id   = "ISO27001:2022",
    evidence_type = "risk_treatment_record",
    title         = "Operational Risk Treatment Records",
    trigger_type  = "universal",
    description   = "Clause 8.3 requires the organization to implement the risk treatment plan and retain documented information of the results. Evidence is the treatment plan execution record",
    freshness_days = 180,
    must_contain  = [
        ChecklistItem("item:8.3:plan_implemented",  "Treatment plan from 6.1.3 being implemented (status per item)", "must", False, "Clause 8.3 — implement the information security risk treatment plan"),
        ChecklistItem("item:8.3:implementation_status","Implementation status per treatment item (planned, in-progress, complete, deferred)", "must", False, "Clause 8.3 — implementation"),
        ChecklistItem("item:8.3:residual_risk",     "Residual risk recorded after treatment", "must", False, "Clause 8.3 — results"),
        ChecklistItem("item:8.3:retention",         "Documented information of results retained", "must", False, "Clause 8.3 — retain documented information of the results"),
    ],
    should_contain= [
        ChecklistItem("item:8.3:soa_link",          "Link to Statement of Applicability for control selection rationale", "should", False, "Audit traceability"),
    ],
)

REQ_C91_MONITORING_MEASUREMENT = EvidenceRequirement(
    id            = "req:9.1:monitoring_measurement_procedure",
    control_ref   = "9.1",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "ISMS Monitoring, Measurement, Analysis and Evaluation Procedure",
    trigger_type  = "universal",
    description   = "Clause 9.1 requires the organization to determine what is monitored and measured, by what methods, when, who, and how analysed. Evidence is a procedure plus the resulting measurement and analysis records",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:9.1:what_monitored",  "What is monitored and measured (ISMS processes and security controls)", "must", False, "Clause 9.1 a)"),
        ChecklistItem("item:9.1:methods",         "Methods for monitoring, measurement, analysis, and evaluation", "must", False, "Clause 9.1 b)"),
        ChecklistItem("item:9.1:timing_measure",  "When monitoring and measurement is performed", "must", False, "Clause 9.1 c)"),
        ChecklistItem("item:9.1:who_measure",     "Who shall monitor and measure", "must", False, "Clause 9.1 d)"),
        ChecklistItem("item:9.1:timing_analyse",  "When results are analysed and evaluated", "must", False, "Clause 9.1 e)"),
        ChecklistItem("item:9.1:who_analyse",     "Who shall analyse and evaluate the results", "must", False, "Clause 9.1 f)"),
        ChecklistItem("item:9.1:retained",        "Documented information retained as evidence of monitoring and measurement results", "must", False, "Clause 9.1 — retained"),
    ],
    should_contain= [
        ChecklistItem("item:9.1:dashboard",       "KPI dashboard or report catalogue", "should", False, "Visibility"),
    ],
)

REQ_C101_CONTINUAL_IMPROVEMENT = EvidenceRequirement(
    id            = "req:10.1:continual_improvement_procedure",
    control_ref   = "10.1",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Continual Improvement Procedure",
    trigger_type  = "universal",
    description   = "Clause 10.1 requires the organization to continually improve the suitability, adequacy, and effectiveness of the ISMS. Evidence is a continual improvement procedure with triggers, targets, and tracking",
    must_contain  = [
        ChecklistItem("item:10.1:triggers",     "Improvement triggers (audit findings, nonconformities, opportunities, performance gaps, interested-party feedback)", "must", False, "Clause 10.1 — continually improve"),
        ChecklistItem("item:10.1:dimensions",   "Improvement targets cover suitability, adequacy, and effectiveness", "must", False, "Clause 10.1 — suitability, adequacy and effectiveness"),
        ChecklistItem("item:10.1:implementation","Implementation steps for improvement actions (owners, dates, resources)", "must", False, "Clause 10.1 — continually improve"),
        ChecklistItem("item:10.1:tracking",     "Tracking of improvement actions to closure with effectiveness check", "must", False, "Clause 10.1 — continually improve"),
    ],
    should_contain= [
        ChecklistItem("item:10.1:mgmt_review_link","Link to management review (9.3) outputs as a primary trigger", "should", False, "Common driver"),
    ],
)

REQ_C102_NONCONFORMITY_CA = EvidenceRequirement(
    id            = "req:10.2:nonconformity_corrective_action",
    control_ref   = "10.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Nonconformity and Corrective Action Procedure",
    trigger_type  = "universal",
    description   = "Clause 10.2 requires the organization to react to nonconformity, evaluate causes, implement corrective action, review effectiveness, and update the ISMS if needed. Evidence is a documented NC/CA procedure",
    must_contain  = [
        ChecklistItem("item:10.2:react",         "React to the nonconformity — control, correct, and deal with consequences", "must", False, "Clause 10.2 a)"),
        ChecklistItem("item:10.2:root_cause",    "Evaluate the need for action to eliminate causes (root cause analysis)", "must", False, "Clause 10.2 b)"),
        ChecklistItem("item:10.2:implementation","Implement corrective action", "must", False, "Clause 10.2 c)"),
        ChecklistItem("item:10.2:effectiveness", "Review effectiveness of corrective action taken", "must", False, "Clause 10.2 d)"),
        ChecklistItem("item:10.2:isms_update",   "Make changes to the ISMS where appropriate", "must", False, "Clause 10.2 e)"),
        ChecklistItem("item:10.2:document",      "Documented information retained on the nature of NC, actions taken, and results", "must", False, "Clause 10.2 — documented information"),
    ],
    should_contain= [
        ChecklistItem("item:10.2:incident_link", "Link to A.5.26 (incident response) and A.5.27 (lessons learned)", "should", False, "Operational coherence"),
    ],
)


# ── Derived specs ─────────────────────────────────────────────────────────────
# Cross-control derivation. Each DerivedSpec consumes the verdict of other
# controls' FulfilmentSpecs and composes them per its op. Used when the
# deriving framework's article is principally satisfied by the implementation
# of source-framework controls (e.g. GDPR Art.32 ← ISO 27001 Annex A).

SPEC_ART_32 = DerivedSpec(
    spec_id      = "spec:GDPR:2016/679:Art.32",
    control_ref  = "Art.32",
    standard_id  = "GDPR:2016/679",
    op           = "ALL",
    title        = "Security of processing (derived via ISO 27001)",
    description  = (
        "Art.32 mandates 'appropriate technical and organisational measures' "
        "for the security of processing. Those measures are implemented by "
        "the ISO 27001 Annex A controls listed here, with one direct-evidence "
        "requirement (Art.32.1.d periodic resilience testing) that ISO doesn't "
        "capture as a discrete artifact."
    ),
    # GDPR Art.32 applies whenever a tenant processes personal data — controller
    # or processor. Until ClientFacts gain a 'is_controller_or_processor' boolean
    # we treat presence of personal data as the gate; the engine resolves this
    # against the ClientFacts catalog.
    applies_when = None,  # TODO: tighten to 'is_controller OR is_processor' when facts exist
    derives_from = [
        DerivedFrom(
            target_control_ref = "A.8.24",
            target_standard_id = "ISO27001:2022",
            role               = "cryptography",
            title              = "Pseudonymisation and encryption of personal data (Art.32.1.a)",
            # Restrict to the items that bear on Art.32 — exclude algorithm
            # governance and roles, which are ISO-specific. The personal_data
            # and pii_keys items are explicitly GDPR-aligned in the A.8.24
            # checklist; the at_rest/in_transit items are the substantive
            # encryption properties Art.32.1.a requires.
            scope_items = [
                "item:A.8.24:personal_data",
                "item:A.8.24:pii_keys",
                "item:A.8.24:at_rest",
                "item:A.8.24:in_transit",
            ],
        ),
        DerivedFrom(
            target_control_ref = "A.5.18",
            target_standard_id = "ISO27001:2022",
            role               = "access_rights",
            title              = "Confidentiality via access control (Art.32.1.b)",
            # Whole control — Art.32.1.b confidentiality is satisfied by the
            # full access-rights management process. No item-level scope.
        ),
        DerivedFrom(
            target_control_ref = "A.5.24",
            target_standard_id = "ISO27001:2022",
            role               = "incident_response",
            title              = "Resilience to unlawful destruction/loss/alteration/disclosure (Art.32.2)",
        ),
        DerivedFrom(
            target_control_ref = "A.5.30",
            target_standard_id = "ISO27001:2022",
            role               = "ict_continuity",
            title              = "Availability and resilience via ICT continuity (Art.32.1.b/c)",
        ),
        DerivedFrom(
            target_control_ref = "A.8.13",
            target_standard_id = "ISO27001:2022",
            role               = "backup",
            title              = "Restore availability in timely manner (Art.32.1.c)",
        ),
    ],
    direct_evidence = [
        EvidenceRequirement(
            id            = "req:Art.32:resilience_test",
            control_ref   = "Art.32",
            standard_id   = "GDPR:2016/679",
            evidence_type = "test_log",
            title         = "Periodic resilience and restoration test record",
            trigger_type  = "universal",
            description   = (
                "Art.32.1.d requires a process for regularly testing, assessing "
                "and evaluating the effectiveness of technical and organisational "
                "measures for ensuring the security of processing."
            ),
            freshness_days = 365,
            must_contain   = [
                ChecklistItem(
                    "item:Art.32:resilience_test_scope",
                    "Test scope covers confidentiality, integrity, availability and resilience",
                    "must", True, "Art.32.1.d",
                ),
                ChecklistItem(
                    "item:Art.32:resilience_test_recent",
                    "Test executed within the freshness window (last 12 months)",
                    "must", True, "Art.32.1.d — 'regularly'",
                ),
                ChecklistItem(
                    "item:Art.32:resilience_test_findings",
                    "Findings recorded and remediated or accepted",
                    "must", True, "Art.32.1.d evaluation requirement",
                ),
            ],
            should_contain = [
                ChecklistItem(
                    "item:Art.32:resilience_test_independent",
                    "Test conducted or reviewed by an independent party",
                    "should", True, "Best practice for credibility",
                ),
            ],
        ),
    ],
)


SPEC_ART_25 = DerivedSpec(
    spec_id      = "spec:GDPR:2016/679:Art.25",
    control_ref  = "Art.25",
    standard_id  = "GDPR:2016/679",
    op           = "ALL",
    title        = "Data protection by design and by default (derived via ISO 27001)",
    description  = (
        "Art.25 requires data protection to be integrated into systems and "
        "processes from the outset (Art.25.1) and to default to processing "
        "only the minimum personal data necessary (Art.25.2). Most of this "
        "is captured by ISO 27001 controls that establish security at design "
        "time, plus a direct-evidence requirement (Art.25.2 privacy-default "
        "configuration record) that ISO doesn't capture as a discrete artifact."
    ),
    # Art.25 binds controllers. We don't yet have an 'is_controller' ClientFact;
    # processors implementing on behalf of controllers carry the same artefacts
    # through their DPA, so we leave applies_when open until facts gain the
    # controller/processor flag. See [[posture-engine-alignment-plan-2026-05-22]].
    applies_when = None,  # TODO: tighten to 'is_controller' when ClientFacts catalog supports it
    derives_from = [
        DerivedFrom(
            target_control_ref = "A.5.8",
            target_standard_id = "ISO27001:2022",
            role               = "design_time_integration",
            title              = "Security/privacy integrated into project management (Art.25.1)",
            # Whole control — A.5.8's security gates at initiation, requirements
            # capture and pre-go-live assessment ARE the design-time integration
            # mechanism Art.25.1 requires when systems are built or procured.
        ),
        DerivedFrom(
            target_control_ref = "A.8.27",
            target_standard_id = "ISO27001:2022",
            role               = "architecture_principles",
            title              = "Secure system architecture and engineering principles (Art.25.1)",
            # Whole control — Art.25.1 requires effective implementation of
            # data-protection principles; A.8.27's defense-in-depth, least
            # privilege, fail-safe defaults and complete-mediation principles
            # are the engineering substrate for that effectiveness.
        ),
        DerivedFrom(
            target_control_ref = "A.8.25",
            target_standard_id = "ISO27001:2022",
            role               = "secure_sdlc",
            title              = "Privacy by design in the development lifecycle (Art.25.1)",
            # A.8.25 is profile_fact (only when the tenant develops software).
            # For non-developer tenants this edge short-circuits via the target
            # spec's applies_when — Art.25.1 still binds them but through
            # procurement (A.5.8 + A.5.34) rather than internal development.
        ),
        DerivedFrom(
            target_control_ref = "A.8.11",
            target_standard_id = "ISO27001:2022",
            role               = "pseudonymisation",
            title              = "Pseudonymisation as a design-time safeguard (Art.25.1)",
            # Art.25.1 explicitly names pseudonymisation as an example design
            # measure. Restrict to the items that bear on the design-measure
            # angle — masking scope, techniques, and explicit personal-data
            # coverage. Roles, testing and exceptions are governance and not
            # load-bearing for Art.25.1's design obligation.
            scope_items = [
                "item:A.8.11:scope",
                "item:A.8.11:techniques",
                "item:A.8.11:personal_data",
            ],
        ),
        DerivedFrom(
            target_control_ref = "A.5.34",
            target_standard_id = "ISO27001:2022",
            role               = "privacy_policy",
            title              = "Privacy and PII protection requirements (Art.25.1/.2)",
            # Restrict to the items that anchor PbD/PbDefault — applicable laws
            # (GDPR identified), PII inventory (what to protect), retention &
            # minimisation (Art.25.2 storage period default), and the link to
            # security controls (Art.25.1 design integration). Lawful basis,
            # data subject rights, breach handling and DPO role are governance
            # adjacents covered by other articles, not Art.25.
            scope_items = [
                "item:A.5.34:applicable_laws",
                "item:A.5.34:pii_inventory",
                "item:A.5.34:retention_minimisation",
                "item:A.5.34:security_controls_ref",
            ],
        ),
        DerivedFrom(
            target_control_ref = "A.8.10",
            target_standard_id = "ISO27001:2022",
            role               = "deletion_by_default",
            title              = "Storage period bounded by retention triggers (Art.25.2)",
            # Whole control — Art.25.2's "period of storage" default is met
            # when the tenant has retention triggers that cause deletion when
            # data is no longer needed, including in backups (item:A.8.10:scope_systems).
        ),
    ],
    direct_evidence = [
        EvidenceRequirement(
            id            = "req:Art.25:default_settings_record",
            control_ref   = "Art.25",
            standard_id   = "GDPR:2016/679",
            evidence_type = "configuration_record",
            title         = "Privacy-default configuration record (Art.25.2)",
            trigger_type  = "universal",
            description   = (
                "Art.25.2 requires that, by default, only personal data which "
                "are necessary for each specific purpose are processed. This is "
                "a system property — a record listing the personal-data systems "
                "and confirming that their default settings minimise the amount, "
                "extent, storage period, and accessibility of personal data. "
                "ISO 27001 does not require this as a discrete artifact; "
                "Art.25.2 does."
            ),
            freshness_days = 365,
            must_contain   = [
                ChecklistItem(
                    "item:Art.25:default_systems_inventoried",
                    "Personal-data systems inventoried (links to Art.30 records)",
                    "must", True, "Art.25.2 — scope of obligation",
                ),
                ChecklistItem(
                    "item:Art.25:default_amount",
                    "Default collection minimises the amount of personal data per purpose",
                    "must", True, "Art.25.2 — amount of personal data collected",
                ),
                ChecklistItem(
                    "item:Art.25:default_extent",
                    "Default processing minimises the extent of processing per purpose",
                    "must", True, "Art.25.2 — extent of their processing",
                ),
                ChecklistItem(
                    "item:Art.25:default_storage",
                    "Default storage period set to the minimum necessary per purpose",
                    "must", True, "Art.25.2 — period of their storage",
                ),
                ChecklistItem(
                    "item:Art.25:default_accessibility",
                    "Default accessibility limited — data not made accessible to indefinite recipients without intervention",
                    "must", True, "Art.25.2 — accessibility",
                ),
            ],
            should_contain = [
                ChecklistItem(
                    "item:Art.25:default_exception_register",
                    "Exception register for higher-than-default settings with documented justification",
                    "should", True, "Demonstrates accountability",
                ),
                ChecklistItem(
                    "item:Art.25:default_review_dpia_link",
                    "Reference to DPIA process for changes to defaults that increase risk",
                    "should", True, "Art.35 linkage",
                ),
            ],
        ),
    ],
)


SPEC_ART_5_1_F = DerivedSpec(
    spec_id      = "spec:GDPR:2016/679:Art.5.1.f",
    control_ref  = "Art.5.1.f",
    standard_id  = "GDPR:2016/679",
    op           = "ALL",
    title        = "Integrity and confidentiality (derived via Art.32)",
    description  = (
        "Art.5.1.f is the GDPR principle that personal data shall be "
        "processed in a manner ensuring appropriate security — protection "
        "against unauthorised or unlawful processing and against accidental "
        "loss, destruction, damage, using appropriate technical or "
        "organisational measures. Art.32 is the dedicated operational "
        "article that implements this principle in detail (state of the "
        "art measures, pseudonymisation/encryption, CIA + resilience, "
        "restoration, periodic testing). Rather than duplicating Art.32's "
        "ISO 27001 derivations, this spec resolves transitively through "
        "Art.32; if Art.32 complies, Art.5.1.f complies."
    ),
    # Same gate as Art.32 — until ClientFacts catalog gains a controller flag,
    # leave open. See [[posture-engine-alignment-plan-2026-05-22]].
    applies_when = None,  # TODO: tighten to 'is_controller' when ClientFacts catalog supports it
    derives_from = [
        DerivedFrom(
            target_control_ref = "Art.32",
            target_standard_id = "GDPR:2016/679",
            role               = "security_of_processing",
            title              = "Operational T&O measures (Art.32) implement Art.5.1.f",
            # Single recursive derivation — Art.32 IS the operationalisation
            # of Art.5.1.f. Engine resolves Art.32 transitively through its
            # five ISO 27001 dependencies + Art.32.1.d resilience test leaf.
            # Cycle guard at fulfilment_engine.evaluate_spec prevents loops.
            #
            # "Unauthorised or unlawful processing" in Art.5.1.f means
            # breaches of integrity/confidentiality (e.g. unauthorised
            # access), not Art.6 legal-basis violations — so Art.6 is not
            # part of this derivation. Likewise Art.25 (design-time) covers
            # a different angle than Art.5.1.f's operational ask.
        ),
    ],
)


SPEC_ART_24 = DerivedSpec(
    spec_id      = "spec:GDPR:2016/679:Art.24",
    control_ref  = "Art.24",
    standard_id  = "GDPR:2016/679",
    op           = "ALL",
    title        = "Responsibility of the controller — accountability (derived via ISO 27001)",
    description  = (
        "Art.24 makes the controller responsible for implementing T&O "
        "measures to ENSURE and to be ABLE TO DEMONSTRATE compliance with "
        "the Regulation, for reviewing and updating those measures, and "
        "for implementing data protection policies (Art.24.2). The ask is "
        "governance maturity, not new substantive obligations — Art.25/28/"
        "30/32/33/35/37 carry the substance. This spec derives from the "
        "ISO 27001 management-system clauses + annex controls that build "
        "the governance posture: leadership, named owners, management "
        "review, a policy framework, the GDPR-specific privacy policy, "
        "and a compliance-review function."
    ),
    # Art.24 binds controllers. Same gate as the other GDPR specs — leave
    # open until ClientFacts catalog supports a controller/processor flag.
    applies_when = None,  # TODO: tighten to 'is_controller' when ClientFacts catalog supports it
    derives_from = [
        DerivedFrom(
            target_control_ref = "5.1",
            target_standard_id = "ISO27001:2022",
            role               = "leadership_commitment",
            title              = "Top management leadership and commitment (Art.24.1)",
            # Whole control — Clause 5.1 is the management-clause anchor for
            # accountability: top management owns the ISMS, allocates
            # resources, integrates it into business processes. Art.24's
            # "controller responsibility" maps directly to that ownership.
        ),
        DerivedFrom(
            target_control_ref = "5.3",
            target_standard_id = "ISO27001:2022",
            role               = "named_authorities",
            title              = "Roles, responsibilities and authorities assigned (Art.24.1)",
            # Whole control — Art.24 accountability requires named owners
            # for compliance posture; Clause 5.3 is the ISO mechanism for
            # role assignment with decision rights.
        ),
        DerivedFrom(
            target_control_ref = "9.3",
            target_standard_id = "ISO27001:2022",
            role               = "review_and_update",
            title              = "Periodic management review of measures (Art.24.1 — 'reviewed and updated')",
            # Whole control — Art.24.1's second sentence ("Those measures
            # shall be reviewed and updated where necessary") is satisfied
            # by the management-review cadence in Clause 9.3.
        ),
        DerivedFrom(
            target_control_ref = "A.5.1",
            target_standard_id = "ISO27001:2022",
            role               = "policy_framework",
            title              = "Information security policies framework (Art.24.2)",
            # Whole control — Art.24.2 ("appropriate data protection
            # policies") is met by the A.5.1 policy framework: a policy
            # exists, is approved, is communicated, and is reviewed. All
            # four A.5.1 EvidenceRequirements load-bearing for the
            # accountability frame.
        ),
        DerivedFrom(
            target_control_ref = "A.5.34",
            target_standard_id = "ISO27001:2022",
            role               = "privacy_governance",
            title              = "Privacy and PII protection — accountability slice (Art.24.2)",
            # Restrict to the items that bear on accountability — knowing
            # the applicable law, the lawful-basis discipline, enabling
            # data subject rights, linking policy to security controls,
            # and breach-handling readiness. pii_inventory (RoPA / Art.30
            # territory) and retention_minimisation (Art.5.1.e / Art.25.2)
            # are governed by sibling articles and excluded here.
            scope_items = [
                "item:A.5.34:applicable_laws",
                "item:A.5.34:lawful_basis",
                "item:A.5.34:data_subject_rights",
                "item:A.5.34:security_controls_ref",
                "item:A.5.34:breach_handling",
            ],
        ),
        DerivedFrom(
            target_control_ref = "A.5.36",
            target_standard_id = "ISO27001:2022",
            role               = "demonstrate_compliance",
            title              = "Compliance review records (Art.24.1 — 'to be able to demonstrate')",
            # Whole control — Art.24.1's accountability bite is being
            # ABLE TO DEMONSTRATE that processing complies. A.5.36's
            # compliance-review records (schedule, scope, findings,
            # corrective actions, named owner) ARE that demonstration.
        ),
    ],
)


SPEC_ART_5_2 = DerivedSpec(
    spec_id      = "spec:GDPR:2016/679:Art.5.2",
    control_ref  = "Art.5.2",
    standard_id  = "GDPR:2016/679",
    op           = "ALL",
    title        = "Accountability principle (derived via Art.24)",
    description  = (
        "Art.5.2 is the GDPR accountability principle: 'The controller "
        "shall be responsible for, and be able to demonstrate compliance "
        "with, paragraph 1.' Art.24 is the operational article that "
        "implements this principle in detail (T&O measures to ensure and "
        "demonstrate compliance, review and update, data protection "
        "policies). Rather than duplicating Art.24's ISO 27001 "
        "derivations, this spec resolves transitively through Art.24."
    ),
    # Same gate as Art.24 — until ClientFacts catalog supports a controller
    # flag, leave open. See [[posture-engine-alignment-plan-2026-05-22]].
    applies_when = None,  # TODO: tighten to 'is_controller' when ClientFacts catalog supports it
    derives_from = [
        DerivedFrom(
            target_control_ref = "Art.24",
            target_standard_id = "GDPR:2016/679",
            role               = "controller_responsibility",
            title              = "Controller responsibility and demonstrability (Art.24) implements Art.5.2",
            # Single recursive derivation — Art.24 IS the operationalisation
            # of Art.5.2's accountability principle. Engine resolves Art.24
            # transitively through its six ISO 27001 management-system /
            # annex governance dependencies. Mirrors the Art.5.1.f → Art.32
            # pattern (principle → operational article).
        ),
    ],
)


SPEC_ART_5_1_E = DerivedSpec(
    spec_id      = "spec:GDPR:2016/679:Art.5.1.e",
    control_ref  = "Art.5.1.e",
    standard_id  = "GDPR:2016/679",
    op           = "ALL",
    title        = "Storage limitation (derived via A.5.33 retention + Art.25)",
    description  = (
        "Art.5.1.e is the GDPR principle that personal data shall be kept "
        "in a form permitting identification of data subjects for no "
        "longer than is necessary for the purposes for which the data are "
        "processed ('storage limitation'). Two derivations: A.5.33 "
        "records retention policy (concrete retention schedule with legal "
        "drivers and disposal at end of retention) and Art.25 "
        "(by-default minimum storage period — Art.25.2 — plus A.8.10 "
        "deletion procedure, both reached transitively through Art.25's "
        "derivations). Art.17 right-to-erasure is the data-subject-side "
        "counterpart but is uncurated; revisit when Art.17 is curated."
    ),
    # Storage limitation binds controllers and processors processing on
    # behalf of controllers. Same gate as the other GDPR specs.
    applies_when = None,  # TODO: tighten to 'is_controller OR is_processor' when ClientFacts catalog supports it
    derives_from = [
        DerivedFrom(
            target_control_ref = "A.5.33",
            target_standard_id = "ISO27001:2022",
            role               = "retention_policy",
            title              = "Records retention schedule and disposal (Art.5.1.e)",
            # Restrict to the retention/disposal items. A.5.33's
            # protection_requirements item (access control, encryption,
            # immutability) is Art.32 territory, not Art.5.1.e — excluded
            # from scope to keep this derivation focused on the storage-
            # period dimension.
            scope_items = [
                "item:A.5.33:records_schedule",
                "item:A.5.33:retention_periods",
                "item:A.5.33:retention_drivers",
                "item:A.5.33:disposal",
            ],
        ),
        DerivedFrom(
            target_control_ref = "Art.25",
            target_standard_id = "GDPR:2016/679",
            role               = "by_default_minimum_storage",
            title              = "Default storage period minimised + operational deletion (Art.5.1.e via Art.25)",
            # Transitive derivation — Art.25's spec already requires
            # Art.25.2's default_storage item (period of their storage set
            # to minimum necessary) AND derives from A.8.10 (information
            # deletion procedure). Both load-bearing for Art.5.1.e's
            # operational ask. Engine cycle guard handles the recursion.
        ),
    ],
)


SPEC_ART_5_1_C = DerivedSpec(
    spec_id      = "spec:GDPR:2016/679:Art.5.1.c",
    control_ref  = "Art.5.1.c",
    standard_id  = "GDPR:2016/679",
    op           = "ALL",
    title        = "Data minimisation (derived via Art.25)",
    description  = (
        "Art.5.1.c is the GDPR principle that personal data shall be "
        "'adequate, relevant and limited to what is necessary in relation "
        "to the purposes for which they are processed' (data "
        "minimisation). Art.25.2 is the operational implementation: by "
        "default, only personal data necessary for each specific purpose "
        "are processed (covering amount, extent, storage period, "
        "accessibility). Plus Art.25's A.5.34 derivation carries the "
        "retention_minimisation policy item. Art.6 (lawful basis defines "
        "the 'purposes' against which minimisation is measured) is the "
        "complementary angle but is uncurated; revisit when Art.6 is "
        "curated."
    ),
    # Same gate as the other GDPR specs — until ClientFacts catalog
    # supports a controller/processor flag, leave open.
    applies_when = None,  # TODO: tighten when ClientFacts catalog supports it
    derives_from = [
        DerivedFrom(
            target_control_ref = "Art.25",
            target_standard_id = "GDPR:2016/679",
            role               = "minimum_by_default",
            title              = "Default minimum data (Art.25.2) implements Art.5.1.c minimisation",
            # Transitive derivation — Art.25.2's default_amount and
            # default_extent items in the privacy-default configuration
            # record directly enforce data minimisation, and Art.25's
            # A.5.34 scope already includes retention_minimisation. Engine
            # cycle guard handles the recursion through Art.25 → ISO
            # 27001 deps. Mirrors the principle → operational article
            # pattern established by Art.5.1.f → Art.32 and Art.5.2 → Art.24.
        ),
    ],
)


SPEC_ART_6 = DerivedSpec(
    spec_id      = "spec:GDPR:2016/679:Art.6",
    control_ref  = "Art.6",
    standard_id  = "GDPR:2016/679",
    op           = "ALL",
    title        = "Lawfulness of processing (derived via ISO 27001 + lawful basis register)",
    description  = (
        "Art.6 requires that processing be lawful only if and to the extent "
        "that at least one of six lawful bases applies (consent, contract, "
        "legal obligation, vital interests, public interest, legitimate "
        "interests). ISO covers the policy commitment via A.5.34's "
        "lawful_basis item ('lawful basis identified per processing "
        "activity') and the law identification via A.5.31's legal/regulatory "
        "register (confirming GDPR is enrolled with a stated compliance "
        "approach). ISO does NOT capture the per-activity lawful basis "
        "register as a discrete artifact — that is the Art.6-specific "
        "auditor-facing artefact, added here as direct evidence. Art.7 "
        "(consent conditions) and Art.13/14 (informing data subjects of "
        "the basis) are complementary; Art.13 privacy notice is already "
        "curated as a standalone EvidenceRequirement and carries the "
        "communication arm."
    ),
    # Art.6 binds controllers (and processors via DPA flow-through). Same gate
    # as the other GDPR specs — leave open until ClientFacts catalog gains a
    # controller/processor flag.
    applies_when = None,  # TODO: tighten to 'is_controller OR is_processor' when ClientFacts catalog supports it
    derives_from = [
        DerivedFrom(
            target_control_ref = "A.5.34",
            target_standard_id = "ISO27001:2022",
            role               = "lawful_basis_policy",
            title              = "Lawful basis identified in privacy policy (Art.6)",
            # Restrict to the items that bear on Art.6 — knowing GDPR applies
            # (applicable_laws) and committing at policy level that a lawful
            # basis is identified per activity (lawful_basis). The other
            # A.5.34 items (pii_inventory / data_subject_rights / retention /
            # security_controls_ref / breach_handling) are governed by
            # sibling articles (Art.30 / Art.15-22 / Art.5.1.e / Art.32 /
            # Art.33) and excluded here.
            scope_items = [
                "item:A.5.34:applicable_laws",
                "item:A.5.34:lawful_basis",
            ],
        ),
        DerivedFrom(
            target_control_ref = "A.5.31",
            target_standard_id = "ISO27001:2022",
            role               = "legal_register",
            title              = "GDPR enrolled in legal/regulatory register (Art.6)",
            # Restrict to the items that prove the tenant has identified the
            # GDPR obligation and stated a compliance approach. Contractual
            # / per-item-owner / last-verified items are A.5.31 governance
            # not load-bearing for Art.6's lawfulness gate.
            scope_items = [
                "item:A.5.31:laws_listed",
                "item:A.5.31:jurisdictions",
                "item:A.5.31:compliance_approach",
            ],
        ),
    ],
    direct_evidence = [
        EvidenceRequirement(
            id            = "req:Art.6:lawful_basis_register",
            control_ref   = "Art.6",
            standard_id   = "GDPR:2016/679",
            evidence_type = "lawful_basis_register",
            title         = "Lawful basis register (Art.6)",
            trigger_type  = "universal",
            description   = (
                "Art.6 obliges the controller to be able to point to a "
                "specific lawful basis per processing activity. A register "
                "(or RoPA extension) listing each activity with the chosen "
                "basis, its justification, and — for consent or legitimate "
                "interests — the supporting record (consent capture or "
                "LIA) is the auditor-facing artifact. ISO does not require "
                "this as a discrete artifact; Art.6 does."
            ),
            freshness_days = 365,
            must_contain   = [
                ChecklistItem(
                    "item:Art.6:activities_enumerated",
                    "Processing activities enumerated (links to Art.30 RoPA)",
                    "must", True, "Art.6.1 — basis applies per activity",
                ),
                ChecklistItem(
                    "item:Art.6:basis_per_activity",
                    "Chosen lawful basis named per activity (one of Art.6.1.a-f)",
                    "must", True, "Art.6.1 — at least one of (a)-(f) applies",
                ),
                ChecklistItem(
                    "item:Art.6:justification",
                    "Justification recorded for the chosen basis per activity",
                    "must", True, "Art.5.2 accountability",
                ),
                ChecklistItem(
                    "item:Art.6:consent_link",
                    "For consent-based activities, link to Art.7 consent capture record",
                    "must", True, "Art.7 — conditions for consent",
                ),
                ChecklistItem(
                    "item:Art.6:lia_link",
                    "For legitimate-interests activities, link to LIA (necessity + balance test)",
                    "must", True, "Art.6.1.f — overriding interests test",
                ),
            ],
            should_contain = [
                ChecklistItem(
                    "item:Art.6:reviewed",
                    "Register reviewed within freshness window when activities or bases change",
                    "should", True, "Accountability — kept current",
                ),
                ChecklistItem(
                    "item:Art.6:basis_change_log",
                    "Log of lawful basis changes per activity (drives Art.13 notice amendments)",
                    "should", True, "Art.5.2 + Art.13 alignment",
                ),
            ],
        ),
    ],
)


SPEC_ART_16 = DerivedSpec(
    spec_id      = "spec:GDPR:2016/679:Art.16",
    control_ref  = "Art.16",
    standard_id  = "GDPR:2016/679",
    op           = "ALL",
    title        = "Right to rectification (derived via ISO 27001 + rectification procedure)",
    description  = (
        "Art.16 gives data subjects the right to obtain rectification of "
        "inaccurate personal data without undue delay (Art.12.3 sets the "
        "one-month response deadline) and to have incomplete personal data "
        "completed. The operational ask is twofold: (1) policy commitment "
        "to enabling the right, plus a personal-data inventory so the "
        "controller knows where to find data to correct; and (2) a "
        "concrete procedure covering intake, identity verification "
        "(Art.12.6), location across all systems, the correction itself, "
        "response to the data subject (Art.12.3), and onward notification "
        "to recipients (Art.19). ISO covers (1) via A.5.34's "
        "data_subject_rights + pii_inventory items; (2) is a GDPR-specific "
        "operational artefact added here as direct evidence. Art.12 "
        "(modalities) and Art.19 (notification) are referenced but "
        "themselves uncurated; revisit when they land."
    ),
    # Art.16 binds controllers. Same gate as the other GDPR specs.
    applies_when = None,  # TODO: tighten to 'is_controller' when ClientFacts catalog supports it
    derives_from = [
        DerivedFrom(
            target_control_ref = "A.5.34",
            target_standard_id = "ISO27001:2022",
            role               = "rights_policy_and_inventory",
            title              = "Data subject rights enabled + PII inventory available (Art.16)",
            # Restrict to the two items that bear on rectification — the
            # policy commitment that the right is enabled, and the PII
            # inventory that makes location-across-systems possible. Other
            # A.5.34 items (lawful_basis / retention_minimisation / security
            # / breach) are governed by sibling articles and excluded.
            scope_items = [
                "item:A.5.34:data_subject_rights",
                "item:A.5.34:pii_inventory",
            ],
        ),
    ],
    direct_evidence = [
        EvidenceRequirement(
            id            = "req:Art.16:rectification_procedure",
            control_ref   = "Art.16",
            standard_id   = "GDPR:2016/679",
            evidence_type = "rectification_procedure",
            title         = "Rectification procedure (Art.16)",
            trigger_type  = "universal",
            description   = (
                "Art.16 requires the controller to rectify inaccurate "
                "personal data without undue delay and to complete "
                "incomplete data. The procedure must cover intake, "
                "identity verification (Art.12.6), data location across "
                "all systems including replicas, the correction step "
                "itself, response to the data subject within one month "
                "(Art.12.3), and onward notification to recipients per "
                "Art.19. ISO does not require this as a discrete "
                "artifact; Art.16 does."
            ),
            freshness_days = 365,
            must_contain   = [
                ChecklistItem(
                    "item:Art.16:intake_channel",
                    "Intake channel published and accessible to data subjects",
                    "must", True, "Art.12.2 — facilitate exercise of rights",
                ),
                ChecklistItem(
                    "item:Art.16:identity_verification",
                    "Identity verification step (proportionate, not over-collecting)",
                    "must", True, "Art.12.6 — verify identity of requester",
                ),
                ChecklistItem(
                    "item:Art.16:data_location",
                    "Data location workflow across all systems including replicas (links to Art.30 RoPA)",
                    "must", True, "Art.16 — rectification across all instances",
                ),
                ChecklistItem(
                    "item:Art.16:correction_record",
                    "Correction recorded with what was changed, when, by whom",
                    "must", True, "Art.5.2 accountability",
                ),
                ChecklistItem(
                    "item:Art.16:response_deadline",
                    "Response to data subject within one month (extendable by two months for complex requests)",
                    "must", True, "Art.12.3 — one-month deadline",
                ),
                ChecklistItem(
                    "item:Art.16:recipient_notification",
                    "Notification to recipients per Art.19 unless impossible or disproportionate",
                    "must", True, "Art.19 — onward notification obligation",
                ),
            ],
            should_contain = [
                ChecklistItem(
                    "item:Art.16:supplementary_statement",
                    "Mechanism for supplementary statement when correction is contested",
                    "should", True, "Art.16 — completion via supplementary statement",
                ),
                ChecklistItem(
                    "item:Art.16:refusal_grounds",
                    "Documented grounds for refusing manifestly unfounded or excessive requests",
                    "should", True, "Art.12.5 — handling unfounded requests",
                ),
            ],
        ),
    ],
)


SPEC_ART_17 = DerivedSpec(
    spec_id      = "spec:GDPR:2016/679:Art.17",
    control_ref  = "Art.17",
    standard_id  = "GDPR:2016/679",
    op           = "ALL",
    title        = "Right to erasure (derived via ISO 27001 + erasure procedure)",
    description  = (
        "Art.17 gives data subjects the right to obtain erasure of personal "
        "data without undue delay on any of six grounds (Art.17.1.a-f: no "
        "longer necessary, consent withdrawn, objection, unlawful "
        "processing, legal obligation, child consent), subject to the "
        "Art.17.3 exceptions (freedom of expression, legal obligation, "
        "public interest, archiving, legal claims). The operational ask "
        "spans (1) policy commitment + PII inventory + retention "
        "alignment, (2) the actual deletion mechanism including backups "
        "and replicas, and (3) an erasure-specific procedure covering "
        "grounds assessment, exception handling, public-data notification "
        "(Art.17.2), and onward notification (Art.19). ISO covers (1) via "
        "A.5.34 and (2) via A.8.10 (information deletion); (3) is a "
        "GDPR-specific artefact added as direct evidence. Art.12 / Art.19 "
        "are uncurated; revisit when they land."
    ),
    # Art.17 binds controllers. Same gate as the other GDPR specs.
    applies_when = None,  # TODO: tighten to 'is_controller' when ClientFacts catalog supports it
    derives_from = [
        DerivedFrom(
            target_control_ref = "A.5.34",
            target_standard_id = "ISO27001:2022",
            role               = "rights_inventory_retention",
            title              = "Rights enabled + PII inventory + retention alignment (Art.17)",
            # Restrict to the three items that bear on erasure — the rights
            # commitment, the inventory needed to locate data, and the
            # retention/minimisation discipline that drives Art.17.1.a
            # ('no longer necessary') and intersects with Art.5.1.e.
            # applicable_laws / lawful_basis / security / breach are
            # governed by sibling articles and excluded.
            scope_items = [
                "item:A.5.34:data_subject_rights",
                "item:A.5.34:pii_inventory",
                "item:A.5.34:retention_minimisation",
            ],
        ),
        DerivedFrom(
            target_control_ref = "A.8.10",
            target_standard_id = "ISO27001:2022",
            role               = "deletion_mechanism",
            title              = "Information deletion procedure incl. backups/replicas (Art.17)",
            # Whole control — Art.17's bite is that erasure must reach every
            # copy including backups; A.8.10's scope_systems item already
            # requires the procedure to cover backups and replicas, and the
            # deletion_methods / verification / records items make the
            # erasure auditable. Aligned with the Art.5.1.e storage-limitation
            # use of A.8.10 reached transitively via Art.25.
        ),
    ],
    direct_evidence = [
        EvidenceRequirement(
            id            = "req:Art.17:erasure_procedure",
            control_ref   = "Art.17",
            standard_id   = "GDPR:2016/679",
            evidence_type = "erasure_procedure",
            title         = "Erasure procedure (Art.17)",
            trigger_type  = "universal",
            description   = (
                "Art.17 requires the controller to erase personal data "
                "without undue delay on any of the six grounds, subject "
                "to the Art.17.3 exceptions. The procedure must cover "
                "intake, identity verification, ground assessment, "
                "exception assessment (with documented refusal where "
                "applicable), erasure across all systems including "
                "backups/replicas (links to A.8.10), Art.17.2 "
                "notification of public-disclosure recipients where the "
                "controller has made the data public, and Art.19 "
                "notification of routine recipients. ISO does not "
                "require this combination as a discrete artifact; "
                "Art.17 does."
            ),
            freshness_days = 365,
            must_contain   = [
                ChecklistItem(
                    "item:Art.17:intake_channel",
                    "Intake channel published and accessible to data subjects",
                    "must", True, "Art.12.2 — facilitate exercise of rights",
                ),
                ChecklistItem(
                    "item:Art.17:identity_verification",
                    "Identity verification step (proportionate, not over-collecting)",
                    "must", True, "Art.12.6 — verify identity of requester",
                ),
                ChecklistItem(
                    "item:Art.17:grounds_assessment",
                    "Assessment of which Art.17.1 ground applies (a-f) recorded per request",
                    "must", True, "Art.17.1 — six grounds for erasure",
                ),
                ChecklistItem(
                    "item:Art.17:exception_assessment",
                    "Assessment of Art.17.3 exceptions with documented refusal grounds where applicable",
                    "must", True, "Art.17.3 — five exception categories",
                ),
                ChecklistItem(
                    "item:Art.17:erasure_scope_backups",
                    "Erasure scope covers backups and replicas (links to A.8.10:scope_systems)",
                    "must", True, "Art.17.1 — without undue delay across all instances",
                ),
                ChecklistItem(
                    "item:Art.17:erasure_record",
                    "Erasure recorded with what was deleted, when, by whom, verification (links to A.8.10:records)",
                    "must", True, "Art.5.2 accountability",
                ),
                ChecklistItem(
                    "item:Art.17:response_deadline",
                    "Response to data subject within one month (extendable by two months for complex requests)",
                    "must", True, "Art.12.3 — one-month deadline",
                ),
                ChecklistItem(
                    "item:Art.17:recipient_notification",
                    "Notification to recipients per Art.19 unless impossible or disproportionate",
                    "must", True, "Art.19 — onward notification obligation",
                ),
            ],
            should_contain = [
                ChecklistItem(
                    "item:Art.17:public_disclosure_step",
                    "Step for Art.17.2 public-disclosure cases — reasonable measures to inform controllers processing the public data",
                    "should", True, "Art.17.2 — public-disclosure notification",
                ),
                ChecklistItem(
                    "item:Art.17:legal_hold_check",
                    "Legal-hold check before erasure (links to A.8.10:legal_hold)",
                    "should", True, "Art.17.3 — legal obligation / claims exception",
                ),
            ],
        ),
    ],
)


SPEC_ART_5_1_A = DerivedSpec(
    spec_id      = "spec:GDPR:2016/679:Art.5.1.a",
    control_ref  = "Art.5.1.a",
    standard_id  = "GDPR:2016/679",
    op           = "ALL",
    title        = "Lawfulness, fairness and transparency (derived via Art.6 + Art.13)",
    description  = (
        "Art.5.1.a is the composite GDPR principle that personal data shall "
        "be processed lawfully, fairly and in a transparent manner. The "
        "principle breaks down into three operational anchors: lawfulness "
        "is the dedicated Art.6 ask (a lawful basis per processing "
        "activity); transparency is operationalised by Art.13/14 (privacy "
        "notice — Art.13 is the directly-collected case and already "
        "curated standalone). Fairness has no dedicated operational "
        "article — it is the residual duty not to mislead and not to "
        "process in ways data subjects would not reasonably expect, "
        "policed through Art.5.2 accountability and Art.13 transparency "
        "rather than a separate artefact. Art.14 (data collected "
        "indirectly) is the complementary transparency angle but is "
        "uncurated; revisit when it lands."
    ),
    # Art.5.1.a binds controllers (and processors under DPA flow-through).
    # Same gate as the other GDPR specs.
    applies_when = None,  # TODO: tighten when ClientFacts catalog supports controller/processor flag
    derives_from = [
        DerivedFrom(
            target_control_ref = "Art.6",
            target_standard_id = "GDPR:2016/679",
            role               = "lawfulness",
            title              = "Lawful basis per processing activity (Art.6) implements Art.5.1.a lawfulness",
            # Transitive derivation — Art.6 IS the operationalisation of the
            # lawfulness limb of Art.5.1.a. Engine resolves Art.6 through its
            # A.5.34 + A.5.31 derivations plus the lawful basis register.
            # Mirrors the principle → operational article pattern (Art.5.1.f
            # → Art.32, Art.5.1.c → Art.25, Art.5.2 → Art.24).
        ),
        DerivedFrom(
            target_control_ref = "Art.13",
            target_standard_id = "GDPR:2016/679",
            role               = "transparency",
            title              = "Privacy notice (Art.13) implements Art.5.1.a transparency",
            # Transitive derivation — Art.13 carries the data-subject-facing
            # transparency artefacts (identity, purposes, lawful basis,
            # recipients, retention, rights, complaints, transfers) required
            # by the transparency limb of Art.5.1.a. Art.14 (indirect
            # collection) is uncurated; when it lands it can be added here
            # without breaking the existing edge.
        ),
    ],
)


SPEC_ART_5_1_B = DerivedSpec(
    spec_id      = "spec:GDPR:2016/679:Art.5.1.b",
    control_ref  = "Art.5.1.b",
    standard_id  = "GDPR:2016/679",
    op           = "ALL",
    title        = "Purpose limitation (derived via Art.6 + Art.30)",
    description  = (
        "Art.5.1.b requires that personal data be collected for specified, "
        "explicit and legitimate purposes and not further processed in a "
        "way incompatible with those purposes. Two operational anchors: "
        "Art.6 establishes the legitimate purpose tied to a lawful basis "
        "(its lawful basis register names the purpose per activity), and "
        "Art.30 RoPA enumerates purposes per processing activity ('the "
        "specified, explicit' bit). The further-processing-compatibility "
        "test (Art.6.4) is the residual ask — it sits inside Art.6 but "
        "is not separately operationalised here; a compatibility "
        "assessment record could be added as direct evidence later. "
        "Art.89 (safeguards for archiving / scientific / statistical "
        "purposes) is the exception carve-out and is uncurated; revisit "
        "when it lands."
    ),
    # Art.5.1.b binds controllers (and processors via DPA flow-through).
    applies_when = None,  # TODO: tighten when ClientFacts catalog supports controller/processor flag
    derives_from = [
        DerivedFrom(
            target_control_ref = "Art.6",
            target_standard_id = "GDPR:2016/679",
            role               = "legitimate_purpose",
            title              = "Lawful basis ties processing to a legitimate purpose (Art.6) implements Art.5.1.b",
            # Transitive derivation — Art.6 binds each activity to a lawful
            # basis with a stated justification (lawful basis register's
            # 'purposes' + 'justification' must-items), which is the
            # 'legitimate' limb of specified/explicit/legitimate. Engine
            # resolves Art.6 through its A.5.34/A.5.31 deps + register.
        ),
        DerivedFrom(
            target_control_ref = "Art.30",
            target_standard_id = "GDPR:2016/679",
            role               = "purposes_enumerated",
            title              = "RoPA enumerates purposes per activity (Art.30.1.b) implements Art.5.1.b specified/explicit",
            # Transitive derivation — Art.30's purposes must-item carries
            # the 'specified, explicit' arm: the controller has written
            # down the purpose of each processing activity. Combined with
            # Art.6's legitimacy ask, this covers the upfront purpose
            # discipline. Further-processing compatibility (Art.6.4) is
            # the residual gap noted in description.
        ),
    ],
)


SPEC_ART_5_1_D = DerivedSpec(
    spec_id      = "spec:GDPR:2016/679:Art.5.1.d",
    control_ref  = "Art.5.1.d",
    standard_id  = "GDPR:2016/679",
    op           = "ALL",
    title        = "Accuracy (derived via Art.16)",
    description  = (
        "Art.5.1.d requires that personal data be 'accurate and, where "
        "necessary, kept up to date; every reasonable step must be taken "
        "to ensure that personal data that are inaccurate, having regard "
        "to the purposes for which they are processed, are erased or "
        "rectified without delay'. Art.16 (right to rectification) is the "
        "operational article that implements both arms: the reactive arm "
        "(rectifying inaccurate data on request — covered by the Art.16 "
        "procedure's intake / location / correction / response steps) and "
        "the proactive arm (the procedure's data_location and "
        "correction_record items make controller-initiated correction "
        "auditable, satisfying the 'every reasonable step' duty). "
        "Erasure of inaccurate data is not a separate Art.17 ground "
        "(Art.17.1.d is unlawful processing, not inaccuracy), so this "
        "spec does not derive from Art.17; the rectification path is the "
        "operational answer to Art.5.1.d inaccurate data."
    ),
    # Art.5.1.d binds controllers (and processors via DPA flow-through).
    applies_when = None,  # TODO: tighten when ClientFacts catalog supports controller/processor flag
    derives_from = [
        DerivedFrom(
            target_control_ref = "Art.16",
            target_standard_id = "GDPR:2016/679",
            role               = "rectification",
            title              = "Right to rectification (Art.16) implements Art.5.1.d accuracy",
            # Single recursive derivation — Art.16's procedure carries both
            # the reactive duty (respond to data subject rectification
            # requests) and the proactive duty (the data_location and
            # correction_record items make controller-initiated accuracy
            # maintenance auditable). Engine resolves Art.16 through its
            # A.5.34 dep + procedure. Mirrors the principle → operational
            # article pattern (Art.5.1.f → Art.32, Art.5.1.c → Art.25,
            # Art.5.2 → Art.24, Art.5.1.a → Art.6 + Art.13).
        ),
    ],
)


SPEC_ART_5_1 = DerivedSpec(
    spec_id      = "spec:GDPR:2016/679:Art.5.1",
    control_ref  = "Art.5.1",
    standard_id  = "GDPR:2016/679",
    op           = "ALL",
    title        = "Principles relating to processing of personal data (Art.5.1 umbrella)",
    description  = (
        "Art.5.1 is the umbrella paragraph listing the six sub-principles "
        "(a) lawfulness/fairness/transparency, (b) purpose limitation, "
        "(c) data minimisation, (d) accuracy, (e) storage limitation, "
        "(f) integrity and confidentiality. All six are individually "
        "curated as DerivedSpecs that resolve through operational "
        "articles and ISO 27001 controls; this spec aggregates them. "
        "op=ALL — every sub-principle must comply for the umbrella to "
        "comply, consistent with GDPR's binding-conjunctive reading of "
        "Art.5.1. Engine cycle guard handles transitive resolution "
        "through each sub-principle's deps."
    ),
    # Art.5.1 binds controllers (and processors via DPA flow-through).
    applies_when = None,  # TODO: tighten when ClientFacts catalog supports controller/processor flag
    derives_from = [
        DerivedFrom(
            target_control_ref = "Art.5.1.a",
            target_standard_id = "GDPR:2016/679",
            role               = "lawfulness_fairness_transparency",
            title              = "Lawfulness, fairness and transparency (Art.5.1.a)",
        ),
        DerivedFrom(
            target_control_ref = "Art.5.1.b",
            target_standard_id = "GDPR:2016/679",
            role               = "purpose_limitation",
            title              = "Purpose limitation (Art.5.1.b)",
        ),
        DerivedFrom(
            target_control_ref = "Art.5.1.c",
            target_standard_id = "GDPR:2016/679",
            role               = "data_minimisation",
            title              = "Data minimisation (Art.5.1.c)",
        ),
        DerivedFrom(
            target_control_ref = "Art.5.1.d",
            target_standard_id = "GDPR:2016/679",
            role               = "accuracy",
            title              = "Accuracy (Art.5.1.d)",
        ),
        DerivedFrom(
            target_control_ref = "Art.5.1.e",
            target_standard_id = "GDPR:2016/679",
            role               = "storage_limitation",
            title              = "Storage limitation (Art.5.1.e)",
        ),
        DerivedFrom(
            target_control_ref = "Art.5.1.f",
            target_standard_id = "GDPR:2016/679",
            role               = "integrity_confidentiality",
            title              = "Integrity and confidentiality (Art.5.1.f)",
        ),
    ],
)


SPEC_ART_5 = DerivedSpec(
    spec_id      = "spec:GDPR:2016/679:Art.5",
    control_ref  = "Art.5",
    standard_id  = "GDPR:2016/679",
    op           = "ALL",
    title        = "Principles relating to processing of personal data (Art.5 umbrella)",
    description  = (
        "Art.5 is the top-level GDPR principles article. It binds Art.5.1 "
        "(the six sub-principles: lawfulness/fairness/transparency, purpose "
        "limitation, data minimisation, accuracy, storage limitation, "
        "integrity and confidentiality) and Art.5.2 (the accountability "
        "principle that the controller shall be responsible for, and able "
        "to demonstrate compliance with, paragraph 1). op=ALL — both "
        "paragraphs must comply for Art.5 to comply. Resolves "
        "transitively through Art.5.1 (6-child roll-up via .a-.f) and "
        "Art.5.2 (single-edge via Art.24). Engine cycle guard + "
        "memoisation handle the three-layer depth (Art.5 → Art.5.1 → "
        "Art.5.1.x → operational article → ISO 27001 control)."
    ),
    # Art.5 binds controllers (and processors via DPA flow-through).
    applies_when = None,  # TODO: tighten when ClientFacts catalog supports controller/processor flag
    derives_from = [
        DerivedFrom(
            target_control_ref = "Art.5.1",
            target_standard_id = "GDPR:2016/679",
            role               = "principles",
            title              = "Six processing principles (Art.5.1) implement Art.5",
            # Transitive derivation through the six-child Art.5.1 umbrella.
            # Engine resolves Art.5.1 → Art.5.1.a..f → operational articles
            # → ISO 27001 deps. Memoisation prevents re-evaluation when
            # Art.6 / Art.13 / Art.24 / Art.25 / Art.32 are reached via
            # multiple paths.
        ),
        DerivedFrom(
            target_control_ref = "Art.5.2",
            target_standard_id = "GDPR:2016/679",
            role               = "accountability",
            title              = "Controller accountability for the principles (Art.5.2) implements Art.5",
            # Transitive derivation — Art.5.2 derives from Art.24 which
            # carries the six ISO 27001 management-system + annex
            # governance dependencies. The accountability arm of Art.5
            # joins the principles arm in op=ALL semantics.
        ),
    ],
)


ALL_DERIVED_SPECS: list[DerivedSpec] = [
    SPEC_ART_32,
    SPEC_ART_25,
    SPEC_ART_5_1_F,
    SPEC_ART_24,
    SPEC_ART_5_2,
    SPEC_ART_5_1_E,
    SPEC_ART_5_1_C,
    SPEC_ART_6,
    SPEC_ART_16,
    SPEC_ART_17,
    SPEC_ART_5_1_A,
    SPEC_ART_5_1_B,
    SPEC_ART_5_1_D,
    SPEC_ART_5_1,
    SPEC_ART_5,
]


# ── Complete registry ──────────────────────────────────────────────────────────

ALL_EVIDENCE_REQUIREMENTS: list[EvidenceRequirement] = [
    # Universal — ISO 27001
    REQ_ISMS_SCOPE,
    REQ_ISMS_POLICY,
    REQ_RISK_ASSESSMENT,
    REQ_RISK_TREATMENT,
    REQ_INTERNAL_AUDIT,
    REQ_MANAGEMENT_REVIEW,
    REQ_ENCRYPTION_POLICY,
    # A.5.24 — 4-leaf operational_process (2026-05-31; program review freshness=180)
    REQ_A524_FRAMEWORK,
    REQ_A524_IR_TEAM_REGISTER,
    REQ_A524_PROGRAM_REVIEW,
    REQ_A524_EXERCISE_RECORD,
    REQ_DATA_MASKING,
    # Universal — ISO 27001 Annex A.5.18 (four-leaf curation, 2026-05-26 —
    # promoted from single-leaf REQ_ACCESS_RIGHTS per [[curation-program-full-multi-leaf]])
    REQ_A518_PROCEDURE,
    REQ_A518_REGISTER,
    REQ_A518_REVIEW,
    REQ_A518_REVOCATION,

    # Universal — ISO 27001 Annex A.5.1 (four-leaf curation, commit 3)
    REQ_A51_ISP_POLICY,
    REQ_A51_APPROVAL,
    REQ_A51_COMMUNICATION,
    REQ_A51_REVIEW,

    # Universal — ISO 27001 Annex A.5.2 (four-leaf curation, 2026-05-27)
    REQ_A52_RESPONSIBILITY_MATRIX,
    REQ_A52_APPROVAL,
    REQ_A52_COMMUNICATION,
    REQ_A52_REVIEW,

    # Universal — ISO 27001 Annex A.5 bulk curation (Phase B, 2026-05-22).
    # Numerical order. 4-leaf curations are interleaved in numeric order:
    #   - A.5.2 / A.5.18 above (policy_program / operational_process)
    #   - A.5.5 / A.5.6 / A.5.9 / A.5.31 / A.5.32 (records_program, 2026-05-29)
    # A.5.23 already exists above as REQ_CLOUD_SERVICES_POLICY (4-leaf,
    # supplier+cloud batch 3). A.5.24 promoted to 4-leaf in batch 14 above
    # (REQ_A524_FRAMEWORK / REQ_A524_IR_TEAM_REGISTER / REQ_A524_PROGRAM_REVIEW
    # / REQ_A524_EXERCISE_RECORD).
    # A.5.3 — 4-leaf policy_program (2026-05-29)
    REQ_A53_SEGREGATION_MATRIX,
    REQ_A53_APPROVAL,
    REQ_A53_COMMUNICATION,
    REQ_A53_REVIEW,
    # A.5.4 — 4-leaf policy_program (2026-05-29)
    REQ_A54_MANAGEMENT_DIRECTIVE,
    REQ_A54_APPROVAL,
    REQ_A54_COMMUNICATION,
    REQ_A54_REVIEW,
    # A.5.5 — 4-leaf records_program (2026-05-29)
    REQ_A55_AUTHORITY_REGISTER,
    REQ_A55_MAINTENANCE_PROCEDURE,
    REQ_A55_APPLICABLE_AUTHORITIES_SCOPE,
    REQ_A55_REVIEW,
    # A.5.6 — 4-leaf records_program (2026-05-29)
    REQ_A56_SIG_REGISTER,
    REQ_A56_ENGAGEMENT_PROCEDURE,
    REQ_A56_RISK_TOPIC_SCOPE,
    REQ_A56_REVIEW,
    # A.5.7 — 4-leaf operational_process (2026-05-31; program review freshness=180)
    REQ_A57_THREAT_INTELLIGENCE_PROCEDURE,
    REQ_A57_FEED_REGISTER,
    REQ_A57_PROGRAM_REVIEW,
    REQ_A57_INTEL_PRODUCT_RECORD,
    # A.5.8 — 4-leaf operational_process (2026-05-31; program review freshness=365)
    REQ_A58_PROCEDURE,
    REQ_A58_PROJECT_REGISTER,
    REQ_A58_PROGRAM_REVIEW,
    REQ_A58_CLOSURE_RECORD,
    # A.5.9 — 4-leaf records_program (2026-05-29; register/review both freshness=90)
    REQ_A59_ASSET_REGISTER,
    REQ_A59_LIFECYCLE_PROCEDURE,
    REQ_A59_DISCOVERY_UPSTREAM,
    REQ_A59_RECONCILIATION_REVIEW,
    # A.5.10 — 4-leaf policy_program (2026-05-29)
    REQ_A510_POLICY,
    REQ_A510_APPROVAL,
    REQ_A510_COMMUNICATION,
    REQ_A510_REVIEW,
    # A.5.11 — 4-leaf operational_process (2026-05-31; program review freshness=365)
    REQ_A511_PROCEDURE,
    REQ_A511_LEAVER_REGISTER,
    REQ_A511_PROGRAM_REVIEW,
    REQ_A511_RETURN_RECORD,
    # A.5.12 — 4-leaf policy_program (2026-05-29)
    REQ_A512_SCHEME,
    REQ_A512_APPROVAL,
    REQ_A512_COMMUNICATION,
    REQ_A512_REVIEW,
    # A.5.13 — 4-leaf operational_process (2026-05-31; program review freshness=365)
    REQ_A513_PROCEDURE,
    REQ_A513_COVERAGE_REGISTER,
    REQ_A513_PROGRAM_REVIEW,
    REQ_A513_APPLICATION_RECORD,
    # A.5.14 — 4-leaf policy_program (2026-05-31; review freshness=365)
    REQ_A514_POLICY,
    REQ_A514_APPROVAL,
    REQ_A514_COMMUNICATION,
    REQ_A514_REVIEW,
    # A.5.15 — 4-leaf policy_program (2026-05-29)
    REQ_A515_POLICY,
    REQ_A515_APPROVAL,
    REQ_A515_COMMUNICATION,
    REQ_A515_REVIEW,
    # A.5.16 — 4-leaf operational_process (2026-05-31; program review freshness=180)
    REQ_A516_PROCEDURE,
    REQ_A516_IDENTITY_REGISTER,
    REQ_A516_PROGRAM_REVIEW,
    REQ_A516_REVOCATION_RECORD,
    # A.5.17 — 4-leaf operational_process (2026-05-31; program review freshness=180)
    REQ_A517_PROCEDURE,
    REQ_A517_CREDENTIAL_REGISTER,
    REQ_A517_PROGRAM_REVIEW,
    REQ_A517_REVOCATION_RECORD,
    # A.5.19 — 4-leaf operational_process (2026-05-31)
    REQ_A519_SUPPLIER_RISK_PROCEDURE,
    REQ_A519_REGISTER,
    REQ_A519_REVIEW,
    REQ_A519_OFFBOARDING,
    # A.5.20 — 4-leaf operational_process adapted (template + coverage + review + deviations)
    REQ_A520_SUPPLIER_AGREEMENT_TEMPLATE,
    REQ_A520_COVERAGE_REGISTER,
    REQ_A520_REVIEW,
    REQ_A520_DEVIATIONS,
    # A.5.21 — 4-leaf operational_process (2026-05-31; review freshness=180)
    REQ_A521_ICT_SUPPLY_CHAIN,
    REQ_A521_REGISTER,
    REQ_A521_REVIEW,
    REQ_A521_EOL_REPLACEMENT,
    # A.5.22 — 4-leaf operational_process adapted (review_record + schedule + meta_review + change_response)
    REQ_A522_SUPPLIER_REVIEW,
    REQ_A522_SCHEDULE_REGISTER,
    REQ_A522_PROGRAM_REVIEW,
    REQ_A522_CHANGE_RESPONSE,
    # A.5.25 — 4-leaf operational_process (2026-05-31; review freshness=180)
    REQ_A525_EVENT_TRIAGE,
    REQ_A525_TRIAGE_LOG,
    REQ_A525_PROGRAM_REVIEW,
    REQ_A525_DECISION_RECORD,
    # A.5.26 — 4-leaf operational_process (2026-05-31; review freshness=180)
    REQ_A526_INCIDENT_RESPONSE_PROCEDURE,
    REQ_A526_INCIDENT_REGISTER,
    REQ_A526_IR_REVIEW,
    REQ_A526_CLOSURE_RECORD,
    # A.5.27 — 4-leaf operational_process (2026-05-31)
    REQ_A527_LESSONS_LEARNED,
    REQ_A527_LESSONS_REGISTER,
    REQ_A527_LESSONS_REVIEW,
    REQ_A527_IMPROVEMENT_RECORD,
    # A.5.28 — 4-leaf operational_process (2026-05-31; program review freshness=365)
    REQ_A528_EVIDENCE_PROCEDURE,
    REQ_A528_CUSTODY_REGISTER,
    REQ_A528_PROGRAM_REVIEW,
    REQ_A528_DISPOSAL_RECORD,
    # A.5.29 — 4-leaf operational_process (2026-05-31; program review freshness=180)
    REQ_A529_PLAN,
    REQ_A529_SCENARIO_REGISTER,
    REQ_A529_PROGRAM_REVIEW,
    REQ_A529_ACTIVATION_RECORD,
    # A.5.30 — 4-leaf operational_process (2026-05-31; program review freshness=180)
    REQ_A530_PLAN,
    REQ_A530_SERVICE_REGISTER,
    REQ_A530_PROGRAM_REVIEW,
    REQ_A530_RECOVERY_RECORD,
    # A.5.31 — 4-leaf records_program (2026-05-29; review freshness=180)
    REQ_A531_OBLIGATIONS_REGISTER,
    REQ_A531_MAINTENANCE_PROCEDURE,
    REQ_A531_APPLICABLE_OBLIGATIONS_SCOPE,
    REQ_A531_REVIEW,
    # A.5.32 — 4-leaf records_program adapted (2026-05-29; procedure leaf retained)
    REQ_A532_PROTECTION_PROCEDURE,
    REQ_A532_LICENSED_INVENTORY,
    REQ_A532_ACQUIRED_WORKS_UPSTREAM,
    REQ_A532_AUDIT_REVIEW,
    # A.5.33 — 4-leaf records_program (2026-06-01; pairs with batch 1
    # records-family A.5.5/6/9/31/32; review freshness=365)
    REQ_A533_RECORDS_PROTECTION_PROCEDURE,
    REQ_A533_RECORDS_SCHEDULE_REGISTER,
    REQ_A533_RECORDS_CATEGORIES_SCOPE,
    REQ_A533_REVIEW,
    # A.5.34 — 4-leaf records_program (2026-06-01; natural pair with A.5.33;
    # ALL 7 prior MUST item-ids preserved for SPEC_ART_24 + SPEC_ART_25
    # derivations; review freshness=365)
    REQ_A534_PRIVACY_PII_POLICY,
    REQ_A534_PII_PROCESSING_REGISTER,
    REQ_A534_PRIVACY_APPLICABILITY_SCOPE,
    REQ_A534_PROGRAM_REVIEW,
    # A.5.35 — 4-leaf records_program review-record-as-primary (2026-06-01;
    # same shape as A.5.22 supplier review; primary leaf freshness=365)
    REQ_A535_INDEPENDENT_REVIEW_REPORT,
    REQ_A535_REVIEW_SCHEDULE_REGISTER,
    REQ_A535_PROGRAM_META_REVIEW,
    REQ_A535_FINDING_RESPONSE_REGISTER,
    # A.5.36 — 4-leaf records_program review-record-as-primary (2026-06-01;
    # batch-mate of A.5.35; primary leaf freshness=365)
    REQ_A536_COMPLIANCE_REVIEW_RECORD,
    REQ_A536_REVIEW_SCHEDULE,
    REQ_A536_PROGRAM_META_REVIEW,
    REQ_A536_NONCONFORMITY_REGISTER,
    # A.5.37 — 4-leaf records_program register-as-primary (2026-06-01;
    # same shape as A.5.9 asset register; review freshness=365)
    REQ_A537_OPERATING_PROCEDURES_REGISTER,
    REQ_A537_MAINTENANCE_PROCEDURE,
    REQ_A537_APPLICABLE_FACILITIES_SCOPE,
    REQ_A537_PROGRAM_REVIEW,

    # Universal — ISO 27001 Annex A.6 People Controls bulk curation (Phase B,
    # 2026-05-22). A.6.7 (Remote Working Policy) already exists as
    # REQ_REMOTE_WORKING further up in the file.
    REQ_A61_SCREENING,
    REQ_A62_EMPLOYMENT_TERMS,
    REQ_A63_SECURITY_AWARENESS,
    REQ_A64_DISCIPLINARY_PROCESS,
    REQ_A65_POST_EMPLOYMENT,
    REQ_A66_NDA,
    REQ_A68_EVENT_REPORTING,

    # Universal — ISO 27001 Annex A.7 Physical Controls bulk curation
    # (Phase B, 2026-05-22). All 14 A.7 controls were uncurated prior.
    REQ_A71_PHYSICAL_PERIMETERS,
    REQ_A72_PHYSICAL_ENTRY,
    REQ_A73_OFFICES_ROOMS,
    REQ_A74_PHYSICAL_MONITORING,
    REQ_A75_ENVIRONMENTAL_THREATS,
    REQ_A76_WORKING_IN_SECURE_AREAS,
    REQ_A77_CLEAR_DESK_SCREEN,
    REQ_A78_EQUIPMENT_SITING,
    REQ_A79_OFF_PREMISES,
    REQ_A710_STORAGE_MEDIA,
    REQ_A711_SUPPORTING_UTILITIES,
    REQ_A712_CABLING_SECURITY,
    REQ_A713_EQUIPMENT_MAINTENANCE,
    REQ_A714_SECURE_DISPOSAL,

    # Universal — ISO 27001 Annex A.8 Technological Controls bulk curation
    # (Phase B, 2026-05-22). A.8.11 / A.8.24 / A.8.25 already exist further
    # up as REQ_DATA_MASKING / REQ_ENCRYPTION_POLICY / REQ_SECURE_DEVELOPMENT.
    REQ_A81_USER_ENDPOINTS,
    # A.8.2 — 4-leaf technical_control spine (drafted 2026-05-26, awaiting load)
    REQ_A82_BASELINE,
    REQ_A82_PROCEDURE,
    REQ_A82_ACTIVITY_LOG,
    REQ_A82_RECERTIFICATION,
    REQ_A83_INFORMATION_ACCESS_RESTRICTION,
    REQ_A84_SOURCE_CODE_ACCESS,
    REQ_A85_SECURE_AUTHENTICATION,
    REQ_A86_CAPACITY_MANAGEMENT,
    REQ_A87_MALWARE_PROTECTION,
    REQ_A88_TECHNICAL_VULNERABILITIES,
    REQ_A89_CONFIGURATION_MANAGEMENT,
    REQ_A810_INFORMATION_DELETION,
    REQ_A812_DLP,
    REQ_A813_BACKUP,
    REQ_A814_REDUNDANCY,
    REQ_A815_LOGGING,
    REQ_A816_MONITORING_ACTIVITIES,
    REQ_A817_CLOCK_SYNC,
    REQ_A818_PRIVILEGED_UTILITY_PROGRAMS,
    REQ_A819_SOFTWARE_INSTALLATION,
    REQ_A820_NETWORKS_SECURITY,
    REQ_A821_NETWORK_SERVICES,
    REQ_A822_NETWORK_SEGREGATION,
    REQ_A823_WEB_FILTERING,
    REQ_A826_APP_SECURITY_REQUIREMENTS,
    REQ_A827_ARCHITECTURE_PRINCIPLES,
    REQ_A828_SECURE_CODING,
    REQ_A829_SECURITY_TESTING,
    REQ_A830_OUTSOURCED_DEVELOPMENT,
    REQ_A831_ENVIRONMENT_SEPARATION,
    REQ_A832_CHANGE_MANAGEMENT,
    REQ_A833_TEST_INFORMATION,
    REQ_A834_AUDIT_TESTING_PROTECTION,

    # Universal — ISO 27001 Clauses 4-10 bulk curation (Phase B, 2026-05-22).
    # 4.3, 5.2, 6.1.2, 6.1.3, 9.2, 9.3 already exist above as the management-
    # system anchor REQs. Pure parents (4, 5, 6, 6.1, 7, 8, 9, 10) are set to
    # explicit_empty via a separate Cypher migration after this loader runs.
    REQ_C41_CONTEXT_ISSUES,
    REQ_C42_INTERESTED_PARTIES,
    REQ_C44_ISMS,
    REQ_C51_LEADERSHIP_COMMITMENT,
    REQ_C53_ISMS_ROLES,
    REQ_C611_RISK_OPPORTUNITY_PLANNING,
    REQ_C62_SECURITY_OBJECTIVES,
    REQ_C63_PLANNING_OF_CHANGES,
    REQ_C71_RESOURCES,
    REQ_C72_COMPETENCE,
    REQ_C73_AWARENESS,
    REQ_C74_COMMUNICATION,
    REQ_C75_DOCUMENTED_INFORMATION,
    REQ_C81_OPERATIONAL_PLANNING,
    REQ_C82_OPERATIONAL_RISK_ASSESSMENT,
    REQ_C83_OPERATIONAL_RISK_TREATMENT,
    REQ_C91_MONITORING_MEASUREMENT,
    REQ_C101_CONTINUAL_IMPROVEMENT,
    REQ_C102_NONCONFORMITY_CA,

    # Universal — GDPR
    REQ_PRIVACY_NOTICE_DIRECT,
    # GDPR Art.30 — 4-leaf records_program spine (2026-05-28 promotion)
    REQ_RECORDS_PROCESSING,
    REQ_ART30_MAINTENANCE_PROCEDURE,
    REQ_ART30_DATA_FLOW_INVENTORY,
    REQ_ART30_ANNUAL_REVIEW,
    # GDPR Art.15 — 4-leaf gdpr_rights spine (2026-05-28 promotion).
    # The operational response leaf REQ_DSAR_RESPONSE stays in the Operational
    # block below; these three universal siblings live here.
    REQ_ART15_HANDLING_PROCEDURE,
    REQ_ART15_REGISTER,
    REQ_ART15_PROCESS_REVIEW,

    # Profile-fact triggered
    REQ_DPA,
    # A.5.23 — 4-leaf operational_process adapted (policy + register + posture_review + exit_migration)
    REQ_CLOUD_SERVICES_POLICY,
    REQ_CLOUD_SERVICE_REGISTER,
    REQ_CLOUD_POSTURE_REVIEW,
    REQ_CLOUD_EXIT_MIGRATION,
    REQ_REMOTE_WORKING,
    REQ_SECURE_DEVELOPMENT,

    # Operational
    REQ_BREACH_NOTIFICATION,
    REQ_DSAR_RESPONSE,
]


def get_requirements_for_control(control_ref: str) -> list[EvidenceRequirement]:
    return [r for r in ALL_EVIDENCE_REQUIREMENTS if r.control_ref == control_ref]


def get_requirements_by_trigger(trigger_type: str) -> list[EvidenceRequirement]:
    return [r for r in ALL_EVIDENCE_REQUIREMENTS if r.trigger_type == trigger_type]


if __name__ == "__main__":
    from collections import Counter
    trigger_counts = Counter(r.trigger_type for r in ALL_EVIDENCE_REQUIREMENTS)
    total_items = sum(
        len(r.must_contain) + len(r.should_contain)
        for r in ALL_EVIDENCE_REQUIREMENTS
    )
    must_items = sum(len(r.must_contain) for r in ALL_EVIDENCE_REQUIREMENTS)
    gdpr_items = sum(
        sum(1 for i in r.must_contain if i.gdpr_aligned)
        for r in ALL_EVIDENCE_REQUIREMENTS
    )

    print(f"Evidence requirements: {len(ALL_EVIDENCE_REQUIREMENTS)}")
    for trigger, count in trigger_counts.items():
        print(f"  {trigger:15s}: {count}")
    print(f"\nChecklist items:")
    print(f"  Total:        {total_items}")
    print(f"  Must-contain: {must_items}")
    print(f"  GDPR-aligned: {gdpr_items}")

    if ALL_DERIVED_SPECS:
        print(f"\nDerived specs: {len(ALL_DERIVED_SPECS)}")
        for ds in ALL_DERIVED_SPECS:
            n_direct = len(ds.direct_evidence)
            direct_items = sum(len(de.must_contain) + len(de.should_contain)
                               for de in ds.direct_evidence)
            print(f"  {ds.standard_id}:{ds.control_ref:10s} {ds.op:10s} "
                  f"{len(ds.derives_from)} deps + {n_direct} direct ({direct_items} items)")
    print(f"\nControls covered:")
    for r in ALL_EVIDENCE_REQUIREMENTS:
        gdpr_count = sum(1 for i in r.must_contain if i.gdpr_aligned)
        flag = " [GDPR items]" if gdpr_count else ""
        print(f"  {r.control_ref:15s} {r.trigger_type:15s} {r.title}{flag}")
