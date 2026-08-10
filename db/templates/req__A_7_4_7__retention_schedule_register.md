---
leaf_id: req:A.7.4.7:retention_schedule_register
control_ref: A.7.4.7
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# PII Retention Schedule Register

<<DOC_CONTROL>>

> Per-category-and-activity row — the actual retention schedules. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.4.7:retention_schedule_register -->
<!-- column: item:A.7.4.7:reg_category_id -->
<!-- column: item:A.7.4.7:reg_retention_period -->
<!-- column: item:A.7.4.7:reg_rationale_type -->
<!-- column: item:A.7.4.7:reg_citation -->
<!-- column: item:A.7.4.7:reg_deletion_trigger -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you organize and document how long you keep different types of personal information, making it easier to manage data in line with privacy standards.

## When to use it

Use this register when you need to track and review how long you retain personal data for each category and activity, updating it about once a year or whenever your retention practices change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each row; completing the register from scratch typically takes 1-2 hours, depending on the number of data categories and activities you need to cover.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4.7:retention_schedule_register -->
| Reg Category Id | Reg Retention Period | Reg Rationale Type | Reg Citation | Reg Deletion Trigger |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4.7:retention_schedule_register -->

## Column guidance — what to fill in

### Reg Category Id

<<MUST item:A.7.4.7:reg_category_id>>
_Why: Referenceability_

> _Standard text:_ Category / activity combination identifier per row

<<GUIDANCE>>

### Reg Retention Period

<<MUST item:A.7.4.7:reg_retention_period>>
_Why: §7.4.7 — schedules_

> _Standard text:_ Retention period per row (with unit — years / months / until event)

<<GUIDANCE>>

### Reg Rationale Type

<<MUST item:A.7.4.7:reg_rationale_type>>
_Why: §7.4.7 — legal, regulatory, business_

> _Standard text:_ Rationale type per row (legal / regulatory / business)

<<GUIDANCE>>

### Reg Citation

<<MUST item:A.7.4.7:reg_citation>>
_Why: Defensibility_

> _Standard text:_ Citation per row (specific statute / regulation / business rationale document)

<<GUIDANCE>>

### Reg Deletion Trigger

<<MUST item:A.7.4.7:reg_deletion_trigger>>
_Why: Integration with A.7.4.5_

> _Standard text:_ Deletion trigger per row (calendar-based / event-based)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Conflict Flag

<<SHOULD item:A.7.4.7:reg_conflict_flag>>
_Why: §7.4.7 — business decision_

> _Standard text:_ Conflict flag per row if legal + business tension exists

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
