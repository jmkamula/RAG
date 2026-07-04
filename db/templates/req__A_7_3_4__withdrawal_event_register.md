---
leaf_id: req:A.7.3.4:withdrawal_event_register
control_ref: A.7.3.4
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Consent Modification / Withdrawal Register

> Per-withdrawal-event row — audit trail of each consent withdrawal or modification with timestamp + propagation status. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.3.4:withdrawal_event_register -->
<!-- column: item:A.7.3.4:reg_event_id -->
<!-- column: item:A.7.3.4:reg_subject_id -->
<!-- column: item:A.7.3.4:reg_event_type -->
<!-- column: item:A.7.3.4:reg_timestamp -->
<!-- column: item:A.7.3.4:reg_propagation_status -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.4:withdrawal_event_register -->
| Reg Event Id | Reg Subject Id | Reg Event Type | Reg Timestamp | Reg Propagation Status |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.4:withdrawal_event_register -->

## Column guidance — what to fill in

### Reg Event Id

<<MUST item:A.7.3.4:reg_event_id>>
_Why: Audit trail_

> _Standard text:_ Unique event identifier per row

### Reg Subject Id

<<MUST item:A.7.3.4:reg_subject_id>>
_Why: Traceability_

> _Standard text:_ Subject identifier per row

### Reg Event Type

<<MUST item:A.7.3.4:reg_event_type>>
_Why: §7.3.4 — modify or withdraw_

> _Standard text:_ Event type per row (modification / partial withdrawal / full withdrawal)

### Reg Timestamp

<<MUST item:A.7.3.4:reg_timestamp>>
_Why: Currency_

> _Standard text:_ Timestamp per row

### Reg Propagation Status

<<MUST item:A.7.3.4:reg_propagation_status>>
_Why: §7.3.4 — dissemination_

> _Standard text:_ Propagation status per row (downstream systems notified / third parties informed)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Channel

<<SHOULD item:A.7.3.4:reg_channel>>
_Why: Parity audit_

> _Standard text:_ Withdrawal channel per row
