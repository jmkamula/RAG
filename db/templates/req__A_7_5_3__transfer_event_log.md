---
leaf_id: req:A.7.5.3:transfer_event_log
control_ref: A.7.5.3
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# PII Transfer Event Log

> Per-transfer-event row — each PII transfer to/from a third party with recipient, timestamp, purpose. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.5.3:transfer_event_log -->
<!-- column: item:A.7.5.3:reg_event_id -->
<!-- column: item:A.7.5.3:reg_direction -->
<!-- column: item:A.7.5.3:reg_third_party -->
<!-- column: item:A.7.5.3:reg_pii_scope -->
<!-- column: item:A.7.5.3:reg_timestamp -->
<!-- column: item:A.7.5.3:reg_basis_link -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.5.3:transfer_event_log -->
| Reg Event Id | Reg Direction | Reg Third Party | Reg Pii Scope | Reg Timestamp | Reg Basis Link |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.5.3:transfer_event_log -->

## Column guidance — what to fill in

### Reg Event Id

<<MUST item:A.7.5.3:reg_event_id>>
_Why: Audit trail_

> _Standard text:_ Unique transfer event identifier per row

### Reg Direction

<<MUST item:A.7.5.3:reg_direction>>
_Why: §7.5.3 — to or from_

> _Standard text:_ Direction per row (outbound to third party / inbound from third party)

### Reg Third Party

<<MUST item:A.7.5.3:reg_third_party>>
_Why: Traceability_

> _Standard text:_ Third party per row

### Reg Pii Scope

<<MUST item:A.7.5.3:reg_pii_scope>>
_Why: Coverage_

> _Standard text:_ PII scope per row (categories + volume)

### Reg Timestamp

<<MUST item:A.7.5.3:reg_timestamp>>
_Why: Currency_

> _Standard text:_ Timestamp per row

### Reg Basis Link

<<MUST item:A.7.5.3:reg_basis_link>>
_Why: §7.5.1 traceability_

> _Standard text:_ Basis link per row (which A.7.5.1 basis authorised this transfer)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Subject Trigger

<<SHOULD item:A.7.5.3:reg_subject_trigger>>
_Why: §7.5.3 — managing obligations_

> _Standard text:_ Subject-request trigger flag per row (rectification/erasure propagation)
