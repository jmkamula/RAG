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

> Per-engagement catalogue — vendor id, scope, contract reference, maturity-assessment outcome, delivered-code-test status

<!-- TABLE-COLUMNS leaf:req:A.8.30:engagement_register -->
<!-- column: item:A.8.30:reg_engagement_id -->
<!-- column: item:A.8.30:reg_vendor -->
<!-- column: item:A.8.30:reg_scope -->
<!-- column: item:A.8.30:reg_contract_ref -->
<!-- column: item:A.8.30:reg_maturity_outcome -->
<!-- column: item:A.8.30:reg_delivered_test_status -->
<!-- /TABLE-COLUMNS -->

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

### Reg Vendor

<<MUST item:A.8.30:reg_vendor>>
_Why: Cross-control coherence_

> _Standard text:_ Per-engagement vendor (cross-link to A.5.19 supplier register)

### Reg Scope

<<MUST item:A.8.30:reg_scope>>
_Why: 27002:8.30 — direct_

> _Standard text:_ Per-engagement scope description (what's being developed; data classes touched)

### Reg Contract Ref

<<MUST item:A.8.30:reg_contract_ref>>
_Why: Cross-control coherence_

> _Standard text:_ Per-engagement contract reference (cross-link to A.5.20)

### Reg Maturity Outcome

<<MUST item:A.8.30:reg_maturity_outcome>>
_Why: Risk-based vendor selection_

> _Standard text:_ Per-engagement maturity-assessment outcome

### Reg Delivered Test Status

<<MUST item:A.8.30:reg_delivered_test_status>>
_Why: 27002:8.30 — review_

> _Standard text:_ Per-engagement delivered-code-test status (latest review outcome)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Owner

<<SHOULD item:A.8.30:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-engagement named owner (Engineering sponsor + Procurement partner)
