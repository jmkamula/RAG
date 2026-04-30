"""
ArionComply — Document Requirements

Defines what documents are required per control and what each must contain.
Three trigger types:
  universal     → required for every client in scope
  profile_fact  → required when a client fact is true
  operational   → required when an event occurs

Each DocumentRequirement links to:
  - One RequirementNode (the control it satisfies)
  - Multiple ChecklistItems (what the document must contain)

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
class DocumentRequirement:
    id:               str          # "req:{control_ref}:{doc_type_slug}"
    control_ref:      str          # "A.8.24"
    standard_id:      str          # "ISO27001:2022"
    document_type:    str          # "policy" | "procedure" | "dpa" | "programme" etc.
    document_title:   str          # human-readable e.g. "Use of Cryptography Policy"
    trigger_type:     str          # "universal" | "profile_fact" | "operational"
                                   # profile_fact: required when ClientFact is True
                                   # the specific fact is encoded in ClientFacts/ObligationRule
                                   # not stored here — derived from obligation chain
    trigger_event:    str | None   # event name when trigger_type == "operational"
                                   # e.g. "personal_data_breach", "data_subject_access_request"
    description:      str          # why this document is required
    must_contain:     list[ChecklistItem] = field(default_factory=list)
    should_contain:   list[ChecklistItem] = field(default_factory=list)


# ── Universal documents — ISO 27001 ───────────────────────────────────────────

REQ_ISMS_SCOPE = DocumentRequirement(
    id            = "req:4.3:isms_scope",
    control_ref   = "4.3",
    standard_id   = "ISO27001:2022",
    document_type = "scope_statement",
    document_title= "ISMS Scope Statement",
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

REQ_ISMS_POLICY = DocumentRequirement(
    id            = "req:5.2:information_security_policy",
    control_ref   = "5.2",
    standard_id   = "ISO27001:2022",
    document_type = "policy",
    document_title= "Information Security Policy",
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

REQ_RISK_ASSESSMENT = DocumentRequirement(
    id            = "req:6.1.2:risk_assessment",
    control_ref   = "6.1.2",
    standard_id   = "ISO27001:2022",
    document_type = "risk_assessment",
    document_title= "Information Security Risk Assessment",
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

REQ_RISK_TREATMENT = DocumentRequirement(
    id            = "req:6.1.3:risk_treatment_plan",
    control_ref   = "6.1.3",
    standard_id   = "ISO27001:2022",
    document_type = "risk_treatment_plan",
    document_title= "Risk Treatment Plan",
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

REQ_INTERNAL_AUDIT = DocumentRequirement(
    id            = "req:9.2:internal_audit_programme",
    control_ref   = "9.2",
    standard_id   = "ISO27001:2022",
    document_type = "audit_programme",
    document_title= "Internal Audit Programme",
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

REQ_MANAGEMENT_REVIEW = DocumentRequirement(
    id            = "req:9.3:management_review",
    control_ref   = "9.3",
    standard_id   = "ISO27001:2022",
    document_type = "management_review_minutes",
    document_title= "Management Review Minutes",
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

REQ_PRIVACY_NOTICE_DIRECT = DocumentRequirement(
    id            = "req:Art.13:privacy_notice",
    control_ref   = "Art.13",
    standard_id   = "GDPR:2016/679",
    document_type = "privacy_notice",
    document_title= "Privacy Notice (Data Collected Directly)",
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

REQ_RECORDS_PROCESSING = DocumentRequirement(
    id            = "req:Art.30:records_of_processing",
    control_ref   = "Art.30",
    standard_id   = "GDPR:2016/679",
    document_type = "records_of_processing",
    document_title= "Records of Processing Activities (RoPA)",
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

REQ_DPA = DocumentRequirement(
    id            = "req:Art.28:data_processing_agreement",
    control_ref   = "Art.28",
    standard_id   = "GDPR:2016/679",
    document_type = "data_processing_agreement",
    document_title= "Data Processing Agreement (DPA)",
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

REQ_CLOUD_SERVICES_POLICY = DocumentRequirement(
    id            = "req:A.5.23:cloud_services_policy",
    control_ref   = "A.5.23",
    standard_id   = "ISO27001:2022",
    document_type = "policy",
    document_title= "Information Security for Use of Cloud Services Policy",
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

REQ_ENCRYPTION_POLICY = DocumentRequirement(
    id            = "req:A.8.24:encryption_policy",
    control_ref   = "A.8.24",
    standard_id   = "ISO27001:2022",
    document_type = "policy",
    document_title= "Use of Cryptography Policy",
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

REQ_INCIDENT_RESPONSE = DocumentRequirement(
    id            = "req:A.5.24:incident_response_procedure",
    control_ref   = "A.5.24",
    standard_id   = "ISO27001:2022",
    document_type = "procedure",
    document_title= "Information Security Incident Response Procedure",
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

REQ_DATA_MASKING = DocumentRequirement(
    id            = "req:A.8.11:data_masking_procedure",
    control_ref   = "A.8.11",
    standard_id   = "ISO27001:2022",
    document_type = "procedure",
    document_title= "Data Masking Procedure",
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

REQ_ACCESS_RIGHTS = DocumentRequirement(
    id            = "req:A.5.18:access_rights_procedure",
    control_ref   = "A.5.18",
    standard_id   = "ISO27001:2022",
    document_type = "procedure",
    document_title= "Access Rights Management Procedure",
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

REQ_REMOTE_WORKING = DocumentRequirement(
    id            = "req:A.6.7:remote_working_policy",
    control_ref   = "A.6.7",
    standard_id   = "ISO27001:2022",
    document_type = "policy",
    document_title= "Remote Working Policy",
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

REQ_SECURE_DEVELOPMENT = DocumentRequirement(
    id            = "req:A.8.25:secure_development_policy",
    control_ref   = "A.8.25",
    standard_id   = "ISO27001:2022",
    document_type = "policy",
    document_title= "Secure Development Lifecycle Policy",
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

REQ_BREACH_NOTIFICATION = DocumentRequirement(
    id            = "req:Art.33:breach_notification",
    control_ref   = "Art.33",
    standard_id   = "GDPR:2016/679",
    document_type = "breach_notification",
    document_title= "Personal Data Breach Notification to Supervisory Authority",
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

REQ_DSAR_RESPONSE = DocumentRequirement(
    id            = "req:Art.15:dsar_response",
    control_ref   = "Art.15",
    standard_id   = "GDPR:2016/679",
    document_type = "dsar_response",
    document_title= "Data Subject Access Request Response",
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

# ── Complete registry ──────────────────────────────────────────────────────────

ALL_DOCUMENT_REQUIREMENTS: list[DocumentRequirement] = [
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


def get_requirements_for_control(control_ref: str) -> list[DocumentRequirement]:
    return [r for r in ALL_DOCUMENT_REQUIREMENTS if r.control_ref == control_ref]


def get_requirements_by_trigger(trigger_type: str) -> list[DocumentRequirement]:
    return [r for r in ALL_DOCUMENT_REQUIREMENTS if r.trigger_type == trigger_type]


if __name__ == "__main__":
    from collections import Counter
    trigger_counts = Counter(r.trigger_type for r in ALL_DOCUMENT_REQUIREMENTS)
    total_items = sum(
        len(r.must_contain) + len(r.should_contain)
        for r in ALL_DOCUMENT_REQUIREMENTS
    )
    must_items = sum(len(r.must_contain) for r in ALL_DOCUMENT_REQUIREMENTS)
    gdpr_items = sum(
        sum(1 for i in r.must_contain if i.gdpr_aligned)
        for r in ALL_DOCUMENT_REQUIREMENTS
    )

    print(f"Document requirements: {len(ALL_DOCUMENT_REQUIREMENTS)}")
    for trigger, count in trigger_counts.items():
        print(f"  {trigger:15s}: {count}")
    print(f"\nChecklist items:")
    print(f"  Total:        {total_items}")
    print(f"  Must-contain: {must_items}")
    print(f"  GDPR-aligned: {gdpr_items}")
    print(f"\nControls covered:")
    for r in ALL_DOCUMENT_REQUIREMENTS:
        gdpr_count = sum(1 for i in r.must_contain if i.gdpr_aligned)
        flag = " [GDPR items]" if gdpr_count else ""
        print(f"  {r.control_ref:15s} {r.trigger_type:15s} {r.document_title}{flag}")
