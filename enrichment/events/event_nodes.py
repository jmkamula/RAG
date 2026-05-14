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


@dataclass
class Event:
    id:                  str          # "event:personal_data_breach"
    event_type:          str          # machine-readable key
    category:            str          # "incident" | "request" | "change"
    title:               str          # human-readable
    description:         str          # what this event is
    legal_deadline:      str | None   # headline deadline if any
    severity_default:    str          # "critical" | "high" | "medium" | "low"
    triggers:            list[EventTrigger] = field(default_factory=list)
    requires_documents:  list[str]    = field(default_factory=list)
    # DocumentRequirement ids e.g. "req:Art.33:breach_notification"


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
    requires_documents = ["req:Art.33:breach_notification"],
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
    requires_documents = [],
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
    requires_documents = [],
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
    requires_documents = [],
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
    requires_documents = [],
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
    requires_documents = ["req:Art.15:dsar_response"],
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
    requires_documents = [],
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
    requires_documents = [],
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
    requires_documents = [],
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
    requires_documents = ["req:Art.28:data_processing_agreement"],
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
    requires_documents = [],
)

# ── Complete registry ──────────────────────────────────────────────────────────

ALL_EVENTS: list[Event] = [
    # Incidents
    EVENT_PERSONAL_DATA_BREACH,
    EVENT_INFOSEC_INCIDENT,
    EVENT_SUPERVISORY_INQUIRY,
    EVENT_AUDIT_NONCONFORMITY,
    EVENT_CERTIFICATION_AUDIT,

    # Requests
    EVENT_DSAR,
    EVENT_ERASURE_REQUEST,
    EVENT_RESTRICTION_REQUEST,

    # Changes
    EVENT_NEW_PROCESSING,
    EVENT_NEW_PROCESSOR,
    EVENT_SYSTEM_CHANGE,
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
        docs = f"  → {len(e.requires_documents)} doc(s)" if e.requires_documents else ""
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
