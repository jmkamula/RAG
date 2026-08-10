---
leaf_id: req:A.7.4.5:end_of_processing_register
control_ref: A.7.4.5
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# End-of-Processing Action Register

<<DOC_CONTROL>>

> Per-batch-action row — the register of delete / de-identify actions taken. Includes verification confirmation. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.4.5:end_of_processing_register -->
<!-- column: item:A.7.4.5:reg_action_id -->
<!-- column: item:A.7.4.5:reg_activity_link -->
<!-- column: item:A.7.4.5:reg_action_type -->
<!-- column: item:A.7.4.5:reg_scope -->
<!-- column: item:A.7.4.5:reg_verification -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of every time you delete or de-identify personal data at the end of a processing batch, including confirmation that the action was completed.

## When to use it

Use this register whenever you finish a data processing batch that requires deleting or de-identifying personal information. Plan to review and update it about once a year to keep it current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for the first entry, with additional time for each batch you record. Completing the initial setup should take around 1 to 1.5 hours.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4.5:end_of_processing_register -->
| Reg Action Id | Reg Activity Link | Reg Action Type | Reg Scope | Reg Verification |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4.5:end_of_processing_register -->

## Column guidance — what to fill in

### Reg Action Id

<<MUST item:A.7.4.5:reg_action_id>>
_Why: Audit trail_

> _Standard text:_ Unique action identifier per row

<<GUIDANCE>>

### Reg Activity Link

<<MUST item:A.7.4.5:reg_activity_link>>
_Why: Traceability_

> _Standard text:_ Processing activity per row

<<GUIDANCE>>

### Reg Action Type

<<MUST item:A.7.4.5:reg_action_type>>
_Why: §7.4.5_

> _Standard text:_ Action type per row (delete / de-identify)

<<GUIDANCE>>

### Reg Scope

<<MUST item:A.7.4.5:reg_scope>>
_Why: Coverage_

> _Standard text:_ Scope per row (which records / systems / backup tier)

<<GUIDANCE>>

### Reg Verification

<<MUST item:A.7.4.5:reg_verification>>
_Why: Effectiveness_

> _Standard text:_ Verification result per row (post-action check confirming PII gone)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Technique Used

<<SHOULD item:A.7.4.5:reg_technique_used>>
_Why: Traceability_

> _Standard text:_ De-identification technique used per row (link to A.7.4.4 register)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
