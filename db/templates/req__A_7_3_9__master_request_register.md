---
leaf_id: req:A.7.3.9:master_request_register
control_ref: A.7.3.9
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Master Subject Request Register

> Per-request row — the umbrella register covering all subject-rights requests routed through the intake channel. Sub-registers on A.7.3.4-8 track type-specific detail. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.3.9:master_request_register -->
<!-- column: item:A.7.3.9:reg_request_id -->
<!-- column: item:A.7.3.9:reg_intake_channel -->
<!-- column: item:A.7.3.9:reg_classified_type -->
<!-- column: item:A.7.3.9:reg_routing -->
<!-- column: item:A.7.3.9:reg_sla_met_flag -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.9:master_request_register -->
| Reg Request Id | Reg Intake Channel | Reg Classified Type | Reg Routing | Reg Sla Met Flag |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.9:master_request_register -->

## Column guidance — what to fill in

### Reg Request Id

<<MUST item:A.7.3.9:reg_request_id>>
_Why: Audit trail_

> _Standard text:_ Unique request identifier per row

### Reg Intake Channel

<<MUST item:A.7.3.9:reg_intake_channel>>
_Why: Traceability_

> _Standard text:_ Intake channel per row

### Reg Classified Type

<<MUST item:A.7.3.9:reg_classified_type>>
_Why: §7.3.9 — legitimate requests_

> _Standard text:_ Classified type per row (access / correction / erasure / portability / restriction / objection / complaint / other)

### Reg Routing

<<MUST item:A.7.3.9:reg_routing>>
_Why: §7.3.9 — handling_

> _Standard text:_ Routing per row (which sub-procedure handled it)

### Reg Sla Met Flag

<<MUST item:A.7.3.9:reg_sla_met_flag>>
_Why: §7.3.9 — response times_

> _Standard text:_ SLA-met flag per row (auditor-critical timeliness proof)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Fee Charged

<<SHOULD item:A.7.3.9:reg_fee_charged>>
_Why: §7.3.9 — fee cases_

> _Standard text:_ Fee-charged flag + amount per row where applicable
