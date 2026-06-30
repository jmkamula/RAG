"""
ArionComply — Event Node Definitions

Events are runtime occurrences that trigger obligations.
Unlike ClientFacts (permanent profile attributes), events happen
at a point in time and have a lifecycle.

Event nodes in Neo4j are TYPE definitions — shared knowledge.
Incident nodes (Postgres + Neo4j projection) are INSTANCES — tenant data.

Three event categories:
  incident     — something bad happened (breach, complaint, audit finding)
  request      — data subject exercised a right (DSAR, erasure, restriction)
  change       — something in the business changed (new processor, new system)
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class EventTrigger:
    control_id:  str          # RequirementNode id e.g. "GDPR:2016/679:Art.33"
    deadline:    str | None   # "72h" | "1 month" | "before" | None
    rationale:   str          # why this control is triggered


# ── Meta-cascade structures (per cascade_implications_2026_06_29.md) ──
# These extend the original Event dataclass with the 5 patterns the
# domain meditation surfaced. Loader writes:
#   emits_events     -> Event-:EMITS_EVENT->Event edges
#   expects_followups-> Event-:EXPECTS_FOLLOWUP_EVENT->Event with window
#   updates_facts    -> Event-:UPDATES_FACT->ClientFact edges
#   expands_scope    -> Event-:EXPANDS_SCOPE->scope-element (free text v1)
#   cascades_review  -> Event-:CASCADES_REVIEW->RequirementNode set
# All optional — existing 11 events leave these empty.

@dataclass
class EmittedEvent:
    target_event_id: str    # "event:information_security_incident"
    rationale:       str    # why this cascading emission happens
    applies_when:    str | None = None  # optional gate

@dataclass
class ExpectedFollowup:
    target_event_id: str    # "event:privilege_revoked"
    window_days:     int    # e.g. 1 for offboarding SLA
    rationale:       str    # why we expect this followup

@dataclass
class FactUpdate:
    fact_id:     str    # "fact:employee_count_250_plus"
    operation:   str    # "set" | "clear" | "recompute"
    rationale:   str

@dataclass
class ScopeExpansion:
    scope_kind:  str    # "site" | "jurisdiction" | "supplier" | "processing_activity"
    control_set: list[str]  # RequirementNode ids to re-evaluate
    rationale:   str


@dataclass
class Event:
    id:                  str          # "event:personal_data_breach"
    event_type:          str          # machine-readable key
    category:            str          # "incident" | "request" | "change" | "personnel" | "iam" | "asset" | "supplier" | "isms"
    title:               str          # human-readable
    description:         str          # what this event is
    legal_deadline:      str | None   # headline deadline if any
    severity_default:    str          # "critical" | "high" | "medium" | "low"
    triggers:            list[EventTrigger]    = field(default_factory=list)
    requires_evidence:   list[str]             = field(default_factory=list)
    # ── Meta-cascade fields (S2a additions, loader S2b) ───────────────
    emits_events:        list[EmittedEvent]    = field(default_factory=list)
    expects_followups:   list[ExpectedFollowup] = field(default_factory=list)
    updates_facts:       list[FactUpdate]      = field(default_factory=list)
    expands_scope:       list[ScopeExpansion]  = field(default_factory=list)
    cascades_review:     list[str]             = field(default_factory=list)
    # RequirementNode ids to re-evaluate against new scope state
    applies_when:        str | None = None  # applicability gate for the event ITSELF
    # S3g: closure-quality enforcement (P8 from cascade meditation).
    # When True, the cascade engine emits 'closure_proof_missing'
    # implications if structured_event metadata lacks an
    # 'effectiveness_evidence' field. ISO 27001 cl. 10.1 + ISO 27002
    # §5.36 require effectiveness verification on closure of certain
    # lifecycle events — bare closure is itself a finding.
    requires_effectiveness_proof: bool = False


# ── Incident events ───────────────────────────────────────────────────────────

EVENT_PERSONAL_DATA_BREACH = Event(
    id               = "event:personal_data_breach",
    event_type       = "personal_data_breach",
    category         = "incident",
    title            = "Personal Data Breach",
    description      = "Unauthorised access, disclosure, loss, destruction "
                       "or alteration of personal data",
    legal_deadline   = "72 hours",
    severity_default = "critical",
    triggers         = [
        EventTrigger("GDPR:2016/679:Art.33",  "72h",     "Notify supervisory authority within 72h"),
        EventTrigger("GDPR:2016/679:Art.34",  None,      "Notify data subjects if high risk to rights"),
        EventTrigger("GDPR:2016/679:Art.32",  None,      "Review and enhance security measures"),
        EventTrigger("ISO27001:2022:A.5.26",  None,      "Invoke incident response procedure"),
        EventTrigger("ISO27001:2022:A.5.27",  None,      "Conduct post-incident lessons learned"),
        EventTrigger("ISO27001:2022:6.1.2",   None,      "Update risk assessment"),
    ],
    requires_evidence = ["req:Art.33:breach_notification"],
)

EVENT_INFOSEC_INCIDENT = Event(
    id               = "event:information_security_incident",
    event_type       = "information_security_incident",
    category         = "incident",
    title            = "Information Security Incident",
    description      = "Compromise of confidentiality, integrity, or "
                       "availability of information assets where no personal "
                       "data is established to be involved. Generic ISO 27001 "
                       "incident path — complements event:personal_data_breach "
                       "for the PII subset.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers         = [
        EventTrigger("ISO27001:2022:A.5.26",  None,  "Invoke incident response procedure"),
        EventTrigger("ISO27001:2022:A.5.27",  None,  "Conduct post-incident lessons learned"),
        EventTrigger("ISO27001:2022:6.1.2",   None,  "Update risk assessment"),
    ],
    requires_evidence = [],
)

EVENT_SUPERVISORY_INQUIRY = Event(
    id               = "event:supervisory_authority_inquiry",
    event_type       = "supervisory_authority_inquiry",
    category         = "incident",
    title            = "Supervisory Authority Inquiry",
    description      = "ICO or other data protection authority has made "
                       "a formal inquiry or started an investigation",
    legal_deadline   = "varies by inquiry",
    severity_default = "critical",
    triggers         = [
        EventTrigger("GDPR:2016/679:Art.31",  None,  "Cooperate with supervisory authority"),
        EventTrigger("GDPR:2016/679:Art.24",  None,  "Demonstrate controller compliance"),
        EventTrigger("GDPR:2016/679:Art.5",   None,  "Evidence adherence to principles"),
        EventTrigger("ISO27001:2022:9.2",     None,  "Internal audit evidence required"),
        EventTrigger("ISO27001:2022:6.1.2",   None,  "Risk assessment evidence required"),
    ],
    requires_evidence = [],
)

EVENT_AUDIT_NONCONFORMITY = Event(
    id               = "event:audit_nonconformity",
    event_type       = "audit_nonconformity",
    category         = "incident",
    title            = "Audit Nonconformity",
    description      = "Internal or external audit identified a nonconformity "
                       "requiring corrective action",
    legal_deadline   = "agreed with auditor",
    severity_default = "high",
    triggers         = [
        EventTrigger("ISO27001:2022:10.2",  None,  "Corrective action required"),
        EventTrigger("ISO27001:2022:10.1",  None,  "Continual improvement process"),
        EventTrigger("ISO27001:2022:9.2",   None,  "Follow-up audit may be required"),
    ],
    requires_evidence = [],
)

EVENT_CERTIFICATION_AUDIT = Event(
    id               = "event:certification_audit",
    event_type       = "certification_audit",
    category         = "incident",
    title            = "ISO 27001 Certification Audit",
    description      = "Initial or surveillance certification audit "
                       "by an accredited certification body",
    legal_deadline   = "scheduled",
    severity_default = "high",
    triggers         = [
        EventTrigger("ISO27001:2022:9.2",   None,  "Internal audit must be complete and documented"),
        EventTrigger("ISO27001:2022:9.3",   None,  "Management review must be complete"),
        EventTrigger("ISO27001:2022:6.1.2", None,  "Risk assessment must be current"),
        EventTrigger("ISO27001:2022:6.1.3", None,  "Risk treatment plan must be current"),
        EventTrigger("ISO27001:2022:5.2",   None,  "IS Policy must be current and approved"),
    ],
    requires_evidence = [],
)

# ── Request events ────────────────────────────────────────────────────────────

EVENT_DSAR = Event(
    id               = "event:dsar",
    event_type       = "data_subject_access_request",
    category         = "request",
    title            = "Data Subject Access Request",
    description      = "Individual requests access to their personal data "
                       "under Art.15 GDPR",
    legal_deadline   = "1 month",
    severity_default = "medium",
    triggers         = [
        EventTrigger("GDPR:2016/679:Art.15",  "1 month",  "Provide copy of personal data"),
        EventTrigger("GDPR:2016/679:Art.12",  "1 month",  "Respond transparently within deadline"),
    ],
    requires_evidence = ["req:Art.15:dsar_response"],
)

EVENT_ERASURE_REQUEST = Event(
    id               = "event:erasure_request",
    event_type       = "data_subject_erasure_request",
    category         = "request",
    title            = "Right to Erasure Request",
    description      = "Individual requests deletion of their personal data "
                       "under Art.17 GDPR",
    legal_deadline   = "1 month",
    severity_default = "medium",
    triggers         = [
        EventTrigger("GDPR:2016/679:Art.17",  "1 month",  "Erase personal data without undue delay"),
        EventTrigger("GDPR:2016/679:Art.12",  "1 month",  "Respond transparently within deadline"),
        EventTrigger("GDPR:2016/679:Art.19",  None,       "Notify processors of erasure obligation"),
    ],
    requires_evidence = [],
)

EVENT_RESTRICTION_REQUEST = Event(
    id               = "event:restriction_request",
    event_type       = "data_subject_restriction_request",
    category         = "request",
    title            = "Right to Restriction Request",
    description      = "Individual requests restriction of processing "
                       "of their personal data under Art.18 GDPR",
    legal_deadline   = "1 month",
    severity_default = "low",
    triggers         = [
        EventTrigger("GDPR:2016/679:Art.18",  "1 month",  "Restrict processing"),
        EventTrigger("GDPR:2016/679:Art.12",  "1 month",  "Respond transparently"),
    ],
    requires_evidence = [],
)

# ── Change events ─────────────────────────────────────────────────────────────

EVENT_NEW_PROCESSING = Event(
    id               = "event:new_processing_activity",
    event_type       = "new_processing_activity",
    category         = "change",
    title            = "New Processing Activity",
    description      = "Organisation begins a new type of personal data "
                       "processing not previously assessed",
    legal_deadline   = "before processing starts",
    severity_default = "medium",
    triggers         = [
        EventTrigger("GDPR:2016/679:Art.35",  "before",        "DPIA if likely high risk"),
        EventTrigger("GDPR:2016/679:Art.30",  "before",        "Update records of processing"),
        EventTrigger("GDPR:2016/679:Art.13",  "at collection", "Update privacy notice"),
        EventTrigger("GDPR:2016/679:Art.6",   "before",        "Confirm lawful basis"),
        EventTrigger("ISO27001:2022:6.1.2",   "before",        "Risk assessment update"),
    ],
    requires_evidence = [],
)

EVENT_NEW_PROCESSOR = Event(
    id               = "event:new_processor_engaged",
    event_type       = "new_processor_engaged",
    category         = "change",
    title            = "New Processor Engaged",
    description      = "Organisation engages a new third party to process "
                       "personal data on its behalf",
    legal_deadline   = "before processing starts",
    severity_default = "high",
    triggers         = [
        EventTrigger("GDPR:2016/679:Art.28",   "before",  "DPA must be in place before processing"),
        EventTrigger("GDPR:2016/679:Art.28.3", "before",  "DPA must contain all mandatory clauses"),
        EventTrigger("ISO27001:2022:A.5.19",   "before",  "Supplier security assessment"),
        EventTrigger("ISO27001:2022:A.5.20",   "before",  "Security requirements in agreement"),
        EventTrigger("ISO27001:2022:A.5.21",   None,      "ICT supply chain security"),
    ],
    requires_evidence = ["req:Art.28:data_processing_agreement"],
)

EVENT_SYSTEM_CHANGE = Event(
    id               = "event:significant_system_change",
    event_type       = "significant_system_change",
    category         = "change",
    title            = "Significant System Change",
    description      = "Major change to systems or processes that handle "
                       "personal data",
    legal_deadline   = "before go-live",
    severity_default = "medium",
    triggers         = [
        EventTrigger("ISO27001:2022:6.1.2",   "before",  "Risk assessment update required"),
        EventTrigger("GDPR:2016/679:Art.35",  "before",  "DPIA if high risk processing"),
        EventTrigger("ISO27001:2022:A.8.29",  "before",  "Security testing before deployment"),
        EventTrigger("ISO27001:2022:A.8.25",  None,      "Secure development lifecycle"),
        EventTrigger("GDPR:2016/679:Art.30",  None,      "Update records of processing"),
    ],
    requires_evidence = [],
)

# ── Complete registry ──────────────────────────────────────────────────────────

# ═══════════════════════════════════════════════════════════════════════════
# S2a: Operational events (per cascade_implications_2026_06_29.md)
# 5 domains, ~30 high-priority events. Each fires direct obligations
# AND populates meta-cascade fields (emits_events / expects_followups /
# updates_facts / expands_scope / cascades_review) where relevant.
# ═══════════════════════════════════════════════════════════════════════════

# ── Personnel domain ──────────────────────────────────────────────────────

EVENT_PERSONNEL_ADDED = Event(
    id               = "event:personnel_added",
    event_type       = "personnel_added",
    category         = "personnel",
    title            = "Personnel added",
    description      = "New employee or worker joined; HR system has a new row.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:A.6.1",  "before_start", "Screening record required prior to start"),
        EventTrigger("ISO27001:2022:A.6.2",  "1 day",        "Terms of employment signed"),
        EventTrigger("ISO27001:2022:A.6.6",  "1 day",        "NDA signed (often packaged with A.6.2)"),
        EventTrigger("ISO27001:2022:A.5.10", "1 week",       "AUP acknowledgement signed"),
        EventTrigger("ISO27001:2022:A.6.3",  "30 days",      "Information-security awareness training assigned"),
        EventTrigger("ISO27001:2022:A.5.16", "same-day",     "Identity provisioned"),
        EventTrigger("ISO27001:2022:A.5.17", "same-day",     "Authentication info issued"),
        EventTrigger("ISO27001:2022:A.5.18", "by start date","Access rights granted per role"),
    ],
    expects_followups = [
        ExpectedFollowup("event:identity_added", 1,
            "IAM identity expected within 1 day of HR entry"),
    ],
    updates_facts = [
        FactUpdate("fact:employee_count_250_plus", "recompute",
            "Recompute headcount threshold; may flip applicability"),
    ],
)

EVENT_PERSONNEL_OFFBOARDED = Event(
    id               = "event:personnel_offboarded",
    event_type       = "personnel_offboarded",
    category         = "personnel",
    title            = "Personnel offboarded",
    description      = "Employee or worker leaving; HR row marked exit.",
    legal_deadline   = None,
    severity_default = "high",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.11", "by last day",  "Return of assets before departure"),
        EventTrigger("ISO27001:2022:A.5.16", "24h",          "Identity revoked within 24h (SLA-met flag)"),
        EventTrigger("ISO27001:2022:A.5.17", "24h",          "Credentials revoked, paired with A.5.16"),
        EventTrigger("ISO27001:2022:A.5.18", "24h",          "Access rights revoked"),
        EventTrigger("ISO27001:2022:A.6.5",  "by last day",  "Post-employment briefing"),
    ],
    expects_followups = [
        ExpectedFollowup("event:privilege_revoked", 1,
            "Privilege revocation expected within 24h SLA"),
        ExpectedFollowup("event:identity_disabled", 1,
            "Identity disable expected within 24h SLA"),
    ],
    updates_facts = [
        FactUpdate("fact:employee_count_250_plus", "recompute",
            "Recompute headcount threshold"),
    ],
)

EVENT_ROLE_CHANGED = Event(
    id               = "event:role_changed",
    event_type       = "role_changed",
    category         = "personnel",
    title            = "Role changed",
    description      = "Personnel role/title updated; access scope may shift.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.18", "1 week",       "Access rights review against new role"),
        EventTrigger("ISO27001:2022:A.6.3",  "30 days",      "Role-specific training if new role demands it"),
        EventTrigger("ISO27001:2022:A.6.5",  None,           "Confidentiality scope re-check"),
        EventTrigger("ISO27001:2022:A.5.4",  None,           "Management responsibility / segregation re-check"),
    ],
)

EVENT_CONTRACTOR_ENGAGED = Event(
    id               = "event:contractor_engaged",
    event_type       = "contractor_engaged",
    category         = "personnel",
    title            = "Contractor engaged",
    description      = "Non-employee worker engaged; supplier-style + personnel obligations.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.20", "before_start", "Supplier-style agreement with security clauses"),
        EventTrigger("ISO27001:2022:A.6.6",  "1 day",        "Contractor NDA (distinct template from A.6.2)"),
        EventTrigger("ISO27001:2022:A.5.10", "1 week",       "AUP acknowledgement"),
        EventTrigger("ISO27001:2022:A.5.16", "same-day",     "Identity provisioned (with contractor flag)"),
        EventTrigger("ISO27001:2022:A.5.18", "by start date","Access rights granted, scope-limited"),
    ],
)

EVENT_CONTRACTOR_OFFBOARDED = Event(
    id               = "event:contractor_offboarded",
    event_type       = "contractor_offboarded",
    category         = "personnel",
    title            = "Contractor offboarded",
    description      = "Contractor engagement ended.",
    legal_deadline   = None,
    severity_default = "high",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.11", "by last day",  "Return of contractor-issued assets"),
        EventTrigger("ISO27001:2022:A.5.16", "24h",          "Identity revoked"),
        EventTrigger("ISO27001:2022:A.5.17", "24h",          "Credentials revoked"),
        EventTrigger("ISO27001:2022:A.5.18", "24h",          "Access rights revoked"),
        EventTrigger("ISO27001:2022:A.5.20", None,           "Supplier-agreement closure record"),
    ],
)

EVENT_MANAGER_CHANGED = Event(
    id               = "event:manager_changed",
    event_type       = "manager_changed",
    category         = "personnel",
    title            = "Reporting line changed",
    description      = "Personnel reports to a new manager; approval-chain rebuilds.",
    legal_deadline   = None,
    severity_default = "low",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.3",  None,           "Segregation-of-duties re-check"),
        EventTrigger("ISO27001:2022:A.5.4",  None,           "Management-responsibility update"),
        EventTrigger("ISO27001:2022:A.5.18", "1 week",       "Approval-chain access path updated"),
    ],
)

EVENT_PERSONNEL_TRANSFERRED_JURISDICTION = Event(
    id               = "event:personnel_transferred_jurisdiction",
    event_type       = "personnel_transferred_jurisdiction",
    category         = "personnel",
    title            = "Personnel cross-jurisdiction transfer",
    description      = "Personnel location change crossing data-residency boundary.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("GDPR:2016/679:Art.27", None,           "Re-evaluate representative-in-EU requirement"),
        EventTrigger("GDPR:2016/679:Art.44", None,           "Re-evaluate cross-border data-flow obligation"),
        EventTrigger("ISO27001:2022:A.5.31", None,           "Legal/regulatory register update for new jurisdiction"),
    ],
    updates_facts = [
        FactUpdate("fact:transfers_data_outside_eu", "recompute",
            "Cross-border posture may flip"),
        FactUpdate("fact:eu_data_subjects", "recompute",
            "EU-presence proportion may change"),
    ],
)

EVENT_DISCIPLINARY_ACTION_TAKEN = Event(
    id               = "event:disciplinary_action_taken",
    event_type       = "disciplinary_action_taken",
    category         = "personnel",
    title            = "Disciplinary action initiated",
    description      = "Formal A.6.4 process opened.",
    legal_deadline   = None,
    severity_default = "high",
    triggers = [
        EventTrigger("ISO27001:2022:A.6.4",  None,           "Disciplinary process record"),
        EventTrigger("ISO27001:2022:A.5.18", "immediate",    "Access rights suspended pending outcome"),
        EventTrigger("ISO27001:2022:A.5.36", None,           "Compliance review notified"),
    ],
)

# ── IAM / identity domain ─────────────────────────────────────────────────

EVENT_IDENTITY_ADDED = Event(
    id               = "event:identity_added",
    event_type       = "identity_added",
    category         = "iam",
    title            = "Identity added",
    description      = "New IAM identity created (human or service).",
    legal_deadline   = None,
    severity_default = "low",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.16", None,           "Identity register row"),
        EventTrigger("ISO27001:2022:A.5.17", None,           "Authentication info initialised"),
    ],
)

EVENT_IDENTITY_DISABLED = Event(
    id               = "event:identity_disabled",
    event_type       = "identity_disabled",
    category         = "iam",
    title            = "Identity disabled",
    description      = "IAM identity set inactive (transient state).",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.16", None,           "Register status flip"),
        EventTrigger("ISO27001:2022:A.5.17", None,           "Credentials suspended"),
        EventTrigger("ISO27001:2022:A.5.18", None,           "Access rights frozen"),
    ],
)

EVENT_PRIVILEGE_GRANTED = Event(
    id               = "event:privilege_granted",
    event_type       = "privilege_granted",
    category         = "iam",
    title            = "Privilege granted",
    description      = "New role/permission assigned.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.18", None,           "Access-rights register row"),
        EventTrigger("ISO27001:2022:A.8.2",  None,           "Privileged-access record if privileged"),
        EventTrigger("ISO27001:2022:A.5.3",  None,           "Segregation re-check against new privilege"),
    ],
)

EVENT_PRIVILEGE_REVOKED = Event(
    id               = "event:privilege_revoked",
    event_type       = "privilege_revoked",
    category         = "iam",
    title            = "Privilege revoked",
    description      = "Role/permission removed.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.18", None,           "Access-rights register update"),
        EventTrigger("ISO27001:2022:A.8.2",  None,           "Privileged-access record update if applicable"),
    ],
)

EVENT_MFA_METHOD_CHANGED = Event(
    id               = "event:mfa_method_changed",
    event_type       = "mfa_method_changed",
    category         = "iam",
    title            = "MFA method changed",
    description      = "Authentication-factor enrolment/de-enrolment.",
    legal_deadline   = None,
    severity_default = "low",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.17", None,           "Authentication-info register update"),
    ],
)

# ── Asset / physical domain ───────────────────────────────────────────────

EVENT_ASSET_ADDED = Event(
    id               = "event:asset_added",
    event_type       = "asset_added",
    category         = "asset",
    title            = "Asset added",
    description      = "New asset entered inventory.",
    legal_deadline   = None,
    severity_default = "low",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.9",  None,           "Asset register row"),
        EventTrigger("ISO27001:2022:A.5.12", "before use",   "Classification assigned"),
        EventTrigger("ISO27001:2022:A.5.13", "before use",   "Labelling applied"),
        EventTrigger("ISO27001:2022:A.7.10", None,           "Media-handling rules if media"),
    ],
)

EVENT_ASSET_RECLASSIFIED = Event(
    id               = "event:asset_reclassified",
    event_type       = "asset_reclassified",
    category         = "asset",
    title            = "Asset reclassified",
    description      = "Classification level changed; downstream technical controls re-evaluated.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.13", "immediate",    "Labels updated to match new classification"),
        EventTrigger("ISO27001:2022:A.5.18", None,           "Access rights re-reviewed"),
        EventTrigger("ISO27001:2022:A.8.12", None,           "DLP rules re-evaluated"),
        EventTrigger("ISO27001:2022:A.8.24", None,           "Cryptographic requirements re-evaluated"),
    ],
    cascades_review = [
        "ISO27001:2022:A.5.13",
        "ISO27001:2022:A.5.18",
        "ISO27001:2022:A.8.12",
        "ISO27001:2022:A.8.24",
    ],
)

EVENT_ASSET_RELOCATED = Event(
    id               = "event:asset_relocated",
    event_type       = "asset_relocated",
    category         = "asset",
    title            = "Asset relocated",
    description      = "Asset physically moved (potentially cross-site or cross-jurisdiction).",
    legal_deadline   = None,
    severity_default = "low",
    triggers = [
        EventTrigger("ISO27001:2022:A.7.8",  None,           "Equipment-siting controls re-applied"),
        EventTrigger("ISO27001:2022:A.7.4",  None,           "Monitoring coverage adjusted"),
        EventTrigger("ISO27001:2022:A.7.5",  None,           "Environmental threat assessment for new site"),
    ],
)

EVENT_ASSET_RETIRED = Event(
    id               = "event:asset_retired",
    event_type       = "asset_retired",
    category         = "asset",
    title            = "Asset retirement decided",
    description      = "End-of-life decision; disposal plan must follow.",
    legal_deadline   = None,
    severity_default = "low",
    triggers = [
        EventTrigger("ISO27001:2022:A.7.14", None,           "Disposal plan authored"),
        EventTrigger("ISO27001:2022:A.8.10", None,           "Information-deletion plan"),
        EventTrigger("ISO27001:2022:A.5.9",  None,           "Register status transitions"),
    ],
    expects_followups = [
        ExpectedFollowup("event:asset_disposed", 30,
            "Disposal expected within 30 days of retirement decision"),
    ],
)

EVENT_ASSET_DISPOSED = Event(
    id               = "event:asset_disposed",
    event_type       = "asset_disposed",
    category         = "asset",
    title            = "Asset disposed",
    description      = "Physical disposal completed; chain-of-custody preserved.",
    legal_deadline   = None,
    severity_default = "low",
    triggers = [
        EventTrigger("ISO27001:2022:A.7.14", None,           "Disposal record (audit artifact)"),
        EventTrigger("ISO27001:2022:A.8.10", None,           "Information-deletion attestation"),
        EventTrigger("ISO27001:2022:A.5.28", None,           "Evidence-handling chain entry"),
        EventTrigger("ISO27001:2022:A.5.9",  None,           "Register marked disposed"),
    ],
    requires_effectiveness_proof = True,
    # ISO 27002:2022 §7.14: equipment must be disposed of "in a
    # secure manner". The disposal certificate / data-erasure proof
    # IS the effectiveness evidence.
)

EVENT_ASSET_LOST_STOLEN = Event(
    id               = "event:asset_lost_stolen",
    event_type       = "asset_lost_stolen",
    category         = "asset",
    title            = "Asset lost or stolen",
    description      = "Unintended loss of physical control over an asset.",
    legal_deadline   = "immediate",
    severity_default = "critical",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.26", "immediate",    "Incident register row"),
        EventTrigger("ISO27001:2022:A.5.27", None,           "Lessons learned scoped"),
        EventTrigger("ISO27001:2022:A.5.9",  None,           "Register marked lost/stolen"),
    ],
    emits_events = [
        EmittedEvent("event:information_security_incident",
            "Loss of asset always emits security incident"),
        EmittedEvent("event:personal_data_breach",
            "Emits breach event if asset contains personal data",
            applies_when="asset.contains_personal_data == true"),
    ],
)

EVENT_FACILITY_ADDED = Event(
    id               = "event:facility_added",
    event_type       = "facility_added",
    category         = "asset",
    title            = "Facility added",
    description      = "New physical site brought online.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.9",  None,           "Register scope extended"),
        EventTrigger("ISO27001:2022:A.5.23", None,           "Cloud-vs-physical balance reassessed"),
    ],
    expands_scope = [
        ScopeExpansion("site",
            ["ISO27001:2022:A.7.1", "ISO27001:2022:A.7.2", "ISO27001:2022:A.7.3",
             "ISO27001:2022:A.7.4", "ISO27001:2022:A.7.5", "ISO27001:2022:A.7.6",
             "ISO27001:2022:A.7.7", "ISO27001:2022:A.7.8", "ISO27001:2022:A.7.9",
             "ISO27001:2022:A.7.10", "ISO27001:2022:A.7.11", "ISO27001:2022:A.7.12",
             "ISO27001:2022:A.7.13", "ISO27001:2022:A.7.14"],
            "All A.7.x controls must be evaluated against the new site"),
    ],
    updates_facts = [
        FactUpdate("fact:has_physical_premises", "set",
            "New site means physical premises in scope"),
    ],
)

EVENT_FACILITY_CLOSED = Event(
    id               = "event:facility_closed",
    event_type       = "facility_closed",
    category         = "asset",
    title            = "Facility closed",
    description      = "Site decommissioned; mass-disposal cascade.",
    legal_deadline   = None,
    severity_default = "high",
    triggers = [
        EventTrigger("ISO27001:2022:A.7.14", None,           "Disposal scope spikes (all facility assets)"),
        EventTrigger("ISO27001:2022:A.5.9",  None,           "Register entries for facility transition"),
    ],
)

# ── Supplier domain ───────────────────────────────────────────────────────

EVENT_SUPPLIER_ENGAGED = Event(
    id               = "event:supplier_engaged",
    event_type       = "supplier_engaged",
    category         = "supplier",
    title            = "Supplier engaged",
    description      = "New vendor contract signed (broader than processor — covers non-PII suppliers too).",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.19", None,           "Policy applied"),
        EventTrigger("ISO27001:2022:A.5.20", "before_start", "Agreement with security clauses signed"),
        EventTrigger("ISO27001:2022:A.5.21", None,           "ICT supply-chain entry if ICT supplier"),
        EventTrigger("ISO27001:2022:A.5.22", "180 days",     "Initial review scheduled"),
    ],
    emits_events = [
        EmittedEvent("event:new_processor_engaged",
            "If supplier processes personal data, the processor event also fires",
            applies_when="supplier.processes_personal_data == true"),
    ],
)

EVENT_SUPPLIER_TERMINATED = Event(
    id               = "event:supplier_terminated",
    event_type       = "supplier_terminated",
    category         = "supplier",
    title            = "Supplier terminated",
    description      = "Contract ended; closure obligations.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.20", None,           "Closure obligations (data return/deletion)"),
        EventTrigger("ISO27001:2022:A.5.21", None,           "Register update"),
        EventTrigger("ISO27001:2022:A.5.22", None,           "Final review"),
        EventTrigger("ISO27001:2022:A.8.10", None,           "Data-deletion attestation"),
    ],
    expects_followups = [
        ExpectedFollowup("event:data_return_attestation_received", 30,
            "Data-return or destruction attestation expected within 30 days"),
    ],
    requires_effectiveness_proof = True,
    # ISO 27002:2022 §5.20: supplier agreement closure includes the
    # return / destruction proof. The expected_followup tracks the
    # ATTESTATION arrival; requires_effectiveness_proof tracks whether
    # the closure ITSELF was filed with the proof inline.
)

EVENT_SUPPLIER_BREACH_REPORTED = Event(
    id               = "event:supplier_breach_reported",
    event_type       = "supplier_breach_reported",
    category         = "supplier",
    title            = "Supplier breach reported",
    description      = "Supplier-side incident disclosed; tenant-side clock starts on awareness.",
    legal_deadline   = None,
    severity_default = "high",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.22", "immediate",    "Emergency supplier review"),
        EventTrigger("ISO27001:2022:A.5.20", None,           "Contract enforcement clauses"),
        EventTrigger("ISO27001:2022:A.5.26", "immediate",    "Incident register row"),
        EventTrigger("ISO27001:2022:A.5.27", None,           "Lessons learned scoped"),
    ],
    emits_events = [
        EmittedEvent("event:personal_data_breach",
            "If our personal data affected, GDPR breach event fires",
            applies_when="supplier.processes_our_personal_data == true"),
    ],
)

# ── Management-system lifecycle domain ────────────────────────────────────

EVENT_POLICY_REVISED = Event(
    id               = "event:policy_revised",
    event_type       = "policy_revised",
    category         = "isms",
    title            = "Policy revised",
    description      = "Existing policy versioned up; downstream alignment required.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:7.5",    None,           "Document control: version, supersedes, archive"),
        EventTrigger("ISO27001:2022:7.4",    None,           "Communication to affected personnel"),
        EventTrigger("ISO27001:2022:A.6.3",  "30 days",      "Awareness/training updated if material"),
        EventTrigger("ISO27001:2022:A.5.36", None,           "Compliance review scoped against new policy"),
        EventTrigger("ISO27001:2022:A.5.37", None,           "Operating procedures cascade update"),
    ],
    cascades_review = [
        "ISO27001:2022:A.5.37",
    ],
)

EVENT_AUP_REVISED = Event(
    id               = "event:aup_revised",
    event_type       = "aup_revised",
    category         = "isms",
    title            = "AUP revised",
    description      = "A.5.10 AUP changed; mass re-acknowledgement required.",
    legal_deadline   = None,
    severity_default = "high",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.10", "7 days",       "Mass re-acknowledgement"),
        EventTrigger("ISO27001:2022:A.6.3",  "30 days",      "Training content refresh"),
        EventTrigger("ISO27001:2022:7.4",    None,           "Communication"),
        EventTrigger("ISO27001:2022:7.5",    None,           "Document control"),
    ],
)

EVENT_CLASSIFICATION_SCHEME_REVISED = Event(
    id               = "event:classification_scheme_revised",
    event_type       = "classification_scheme_revised",
    category         = "isms",
    title            = "Classification scheme revised",
    description      = "A.5.12 classification scheme changed; multi-dimensional cascade.",
    legal_deadline   = None,
    severity_default = "high",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.13", None,           "Labels reviewed against new scheme"),
        EventTrigger("ISO27001:2022:A.5.18", None,           "Access rights recomputed"),
        EventTrigger("ISO27001:2022:A.8.12", None,           "DLP rules updated"),
        EventTrigger("ISO27001:2022:A.8.24", None,           "Crypto requirements re-evaluated"),
        EventTrigger("ISO27001:2022:A.6.3",  None,           "Retraining on new scheme"),
    ],
    cascades_review = [
        "ISO27001:2022:A.5.13",
        "ISO27001:2022:A.5.18",
        "ISO27001:2022:A.8.12",
        "ISO27001:2022:A.8.24",
    ],
)

EVENT_RISK_ASSESSMENT_COMPLETED = Event(
    id               = "event:risk_assessment_completed",
    event_type       = "risk_assessment_completed",
    category         = "isms",
    title            = "Risk assessment cycle completed",
    description      = "6.1.2 cycle done; treatment + SoA must follow.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:6.1.3",  None,           "Risk treatment re-evaluated"),
        EventTrigger("ISO27001:2022:8.3",    None,           "Operational treatment review"),
        EventTrigger("ISO27001:2022:9.3",    None,           "Management review input"),
    ],
    expects_followups = [
        ExpectedFollowup("event:risk_treatment_decision", 30,
            "Treatment decision expected within 30 days of assessment"),
    ],
)

EVENT_SOA_UPDATED = Event(
    id               = "event:soa_updated",
    event_type       = "soa_updated",
    category         = "isms",
    title            = "Statement of Applicability updated",
    description      = "Control applicability changed; re-evaluate entire control set.",
    legal_deadline   = None,
    severity_default = "high",
    triggers = [
        EventTrigger("ISO27001:2022:9.2",    None,           "Audit scope adjusted"),
        EventTrigger("ISO27001:2022:A.5.36", None,           "Compliance review scope adjusted"),
    ],
    cascades_review = [
        # SoA update potentially affects every Annex A control; loader writes
        # a special edge type CASCADES_REVIEW with role='scope_recompute'
    ],
)

EVENT_INTERNAL_AUDIT_COMPLETED = Event(
    id               = "event:internal_audit_completed",
    event_type       = "internal_audit_completed",
    category         = "isms",
    title            = "Internal audit cycle completed",
    description      = "9.2 audit closed; findings transition to corrective-action queue.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:9.3",    None,           "Management review input"),
        EventTrigger("ISO27001:2022:10.1",   None,           "Nonconformity identification"),
    ],
)

EVENT_COMPLIANCE_REVIEW_COMPLETED = Event(
    id               = "event:compliance_review_completed",
    event_type       = "compliance_review_completed",
    category         = "isms",
    title            = "Compliance review completed",
    description      = "A.5.36 review cycle done; findings may trigger correction.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:9.3",    None,           "Management review input"),
        EventTrigger("ISO27001:2022:10.1",   None,           "Nonconformity if any"),
        EventTrigger("ISO27001:2022:A.6.4",  None,           "Disciplinary consideration if applicable"),
    ],
)

EVENT_MANAGEMENT_REVIEW_COMPLETED = Event(
    id               = "event:management_review_completed",
    event_type       = "management_review_completed",
    category         = "isms",
    title            = "Management review completed",
    description      = "9.3 review cycle done; decisions become corrective-action candidates.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:10.1",   None,           "Corrective actions opened per decisions"),
        EventTrigger("ISO27001:2022:10.2",   None,           "Continual-improvement actions"),
        EventTrigger("ISO27001:2022:6.2",    None,           "Objectives may be re-set"),
    ],
)

EVENT_CORRECTIVE_ACTION_OPENED = Event(
    id               = "event:corrective_action_opened",
    event_type       = "corrective_action_opened",
    category         = "isms",
    title            = "Corrective action opened",
    description      = "10.1 corrective action started; tracking begins.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:10.1",   None,           "Corrective-action register row"),
        EventTrigger("ISO27001:2022:9.3",    None,           "Management awareness"),
    ],
    expects_followups = [
        ExpectedFollowup("event:corrective_action_closed", 90,
            "Closure expected within 90 days (tenant-policy enforced)"),
    ],
)

EVENT_CORRECTIVE_ACTION_CLOSED = Event(
    id               = "event:corrective_action_closed",
    event_type       = "corrective_action_closed",
    category         = "isms",
    title            = "Corrective action closed",
    description      = "10.1 closure; effectiveness proof required (closure without proof is itself a finding).",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:10.1",   None,           "Closure record + effectiveness evidence"),
        EventTrigger("ISO27001:2022:10.2",   None,           "Continual improvement input"),
    ],
    requires_effectiveness_proof = True,
    # ISO 27001 cl. 10.1: "the effectiveness of any corrective action
    # taken shall be reviewed". Closure-without-proof is itself a NC.
)

EVENT_VULNERABILITY_DISCLOSED_CRITICAL = Event(
    id               = "event:vulnerability_disclosed_critical",
    event_type       = "vulnerability_disclosed_critical",
    category         = "isms",
    title            = "Critical vulnerability disclosed",
    description      = "CVE-class signal requiring expedited patch decision.",
    legal_deadline   = "72h",
    severity_default = "critical",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.7",  None,           "Threat-intel signal recorded"),
        EventTrigger("ISO27001:2022:A.8.8",  "72h",          "Patch decision required"),
        EventTrigger("ISO27001:2022:A.5.25", None,           "Triage if exploited in the wild"),
        EventTrigger("ISO27001:2022:A.8.32", None,           "Emergency change consideration"),
    ],
)

EVENT_PRODUCTION_DEPLOYMENT = Event(
    id               = "event:production_deployment",
    event_type       = "production_deployment",
    category         = "isms",
    title            = "Production deployment",
    description      = "Code or configuration deployed to production.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:A.8.32", "before",       "Change record with approval chain"),
        EventTrigger("ISO27001:2022:A.8.29", "before",       "Security testing evidence pre-deployment"),
        EventTrigger("ISO27001:2022:A.8.31", None,           "Dev/test/prod separation evidence"),
        EventTrigger("ISO27001:2022:A.5.26", "after",        "Heightened incident monitoring post-deploy"),
    ],
)

EVENT_RETENTION_PERIOD_REACHED = Event(
    id               = "event:retention_period_reached",
    event_type       = "retention_period_reached",
    category         = "isms",
    title            = "Retention period reached",
    description      = "A.5.33 records hit retention end; deletion or extension decision required.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.33", None,           "Retention review record"),
        EventTrigger("ISO27001:2022:A.8.10", None,           "Information-deletion execution"),
        EventTrigger("GDPR:2016/679:Art.5",  None,           "Storage-limitation principle check (Art.5.1.e)"),
    ],
)

EVENT_RISK_TREATMENT_DECISION = Event(
    id               = "event:risk_treatment_decision",
    event_type       = "risk_treatment_decision",
    category         = "isms",
    title            = "Risk treatment decision",
    description      = "6.1.3 risk treatment plan decision (accept / mitigate / "
                       "transfer / avoid) made for risks surfaced by assessment.",
    legal_deadline   = None,
    severity_default = "medium",
    triggers = [
        EventTrigger("ISO27001:2022:6.1.3",  None,           "Treatment plan record"),
        EventTrigger("ISO27001:2022:A.5.36", None,           "Compliance review of treatment effectiveness"),
    ],
    expects_followups = [
        ExpectedFollowup("event:soa_updated", 30,
            "SoA must reflect any control applicability changes from treatment"),
    ],
)

EVENT_DATA_RETURN_ATTESTATION_RECEIVED = Event(
    id               = "event:data_return_attestation_received",
    event_type       = "data_return_attestation_received",
    category         = "supplier",
    title            = "Data return / destruction attestation received",
    description      = "Supplier-side attestation that controller data has been "
                       "returned or destroyed per A.5.20 closure clause. Closure "
                       "event for supplier_terminated chains.",
    legal_deadline   = None,
    severity_default = "low",
    triggers = [
        EventTrigger("ISO27001:2022:A.5.20", None,           "Closure-record completion"),
        EventTrigger("ISO27001:2022:A.5.28", None,           "Evidence-handling chain entry"),
        EventTrigger("ISO27001:2022:A.8.10", None,           "Information-deletion attestation filed"),
    ],
)

EVENT_CONSENT_WITHDRAWN = Event(
    id               = "event:consent_withdrawn",
    event_type       = "consent_withdrawn",
    category         = "isms",
    title            = "Consent withdrawn",
    description      = "GDPR Art.7.3 — data subject withdraws consent.",
    legal_deadline   = "1 month",
    severity_default = "high",
    triggers = [
        EventTrigger("GDPR:2016/679:Art.7",  "without_undue_delay", "Acknowledge withdrawal"),
        EventTrigger("GDPR:2016/679:Art.17", "1 month",      "Erasure if consent was sole lawful basis"),
        EventTrigger("ISO27001:2022:A.5.18", None,           "Access rights review for consent-based processing"),
    ],
    emits_events = [
        EmittedEvent("event:erasure_request",
            "Withdrawal can cascade to erasure under Art.17.1.b",
            applies_when="consent.was_sole_lawful_basis == true"),
    ],
)

# Sentinel placeholder so the ALL_EVENTS list below has a single ordered append
# and downstream files importing event constants don't break if we add more.


ALL_EVENTS: list[Event] = [
    # ── Existing 11 (compliance-lifecycle) ────────────────────────────
    EVENT_PERSONAL_DATA_BREACH,
    EVENT_INFOSEC_INCIDENT,
    EVENT_SUPERVISORY_INQUIRY,
    EVENT_AUDIT_NONCONFORMITY,
    EVENT_CERTIFICATION_AUDIT,
    EVENT_DSAR,
    EVENT_ERASURE_REQUEST,
    EVENT_RESTRICTION_REQUEST,
    EVENT_NEW_PROCESSING,
    EVENT_NEW_PROCESSOR,
    EVENT_SYSTEM_CHANGE,

    # ── S2a: personnel domain ─────────────────────────────────────────
    EVENT_PERSONNEL_ADDED,
    EVENT_PERSONNEL_OFFBOARDED,
    EVENT_ROLE_CHANGED,
    EVENT_CONTRACTOR_ENGAGED,
    EVENT_CONTRACTOR_OFFBOARDED,
    EVENT_MANAGER_CHANGED,
    EVENT_PERSONNEL_TRANSFERRED_JURISDICTION,
    EVENT_DISCIPLINARY_ACTION_TAKEN,

    # ── S2a: IAM domain ───────────────────────────────────────────────
    EVENT_IDENTITY_ADDED,
    EVENT_IDENTITY_DISABLED,
    EVENT_PRIVILEGE_GRANTED,
    EVENT_PRIVILEGE_REVOKED,
    EVENT_MFA_METHOD_CHANGED,

    # ── S2a: asset / physical domain ──────────────────────────────────
    EVENT_ASSET_ADDED,
    EVENT_ASSET_RECLASSIFIED,
    EVENT_ASSET_RELOCATED,
    EVENT_ASSET_RETIRED,
    EVENT_ASSET_DISPOSED,
    EVENT_ASSET_LOST_STOLEN,
    EVENT_FACILITY_ADDED,
    EVENT_FACILITY_CLOSED,

    # ── S2a: supplier domain ──────────────────────────────────────────
    EVENT_SUPPLIER_ENGAGED,
    EVENT_SUPPLIER_TERMINATED,
    EVENT_SUPPLIER_BREACH_REPORTED,
    EVENT_DATA_RETURN_ATTESTATION_RECEIVED,

    # ── S2a: management-system lifecycle domain ───────────────────────
    EVENT_POLICY_REVISED,
    EVENT_AUP_REVISED,
    EVENT_CLASSIFICATION_SCHEME_REVISED,
    EVENT_RISK_ASSESSMENT_COMPLETED,
    EVENT_RISK_TREATMENT_DECISION,
    EVENT_SOA_UPDATED,
    EVENT_INTERNAL_AUDIT_COMPLETED,
    EVENT_COMPLIANCE_REVIEW_COMPLETED,
    EVENT_MANAGEMENT_REVIEW_COMPLETED,
    EVENT_CORRECTIVE_ACTION_OPENED,
    EVENT_CORRECTIVE_ACTION_CLOSED,
    EVENT_VULNERABILITY_DISCLOSED_CRITICAL,
    EVENT_PRODUCTION_DEPLOYMENT,
    EVENT_RETENTION_PERIOD_REACHED,
    EVENT_CONSENT_WITHDRAWN,
]

# Phrase detection map — used by classifier
EVENT_PHRASES: dict[str, list[str]] = {
    "personal_data_breach": [
        "data breach", "breach occurred", "breach happened",
        "unauthorised access", "data leak", "data was leaked",
        "personal data was accessed", "security incident involving",
        "lost data", "stolen data", "ransomware",
    ],
    "supervisory_authority_inquiry": [
        "ICO", "supervisory authority", "data protection authority",
        "DPA contacted", "regulatory inquiry", "investigation by",
        "enforcement notice", "ICO investigation",
    ],
    "audit_nonconformity": [
        "nonconformity", "non-conformity", "audit finding",
        "failed audit", "corrective action required",
        "major finding", "minor finding",
    ],
    "certification_audit": [
        "certification audit", "stage 1", "stage 2",
        "surveillance audit", "recertification",
        "certification body", "preparing for audit",
        "audit next month", "upcoming audit",
    ],
    "data_subject_access_request": [
        "DSAR", "data subject access request", "access request",
        "someone asked for their data", "right of access",
        "subject access", "requesting their data",
    ],
    "data_subject_erasure_request": [
        "right to erasure", "right to be forgotten",
        "delete their data", "erasure request",
        "remove their data", "data deletion request",
    ],
    "data_subject_restriction_request": [
        "restriction request", "right to restriction",
        "restrict processing", "stop processing their data",
    ],
    "new_processing_activity": [
        "new processing", "starting to process",
        "new data collection", "new product that processes",
        "new system that handles", "expanding our processing",
    ],
    "new_processor_engaged": [
        "new processor", "new supplier", "new third party",
        "engaging a processor", "new cloud provider",
        "new SaaS", "new vendor processing",
    ],
    "significant_system_change": [
        "system change", "new system", "system upgrade",
        "migrating our", "new platform", "replacing our",
        "major change to", "go-live",
    ],
}


def detect_events(query: str) -> list[str]:
    """Detect event types from query text. Returns list of event_type strings."""
    query_lower = query.lower()
    detected = []
    for event_type, phrases in EVENT_PHRASES.items():
        if any(phrase.lower() in query_lower for phrase in phrases):
            detected.append(event_type)
    return detected


def get_event(event_type: str) -> Event | None:
    return next((e for e in ALL_EVENTS if e.event_type == event_type), None)


if __name__ == "__main__":
    from collections import Counter
    cats = Counter(e.category for e in ALL_EVENTS)
    total_triggers = sum(len(e.triggers) for e in ALL_EVENTS)

    print(f"Events: {len(ALL_EVENTS)}")
    for cat, count in cats.items():
        print(f"  {cat:10s}: {count}")
    print(f"\nTotal obligation triggers: {total_triggers}")
    print(f"\nEvent registry:")
    for e in ALL_EVENTS:
        deadline = f"  [{e.legal_deadline}]" if e.legal_deadline else ""
        docs = f"  → {len(e.requires_evidence)} doc(s)" if e.requires_evidence else ""
        print(f"  {e.event_type:40s} {e.severity_default:8s}{deadline}{docs}")

    print(f"\nPhrase detection test:")
    tests = [
        "we had a data breach last week",
        "the ICO has contacted us",
        "we received a DSAR yesterday",
        "we are engaging a new cloud provider",
        "preparing for our certification audit next month",
    ]
    for t in tests:
        detected = detect_events(t)
        print(f"  '{t[:45]}' → {detected}")
