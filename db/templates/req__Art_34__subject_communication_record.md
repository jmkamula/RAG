---
leaf_id: req:Art.34:subject_communication_record
control_ref: Art.34
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Subject Communication Record

<<DOC_CONTROL>>

> Per-breach communication record — proves Art.34 communication was made (or documented exception applied). Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.34:subject_communication_record -->
<!-- column: item:Art.34:reg_breach_id -->
<!-- column: item:Art.34:reg_high_risk_decision -->
<!-- column: item:Art.34:reg_exception_cited -->
<!-- column: item:Art.34:reg_communication_method -->
<!-- column: item:Art.34:reg_communication_date -->
<!-- column: item:Art.34:reg_subjects_reached -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of how and when you communicated with individuals after a data breach, or if you applied an exception. It supports your compliance with GDPR requirements for breach notifications.

## When to use it

Use this register whenever a data breach occurs and you need to document your communication with affected individuals, or note an exception. Review and update it at least once a year to keep it current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes to complete all required sections for each breach incident. Additional time may be needed as you add more incidents to the register.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.34:subject_communication_record -->
| Reg Breach Id | Reg High Risk Decision | Reg Exception Cited | Reg Communication Method | Reg Communication Date | Reg Subjects Reached |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.34:subject_communication_record -->

## Column guidance — what to fill in

### Reg Breach Id

<<MUST item:Art.34:reg_breach_id>>
_Why: Cross-article_

> _Standard text:_ Per-row breach id (Art.33 register cross-reference)

<<GUIDANCE>>

### Reg High Risk Decision

<<MUST item:Art.34:reg_high_risk_decision>>
_Why: Art.34.1_

> _Standard text:_ Per-row high-risk decision (high risk → communicate / no high risk → no communication, with rationale)

<<GUIDANCE>>

### Reg Exception Cited

<<MUST item:Art.34:reg_exception_cited>>
_Why: Art.34.3_

> _Standard text:_ Per-row Art.34.3 exception cited (if claimed)

<<GUIDANCE>>

### Reg Communication Method

<<MUST item:Art.34:reg_communication_method>>
_Why: Art.34.2_

> _Standard text:_ Per-row communication method (email + in-app / public notice / mixed)

<<GUIDANCE>>

### Reg Communication Date

<<MUST item:Art.34:reg_communication_date>>
_Why: Currency_

> _Standard text:_ Per-row communication date

<<GUIDANCE>>

### Reg Subjects Reached

<<MUST item:Art.34:reg_subjects_reached>>
_Why: Effectiveness signal_

> _Standard text:_ Per-row subjects-reached count (or 'unable to calculate, public communication used')

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Sa Concurrence

<<SHOULD item:Art.34:reg_sa_concurrence>>
_Why: Art.34.4_

> _Standard text:_ Per-row SA concurrence where SA consulted (Art.34.4)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
