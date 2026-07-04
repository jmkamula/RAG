---
leaf_id: req:B.8.3.1:support_request_register
control_ref: B.8.3.1
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Customer Subject-Rights Support Register

> Per-customer-request row — the register of customer requests for subject-rights support. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:B.8.3.1:support_request_register -->
<!-- column: item:B.8.3.1:reg_request_id -->
<!-- column: item:B.8.3.1:reg_customer_id -->
<!-- column: item:B.8.3.1:reg_request_type -->
<!-- column: item:B.8.3.1:reg_response -->
<!-- column: item:B.8.3.1:reg_sla_met -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.3.1:support_request_register -->
| Reg Request Id | Reg Customer Id | Reg Request Type | Reg Response | Reg Sla Met |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.3.1:support_request_register -->

## Column guidance — what to fill in

### Reg Request Id

<<MUST item:B.8.3.1:reg_request_id>>
_Why: Audit trail_

> _Standard text:_ Unique request identifier per row

### Reg Customer Id

<<MUST item:B.8.3.1:reg_customer_id>>
_Why: Scope_

> _Standard text:_ Requesting customer identifier per row

### Reg Request Type

<<MUST item:B.8.3.1:reg_request_type>>
_Why: §8.3.1_

> _Standard text:_ Request type per row (rectification support / erasure support / portability export / restriction / info-for-Art.15)

### Reg Response

<<MUST item:B.8.3.1:reg_response>>
_Why: Audit trail_

> _Standard text:_ Response per row (what was provided / done)

### Reg Sla Met

<<MUST item:B.8.3.1:reg_sla_met>>
_Why: Timeliness_

> _Standard text:_ SLA-met flag per row

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Contract Ref

<<SHOULD item:B.8.3.1:reg_contract_ref>>
_Why: Traceability_

> _Standard text:_ Contract reference per row (which B.8.2.1 agreement scoped this support)
