"""
Tier 1 Enrichment — GDPR Breach Notification (Art.33–34 cluster)

Sources:
  - GDPR Art.33–34 verbatim text
  - EDPB Guidelines 9/2022 on personal data breach notification
  - EDPB Guidelines 01/2021 on data breach notification examples
  - ICO: Reporting a data breach (ico.org.uk)
  - WP29 Guidelines on Personal data breach notification (WP250)
  - Recitals 85-88 (breach notification rationale)
  - Art.4(12) definition of personal data breach

This cluster has the highest misconception density of any Tier 1 group.
Common misconceptions addressed in business descriptions:
  - 72 hours runs from AWARENESS not from occurrence of the breach
  - Art.34 (subject notification) is SEPARATE from Art.33 (authority notification)
  - Encrypted data reduces the Art.34 obligation but NOT Art.33
  - Processor must notify CONTROLLER, not the supervisory authority directly
  - "Unlikely to result in a risk" exemption is narrow — default is to notify
  - Art.33.5 documentation obligation applies even to NON-notified breaches
  - Art.33.3 notification content can be provided in phases

REVIEW CHECKLIST:
  □ Does the 72-hour clock start correctly (awareness, not occurrence)?
  □ Is the Art.33 vs Art.34 threshold distinction accurate?
  □ Is the encryption exemption scoped correctly (Art.34 only, not Art.33)?
  □ Is the processor notification chain correct (processor→controller only)?
  □ Are the Art.33.5 documentation obligations correctly scoped?
"""

TIER1_ENRICHMENT = {

# ═══════════════════════════════════════════════════════════════════════════
# Art.33 — Notification to supervisory authority (article level)
# ═══════════════════════════════════════════════════════════════════════════

"Art.33": {
    "business_description": (
        "When an organisation suffers a personal data breach, it must notify "
        "its supervisory authority (e.g. Information Commissioner's Office (ICO) in the UK, Data Protection Commission (DPC) in Ireland) "
        "within 72 hours of becoming aware of the breach — unless the breach "
        "is unlikely to result in any risk to individuals' rights and freedoms. "
        "This exemption is narrow: the the European Data Protection Board (EDPB) position is that controllers "
        "should default to notifying and apply the exemption only where the "
        "absence of risk is clear and documented. The notification obligation "
        "sits with the controller; processors must notify their controller "
        "without undue delay, not the supervisory authority directly. "
        "If 72 hours cannot be met, the notification should still be submitted "
        "as soon as possible with an explanation of the delay. Importantly, "
        "Art.33 applies regardless of whether data subjects are also notified "
        "— that is a separate obligation under Art.34 with a different threshold."
    ),
    "query_keywords": {
        "exact": [
            "notification of a personal data breach",
            "notify the supervisory authority",
            "72 hours",
            "without undue delay",
            "unlikely to result in a risk",
        ],
        "practitioner": [
            "report a breach",
            "breach notification",
            "notify the ICO",
            "notify the DPA",
            "report to regulator",
            "breach reporting",
            "data breach report",
            "ICO breach notification",
            "72 hour rule",
            "72 hour deadline",
            "when to report a breach",
            "do we need to report this breach",
            "mandatory breach reporting",
            "breach report deadline",
        ],
        "scenario": [
            "ransomware attack personal data",
            "accidental email disclosure",
            "lost laptop with personal data",
            "database breach",
            "unauthorised access to personal data",
            "data leaked online",
            "phishing attack resulting in data access",
            "employee accidentally sent data to wrong person",
            "data stolen",
        ],
        "confusion": [
            "Art.34",           # Art.34 is data subject notification — different
                                # threshold and different action
            "Art.32",           # security measures to prevent breach — distinct
                                # from notification after breach occurs
            "voluntary breach notification",  # Art.33 is mandatory, not voluntary
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.33.1 — The 72-hour obligation on controllers
# ═══════════════════════════════════════════════════════════════════════════

"Art.33.1": {
    "business_description": (
        "The 72-hour clock starts when the controller 'becomes aware' of the "
        "breach — not when the breach occurred. A breach that happened three "
        "weeks ago but was discovered today starts its 72-hour window today. "
        "However, 'becoming aware' requires a reasonable degree of certainty "
        "that a breach has occurred — a suspicion alone does not start the "
        "clock, but a controller cannot delay investigation to avoid the "
        "72-hour deadline. The European Data Protection Board (EDPB) position is that the clock starts when "
        "the controller has reasonable certainty of a breach, even if the "
        "full scope is unknown. Notification can be submitted in phases: an "
        "initial notification within 72 hours with what is known, followed "
        "by updates as further information is established. The exemption — "
        "'unlikely to result in a risk' — is interpreted narrowly. Encrypted "
        "data with no key exposure, or data already publicly available, may "
        "qualify. The controller must document its reasoning if relying on "
        "the exemption. Failure to notify within 72 hours is one of the "
        "most frequently enforced General Data Protection Regulation (GDPR) violations and attracts fines up to "
        "€10M or 2% of global turnover under Art.83(4)."
    ),
    "query_keywords": {
        "exact": [
            "not later than 72 hours",
            "after having become aware",
            "unlikely to result in a risk to the rights and freedoms",
            "without undue delay",
        ],
        "practitioner": [
            "72 hour breach deadline",
            "when does the 72 hours start",
            "72 hours from discovery",
            "72 hours from awareness",
            "breach notification window",
            "missed 72 hour deadline",
            "late breach notification",
            "phased breach notification",
            "initial breach report",
            "follow up breach notification",
            "when are we aware of a breach",
        ],
        "scenario": [
            "discovered a breach that happened weeks ago",
            "not sure if it is a breach yet",
            "how long do we have to report",
            "can we investigate before reporting",
            "partial information at time of notification",
            "breach discovered over weekend",
            "breach notification outside business hours",
        ],
        "confusion": [
            "72 hours from breach occurrence",  # WRONG — it is from awareness
            "Art.33.2",     # processor notification to controller — separate
                            # obligation, no 72-hour clock applies
            "Art.34.1",     # subject notification — different threshold
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.33.2 — Processor notification to controller
# ═══════════════════════════════════════════════════════════════════════════

"Art.33.2": {
    "business_description": (
        "When a processor (a supplier, cloud provider, or third party "
        "processing data on behalf of the controller) becomes aware of a "
        "personal data breach, it must notify the controller without undue "
        "delay. The processor does NOT notify the supervisory authority — "
        "that remains the controller's obligation. The processor's "
        "notification to the controller effectively starts the controller's "
        "72-hour clock. The phrase 'without undue delay' is not a fixed "
        "period but European Data Protection Board (EDPB) guidance indicates that processors should aim to "
        "notify within 24-36 hours to give the controller enough time to "
        "meet its own 72-hour deadline. The Data Processing Agreement (DPA) "
        "under Art.28 should specify the breach notification procedure "
        "between processor and controller — including what information the "
        "processor must provide and within what timeframe. Processors who "
        "fail to notify controllers promptly can be held jointly liable."
    ),
    "query_keywords": {
        "exact": [
            "processor shall notify the controller",
            "without undue delay",
            "becoming aware of a personal data breach",
        ],
        "practitioner": [
            "supplier breach notification",
            "third party data breach",
            "processor data breach",
            "cloud provider breach",
            "vendor breach notification",
            "subprocessor breach",
            "processor to controller notification",
            "processor breach reporting obligation",
            "DPA breach notification clause",
            "what must our processor tell us about a breach",
        ],
        "scenario": [
            "our cloud provider had a breach",
            "our payroll provider was hacked",
            "third party processor suffered a breach",
            "supplier notified us of a breach",
            "processor did not notify us of breach in time",
        ],
        "confusion": [
            "processor notifies supervisory authority",  # WRONG — processor
                                                        # notifies controller only
            "Art.33.1",     # controller's 72-hour obligation — Art.33.2 is
                            # the processor's obligation to notify the controller
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.33.3 — Content of the breach notification
# ═══════════════════════════════════════════════════════════════════════════

"Art.33.3": {
    "business_description": (
        "A complete breach notification to the supervisory authority must "
        "contain four categories of information: (a) the nature of the breach "
        "including the categories and approximate number of data subjects and "
        "records affected; (b) the name and contact details of the Data Protection Officer (DPO) or "
        "other contact point; (c) the likely consequences of the breach; "
        "and (d) the measures taken or proposed to address the breach and "
        "mitigate its effects. Where this information is not all available "
        "within 72 hours, Art.33.4 allows it to be provided in phases — "
        "the initial notification can contain what is known, with follow-up "
        "communications as further details are established. Supervisory "
        "authorities (including the Information Commissioner's Office (ICO)) provide online notification portals "
        "with forms structured around these four content requirements. "
        "Notifications that omit any of these elements are incomplete and "
        "may result in regulatory follow-up."
    ),
    "query_keywords": {
        "exact": [
            "nature of the personal data breach",
            "categories and approximate number of data subjects",
            "name and contact details of the data protection officer",
            "likely consequences of the personal data breach",
            "measures taken or proposed to be taken",
        ],
        "practitioner": [
            "what to include in breach notification",
            "breach notification content",
            "breach report content",
            "what information to provide to ICO",
            "breach notification form",
            "ICO breach notification form",
            "what does a breach notification need to say",
            "breach notification template",
            "phased breach notification",
            "follow up breach notification",
        ],
        "scenario": [
            "drafting a breach notification to ICO",
            "what do we tell the regulator about the breach",
            "we do not know the full extent of the breach yet",
            "breach notification with incomplete information",
        ],
        "confusion": [
            "Art.34.2",     # content of data subject notification — similar
                            # structure but different content requirements
            "Art.33.5",     # internal documentation obligation — separate
                            # from the notification to supervisory authority
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.33.5 — Internal breach documentation obligation
# ═══════════════════════════════════════════════════════════════════════════

"Art.33.5": {
    "business_description": (
        "Every personal data breach must be documented internally — including "
        "breaches that do not meet the threshold for supervisory authority "
        "notification. This is one of the most underappreciated obligations "
        "in the breach notification framework. A controller cannot simply "
        "decide a breach is low-risk and move on; it must record the breach "
        "in a breach register, document the facts, its effects, and the "
        "remedial action taken, and record its reasoning for any decision "
        "not to notify the supervisory authority or data subjects. This "
        "breach register must be available to the supervisory authority on "
        "request. In practice, controllers should maintain a breach log that "
        "captures: date of discovery, date of occurrence (if known), "
        "nature of breach, data categories and volume affected, cause, "
        "impact assessment, whether Art.33 notification was made (and why "
        "or why not), whether Art.34 notification was made (and why or why "
        "not), and remedial actions. Absence of a breach register is itself "
        "a compliance gap even if no notifiable breaches have occurred."
    ),
    "query_keywords": {
        "exact": [
            "document any personal data breaches",
            "facts relating to the personal data breach",
            "effects and the remedial action taken",
        ],
        "practitioner": [
            "breach register",
            "breach log",
            "breach record",
            "data breach register",
            "breach documentation",
            "record of breaches",
            "internal breach records",
            "breach log template",
            "do we need to record non-notified breaches",
            "breach register GDPR",
        ],
        "scenario": [
            "setting up a breach register",
            "we had a minor breach do we need to record it",
            "breach below notification threshold still needs recording",
            "auditor asked to see breach register",
            "ICO requested breach records",
        ],
        "confusion": [
            "Art.33.1",     # notification to supervisory authority — Art.33.5
                            # applies even when Art.33.1 notification is NOT made
            "Art.30",       # RoPA — record of processing activities, different
                            # from breach register
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.34 — Communication of breach to data subjects
# ═══════════════════════════════════════════════════════════════════════════

"Art.34": {
    "business_description": (
        "Art.34 is the obligation to tell the affected individuals about a "
        "breach — separate from the obligation to tell the supervisory "
        "authority under Art.33. The threshold is higher: the breach must "
        "be 'likely to result in a high risk to the rights and freedoms' of "
        "individuals. Not all breaches that trigger Art.33 notification also "
        "trigger Art.34. A breach that is reported to the Information Commissioner's Office (ICO) because it "
        "might result in risk does not automatically need to be communicated "
        "to data subjects unless that risk is 'high'. There are three "
        "exemptions from the Art.34 obligation even when a high risk exists: "
        "(a) the data was encrypted or otherwise protected making it "
        "unintelligible; (b) the controller took subsequent measures "
        "eliminating the high risk; or (c) individual notification would "
        "involve disproportionate effort — in which case a public "
        "communication must be used instead. Supervisory authorities can "
        "require controllers to notify data subjects if they have not done so."
    ),
    "query_keywords": {
        "exact": [
            "communication of a personal data breach to the data subject",
            "high risk to the rights and freedoms",
            "communicate the personal data breach to the data subject",
        ],
        "practitioner": [
            "notify customers of breach",
            "tell customers about data breach",
            "data subject breach notification",
            "individual breach notification",
            "customer breach letter",
            "do we need to tell individuals",
            "breach notification to affected persons",
            "high risk breach",
            "when to notify individuals of breach",
        ],
        "scenario": [
            "breach affecting customer personal data",
            "should we tell our customers about the breach",
            "breach involving financial data",
            "breach involving health data",
            "sensitive data exposed in breach",
            "do we need to contact affected individuals",
        ],
        "confusion": [
            "Art.33",       # authority notification — Art.34 is subject
                            # notification with higher threshold
            "Art.33.1",     # 72-hour clock — does not apply to Art.34
            "Art.12",       # transparency and modalities for communication
                            # with data subjects generally
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.34.1 — The high-risk threshold for subject notification
# ═══════════════════════════════════════════════════════════════════════════

"Art.34.1": {
    "business_description": (
        "The trigger for notifying data subjects is 'high risk' — a higher "
        "bar than the 'risk' threshold that triggers supervisory authority "
        "notification under Art.33.1. High risk typically involves breaches "
        "where individuals could suffer: financial loss, identity theft, "
        "discrimination, reputational damage, or significant social or "
        "economic disadvantage. The European Data Protection Board (EDPB) provides examples: exposure of "
        "financial account credentials, medical records, special category "
        "data, or data enabling identity theft. The assessment is specific "
        "to the individuals affected — a breach of encrypted data presents "
        "lower risk than unencrypted data. ArionComply advises treating "
        "any breach involving special category data, financial credentials, "
        "authentication data, or data enabling direct harm to individuals "
        "as presumptively high-risk pending a documented risk assessment. "
        "The notification must be made 'without undue delay' — there is no "
        "fixed period but the EDPB expects prompt notification once a high "
        "risk determination is made."
    ),
    "query_keywords": {
        "exact": [
            "likely to result in a high risk",
            "high risk to the rights and freedoms of natural persons",
            "without undue delay",
        ],
        "practitioner": [
            "high risk breach",
            "what is high risk for breach notification",
            "when is a breach high risk",
            "breach risk assessment",
            "do we need to notify individuals",
            "severity of breach",
            "breach impact assessment",
        ],
        "scenario": [
            "special category data breached",
            "financial data exposed",
            "passwords leaked",
            "medical records breached",
            "identity theft risk from breach",
            "breach involving vulnerable individuals",
        ],
        "confusion": [
            "Art.33.1",     # 'risk' threshold — lower bar than 'high risk'
                            # in Art.34.1
            "Art.35.1",     # DPIA high risk — different assessment, before
                            # processing not after breach
        ],
    },
},

# ═══════════════════════════════════════════════════════════════════════════
# Art.34.3 — Exemptions from subject notification
# ═══════════════════════════════════════════════════════════════════════════

"Art.34.3": {
    "business_description": (
        "Three circumstances exempt a controller from the Art.34.1 obligation "
        "to notify data subjects even where a high risk exists. First, where "
        "the controller implemented appropriate protection measures — "
        "specifically encryption or other measures rendering the data "
        "unintelligible to anyone not authorised to access it. This is the "
        "primary practical exemption: if breached data was properly encrypted "
        "and the keys were not compromised, subject notification may not be "
        "required. Second, where the controller took subsequent measures "
        "that ensure the high risk is no longer likely to materialise — for "
        "example, remotely wiping a stolen device. Third, where individual "
        "notification would involve disproportionate effort — but this does "
        "not eliminate the obligation; a public communication must be made "
        "instead. Important: these exemptions apply only to Art.34 subject "
        "notification — they do not affect the Art.33 obligation to notify "
        "the supervisory authority. A controller can be required by the "
        "supervisory authority to notify data subjects even if the controller "
        "believes an exemption applies."
    ),
    "query_keywords": {
        "exact": [
            "render it unintelligible",
            "subsequent measures",
            "disproportionate effort",
            "public communication",
        ],
        "practitioner": [
            "encrypted data breach exemption",
            "encryption exemption breach notification",
            "do we need to tell individuals if data was encrypted",
            "breach notification exemption",
            "encrypted breach no notification",
            "public communication instead of individual notification",
            "mass breach disproportionate effort",
        ],
        "scenario": [
            "breached data was encrypted",
            "stolen laptop was encrypted",
            "too many individuals to notify individually",
            "can we use a press release instead of individual notification",
            "we remotely wiped the stolen device",
        ],
        "confusion": [
            "encryption exemption for Art.33",  # WRONG — encryption reduces
                                                # Art.34 obligation, NOT Art.33
            "Art.33.1",     # supervisory authority notification — encryption
                            # does not exempt from this obligation
        ],
    },
},

}  # end TIER1_ENRICHMENT


# ── Metadata ──────────────────────────────────────────────────────────────────

CLUSTER_METADATA = {
    "cluster":        "GDPR Breach Notification",
    "articles":       ["Art.33", "Art.33.1", "Art.33.2", "Art.33.3",
                       "Art.33.5", "Art.34", "Art.34.1", "Art.34.3"],
    "primary_source": "GDPR 2016/679 Art.33–34 verbatim text",
    "secondary_sources": [
        "EDPB Guidelines 9/2022 on personal data breach notification",
        "EDPB Guidelines 01/2021 on data breach notification examples",
        "ICO: Reporting a data breach (ico.org.uk)",
        "WP29 Guidelines on Personal data breach notification (WP250rev.01)",
        "GDPR Art.4(12) definition of personal data breach",
        "Recitals 85-88",
    ],
    "authored_by":    "ArionComply Tier 1 — manual authoring",
    "review_status":  "PENDING_REVIEW",
    "review_notes":   "",
    "key_positions": {
        "72_hour_clock":     "Starts from AWARENESS, not from breach occurrence",
        "encryption":        "Reduces Art.34 (subject) obligation. Does NOT affect Art.33 (authority) obligation.",
        "processor_chain":   "Processor notifies CONTROLLER only. Controller notifies supervisory authority.",
        "exemption_scope":   "Art.33 exemption ('unlikely to result in risk') is narrow — default is to notify",
        "documentation":     "Art.33.5 documentation applies to ALL breaches, including non-notified ones",
        "threshold_diff":    "Art.33 = 'risk'. Art.34 = 'HIGH risk'. Different bars, different obligations.",
    },
}
