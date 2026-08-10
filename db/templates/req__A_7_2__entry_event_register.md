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

<<DOC_CONTROL>>

> The catalogue of entry events into secure areas — badge-swipes, visitor sign-ins, exceptions invoked. Drives 'show me who entered the server room on date X' audit

<!-- TABLE-COLUMNS leaf:req:A.7.2:entry_event_register -->
<!-- column: item:A.7.2:reg_event_id -->
<!-- column: item:A.7.2:reg_subject -->
<!-- column: item:A.7.2:reg_area -->
<!-- column: item:A.7.2:reg_timestamp -->
<!-- column: item:A.7.2:reg_method -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of everyone who enters secure areas, such as server rooms, including staff badge-swipes and visitor sign-ins. It's useful if you need to quickly answer questions about who accessed sensitive spaces.

## When to use it

Use this register whenever you have secure areas that people enter, and update it as new entry events occur or when details change. It's important to keep it current to support audits and investigations.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Setting up the register from scratch will likely take about 1 to 1.5 hours for the initial required details, plus a few minutes each time you add a new entry.

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

<<GUIDANCE>>

### Reg Subject

<<MUST item:A.7.2:reg_subject>>
_Why: Accountability_

> _Standard text:_ Per-event subject identifier (employee or visitor; for visitors, host also recorded)

<<GUIDANCE>>

### Reg Area

<<MUST item:A.7.2:reg_area>>
_Why: Cross-control coherence_

> _Standard text:_ Per-event area entered (from the perimeter register A.7.1)

<<GUIDANCE>>

### Reg Timestamp

<<MUST item:A.7.2:reg_timestamp>>
_Why: 27002:7.2 — controls_

> _Standard text:_ Per-event timestamp (entry; exit timestamp where mantrap enforces it)

<<GUIDANCE>>

### Reg Method

<<MUST item:A.7.2:reg_method>>
_Why: Operational discipline_

> _Standard text:_ Per-event entry method (badge / biometric / mechanical / visitor-escort / exception-override)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Anomaly Flag

<<SHOULD item:A.7.2:reg_anomaly_flag>>
_Why: Detection_

> _Standard text:_ Anomaly flag per event (out-of-hours, unusual area for this subject, override-without-justification)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
