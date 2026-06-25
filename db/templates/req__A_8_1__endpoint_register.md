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

> Catalogue of endpoints in scope of the policy — device id, class, owner, enrolment status, compliance state. Drives 'show me every issued device is enrolled and compliant' audit

<!-- TABLE-COLUMNS leaf:req:A.8.1:endpoint_register -->
<!-- column: item:A.8.1:reg_device_id -->
<!-- column: item:A.8.1:reg_class -->
<!-- column: item:A.8.1:reg_owner -->
<!-- column: item:A.8.1:reg_enrolment -->
<!-- column: item:A.8.1:reg_compliance -->
<!-- /TABLE-COLUMNS -->

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

### Reg Class

<<MUST item:A.8.1:reg_class>>
_Why: Drives policy applicability_

> _Standard text:_ Per-device class (corporate / BYOD / contractor)

### Reg Owner

<<MUST item:A.8.1:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-device named owner (user) and asset owner (IT)

### Reg Enrolment

<<MUST item:A.8.1:reg_enrolment>>
_Why: Drift detection_

> _Standard text:_ Enrolment status (MDM-enrolled / not-required / pending) per row

### Reg Compliance

<<MUST item:A.8.1:reg_compliance>>
_Why: Continuous evidence_

> _Standard text:_ Compliance state per row (encryption on / patch current / EDR active)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Last Seen

<<SHOULD item:A.8.1:reg_last_seen>>
_Why: Operational discipline_

> _Standard text:_ Last check-in timestamp per row (drives stale-device detection)
