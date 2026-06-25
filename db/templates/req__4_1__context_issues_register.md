---
leaf_id: req:4.1:context_issues_register
control_ref: 4.1
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Internal and External Issues Register

> Clause 4.1 requires the organization to determine external and internal issues relevant to its ISMS purpose and outcomes. The register is the canonical artefact — issue rows with internal/external classification, relevance to ISMS outcomes, owner, last assessment date. Sibling leaves: identification framework, applicable-domains scope, program review

<!-- TABLE-COLUMNS leaf:req:4.1:context_issues_register -->
<!-- column: item:4.1:internal_issues -->
<!-- column: item:4.1:external_issues -->
<!-- column: item:4.1:relevance_to_ismsm -->
<!-- column: item:4.1:owner -->
<!-- column: item:4.1:reg_last_assessed -->
<!-- column: item:4.1:reg_risk_handoff -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:4.1:context_issues_register -->
| Internal Issues | External Issues | Relevance To Ismsm | Owner | Reg Last Assessed | Reg Risk Handoff |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:4.1:context_issues_register -->

## Column guidance — what to fill in

### Internal Issues

<<MUST item:4.1:internal_issues>>
_Why: Clause 4.1 — internal issues_

> _Standard text:_ Internal issues documented per row (organizational culture, governance, contracts, capabilities, technologies)

### External Issues

<<MUST item:4.1:external_issues>>
_Why: Clause 4.1 — external issues_

> _Standard text:_ External issues documented per row (regulatory, market, threat landscape, social, technology trends)

### Relevance To Ismsm

<<MUST item:4.1:relevance_to_ismsm>>
_Why: Clause 4.1 — affect ability to achieve outcomes_

> _Standard text:_ Relevance to ISMS intended outcomes stated per issue

### Owner

<<MUST item:4.1:owner>>
_Why: Accountability_

> _Standard text:_ Named owner of the register (typically ISMS Manager)

### Reg Last Assessed

<<MUST item:4.1:reg_last_assessed>>
_Why: Currency_

> _Standard text:_ Last assessment date per issue row (drives staleness detection)

### Reg Risk Handoff

<<MUST item:4.1:reg_risk_handoff>>
_Why: Cross-clause coherence_

> _Standard text:_ Per-issue handoff to the risk assessment (6.1.2) where relevance warrants it

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Horizon

<<SHOULD item:4.1:reg_horizon>>
_Why: Planning visibility_

> _Standard text:_ Time-horizon column per issue (near-term vs long-term)
