---
leaf_id: req:A.8.21:service_register
control_ref: A.8.21
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Network Services Register

> Per-service catalogue — service id, provider, security mechanisms in use, SLA performance, last-review date

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row service identifier (ISP / CDN / DNS / SD-WAN / managed-firewall)

<<MUST item:A.8.21:reg_service_id>>
_Why: Identification_

<<TEXT>>

## 2. Per-row provider + contract reference (cross-link to A.5.19/A.5.20 supplier register)

<<MUST item:A.8.21:reg_provider>>
_Why: Cross-control coherence_

<<TEXT>>

## 3. Per-row security mechanisms in use (matches procedure's baseline for the class)

<<MUST item:A.8.21:reg_mechanisms>>
_Why: 27002:8.21 — security mechanisms_

<<TEXT>>

## 4. Per-row SLA performance vs baseline

<<MUST item:A.8.21:reg_sla_performance>>
_Why: 27002:8.21 — monitored_

<<TEXT>>

## 5. Per-row last-review timestamp

<<MUST item:A.8.21:reg_last_reviewed>>
_Why: Drift detection_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row owner (relationship manager + technical owner)

<<SHOULD item:A.8.21:reg_owner>>
_Why: Accountability_

<<TEXT>>
