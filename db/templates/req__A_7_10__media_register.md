---
leaf_id: req:A.7.10:media_register
control_ref: A.7.10
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Storage Media Register

> The catalogue of issued storage media — id, classification, current holder, lifecycle stage. Drives 'where is media X' query and stale-issue detection

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row media identifier (serial/asset tag)

<<MUST item:A.7.10:reg_media_id>>
_Why: Lifecycle tracking_

<<TEXT>>

## 2. Per-row classification (drives encryption + handling requirements)

<<MUST item:A.7.10:reg_class>>
_Why: Cross-control coherence_

<<TEXT>>

## 3. Per-row current holder

<<MUST item:A.7.10:reg_holder>>
_Why: Accountability_

<<TEXT>>

## 4. Per-row lifecycle stage (in-use / in-transit / awaiting-disposal / disposed)

<<MUST item:A.7.10:reg_lifecycle_stage>>
_Why: 27002:7.10 — life cycle_

<<TEXT>>

## 5. Per-row issue date

<<MUST item:A.7.10:reg_issued_date>>
_Why: Drift detection_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row last-seen timestamp (drives stale-issue detection)

<<SHOULD item:A.7.10:reg_last_seen>>
_Why: Loss detection_

<<TEXT>>
