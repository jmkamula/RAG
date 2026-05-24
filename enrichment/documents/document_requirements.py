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
    trigger_event:    str | None   # event name when trigger_type == "operational"
                                   # e.g. "personal_data_breach", "data_subject_access_request"
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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

REQ_RECORDS_PROCESSING = EvidenceRequirement(
    id            = "req:Art.30:records_of_processing",
    control_ref   = "Art.30",
    standard_id   = "GDPR:2016/679",
    evidence_type = "records_of_processing",
    title= "Records of Processing Activities (RoPA)",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "Controllers must maintain records of all processing activities under Art.30",
    must_contain  = [
        ChecklistItem("item:Art.30:controller_name",  "Name and contact details of controller", "must", True, "Art.30.1a"),
        ChecklistItem("item:Art.30:purposes",         "Purposes of the processing", "must", True, "Art.30.1b"),
        ChecklistItem("item:Art.30:categories_ds",    "Categories of data subjects", "must", True, "Art.30.1c"),
        ChecklistItem("item:Art.30:categories_data",  "Categories of personal data", "must", True, "Art.30.1c"),
        ChecklistItem("item:Art.30:recipients",       "Categories of recipients", "must", True, "Art.30.1d"),
        ChecklistItem("item:Art.30:transfers",        "Transfers to third countries with safeguards", "must", True, "Art.30.1e"),
        ChecklistItem("item:Art.30:retention",        "Envisaged time limits for erasure", "must", True, "Art.30.1f"),
        ChecklistItem("item:Art.30:security",         "General description of security measures", "must", True, "Art.30.1g"),
    ],
    should_contain= [
        ChecklistItem("item:Art.30:maintained",   "Kept in written form (electronic acceptable)", "should", True, "Art.30.3"),
        ChecklistItem("item:Art.30:processors",   "Processor details listed per activity", "should", True, "Completeness"),
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
    trigger_event = None,
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

REQ_CLOUD_SERVICES_POLICY = EvidenceRequirement(
    id            = "req:A.5.23:cloud_services_policy",
    control_ref   = "A.5.23",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title= "Information Security for Use of Cloud Services Policy",
    trigger_type  = "profile_fact",
    trigger_event = None,
    description   = "A.5.23 requires a topic-specific policy for cloud service usage",
    must_contain  = [
        ChecklistItem("item:A.5.23:scope",           "Scope of cloud services covered", "must", False, "A.5.23a"),
        ChecklistItem("item:A.5.23:risk_management", "How information security risks will be managed", "must", False, "A.5.23b"),
        ChecklistItem("item:A.5.23:selection",       "Cloud service selection criteria", "must", False, "A.5.23c"),
        ChecklistItem("item:A.5.23:responsibilities","Roles and responsibilities (provider vs customer)", "must", False, "A.5.23d"),
        ChecklistItem("item:A.5.23:controls",        "Which controls managed by provider vs organisation", "must", False, "A.5.23e"),
        ChecklistItem("item:A.5.23:incidents",       "Procedures for handling cloud-related security incidents", "must", False, "A.5.23h"),
        ChecklistItem("item:A.5.23:exit",            "Exit strategy and data return/deletion on termination", "must", False, "A.5.23j"),
        ChecklistItem("item:A.5.23:personal_data",   "How personal data in cloud storage is protected", "must", True, "GDPR Art.32 alignment"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.23:monitoring",  "Monitoring and review approach", "should", False, "A.5.23i"),
        ChecklistItem("item:A.5.23:approved",    "Approved cloud service providers list", "should", False, "Governance"),
    ],
)

REQ_ENCRYPTION_POLICY = EvidenceRequirement(
    id            = "req:A.8.24:encryption_policy",
    control_ref   = "A.8.24",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title= "Use of Cryptography Policy",
    trigger_type  = "universal",
    trigger_event = None,
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

REQ_INCIDENT_RESPONSE = EvidenceRequirement(
    id            = "req:A.5.24:incident_response_procedure",
    control_ref   = "A.5.24",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title= "Information Security Incident Response Procedure",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.24 requires documented incident management processes",
    must_contain  = [
        ChecklistItem("item:A.5.24:roles",           "Roles and responsibilities defined", "must", False, "A.5.24a"),
        ChecklistItem("item:A.5.24:detection",       "Detection and reporting process", "must", False, "A.5.24b"),
        ChecklistItem("item:A.5.24:assessment",      "Incident assessment and classification criteria", "must", False, "A.5.24c"),
        ChecklistItem("item:A.5.24:response",        "Response and escalation procedures", "must", False, "A.5.24d"),
        ChecklistItem("item:A.5.24:personal_data",   "Step to determine if personal data breach occurred", "must", True, "GDPR Art.33 alignment — 72hr notification"),
        ChecklistItem("item:A.5.24:notification",    "Notification process for personal data breaches", "must", True, "GDPR Art.33/34 alignment"),
        ChecklistItem("item:A.5.24:evidence",        "Evidence collection and preservation", "must", False, "A.5.24e"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.24:lessons",     "Lessons learned process", "should", False, "A.5.27 linkage"),
        ChecklistItem("item:A.5.24:contacts",    "External contact list (regulator, legal, PR)", "should", False, "Response effectiveness"),
        ChecklistItem("item:A.5.24:tested",      "Testing frequency and date of last test", "should", False, "Effectiveness"),
    ],
)

REQ_DATA_MASKING = EvidenceRequirement(
    id            = "req:A.8.11:data_masking_procedure",
    control_ref   = "A.8.11",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title= "Data Masking Procedure",
    trigger_type  = "universal",
    trigger_event = None,
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

REQ_ACCESS_RIGHTS = EvidenceRequirement(
    id            = "req:A.5.18:access_rights_procedure",
    control_ref   = "A.5.18",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title= "Access Rights Management Procedure",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.18 requires procedures for provisioning, review and revocation of access rights",
    must_contain  = [
        ChecklistItem("item:A.5.18:provisioning",  "Access provisioning process", "must", False, "A.5.18a"),
        ChecklistItem("item:A.5.18:review",        "Periodic access rights review — at least annually", "must", False, "A.5.18b"),
        ChecklistItem("item:A.5.18:revocation",    "Revocation process on role change or departure", "must", False, "A.5.18c"),
        ChecklistItem("item:A.5.18:privileged",    "Privileged access controls", "must", False, "A.5.18d"),
        ChecklistItem("item:A.5.18:approval",      "Approval process for access requests", "must", False, "Governance"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.18:records",     "Records of access grants and reviews maintained", "should", False, "Audit trail"),
        ChecklistItem("item:A.5.18:segregation", "Segregation of duties considered", "should", False, "A.5.3 linkage"),
    ],
)

REQ_REMOTE_WORKING = EvidenceRequirement(
    id            = "req:A.6.7:remote_working_policy",
    control_ref   = "A.6.7",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title= "Remote Working Policy",
    trigger_type  = "profile_fact",
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = "personal_data_breach",
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

REQ_DSAR_RESPONSE = EvidenceRequirement(
    id            = "req:Art.15:dsar_response",
    control_ref   = "Art.15",
    standard_id   = "GDPR:2016/679",
    evidence_type = "dsar_response",
    title= "Data Subject Access Request Response",
    trigger_type  = "operational",
    trigger_event = "data_subject_access_request",
    description   = "Art.15 requires response to access requests within one month",
    must_contain  = [
        ChecklistItem("item:Art.15:confirmation",  "Confirmation that personal data is or is not processed", "must", True, "Art.15.1"),
        ChecklistItem("item:Art.15:categories",    "Categories of personal data processed", "must", True, "Art.15.1b"),
        ChecklistItem("item:Art.15:purposes",      "Purposes of processing", "must", True, "Art.15.1a"),
        ChecklistItem("item:Art.15:recipients",    "Recipients or categories of recipients", "must", True, "Art.15.1c"),
        ChecklistItem("item:Art.15:retention",     "Envisaged retention period", "must", True, "Art.15.1d"),
        ChecklistItem("item:Art.15:rights",        "Rights to rectification, erasure, restriction, objection", "must", True, "Art.15.1e"),
        ChecklistItem("item:Art.15:complaint",     "Right to lodge complaint with supervisory authority", "must", True, "Art.15.1f"),
        ChecklistItem("item:Art.15:timing",        "Responded within one calendar month", "must", True, "Art.12.3"),
    ],
    should_contain= [
        ChecklistItem("item:Art.15:copy",      "Copy of personal data provided", "should", True, "Art.15.3"),
        ChecklistItem("item:Art.15:format",    "Provided in electronic format if requested", "should", True, "Art.15.3"),
    ],
)

# ── Annex A.5.1 — four-leaf curation (commit 3 — first full multi-leaf spec) ──
# A.5.1 requires the InfoSec policy and topic-specific policies to be defined,
# approved by management, published, communicated to relevant personnel, and
# reviewed at planned intervals. The single existing REQ_ISMS_POLICY at clause
# 5.2 only captures the policy artefact itself; A.5.1's auditor-expected
# fulfilment is a stack of four distinct evidence pieces. Same policy PDF
# can satisfy the policy leaf here AND the 5.2 leaf at the same time
# (artefact ↔ leaf is many-to-many per the Tension 5 resolution).

REQ_A51_ISP_POLICY = EvidenceRequirement(
    id            = "req:A.5.1:isp_policy",
    control_ref   = "A.5.1",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Information Security Policy (Annex A.5.1)",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.1 requires an information security policy that defines principles, scope, and roles, and references topic-specific policies",
    must_contain  = [
        ChecklistItem("item:A.5.1:scope",            "Scope of the policy defined (which assets, locations, personnel)", "must", False, "A.5.1 — defined"),
        ChecklistItem("item:A.5.1:principles",       "Information security principles and objectives stated", "must", False, "A.5.1 — defined"),
        ChecklistItem("item:A.5.1:roles",            "Roles and responsibilities for information security", "must", False, "A.5.1 — defined"),
        ChecklistItem("item:A.5.1:legal_compliance", "Commitment to legal, regulatory and contractual compliance", "must", False, "A.5.1 — defined"),
        ChecklistItem("item:A.5.1:topic_refs",       "References to topic-specific policies that flow from this one", "must", False, "A.5.1 — topic-specific policies"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.1:version",          "Version number and effective date", "should", False, "Document control"),
        ChecklistItem("item:A.5.1:owner",            "Policy owner named (typically CISO or equivalent)", "should", False, "Accountability"),
    ],
)

REQ_A51_APPROVAL = EvidenceRequirement(
    id            = "req:A.5.1:management_approval",
    control_ref   = "A.5.1",
    standard_id   = "ISO27001:2022",
    evidence_type = "approval",
    title         = "Top Management Approval of InfoSec Policy",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.1 requires top management to approve the InfoSec policy. The approval can live inside the policy as a signed cover page, in a board minute, or as a separate signed cover letter — any form that names a top-management signatory and a date",
    must_contain  = [
        ChecklistItem("item:A.5.1:approval_signatory", "Signatory at top-management level (CEO, board chair, or delegated equivalent)", "must", False, "A.5.1 — approved by management"),
        ChecklistItem("item:A.5.1:approval_date",      "Approval date recorded", "must", False, "A.5.1 — approved"),
        ChecklistItem("item:A.5.1:approval_target",    "Reference to the specific policy version being approved", "must", False, "A.5.1 — approved"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.1:approval_authority", "Statement of the signatory's authority to approve (delegation chain if not CEO)", "should", False, "Accountability"),
    ],
)

REQ_A51_COMMUNICATION = EvidenceRequirement(
    id            = "req:A.5.1:communication_record",
    control_ref   = "A.5.1",
    standard_id   = "ISO27001:2022",
    evidence_type = "communication_record",
    title         = "Information Security Policy Communication Record",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.1 requires the policy to be published and communicated to relevant personnel. Evidence must show active distribution (date, audience, channel), not mere availability on an intranet",
    must_contain  = [
        ChecklistItem("item:A.5.1:comm_date",         "Date of publication/communication", "must", False, "A.5.1 — communicated"),
        ChecklistItem("item:A.5.1:comm_audience",     "Audience reached (all staff, scoped subset, or named groups)", "must", False, "A.5.1 — communicated to relevant personnel"),
        ChecklistItem("item:A.5.1:comm_channel",      "Channel used (intranet publication, email, training session, town hall)", "must", False, "A.5.1 — communicated"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.1:comm_acknowledgment", "Acknowledgment of receipt and understanding by personnel (e.g. signed register, e-learning completion)", "should", False, "A.5.1 — acknowledged"),
        ChecklistItem("item:A.5.1:comm_interested",   "Communication to relevant interested parties (contractors, suppliers) where appropriate", "should", False, "A.5.1 — interested parties"),
    ],
)

REQ_A51_REVIEW = EvidenceRequirement(
    id            = "req:A.5.1:annual_review",
    control_ref   = "A.5.1",
    standard_id   = "ISO27001:2022",
    evidence_type = "review_record",
    title         = "Annual Information Security Policy Review Record",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.1 requires the policy to be reviewed at planned intervals (typically annually) and after significant changes. The review record captures who reviewed it, when, and the outcome (unchanged / amended / retired)",
    must_contain  = [
        ChecklistItem("item:A.5.1:review_date",       "Review date within the planned review interval (typically within 12 months of last review)", "must", False, "A.5.1 — reviewed at planned intervals"),
        ChecklistItem("item:A.5.1:review_outcome",    "Outcome of the review (no change / amended to vN / retired)", "must", False, "A.5.1 — reviewed"),
        ChecklistItem("item:A.5.1:review_reviewer",   "Reviewer identity and role", "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.1:review_triggers",   "List of significant-change triggers that should prompt an ad-hoc review", "should", False, "A.5.1 — review on significant change"),
        ChecklistItem("item:A.5.1:review_next_date",  "Next planned review date stated", "should", False, "Planning"),
    ],
)


# ── ISO 27001 Annex A.5 — Organizational Controls (Phase B bulk curation) ────
# Style locked 2026-05-22 via A.5.26 worked example:
#   - Single leaf per control where the obligation is a single document type
#   - Cross-references to sibling controls go in SHOULD items, never MUST
#   - freshness_days only when the standard text itself requires periodic
#     review/update/maintenance ("kept up to date", "regularly reviewed",
#     "planned intervals", "tested")
#   - Item ids follow item:{control_ref}:{slug}; rationale strings are
#     control-ref-keyed short phrases
# A.5.1 (4-leaf) and A.5.18 / A.5.23 / A.5.24 already exist above and below.

REQ_A52_ROLES_RESPONSIBILITIES = EvidenceRequirement(
    id            = "req:A.5.2:roles_and_responsibilities",
    control_ref   = "A.5.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "responsibility_matrix",
    title         = "Information Security Roles and Responsibilities",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.2 requires roles and responsibilities for information security to be defined and allocated. Evidence is a responsibility matrix (or equivalent section in the ISMS charter) that enumerates roles, assigns owners, and shows allocation across the organization",
    must_contain  = [
        ChecklistItem("item:A.5.2:roles_enumerated", "Information security roles enumerated (CISO, ISMS Manager, Asset Owners, Risk Owners, Incident Manager, DPO where applicable)", "must", False, "A.5.2 — defined"),
        ChecklistItem("item:A.5.2:responsibilities", "Responsibilities described per role (decision rights, oversight, execution)", "must", False, "A.5.2 — defined"),
        ChecklistItem("item:A.5.2:allocation",       "Allocation to named individuals or positions, not just abstract role labels", "must", False, "A.5.2 — allocated according to organization needs"),
        ChecklistItem("item:A.5.2:reporting_lines",  "Reporting and escalation lines stated (who each role reports to)", "must", False, "A.5.2 — organization needs"),
        ChecklistItem("item:A.5.2:approval",         "Approved by management with date", "must", False, "A.5.2 — established"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.2:isp_link",         "Links back to the Information Security Policy (A.5.1)", "should", False, "Coherence with policy framework"),
        ChecklistItem("item:A.5.2:segregation_note", "Notes conflicts to be resolved via segregation of duties (A.5.3)", "should", False, "Cross-control consistency"),
    ],
)

REQ_A53_SEGREGATION_OF_DUTIES = EvidenceRequirement(
    id            = "req:A.5.3:segregation_of_duties",
    control_ref   = "A.5.3",
    standard_id   = "ISO27001:2022",
    evidence_type = "segregation_matrix",
    title         = "Segregation of Duties Matrix",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.3 requires conflicting duties and conflicting areas of responsibility to be segregated. Evidence is a matrix or analysis that identifies conflict pairs and the mechanism preventing one person from holding both",
    must_contain  = [
        ChecklistItem("item:A.5.3:conflict_pairs",    "Conflicting duty pairs identified (e.g. requestor vs approver, developer vs production deployer)", "must", False, "A.5.3 — conflicting duties"),
        ChecklistItem("item:A.5.3:separation_method", "Separation mechanism stated per pair (different people, different systems, four-eyes)", "must", False, "A.5.3 — segregated"),
        ChecklistItem("item:A.5.3:compensating",      "Compensating controls where full separation is not feasible (small-team exceptions)", "must", False, "A.5.3 — risk-based"),
        ChecklistItem("item:A.5.3:owner",             "Named owner of the matrix accountable for its maintenance", "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.3:coverage_scope",    "Scope of coverage stated (functional areas, systems, processes)", "should", False, "Audit clarity"),
        ChecklistItem("item:A.5.3:exception_process", "Exception process for temporary or unavoidable conflicts", "should", False, "Real-world flexibility"),
    ],
)

REQ_A54_MANAGEMENT_RESPONSIBILITIES = EvidenceRequirement(
    id            = "req:A.5.4:management_responsibilities",
    control_ref   = "A.5.4",
    standard_id   = "ISO27001:2022",
    evidence_type = "management_directive",
    title         = "Management Directive on Information Security Compliance",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.4 requires management to require all personnel to apply information security per the policy framework. Evidence is a management directive, mandate letter, or equivalent statement that personnel are bound by InfoSec policies and procedures",
    must_contain  = [
        ChecklistItem("item:A.5.4:mandate_statement", "Statement that personnel are required to apply InfoSec policies, topic-specific policies, and procedures", "must", False, "A.5.4 — require all personnel"),
        ChecklistItem("item:A.5.4:scope_personnel",   "Applicability to all personnel (employees, contractors, third parties acting on behalf)", "must", False, "A.5.4 — all personnel"),
        ChecklistItem("item:A.5.4:policy_references", "Names or references the in-scope policies and procedures", "must", False, "A.5.4 — in accordance with"),
        ChecklistItem("item:A.5.4:enforcement",       "Statement of consequence for non-compliance (link to HR disciplinary process)", "must", False, "A.5.4 — require"),
        ChecklistItem("item:A.5.4:management_signature","Signed by senior management with date", "must", False, "A.5.4 — management"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.4:onboarding_step",   "Distribution at onboarding for new personnel referenced", "should", False, "New-joiner coverage"),
        ChecklistItem("item:A.5.4:periodic_refresh",  "Periodic re-acknowledgement referenced (annual at minimum)", "should", False, "Ongoing reinforcement"),
    ],
)

REQ_A55_AUTHORITY_CONTACTS = EvidenceRequirement(
    id            = "req:A.5.5:authority_contact_register",
    control_ref   = "A.5.5",
    standard_id   = "ISO27001:2022",
    evidence_type = "contact_register",
    title         = "Authority Contact Register",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.5 requires the organization to establish and maintain contact with relevant authorities. Evidence is a register of authority contacts (data protection authority, law enforcement, sectoral regulator) with current contact details and last-verified dates",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:A.5.5:authorities_listed", "Relevant authorities listed (DPA, sectoral regulator, law enforcement, CERT/CSIRT)", "must", False, "A.5.5 — relevant authorities"),
        ChecklistItem("item:A.5.5:contact_details",    "Current contact details per authority (name, role, phone, email)", "must", False, "A.5.5 — establish contact"),
        ChecklistItem("item:A.5.5:escalation_criteria","Escalation criteria stating when each authority is engaged", "must", False, "A.5.5 — maintain contact"),
        ChecklistItem("item:A.5.5:last_verified",      "Last-verified date per entry (proves the register is maintained)", "must", False, "A.5.5 — maintain"),
        ChecklistItem("item:A.5.5:owner",              "Named owner responsible for maintenance", "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.5:backup_contacts",    "Backup or secondary contacts per authority", "should", False, "Continuity"),
        ChecklistItem("item:A.5.5:notification_templates","References notification templates per authority type", "should", False, "Speed at time of incident"),
    ],
)

REQ_A56_SIG_CONTACTS = EvidenceRequirement(
    id            = "req:A.5.6:special_interest_group_register",
    control_ref   = "A.5.6",
    standard_id   = "ISO27001:2022",
    evidence_type = "contact_register",
    title         = "Special Interest Group and Professional Forum Register",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.6 requires contact with special interest groups (SIGs), security forums, and professional associations. Evidence is a register of memberships and engagements that demonstrate active connection to the security community",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:A.5.6:sigs_listed",     "SIGs and forums listed (ISACs, ISC2/ISACA chapters, vendor groups, sector-specific)", "must", False, "A.5.6 — special interest groups"),
        ChecklistItem("item:A.5.6:basis_of_contact","Basis of contact stated per entry (paid membership, subscription, attendance)", "must", False, "A.5.6 — establish contact"),
        ChecklistItem("item:A.5.6:topics_shared",   "Topics or threat categories that drive each engagement", "must", False, "A.5.6 — maintain contact"),
        ChecklistItem("item:A.5.6:last_engaged",    "Last-engaged date per entry (event attended, briefing received)", "must", False, "A.5.6 — maintain"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.6:representative",  "Internal representative or point of contact per group", "should", False, "Accountability"),
        ChecklistItem("item:A.5.6:renewal_dates",   "Subscription or membership renewal dates tracked", "should", False, "Continuity of access"),
    ],
)

REQ_A57_THREAT_INTELLIGENCE = EvidenceRequirement(
    id            = "req:A.5.7:threat_intelligence_procedure",
    control_ref   = "A.5.7",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Threat Intelligence Programme Procedure",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.7 requires information about information security threats to be collected and analysed to produce threat intelligence. Evidence is a documented procedure covering sources, collection cadence, analysis approach, and intelligence products",
    must_contain  = [
        ChecklistItem("item:A.5.7:sources",          "Threat intelligence sources enumerated (open-source feeds, vendor feeds, ISACs, government advisories)", "must", False, "A.5.7 — collected"),
        ChecklistItem("item:A.5.7:collection_cadence","Collection cadence stated (continuous, daily, weekly)", "must", False, "A.5.7 — collected"),
        ChecklistItem("item:A.5.7:analysis_approach","Analysis approach defined (correlation, prioritisation, relevance filtering)", "must", False, "A.5.7 — analysed"),
        ChecklistItem("item:A.5.7:products",         "Intelligence products produced (IOC lists, threat briefings, advisories)", "must", False, "A.5.7 — produce threat intelligence"),
        ChecklistItem("item:A.5.7:distribution",     "Distribution path to consumers (security ops, IT, risk owners)", "must", False, "A.5.7 — produce"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.7:risk_feedback",    "Feedback loop into the risk register / risk assessment", "should", False, "Closes the operational loop"),
        ChecklistItem("item:A.5.7:product_retention","Retention period for intelligence products", "should", False, "Audit + lookback"),
    ],
)

REQ_A58_PROJECT_MANAGEMENT_SECURITY = EvidenceRequirement(
    id            = "req:A.5.8:project_management_security_integration",
    control_ref   = "A.5.8",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Information Security in Project Management Procedure",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.8 requires information security to be integrated into project management. Evidence is a project management standard or methodology that names security gates, deliverables, and responsibilities through the project lifecycle",
    must_contain  = [
        ChecklistItem("item:A.5.8:initiation_gate",  "Security gate at project initiation (risk assessment, classification of information)", "must", False, "A.5.8 — integrated"),
        ChecklistItem("item:A.5.8:requirements",     "Security requirements captured in project plan / requirements document", "must", False, "A.5.8 — integrated"),
        ChecklistItem("item:A.5.8:assessment_pre_golive","Security assessment before go-live (penetration test, control verification)", "must", False, "A.5.8 — integrated"),
        ChecklistItem("item:A.5.8:role",             "Information security role defined in the project governance (advisor, reviewer, gate-owner)", "must", False, "A.5.8 — integrated"),
        ChecklistItem("item:A.5.8:closure_signoff",  "Project closure security sign-off step (handover to operations)", "must", False, "A.5.8 — integrated"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.8:tiering",          "Project tiering (which projects need full vs lightweight security review)", "should", False, "Proportionality"),
        ChecklistItem("item:A.5.8:templates",        "References standard project templates that include security sections", "should", False, "Consistency"),
    ],
)

REQ_A59_ASSET_INVENTORY = EvidenceRequirement(
    id            = "req:A.5.9:asset_inventory",
    control_ref   = "A.5.9",
    standard_id   = "ISO27001:2022",
    evidence_type = "asset_register",
    title         = "Inventory of Information and Associated Assets",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.9 requires an inventory of information and associated assets, including owners, to be developed and maintained. Evidence is an asset register that names assets, classifies them, and assigns owners",
    freshness_days = 90,
    must_contain  = [
        ChecklistItem("item:A.5.9:asset_records",  "Asset records exist (information assets, software, hardware, services)", "must", False, "A.5.9 — inventory"),
        ChecklistItem("item:A.5.9:owner_per_asset","Owner named per asset (individual or role accountable)", "must", False, "A.5.9 — including owners"),
        ChecklistItem("item:A.5.9:classification", "Classification per asset (links to A.5.12 scheme)", "must", False, "A.5.9 — inventory"),
        ChecklistItem("item:A.5.9:location",       "Location or system where the asset resides", "must", False, "A.5.9 — inventory"),
        ChecklistItem("item:A.5.9:last_updated",   "Last-updated date per record (proves maintenance)", "must", False, "A.5.9 — maintained"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.9:lifecycle_status","Lifecycle status per asset (active, retired, in-procurement)", "should", False, "Operational completeness"),
        ChecklistItem("item:A.5.9:dependencies",   "Dependency or relationship to other assets (supports A.8.x mapping)", "should", False, "Risk traceability"),
    ],
)

REQ_A510_ACCEPTABLE_USE = EvidenceRequirement(
    id            = "req:A.5.10:acceptable_use_policy",
    control_ref   = "A.5.10",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Acceptable Use Policy",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.10 requires rules for acceptable use and procedures for handling information and associated assets. Evidence is an Acceptable Use Policy (AUP) covering both general principles and the handling rules per asset/information class",
    must_contain  = [
        ChecklistItem("item:A.5.10:scope",            "Scope of the policy (which assets, which users, which information classes)", "must", False, "A.5.10 — rules for acceptable use"),
        ChecklistItem("item:A.5.10:acceptable_uses",  "Acceptable use rules stated (work purposes, identified personal-use boundaries)", "must", False, "A.5.10 — acceptable use"),
        ChecklistItem("item:A.5.10:prohibited_uses",  "Prohibited use rules stated (unlawful, harmful, security-bypassing activities)", "must", False, "A.5.10 — rules"),
        ChecklistItem("item:A.5.10:handling_procedures","Handling procedures per information class (storage, transmission, disposal)", "must", False, "A.5.10 — procedures for handling"),
        ChecklistItem("item:A.5.10:enforcement",      "Enforcement and disciplinary consequences referenced", "must", False, "A.5.10 — implemented"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.10:byod",             "BYOD provisions where personal devices are used for work", "should", False, "Modern workforce"),
        ChecklistItem("item:A.5.10:social_media",     "Social media usage and corporate-information disclosure rules", "should", False, "Reputational risk"),
    ],
)

REQ_A511_RETURN_OF_ASSETS = EvidenceRequirement(
    id            = "req:A.5.11:return_of_assets_procedure",
    control_ref   = "A.5.11",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Return of Assets Procedure",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.11 requires personnel to return all organizational assets upon change or termination. Evidence is a procedure (often part of HR offboarding) covering triggers, the return checklist, and verification",
    must_contain  = [
        ChecklistItem("item:A.5.11:triggers",         "Triggers enumerated (termination, role change, contract end, change of agreement)", "must", False, "A.5.11 — upon change or termination"),
        ChecklistItem("item:A.5.11:asset_checklist",  "Checklist of asset types to be returned (laptops, mobile devices, badges, tokens, documents)", "must", False, "A.5.11 — all the organization's assets"),
        ChecklistItem("item:A.5.11:verification",     "Verification step signed by both the returning party and the receiving role (IT/manager)", "must", False, "A.5.11 — return"),
        ChecklistItem("item:A.5.11:data_handling",    "Data wipe / data return step for assets carrying organizational information", "must", False, "A.5.11 — organization's assets"),
        ChecklistItem("item:A.5.11:owner",            "Owner of the procedure (typically HR + IT joint)", "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.11:timeline",         "Timeline stated (e.g. assets returned by last working day)", "should", False, "Timeliness"),
        ChecklistItem("item:A.5.11:exception_process","Exception process for outstanding assets (working from home, contractor delays)", "should", False, "Real-world friction"),
    ],
)

REQ_A512_INFORMATION_CLASSIFICATION = EvidenceRequirement(
    id            = "req:A.5.12:information_classification_scheme",
    control_ref   = "A.5.12",
    standard_id   = "ISO27001:2022",
    evidence_type = "classification_scheme",
    title         = "Information Classification Scheme",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.12 requires information to be classified per the organization's security needs across confidentiality, integrity, availability, and interested-party requirements. Evidence is a classification scheme defining levels and handling implications",
    must_contain  = [
        ChecklistItem("item:A.5.12:levels_defined",  "Classification levels defined (e.g. Public / Internal / Confidential / Restricted)", "must", False, "A.5.12 — classified"),
        ChecklistItem("item:A.5.12:cia_dimensions",  "Each level addresses confidentiality, integrity, and availability dimensions", "must", False, "A.5.12 — based on C/I/A"),
        ChecklistItem("item:A.5.12:level_definitions","Definition and indicative examples per level", "must", False, "A.5.12 — needs of the organization"),
        ChecklistItem("item:A.5.12:handling_per_level","Handling implications per level (links to A.5.13 labelling, A.5.10 acceptable use)", "must", False, "A.5.12 — security needs"),
        ChecklistItem("item:A.5.12:classification_authority","Decision authority for classifying information (owner-led by default)", "must", False, "A.5.12 — classified"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.12:interested_parties","Considerations for interested-party requirements (regulator-imposed classifications)", "should", False, "Completeness"),
        ChecklistItem("item:A.5.12:declassification","Declassification or reclassification process", "should", False, "Lifecycle"),
    ],
)

REQ_A513_INFORMATION_LABELLING = EvidenceRequirement(
    id            = "req:A.5.13:information_labelling_procedure",
    control_ref   = "A.5.13",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Information Labelling Procedure",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.13 requires procedures for information labelling aligned with the classification scheme. Evidence is a procedure covering how each classification level is marked on digital and physical assets",
    must_contain  = [
        ChecklistItem("item:A.5.13:visual_marks",     "Visual marking conventions per classification level (headers, watermarks, banners)", "must", False, "A.5.13 — labelling"),
        ChecklistItem("item:A.5.13:metadata_tags",    "Digital metadata tags or sensitivity labels (e.g. Microsoft Purview / similar)", "must", False, "A.5.13 — labelling"),
        ChecklistItem("item:A.5.13:physical_media",   "Physical media labelling rules (paper documents, removable storage)", "must", False, "A.5.13 — labelling"),
        ChecklistItem("item:A.5.13:label_persistence","Label persistence on copying, export, or transformation", "must", False, "A.5.13 — implemented"),
        ChecklistItem("item:A.5.13:training_ref",     "References training so personnel know how to apply labels", "must", False, "A.5.13 — implemented"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.13:legacy_handling",  "Handling of legacy unlabelled assets (default-classify rule)", "should", False, "Pragmatic adoption"),
        ChecklistItem("item:A.5.13:automation",       "Automation / tooling references where labelling is auto-applied", "should", False, "Scalability"),
    ],
)

REQ_A514_INFORMATION_TRANSFER = EvidenceRequirement(
    id            = "req:A.5.14:information_transfer_policy",
    control_ref   = "A.5.14",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Information Transfer Policy",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.14 requires transfer rules, procedures, or agreements covering all transfer facilities within the organization and to/from other parties. Evidence is a policy covering electronic, physical, and verbal transfers with protections per classification",
    must_contain  = [
        ChecklistItem("item:A.5.14:electronic_transfer","Rules for electronic transfers (email, file transfer, cloud sharing) with encryption requirements per classification", "must", False, "A.5.14 — transfer facilities"),
        ChecklistItem("item:A.5.14:physical_media",   "Rules for physical media transfers (removable storage, paper documents, post/courier)", "must", False, "A.5.14 — all types of transfer facilities"),
        ChecklistItem("item:A.5.14:verbal_visual",    "Rules for verbal and visual transfers (calls, screen-shares, in-person discussions in public)", "must", False, "A.5.14 — all types"),
        ChecklistItem("item:A.5.14:internal_vs_external","Distinction between internal and external transfer requirements", "must", False, "A.5.14 — within the organization and between"),
        ChecklistItem("item:A.5.14:authorisation",    "Authorisation requirements for transfers above defined classification levels", "must", False, "A.5.14 — rules"),
        ChecklistItem("item:A.5.14:legal_jurisdiction","Legal and jurisdictional considerations (cross-border transfers, data sovereignty)", "must", False, "A.5.14 — between organization and other parties"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.14:transfer_agreements","Standard transfer agreements with frequent counterparties", "should", False, "Efficiency"),
        ChecklistItem("item:A.5.14:approved_channels","Approved channel list (e.g. encrypted email, sanctioned file-sharing)", "should", False, "User clarity"),
    ],
)

REQ_A515_ACCESS_CONTROL_POLICY = EvidenceRequirement(
    id            = "req:A.5.15:access_control_policy",
    control_ref   = "A.5.15",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Access Control Policy",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.15 requires rules controlling physical and logical access based on business and information security requirements. Evidence is an access control policy stating the principles and decision rules. The supporting procedure (rights provisioning) lives at A.5.18",
    must_contain  = [
        ChecklistItem("item:A.5.15:physical_rules",  "Physical access rules (premises, server rooms, restricted areas)", "must", False, "A.5.15 — physical access"),
        ChecklistItem("item:A.5.15:logical_rules",   "Logical access rules (systems, applications, network segments)", "must", False, "A.5.15 — logical access"),
        ChecklistItem("item:A.5.15:rbac",            "Role-based access control as the default model", "must", False, "A.5.15 — based on business requirements"),
        ChecklistItem("item:A.5.15:least_privilege", "Principle of least privilege stated", "must", False, "A.5.15 — security requirements"),
        ChecklistItem("item:A.5.15:need_to_know",    "Principle of need-to-know stated", "must", False, "A.5.15 — security requirements"),
        ChecklistItem("item:A.5.15:authorisation",   "Authorisation procedure for granting access (links to A.5.18)", "must", False, "A.5.15 — established"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.15:emergency_access","Emergency / break-glass access provisions", "should", False, "Operational continuity"),
        ChecklistItem("item:A.5.15:periodic_review", "Periodic access review cadence stated (links to A.5.18 procedure)", "should", False, "Drift prevention"),
    ],
)

REQ_A516_IDENTITY_MANAGEMENT = EvidenceRequirement(
    id            = "req:A.5.16:identity_management_procedure",
    control_ref   = "A.5.16",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Identity Lifecycle Management Procedure",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.16 requires the full lifecycle of identities to be managed. Evidence is a procedure covering creation, modification, suspension, and termination of identities, with timeliness and accountability stated",
    must_contain  = [
        ChecklistItem("item:A.5.16:creation",        "Identity creation steps (verification of person, naming convention, initial entitlements)", "must", False, "A.5.16 — lifecycle"),
        ChecklistItem("item:A.5.16:modification",    "Modification steps for role changes (add/remove entitlements)", "must", False, "A.5.16 — lifecycle"),
        ChecklistItem("item:A.5.16:suspension",      "Suspension steps for leave of absence or risk events", "must", False, "A.5.16 — lifecycle"),
        ChecklistItem("item:A.5.16:termination",     "Termination steps with stated deactivation timeline (e.g. within 24h of last day)", "must", False, "A.5.16 — lifecycle"),
        ChecklistItem("item:A.5.16:unique_identity", "Unique identity per person (no shared user accounts for individuals)", "must", False, "A.5.16 — managed"),
        ChecklistItem("item:A.5.16:ownership",       "Ownership of each lifecycle phase (HR triggers, IT executes, manager approves)", "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.16:attestation",     "Periodic identity attestation cadence (e.g. annual recertification)", "should", False, "Drift prevention"),
        ChecklistItem("item:A.5.16:service_accounts","Service / shared / non-human account governance", "should", False, "Coverage of edge cases"),
    ],
)

REQ_A517_AUTHENTICATION_INFORMATION = EvidenceRequirement(
    id            = "req:A.5.17:authentication_information_procedure",
    control_ref   = "A.5.17",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Authentication Information Management Procedure",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.17 requires authentication information (passwords, tokens, keys) to be allocated and managed by a controlled process, with personnel advised on appropriate handling. Evidence is a procedure covering allocation, storage, and user guidance",
    must_contain  = [
        ChecklistItem("item:A.5.17:allocation",      "Initial allocation method for authentication information (in-person, secure channel, ephemeral link)", "must", False, "A.5.17 — allocation"),
        ChecklistItem("item:A.5.17:transmission",    "Transmission method requirements (out-of-band, encrypted, not over the same channel as the identity)", "must", False, "A.5.17 — management process"),
        ChecklistItem("item:A.5.17:complexity",      "Password / credential complexity and rotation requirements", "must", False, "A.5.17 — management"),
        ChecklistItem("item:A.5.17:storage",         "Storage requirements (hashed + salted, vaulted, never plaintext)", "must", False, "A.5.17 — management"),
        ChecklistItem("item:A.5.17:reset",           "Reset / recovery process with identity verification", "must", False, "A.5.17 — management"),
        ChecklistItem("item:A.5.17:user_advisory",   "Advisory guidance to personnel on protecting their authentication information", "must", False, "A.5.17 — advising personnel"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.17:mfa",             "Multi-factor authentication where required by access policy", "should", False, "Modern baseline"),
        ChecklistItem("item:A.5.17:factor_classes",  "Authentication factor classes documented (knowledge, possession, inherence)", "should", False, "Risk-based mapping"),
    ],
)

REQ_A519_SUPPLIER_RISK_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.19:supplier_risk_procedure",
    control_ref   = "A.5.19",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Supplier Information Security Risk Management Procedure",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.19 requires processes and procedures to manage information security risks arising from supplier products and services. Evidence is a supplier risk management procedure covering inventory, due diligence, risk classification, and ongoing monitoring",
    must_contain  = [
        ChecklistItem("item:A.5.19:inventory",        "Supplier inventory maintained (who they are, what they provide, criticality)", "must", False, "A.5.19 — manage"),
        ChecklistItem("item:A.5.19:risk_classification","Risk classification approach per supplier (tier or category)", "must", False, "A.5.19 — risks associated"),
        ChecklistItem("item:A.5.19:due_diligence",    "Due diligence steps before engagement (questionnaire, attestation review, audit)", "must", False, "A.5.19 — manage"),
        ChecklistItem("item:A.5.19:ongoing_monitoring","Ongoing monitoring approach (periodic reassessment, event-triggered review)", "must", False, "A.5.19 — manage"),
        ChecklistItem("item:A.5.19:exit_planning",    "Exit considerations (data return/destruction, transition planning)", "must", False, "A.5.19 — manage"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.19:tiering_model",    "Tiering model with concrete criteria (data sensitivity, dependency, financial exposure)", "should", False, "Proportionality"),
        ChecklistItem("item:A.5.19:questionnaire_ref","Reference to standard supplier security questionnaire", "should", False, "Consistency"),
    ],
)

REQ_A520_SUPPLIER_AGREEMENT_TEMPLATE = EvidenceRequirement(
    id            = "req:A.5.20:supplier_agreement_security_template",
    control_ref   = "A.5.20",
    standard_id   = "ISO27001:2022",
    evidence_type = "agreement_template",
    title         = "Supplier Agreement Security Requirements Template",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.20 requires information security requirements to be established and agreed with each supplier based on the relationship type. Evidence is a standard set of security clauses or a template attached to supplier agreements",
    must_contain  = [
        ChecklistItem("item:A.5.20:minimum_requirements","Minimum security requirements (controls baseline, certifications expected)", "must", False, "A.5.20 — security requirements established"),
        ChecklistItem("item:A.5.20:data_handling",     "Data handling requirements (encryption at rest and in transit, location/sovereignty)", "must", False, "A.5.20 — relevant security requirements"),
        ChecklistItem("item:A.5.20:incident_notification","Incident notification clause with timeline (e.g. within 24h of detection)", "must", False, "A.5.20 — agreed"),
        ChecklistItem("item:A.5.20:audit_rights",      "Audit rights (right to audit, accept attestations like ISO 27001 / SOC 2 in lieu)", "must", False, "A.5.20 — agreed"),
        ChecklistItem("item:A.5.20:subprocessor_limits","Sub-processor / fourth-party restrictions and approval process", "must", False, "A.5.20 — supplier relationship type"),
        ChecklistItem("item:A.5.20:termination_return","Termination + data return/destruction clauses", "must", False, "A.5.20 — agreed"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.20:security_sla",      "Security-specific SLAs (e.g. patching cadence, MFA requirements)", "should", False, "Measurable accountability"),
        ChecklistItem("item:A.5.20:tier_variants",     "Variant clause sets per supplier tier", "should", False, "Proportionality"),
    ],
)

REQ_A521_ICT_SUPPLY_CHAIN = EvidenceRequirement(
    id            = "req:A.5.21:ict_supply_chain_procedure",
    control_ref   = "A.5.21",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "ICT Supply Chain Information Security Procedure",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.21 requires processes and procedures to manage information security risks in the ICT products and services supply chain. Evidence is a procedure covering sourcing, integrity verification, sub-supplier visibility, and end-of-life",
    must_contain  = [
        ChecklistItem("item:A.5.21:sourcing_controls", "Sourcing controls (approved vendor list, banned-vendor list, country-of-origin considerations)", "must", False, "A.5.21 — manage risks"),
        ChecklistItem("item:A.5.21:integrity_verification","Component integrity verification (signed firmware, signed packages, hash verification)", "must", False, "A.5.21 — ICT products"),
        ChecklistItem("item:A.5.21:subsupplier_visibility","Sub-supplier visibility expectations (disclosure of components, fourth-party listing)", "must", False, "A.5.21 — supply chain"),
        ChecklistItem("item:A.5.21:patching_expectations","Support and patching expectations stated for each ICT product/service", "must", False, "A.5.21 — manage risks"),
        ChecklistItem("item:A.5.21:end_of_life",       "End-of-life planning (replacement before vendor support ends)", "must", False, "A.5.21 — manage"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.21:sbom",              "SBOM expectations for software components", "should", False, "Modern supply chain hygiene"),
        ChecklistItem("item:A.5.21:secure_development","Secure development practice expectations for software vendors", "should", False, "Vendor maturity bar"),
    ],
)

REQ_A522_SUPPLIER_REVIEW = EvidenceRequirement(
    id            = "req:A.5.22:supplier_review_record",
    control_ref   = "A.5.22",
    standard_id   = "ISO27001:2022",
    evidence_type = "review_record",
    title         = "Supplier Information Security Review Records",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.22 requires regular monitoring, review, evaluation, and change management of supplier information security practices and service delivery. Evidence is a record (or set of records) of reviews completed per supplier",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:A.5.22:review_schedule",  "Review schedule per supplier (cadence proportional to tier)", "must", False, "A.5.22 — regularly"),
        ChecklistItem("item:A.5.22:scope",            "Scope of review (security practices, service delivery, changes since last review)", "must", False, "A.5.22 — monitor, review, evaluate"),
        ChecklistItem("item:A.5.22:findings",         "Findings recorded per review with severity", "must", False, "A.5.22 — review"),
        ChecklistItem("item:A.5.22:change_management","Change management trigger when supplier changes scope, location, or sub-processors", "must", False, "A.5.22 — manage change"),
        ChecklistItem("item:A.5.22:escalation",       "Escalation criteria for findings (when does a finding terminate the relationship)", "must", False, "A.5.22 — manage"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.22:metrics",          "KPIs / metrics tracked per supplier (incidents, SLA breaches)", "should", False, "Measurable monitoring"),
        ChecklistItem("item:A.5.22:attestations_accepted","Third-party attestations accepted in lieu of direct audit", "should", False, "Efficiency"),
    ],
)

REQ_A525_EVENT_TRIAGE = EvidenceRequirement(
    id            = "req:A.5.25:event_assessment_procedure",
    control_ref   = "A.5.25",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Security Event Assessment and Triage Procedure",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.25 requires the organization to assess information security events and decide whether to categorise them as incidents. Evidence is a triage procedure covering detection sources, assessment criteria, decision authority, and handoff to incident response (A.5.26)",
    must_contain  = [
        ChecklistItem("item:A.5.25:detection_sources","Detection sources enumerated (monitoring, user reports, third parties)", "must", False, "A.5.25 — events"),
        ChecklistItem("item:A.5.25:assessment_criteria","Assessment criteria (impact, scope, certainty) for classifying severity", "must", False, "A.5.25 — assess"),
        ChecklistItem("item:A.5.25:decision_authority","Decision authority named (who decides event vs incident vs false positive)", "must", False, "A.5.25 — decide"),
        ChecklistItem("item:A.5.25:classification_scale","Classification scale used (event, near-miss, incident with severity)", "must", False, "A.5.25 — categorized"),
        ChecklistItem("item:A.5.25:triage_timeline", "Timeline for triage decision after detection", "must", False, "A.5.25 — assess and decide"),
        ChecklistItem("item:A.5.25:handoff",         "Handoff to incident response process (A.5.26) when classified as incident", "must", False, "A.5.25 — incidents"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.25:severity_matrix", "Severity matrix with concrete examples", "should", False, "Consistency across triagers"),
        ChecklistItem("item:A.5.25:automation",      "Automation or playbook references for common event types", "should", False, "Scalability"),
    ],
)


# ── ISO 27001 Annex A.5 — incident response (A.5.26 worked example) ──────────
# A.5.26 says: "Information security incidents shall be responded to in
# accordance with the documented procedures." Single-leaf: the procedure
# document itself. Periodic-review concerns live at A.5.36 (compliance
# review) — not duplicated here. Triage decision (event → incident) lives at
# A.5.25; lessons-learned at A.5.27; evidence handling at A.5.28. We point
# to those via SHOULD items rather than redundant MUST items, so a single
# procedure document that covers them all satisfies the leaf cleanly.

REQ_A526_INCIDENT_RESPONSE_PROCEDURE = EvidenceRequirement(
    id            = "req:A.5.26:incident_response_procedure",
    control_ref   = "A.5.26",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Incident Response Procedure",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.26 requires documented procedures for responding to information security incidents end-to-end. Evidence is a procedure document covering roles, containment, investigation, recovery, communication, and post-incident review",
    must_contain  = [
        ChecklistItem("item:A.5.26:roles",          "Roles and responsibilities for incident response defined (Incident Manager, security team, comms lead, legal)", "must", False, "A.5.26 — execution needs assigned owners"),
        ChecklistItem("item:A.5.26:containment",    "Containment steps documented (immediate actions to limit damage)", "must", False, "A.5.26 — respond to incidents"),
        ChecklistItem("item:A.5.26:investigation",  "Investigation steps defined (root cause analysis, timeline reconstruction)", "must", False, "A.5.26 — documented procedures"),
        ChecklistItem("item:A.5.26:eradication",    "Eradication and recovery steps documented (restore secure state)", "must", False, "A.5.26 — respond to incidents"),
        ChecklistItem("item:A.5.26:communication",  "Internal and external communication criteria specified (who is informed, when, by whom)", "must", False, "A.5.26 — documented procedures"),
        ChecklistItem("item:A.5.26:post_review",    "Post-incident review step required after closure", "must", False, "A.5.26 — supports A.5.27 lessons-learned"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.26:classification_ref", "References incident classification used at triage (links to A.5.25)", "should", False, "Triage gates the response path"),
        ChecklistItem("item:A.5.26:evidence_ref",       "References evidence handling procedure (links to A.5.28)",            "should", False, "Forensic preservation"),
        ChecklistItem("item:A.5.26:authority_contacts", "References authority/regulator contact list (links to A.5.5)",        "should", False, "Some incidents trigger external notification"),
        ChecklistItem("item:A.5.26:exercise_freq",      "Tabletop or simulation frequency stated (annual or more often)",       "should", False, "Validates the procedure works under pressure"),
    ],
)

REQ_A527_LESSONS_LEARNED = EvidenceRequirement(
    id            = "req:A.5.27:lessons_learned_procedure",
    control_ref   = "A.5.27",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Lessons Learned from Information Security Incidents",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.27 requires knowledge from incidents to be used to strengthen and improve information security controls. Evidence is a lessons-learned procedure with capture, action assignment, and feedback into the broader control framework",
    must_contain  = [
        ChecklistItem("item:A.5.27:trigger",        "Post-incident review trigger (every incident above a threshold, or all incidents)", "must", False, "A.5.27 — knowledge gained from incidents"),
        ChecklistItem("item:A.5.27:capture_format", "Lessons capture format (what worked, what didn't, root causes, control gaps)", "must", False, "A.5.27 — knowledge"),
        ChecklistItem("item:A.5.27:actions",        "Action items assigned to owners with target dates", "must", False, "A.5.27 — strengthen and improve"),
        ChecklistItem("item:A.5.27:tracking",       "Tracking actions to closure with status updates", "must", False, "A.5.27 — improve"),
        ChecklistItem("item:A.5.27:feedback_loop",  "Feedback loop into risk register, control catalogue, and training programmes", "must", False, "A.5.27 — information security controls"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.27:kb_update",      "Knowledge base or runbook update step", "should", False, "Captured knowledge stays useful"),
        ChecklistItem("item:A.5.27:training_refresh","Training refresh step where lessons reveal awareness gaps", "should", False, "People dimension"),
    ],
)

REQ_A528_EVIDENCE_HANDLING = EvidenceRequirement(
    id            = "req:A.5.28:evidence_collection_procedure",
    control_ref   = "A.5.28",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Evidence Identification, Collection, and Preservation Procedure",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.28 requires procedures for identification, collection, acquisition, and preservation of evidence related to information security events. Evidence is a procedure covering forensic handling end-to-end",
    must_contain  = [
        ChecklistItem("item:A.5.28:identification",  "Identification step (what counts as evidence — logs, images, physical media, witness statements)", "must", False, "A.5.28 — identification"),
        ChecklistItem("item:A.5.28:chain_of_custody","Chain of custody requirements (who handled what, when, where stored)", "must", False, "A.5.28 — preservation"),
        ChecklistItem("item:A.5.28:acquisition",     "Acquisition method per evidence type (disk imaging, log export, memory capture)", "must", False, "A.5.28 — acquisition"),
        ChecklistItem("item:A.5.28:preservation",    "Preservation method (read-only storage, hashes recorded, secure vault)", "must", False, "A.5.28 — preservation"),
        ChecklistItem("item:A.5.28:retention",       "Retention period stated (often driven by legal and regulatory)", "must", False, "A.5.28 — preservation"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.28:legal_admissibility","Legal admissibility considerations (jurisdictional rules)", "should", False, "Evidence usable in court / regulatory"),
        ChecklistItem("item:A.5.28:third_party_forensics","Third-party forensic engagement procedure if outsourced", "should", False, "Operational flexibility"),
    ],
)

REQ_A529_DISRUPTION_SECURITY = EvidenceRequirement(
    id            = "req:A.5.29:information_security_during_disruption",
    control_ref   = "A.5.29",
    standard_id   = "ISO27001:2022",
    evidence_type = "plan",
    title         = "Information Security During Disruption Plan",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.29 requires planning to maintain information security at an appropriate level during disruption. Evidence is a plan (often a BCP security annex) covering which controls must keep working under disruption, fallback measures, and post-disruption restoration",
    must_contain  = [
        ChecklistItem("item:A.5.29:scenarios",       "Disruption scenarios considered (cyber attack, natural event, supplier failure)", "must", False, "A.5.29 — disruption"),
        ChecklistItem("item:A.5.29:must_continue",   "Security controls that must continue operating during disruption", "must", False, "A.5.29 — maintain information security"),
        ChecklistItem("item:A.5.29:fallback",        "Fallback or compensating security measures when primary controls fail", "must", False, "A.5.29 — appropriate level"),
        ChecklistItem("item:A.5.29:communication",   "Communication during disruption (internal, external, regulators)", "must", False, "A.5.29 — plan"),
        ChecklistItem("item:A.5.29:restoration",     "Restoration of normal security controls after disruption ends", "must", False, "A.5.29 — maintain"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.29:bcp_integration", "Integration with the broader Business Continuity Plan", "should", False, "Coherence with BCP framework"),
        ChecklistItem("item:A.5.29:test_schedule",   "Test schedule for the disruption plan", "should", False, "Plans must be exercised"),
    ],
)

REQ_A530_ICT_CONTINUITY = EvidenceRequirement(
    id            = "req:A.5.30:ict_readiness_for_business_continuity",
    control_ref   = "A.5.30",
    standard_id   = "ISO27001:2022",
    evidence_type = "plan",
    title         = "ICT Readiness for Business Continuity Plan",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.30 requires ICT readiness to be planned, implemented, maintained, and tested per business continuity objectives. Evidence is an ICT continuity plan with recovery procedures, backup arrangements, and test records",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:A.5.30:rto_rpo",         "Recovery Time and Recovery Point Objectives per ICT service (BIA-derived)", "must", False, "A.5.30 — business continuity objectives"),
        ChecklistItem("item:A.5.30:recovery_procedures","Recovery procedures documented per ICT service", "must", False, "A.5.30 — ICT readiness"),
        ChecklistItem("item:A.5.30:backup",          "Backup arrangements (frequency, retention, location separation, restore tested)", "must", False, "A.5.30 — implemented"),
        ChecklistItem("item:A.5.30:failover",        "Failover or redundancy arrangements for critical services", "must", False, "A.5.30 — readiness"),
        ChecklistItem("item:A.5.30:test_records",    "Test records (last test date, outcome, gaps identified, remediation status)", "must", False, "A.5.30 — tested"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.30:scenario_coverage","Test scenarios cover both partial-failure and full-outage cases", "should", False, "Test realism"),
        ChecklistItem("item:A.5.30:communication_tree","Communication tree for ICT outages (who is informed, escalation)", "should", False, "Coordination"),
    ],
)

REQ_A531_LEGAL_REGULATORY_REGISTER = EvidenceRequirement(
    id            = "req:A.5.31:legal_regulatory_register",
    control_ref   = "A.5.31",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Legal, Statutory, Regulatory and Contractual Requirements Register",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.31 requires applicable legal, statutory, regulatory, and contractual requirements relevant to information security to be identified, documented, and kept up to date. Evidence is a register that enumerates them and maps each to the organization's compliance approach",
    freshness_days = 180,
    must_contain  = [
        ChecklistItem("item:A.5.31:laws_listed",       "Applicable laws and regulations listed (GDPR, sectoral, jurisdictional)", "must", False, "A.5.31 — identified"),
        ChecklistItem("item:A.5.31:jurisdictions",     "Jurisdictions covered explicitly (HQ, places of operation, customer locations)", "must", False, "A.5.31 — relevant"),
        ChecklistItem("item:A.5.31:contractual",       "Contractual obligations summarised (customer contracts, regulator agreements)", "must", False, "A.5.31 — contractual requirements"),
        ChecklistItem("item:A.5.31:compliance_approach","Approach for compliance per item (how we meet it, controls referenced)", "must", False, "A.5.31 — approach to meet"),
        ChecklistItem("item:A.5.31:owner_per_item",    "Owner named per requirement (who tracks change and compliance)", "must", False, "Accountability"),
        ChecklistItem("item:A.5.31:last_verified",     "Last-verified or last-reviewed date per entry", "must", False, "A.5.31 — kept up to date"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.31:evidence_links",    "Links to evidence of compliance per requirement", "should", False, "Audit traceability"),
        ChecklistItem("item:A.5.31:change_monitoring", "Source for change monitoring (legal counsel, regulator alerts, industry feed)", "should", False, "Currency"),
    ],
)

REQ_A532_INTELLECTUAL_PROPERTY = EvidenceRequirement(
    id            = "req:A.5.32:intellectual_property_procedure",
    control_ref   = "A.5.32",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Intellectual Property Rights Protection Procedure",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.32 requires appropriate procedures to protect intellectual property rights. Evidence is a procedure covering both the organization's IPR and respect for third-party IPR",
    must_contain  = [
        ChecklistItem("item:A.5.32:scope_iprs",       "Scope of IPRs covered (software licences, trademarks, copyrights, patents, trade secrets)", "must", False, "A.5.32 — IPR"),
        ChecklistItem("item:A.5.32:licensed_inventory","Inventory of licensed software with entitlements and expiry", "must", False, "A.5.32 — protect"),
        ChecklistItem("item:A.5.32:usage_controls",   "Usage controls preventing unlicensed software installation", "must", False, "A.5.32 — appropriate procedures"),
        ChecklistItem("item:A.5.32:third_party_respect","Third-party IPR respect (citation, attribution, royalty payment)", "must", False, "A.5.32 — protect intellectual property rights"),
        ChecklistItem("item:A.5.32:employee_creations","Employee-creations statement (who owns work product, open-source contribution policy)", "must", False, "A.5.32 — protect"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.32:audit_cadence",    "Audit cadence for software licence compliance", "should", False, "Drift prevention"),
        ChecklistItem("item:A.5.32:renewal_tracking", "License renewal tracking process", "should", False, "Continuity of use"),
    ],
)

REQ_A533_RECORDS_PROTECTION = EvidenceRequirement(
    id            = "req:A.5.33:records_protection_policy",
    control_ref   = "A.5.33",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Records Retention and Protection Policy",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.33 requires records to be protected from loss, destruction, falsification, unauthorized access, and unauthorized release. Evidence is a records retention/protection policy that classifies records, sets retention, and specifies protection",
    must_contain  = [
        ChecklistItem("item:A.5.33:records_schedule", "Records inventory or schedule (which record classes the organization holds)", "must", False, "A.5.33 — records"),
        ChecklistItem("item:A.5.33:retention_periods","Retention period per record class (driven by legal, regulatory, business need)", "must", False, "A.5.33 — protected"),
        ChecklistItem("item:A.5.33:protection_requirements","Protection requirements (access control, encryption at rest, immutability where needed)", "must", False, "A.5.33 — protect from loss, destruction, falsification, unauthorized access and release"),
        ChecklistItem("item:A.5.33:retention_drivers","Legal/regulatory drivers per retention period stated", "must", False, "A.5.33 — protected"),
        ChecklistItem("item:A.5.33:disposal",         "Disposal procedure at end of retention (secure destruction, certificate of destruction)", "must", False, "A.5.33 — protected"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.33:format_guidance",  "Format-specific guidance (paper vs digital records)", "should", False, "Practical implementation"),
        ChecklistItem("item:A.5.33:legal_hold",       "Legal hold provisions overriding normal retention", "should", False, "Litigation readiness"),
    ],
)

REQ_A534_PII_PROTECTION = EvidenceRequirement(
    id            = "req:A.5.34:privacy_and_pii_protection_policy",
    control_ref   = "A.5.34",
    standard_id   = "ISO27001:2022",
    evidence_type = "policy",
    title         = "Privacy and PII Protection Policy",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.34 requires identification of and compliance with privacy and PII protection requirements per applicable law, regulation, and contract. Evidence is a privacy policy (or PIMS-aligned policy) that names the law(s), the PII handled, and the controls",
    must_contain  = [
        ChecklistItem("item:A.5.34:applicable_laws", "Applicable privacy laws identified (GDPR, regional equivalents)", "must", False, "A.5.34 — applicable laws and regulations"),
        ChecklistItem("item:A.5.34:pii_inventory",   "PII categories or inventory referenced (links to GDPR Art.30 records)", "must", False, "A.5.34 — protection of PII"),
        ChecklistItem("item:A.5.34:lawful_basis",    "Lawful basis identified per processing activity (where law requires)", "must", False, "A.5.34 — applicable laws"),
        ChecklistItem("item:A.5.34:data_subject_rights","Data subject rights enabled (access, rectification, erasure, portability where applicable)", "must", False, "A.5.34 — preservation of privacy"),
        ChecklistItem("item:A.5.34:retention_minimisation","Retention and data minimisation requirements", "must", False, "A.5.34 — preservation of privacy"),
        ChecklistItem("item:A.5.34:security_controls_ref","References security controls applied to PII (links to A.8.x)", "must", False, "A.5.34 — protection of PII"),
        ChecklistItem("item:A.5.34:breach_handling", "Breach handling reference (links to A.5.26 + GDPR Art.33)", "must", False, "A.5.34 — applicable laws"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.34:dpia_process",    "PIA / DPIA process reference for high-risk processing", "should", False, "Pre-emptive risk handling"),
        ChecklistItem("item:A.5.34:dpo_role",        "DPO or Privacy Officer role named", "should", False, "Accountability"),
    ],
)

REQ_A535_INDEPENDENT_REVIEW = EvidenceRequirement(
    id            = "req:A.5.35:independent_review_report",
    control_ref   = "A.5.35",
    standard_id   = "ISO27001:2022",
    evidence_type = "audit_report",
    title         = "Independent Information Security Review Report",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.35 requires the organization's approach to information security to be reviewed independently at planned intervals (or on significant change). Evidence is an independent review report covering people, process, and technology",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:A.5.35:independence",    "Independence of the reviewer demonstrated (separate function, external auditor, or rotating internal reviewer)", "must", False, "A.5.35 — reviewed independently"),
        ChecklistItem("item:A.5.35:scope",           "Scope covers people, processes, and technologies", "must", False, "A.5.35 — including people, processes and technologies"),
        ChecklistItem("item:A.5.35:review_date",     "Review date and period covered", "must", False, "A.5.35 — planned intervals"),
        ChecklistItem("item:A.5.35:findings",        "Findings listed with severity", "must", False, "A.5.35 — review"),
        ChecklistItem("item:A.5.35:recommendations", "Recommendations stated", "must", False, "A.5.35 — review"),
        ChecklistItem("item:A.5.35:management_response","Management response to findings (accept, remediate, transfer)", "must", False, "Closes the loop"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.35:reviewer_credentials","External auditor accreditation or internal reviewer qualifications", "should", False, "Reviewer credibility"),
        ChecklistItem("item:A.5.35:prior_review_compare","Comparison or movement from prior review's findings", "should", False, "Progress tracking"),
    ],
)

REQ_A536_COMPLIANCE_REVIEW = EvidenceRequirement(
    id            = "req:A.5.36:compliance_review_record",
    control_ref   = "A.5.36",
    standard_id   = "ISO27001:2022",
    evidence_type = "review_record",
    title         = "Compliance Review Records (Policies, Rules, Standards)",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.36 requires compliance with the organization's information security policy, topic-specific policies, rules, and standards to be regularly reviewed. Evidence is a record (or set of records) showing what was reviewed, how, and what was found",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:A.5.36:schedule",        "Review schedule covering all in-scope policies, rules, and standards", "must", False, "A.5.36 — regularly reviewed"),
        ChecklistItem("item:A.5.36:scope",           "Scope (which policies / rules / standards reviewed in each cycle)", "must", False, "A.5.36 — information security policy, topic-specific policies, rules and standards"),
        ChecklistItem("item:A.5.36:method",          "Method used (control sampling, formal audit, automated check, attestation)", "must", False, "A.5.36 — reviewed"),
        ChecklistItem("item:A.5.36:findings",        "Findings recorded per review with severity", "must", False, "A.5.36 — review"),
        ChecklistItem("item:A.5.36:corrective_actions","Corrective actions tracked to closure", "must", False, "Closes the loop"),
        ChecklistItem("item:A.5.36:owner",           "Named owner of the compliance review function", "must", False, "Accountability"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.36:continuous_compliance","Continuous-compliance monitoring tooling where used", "should", False, "Scale and timeliness"),
        ChecklistItem("item:A.5.36:exception_register","Exception register for accepted non-conformities with expiry", "should", False, "Realistic operations"),
    ],
)

REQ_A537_OPERATING_PROCEDURES = EvidenceRequirement(
    id            = "req:A.5.37:operating_procedures_register",
    control_ref   = "A.5.37",
    standard_id   = "ISO27001:2022",
    evidence_type = "register",
    title         = "Documented Operating Procedures Register",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.5.37 requires operating procedures for information processing facilities to be documented and made available to personnel who need them. Evidence is a register or catalogue of operating procedures with availability arrangements",
    must_contain  = [
        ChecklistItem("item:A.5.37:procedure_inventory","Inventory of operating procedures (which facilities/systems they cover)", "must", False, "A.5.37 — documented"),
        ChecklistItem("item:A.5.37:scope_coverage",     "Scope coverage stated (every information processing facility represented)", "must", False, "A.5.37 — information processing facilities"),
        ChecklistItem("item:A.5.37:availability",       "Availability mechanism stated (where personnel find them — intranet location, runbook system)", "must", False, "A.5.37 — made available to personnel"),
        ChecklistItem("item:A.5.37:owner_per_procedure","Ownership per procedure (who keeps it current)", "must", False, "A.5.37 — documented"),
        ChecklistItem("item:A.5.37:version_control",    "Version control with last-updated and review-due dates", "must", False, "A.5.37 — documented"),
    ],
    should_contain= [
        ChecklistItem("item:A.5.37:update_triggers",    "Update triggers (system change, control change, finding-driven update)", "should", False, "Currency over time"),
        ChecklistItem("item:A.5.37:template",           "Template adherence for procedures (consistent shape across the catalogue)", "should", False, "Reviewability"),
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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

REQ_A82_PRIVILEGED_ACCESS = EvidenceRequirement(
    id            = "req:A.8.2:privileged_access_procedure",
    control_ref   = "A.8.2",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Privileged Access Rights Management Procedure",
    trigger_type  = "universal",
    trigger_event = None,
    description   = "A.8.2 requires the allocation and use of privileged access rights to be restricted and managed. Evidence is a procedure governing privileged account lifecycle, use, and oversight",
    freshness_days = 365,
    must_contain  = [
        ChecklistItem("item:A.8.2:privileged_inventory","Inventory of privileged accounts (human and service) per system", "must", False, "A.8.2 — privileged access rights"),
        ChecklistItem("item:A.8.2:least_privilege","Least-privilege allocation principle stated and enforced", "must", False, "A.8.2 — restricted"),
        ChecklistItem("item:A.8.2:separate_accounts","Separate accounts for administrative actions (admin account distinct from daily-use)", "must", False, "A.8.2 — managed"),
        ChecklistItem("item:A.8.2:mfa_mandatory","MFA mandatory for all privileged logins", "must", False, "A.8.2 — restricted"),
        ChecklistItem("item:A.8.2:logging",       "Logging of privileged actions (links to A.8.15)", "must", False, "A.8.2 — managed"),
        ChecklistItem("item:A.8.2:periodic_review","Periodic review of privileged account entitlements (typically quarterly)", "must", False, "A.8.2 — managed"),
        ChecklistItem("item:A.8.2:break_glass",   "Break-glass account governance (sealed credentials, post-use review)", "must", False, "Emergency access without weak ongoing exposure"),
    ],
    should_contain= [
        ChecklistItem("item:A.8.2:pam_tooling",   "PAM tooling used (vaulting, session recording)", "should", False, "Modern baseline"),
        ChecklistItem("item:A.8.2:jit_elevation", "Just-in-time / time-bound privilege elevation", "should", False, "Reduces standing privilege"),
    ],
)

REQ_A83_INFORMATION_ACCESS_RESTRICTION = EvidenceRequirement(
    id            = "req:A.8.3:information_access_restriction_procedure",
    control_ref   = "A.8.3",
    standard_id   = "ISO27001:2022",
    evidence_type = "procedure",
    title         = "Information Access Restriction Procedure",
    trigger_type  = "universal",
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
    trigger_event = None,
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
            trigger_event = None,
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
            trigger_event = None,
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
            trigger_event = None,
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
            trigger_event = None,
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
            trigger_event = None,
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
    REQ_INCIDENT_RESPONSE,
    REQ_DATA_MASKING,
    REQ_ACCESS_RIGHTS,

    # Universal — ISO 27001 Annex A.5.1 (four-leaf curation, commit 3)
    REQ_A51_ISP_POLICY,
    REQ_A51_APPROVAL,
    REQ_A51_COMMUNICATION,
    REQ_A51_REVIEW,

    # Universal — ISO 27001 Annex A.5 bulk curation (Phase B, 2026-05-22).
    # Numerical order; A.5.18 / A.5.23 / A.5.24 already exist above as
    # REQ_ACCESS_RIGHTS / REQ_CLOUD_SERVICES_POLICY / REQ_INCIDENT_RESPONSE.
    REQ_A52_ROLES_RESPONSIBILITIES,
    REQ_A53_SEGREGATION_OF_DUTIES,
    REQ_A54_MANAGEMENT_RESPONSIBILITIES,
    REQ_A55_AUTHORITY_CONTACTS,
    REQ_A56_SIG_CONTACTS,
    REQ_A57_THREAT_INTELLIGENCE,
    REQ_A58_PROJECT_MANAGEMENT_SECURITY,
    REQ_A59_ASSET_INVENTORY,
    REQ_A510_ACCEPTABLE_USE,
    REQ_A511_RETURN_OF_ASSETS,
    REQ_A512_INFORMATION_CLASSIFICATION,
    REQ_A513_INFORMATION_LABELLING,
    REQ_A514_INFORMATION_TRANSFER,
    REQ_A515_ACCESS_CONTROL_POLICY,
    REQ_A516_IDENTITY_MANAGEMENT,
    REQ_A517_AUTHENTICATION_INFORMATION,
    REQ_A519_SUPPLIER_RISK_PROCEDURE,
    REQ_A520_SUPPLIER_AGREEMENT_TEMPLATE,
    REQ_A521_ICT_SUPPLY_CHAIN,
    REQ_A522_SUPPLIER_REVIEW,
    REQ_A525_EVENT_TRIAGE,
    REQ_A526_INCIDENT_RESPONSE_PROCEDURE,
    REQ_A527_LESSONS_LEARNED,
    REQ_A528_EVIDENCE_HANDLING,
    REQ_A529_DISRUPTION_SECURITY,
    REQ_A530_ICT_CONTINUITY,
    REQ_A531_LEGAL_REGULATORY_REGISTER,
    REQ_A532_INTELLECTUAL_PROPERTY,
    REQ_A533_RECORDS_PROTECTION,
    REQ_A534_PII_PROTECTION,
    REQ_A535_INDEPENDENT_REVIEW,
    REQ_A536_COMPLIANCE_REVIEW,
    REQ_A537_OPERATING_PROCEDURES,

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
    REQ_A82_PRIVILEGED_ACCESS,
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
    REQ_RECORDS_PROCESSING,

    # Profile-fact triggered
    REQ_DPA,
    REQ_CLOUD_SERVICES_POLICY,
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
