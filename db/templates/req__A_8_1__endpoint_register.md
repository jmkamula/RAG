---
leaf_id: req:A.8.1:endpoint_register
control_ref: A.8.1
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Endpoint Inventory Register

<<DOC_CONTROL>>

> Catalogue of endpoints in scope of the policy — device id, class, owner, enrolment status, compliance state. Drives 'show me every issued device is enrolled and compliant' audit

<!-- TABLE-COLUMNS leaf:req:A.8.1:endpoint_register -->
<!-- column: item:A.8.1:reg_device_id -->
<!-- column: item:A.8.1:reg_class -->
<!-- column: item:A.8.1:reg_owner -->
<!-- column: item:A.8.1:reg_enrolment -->
<!-- column: item:A.8.1:reg_compliance -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized list of all devices covered by your policy, including details like device ID, type, owner, and compliance status. It’s useful for audits and tracking device compliance.

## When to use it

Use this register at all times to maintain an up-to-date inventory of every device in your environment. Update it whenever devices are added, removed, or their compliance status changes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per device entry to gather and record the required details. Setting up the initial register may take longer if you have many devices.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.1:endpoint_register -->
| Reg Device Id | Reg Class | Reg Owner | Reg Enrolment | Reg Compliance |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.1:endpoint_register -->

## Column guidance — what to fill in

### Reg Device Id

<<MUST item:A.8.1:reg_device_id>>
_Why: Identification_

> _Standard text:_ Per-device unique identifier (serial, asset tag, MDM-issued id)

<<GUIDANCE>>

### Reg Class

<<MUST item:A.8.1:reg_class>>
_Why: Drives policy applicability_

> _Standard text:_ Per-device class (corporate / BYOD / contractor)

<<GUIDANCE>>

### Reg Owner

<<MUST item:A.8.1:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-device named owner (user) and asset owner (IT)

<<GUIDANCE>>

### Reg Enrolment

<<MUST item:A.8.1:reg_enrolment>>
_Why: Drift detection_

> _Standard text:_ Enrolment status (MDM-enrolled / not-required / pending) per row

<<GUIDANCE>>

### Reg Compliance

<<MUST item:A.8.1:reg_compliance>>
_Why: Continuous evidence_

> _Standard text:_ Compliance state per row (encryption on / patch current / EDR active)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Last Seen

<<SHOULD item:A.8.1:reg_last_seen>>
_Why: Operational discipline_

> _Standard text:_ Last check-in timestamp per row (drives stale-device detection)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
