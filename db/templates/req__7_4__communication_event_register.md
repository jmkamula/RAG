---
leaf_id: req:7.4:communication_event_register
control_ref: 7.4
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# ISMS Communication Event Register

> Per-communication record — what was communicated, when, to whom, via what channel, with what acknowledgement. The proof communications actually happened, not just planned. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:7.4:communication_event_register -->
<!-- column: item:7.4:reg_event_id -->
<!-- column: item:7.4:reg_topic -->
<!-- column: item:7.4:reg_audience -->
<!-- column: item:7.4:reg_channel -->
<!-- column: item:7.4:reg_date -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:7.4:communication_event_register -->
| Reg Event Id | Reg Topic | Reg Audience | Reg Channel | Reg Date |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:7.4:communication_event_register -->

## Column guidance — what to fill in

### Reg Event Id

<<MUST item:7.4:reg_event_id>>
_Why: Audit defensibility_

> _Standard text:_ Unique event identifier per row

### Reg Topic

<<MUST item:7.4:reg_topic>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-row topic (matches procedure 'what' catalog)

### Reg Audience

<<MUST item:7.4:reg_audience>>
_Why: Clause 7.4 c)_

> _Standard text:_ Per-row audience (which internal group / external party)

### Reg Channel

<<MUST item:7.4:reg_channel>>
_Why: Clause 7.4 d)_

> _Standard text:_ Per-row channel used

### Reg Date

<<MUST item:7.4:reg_date>>
_Why: Currency_

> _Standard text:_ Per-row date / time of communication

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Ack

<<SHOULD item:7.4:reg_ack>>
_Why: Closure proof_

> _Standard text:_ Per-row acknowledgement evidence where required (read-receipt, attendance log, signed receipt)

### Reg Sender

<<SHOULD item:7.4:reg_sender>>
_Why: Accountability — log-shape registers_

> _Standard text:_ Per-row sender / responsible person
