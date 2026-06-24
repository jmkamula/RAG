---
leaf_id: req:A.8.1:endpoint_register
control_ref: A.8.1
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Endpoint Inventory Register

> Catalogue of endpoints in scope of the policy — device id, class, owner, enrolment status, compliance state. Drives 'show me every issued device is enrolled and compliant' audit

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-device unique identifier (serial, asset tag, MDM-issued id)

<<MUST item:A.8.1:reg_device_id>>
_Why: Identification_

<<TEXT>>

## 2. Per-device class (corporate / BYOD / contractor)

<<MUST item:A.8.1:reg_class>>
_Why: Drives policy applicability_

<<TEXT>>

## 3. Per-device named owner (user) and asset owner (IT)

<<MUST item:A.8.1:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 4. Enrolment status (MDM-enrolled / not-required / pending) per row

<<MUST item:A.8.1:reg_enrolment>>
_Why: Drift detection_

<<TEXT>>

## 5. Compliance state per row (encryption on / patch current / EDR active)

<<MUST item:A.8.1:reg_compliance>>
_Why: Continuous evidence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Last check-in timestamp per row (drives stale-device detection)

<<SHOULD item:A.8.1:reg_last_seen>>
_Why: Operational discipline_

<<TEXT>>
