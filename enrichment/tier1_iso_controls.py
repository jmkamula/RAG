"""
Tier 1 Enrichment — ISO 27001:2022 Controls
Covers: 5.1, 5.2, 6.1.2, 6.1.3 (Governance)
        A.5.15-18 (Access Control)
        A.5.24-27 (Incident Management)
        A.8.24 (Cryptography)
        A.8.7-8 (Malware/Vulnerability)
        A.5.19-21 (Supplier Security)

Sources:
  - ISO 27001:2022 standard clauses and Annex A control titles
  - ISO 27002:2022 implementation guidance
  - NCSC 10 Steps to Cyber Security
  - CIS Critical Security Controls v8
  - ENISA Good Practice Guide for Incident Management
  - GDPR cross-framework mappings (cross_framework_summary on nodes)

Note: ISO nodes have no obligation_text until ISO 27002 PDF is ingested
(Phase 3). Business descriptions are authored from ISO 27002:2022
implementation guidance and industry best practice.
"""

TIER1_ENRICHMENT = {

# ═══════════════════════════════════════════════════════════════════════════
# ISO GOVERNANCE — 5.1, 5.2, 6.1.2, 6.1.3
# ═══════════════════════════════════════════════════════════════════════════

"5.1": {
    "business_description": (
        "Clause 5.1 requires top management to demonstrate leadership and "
        "commitment to the Information Security Management System (ISMS). "
        "This is not a delegable obligation — the standard requires "
        "evidence that senior leadership personally drives information "
        "security, not merely that they have appointed someone to manage it. "
        "In practice, evidence of leadership commitment includes: approved "
        "information security policy signed by a director; board-level "
        "reporting on security risks and incidents; resources allocated to "
        "information security; and visible senior management participation "
        "in security activities. ISO 27001:2022 auditors specifically look "
        "for evidence that top management understands the ISMS objectives "
        "and can articulate how security aligns with business strategy. "
        "Absence of visible management commitment is one of the most common "
        "audit findings. This clause also satisfies the General Data "
        "Protection Regulation (GDPR) Art.24 accountability requirement "
        "for management oversight of data protection."
    ),
    "query_keywords": {
        "exact": [
            "leadership and commitment",
            "top management",
            "information security management system",
            "ISMS",
        ],
        "practitioner": [
            "management commitment security",
            "board security oversight",
            "senior management information security",
            "ISMS leadership",
            "security governance",
            "information security policy sign off",
            "top management ISMS",
        ],
        "scenario": [
            "board needs to approve security policy",
            "getting management buy-in for security",
            "evidence of leadership commitment for ISO audit",
            "management reporting on security",
        ],
        "confusion": [
            "5.2",       # security policy — 5.2 is about the policy itself;
                         # 5.1 is about management commitment to the whole ISMS
        ],
    },
},

"5.2": {
    "business_description": (
        "Clause 5.2 requires top management to establish an information "
        "security policy that is appropriate to the organisation's purpose, "
        "includes information security objectives or provides a framework "
        "for setting them, commits to satisfying applicable requirements, "
        "and commits to continual improvement of the Information Security "
        "Management System (ISMS). The policy must be communicated within "
        "the organisation and made available to interested parties as "
        "appropriate. In practice: the policy must be formally approved "
        "by a director or the board, not just the IT or security function; "
        "it must be reviewed periodically (typically annually); all staff "
        "with access to information assets must have seen and understood "
        "it; and evidence of communication must be retained. The information "
        "security policy is the anchor document for the entire ISMS and "
        "the first document an ISO 27001 auditor will examine."
    ),
    "query_keywords": {
        "exact": [
            "information security policy",
            "appropriate to the purpose of the organisation",
            "continual improvement",
        ],
        "practitioner": [
            "information security policy",
            "IS policy",
            "security policy",
            "ISMS policy",
            "security policy requirements ISO 27001",
            "what must be in information security policy",
        ],
        "scenario": [
            "writing an information security policy",
            "reviewing our security policy",
            "security policy for ISO 27001 certification",
            "board approval of security policy",
        ],
        "confusion": [
            "5.1",       # leadership commitment — 5.2 is the policy;
                         # 5.1 is the commitment to the ISMS as a whole
            "A.5.1",     # Annex A control for policies — 5.2 is the
                         # management system requirement; A.5.1 is the
                         # operational policy control
        ],
    },
},

"6.1.2": {
    "business_description": (
        "Clause 6.1.2 requires the organisation to perform an information "
        "security risk assessment process that establishes and maintains "
        "criteria for accepting risks, identifies risks associated with "
        "the loss of confidentiality, integrity and availability of "
        "information assets, analyses and evaluates those risks, and "
        "prioritises them for treatment. This is the core analytical "
        "engine of the Information Security Management System (ISMS) — "
        "all security control selection must be justified by the risk "
        "assessment. A risk assessment that was completed once and not "
        "revisited does not satisfy this clause; it must be a living "
        "process updated when significant changes occur and reviewed at "
        "planned intervals. The risk assessment output must be documented "
        "and retained as evidence. ArionComply advises reviewing the risk "
        "assessment at minimum annually and following any significant "
        "change to systems, infrastructure, or the threat landscape."
    ),
    "query_keywords": {
        "exact": [
            "information security risk assessment",
            "risk acceptance criteria",
            "loss of confidentiality integrity and availability",
        ],
        "practitioner": [
            "risk assessment ISO 27001",
            "information security risk assessment",
            "ISMS risk assessment",
            "security risk assessment",
            "risk register",
            "asset risk assessment",
            "threat and vulnerability assessment",
        ],
        "scenario": [
            "conducting our annual risk assessment",
            "risk assessment for ISO 27001",
            "identifying information security risks",
            "risk register update",
        ],
        "confusion": [
            "6.1.3",     # risk treatment — 6.1.2 identifies and assesses
                         # risks; 6.1.3 is about selecting controls to
                         # treat them
            "A.5.19",    # supplier risk — a category of risk but not
                         # the risk assessment process itself
        ],
    },
},

"6.1.3": {
    "business_description": (
        "Clause 6.1.3 requires the organisation to determine and implement "
        "appropriate risk treatment options based on the risk assessment "
        "(6.1.2), select controls necessary for the chosen risk treatment "
        "options (referencing Annex A and other sources), produce a "
        "Statement of Applicability (SoA) documenting which controls "
        "are applied and justified, and obtain risk owner sign-off on "
        "the residual risk. The Statement of Applicability is one of the "
        "most important documents for ISO 27001 certification — it formally "
        "documents which of the 93 Annex A controls are applicable to the "
        "organisation, whether they are implemented, and why any controls "
        "are excluded. Risk treatment options are: modify (implement controls "
        "to reduce risk), retain (accept the risk), avoid (stop the "
        "activity), or share (transfer to insurer or third party). The "
        "Information Security Management System (ISMS) must document "
        "the risk treatment plan and track implementation progress."
    ),
    "query_keywords": {
        "exact": [
            "risk treatment",
            "statement of applicability",
            "SoA",
            "risk treatment plan",
            "residual risk",
        ],
        "practitioner": [
            "statement of applicability",
            "SoA",
            "risk treatment plan",
            "Annex A controls selection",
            "risk treatment ISO 27001",
            "which controls to implement",
            "risk acceptance",
            "risk owner",
        ],
        "scenario": [
            "creating our statement of applicability",
            "selecting Annex A controls",
            "risk treatment decisions",
            "which risks to accept vs treat",
            "ISO 27001 SoA",
        ],
        "confusion": [
            "6.1.2",     # risk assessment — 6.1.3 treats risks identified
                         # in 6.1.2; they are sequential steps in the same
                         # risk management process
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# ISO ACCESS CONTROL — A.5.15, A.5.16, A.5.17, A.5.18
# ═══════════════════════════════════════════════════════════════════════════

"A.5.15": {
    "business_description": (
        "Control A.5.15 requires policies and rules for access control to "
        "be established, documented, and reviewed based on business and "
        "information security requirements. Access control policy defines "
        "the principles that govern who can access what — the principle "
        "of least privilege (users get the minimum access needed for their "
        "role), need-to-know (access to sensitive information is limited to "
        "those who need it), and segregation of duties (no single person "
        "controls an entire process). In practice, the access control "
        "policy provides the framework; the operational controls in "
        "A.5.16 (identity management), A.5.17 (authentication), and "
        "A.5.18 (access rights) implement it. This control also directly "
        "implements the General Data Protection Regulation (GDPR) "
        "obligation in Art.32.4 (authorised access to personal data) "
        "and Art.5.1.f (integrity and confidentiality principle)."
    ),
    "query_keywords": {
        "exact": [
            "access control",
            "access control policy",
            "least privilege",
            "need to know",
        ],
        "practitioner": [
            "access control policy",
            "role based access control",
            "RBAC",
            "least privilege",
            "need to know",
            "access management policy",
            "user access policy",
            "logical access control",
        ],
        "scenario": [
            "implementing access control",
            "access control policy for ISO 27001",
            "controlling who can access what",
            "user access management",
        ],
        "confusion": [
            "A.5.16",    # identity management — A.5.15 is the policy;
                         # A.5.16 is the identity management implementation
            "A.5.18",    # access rights — A.5.15 is the policy framework;
                         # A.5.18 is the provisioning and review process
        ],
    },
},

"A.5.16": {
    "business_description": (
        "Control A.5.16 requires the full lifecycle of identities to be "
        "managed: creation, maintenance, and deletion of user identities "
        "across all systems. An identity management process must ensure "
        "that users are uniquely identified (no shared accounts), that "
        "identities are linked to real individuals who are accountable "
        "for their actions, that access granted on joining is appropriate "
        "to the role, and that identities are promptly disabled or deleted "
        "when the individual leaves or changes role. Shared accounts and "
        "generic administrative accounts represent a significant risk — "
        "they prevent attributing actions to specific individuals and make "
        "it impossible to revoke individual access. In multi-system "
        "environments, an Identity and Access Management (IAM) system or "
        "a centralised directory (such as Microsoft Active Directory or "
        "a cloud Identity Provider (IdP)) is the standard approach to "
        "managing identity lifecycle at scale."
    ),
    "query_keywords": {
        "exact": [
            "identity management",
            "unique identification",
        ],
        "practitioner": [
            "identity management",
            "IAM",
            "identity and access management",
            "user lifecycle management",
            "joiner mover leaver",
            "onboarding offboarding access",
            "shared accounts",
            "generic accounts",
            "active directory",
            "IdP",
            "identity provider",
            "single sign on",
            "SSO",
        ],
        "scenario": [
            "managing user accounts across systems",
            "employee leaves access not revoked",
            "shared admin accounts",
            "identity lifecycle management",
            "new employee onboarding access",
        ],
        "confusion": [
            "A.5.15",    # access control policy — A.5.16 is the identity
                         # management implementation; A.5.15 is the policy
            "A.5.18",    # access rights — A.5.16 manages identities;
                         # A.5.18 manages the rights granted to those identities
        ],
    },
},

"A.5.17": {
    "business_description": (
        "Control A.5.17 requires authentication information — passwords, "
        "tokens, certificates, and other credentials — to be managed "
        "securely. This includes: provisioning temporary credentials "
        "that must be changed on first use; enforcing a password policy "
        "covering length, complexity, and history; prohibiting shared "
        "authentication information; protecting authentication credentials "
        "in storage (hashing with a strong algorithm); and implementing "
        "multi-factor authentication (MFA) for privileged access and "
        "remote access. ISO 27002:2022 guidance recommends MFA for all "
        "accounts with access to personal data — a position consistent "
        "with the Information Commissioner's Office (ICO) technical "
        "guidance on security measures under the General Data Protection "
        "Regulation (GDPR). Password policies should follow current "
        "guidance (such as National Institute of Standards and Technology "
        "(NIST) SP 800-63B) which prioritises length and breach-checking "
        "over complexity requirements."
    ),
    "query_keywords": {
        "exact": [
            "authentication information",
            "password",
            "multi-factor authentication",
            "MFA",
        ],
        "practitioner": [
            "password policy",
            "MFA",
            "multi-factor authentication",
            "two factor authentication",
            "2FA",
            "authentication controls",
            "privileged access authentication",
            "password management",
            "credential management",
            "SSO",
        ],
        "scenario": [
            "implementing MFA",
            "password policy requirements",
            "privileged account authentication",
            "remote access security",
            "authentication for cloud systems",
        ],
        "confusion": [
            "A.5.16",    # identity management — A.5.17 is about securing
                         # credentials; A.5.16 is about managing the identities
                         # those credentials authenticate
        ],
    },
},

"A.5.18": {
    "business_description": (
        "Control A.5.18 requires access rights to be provisioned, reviewed, "
        "modified, and removed through a formal process. Three key "
        "requirements: provisioning must follow the principle of least "
        "privilege and require authorisation from the asset owner; "
        "access rights must be reviewed periodically (ArionComply advises "
        "at minimum annually, with more frequent reviews for privileged "
        "access); and access must be removed promptly on role change or "
        "departure. The access review process — sometimes called a "
        "User Access Review (UAR) or recertification — is a key control "
        "that auditors check for ISO 27001 and is also required evidence "
        "for the General Data Protection Regulation (GDPR) Art.32.4 "
        "obligation (processing only on instructions). Organisations "
        "without a documented access review process, or with access "
        "reviews that are only conducted annually for all access types "
        "including privileged, represent a significant risk."
    ),
    "query_keywords": {
        "exact": [
            "access rights",
            "provisioning",
            "removal of access rights",
            "access review",
        ],
        "practitioner": [
            "access rights review",
            "user access review",
            "UAR",
            "access recertification",
            "provisioning access",
            "revoking access",
            "access rights management",
            "privileged access review",
            "leavers access",
        ],
        "scenario": [
            "reviewing user access rights",
            "employee left access still active",
            "access rights audit",
            "periodic access review",
            "removing access on role change",
        ],
        "confusion": [
            "A.5.15",    # access control policy — A.5.18 is the operational
                         # access rights process; A.5.15 is the policy
            "A.8.2",     # privileged access rights — a more specific control
                         # for privileged/administrative access
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# ISO INCIDENT MANAGEMENT — A.5.24, A.5.25, A.5.26, A.5.27
# ═══════════════════════════════════════════════════════════════════════════

"A.5.24": {
    "business_description": (
        "Control A.5.24 requires the organisation to plan and prepare for "
        "managing information security incidents through documented "
        "responsibilities, procedures, and reporting mechanisms. An incident "
        "management capability must exist before incidents occur — "
        "organisations that try to respond to incidents without established "
        "procedures consistently perform worse than those with documented, "
        "rehearsed processes. The incident management plan must define: "
        "what constitutes an information security event and incident; "
        "who is responsible for incident detection, reporting, triage, "
        "response, and recovery; escalation procedures including when to "
        "involve senior management, legal, and communications; and how "
        "to preserve evidence for potential investigation. This control "
        "directly enables the General Data Protection Regulation (GDPR) "
        "breach notification obligations under Art.33 and Art.34 — an "
        "organisation without an incident management process is unlikely "
        "to be able to meet the 72-hour supervisory authority notification "
        "deadline."
    ),
    "query_keywords": {
        "exact": [
            "information security incident management",
            "incident management planning and preparation",
            "responsibilities and procedures",
        ],
        "practitioner": [
            "incident response plan",
            "IRP",
            "incident management procedure",
            "security incident procedure",
            "incident response playbook",
            "incident management planning",
            "security incident response",
        ],
        "scenario": [
            "creating an incident response plan",
            "preparing for security incidents",
            "incident management for ISO 27001",
            "security incident process",
        ],
        "confusion": [
            "A.5.25",    # assessment and decision — A.5.24 is planning and
                         # preparation; A.5.25 is assessing events when they
                         # occur
            "Art.33",    # GDPR breach notification — A.5.24 enables Art.33
                         # but is a broader incident management control
        ],
    },
},

"A.5.25": {
    "business_description": (
        "Control A.5.25 requires information security events to be assessed "
        "and a decision made as to whether they should be classified as "
        "information security incidents. Not all security events are "
        "incidents — a failed login attempt is an event; repeated failed "
        "attempts followed by a successful login from an unusual location "
        "is an incident. The assessment process must be documented so that "
        "decisions are consistent and defensible. For organisations subject "
        "to the General Data Protection Regulation (GDPR), this assessment "
        "also determines whether a personal data breach has occurred and "
        "whether the 72-hour Art.33 notification clock has started. "
        "ArionComply advises that the assessment process should include an "
        "explicit personal data breach determination step — a documented "
        "decision that either confirms a breach has occurred (starting the "
        "clock) or records the rationale for concluding no breach occurred."
    ),
    "query_keywords": {
        "exact": [
            "assessment and decision on information security events",
            "classified as incidents",
        ],
        "practitioner": [
            "incident triage",
            "security event assessment",
            "incident classification",
            "is this a security incident",
            "incident severity classification",
            "personal data breach determination",
        ],
        "scenario": [
            "assessing whether an event is an incident",
            "triage security events",
            "incident classification process",
            "determining if a data breach occurred",
        ],
        "confusion": [
            "A.5.24",    # planning — A.5.25 is operational assessment;
                         # A.5.24 is the planning and preparation beforehand
            "A.5.26",    # response — A.5.25 determines if it is an incident;
                         # A.5.26 responds to confirmed incidents
        ],
    },
},

"A.5.26": {
    "business_description": (
        "Control A.5.26 requires incidents to be responded to in accordance "
        "with documented procedures. Response activities include: containment "
        "(limiting the spread or impact of the incident), evidence "
        "preservation (for forensic investigation and potential legal "
        "proceedings), eradication (removing the threat), and recovery "
        "(restoring systems and services to normal operation). The response "
        "procedure must specify who has the authority to take containment "
        "actions — including taking systems offline if necessary — and "
        "the communications process for notifying affected parties. For "
        "incidents involving personal data, the response procedure must "
        "integrate with the General Data Protection Regulation (GDPR) "
        "breach notification process: the incident response team must be "
        "able to determine whether a personal data breach has occurred "
        "and trigger the 72-hour notification process where required. "
        "Forensic evidence preservation must not compromise the ability "
        "to contain and recover from the incident."
    ),
    "query_keywords": {
        "exact": [
            "response to information security incidents",
            "containment",
            "evidence collection",
            "eradication",
            "recovery",
        ],
        "practitioner": [
            "incident response",
            "security incident response",
            "containment",
            "incident containment",
            "breach response",
            "cyber incident response",
            "incident recovery",
            "forensic evidence",
        ],
        "scenario": [
            "responding to a security incident",
            "containing a data breach",
            "recovering from a cyberattack",
            "incident response for ransomware",
            "evidence preservation during incident",
        ],
        "confusion": [
            "A.5.25",    # assessment — A.5.26 responds to confirmed incidents;
                         # A.5.25 determines whether an event is an incident
            "A.5.27",    # learning — A.5.26 is the response; A.5.27 is
                         # learning from the incident after it is resolved
        ],
    },
},

"A.5.27": {
    "business_description": (
        "Control A.5.27 requires knowledge gained from analysing information "
        "security incidents to be used to reduce the likelihood or impact of "
        "future incidents. Post-incident review — sometimes called a "
        "post-incident analysis, lessons-learned review, or root cause "
        "analysis — must be conducted after significant incidents and the "
        "findings must be acted upon. This control prevents organisations "
        "from repeatedly experiencing the same types of incidents because "
        "root causes are never addressed. In practice: a post-incident "
        "review should be conducted within 2–4 weeks of incident resolution; "
        "the review should identify root causes, contributing factors, and "
        "effectiveness of the response; findings should be tracked through "
        "to completion; and significant findings should be fed back into "
        "the risk assessment (6.1.2) and control framework. This control "
        "also directly informs the General Data Protection Regulation (GDPR) "
        "Art.32.1.d requirement to regularly evaluate the effectiveness of "
        "security measures."
    ),
    "query_keywords": {
        "exact": [
            "learning from information security incidents",
            "post-incident",
            "lessons learned",
            "root cause",
        ],
        "practitioner": [
            "post incident review",
            "lessons learned",
            "root cause analysis",
            "incident post mortem",
            "after action review",
            "incident improvement",
            "PIR",
        ],
        "scenario": [
            "post incident review process",
            "learning from a security incident",
            "root cause analysis after breach",
            "improving security after incident",
        ],
        "confusion": [
            "A.5.26",    # response — A.5.27 is post-incident learning;
                         # A.5.26 is the active response during the incident
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# ISO CRYPTOGRAPHY — A.8.24
# ═══════════════════════════════════════════════════════════════════════════

"A.8.24": {
    "business_description": (
        "Control A.8.24 requires the organisation to define and implement "
        "rules for the effective use of cryptography to protect information. "
        "A cryptography policy must cover: which types of information require "
        "encryption and at what classification level; approved encryption "
        "algorithms and key lengths (current best practice: AES-256 for "
        "symmetric encryption, RSA-2048 or higher / Elliptic Curve "
        "Cryptography (ECC) P-256 for asymmetric); key management lifecycle "
        "including generation, distribution, storage, rotation, and "
        "destruction; and who is responsible for cryptographic decisions. "
        "This control directly implements the General Data Protection "
        "Regulation (GDPR) Art.32.1.a obligation (pseudonymisation and "
        "encryption of personal data) and supports Art.34.3.a (encryption "
        "as a mitigation reducing the obligation to notify data subjects "
        "following a breach). A.8.24 is the ISO control most frequently "
        "cited in GDPR enforcement actions alongside Art.32."
    ),
    "query_keywords": {
        "exact": [
            "use of cryptography",
            "cryptography policy",
            "key management",
            "encryption algorithm",
        ],
        "practitioner": [
            "encryption policy",
            "cryptography policy",
            "key management",
            "encryption standards",
            "approved algorithms",
            "AES-256",
            "TLS",
            "Transport Layer Security (TLS)",
            "certificate management",
            "PKI",
            "public key infrastructure",
            "data at rest encryption",
            "data in transit encryption",
        ],
        "scenario": [
            "implementing encryption policy",
            "what encryption to use",
            "key management procedure",
            "encrypting databases containing personal data",
            "encryption for cloud storage",
        ],
        "confusion": [
            "A.8.11",    # data masking — related but different; A.8.24 is
                         # encryption; A.8.11 is pseudonymisation/masking
            "Art.32.1.a", # GDPR encryption obligation — A.8.24 is the ISO
                          # control that implements Art.32.1.a
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# ISO VULNERABILITY — A.8.7, A.8.8
# ═══════════════════════════════════════════════════════════════════════════

"A.8.7": {
    "business_description": (
        "Control A.8.7 requires protection against malware — malicious "
        "software including viruses, ransomware, trojans, spyware, and "
        "adware. Protection must be implemented across all systems and "
        "must include detection, prevention, and recovery capabilities. "
        "Anti-malware software alone is no longer sufficient — modern "
        "malware increasingly evades signature-based detection. ISO "
        "27002:2022 guidance includes: user education (the primary "
        "infection vector is still social engineering); controls on "
        "software installation; network-level controls to detect and "
        "block malicious traffic; endpoint detection and response (EDR); "
        "and tested backup and recovery processes. Ransomware in particular "
        "has direct General Data Protection Regulation (GDPR) implications: "
        "a ransomware attack that encrypts personal data constitutes "
        "a personal data breach (loss of availability and potentially "
        "confidentiality) and may trigger Art.33 notification obligations. "
        "Organisations without adequate malware protection face both "
        "operational and regulatory risk."
    ),
    "query_keywords": {
        "exact": [
            "protection against malware",
            "malware",
            "ransomware",
            "antivirus",
        ],
        "practitioner": [
            "anti-malware",
            "antivirus",
            "EDR",
            "endpoint detection and response",
            "ransomware protection",
            "malware protection",
            "endpoint security",
            "malicious software protection",
        ],
        "scenario": [
            "ransomware attack protection",
            "malware on endpoint",
            "antivirus requirements ISO 27001",
            "endpoint protection",
        ],
        "confusion": [
            "A.8.8",     # vulnerability management — A.8.7 is malware
                         # protection; A.8.8 is managing technical
                         # vulnerabilities that malware exploits
        ],
    },
},

"A.8.8": {
    "business_description": (
        "Control A.8.8 requires technical vulnerabilities in systems to "
        "be identified, assessed, and remediated. A vulnerability management "
        "programme must: identify systems in scope; obtain timely information "
        "about vulnerabilities in those systems (via vendor alerts, National "
        "Vulnerability Database (NVD), Common Vulnerabilities and Exposures "
        "(CVE) feeds); assess the risk posed by each vulnerability in the "
        "organisation's specific context; and apply patches or mitigating "
        "controls within a risk-based timeframe. ArionComply advises a "
        "patch management policy that defines target remediation timescales "
        "by severity: critical vulnerabilities within 24-72 hours, high "
        "within 7-14 days, medium within 30 days. This control directly "
        "implements the General Data Protection Regulation (GDPR) Art.32.1.d "
        "obligation (regular testing and evaluation of security measures) "
        "and is a mandatory control in most cyber insurance frameworks. "
        "Systems running end-of-life software with no patch support represent "
        "an automatic high risk in any GDPR security assessment."
    ),
    "query_keywords": {
        "exact": [
            "management of technical vulnerabilities",
            "vulnerability management",
            "patch management",
            "CVE",
        ],
        "practitioner": [
            "vulnerability management",
            "patch management",
            "vulnerability scanning",
            "CVE",
            "Common Vulnerabilities and Exposures (CVE)",
            "NVD",
            "patching",
            "vulnerability assessment",
            "penetration testing",
            "security scanning",
            "end of life software",
        ],
        "scenario": [
            "unpatched systems",
            "vulnerability scanning programme",
            "patch management process",
            "critical vulnerability remediation",
            "end of life operating systems",
        ],
        "confusion": [
            "A.8.7",     # malware protection — A.8.8 manages the vulnerabilities
                         # that malware exploits; A.8.7 is malware detection
                         # and prevention
            "Art.32.1.d", # GDPR security testing — A.8.8 implements this
                          # GDPR obligation
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# ISO SUPPLIER SECURITY — A.5.19, A.5.20, A.5.21
# ═══════════════════════════════════════════════════════════════════════════

"A.5.19": {
    "business_description": (
        "Control A.5.19 requires processes to be implemented and maintained "
        "to manage information security risks in supplier relationships. "
        "Suppliers — including cloud providers, managed service providers, "
        "software vendors, and contractors — represent a significant attack "
        "surface. Supply chain attacks have become one of the most impactful "
        "threat vectors: a compromise of a trusted supplier can provide "
        "access to all of their customers. Supplier security management "
        "must cover: identifying which suppliers have access to the "
        "organisation's systems or information; assessing supplier security "
        "before engagement (due diligence); establishing security "
        "requirements in supplier agreements (A.5.20); monitoring supplier "
        "security performance during the relationship; and managing "
        "offboarding securely. This control also directly supports the "
        "General Data Protection Regulation (GDPR) Art.28 obligation "
        "(processor due diligence and Data Processing Agreements (DPAs)) "
        "for suppliers processing personal data."
    ),
    "query_keywords": {
        "exact": [
            "information security in supplier relationships",
            "supplier security",
            "supply chain security",
            "third party security",
        ],
        "practitioner": [
            "supplier security",
            "third party risk",
            "third party risk management",
            "vendor security",
            "supply chain risk",
            "supplier due diligence",
            "TPRM",
            "third party risk management",
        ],
        "scenario": [
            "assessing supplier security",
            "third party risk management",
            "supplier security assessment",
            "cloud provider security",
            "managed service provider security",
        ],
        "confusion": [
            "A.5.20",    # supplier agreements — A.5.19 is the overall
                         # supplier security programme; A.5.20 is the
                         # contractual security requirements
            "Art.28",    # GDPR processor obligations — A.5.19 is the ISO
                         # control; Art.28 is the GDPR equivalent
        ],
    },
},

"A.5.20": {
    "business_description": (
        "Control A.5.20 requires information security requirements to be "
        "established and agreed with each supplier and reflected in "
        "supplier agreements. Security requirements in supplier contracts "
        "should cover: the security measures the supplier must implement; "
        "the right to audit the supplier's security; incident notification "
        "obligations (including timescales); access and authentication "
        "requirements; data handling and disposal obligations; and "
        "subcontractor management. For suppliers processing personal data, "
        "the supplier agreement must also serve as a Data Processing "
        "Agreement (DPA) under General Data Protection Regulation (GDPR) "
        "Art.28 containing the eight mandatory clauses. ArionComply "
        "recommends maintaining a standard security schedule for inclusion "
        "in all supplier contracts and a separate, more detailed DPA "
        "template for suppliers acting as data processors."
    ),
    "query_keywords": {
        "exact": [
            "supplier agreements",
            "information security requirements",
            "addressing information security within supplier agreements",
        ],
        "practitioner": [
            "supplier contract security",
            "security clauses in contracts",
            "vendor contract security",
            "supplier security requirements",
            "third party contract",
            "right to audit supplier",
        ],
        "scenario": [
            "what security clauses to include in supplier contracts",
            "reviewing supplier agreement for security",
            "supplier contract for cloud services",
        ],
        "confusion": [
            "A.5.19",    # supplier security programme — A.5.20 is the
                         # contractual requirements; A.5.19 is the broader
                         # supplier security management process
            "Art.28.3",  # DPA mandatory clauses — A.5.20 includes DPA
                         # requirements; Art.28.3 specifies the GDPR mandatory
                         # clauses
        ],
    },
},

"A.5.21": {
    "business_description": (
        "Control A.5.21 extends supplier security to the entire Information "
        "and Communications Technology (ICT) supply chain — including "
        "hardware manufacturers, software developers, and service providers "
        "in the chain that delivers technology components to the organisation. "
        "Supply chain attacks targeting software build pipelines, hardware "
        "firmware, and managed service providers have become a primary "
        "threat vector. This control requires organisations to: understand "
        "their ICT supply chain; establish practices for vetting suppliers "
        "at each tier; require suppliers to cascade security requirements "
        "to their own suppliers; and monitor for security issues in supply "
        "chain components. In practice for most organisations, this means: "
        "software composition analysis to identify open source vulnerabilities; "
        "scrutiny of cloud and Software as a Service (SaaS) providers' "
        "subprocessor and supply chain practices; and inclusion of supply "
        "chain security requirements in procurement criteria."
    ),
    "query_keywords": {
        "exact": [
            "ICT supply chain",
            "information and communications technology supply chain",
            "supply chain security",
        ],
        "practitioner": [
            "ICT supply chain security",
            "software supply chain",
            "open source security",
            "software composition analysis",
            "SCA",
            "supply chain attack",
            "subcontractor security",
            "SaaS supply chain",
        ],
        "scenario": [
            "software supply chain attack",
            "open source library vulnerabilities",
            "cloud provider supply chain",
            "third party software security",
            "SolarWinds type attack",
        ],
        "confusion": [
            "A.5.19",    # general supplier security — A.5.21 is specifically
                         # ICT supply chain; A.5.19 is all supplier relationships
            "A.5.20",    # supplier agreements — A.5.21 extends requirements
                         # into the deeper supply chain
        ],
    },
},

}  # end TIER1_ENRICHMENT

CLUSTER_METADATA = {
    "cluster":       "ISO 27001:2022 Controls — Governance, Access, Incident, Crypto, Vulnerability, Supplier",
    "controls":      ["5.1", "5.2", "6.1.2", "6.1.3",
                      "A.5.15", "A.5.16", "A.5.17", "A.5.18",
                      "A.5.24", "A.5.25", "A.5.26", "A.5.27",
                      "A.8.24", "A.8.7", "A.8.8",
                      "A.5.19", "A.5.20", "A.5.21"],
    "primary_source": "ISO 27001:2022 standard + ISO 27002:2022 implementation guidance",
    "secondary_sources": [
        "NCSC 10 Steps to Cyber Security",
        "CIS Critical Security Controls v8",
        "ENISA Good Practice Guide for Incident Management",
        "NIST SP 800-63B (authentication guidance)",
        "GDPR Art.32 cross-framework mappings",
    ],
    "authored_by":   "ArionComply Tier 1 — manual authoring",
    "review_status": "PENDING_REVIEW",
    "review_notes":  "",
}
