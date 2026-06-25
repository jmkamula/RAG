---
leaf_id: req:A.5.20:deviation_register
control_ref: A.5.20
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Supplier Agreement Deviation Register

> Where a supplier successfully negotiates softer terms than the template (or omits a clause entirely), the org needs an auditable record: which clause, which supplier, the reason, the compensating control, the approver. This is the lifecycle-end slot of operational_process applied to agreements: each deviation is the supplier 'exiting' the standard template path

<!-- TABLE-COLUMNS leaf:req:A.5.20:deviation_register -->
<!-- column: item:A.5.20:dev_clause -->
<!-- column: item:A.5.20:dev_supplier -->
<!-- column: item:A.5.20:dev_reason -->
<!-- column: item:A.5.20:dev_compensating -->
<!-- column: item:A.5.20:dev_approver -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.20:deviation_register -->
| Dev Clause | Dev Supplier | Dev Reason | Dev Compensating | Dev Approver |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.20:deviation_register -->

## Column guidance — what to fill in

### Dev Clause

<<MUST item:A.5.20:dev_clause>>
_Why: Audit defensibility_

> _Standard text:_ Clause deviated from per row (identified by template section)

### Dev Supplier

<<MUST item:A.5.20:dev_supplier>>
_Why: Accountability_

> _Standard text:_ Supplier identifier per row (link to A.5.19 supplier register)

### Dev Reason

<<MUST item:A.5.20:dev_reason>>
_Why: Audit defensibility_

> _Standard text:_ Reason for the deviation captured (commercial necessity, market constraint, supplier capability)

### Dev Compensating

<<MUST item:A.5.20:dev_compensating>>
_Why: Risk-based_

> _Standard text:_ Compensating control stated (monitoring, contractual remedy, alternative requirement)

### Dev Approver

<<MUST item:A.5.20:dev_approver>>
_Why: Accountability_

> _Standard text:_ Approver of the deviation, at level proportional to residual risk

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Dev Expiry

<<SHOULD item:A.5.20:dev_expiry>>
_Why: Drift control_

> _Standard text:_ Expiry / re-papering target date for each deviation (so deviations age out rather than persist indefinitely)

### Dev Reassessment

<<SHOULD item:A.5.20:dev_reassessment>>
_Why: Change-driven_

> _Standard text:_ Trigger for reassessment when supplier or risk circumstances change
