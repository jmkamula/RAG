"""
Tier 1 Enrichment — GDPR Principles (Art.5–7) + DPIA/DPO (Art.35, 37)

Sources:
  - GDPR Art.5, 6, 7, 35, 37 verbatim text
  - EDPB Guidelines 05/2020 on consent
  - EDPB Guidelines 3/2022 on deceptive design patterns
  - EDPB Guidelines 4/2022 on the calculation of fines
  - EDPB Guidelines 9/2020 on DPIA triggers
  - EDPB Guidelines 04/2017 on DPO designation
  - ICO guidance on lawful bases for processing
  - ICO guidance on legitimate interests
  - ICO DPIA guidance
  - Recitals 32, 33, 37, 38, 39, 40-50, 89-96, 97
"""

TIER1_ENRICHMENT = {

# ═══════════════════════════════════════════════════════════════════════════
# Art.5 — The six principles
# ═══════════════════════════════════════════════════════════════════════════

"Art.5": {
    "business_description": (
        "Article 5 establishes the six foundational principles that govern "
        "all personal data processing under the General Data Protection "
        "Regulation (GDPR): lawfulness, fairness and transparency; purpose "
        "limitation; data minimisation; accuracy; storage limitation; and "
        "integrity and confidentiality. A seventh principle — accountability "
        "— is added by Art.5.2 and requires the controller to be able to "
        "demonstrate compliance with all six. These principles are not "
        "abstract — every processing activity must be capable of being "
        "justified against each of them. Failure on any single principle "
        "is a violation of Art.5, which carries the highest GDPR fines: "
        "up to €20M or 4% of global annual turnover under Art.83(5). The "
        "principles underpin all other GDPR obligations — understanding "
        "them is the foundation for understanding the rest of the regulation."
    ),
    "query_keywords": {
        "exact": [
            "principles relating to processing of personal data",
            "lawfulness fairness and transparency",
            "purpose limitation",
            "data minimisation",
            "accuracy",
            "storage limitation",
            "integrity and confidentiality",
        ],
        "practitioner": [
            "GDPR principles",
            "data protection principles",
            "six principles GDPR",
            "Art.5 principles",
            "fundamental GDPR obligations",
            "core GDPR requirements",
        ],
        "scenario": [
            "are we processing data lawfully",
            "do we comply with the GDPR principles",
            "data protection principles assessment",
        ],
        "confusion": [
            "Art.6",     # lawful basis — Art.5.1.a requires lawfulness
                         # as a principle; Art.6 specifies the lawful bases
            "Art.5.2",   # accountability principle — separate from the six
                         # processing principles in Art.5.1
        ],
    },
},

"Art.5.1": {
    "business_description": (
        "The six processing principles collectively define what lawful "
        "personal data processing looks like. They apply cumulatively — "
        "all six must be satisfied simultaneously for every processing "
        "activity. A processing activity that has a lawful basis (Art.5.1.a) "
        "but collects more data than necessary (Art.5.1.c) still violates "
        "Art.5. The principles are self-reinforcing: purpose limitation "
        "(Art.5.1.b) constrains what can be done with data once collected; "
        "data minimisation (Art.5.1.c) constrains how much is collected; "
        "storage limitation (Art.5.1.e) constrains how long it is kept; "
        "integrity and confidentiality (Art.5.1.f) constrains how it is "
        "protected. Together they describe the complete lifecycle of "
        "responsible personal data processing."
    ),
    "query_keywords": {
        "exact": [
            "personal data shall be",
            "lawfully fairly and in a transparent manner",
        ],
        "practitioner": [
            "all GDPR principles",
            "data protection principles checklist",
            "processing principles GDPR",
        ],
        "scenario": [
            "assessing compliance with GDPR principles",
            "GDPR principles review",
        ],
        "confusion": [],
    },
},

"Art.5.1.a": {
    "business_description": (
        "Personal data must be processed lawfully, fairly, and transparently. "
        "Lawfulness requires a valid legal basis under Art.6 (and Art.9 for "
        "special categories). Fairness requires that processing does not "
        "operate against individuals' reasonable expectations — processing "
        "data in ways people would not expect, even with a technical legal "
        "basis, can still be unfair. Transparency requires that individuals "
        "are told about the processing through privacy notices complying "
        "with Art.13 and 14. All three elements must be met: having a lawful "
        "basis does not automatically satisfy fairness or transparency. The "
        "Information Commissioner's Office (ICO) and the European Data "
        "Protection Board (EDPB) regularly cite failures of fairness and "
        "transparency in enforcement actions against organisations that "
        "technically had a legal basis but processed data in ways individuals "
        "did not expect."
    ),
    "query_keywords": {
        "exact": [
            "lawfully fairly and in a transparent manner",
            "lawfulness fairness and transparency",
        ],
        "practitioner": [
            "lawful basis GDPR",
            "fair processing",
            "transparent processing",
            "privacy notice requirement",
            "processing lawfully",
            "GDPR lawful processing",
        ],
        "scenario": [
            "are we processing personal data lawfully",
            "do we have a legal basis for processing",
            "are we being transparent about data use",
        ],
        "confusion": [
            "Art.6",     # lawful basis — Art.5.1.a is the principle;
                         # Art.6 lists the specific lawful bases
        ],
    },
},

"Art.5.1.b": {
    "business_description": (
        "Personal data collected for one purpose cannot be reused for an "
        "incompatible purpose without a fresh lawful basis or data subject "
        "consent. Purpose limitation is one of the most frequently violated "
        "GDPR principles — it is breached whenever data collected for "
        "service delivery is then used for marketing without consent, when "
        "HR data is used for purposes beyond employment, or when customer "
        "data is sold or shared with third parties in ways not disclosed at "
        "collection. Further processing for archiving in the public interest, "
        "scientific research, or statistical purposes may be compatible under "
        "Art.89. To assess compatibility, controllers must consider: the "
        "link between the original and new purposes, the nature of the data, "
        "the consequences for individuals, and the existence of appropriate "
        "safeguards. The General Data Protection Regulation (GDPR) "
        "compatibility test is conducted by the controller — it is not a "
        "license to process for any purpose with a plausible link."
    ),
    "query_keywords": {
        "exact": [
            "specified explicit and legitimate purposes",
            "purpose limitation",
            "not further processed in a manner that is incompatible",
        ],
        "practitioner": [
            "purpose limitation",
            "reuse of personal data",
            "secondary use of data",
            "using data for new purposes",
            "purpose compatibility",
            "can we use data for marketing",
            "data collected for one purpose used for another",
        ],
        "scenario": [
            "want to use customer data for a new purpose",
            "repurposing data collected from customers",
            "using service data for analytics",
            "sharing customer data with a third party",
        ],
        "confusion": [
            "Art.6",     # lawful basis for the new processing activity —
                         # purpose limitation and lawful basis are separate
                         # but both must be satisfied
        ],
    },
},

"Art.5.1.c": {
    "business_description": (
        "Data minimisation requires that personal data collected is "
        "adequate (sufficient for the purpose), relevant (pertinent to "
        "the purpose), and limited to what is necessary (no more than "
        "needed). This principle directly limits what data can be collected "
        "at the point of collection — not just how long it is kept "
        "(that is storage limitation, Art.5.1.e). In practice, data "
        "minimisation means: registration forms should only require fields "
        "genuinely needed; systems should not log more data than necessary; "
        "APIs should not return more data than the calling application needs. "
        "Data minimisation is also implemented technically through privacy "
        "by default (Art.25.2) — systems should be configured to collect "
        "the minimum by default, not the maximum. The General Data Protection "
        "Regulation (GDPR) does not specify what is 'necessary' for a given "
        "purpose — this is a proportionality assessment that controllers "
        "must document and be able to justify."
    ),
    "query_keywords": {
        "exact": [
            "adequate relevant and limited to what is necessary",
            "data minimisation",
        ],
        "practitioner": [
            "data minimisation",
            "collect only what you need",
            "minimum data collection",
            "limit data collection",
            "GDPR data collection requirements",
            "necessity of data collection",
            "do we need all this data",
        ],
        "scenario": [
            "registration form collects too much data",
            "system logs contain personal data not needed",
            "API returns more data than required",
            "reducing data collection for GDPR",
        ],
        "confusion": [
            "Art.5.1.e", # storage limitation — data minimisation is about
                         # what is collected; storage limitation is about
                         # how long it is kept
        ],
    },
},

"Art.5.1.d": {
    "business_description": (
        "Personal data must be accurate and kept up to date where necessary. "
        "Controllers must take every reasonable step to ensure inaccurate "
        "data is erased or rectified without delay. The accuracy obligation "
        "is both a principle (Art.5.1.d) and a data subject right "
        "(Art.16 — right to rectification). In practice, this means: "
        "data capture processes should validate data at point of entry; "
        "data held for extended periods should be subject to periodic "
        "review and refresh procedures; processes must exist to update "
        "data when individuals notify the organisation of changes; and "
        "inaccurate data used in automated decision-making must be "
        "correctable. 'Where necessary' acknowledges that some data "
        "(e.g. historical records) need not be updated — the obligation "
        "applies where accuracy matters for the processing purpose."
    ),
    "query_keywords": {
        "exact": [
            "accurate and where necessary kept up to date",
            "accuracy",
            "inaccurate personal data are erased or rectified without delay",
        ],
        "practitioner": [
            "data accuracy GDPR",
            "accurate personal data",
            "keeping data up to date",
            "data quality GDPR",
            "right to rectification",
            "inaccurate data",
            "data correction",
        ],
        "scenario": [
            "customer notified us their data is wrong",
            "our data may be out of date",
            "how to handle data accuracy for GDPR",
            "automated decisions based on personal data",
        ],
        "confusion": [
            "Art.16",    # right to rectification — the data subject's right
                         # flowing from the accuracy principle
        ],
    },
},

"Art.5.1.e": {
    "business_description": (
        "Personal data must not be kept in a form that identifies individuals "
        "for longer than is necessary for the processing purpose. Once the "
        "purpose is fulfilled, the data must be deleted, anonymised, or "
        "pseudonymised. The General Data Protection Regulation (GDPR) does "
        "not specify retention periods — organisations must determine "
        "appropriate periods based on the purpose, applicable law, and "
        "business need. A retention schedule documenting the rationale for "
        "each data category's retention period is the standard accountability "
        "evidence for this principle. Exceptions include processing for "
        "archiving in the public interest, scientific research, historical "
        "research, or statistical purposes subject to Art.89 safeguards. "
        "Keeping data 'just in case it might be useful' does not satisfy "
        "storage limitation — there must be a defined purpose for retention."
    ),
    "query_keywords": {
        "exact": [
            "no longer than is necessary",
            "storage limitation",
            "kept in a form which permits identification",
        ],
        "practitioner": [
            "data retention",
            "how long to keep personal data",
            "retention period GDPR",
            "retention schedule",
            "data deletion GDPR",
            "delete personal data",
            "when to delete data",
            "data lifecycle GDPR",
        ],
        "scenario": [
            "how long can we keep customer data",
            "setting retention periods for personal data",
            "deleting personal data after contract ends",
            "archiving personal data",
            "backup retention GDPR",
        ],
        "confusion": [
            "Art.5.1.c", # data minimisation — minimisation is about what
                         # is collected; retention/storage limitation is
                         # about how long it is kept
            "Art.17",    # right to erasure — the data subject right flowing
                         # from the storage limitation principle
        ],
    },
},

"Art.5.1.f": {
    "business_description": (
        "Personal data must be processed in a manner that ensures appropriate "
        "security, including protection against unauthorised or unlawful "
        "processing and against accidental loss, destruction or damage. "
        "This is the 'integrity and confidentiality' principle — the "
        "security principle in Art.5.1 — and it is the foundation for the "
        "more detailed security obligations in Art.32. Art.5.1.f is a "
        "principle; Art.32 is the implementing obligation that specifies "
        "what security measures must look like. A breach of Art.32 is also "
        "a breach of Art.5.1.f, but the Article 5 breach attracts the "
        "higher Art.83(5) fine ceiling (€20M / 4% turnover) rather than "
        "the Art.83(4) ceiling (€10M / 2% turnover) that applies to Art.32 "
        "in isolation. The General Data Protection Regulation (GDPR) "
        "regulators regularly cite Art.5.1.f alongside Art.32 in security "
        "enforcement actions."
    ),
    "query_keywords": {
        "exact": [
            "integrity and confidentiality",
            "appropriate security of the personal data",
            "protection against unauthorised or unlawful processing",
            "accidental loss destruction or damage",
        ],
        "practitioner": [
            "security principle GDPR",
            "data security GDPR principle",
            "integrity and confidentiality principle",
            "GDPR security obligation",
            "protect personal data",
        ],
        "scenario": [
            "security breach of personal data",
            "what are our security obligations under GDPR principles",
        ],
        "confusion": [
            "Art.32",    # security of processing — Art.5.1.f is the
                         # principle; Art.32 is the detailed implementation
                         # obligation. Both are typically cited together
                         # in enforcement action.
        ],
    },
},

"Art.5.2": {
    "business_description": (
        "The accountability principle requires the controller to be "
        "responsible for and able to demonstrate compliance with all six "
        "principles in Art.5.1. 'Responsible for' means the controller "
        "cannot outsource its compliance — it owns the obligation. 'Able "
        "to demonstrate' means maintaining evidence of compliance that "
        "can be produced to a supervisory authority on demand. Together "
        "these obligations underpin the entire General Data Protection "
        "Regulation (GDPR) accountability framework and flow into the "
        "specific obligations in Art.24 (policies and measures), Art.30 "
        "(records), Art.37 (Data Protection Officer (DPO) appointment), "
        "and Art.35 (Data Protection Impact Assessments (DPIAs)). "
        "Art.5.2 is frequently cited in enforcement decisions as the "
        "umbrella accountability violation where an organisation has failed "
        "to maintain adequate evidence of compliance, even where individual "
        "processing activities were compliant."
    ),
    "query_keywords": {
        "exact": [
            "responsible for and be able to demonstrate compliance",
            "accountability",
        ],
        "practitioner": [
            "accountability principle GDPR",
            "demonstrate GDPR compliance",
            "prove compliance with GDPR",
            "GDPR accountability",
            "compliance evidence GDPR",
        ],
        "scenario": [
            "ICO asked us to demonstrate compliance",
            "what evidence do we need for GDPR",
            "regulatory investigation GDPR",
        ],
        "confusion": [
            "Art.24",    # Art.24 is the operational obligation flowing from
                         # Art.5.2 — same concept, Art.24 gives it substance
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.6 — Lawful bases for processing
# ═══════════════════════════════════════════════════════════════════════════

"Art.6": {
    "business_description": (
        "Article 6 lists the six lawful bases for processing personal data. "
        "Every processing activity must be matched to one of these bases "
        "before processing begins. The six bases are: (a) consent; "
        "(b) contract performance; (c) legal obligation; (d) vital interests; "
        "(e) public task; and (f) legitimate interests. The choice of lawful "
        "basis matters — it determines what rights data subjects have, and "
        "what happens when they exercise them. If processing is based on "
        "consent, the data subject can withdraw it. If based on contract, "
        "the processing continues while the contract exists. If based on "
        "legitimate interests, the data subject can object. Controllers "
        "must identify and document their lawful basis before processing "
        "begins and include it in their privacy notice. Switching lawful "
        "basis after the fact — particularly from legitimate interests to "
        "consent when challenged — is not permitted under the General Data "
        "Protection Regulation (GDPR)."
    ),
    "query_keywords": {
        "exact": [
            "lawfulness of processing",
            "processing shall be lawful only if",
            "at least one of the following applies",
        ],
        "practitioner": [
            "lawful basis",
            "legal basis for processing",
            "six lawful bases",
            "legitimate interests",
            "legal obligation GDPR",
            "consent as lawful basis",
            "contract performance GDPR",
            "Art.6 lawful basis",
            "which lawful basis",
        ],
        "scenario": [
            "what lawful basis do we have for processing this data",
            "choosing the right lawful basis",
            "can we rely on legitimate interests",
            "do we need consent",
            "processing employee data lawful basis",
        ],
        "confusion": [
            "Art.7",     # consent conditions — Art.6.1.a refers to consent;
                         # Art.7 specifies the conditions consent must meet
            "Art.5.1.a", # lawfulness principle — Art.5.1.a requires lawfulness;
                         # Art.6 provides the lawful bases
        ],
    },
},

"Art.6.1": {
    "business_description": (
        "The six specific lawful bases are: (a) consent — freely given, "
        "specific, informed and unambiguous; (b) contract — necessary for "
        "performance of a contract with the data subject; (c) legal "
        "obligation — necessary for compliance with a legal obligation; "
        "(d) vital interests — necessary to protect someone's life; "
        "(e) public task — necessary for performing a public function; "
        "and (f) legitimate interests — necessary for the legitimate "
        "interests of the controller or a third party, unless overridden "
        "by the data subject's interests. Legitimate interests (f) is the "
        "most flexible but also the most contested basis — it requires a "
        "Legitimate Interests Assessment (LIA) balancing the organisation's "
        "interests against those of data subjects. It cannot be used as a "
        "default or fallback when other bases are unavailable. The General "
        "Data Protection Regulation (GDPR) requires the selected basis to "
        "be appropriate to the processing — not merely technically applicable."
    ),
    "query_keywords": {
        "exact": [
            "consent",
            "performance of a contract",
            "legal obligation",
            "vital interests",
            "public task",
            "legitimate interests",
            "legitimate interests assessment",
            "LIA",
        ],
        "practitioner": [
            "consent vs legitimate interests",
            "legitimate interests assessment",
            "LIA",
            "which lawful basis for marketing",
            "employment data lawful basis",
            "B2B data lawful basis",
            "direct marketing lawful basis",
        ],
        "scenario": [
            "can we use legitimate interests for marketing",
            "do we need consent for this processing",
            "what basis for employee monitoring",
            "lawful basis for CCTV",
        ],
        "confusion": [
            "Art.9",     # special category data requires an additional basis
                         # under Art.9 in addition to an Art.6 basis
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.7 — Consent
# ═══════════════════════════════════════════════════════════════════════════

"Art.7": {
    "business_description": (
        "Article 7 sets out the conditions that make consent valid under "
        "the General Data Protection Regulation (GDPR). Consent must be: "
        "freely given (no penalty for refusal, no bundling with service "
        "terms), specific (separate consent for each distinct purpose), "
        "informed (data subjects know who is processing and why), and "
        "unambiguous (a clear affirmative act — silence, pre-ticked boxes, "
        "and inactivity do not constitute consent). Art.7 also requires: "
        "that consent can be demonstrated (records of when and how consent "
        "was given); that consent requests are clearly separate from other "
        "terms; and that withdrawal is as easy as giving consent. Where "
        "consent relies on a contract, the European Data Protection Board "
        "(EDPB) has confirmed that conditional consent — 'consent or we "
        "cannot provide the service' — may not be freely given unless the "
        "processing is genuinely necessary for the service."
    ),
    "query_keywords": {
        "exact": [
            "conditions for consent",
            "freely given specific informed and unambiguous",
            "demonstrate that the data subject has consented",
            "withdraw consent at any time",
        ],
        "practitioner": [
            "valid consent GDPR",
            "consent requirements",
            "GDPR consent",
            "freely given consent",
            "consent records",
            "consent management",
            "withdrawal of consent",
            "consent mechanism",
            "cookie consent",
            "user consent",
            "consent to collect data",
            "consent for data collection",
            "obtain consent",
            "getting consent",
            "consent from users",
        ],
        "scenario": [
            "is our consent mechanism valid",
            "do we have valid consent for marketing",
            "pre-ticked consent boxes",
            "consent bundled with terms and conditions",
            "proving consent was given",
        ],
        "confusion": [
            "Art.6.1.a", # consent as lawful basis — Art.7 sets the conditions
                         # for that basis; valid consent under Art.7 is
                         # required for Art.6.1.a to apply
            "Art.9",     # explicit consent for special category data — a
                         # higher standard than Art.7 consent
        ],
    },
},

"Art.7.1": {
    "business_description": (
        "The controller bears the burden of proof for consent — if challenged, "
        "the organisation must be able to demonstrate that consent was given. "
        "This requires maintaining consent records showing: who gave consent, "
        "when it was given, what they were told, what they consented to, and "
        "the mechanism used. Consent management platforms typically provide "
        "this audit trail. Consent that cannot be demonstrated is treated as "
        "if it was never given — the General Data Protection Regulation (GDPR) "
        "does not allow organisations to rely on verbal consent or consent "
        "that was not recorded. Retroactive consent — obtaining records of "
        "consent claimed to have been given in the past without evidence — "
        "is not valid."
    ),
    "query_keywords": {
        "exact": [
            "demonstrate that the data subject has consented",
        ],
        "practitioner": [
            "consent records",
            "prove consent",
            "consent audit trail",
            "consent management platform",
            "CMP",
            "consent evidence",
            "documenting consent",
        ],
        "scenario": [
            "we cannot prove consent was given",
            "consent records missing",
            "how to record consent",
            "consent management system",
        ],
        "confusion": [],
    },
},

"Art.7.3": {
    "business_description": (
        "Data subjects may withdraw consent at any time and the mechanism "
        "for withdrawal must be as easy as the mechanism for giving consent. "
        "If consent was given by clicking a button, withdrawal must also be "
        "by clicking a button — not by sending a letter or calling a helpline. "
        "Withdrawal does not affect the lawfulness of processing that took "
        "place before withdrawal — a controller is not required to delete "
        "historic data processed under valid consent that has since been "
        "withdrawn, though Art.17 (right to erasure) may apply separately. "
        "Controllers must inform data subjects of their right to withdraw "
        "before they give consent. The European Data Protection Board (EDPB) "
        "has enforced this obligation against organisations whose withdrawal "
        "process was significantly more burdensome than the consent process."
    ),
    "query_keywords": {
        "exact": [
            "withdraw consent at any time",
            "as easy to withdraw consent as to give it",
            "withdrawal of consent shall not affect the lawfulness",
        ],
        "practitioner": [
            "consent withdrawal",
            "right to withdraw consent",
            "unsubscribe",
            "opt out",
            "revoke consent",
            "easy withdrawal of consent",
            "consent withdrawal mechanism",
        ],
        "scenario": [
            "customer wants to withdraw consent",
            "unsubscribe process",
            "how to implement consent withdrawal",
            "withdrawal harder than giving consent",
        ],
        "confusion": [
            "Art.17",    # right to erasure — withdrawal of consent may
                         # trigger Art.17 but they are separate rights
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.35 — Data Protection Impact Assessment
# ═══════════════════════════════════════════════════════════════════════════

"Art.35": {
    "business_description": (
        "A Data Protection Impact Assessment (DPIA) is required before "
        "commencing processing that is likely to result in high risk to "
        "individuals' rights and freedoms. The key word is 'before' — a "
        "DPIA conducted after processing has begun does not satisfy "
        "Art.35. The European Data Protection Board (EDPB) Guidelines "
        "9/2020 identify nine processing characteristics that trigger a "
        "mandatory DPIA: evaluation or scoring; automated decision-making "
        "with legal or significant effects; systematic monitoring; sensitive "
        "data or data of a highly personal nature; data processed on a "
        "large scale; matching or combining datasets; data concerning "
        "vulnerable data subjects; innovative use of technology; and "
        "transfer of data across borders with inadequate protections. "
        "Two or more of these characteristics meeting simultaneously "
        "creates a strong presumption that a DPIA is required. "
        "Supervisory authorities publish lists of processing operations "
        "that always require a DPIA and operations that never do."
    ),
    "query_keywords": {
        "exact": [
            "data protection impact assessment",
            "DPIA",
            "prior to the processing",
            "likely to result in a high risk",
            "systematic and extensive evaluation",
            "systematic monitoring",
            "large scale",
        ],
        "practitioner": [
            "DPIA",
            "data protection impact assessment",
            "do we need a DPIA",
            "when is a DPIA required",
            "high risk processing",
            "privacy impact assessment",
            "PIA",
            "DPIA triggers",
        ],
        "scenario": [
            "new processing activity",
            "profiling customers",
            "monitoring employees",
            "processing health data at scale",
            "new AI system processing personal data",
            "facial recognition",
            "CCTV with analytics",
        ],
        "confusion": [
            "Art.36",    # prior consultation — required AFTER a DPIA
                         # identifies unmitigable high residual risk
            "Art.32",    # security of processing — distinct from DPIA;
                         # a DPIA assesses processing risk before commencing,
                         # Art.32 requires ongoing security measures
        ],
    },
},

"Art.35.1": {
    "business_description": (
        "The Data Protection Impact Assessment (DPIA) obligation is triggered when a type of processing — "
        "particularly using new technologies — is likely to result in "
        "high risk. ArionComply advises treating any of the following as "
        "triggers requiring at minimum a DPIA screening: use of artificial "
        "intelligence or machine learning on personal data; large-scale "
        "processing of special category data; systematic monitoring of "
        "individuals in publicly accessible areas; processing that involves "
        "automated decision-making with legal or significant effects; "
        "and processing of children's data at scale. The DPIA must be "
        "conducted by the controller and the Data Protection Officer (DPO) "
        "must be consulted where one is designated. The assessment must "
        "be completed and the residual risk accepted by senior management "
        "before processing commences. If the DPIA identifies a high "
        "residual risk that cannot be mitigated, the controller must "
        "consult the supervisory authority under Art.36 before proceeding."
    ),
    "query_keywords": {
        "exact": [
            "using new technologies",
            "prior to the processing carry out an assessment",
        ],
        "practitioner": [
            "when to do a DPIA",
            "DPIA requirement",
            "new technology DPIA",
            "AI GDPR DPIA",
            "machine learning DPIA",
            "DPIA before launch",
            "DPIA screening",
        ],
        "scenario": [
            "implementing AI that uses personal data",
            "building an automated decision system",
            "new product with personal data",
            "pilot processing activity",
        ],
        "confusion": [
            "Art.35.3",  # the three mandatory DPIA categories — Art.35.1
                         # is the general trigger; Art.35.3 lists cases
                         # where a DPIA is always required
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.37 — Designation of the Data Protection Officer
# ═══════════════════════════════════════════════════════════════════════════

"Art.37": {
    "business_description": (
        "Controllers and processors must designate a Data Protection Officer "
        "(DPO) in three mandatory circumstances: (a) where processing is "
        "carried out by a public authority; (b) where the core activities "
        "require regular and systematic monitoring of data subjects on a "
        "large scale; or (c) where the core activities consist of large-scale "
        "processing of special category data or criminal conviction data. "
        "Outside these mandatory cases, organisations may voluntarily "
        "designate a DPO — and many do for accountability and governance "
        "purposes. A DPO can be an employee or an external service provider. "
        "The DPO's contact details must be published and communicated to "
        "the supervisory authority. The General Data Protection Regulation "
        "(GDPR) does not prescribe specific qualifications but requires "
        "'expert knowledge of data protection law and practices.' Once "
        "designated, a DPO cannot be dismissed or penalised for performing "
        "their tasks — this independence is a key protection."
    ),
    "query_keywords": {
        "exact": [
            "designation of the data protection officer",
            "regular and systematic monitoring of data subjects on a large scale",
            "large scale of special categories of data",
            "expert knowledge of data protection law",
        ],
        "practitioner": [
            "DPO",
            "data protection officer",
            "do we need a DPO",
            "DPO requirement",
            "when is a DPO required",
            "mandatory DPO",
            "DPO appointment",
            "outsourced DPO",
            "DPO as a service",
        ],
        "scenario": [
            "do we need to appoint a DPO",
            "our organisation processes a lot of personal data",
            "we monitor users systematically",
            "we process health data at scale",
            "appointing an external DPO",
        ],
        "confusion": [
            "Art.38",    # position of the DPO — independence, resources,
                         # reporting line — distinct from the designation
                         # requirement in Art.37
            "Art.39",    # tasks of the DPO — what the DPO does;
                         # Art.37 is who must be appointed
        ],
    },
},

"Art.37.1": {
    "business_description": (
        "The three mandatory Data Protection Officer (DPO) triggers each require interpretation. "
        "'Core activities' means the primary business activities, not "
        "support functions — HR data processing by a manufacturing company "
        "does not make data processing a core activity. 'Large scale' is "
        "not defined in the General Data Protection Regulation (GDPR); the "
        "European Data Protection Board (EDPB) considers factors including "
        "the number of data subjects, the volume of data, the geographical "
        "scope, and the duration of processing. 'Regular and systematic "
        "monitoring' includes behavioural advertising, location tracking, "
        "loyalty programmes, CCTV, and employee monitoring. Special "
        "category data triggers include healthcare providers, insurers, "
        "and any organisation processing health, biometric, or other "
        "Art.9 data at scale. ArionComply advises conducting a documented "
        "DPO necessity assessment and retaining it as accountability "
        "evidence even where the conclusion is that a DPO is not required."
    ),
    "query_keywords": {
        "exact": [
            "core activities",
            "regular and systematic monitoring",
            "large scale of special categories",
        ],
        "practitioner": [
            "core activities DPO",
            "large scale processing",
            "systematic monitoring DPO",
            "DPO necessity assessment",
            "do our activities trigger DPO requirement",
        ],
        "scenario": [
            "are we large scale enough for a DPO",
            "does our monitoring require a DPO",
            "technology company DPO requirement",
            "SaaS provider DPO obligation",
        ],
        "confusion": [
            "Art.37",    # the parent article — Art.37.1 is the specific
                         # three-trigger paragraph
        ],
    },
},

}  # end TIER1_ENRICHMENT

CLUSTER_METADATA = {
    "cluster":       "GDPR Principles, Lawful Basis, Consent, DPIA, DPO",
    "articles":      ["Art.5", "Art.5.1", "Art.5.1.a", "Art.5.1.b", "Art.5.1.c",
                      "Art.5.1.d", "Art.5.1.e", "Art.5.1.f", "Art.5.2",
                      "Art.6", "Art.6.1", "Art.7", "Art.7.1", "Art.7.3",
                      "Art.35", "Art.35.1", "Art.37", "Art.37.1"],
    "primary_source": "GDPR 2016/679 Art.5-7, 35, 37",
    "secondary_sources": [
        "EDPB Guidelines 05/2020 on consent",
        "EDPB Guidelines 3/2022 on deceptive design patterns",
        "EDPB Guidelines 9/2020 on DPIA triggers",
        "EDPB Guidelines 04/2017 on DPO designation",
        "ICO guidance on lawful bases for processing",
        "ICO guidance on DPIAs",
        "Recitals 32, 33, 37-50, 89-96, 97",
    ],
    "authored_by":   "ArionComply Tier 1 — manual authoring",
    "review_status": "PENDING_REVIEW",
    "review_notes":  "",
}
