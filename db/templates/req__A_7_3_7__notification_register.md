---
leaf_id: req:A.7.3.7:notification_register
control_ref: A.7.3.7
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Third-Party Notification Register

<<DOC_CONTROL>>

> Per-notification-event row — audit trail of every third-party notification issued. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.3.7:notification_register -->
<!-- column: item:A.7.3.7:reg_notification_id -->
<!-- column: item:A.7.3.7:reg_recipient -->
<!-- column: item:A.7.3.7:reg_trigger_event -->
<!-- column: item:A.7.3.7:reg_dispatch_date -->
<!-- column: item:A.7.3.7:reg_ack_received -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of every notification you send to third parties, making it easy to demonstrate compliance with privacy requirements.

## When to use it

Use this register whenever you notify a third party about a relevant event, and review or update it at least once a year to ensure it stays current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required entry, so setting up the initial register with five elements may take around 1 to 1.5 hours, plus ongoing time for each new notification.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.7:notification_register -->
| Reg Notification Id | Reg Recipient | Reg Trigger Event | Reg Dispatch Date | Reg Ack Received |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.7:notification_register -->

## Column guidance — what to fill in

### Reg Notification Id

<<MUST item:A.7.3.7:reg_notification_id>>
_Why: Audit trail_

> _Standard text:_ Unique notification identifier per row

<<GUIDANCE>>

### Reg Recipient

<<MUST item:A.7.3.7:reg_recipient>>
_Why: Traceability_

> _Standard text:_ Recipient third party per row

<<GUIDANCE>>

### Reg Trigger Event

<<MUST item:A.7.3.7:reg_trigger_event>>
_Why: §7.3.7_

> _Standard text:_ Trigger event per row (which subject event caused the notification)

<<GUIDANCE>>

### Reg Dispatch Date

<<MUST item:A.7.3.7:reg_dispatch_date>>
_Why: Currency_

> _Standard text:_ Dispatch date per row

<<GUIDANCE>>

### Reg Ack Received

<<MUST item:A.7.3.7:reg_ack_received>>
_Why: §7.3.7 — monitor acknowledgement_

> _Standard text:_ Acknowledgement received flag + date per row

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Impossibility Flag

<<SHOULD item:A.7.3.7:reg_impossibility_flag>>
_Why: Art.19_

> _Standard text:_ Impossibility / disproportionate-effort invocation flag per row where applicable

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
