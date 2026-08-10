---
leaf_id: req:Art.41:monitoring_record
control_ref: Art.41
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Code Monitoring Activity Record

<<DOC_CONTROL>>

> Per-monitoring activity record — assessments, complaint handlings, infringement actions (Art.41.4). Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.41:monitoring_record -->
<!-- column: item:Art.41:reg_adherent -->
<!-- column: item:Art.41:reg_activity_type -->
<!-- column: item:Art.41:reg_outcome -->
<!-- column: item:Art.41:reg_sa_notification -->
<!-- column: item:Art.41:reg_date -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of all your code monitoring activities, including assessments, complaint handling, and any actions taken for infringements, making it easier to demonstrate compliance with GDPR requirements.

## When to use it

Use this template whenever your organization conducts code monitoring activities that fall under GDPR Article 41, such as handling complaints or performing assessments. Update the register at least once a year to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes filling out the required sections for each monitoring activity, with additional time needed as you add more entries to the register.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.41:monitoring_record -->
| Reg Adherent | Reg Activity Type | Reg Outcome | Reg Sa Notification | Reg Date |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.41:monitoring_record -->

## Column guidance — what to fill in

### Reg Adherent

<<MUST item:Art.41:reg_adherent>>
_Why: Audit_

> _Standard text:_ Per-row adherent monitored

<<GUIDANCE>>

### Reg Activity Type

<<MUST item:Art.41:reg_activity_type>>
_Why: Art.41.2-4_

> _Standard text:_ Per-row activity (eligibility check / periodic monitoring / complaint / infringement action)

<<GUIDANCE>>

### Reg Outcome

<<MUST item:Art.41:reg_outcome>>
_Why: Art.41.4_

> _Standard text:_ Per-row outcome (compliant / non-compliant — corrective / suspension / exclusion per Art.41.4)

<<GUIDANCE>>

### Reg Sa Notification

<<MUST item:Art.41:reg_sa_notification>>
_Why: Art.41.4_

> _Standard text:_ Per-row SA notification where Art.41.4 actions taken

<<GUIDANCE>>

### Reg Date

<<MUST item:Art.41:reg_date>>
_Why: Currency_

> _Standard text:_ Per-row activity date

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Appeal

<<SHOULD item:Art.41:reg_appeal>>
_Why: Procedural fairness_

> _Standard text:_ Per-row appeal handling where adherent contests the outcome

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
