---
leaf_id: req:7.3:awareness_completion_register
control_ref: 7.3
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# ISMS Awareness Completion Register

<<DOC_CONTROL>>

> Per-person completion record — who completed which module, on what date, with what acknowledgement. The proof that awareness was actually delivered, not just designed. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:7.3:awareness_completion_register -->
<!-- column: item:7.3:reg_subject_id -->
<!-- column: item:7.3:reg_module -->
<!-- column: item:7.3:reg_completion_date -->
<!-- column: item:7.3:reg_acknowledgement -->
<!-- column: item:7.3:reg_expiry -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of which employees have completed required ISMS awareness training, including dates and acknowledgements. It serves as proof that your organization has actually delivered the training, not just planned it.

## When to use it

Use this register whenever you need to track and demonstrate staff completion of ISMS awareness modules. Update it at least once a year to ensure your records stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required column to set up the register, plus a few minutes for each employee entry. For a small team, initial setup and data entry may take 1-2 hours.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:7.3:awareness_completion_register -->
| Reg Subject Id | Reg Module | Reg Completion Date | Reg Acknowledgement | Reg Expiry |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:7.3:awareness_completion_register -->

## Column guidance — what to fill in

### Reg Subject Id

<<MUST item:7.3:reg_subject_id>>
_Why: Accountability_

> _Standard text:_ Subject identifier per row (employee or contractor)

<<GUIDANCE>>

### Reg Module

<<MUST item:7.3:reg_module>>
_Why: Coverage_

> _Standard text:_ Module identifier per row (policy module, contribution module, consequences module)

<<GUIDANCE>>

### Reg Completion Date

<<MUST item:7.3:reg_completion_date>>
_Why: Currency_

> _Standard text:_ Completion date per row

<<GUIDANCE>>

### Reg Acknowledgement

<<MUST item:7.3:reg_acknowledgement>>
_Why: Evidence preservation_

> _Standard text:_ Acknowledgement per row (signed receipt, LMS attestation, quiz pass)

<<GUIDANCE>>

### Reg Expiry

<<MUST item:7.3:reg_expiry>>
_Why: Currency_

> _Standard text:_ Expiry / next-due date per row (drives refresher trigger)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Assessment Score

<<SHOULD item:7.3:reg_assessment_score>>
_Why: Effectiveness signal_

> _Standard text:_ Per-row assessment score where the module included a knowledge check

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
