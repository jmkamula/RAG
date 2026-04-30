"""
Tier 1 Enrichment — GDPR Security of Processing (Art.32 cluster)

Sources:
  - GDPR Art.32 verbatim text (obligation_text already in nodes)
  - EDPB Guidelines 4/2019 on Article 25 (data protection by design)
  - EDPB Recommendations 01/2020 on pseudonymisation
  - ENISA Guidelines on Security Measures for Art.32
  - ICO guidance: Security (https://ico.org.uk/for-organisations/
    uk-gdpr-guidance-and-resources/security/)
  - WP29 Opinion on encryption (WP247)
  - Recital 83 (security risk assessment rationale)

Each entry contains:
  business_description:
    Written in practitioner language from the perspective of a DPO,
    CISO, or compliance manager. Describes what the obligation means
    in practice, when it is triggered, and common misunderstandings.
    Does NOT add obligations not present in the legal text.
    Does NOT recommend specific technologies unless the text does.

  query_keywords:
    exact:      terms that appear in the standard text verbatim,
                or are the standard formal shorthand for this concept
    practitioner: how DPOs, CISOs, lawyers actually refer to this
    scenario:   real-world situations that trigger this obligation
    confusion:  adjacent concepts commonly mistaken for this node
                (so the reranker can distinguish them)

REVIEW CHECKLIST (for each node):
  □ Does the business_description stay within the legal text?
  □ Are there any specific technology mandates not in the text?
  □ Are the practitioner terms sourced from real guidance/usage?
  □ Do the confusion terms correctly identify adjacent nodes?
  □ Is anything missing that a DPO would ask about?
"""

TIER1_ENRICHMENT = {

# ═══════════════════════════════════════════════════════════════════════════
# Art.32 — Security of processing (article level)
# ═══════════════════════════════════════════════════════════════════════════

"Art.32": {
    "business_description": (
        "Article 32 is the core General Data Protection Regulation (GDPR) security obligation. It requires both "
        "controllers and processors to implement security measures that are "
        "appropriate to the risk their processing poses to individuals — not "
        "a fixed minimum standard, but a risk-calibrated one. The four specific "
        "measures listed (encryption, resilience, restoration, testing) are "
        "examples of 'as appropriate' measures, not a mandatory checklist. "
        "The starting point is always a risk assessment: what could go wrong "
        "with this personal data, how likely is it, how severe would the harm "
        "be? The security measures must be proportionate to that answer. "
        "Adherence to an approved code of conduct or certification scheme "
        "(e.g. ISO 27001) can be used as evidence of compliance, but is not "
        "itself sufficient — the risk-appropriateness must still be demonstrated."
    ),
    "query_keywords": {
        "exact": [
            "security of processing",
            "appropriate technical and organisational measures",
            "TOMs",
            "technical and organisational measures",
            "level of security appropriate to the risk",
            "state of the art",
            "costs of implementation",
        ],
        "practitioner": [
            "GDPR security requirements",
            "data security obligations",
            "information security GDPR",
            "security measures personal data",
            "GDPR security controls",
            "data protection security",
            "security risk assessment GDPR",
            "what security does GDPR require",
            "GDPR technical controls",
        ],
        "scenario": [
            "implementing security for a new system processing personal data",
            "what security do we need for GDPR",
            "are our security measures sufficient for GDPR",
            "security audit personal data",
            "GDPR compliance for cloud systems",
            "third party processing security",
        ],
        "confusion": [
            # Art.25 is commonly confused with Art.32
            "privacy by design",   # → Art.25, not Art.32
            "data minimisation",   # → Art.5.1.c, not Art.32
            # ISO 27001 is evidence of Art.32, not equivalent to it
            "ISO 27001 compliance", # relevant but not synonymous
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.32.1 — The risk-based security paragraph
# ═══════════════════════════════════════════════════════════════════════════

"Art.32.1": {
    "business_description": (
        "This is the operative paragraph establishing the risk-based security "
        "standard. Four factors determine what measures are 'appropriate': "
        "the state of the art (current best practice), implementation costs, "
        "the nature/scope/context/purposes of the processing, and the risk "
        "to individuals' rights and freedoms. These four factors work together "
        "— high risk processing justifies higher cost measures; low risk "
        "processing with expensive countermeasures may be disproportionate. "
        "The four specific measures listed (encryption/pseudonymisation, "
        "resilience, restoration capability, testing) are explicitly framed "
        "as 'inter alia as appropriate' — meaning they are illustrative, "
        "not mandatory. A controller must assess which of these, and what "
        "else, is appropriate for their specific processing. The risk "
        "assessment required by Art.32.2 is the method for making that "
        "determination."
    ),
    "query_keywords": {
        "exact": [
            "taking into account the state of the art",
            "costs of implementation",
            "nature scope context and purposes",
            "risk of varying likelihood and severity",
            "inter alia as appropriate",
            "pseudonymisation and encryption",
            "confidentiality integrity availability resilience",
        ],
        "practitioner": [
            "risk-based security",
            "proportionate security measures",
            "security risk assessment",
            "appropriate security GDPR",
            "what level of security is required",
            "GDPR security standard",
            "how to assess security for GDPR",
        ],
        "scenario": [
            "determining what security measures to implement",
            "is our security sufficient for GDPR",
            "security measures proportionate to risk",
            "choosing security controls for personal data processing",
        ],
        "confusion": [
            "absolute security requirement",  # Art.32 is risk-based, not absolute
            "specific security standards mandated",  # no specific standard mandated
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.32.1.a — Pseudonymisation and encryption
# ═══════════════════════════════════════════════════════════════════════════

"Art.32.1.a": {
    "business_description": (
        "Pseudonymisation and encryption are listed as examples of appropriate "
        "security measures — they are not mandatory requirements. However, in "
        "practice, for most organisations processing personal data, the Information Commissioner's Office (ICO) "
        "and other supervisory authorities expect encryption of personal data "
        "at rest and in transit to be a baseline measure. The European Data Protection Board (EDPB) and European Union Agency for Cybersecurity (ENISA) "
        "guidance consistently cite encryption as a key measure for Art.32. "
        "Pseudonymisation — replacing identifying data with pseudonyms while "
        "retaining a key — is a weaker form of protection than anonymisation "
        "but can reduce the risk associated with a breach. Note: the choice "
        "of encryption algorithm and key length is not specified by the General Data Protection Regulation (GDPR); "
        "what matters is that the chosen approach is appropriate to current "
        "best practice (state of the art). A separate key management procedure "
        "is essential — encryption without controlled key management provides "
        "limited protection."
    ),
    "query_keywords": {
        "exact": [
            "pseudonymisation and encryption of personal data",
            "pseudonymisation",
            "encryption",
        ],
        "practitioner": [
            "encrypt personal data",
            "data encryption GDPR",
            "encryption at rest",
            "encryption in transit",
            "encrypt data at rest",
            "TLS",
            "HTTPS",
            "disk encryption",
            "database encryption",
            "field level encryption",
            "key management",
            "encryption policy",
            "cryptography policy",
            "pseudonymise",
            "tokenisation",
            "data masking",
            "AES",
            "end to end encryption",
        ],
        "scenario": [
            "do we need to encrypt personal data",
            "what encryption does GDPR require",
            "is our encryption sufficient for GDPR",
            "laptop encryption GDPR",
            "cloud storage encryption",
            "email encryption personal data",
            "database contains personal data encryption",
            "personal data in S3 bucket",
            "encryption key management procedure",
        ],
        "confusion": [
            "anonymisation",   # stronger than pseudonymisation — Art.32.1.a
                               # covers pseudonymisation, not anonymisation
            "data masking",    # A.8.11 — related but distinct ISO control
            "Art.34.3.a",      # encryption reduces breach notification obligation
                               # but that is a different node
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.32.1.b — Confidentiality, integrity, availability, resilience
# ═══════════════════════════════════════════════════════════════════════════

"Art.32.1.b": {
    "business_description": (
        "This sub-point maps directly to the classic Confidentiality, Integrity and Availability (CIA) triad from information "
        "security, with 'resilience' added — making it Confidentiality, Integrity, Availability and Resilience (CIAR). Confidentiality "
        "means personal data is accessible only to authorised parties. Integrity "
        "means data is accurate and has not been tampered with. Availability "
        "means data is accessible when needed. Resilience means the processing "
        "systems can withstand and recover from disruption. The explicit addition "
        "of 'resilience' to the traditional CIA triad reflects the General Data Protection Regulation (GDPR) concern "
        "with continuity of processing — where a security incident "
        "— such as a ransomware attack, Distributed Denial of Service (DDoS), or unauthorised deletion — "
        "causes a loss of availability of personal data, that loss may itself "
        "constitute a personal data breach under Art.4(12), triggering the "
        "notification obligations in Art.33. A planned maintenance window does "
        "not. The distinction is causation: availability disruption caused by a "
        "security incident is a potential breach; disruption from routine "
        "operations is not. This sub-point is the basis for access control, "
        "backup, and business continuity requirements under GDPR."
    ),
    "query_keywords": {
        "exact": [
            "confidentiality integrity availability and resilience",
            "ongoing confidentiality integrity availability",
            "resilience of processing systems and services",
            "CIA triad",
            "CIAR",
        ],
        "practitioner": [
            "data confidentiality",
            "data integrity",
            "system availability",
            "business resilience",
            "system resilience",
            "access control GDPR",
            "backup GDPR",
            "business continuity GDPR",
            "uptime personal data systems",
            "GDPR availability obligation",
        ],
        "scenario": [
            "system outage affecting personal data",
            "unauthorised access to personal data systems",
            "data tampering",
            "backup and recovery for GDPR",
            "business continuity plan GDPR",
            "personal data system downtime",
        ],
        "confusion": [
            "Art.32.1.c",  # restoration after incident — adjacent but distinct
            "Art.5.1.f",   # the security principle — broader, covers all of Art.32
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.32.1.c — Restoration of availability and access
# ═══════════════════════════════════════════════════════════════════════════

"Art.32.1.c": {
    "business_description": (
        "This sub-point requires the ability to restore access to personal data "
        "in a timely manner after a physical or technical incident. In practice "
        "this means having tested backup and recovery procedures specifically "
        "covering personal data systems. 'Timely' is not defined in the General Data Protection Regulation (GDPR) — "
        "it depends on the nature of the processing. A hospital patient records "
        "system requires faster restoration than a marketing database. The key "
        "word is 'ability' — organisations must be able to demonstrate they can "
        "restore, not just that they have backups. Untested backups that have "
        "never been verified do not satisfy this obligation. This sub-point is "
        "closely related to ISO 27001's requirements for backup (A.8.13) and "
        "redundancy (A.8.14), and links to business continuity planning."
    ),
    "query_keywords": {
        "exact": [
            "restore the availability and access to personal data",
            "timely manner",
            "physical or technical incident",
            "restoration",
        ],
        "practitioner": [
            "backup and recovery GDPR",
            "data restoration",
            "restore personal data",
            "disaster recovery GDPR",
            "backup testing",
            "recovery time objective",
            "RTO personal data",
            "RPO personal data",
            "business continuity personal data",
            "data recovery procedure",
        ],
        "scenario": [
            "ransomware attack personal data",
            "database failure personal data",
            "server crash personal data",
            "can we recover personal data after incident",
            "backup restore test GDPR",
            "data centre outage",
        ],
        "confusion": [
            "Art.32.1.b",  # ongoing availability — this node is about restoration
                           # after an incident, not ongoing availability
            "Art.33",      # breach notification — incident may trigger Art.33
                           # but restoration is Art.32.1.c
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.32.1.d — Regular testing and evaluation
# ═══════════════════════════════════════════════════════════════════════════

"Art.32.1.d": {
    "business_description": (
        "This sub-point requires a documented process for regularly testing, "
        "assessing, and evaluating the effectiveness of security measures — "
        "not just implementing them and assuming they work. 'Regularly' is "
        "not defined in the General Data Protection Regulation (GDPR) text; the appropriate frequency depends on "
        "the risk level of the processing. ArionComply advises a minimum of "
        "annual testing as a baseline for standard-risk processing, with more "
        "frequent testing — quarterly or continuous — for high-risk processing "
        "such as large-scale processing of special category data or critical "
        "infrastructure. This creates an obligation for ongoing assurance activity: "
        "penetration testing, vulnerability assessments, security audits, "
        "and review of security controls. The key requirement is that it is "
        "a 'process' — ad hoc or one-off tests do not satisfy this. Results "
        "must be documented and used to improve security measures. This "
        "obligation is what underpins requirements for vulnerability management "
        "programmes, security testing in development, and periodic security "
        "reviews of third-party processors."
    ),
    "query_keywords": {
        "exact": [
            "regularly testing assessing and evaluating",
            "effectiveness of technical and organisational measures",
            "process for regularly testing",
        ],
        "practitioner": [
            "penetration testing GDPR",
            "pen test",
            "vulnerability assessment GDPR",
            "security testing",
            "security audit GDPR",
            "security review",
            "security testing frequency",
            "how often security test",
            "GDPR security assurance",
            "security control testing",
            "VAPT",
            "vulnerability management GDPR",
        ],
        "scenario": [
            "do we need to do penetration testing for GDPR",
            "how often do we need to test security for GDPR",
            "security testing programme GDPR",
            "third party security audit",
            "annual security review personal data",
        ],
        "confusion": [
            "Art.35",     # DPIA — impact assessment before processing, not
                          # ongoing testing of existing measures
            "A.8.8",      # ISO vulnerability management — implements this
            "A.8.29",     # ISO security testing in development — implements this
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.32.4 — Instructions-only processing
# ═══════════════════════════════════════════════════════════════════════════

"Art.32.4": {
    "business_description": (
        "This paragraph requires controllers and processors to ensure that "
        "anyone who has access to personal data — staff, contractors, system "
        "administrators — only processes it on documented instructions from "
        "the controller, unless legally required to act otherwise. In practice "
        "this means: role-based access controls limiting who can access data, "
        "documented data handling instructions (often part of employment "
        "contracts or data handling policies), confidentiality obligations "
        "for staff with data access, and training to ensure staff understand "
        "their obligations. This is where General Data Protection Regulation (GDPR) creates a direct obligation "
        "around staff data handling behaviour, not just technical measures. "
        "It is the GDPR equivalent of ISO 27001 A.6.3 (information security "
        "awareness), A.5.3 (segregation of duties), and the confidentiality "
        "clause in A.6.6."
    ),
    "query_keywords": {
        "exact": [
            "except on instructions from the controller",
            "acting under the authority of the controller or the processor",
            "access to personal data",
            "does not process them except on instructions",
        ],
        "practitioner": [
            "staff data handling",
            "employee data access",
            "data handling instructions",
            "confidentiality obligations staff",
            "data processing instructions",
            "staff access to personal data",
            "role based access control GDPR",
            "need to know principle GDPR",
            "authorised access personal data",
            "data handling training",
        ],
        "scenario": [
            "staff accessing personal data they should not",
            "employee misuse of personal data",
            "contractor access to personal data",
            "system administrator access personal data",
            "need to know basis personal data",
        ],
        "confusion": [
            "Art.29",    # same concept for processor staff — Art.32.4 is the
                         # controller/processor obligation; Art.29 is the
                         # processor-specific formulation
            "Art.28.3.a", # documented instructions in the contract — Art.32.4
                          # is the operational obligation, not the contractual one
        ],
    },
},

}  # end TIER1_ENRICHMENT


# ── Metadata ──────────────────────────────────────────────────────────────────

CLUSTER_METADATA = {
    "cluster":        "GDPR Security of Processing",
    "articles":       ["Art.32", "Art.32.1", "Art.32.1.a", "Art.32.1.b",
                       "Art.32.1.c", "Art.32.1.d", "Art.32.4"],
    "primary_source": "GDPR 2016/679 Art.32 verbatim text",
    "secondary_sources": [
        "EDPB Guidelines 4/2019 on Art.25 (security context)",
        "ENISA Guidelines on Security Measures for Art.32",
        "ICO Security guidance (ico.org.uk)",
        "WP29 Opinion 05/2014 on anonymisation techniques",
        "Recital 83 (security risk assessment rationale)",
    ],
    "authored_by":    "ArionComply Tier 1 — manual authoring",
    "review_status":  "REVIEWED_v1",
    "review_notes":   "Art.32.1.b: availability disruption narrowed to security-incident-caused loss. Art.32.1.d: annual frequency labelled as ArionComply advisory position, not regulatory mandate.",
}
