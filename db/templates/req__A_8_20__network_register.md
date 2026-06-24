---
leaf_id: req:A.8.20:network_register
control_ref: A.8.20
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Network Inventory Register

> Per-network inventory — segment id, classification, perimeter type, owner. Drives 'every segment has a documented zone + perimeter' audit

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row segment / VPC / VLAN identifier

<<MUST item:A.8.20:reg_segment_id>>
_Why: Identification_

<<TEXT>>

## 2. Per-row classification tier (from A.5.12)

<<MUST item:A.8.20:reg_classification>>
_Why: Cross-control coherence_

<<TEXT>>

## 3. Per-row zone assignment (matches A.8.22 zone model)

<<MUST item:A.8.20:reg_zone>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 4. Per-row perimeter type (boundary firewall / service mesh / IAP / vendor-managed)

<<MUST item:A.8.20:reg_perimeter>>
_Why: 27002:8.20 — perimeter_

<<TEXT>>

## 5. Per-row named owner (network engineer accountable)

<<MUST item:A.8.20:reg_owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row last-audited timestamp (drives drift detection)

<<SHOULD item:A.8.20:reg_last_audited>>
_Why: Drift detection_

<<TEXT>>
