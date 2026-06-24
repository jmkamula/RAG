---
leaf_id: req:A.6.8:event_report_register
control_ref: A.6.8
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
---

# Event Report Register

> The operational catalogue of every event report received. Each row: report identifier, channel used, reporter identity (or 'anonymous'), report timestamp, content summary, triage outcome (link to A.5.25 triage record), closure. Drives the 'show me the reporting program is actually used and acted on' audit

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row report identifier (links to A.5.25 triage record where the report was triaged)

<<MUST item:A.6.8:reg_report_id>>
_Why: Cross-control coherence_

<<TEXT>>

## 2. Per-row channel used (drives channel-mix analysis — are some channels under-used?)

<<MUST item:A.6.8:reg_channel>>
_Why: 27002:6.8 — channels effectiveness_

<<TEXT>>

## 3. Per-row reporter identity or 'anonymous' (anonymous reports are first-class; non-attribution is the point of the option)

<<MUST item:A.6.8:reg_reporter>>
_Why: 27002:6.8 — mechanism_

<<TEXT>>

## 4. Per-row report timestamp (drives timeliness analysis — gap between event time and report time)

<<MUST item:A.6.8:reg_report_timestamp>>
_Why: 27002:6.8 — timely_

<<TEXT>>

## 5. Per-row content summary (one-line headline + classification — observed / suspected / near-miss)

<<MUST item:A.6.8:reg_summary>>
_Why: Operational discipline_

<<TEXT>>

## 6. Per-row triage outcome (incident-confirmed → A.5.26 register; false-positive-closed; near-miss-filed-for-trend; pending-investigation)

<<MUST item:A.6.8:reg_triage_outcome>>
_Why: 27002:6.8 + A.5.25_

<<TEXT>>

## 7. Per-row closure date (every report reaches a closed state, no open-forever)

<<MUST item:A.6.8:reg_closure_date>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row acknowledgment-sent-to-reporter flag (where reporter known + non-anonymous)

<<SHOULD item:A.6.8:reg_ack_sent>>
_Why: Reporting culture_

<<TEXT>>

### 2. Per-row lessons-feed flag where the report surfaced a control gap (feeds back to A.6.3 awareness curriculum or relevant control owner)

<<SHOULD item:A.6.8:reg_lessons_feed>>
_Why: Continual improvement_

<<TEXT>>
