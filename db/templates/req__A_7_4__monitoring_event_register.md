---
leaf_id: req:A.7.4:monitoring_event_register
control_ref: A.7.4
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Monitoring Event Register

> The catalogue of detection events worth investigating — anomalous access attempts, alarms triggered, CCTV-detected behaviour requiring review. Subset of raw detection signal (after first-pass filtering)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-event unique identifier

<<MUST item:A.7.4:reg_event_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Per-event source (CCTV / IDS / access-control / alarm)

<<MUST item:A.7.4:reg_source>>
_Why: 27002:7.4 — detection_

<<TEXT>>

## 3. Per-event timestamp

<<MUST item:A.7.4:reg_timestamp>>
_Why: Operational discipline_

<<TEXT>>

## 4. Per-event classification (true-positive / false-positive / requires-investigation)

<<MUST item:A.7.4:reg_classification>>
_Why: 27002:7.4 — alert response_

<<TEXT>>

## 5. Per-event outcome (closed-no-action / handed-to-A.5.26-incident / lessons-captured)

<<MUST item:A.7.4:reg_outcome>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-event evidence-package link (CCTV clip reference, log excerpt — for cases handed to A.5.28 evidence handling)

<<SHOULD item:A.7.4:reg_evidence_link>>
_Why: Cross-control coherence_

<<TEXT>>
