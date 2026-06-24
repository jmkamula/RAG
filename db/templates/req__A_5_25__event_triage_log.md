---
leaf_id: req:A.5.25:event_triage_log
control_ref: A.5.25
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Security Event Triage Log

> A.5.25 expects records of events, incidents and weaknesses to be maintained and accessible to competent personnel. The triage log is the live source of truth — every triaged event, its classification, decision and owner — feeding the periodic review and the per-event triage-decision records

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Each event captured with a unique identifier and detection timestamp

<<MUST item:A.5.25:log_event_id>>
_Why: 27002:5.25 — records of events_

<<TEXT>>

## 2. Detection source per row (which monitoring system / user / third party reported it)

<<MUST item:A.5.25:log_source>>
_Why: 27002:5.25 — events_

<<TEXT>>

## 3. Classification per row (event / near-miss / incident / false positive) with severity

<<MUST item:A.5.25:log_classification>>
_Why: 27002:5.25 — categorised_

<<TEXT>>

## 4. Triage decision per row (close as false positive / file as near-miss / escalate to A.5.26)

<<MUST item:A.5.25:log_decision>>
_Why: 27002:5.25 — decision_

<<TEXT>>

## 5. Named triager per row (accountability)

<<MUST item:A.5.25:log_owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. False-positive flag tracked separately (drives calibration in the program review)

<<SHOULD item:A.5.25:log_fp_tag>>
_Why: Calibration_

<<TEXT>>

### 2. Trend / correlation tag where related events should be grouped

<<SHOULD item:A.5.25:log_trend_tag>>
_Why: 27002:5.25 — correlation_

<<TEXT>>
