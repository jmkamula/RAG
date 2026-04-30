"""
ArionComply — Obligation Rules

Maps ClientFacts to mandatory control node_ids.
Each rule says: IF these facts are true THEN these controls are legally required.

Rules are deterministic — not probabilistic retrieval.
A control in mandatory_controls cannot be missed by vector search scoring.

Source: ISO 27001:2022 and GDPR 2016/679 explicit conditions.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from enrichment.obligations.client_facts import ClientFacts


@dataclass
class ObligationRule:
    id:                  str
    description:         str
    rationale:           str           # why these controls are required
    condition:           Callable[[ClientFacts], bool]
    mandatory_controls:  list[str]     # node_ids: "STANDARD:VERSION:REF"
    trigger_type:        str           # "profile_fact" | "universal"


# ── Universal rules — apply to every client in scope ──────────────────────────

RULE_ISO_UNIVERSAL = ObligationRule(
    id          = "iso_universal",
    description = "ISO 27001 universal requirements",
    rationale   = "Every ISO 27001 organisation must have these regardless of profile",
    condition   = lambda f: f.iso_in_scope,
    trigger_type= "universal",
    mandatory_controls = [
        "ISO27001:2022:4",       # context of the organisation
        "ISO27001:2022:4.1",     # understanding the organisation
        "ISO27001:2022:4.2",     # understanding interested parties
        "ISO27001:2022:4.3",     # scope of the ISMS
        "ISO27001:2022:5.1",     # leadership and commitment
        "ISO27001:2022:5.2",     # policy
        "ISO27001:2022:6.1.2",   # risk assessment
        "ISO27001:2022:6.1.3",   # risk treatment
        "ISO27001:2022:9.2",     # internal audit
        "ISO27001:2022:9.3",     # management review
        "ISO27001:2022:10.1",    # continual improvement
        "ISO27001:2022:10.2",    # nonconformity and corrective action
    ],
)

RULE_GDPR_UNIVERSAL = ObligationRule(
    id          = "gdpr_universal",
    description = "GDPR universal requirements for controllers",
    rationale   = "Every organisation processing EU personal data must meet these",
    condition   = lambda f: f.gdpr_in_scope and f.role_controller,
    trigger_type= "universal",
    mandatory_controls = [
        "GDPR:2016/679:Art.5",    # principles
        "GDPR:2016/679:Art.5.1",  # lawfulness, fairness, transparency
        "GDPR:2016/679:Art.6",    # lawful basis
        "GDPR:2016/679:Art.24",   # controller responsibility
        "GDPR:2016/679:Art.25",   # data protection by design
        "GDPR:2016/679:Art.32",   # security of processing
    ],
)

# ── Transparency obligations ───────────────────────────────────────────────────

RULE_PRIVACY_NOTICES = ObligationRule(
    id          = "privacy_notices",
    description = "Privacy notice obligations for controllers",
    rationale   = "Controllers must provide privacy notices at or before data collection",
    condition   = lambda f: f.role_controller and f.gdpr_in_scope,
    trigger_type= "profile_fact",
    mandatory_controls = [
        "GDPR:2016/679:Art.13",    # privacy notice — data collected directly
        "GDPR:2016/679:Art.14",    # privacy notice — data from third parties
    ],
)

# ── Processor relationships ────────────────────────────────────────────────────

RULE_USES_PROCESSORS = ObligationRule(
    id          = "uses_processors",
    description = "Controller uses third party processors",
    rationale   = "Written DPA mandatory for every processor under Art.28.3",
    condition   = lambda f: f.role_controller and f.uses_processors,
    trigger_type= "profile_fact",
    mandatory_controls = [
        "GDPR:2016/679:Art.28",      # processor requirements
        "GDPR:2016/679:Art.28.3",    # mandatory DPA clauses
        "ISO27001:2022:A.5.19",      # information security in supplier relationships
        "ISO27001:2022:A.5.20",      # addressing security in supplier agreements
        "ISO27001:2022:A.5.21",      # managing ICT supply chain
        "ISO27001:2022:A.5.22",      # supplier service delivery management
    ],
)

RULE_USES_CLOUD = ObligationRule(
    id          = "uses_cloud_services",
    description = "Organisation uses cloud services to process personal data",
    rationale   = "Cloud providers are processors — Art.28 DPA mandatory. A.5.23 is the ISO control.",
    condition   = lambda f: f.uses_cloud_services and f.processes_personal_data,
    trigger_type= "profile_fact",
    mandatory_controls = [
        "GDPR:2016/679:Art.28",      # cloud provider is processor
        "GDPR:2016/679:Art.28.3",    # DPA mandatory clauses
        "GDPR:2016/679:Art.32",      # security measures cover cloud
        "ISO27001:2022:A.5.23",      # information security for cloud services
        "ISO27001:2022:A.5.22",      # supplier service delivery
    ],
)

RULE_IS_PROCESSOR = ObligationRule(
    id          = "is_processor",
    description = "Organisation acts as processor for other controllers",
    rationale   = "Processors have specific obligations under Art.28, 29 and 32",
    condition   = lambda f: f.role_processor,
    trigger_type= "profile_fact",
    mandatory_controls = [
        "GDPR:2016/679:Art.28",      # processor obligations
        "GDPR:2016/679:Art.29",      # processing under controller authority
        "GDPR:2016/679:Art.32",      # security measures
    ],
)

RULE_JOINT_CONTROLLERS = ObligationRule(
    id          = "joint_controllers",
    description = "Joint controller arrangement",
    rationale   = "Joint controllers must have written arrangement determining responsibilities",
    condition   = lambda f: f.role_joint_controller,
    trigger_type= "profile_fact",
    mandatory_controls = [
        "GDPR:2016/679:Art.26",      # joint controller arrangement
    ],
)

# ── Special data types ─────────────────────────────────────────────────────────

RULE_SPECIAL_CATEGORY = ObligationRule(
    id          = "special_category_data",
    description = "Processing special category personal data",
    rationale   = "Art.9 requires explicit legal basis for health, biometric, genetic data etc.",
    condition   = lambda f: f.special_category_data and f.gdpr_in_scope,
    trigger_type= "profile_fact",
    mandatory_controls = [
        "GDPR:2016/679:Art.9",       # conditions for processing
        "GDPR:2016/679:Art.9.2",     # explicit consent or Art.9.2 basis
    ],
)

RULE_CRIMINAL_DATA = ObligationRule(
    id          = "criminal_conviction_data",
    description = "Processing criminal conviction and offences data",
    rationale   = "Art.10 restricts processing of criminal conviction data",
    condition   = lambda f: f.criminal_conviction_data and f.gdpr_in_scope,
    trigger_type= "profile_fact",
    mandatory_controls = [
        "GDPR:2016/679:Art.10",      # criminal convictions data
    ],
)

RULE_CHILDRENS_DATA = ObligationRule(
    id          = "childrens_data",
    description = "Processing children's personal data",
    rationale   = "Art.8 requires parental consent for under-16s for online services",
    condition   = lambda f: f.childrens_data and f.gdpr_in_scope,
    trigger_type= "profile_fact",
    mandatory_controls = [
        "GDPR:2016/679:Art.8",       # conditions for child's consent
    ],
)

# ── Automated decision making ──────────────────────────────────────────────────

RULE_AUTOMATED_DECISIONS = ObligationRule(
    id          = "automated_decision_making",
    description = "Automated individual decision-making or profiling",
    rationale   = "Art.22 gives data subjects right to object to automated decisions",
    condition   = lambda f: (f.automated_decision_making or f.profiling) and f.gdpr_in_scope,
    trigger_type= "profile_fact",
    mandatory_controls = [
        "GDPR:2016/679:Art.22",      # automated decision-making
    ],
)

# ── DPO requirement ────────────────────────────────────────────────────────────

RULE_DPO_REQUIRED = ObligationRule(
    id          = "dpo_required",
    description = "Data Protection Officer appointment required",
    rationale   = "Art.37 requires DPO for public authorities and large-scale/systematic processing",
    condition   = lambda f: f.dpo_required and f.gdpr_in_scope,
    trigger_type= "profile_fact",
    mandatory_controls = [
        "GDPR:2016/679:Art.37",      # designation of DPO
        "GDPR:2016/679:Art.38",      # position of DPO
        "GDPR:2016/679:Art.39",      # tasks of DPO
    ],
)

# ── Records of processing ──────────────────────────────────────────────────────

RULE_RECORDS_REQUIRED = ObligationRule(
    id          = "records_of_processing",
    description = "Records of processing activities mandatory",
    rationale   = "Art.30 records mandatory for 250+ employees, high risk or special category",
    condition   = lambda f: f.records_required and f.gdpr_in_scope,
    trigger_type= "profile_fact",
    mandatory_controls = [
        "GDPR:2016/679:Art.30",      # records of processing activities
    ],
)

# ── DPIA ──────────────────────────────────────────────────────────────────────

RULE_DPIA_REQUIRED = ObligationRule(
    id          = "dpia_required",
    description = "Data Protection Impact Assessment required",
    rationale   = "Art.35 DPIA mandatory before high risk processing begins",
    condition   = lambda f: f.dpia_required and f.gdpr_in_scope,
    trigger_type= "profile_fact",
    mandatory_controls = [
        "GDPR:2016/679:Art.35",      # DPIA
        "GDPR:2016/679:Art.36",      # prior consultation with supervisory authority
        "ISO27001:2022:6.1.2",       # risk assessment
    ],
)

# ── International transfers ────────────────────────────────────────────────────

RULE_INTERNATIONAL_TRANSFERS = ObligationRule(
    id          = "international_transfers",
    description = "Personal data transferred outside EU/UK",
    rationale   = "Chapter V requires adequacy decision or appropriate safeguards for transfers",
    condition   = lambda f: f.transfers_data_outside_eu and f.gdpr_in_scope,
    trigger_type= "profile_fact",
    mandatory_controls = [
        "GDPR:2016/679:Art.44",      # general transfer principle
        "GDPR:2016/679:Art.46",      # transfers with appropriate safeguards (SCCs)
    ],
)

# ── ISO 27001 technical controls ──────────────────────────────────────────────

RULE_SOFTWARE_DEVELOPMENT = ObligationRule(
    id          = "software_development",
    description = "Organisation develops software",
    rationale   = "ISO 27001 A.8.25-A.8.29 apply to organisations with software development",
    condition   = lambda f: f.develops_software and f.iso_in_scope,
    trigger_type= "profile_fact",
    mandatory_controls = [
        "ISO27001:2022:A.8.25",      # secure development lifecycle
        "ISO27001:2022:A.8.26",      # application security requirements
        "ISO27001:2022:A.8.27",      # secure system architecture
        "ISO27001:2022:A.8.28",      # secure coding
        "ISO27001:2022:A.8.29",      # security testing in development
        "ISO27001:2022:A.8.30",      # outsourced development
    ],
)

RULE_REMOTE_WORKERS = ObligationRule(
    id          = "remote_workers",
    description = "Organisation has remote workers",
    rationale   = "A.6.7 specifically covers remote working security requirements",
    condition   = lambda f: f.has_remote_workers and f.iso_in_scope,
    trigger_type= "profile_fact",
    mandatory_controls = [
        "ISO27001:2022:A.6.7",       # remote working
    ],
)

RULE_PHYSICAL_PREMISES = ObligationRule(
    id          = "physical_premises",
    description = "Organisation has physical premises",
    rationale   = "A.7.x physical security controls apply to organisations with premises",
    condition   = lambda f: f.has_physical_premises and f.iso_in_scope,
    trigger_type= "profile_fact",
    mandatory_controls = [
        "ISO27001:2022:A.7.1",       # physical security perimeters
        "ISO27001:2022:A.7.2",       # physical entry
        "ISO27001:2022:A.7.3",       # securing offices, rooms and facilities
        "ISO27001:2022:A.7.4",       # physical security monitoring
        "ISO27001:2022:A.7.5",       # protecting against physical threats
        "ISO27001:2022:A.7.6",       # working in secure areas
        "ISO27001:2022:A.7.7",       # clear desk and clear screen
    ],
)

# ── All rules in evaluation order ─────────────────────────────────────────────

ALL_RULES: list[ObligationRule] = [
    # Universal first — always evaluated
    RULE_ISO_UNIVERSAL,
    RULE_GDPR_UNIVERSAL,

    # GDPR profile-triggered
    RULE_PRIVACY_NOTICES,
    RULE_USES_PROCESSORS,
    RULE_USES_CLOUD,
    RULE_IS_PROCESSOR,
    RULE_JOINT_CONTROLLERS,
    RULE_SPECIAL_CATEGORY,
    RULE_CRIMINAL_DATA,
    RULE_CHILDRENS_DATA,
    RULE_AUTOMATED_DECISIONS,
    RULE_DPO_REQUIRED,
    RULE_RECORDS_REQUIRED,
    RULE_DPIA_REQUIRED,
    RULE_INTERNATIONAL_TRANSFERS,

    # ISO 27001 profile-triggered
    RULE_SOFTWARE_DEVELOPMENT,
    RULE_REMOTE_WORKERS,
    RULE_PHYSICAL_PREMISES,
]


def get_implied_controls(facts: ClientFacts) -> list[dict]:
    """
    Evaluate all rules against client facts.
    Returns list of {control_id, rule_id, rationale} for all triggered controls.
    """
    results = []
    seen    = set()

    for rule in ALL_RULES:
        if rule.condition(facts):
            for control_id in rule.mandatory_controls:
                if control_id not in seen:
                    results.append({
                        "control_id": control_id,
                        "rule_id":    rule.id,
                        "rationale":  rule.rationale,
                        "trigger_type": rule.trigger_type,
                    })
                    seen.add(control_id)

    return results


if __name__ == "__main__":
    from enrichment.obligations.client_facts import ARION_FACTS

    print("Arion Networks — implied obligations:")
    print(f"Active facts: {ARION_FACTS.active_flags()}\n")

    implied = get_implied_controls(ARION_FACTS)
    print(f"Mandatory controls: {len(implied)}\n")

    current_rule = None
    for item in implied:
        if item["rule_id"] != current_rule:
            current_rule = item["rule_id"]
            rule = next(r for r in ALL_RULES if r.id == current_rule)
            print(f"\n[{rule.id}] {rule.description}")
        print(f"  {item['control_id']}")
