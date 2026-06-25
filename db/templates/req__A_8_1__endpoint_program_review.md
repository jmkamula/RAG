---
leaf_id: req:A.8.1:endpoint_program_review
control_ref: A.8.1
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Endpoint Program Review

> Annual verification that endpoint protections still match the policy, the register reflects reality, and any new device classes have been incorporated (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.1:endpoint_program_review -->
<!-- column: item:A.8.1:rev_date -->
<!-- column: item:A.8.1:rev_reviewer -->
<!-- column: item:A.8.1:rev_compliance_sample -->
<!-- column: item:A.8.1:rev_scope_check -->
<!-- column: item:A.8.1:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.1:endpoint_program_review -->
| Rev Date | Rev Reviewer | Rev Compliance Sample | Rev Scope Check | Rev Register Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.1:endpoint_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.1:rev_date>>
_Why: 27002:8.1 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.8.1:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (IT lead + InfoSec lead jointly)

### Rev Compliance Sample

<<MUST item:A.8.1:rev_compliance_sample>>
_Why: Continuous evidence_

> _Standard text:_ Sample-based compliance verification across the register (encryption / patching / EDR coverage)

### Rev Scope Check

<<MUST item:A.8.1:rev_scope_check>>
_Why: Cross-leaf coherence_

> _Standard text:_ Cross-check against the applicable scope — any new class or vendor missing

### Rev Register Update

<<MUST item:A.8.1:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the policy / register

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.1:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
