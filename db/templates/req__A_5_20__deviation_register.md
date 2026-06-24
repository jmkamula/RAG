---
leaf_id: req:A.5.20:deviation_register
control_ref: A.5.20
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Supplier Agreement Deviation Register

> Where a supplier successfully negotiates softer terms than the template (or omits a clause entirely), the org needs an auditable record: which clause, which supplier, the reason, the compensating control, the approver. This is the lifecycle-end slot of operational_process applied to agreements: each deviation is the supplier 'exiting' the standard template path

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Clause deviated from per row (identified by template section)

<<MUST item:A.5.20:dev_clause>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Supplier identifier per row (link to A.5.19 supplier register)

<<MUST item:A.5.20:dev_supplier>>
_Why: Accountability_

<<TEXT>>

## 3. Reason for the deviation captured (commercial necessity, market constraint, supplier capability)

<<MUST item:A.5.20:dev_reason>>
_Why: Audit defensibility_

<<TEXT>>

## 4. Compensating control stated (monitoring, contractual remedy, alternative requirement)

<<MUST item:A.5.20:dev_compensating>>
_Why: Risk-based_

<<TEXT>>

## 5. Approver of the deviation, at level proportional to residual risk

<<MUST item:A.5.20:dev_approver>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Expiry / re-papering target date for each deviation (so deviations age out rather than persist indefinitely)

<<SHOULD item:A.5.20:dev_expiry>>
_Why: Drift control_

<<TEXT>>

### 2. Trigger for reassessment when supplier or risk circumstances change

<<SHOULD item:A.5.20:dev_reassessment>>
_Why: Change-driven_

<<TEXT>>
