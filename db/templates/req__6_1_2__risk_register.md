---
leaf_id: req:6.1.2:risk_register
control_ref: 6.1.2
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Information Security Risk Register

<<DOC_CONTROL>>

> The live output of the assessment procedure — every identified risk with owner, scoring, treatment status. Distinct from the procedure: the procedure is the methodology, the register is the data. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:6.1.2:risk_register -->
<!-- column: item:6.1.2:reg_risk_id -->
<!-- column: item:6.1.2:reg_description -->
<!-- column: item:6.1.2:reg_owner -->
<!-- column: item:6.1.2:reg_scoring -->
<!-- column: item:6.1.2:reg_treatment_status -->
<!-- column: item:6.1.2:reg_last_assessed -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of all your information security risks, including who owns each risk, how serious it is, and what’s being done about it. It’s a practical tool for tracking and managing your security risks over time.

## When to use it

Use this register whenever you need to document and monitor information security risks in your environment. Plan to review and update it about once a year to keep it current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60-90 minutes to set up the required sections for the first time, plus additional time for each risk you add to the register.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:6.1.2:risk_register -->
| Reg Risk Id | Reg Description | Reg Owner | Reg Scoring | Reg Treatment Status | Reg Last Assessed |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:6.1.2:risk_register -->

## Column guidance — what to fill in

### Reg Risk Id

<<MUST item:6.1.2:reg_risk_id>>
_Why: Audit defensibility_

> _Standard text:_ Unique risk identifier per row

<<GUIDANCE>>

### Reg Description

<<MUST item:6.1.2:reg_description>>
_Why: Clause 6.1.2c — identified_

> _Standard text:_ Risk description per row (asset, threat, vulnerability)

<<GUIDANCE>>

### Reg Owner

<<MUST item:6.1.2:reg_owner>>
_Why: Clause 6.1.2c_

> _Standard text:_ Risk owner per row

<<GUIDANCE>>

### Reg Scoring

<<MUST item:6.1.2:reg_scoring>>
_Why: Clause 6.1.2d-e_

> _Standard text:_ Likelihood + consequence scores per row applied per the procedure's criteria

<<GUIDANCE>>

### Reg Treatment Status

<<MUST item:6.1.2:reg_treatment_status>>
_Why: Cross-clause coherence_

> _Standard text:_ Treatment status per row (accept / mitigate / transfer / avoid; link to 6.1.3 plan)

<<GUIDANCE>>

### Reg Last Assessed

<<MUST item:6.1.2:reg_last_assessed>>
_Why: Currency_

> _Standard text:_ Last assessment date per row (drives staleness)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg 4 1 Link

<<SHOULD item:6.1.2:reg_4_1_link>>
_Why: Traceability_

> _Standard text:_ Link from each risk back to the issues register (4.1) entry that surfaced it where applicable

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
