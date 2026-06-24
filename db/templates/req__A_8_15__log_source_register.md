---
leaf_id: req:A.8.15:log_source_register
control_ref: A.8.15
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Log Source Register

> Per-source register — what's emitting logs, where they land, what retention applies, last-event timestamp (drives 'silent source' detection)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-source identifier (system / app / network device)

<<MUST item:A.8.15:reg_source_id>>
_Why: Identification_

<<TEXT>>

## 2. Per-source log class (auth / access / change / fault / business-event / privacy-relevant)

<<MUST item:A.8.15:reg_log_class>>
_Why: 27002:8.15 — record_

<<TEXT>>

## 3. Per-source collection destination (SIEM index / cold-archive bucket / regulator-required path)

<<MUST item:A.8.15:reg_destination>>
_Why: 27002:8.15 — stored_

<<TEXT>>

## 4. Per-source retention tier applied

<<MUST item:A.8.15:reg_retention_tier>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. Per-source last-event timestamp (drives silent-source detection — common detection gap)

<<MUST item:A.8.15:reg_last_event>>
_Why: Drift detection_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-source named owner (system / app owner)

<<SHOULD item:A.8.15:reg_owner>>
_Why: Accountability_

<<TEXT>>
