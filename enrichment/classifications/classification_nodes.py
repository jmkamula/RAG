"""
ArionComply — Classification Vocabulary Definitions

Classification dimensions and allowed values bridge per-tenant incidents
(Postgres) to curated Event definitions (Neo4j).

Each ClassificationDimension is owned by a standard and describes an axis on
which an incident can be classified. Each ClassificationValue is one allowed
value on that dimension, and MANIFESTS_AS zero or more :Event nodes — those
events' TRIGGERS_OBLIGATION + REQUIRES_DOCUMENT edges define what must be
done to resolve an incident classified with that value.

Loaded into Neo4j as graph nodes; Postgres `incident_classifications` rows
reference (standard_id, dimension, value) as the logical key.

v1 dimensions:
  GDPR / breach_cia     — combinable (an incident can be confidentiality +
                          integrity + availability simultaneously, per EDPB
                          Guidelines 9/2022).
  ISO_27035 / category  — non-combinable (mechanism is singular).

Adding a dimension or value here is a *curator* action — these are
definitions, not tenant data. After editing, run:
    python3 enrichment/classifications/load_to_neo4j.py --dry-run
    python3 enrichment/classifications/load_to_neo4j.py
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ClassificationValue:
    id:          str          # "classval:GDPR:breach_cia:confidentiality"
    standard_id: str          # "GDPR"
    dimension:   str          # "breach_cia"
    value:       str          # "confidentiality"
    title:       str
    description: str
    # Event ids this value manifests as — drives obligation materialisation.
    # 0..N: empty list = pure label, no obligations triggered.
    manifests_as: list[str] = field(default_factory=list)


@dataclass
class ClassificationDimension:
    id:             str        # "classdim:GDPR:breach_cia"
    standard_id:    str
    dimension:      str
    title:          str
    description:    str
    clause_ref:     str        # citation in the source standard
    is_combinable:  bool       # may one incident carry multiple values on this dimension?
    values:         list[ClassificationValue] = field(default_factory=list)


# ── Dimension 1: GDPR — breach CIA dimension ────────────────────────────────

DIM_GDPR_BREACH_CIA = ClassificationDimension(
    id            = "classdim:GDPR:breach_cia",
    standard_id   = "GDPR",
    dimension     = "breach_cia",
    title         = "Personal Data Breach CIA Dimension",
    description   = "Personal data breaches are classified by which property "
                    "of the CIA triad was compromised. A single breach can "
                    "affect more than one — e.g. ransomware affecting personal "
                    "data is both a confidentiality breach (data exfiltrated) "
                    "and an availability breach (data encrypted).",
    clause_ref    = "GDPR Art. 4(12); EDPB Guidelines 9/2022 §I.B",
    is_combinable = True,
    values = [
        ClassificationValue(
            id           = "classval:GDPR:breach_cia:confidentiality",
            standard_id  = "GDPR",
            dimension    = "breach_cia",
            value        = "confidentiality",
            title        = "Confidentiality Breach",
            description  = "Unauthorised or accidental disclosure of, or access "
                           "to, personal data.",
            manifests_as = ["event:personal_data_breach"],
        ),
        ClassificationValue(
            id           = "classval:GDPR:breach_cia:integrity",
            standard_id  = "GDPR",
            dimension    = "breach_cia",
            value        = "integrity",
            title        = "Integrity Breach",
            description  = "Unauthorised or accidental alteration of personal "
                           "data.",
            manifests_as = ["event:personal_data_breach"],
        ),
        ClassificationValue(
            id           = "classval:GDPR:breach_cia:availability",
            standard_id  = "GDPR",
            dimension    = "breach_cia",
            value        = "availability",
            title        = "Availability Breach",
            description  = "Accidental or unauthorised loss of access to, or "
                           "destruction of, personal data.",
            manifests_as = ["event:personal_data_breach"],
        ),
    ],
)


# ── Dimension 2: ISO 27035 — incident category (mechanism) ──────────────────

DIM_ISO27035_CATEGORY = ClassificationDimension(
    id            = "classdim:ISO_27035:category",
    standard_id   = "ISO_27035",
    dimension     = "category",
    title         = "Information Security Incident Category",
    description   = "ISO/IEC 27035-1 categorises incidents by mechanism / "
                    "cause. The category is singular — an incident has one "
                    "primary mechanism even if multiple controls are touched. "
                    "All values manifest as event:information_security_incident "
                    "in v1; can be split into mechanism-specific events later "
                    "if obligations need to diverge.",
    clause_ref    = "ISO/IEC 27035-1:2023 §5.4",
    is_combinable = False,
    values = [
        ClassificationValue(
            id           = "classval:ISO_27035:category:malicious_code",
            standard_id  = "ISO_27035",
            dimension    = "category",
            value        = "malicious_code",
            title        = "Malicious Code",
            description  = "Virus, worm, ransomware, trojan, spyware, or other "
                           "malware affecting information systems.",
            manifests_as = ["event:information_security_incident"],
        ),
        ClassificationValue(
            id           = "classval:ISO_27035:category:social_engineering",
            standard_id  = "ISO_27035",
            dimension    = "category",
            value        = "social_engineering",
            title        = "Social Engineering",
            description  = "Phishing, pretexting, baiting, or other "
                           "manipulation of people to gain unauthorised "
                           "access or information.",
            manifests_as = ["event:information_security_incident"],
        ),
        ClassificationValue(
            id           = "classval:ISO_27035:category:misuse_of_resources",
            standard_id  = "ISO_27035",
            dimension    = "category",
            value        = "misuse_of_resources",
            title        = "Misuse of Resources",
            description  = "Unauthorised or inappropriate use of organisational "
                           "information systems by authorised users.",
            manifests_as = ["event:information_security_incident"],
        ),
        ClassificationValue(
            id           = "classval:ISO_27035:category:denial_of_service",
            standard_id  = "ISO_27035",
            dimension    = "category",
            value        = "denial_of_service",
            title        = "Denial of Service",
            description  = "Disruption of system availability, whether "
                           "deliberate (DDoS) or accidental (resource "
                           "exhaustion).",
            manifests_as = ["event:information_security_incident"],
        ),
        ClassificationValue(
            id           = "classval:ISO_27035:category:intrusion",
            standard_id  = "ISO_27035",
            dimension    = "category",
            value        = "intrusion",
            title        = "Intrusion / Unauthorised Access",
            description  = "Unauthorised access to information systems, "
                           "networks, or data — successful or attempted.",
            manifests_as = ["event:information_security_incident"],
        ),
        ClassificationValue(
            id           = "classval:ISO_27035:category:technical_failure",
            standard_id  = "ISO_27035",
            dimension    = "category",
            value        = "technical_failure",
            title        = "Technical Failure",
            description  = "Hardware, software, or network failure resulting "
                           "in loss of confidentiality, integrity, or "
                           "availability.",
            manifests_as = ["event:information_security_incident"],
        ),
        ClassificationValue(
            id           = "classval:ISO_27035:category:information_gathering",
            standard_id  = "ISO_27035",
            dimension    = "category",
            value        = "information_gathering",
            title        = "Unauthorised Information Gathering",
            description  = "Reconnaissance, scanning, or other activity to "
                           "gather information about systems without "
                           "authorisation.",
            manifests_as = ["event:information_security_incident"],
        ),
        ClassificationValue(
            id           = "classval:ISO_27035:category:unspecified",
            standard_id  = "ISO_27035",
            dimension    = "category",
            value        = "unspecified",
            title        = "Unspecified Information Security Incident",
            description  = "Incident is information-security-relevant but the "
                           "mechanism has not been pinned down. Used by the "
                           "workbook importer when the source data does not "
                           "indicate a specific category; curator refines later.",
            manifests_as = ["event:information_security_incident"],
        ),
    ],
)


ALL_DIMENSIONS: list[ClassificationDimension] = [
    DIM_GDPR_BREACH_CIA,
    DIM_ISO27035_CATEGORY,
]


def all_values() -> list[ClassificationValue]:
    return [v for d in ALL_DIMENSIONS for v in d.values]


def get_dimension(standard_id: str, dimension: str) -> ClassificationDimension | None:
    return next(
        (d for d in ALL_DIMENSIONS
         if d.standard_id == standard_id and d.dimension == dimension),
        None,
    )


def get_value(standard_id: str, dimension: str, value: str) -> ClassificationValue | None:
    return next(
        (v for v in all_values()
         if v.standard_id == standard_id
         and v.dimension == dimension
         and v.value == value),
        None,
    )


if __name__ == "__main__":
    print(f"Dimensions: {len(ALL_DIMENSIONS)}")
    for d in ALL_DIMENSIONS:
        flag = "combinable" if d.is_combinable else "single"
        print(f"  {d.standard_id}/{d.dimension:18s} [{flag:10s}]  "
              f"{len(d.values)} values  ({d.clause_ref})")
    print(f"\nTotal values: {sum(len(d.values) for d in ALL_DIMENSIONS)}")
    print(f"\nValue → event bindings:")
    for v in all_values():
        binds = ", ".join(v.manifests_as) if v.manifests_as else "(label only)"
        print(f"  {v.standard_id}/{v.dimension}/{v.value:25s} → {binds}")
