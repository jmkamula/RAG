"""
ArionComply — Client Fact Taxonomy

Defines the complete set of client facts that drive obligation implication.
25 facts cover all material differentiators across ISO 27001 and GDPR.

Facts are:
  - Boolean (true/false about the client's situation)
  - Collected once at onboarding via questionnaire
  - Stored in Postgres per tenant
  - Loaded at session start into TenantProfile

NOT facts:
  - Compliance findings (NC/OFI/Comply) — those are posture
  - Evidence state (documents uploaded) — that is document management
  - Session state (what the client said today) — that is conversation
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ClientFacts:
    """
    Complete fact profile for a tenant.
    Drives obligation implication — which controls are legally required.
    """

    # ── Scope ─────────────────────────────────────────────────────────────
    processes_personal_data:      bool = False   # entire GDPR triggered
    eu_data_subjects:             bool = False   # GDPR territorial scope
    uk_data_subjects:             bool = False   # UK GDPR scope

    # ── Role ──────────────────────────────────────────────────────────────
    role_controller:              bool = False   # Art.24, Art.13/14
    role_processor:               bool = False   # Art.28, Art.29
    role_joint_controller:        bool = False   # Art.26

    # ── Data types ────────────────────────────────────────────────────────
    special_category_data:        bool = False   # Art.9 (health/biometric/etc)
    criminal_conviction_data:     bool = False   # Art.10
    childrens_data:               bool = False   # Art.8, age verification

    # ── Processing activities ─────────────────────────────────────────────
    automated_decision_making:    bool = False   # Art.22
    profiling:                    bool = False   # Art.22
    large_scale_processing:       bool = False   # Art.37 DPO trigger
    systematic_monitoring:        bool = False   # Art.37 DPO trigger
    high_risk_processing:         bool = False   # Art.35 DPIA required

    # ── Organisation ──────────────────────────────────────────────────────
    employee_count_250_plus:      bool = False   # Art.30 records mandatory
    public_authority:             bool = False   # Art.37 DPO mandatory
    sector:                       str  = "general"  # healthcare/finance/etc

    # ── Third parties ─────────────────────────────────────────────────────
    uses_processors:              bool = False   # Art.28, A.5.19-A.5.22
    uses_cloud_services:          bool = False   # Art.28, A.5.23
    transfers_data_outside_eu:    bool = False   # Art.44-49, SCCs

    # ── Technical ─────────────────────────────────────────────────────────
    develops_software:            bool = False   # A.8.25-A.8.29 SDLC
    has_remote_workers:           bool = False   # A.6.7
    has_physical_premises:        bool = True    # A.7.x (most orgs do)

    # ── Certification ─────────────────────────────────────────────────────
    certification_target:         list[str] = field(
        default_factory=lambda: ["ISO27001:2022", "GDPR:2016/679"]
    )

    # ── Derived helpers ───────────────────────────────────────────────────
    @property
    def gdpr_in_scope(self) -> bool:
        return (self.processes_personal_data and
                (self.eu_data_subjects or self.uk_data_subjects))

    @property
    def iso_in_scope(self) -> bool:
        return "ISO27001:2022" in self.certification_target

    @property
    def dpo_required(self) -> bool:
        return (self.public_authority or
                self.large_scale_processing or
                self.systematic_monitoring)

    @property
    def dpia_required(self) -> bool:
        return self.high_risk_processing

    @property
    def records_required(self) -> bool:
        return (self.employee_count_250_plus or
                self.high_risk_processing or
                self.special_category_data)

    def active_flags(self) -> list[str]:
        """Return list of fact names that are True."""
        flags = []
        for name, val in self.__dict__.items():
            if isinstance(val, bool) and val:
                flags.append(name)
        # Add derived
        if self.gdpr_in_scope:   flags.append("gdpr_in_scope")
        if self.iso_in_scope:    flags.append("iso_in_scope")
        if self.dpo_required:    flags.append("dpo_required")
        if self.dpia_required:   flags.append("dpia_required")
        if self.records_required: flags.append("records_required")
        return flags

    def to_dict(self) -> dict:
        return {
            k: v for k, v in self.__dict__.items()
            if not k.startswith('_')
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ClientFacts":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ── Arion Networks test profile ────────────────────────────────────────────────
ARION_FACTS = ClientFacts(
    processes_personal_data   = True,
    eu_data_subjects          = True,
    uk_data_subjects          = True,
    role_controller           = True,
    role_processor            = True,    # also processes for clients
    special_category_data     = False,
    automated_decision_making = False,
    large_scale_processing    = False,
    employee_count_250_plus   = False,
    public_authority          = False,
    sector                    = "technology",
    uses_processors           = True,
    uses_cloud_services       = True,
    transfers_data_outside_eu = False,
    develops_software         = True,
    has_remote_workers        = True,
    has_physical_premises     = True,
    certification_target      = ["ISO27001:2022", "GDPR:2016/679"],
)
