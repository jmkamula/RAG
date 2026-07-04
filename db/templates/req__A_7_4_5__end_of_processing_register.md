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

> Per-batch-action row — the register of delete / de-identify actions taken. Includes verification confirmation. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.4.5:end_of_processing_register -->
<!-- column: item:A.7.4.5:reg_action_id -->
<!-- column: item:A.7.4.5:reg_activity_link -->
<!-- column: item:A.7.4.5:reg_action_type -->
<!-- column: item:A.7.4.5:reg_scope -->
<!-- column: item:A.7.4.5:reg_verification -->
<!-- /TABLE-COLUMNS -->

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

### Reg Activity Link

<<MUST item:A.7.4.5:reg_activity_link>>
_Why: Traceability_

> _Standard text:_ Processing activity per row

### Reg Action Type

<<MUST item:A.7.4.5:reg_action_type>>
_Why: §7.4.5_

> _Standard text:_ Action type per row (delete / de-identify)

### Reg Scope

<<MUST item:A.7.4.5:reg_scope>>
_Why: Coverage_

> _Standard text:_ Scope per row (which records / systems / backup tier)

### Reg Verification

<<MUST item:A.7.4.5:reg_verification>>
_Why: Effectiveness_

> _Standard text:_ Verification result per row (post-action check confirming PII gone)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Technique Used

<<SHOULD item:A.7.4.5:reg_technique_used>>
_Why: Traceability_

> _Standard text:_ De-identification technique used per row (link to A.7.4.4 register)
