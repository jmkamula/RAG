"""
Tier 1 Enrichment — GDPR Controller Obligations + Records
Covers: Art.24, Art.25, Art.28, Art.30

Sources:
  - GDPR Art.24, 25, 28, 30 verbatim text
  - EDPB Guidelines 07/2020 on the concepts of controller and processor
  - EDPB Guidelines 4/2019 on Art.25 data protection by design and default
  - ICO guidance on accountability and governance
  - ICO guidance on contracts and liabilities with processors
  - WP29 Guidelines on data processors (WP169)
  - Recitals 74, 75, 78, 81, 82

Key positions:
  Art.24: Accountability is demonstrated, not just claimed — evidence required
  Art.25: Privacy by design applies at design time, not retrospectively
  Art.28: DPAs are mandatory, not optional — and content is prescribed
  Art.30: RoPA must be maintained AND kept current — not a one-time exercise
"""

TIER1_ENRICHMENT = {

# ═══════════════════════════════════════════════════════════════════════════
# Art.24 — Responsibility of the controller
# ═══════════════════════════════════════════════════════════════════════════

"Art.24": {
    "business_description": (
        "Article 24 establishes the accountability principle as an active "
        "obligation: controllers must not only comply with the General Data "
        "Protection Regulation (GDPR), they must be able to demonstrate "
        "compliance. This shifts the burden of proof onto the organisation "
        "— in a regulatory investigation, it is the controller's "
        "responsibility to show that appropriate measures are in place, not "
        "the regulator's responsibility to prove they are absent. 'Appropriate "
        "technical and organisational measures' under Art.24 are broader than "
        "security measures under Art.32 — they encompass all compliance "
        "measures including policies, training, governance structures, "
        "records, and DPIAs. The measures must be reviewed and updated "
        "where necessary, making compliance a continuous obligation not a "
        "one-time project. Where proportionate, Art.24 requires data "
        "protection policies — the basis for an organisation's privacy policy "
        "and internal data handling policies."
    ),
    "query_keywords": {
        "exact": [
            "responsibility of the controller",
            "able to demonstrate",
            "appropriate technical and organisational measures",
            "reviewed and updated where necessary",
        ],
        "practitioner": [
            "accountability GDPR",
            "demonstrate compliance",
            "prove GDPR compliance",
            "GDPR accountability obligation",
            "data protection governance",
            "controller responsibility",
            "data protection policy",
            "compliance programme GDPR",
            "GDPR documentation requirements",
        ],
        "scenario": [
            "regulator asks us to prove we are compliant",
            "what evidence do we need for GDPR compliance",
            "data protection audit",
            "ICO investigation",
            "how do we demonstrate accountability",
        ],
        "confusion": [
            "Art.5.2",   # the accountability principle — Art.24 is the
                         # operational obligation flowing from Art.5.2
            "Art.32",    # security measures specifically — Art.24 covers
                         # all compliance measures, not just security
        ],
    },
},

"Art.24.1": {
    "business_description": (
        "The operative paragraph of the accountability obligation. Four "
        "factors calibrate what measures are 'appropriate': the nature, "
        "scope, context and purposes of the processing, and the risks to "
        "individuals' rights and freedoms. A small organisation doing "
        "low-risk processing faces a proportionately lower documentation "
        "burden than a large organisation profiling individuals for credit "
        "scoring. The measures must be reviewed and updated — the GDPR "
        "does not permit a static compliance position. Organisations that "
        "completed a General Data Protection Regulation (GDPR) project in "
        "2018 and have not revisited it since are not in compliance with "
        "this paragraph. In practice, accountability evidence includes: "
        "data protection policies, Records of Processing Activities (RoPA), "
        "Data Protection Impact Assessments (DPIAs), processor contracts, "
        "staff training records, and a Data Protection Officer (DPO) "
        "appointment where required."
    ),
    "query_keywords": {
        "exact": [
            "nature scope context and purposes of processing",
            "risks of varying likelihood and severity",
            "reviewed and updated where necessary",
        ],
        "practitioner": [
            "GDPR compliance programme",
            "data protection measures",
            "accountability documentation",
            "GDPR review",
            "data protection governance framework",
        ],
        "scenario": [
            "what does GDPR accountability require in practice",
            "our GDPR compliance is out of date",
            "updating data protection measures",
        ],
        "confusion": [
            "Art.32.1",  # the security risk calibration — similar four-factor
                         # test but for security measures only
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.25 — Data protection by design and by default
# ═══════════════════════════════════════════════════════════════════════════

"Art.25": {
    "business_description": (
        "Article 25 requires data protection to be built into systems and "
        "processes from the outset — not added as an afterthought. Privacy "
        "by design (Art.25.1) means data protection measures are integrated "
        "during system design, development, and procurement. Privacy by "
        "default (Art.25.2) means that, without any action by the "
        "individual, only the minimum necessary personal data is processed. "
        "Together these obligations create a requirement to consider data "
        "protection before systems are built, not after. The European Data "
        "Protection Board (EDPB) Guidelines 4/2019 set out seven "
        "foundational principles: proactive not reactive, privacy as the "
        "default, privacy embedded into design, full functionality, "
        "end-to-end security, visibility and transparency, and respect for "
        "user privacy. Certification mechanisms under Art.42 can be used "
        "to demonstrate compliance with Art.25."
    ),
    "query_keywords": {
        "exact": [
            "data protection by design and by default",
            "privacy by design",
            "privacy by default",
            "at the time of the determination of the means",
        ],
        "practitioner": [
            "privacy by design",
            "privacy by default",
            "build in privacy",
            "data protection in system design",
            "GDPR for developers",
            "privacy engineering",
            "data minimisation by design",
            "privacy requirements for new systems",
            "PbD",
        ],
        "scenario": [
            "building a new system that processes personal data",
            "procuring software that handles personal data",
            "designing a new product with user data",
            "app development GDPR requirements",
            "privacy requirements before going live",
        ],
        "confusion": [
            "Art.32",    # security of processing — Art.25 is about design
                         # and minimisation, Art.32 is about security measures
            "Art.35",    # DPIA — related but distinct; Art.35 is an
                         # assessment before high-risk processing
        ],
    },
},

"Art.25.1": {
    "business_description": (
        "Privacy by design requires controllers to implement data protection "
        "measures both at the time of designing the processing system and "
        "at the time of the processing itself. Pseudonymisation is "
        "specifically mentioned as an example of a technical design measure. "
        "The obligation applies to controllers procuring systems as well as "
        "those building them — a controller who procures a system that does "
        "not meet privacy by design requirements cannot shift responsibility "
        "to the vendor. In practice, privacy by design requires: privacy "
        "impact screening for new projects, data protection requirements in "
        "technical specifications, developer training on privacy engineering, "
        "and design review checkpoints that include privacy assessment. "
        "The General Data Protection Regulation (GDPR) does not specify how "
        "privacy by design must be implemented — ArionComply recommends "
        "adopting a privacy impact screening process triggered at project "
        "initiation and a privacy review gate before system launch."
    ),
    "query_keywords": {
        "exact": [
            "at the time of the determination of the means for processing",
            "pseudonymisation",
            "implement data-protection principles in an effective manner",
        ],
        "practitioner": [
            "privacy impact screening",
            "privacy review",
            "data protection requirements for development",
            "GDPR software development",
            "privacy checklist for developers",
            "data protection by design implementation",
        ],
        "scenario": [
            "new feature collects personal data",
            "software procurement with personal data",
            "how to implement privacy by design",
            "privacy in the development lifecycle",
        ],
        "confusion": [
            "Art.25.2",  # privacy by default — separate obligation about
                         # minimum data processing by default settings
        ],
    },
},

"Art.25.2": {
    "business_description": (
        "Privacy by default requires that, without any action by the "
        "individual, only the minimum personal data necessary for the "
        "specific purpose is processed. This applies to the amount of data "
        "collected, the extent of processing, storage periods, and "
        "accessibility. In practical terms: pre-ticked consent boxes "
        "violate this obligation; optional data fields should default to "
        "empty, not pre-filled; sharing settings should default to private "
        "not public; retention periods should default to minimum, not "
        "maximum. The European Data Protection Board (EDPB) has taken "
        "enforcement action against social media platforms for defaulting "
        "to maximum data sharing rather than minimum. The test is: "
        "if a user takes no action at all, does the system process the "
        "minimum necessary data? If not, the default settings must be changed."
    ),
    "query_keywords": {
        "exact": [
            "by default only personal data which are necessary",
            "privacy by default",
            "amount of personal data collected",
            "extent of their processing",
            "period of their storage",
            "accessibility",
        ],
        "practitioner": [
            "default settings GDPR",
            "pre-ticked boxes",
            "opt-in by default",
            "minimum data by default",
            "data minimisation defaults",
            "privacy settings default",
        ],
        "scenario": [
            "default sharing settings on our platform",
            "optional fields in registration form",
            "pre-populated consent checkboxes",
            "user settings default to public",
        ],
        "confusion": [
            "Art.7",     # consent — pre-ticked boxes violate both Art.25.2
                         # and Art.7, but Art.25.2 is the design obligation
            "Art.5.1.c", # data minimisation principle — Art.25.2 is the
                         # operational implementation of that principle
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.28 — Processor obligations
# ═══════════════════════════════════════════════════════════════════════════

"Art.28": {
    "business_description": (
        "Article 28 governs the relationship between controllers and their "
        "processors — organisations that process personal data on a "
        "controller's behalf. There are two core obligations: controllers "
        "must only use processors that provide 'sufficient guarantees' of "
        "security and compliance (Art.28.1), and the processing relationship "
        "must be governed by a binding contract — a Data Processing "
        "Agreement (DPA) — containing the mandatory clauses prescribed in "
        "Art.28.3. This is not optional: processing by a processor without "
        "a compliant DPA in place is a General Data Protection Regulation "
        "(GDPR) violation by the controller regardless of what the processor "
        "does or does not do. Every cloud provider, payroll processor, "
        "marketing platform, and IT support vendor that accesses personal "
        "data is likely a processor requiring a DPA. Standard Contractual "
        "Clauses are often used but must contain the Art.28.3 mandatory "
        "clauses to be compliant."
    ),
    "query_keywords": {
        "exact": [
            "sufficient guarantees",
            "data processing agreement",
            "processing by a processor shall be governed by a contract",
        ],
        "practitioner": [
            "data processing agreement",
            "DPA",
            "processor contract",
            "GDPR contract with suppliers",
            "vendor GDPR compliance",
            "third party processing agreement",
            "processor due diligence",
            "cloud provider GDPR",
            "subprocessor",
            "who is a processor",
        ],
        "scenario": [
            "cloud provider handling personal data",
            "payroll provider has access to employee data",
            "marketing platform processes customer data",
            "IT support can access personal data",
            "do we need a DPA with our supplier",
        ],
        "confusion": [
            "Art.26",    # joint controllers — Art.28 is controller/processor;
                         # Art.26 is where two controllers share responsibility
            "Art.29",    # processing under authority — distinct from the
                         # contractual DPA requirement in Art.28
        ],
    },
},

"Art.28.1": {
    "business_description": (
        "Before engaging a processor, the controller must assess whether "
        "the processor provides 'sufficient guarantees' to implement "
        "appropriate technical and organisational measures. This means "
        "processor due diligence is a General Data Protection Regulation "
        "(GDPR) obligation, not just good practice. Due diligence should "
        "cover: the processor's security certifications (ISO 27001, "
        "SOC 2 Type II), their data protection policies, their breach "
        "notification procedures, their subprocessor management, and "
        "whether they will accept the mandatory Data Processing Agreement (DPA) clauses. The "
        "Information Commissioner's Office (ICO) and other supervisory "
        "authorities expect controllers to be able to demonstrate that "
        "processor selection was based on an assessment of compliance "
        "capability. Relying solely on a processor's contractual "
        "representations without any assessment may not satisfy this "
        "obligation."
    ),
    "query_keywords": {
        "exact": [
            "sufficient guarantees to implement appropriate technical",
            "processors providing sufficient guarantees",
        ],
        "practitioner": [
            "processor due diligence",
            "supplier GDPR assessment",
            "vendor assessment GDPR",
            "how to assess a processor",
            "processor security assessment",
            "third party risk assessment GDPR",
        ],
        "scenario": [
            "onboarding a new supplier that processes personal data",
            "assessing cloud provider GDPR compliance",
            "what to check before using a processor",
        ],
        "confusion": [
            "Art.28.3",  # the DPA content requirements — Art.28.1 is the
                         # assessment before engagement, Art.28.3 is the
                         # contract content after engagement
        ],
    },
},

"Art.28.3": {
    "business_description": (
        "The Data Processing Agreement (DPA) governing processor "
        "relationships must contain eight specific obligations on the "
        "processor prescribed by the General Data Protection Regulation "
        "(GDPR): (a) process data only on the controller's documented "
        "instructions; (b) ensure persons authorised to process have "
        "committed to confidentiality; (c) implement security measures "
        "under Art.32; (d) respect subprocessor restrictions; (e) assist "
        "the controller with data subject rights; (f) assist with security, "
        "breach notification, Data Protection Impact Assessments (DPIAs) "
        "and prior consultation; (g) delete or return data at the end of "
        "services; and (h) make available all information needed for the "
        "controller to demonstrate compliance and allow audits. A DPA that "
        "omits any of these clauses is non-compliant regardless of what "
        "other terms it contains. The European Data Protection Board (EDPB) "
        "has confirmed that standard template DPAs from cloud providers "
        "must contain all eight obligations to be valid."
    ),
    "query_keywords": {
        "exact": [
            "only on documented instructions from the controller",
            "committed themselves to confidentiality",
            "measures required pursuant to Article 32",
            "delete or returns all the personal data",
            "allow for audits",
        ],
        "practitioner": [
            "DPA mandatory clauses",
            "data processing agreement content",
            "what must a DPA contain",
            "GDPR contract requirements processor",
            "processor contract mandatory terms",
            "DPA template",
            "Art.28 contract clauses",
        ],
        "scenario": [
            "reviewing a processor contract",
            "drafting a DPA",
            "cloud provider DPA review",
            "does this DPA meet GDPR requirements",
        ],
        "confusion": [
            "Art.46",    # standard contractual clauses for international
                         # transfers — different instrument, different purpose
            "Art.28.1",  # due diligence — Art.28.3 is the contract content,
                         # Art.28.1 is the assessment before contracting
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.30 — Records of processing activities
# ═══════════════════════════════════════════════════════════════════════════

"Art.30": {
    "business_description": (
        "Article 30 requires controllers and processors to maintain a "
        "Record of Processing Activities (RoPA) — a living inventory of "
        "every personal data processing activity the organisation undertakes. "
        "The RoPA is one of the most practically important accountability "
        "documents under the General Data Protection Regulation (GDPR) and "
        "is typically the first document a supervisory authority requests "
        "in an investigation. Controllers and processors have separate "
        "RoPA obligations: controllers record their own processing (Art.30.1); "
        "processors record the processing they carry out on behalf of each "
        "controller (Art.30.2). Organisations with fewer than 250 employees "
        "have a partial exemption but it is narrow — it only applies where "
        "processing is not likely to result in risk, is not carried out "
        "regularly, and does not involve special category data. Most "
        "organisations do not qualify for this exemption in full."
    ),
    "query_keywords": {
        "exact": [
            "record of processing activities",
            "RoPA",
            "records of processing activities",
        ],
        "practitioner": [
            "data inventory",
            "processing register",
            "record of processing",
            "data mapping",
            "GDPR data inventory",
            "article 30 record",
            "processing activities register",
            "250 employee exemption",
            "RoPA template",
        ],
        "scenario": [
            "creating a record of processing activities",
            "updating our data inventory",
            "supervisory authority requested our processing records",
            "do we need a RoPA",
            "small organisation RoPA exemption",
        ],
        "confusion": [
            "Art.35",    # DPIA — a DPIA is for specific high-risk processing;
                         # the RoPA is a comprehensive register of all processing
            "Art.13",    # privacy notice — the RoPA is an internal document;
                         # privacy notices are the external-facing equivalent
        ],
    },
},

"Art.30.1": {
    "business_description": (
        "The controller's Record of Processing Activities (RoPA) must "
        "contain seven categories of information for each processing activity: "
        "(a) the name and contact details of the controller, joint controller, "
        "representative and Data Protection Officer (DPO); (b) the purposes "
        "of the processing; (c) a description of data subject categories and "
        "personal data categories; (d) the categories of recipients; "
        "(e) transfers to third countries and the safeguards in place; "
        "(f) envisaged erasure timeframes; and (g) a general description of "
        "security measures. In practice, the RoPA also typically records "
        "the lawful basis for processing (Art.6/9), the system or location "
        "where data is held, and the data owner — though these are not "
        "explicitly required by Art.30.1, they are necessary to support "
        "other General Data Protection Regulation (GDPR) obligations. The "
        "RoPA must be available to the supervisory authority on request and "
        "must be kept current as processing activities change."
    ),
    "query_keywords": {
        "exact": [
            "purposes of the processing",
            "categories of data subjects",
            "categories of recipients",
            "envisaged time limits for erasure",
        ],
        "practitioner": [
            "controller RoPA",
            "what to include in RoPA",
            "RoPA fields",
            "data inventory fields",
            "processing activity record content",
        ],
        "scenario": [
            "building our RoPA",
            "what fields does our data inventory need",
            "RoPA template for controller",
        ],
        "confusion": [
            "Art.30.2",  # processor RoPA — Art.30.1 is for controllers,
                         # Art.30.2 is for processors; both may apply to the
                         # same organisation in different capacities
        ],
    },
},

"Art.30.2": {
    "business_description": (
        "Processors must maintain their own Record of Processing Activities "
        "(RoPA) recording: the name and contact details of the processor "
        "and each controller on whose behalf they process; the categories "
        "of processing carried out for each controller; any transfers to "
        "third countries; and a general description of security measures. "
        "This is separate from and in addition to the controller's own "
        "RoPA. Organisations acting as both controller and processor — "
        "common in technology businesses that process customer data (as "
        "controller) and also process data on behalf of business clients "
        "(as processor) — must maintain two separate RoPA records. The "
        "processor RoPA is available to the supervisory authority on request "
        "alongside the controller RoPA."
    ),
    "query_keywords": {
        "exact": [
            "processor shall maintain a record",
            "categories of processing carried out on behalf of each controller",
        ],
        "practitioner": [
            "processor RoPA",
            "processor data inventory",
            "we process data on behalf of clients",
            "processor record of processing",
            "SaaS provider processing records",
        ],
        "scenario": [
            "we are a processor for our clients",
            "our platform processes client data on their behalf",
            "technology company acting as processor",
        ],
        "confusion": [
            "Art.30.1",  # controller RoPA — both may apply if the organisation
                         # acts as both controller and processor
        ],
    },
},

}  # end TIER1_ENRICHMENT

CLUSTER_METADATA = {
    "cluster":       "GDPR Controller Obligations and Records",
    "articles":      ["Art.24", "Art.24.1", "Art.25", "Art.25.1", "Art.25.2",
                      "Art.28", "Art.28.1", "Art.28.3", "Art.30", "Art.30.1",
                      "Art.30.2"],
    "primary_source": "GDPR 2016/679 Art.24, 25, 28, 30",
    "secondary_sources": [
        "EDPB Guidelines 07/2020 on controller and processor concepts",
        "EDPB Guidelines 4/2019 on Art.25 data protection by design",
        "ICO guidance: Accountability and governance",
        "ICO guidance: Contracts and liabilities with processors",
        "WP29 Guidelines on data processors (WP169)",
        "Recitals 74, 75, 78, 81, 82",
    ],
    "authored_by":   "ArionComply Tier 1 — manual authoring",
    "review_status": "PENDING_REVIEW",
    "review_notes":  "",
}
