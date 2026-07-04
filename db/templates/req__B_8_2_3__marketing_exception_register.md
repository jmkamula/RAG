---
leaf_id: req:B.8.2.3:marketing_exception_register
control_ref: B.8.2.3
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Marketing Use Exception Register

> Per-exception row — the register of authorised marketing/advertising uses of customer PII (typically zero rows for most processors). Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:B.8.2.3:marketing_exception_register -->
<!-- column: item:B.8.2.3:reg_exception_id -->
<!-- column: item:B.8.2.3:reg_customer_id -->
<!-- column: item:B.8.2.3:reg_customer_permit -->
<!-- column: item:B.8.2.3:reg_subject_consent -->
<!-- column: item:B.8.2.3:reg_activity_scope -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.2.3:marketing_exception_register -->
| Reg Exception Id | Reg Customer Id | Reg Customer Permit | Reg Subject Consent | Reg Activity Scope |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.2.3:marketing_exception_register -->

## Column guidance — what to fill in

### Reg Exception Id

<<MUST item:B.8.2.3:reg_exception_id>>
_Why: Traceability_

> _Standard text:_ Unique exception identifier per row

### Reg Customer Id

<<MUST item:B.8.2.3:reg_customer_id>>
_Why: Scope_

> _Standard text:_ Customer identifier per row (which customer's PII involved)

### Reg Customer Permit

<<MUST item:B.8.2.3:reg_customer_permit>>
_Why: §8.2.3 — customer contractual requirements documented_

> _Standard text:_ Customer-permit document reference per row (contract clause / signed permit)

### Reg Subject Consent

<<MUST item:B.8.2.3:reg_subject_consent>>
_Why: §8.2.3 — prior consent_

> _Standard text:_ Subject-level consent evidence path per row (customer-obtained + provided to processor OR processor-obtained direct)

### Reg Activity Scope

<<MUST item:B.8.2.3:reg_activity_scope>>
_Why: Defensibility_

> _Standard text:_ Marketing activity scope per row (targeted advertising channels + creative)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Withdrawal Handling

<<SHOULD item:B.8.2.3:reg_withdrawal_handling>>
_Why: Art.7.3 — right to withdraw_

> _Standard text:_ Withdrawal handling pathway per row (how subject opt-out propagates)
