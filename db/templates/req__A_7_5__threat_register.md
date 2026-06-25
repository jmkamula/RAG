---
leaf_id: req:A.7.5:threat_register
control_ref: A.7.5
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Per-Site Threat Register

> The catalogue of identified physical/environmental threats per site with protection measures, last assessment date, residual risk

<!-- TABLE-COLUMNS leaf:req:A.7.5:threat_register -->
<!-- column: item:A.7.5:reg_site_threat -->
<!-- column: item:A.7.5:reg_likelihood -->
<!-- column: item:A.7.5:reg_impact -->
<!-- column: item:A.7.5:reg_protection_in_place -->
<!-- column: item:A.7.5:reg_residual_risk -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.5:threat_register -->
| Reg Site Threat | Reg Likelihood | Reg Impact | Reg Protection In Place | Reg Residual Risk |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.5:threat_register -->

## Column guidance — what to fill in

### Reg Site Threat

<<MUST item:A.7.5:reg_site_threat>>
_Why: 27002:7.5 — assessment_

> _Standard text:_ Per-row site + threat pair (one row per applicable threat per site)

### Reg Likelihood

<<MUST item:A.7.5:reg_likelihood>>
_Why: 27002:7.5 — assessment_

> _Standard text:_ Per-row likelihood rating (informed by geography / historical events / climate projections)

### Reg Impact

<<MUST item:A.7.5:reg_impact>>
_Why: 27002:7.5 — assessment_

> _Standard text:_ Per-row impact rating (worst-case + most-likely scenarios)

### Reg Protection In Place

<<MUST item:A.7.5:reg_protection_in_place>>
_Why: 27002:7.5 — implemented_

> _Standard text:_ Per-row protection measures actually deployed (matches procedure's per-threat list)

### Reg Residual Risk

<<MUST item:A.7.5:reg_residual_risk>>
_Why: Risk discipline_

> _Standard text:_ Per-row residual risk after controls (accepted / requires-treatment)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Last Event

<<SHOULD item:A.7.5:reg_last_event>>
_Why: Empirical input_

> _Standard text:_ Per-row last actual event of this threat type (drives re-assessment cadence)
