---
leaf_id: req:A.8.30:engagement_register
control_ref: A.8.30
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Outsourced Development Engagement Register

<<DOC_CONTROL>>

> Per-engagement catalogue — vendor id, scope, contract reference, maturity-assessment outcome, delivered-code-test status

<!-- TABLE-COLUMNS leaf:req:A.8.30:engagement_register -->
<!-- column: item:A.8.30:reg_engagement_id -->
<!-- column: item:A.8.30:reg_vendor -->
<!-- column: item:A.8.30:reg_scope -->
<!-- column: item:A.8.30:reg_contract_ref -->
<!-- column: item:A.8.30:reg_maturity_outcome -->
<!-- column: item:A.8.30:reg_delivered_test_status -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of each outsourced development engagement, including vendor details, contract references, and the status of delivered code testing. It supports your compliance with ISO 27001 requirements for managing external development partners.

## When to use it

Use this register whenever you engage third-party vendors for software development, especially if your risk profile or compliance obligations require tracking these relationships. Update the register as new engagements begin or existing ones change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes entering details for each new engagement, depending on how readily available the required information is. Ongoing updates for new vendors or changes will take less time per entry.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.30:engagement_register -->
| Reg Engagement Id | Reg Vendor | Reg Scope | Reg Contract Ref | Reg Maturity Outcome | Reg Delivered Test Status |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.30:engagement_register -->

## Column guidance — what to fill in

### Reg Engagement Id

<<MUST item:A.8.30:reg_engagement_id>>
_Why: Identification_

> _Standard text:_ Per-engagement unique identifier

<<GUIDANCE>>

### Reg Vendor

<<MUST item:A.8.30:reg_vendor>>
_Why: Cross-control coherence_

> _Standard text:_ Per-engagement vendor (cross-link to A.5.19 supplier register)

<<GUIDANCE>>

### Reg Scope

<<MUST item:A.8.30:reg_scope>>
_Why: 27002:8.30 — direct_

> _Standard text:_ Per-engagement scope description (what's being developed; data classes touched)

<<GUIDANCE>>

### Reg Contract Ref

<<MUST item:A.8.30:reg_contract_ref>>
_Why: Cross-control coherence_

> _Standard text:_ Per-engagement contract reference (cross-link to A.5.20)

<<GUIDANCE>>

### Reg Maturity Outcome

<<MUST item:A.8.30:reg_maturity_outcome>>
_Why: Risk-based vendor selection_

> _Standard text:_ Per-engagement maturity-assessment outcome

<<GUIDANCE>>

### Reg Delivered Test Status

<<MUST item:A.8.30:reg_delivered_test_status>>
_Why: 27002:8.30 — review_

> _Standard text:_ Per-engagement delivered-code-test status (latest review outcome)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Owner

<<SHOULD item:A.8.30:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-engagement named owner (Engineering sponsor + Procurement partner)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
