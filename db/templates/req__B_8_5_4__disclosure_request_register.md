---
leaf_id: req:B.8.5.4:disclosure_request_register
control_ref: B.8.5.4
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Legally-Binding Disclosure Request Register

<<DOC_CONTROL>>

> Per-request row — every legally-binding disclosure request received. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:B.8.5.4:disclosure_request_register -->
<!-- column: item:B.8.5.4:reg_request_id -->
<!-- column: item:B.8.5.4:reg_requester -->
<!-- column: item:B.8.5.4:reg_customer_affected -->
<!-- column: item:B.8.5.4:reg_customer_notification -->
<!-- column: item:B.8.5.4:reg_response_outcome -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of every legally-binding disclosure request your organization receives, supporting privacy compliance and annual reporting needs.

## When to use it

Use this register whenever your organization receives a legally-binding disclosure request. Review and update it at least once a year to ensure your records stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required entry, so setting up the initial register with five elements may take around 1 to 1.5 hours, plus additional time for each new request.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.5.4:disclosure_request_register -->
| Reg Request Id | Reg Requester | Reg Customer Affected | Reg Customer Notification | Reg Response Outcome |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.5.4:disclosure_request_register -->

## Column guidance — what to fill in

### Reg Request Id

<<MUST item:B.8.5.4:reg_request_id>>
_Why: Audit trail_

> _Standard text:_ Unique request identifier per row

<<GUIDANCE>>

### Reg Requester

<<MUST item:B.8.5.4:reg_requester>>
_Why: Traceability_

> _Standard text:_ Requesting authority per row (law enforcement / regulator / court)

<<GUIDANCE>>

### Reg Customer Affected

<<MUST item:B.8.5.4:reg_customer_affected>>
_Why: Scope_

> _Standard text:_ Customer(s) whose PII was targeted per row

<<GUIDANCE>>

### Reg Customer Notification

<<MUST item:B.8.5.4:reg_customer_notification>>
_Why: §8.5.4 — notify customer_

> _Standard text:_ Customer notification date per row (or gag-order flag)

<<GUIDANCE>>

### Reg Response Outcome

<<MUST item:B.8.5.4:reg_response_outcome>>
_Why: Audit trail_

> _Standard text:_ Response outcome per row (data disclosed / request rejected / partial)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Legal Review

<<SHOULD item:B.8.5.4:reg_legal_review>>
_Why: Defensibility_

> _Standard text:_ Legal counsel signoff per row

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
