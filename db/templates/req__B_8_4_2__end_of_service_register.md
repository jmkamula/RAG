---
leaf_id: req:B.8.4.2:end_of_service_register
control_ref: B.8.4.2
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# End-of-Service Action Register

<<DOC_CONTROL>>

> Per-customer-end-of-service row — the register of return / transfer / disposal actions taken at contract termination. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:B.8.4.2:end_of_service_register -->
<!-- column: item:B.8.4.2:reg_customer_id -->
<!-- column: item:B.8.4.2:reg_termination_date -->
<!-- column: item:B.8.4.2:reg_action_type -->
<!-- column: item:B.8.4.2:reg_completion_date -->
<!-- column: item:B.8.4.2:reg_certification_ref -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of what happens to customer data and assets when a contract ends, making it easier to show compliance with privacy standards like ISO 27701.

## When to use it

Use this register whenever a customer contract ends and you need to document the return, transfer, or disposal of their information. Review and update it about once a year to keep records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required entry, so creating a new register from scratch with five required elements will likely take around an hour, plus additional time for each customer contract you record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.4.2:end_of_service_register -->
| Reg Customer Id | Reg Termination Date | Reg Action Type | Reg Completion Date | Reg Certification Ref |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.4.2:end_of_service_register -->

## Column guidance — what to fill in

### Reg Customer Id

<<MUST item:B.8.4.2:reg_customer_id>>
_Why: Traceability_

> _Standard text:_ Customer identifier per row

<<GUIDANCE>>

### Reg Termination Date

<<MUST item:B.8.4.2:reg_termination_date>>
_Why: Currency_

> _Standard text:_ Contract termination date per row

<<GUIDANCE>>

### Reg Action Type

<<MUST item:B.8.4.2:reg_action_type>>
_Why: §8.4.2_

> _Standard text:_ Action type per row (return / transfer / dispose / hybrid)

<<GUIDANCE>>

### Reg Completion Date

<<MUST item:B.8.4.2:reg_completion_date>>
_Why: Effectiveness_

> _Standard text:_ Completion date per row (return delivered / disposal complete)

<<GUIDANCE>>

### Reg Certification Ref

<<MUST item:B.8.4.2:reg_certification_ref>>
_Why: Audit trail_

> _Standard text:_ Certification reference issued to customer

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Verifier

<<SHOULD item:B.8.4.2:reg_verifier>>
_Why: Accountability_

> _Standard text:_ Verifier identity per row

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
