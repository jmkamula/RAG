---
leaf_id: req:A.8.17:sync_register
control_ref: A.8.17
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Clock Sync Status Register

> Per-system sync status — system id, current sync source, current drift, last successful sync timestamp

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row system identifier

<<MUST item:A.8.17:reg_system_id>>
_Why: Identification_

<<TEXT>>

## 2. Per-row current sync source

<<MUST item:A.8.17:reg_source>>
_Why: 27002:8.17 — synchronized_

<<TEXT>>

## 3. Per-row current drift measurement

<<MUST item:A.8.17:reg_drift>>
_Why: Drift detection_

<<TEXT>>

## 4. Per-row last successful sync timestamp

<<MUST item:A.8.17:reg_last_sync>>
_Why: Drift detection_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row outstanding alerts (drift exceeded / source lost)

<<SHOULD item:A.8.17:reg_alerts>>
_Why: Operational visibility_

<<TEXT>>
