---
leaf_id: req:B.8.5.5:disclosure_decision_register
control_ref: B.8.5.5
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Disclosure Decision Register

<<DOC_CONTROL>>

> Per-decision row — every disclosure request evaluated (accept + reject) with rationale. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:B.8.5.5:disclosure_decision_register -->
<!-- column: item:B.8.5.5:reg_decision_id -->
<!-- column: item:B.8.5.5:reg_request_source -->
<!-- column: item:B.8.5.5:reg_binding_classification -->
<!-- column: item:B.8.5.5:reg_outcome -->
<!-- column: item:B.8.5.5:reg_customer_authorisation -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of every decision made about sharing personal data, including both approvals and rejections, along with the reasons behind each choice.

## When to use it

Use this register whenever you evaluate a request to disclose personal information, whether you accept or reject it. Review and update the register about once a year to keep it current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each decision you record. Setting up the register from scratch will likely take around 1-2 hours, depending on the number of decisions to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.5.5:disclosure_decision_register -->
| Reg Decision Id | Reg Request Source | Reg Binding Classification | Reg Outcome | Reg Customer Authorisation |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.5.5:disclosure_decision_register -->

## Column guidance — what to fill in

### Reg Decision Id

<<MUST item:B.8.5.5:reg_decision_id>>
_Why: Audit trail_

> _Standard text:_ Unique decision identifier per row

<<GUIDANCE>>

### Reg Request Source

<<MUST item:B.8.5.5:reg_request_source>>
_Why: Traceability_

> _Standard text:_ Request source per row

<<GUIDANCE>>

### Reg Binding Classification

<<MUST item:B.8.5.5:reg_binding_classification>>
_Why: §8.5.5_

> _Standard text:_ Binding classification per row (legally binding / not binding)

<<GUIDANCE>>

### Reg Outcome

<<MUST item:B.8.5.5:reg_outcome>>
_Why: §8.5.5_

> _Standard text:_ Outcome per row (rejected / accepted / customer-consulted)

<<GUIDANCE>>

### Reg Customer Authorisation

<<MUST item:B.8.5.5:reg_customer_authorisation>>
_Why: §8.5.5 — customer-authorised_

> _Standard text:_ Customer authorisation reference per row (contract clause / one-off approval)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Legal Review

<<SHOULD item:B.8.5.5:reg_legal_review>>
_Why: Defensibility_

> _Standard text:_ Legal counsel signoff per row

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
