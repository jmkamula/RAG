---
leaf_id: req:Art.19:notification_register
control_ref: Art.19
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Recipient Notification Register

<<DOC_CONTROL>>

> Per-notification record proving Art.19 obligations were met for each Art.16/17/18 event. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.19:notification_register -->
<!-- column: item:Art.19:reg_event_id -->
<!-- column: item:Art.19:reg_recipient_list -->
<!-- column: item:Art.19:reg_notification_date -->
<!-- column: item:Art.19:reg_omission_grounds -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record showing that you have notified all relevant parties when personal data is corrected, erased, or restricted, as required by GDPR Article 19.

## When to use it

Use this register whenever you inform recipients about changes to personal data, such as after a correction or deletion. Review and update it at least once a year to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each notification event you need to record. Completing the register from scratch may take around 1-2 hours, depending on the number of notifications.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.19:notification_register -->
| Reg Event Id | Reg Recipient List | Reg Notification Date | Reg Omission Grounds |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.19:notification_register -->

## Column guidance — what to fill in

### Reg Event Id

<<MUST item:Art.19:reg_event_id>>
_Why: Cross-leaf_

> _Standard text:_ Per-row source event id (Art.12 register reference)

<<GUIDANCE>>

### Reg Recipient List

<<MUST item:Art.19:reg_recipient_list>>
_Why: Art.19 — recipients_

> _Standard text:_ Per-row recipients notified list

<<GUIDANCE>>

### Reg Notification Date

<<MUST item:Art.19:reg_notification_date>>
_Why: Currency_

> _Standard text:_ Per-row notification date

<<GUIDANCE>>

### Reg Omission Grounds

<<MUST item:Art.19:reg_omission_grounds>>
_Why: Art.19 — exception_

> _Standard text:_ Per-row omitted recipients with impossibility/disproportionality grounds where applicable

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Ack Received

<<SHOULD item:Art.19:reg_ack_received>>
_Why: Closure_

> _Standard text:_ Per-row recipient acknowledgement where available

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
