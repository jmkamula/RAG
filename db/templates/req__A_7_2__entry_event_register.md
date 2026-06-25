---
leaf_id: req:A.7.2:entry_event_register
control_ref: A.7.2
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Physical Entry Event Register

> The catalogue of entry events into secure areas — badge-swipes, visitor sign-ins, exceptions invoked. Drives 'show me who entered the server room on date X' audit

<!-- TABLE-COLUMNS leaf:req:A.7.2:entry_event_register -->
<!-- column: item:A.7.2:reg_event_id -->
<!-- column: item:A.7.2:reg_subject -->
<!-- column: item:A.7.2:reg_area -->
<!-- column: item:A.7.2:reg_timestamp -->
<!-- column: item:A.7.2:reg_method -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2:entry_event_register -->
| Reg Event Id | Reg Subject | Reg Area | Reg Timestamp | Reg Method |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2:entry_event_register -->

## Column guidance — what to fill in

### Reg Event Id

<<MUST item:A.7.2:reg_event_id>>
_Why: Audit defensibility_

> _Standard text:_ Per-event unique identifier

### Reg Subject

<<MUST item:A.7.2:reg_subject>>
_Why: Accountability_

> _Standard text:_ Per-event subject identifier (employee or visitor; for visitors, host also recorded)

### Reg Area

<<MUST item:A.7.2:reg_area>>
_Why: Cross-control coherence_

> _Standard text:_ Per-event area entered (from the perimeter register A.7.1)

### Reg Timestamp

<<MUST item:A.7.2:reg_timestamp>>
_Why: 27002:7.2 — controls_

> _Standard text:_ Per-event timestamp (entry; exit timestamp where mantrap enforces it)

### Reg Method

<<MUST item:A.7.2:reg_method>>
_Why: Operational discipline_

> _Standard text:_ Per-event entry method (badge / biometric / mechanical / visitor-escort / exception-override)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Anomaly Flag

<<SHOULD item:A.7.2:reg_anomaly_flag>>
_Why: Detection_

> _Standard text:_ Anomaly flag per event (out-of-hours, unusual area for this subject, override-without-justification)
