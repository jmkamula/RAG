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

> Per-monitoring activity record — assessments, complaint handlings, infringement actions (Art.41.4). Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.41:monitoring_record -->
<!-- column: item:Art.41:reg_adherent -->
<!-- column: item:Art.41:reg_activity_type -->
<!-- column: item:Art.41:reg_outcome -->
<!-- column: item:Art.41:reg_sa_notification -->
<!-- column: item:Art.41:reg_date -->
<!-- /TABLE-COLUMNS -->

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

### Reg Activity Type

<<MUST item:Art.41:reg_activity_type>>
_Why: Art.41.2-4_

> _Standard text:_ Per-row activity (eligibility check / periodic monitoring / complaint / infringement action)

### Reg Outcome

<<MUST item:Art.41:reg_outcome>>
_Why: Art.41.4_

> _Standard text:_ Per-row outcome (compliant / non-compliant — corrective / suspension / exclusion per Art.41.4)

### Reg Sa Notification

<<MUST item:Art.41:reg_sa_notification>>
_Why: Art.41.4_

> _Standard text:_ Per-row SA notification where Art.41.4 actions taken

### Reg Date

<<MUST item:Art.41:reg_date>>
_Why: Currency_

> _Standard text:_ Per-row activity date

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Appeal

<<SHOULD item:Art.41:reg_appeal>>
_Why: Procedural fairness_

> _Standard text:_ Per-row appeal handling where adherent contests the outcome
