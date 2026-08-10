---
leaf_id: req:A.6.8:event_report_register
control_ref: A.6.8
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Event Report Register

<<DOC_CONTROL>>

> The operational catalogue of every event report received. Each row: report identifier, channel used, reporter identity (or 'anonymous'), report timestamp, content summary, triage outcome (link to A.5.25 triage record), closure. Drives the 'show me the reporting program is actually used and acted on' audit

<!-- TABLE-COLUMNS leaf:req:A.6.8:event_report_register -->
<!-- column: item:A.6.8:reg_report_id -->
<!-- column: item:A.6.8:reg_channel -->
<!-- column: item:A.6.8:reg_reporter -->
<!-- column: item:A.6.8:reg_report_timestamp -->
<!-- column: item:A.6.8:reg_summary -->
<!-- column: item:A.6.8:reg_triage_outcome -->
<!-- column: item:A.6.8:reg_closure_date -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of every event report your organization receives, showing how each report was handled from start to finish. It’s useful for demonstrating that your reporting process is active and effective during audits.

## When to use it

Use this register whenever your environment receives an event report, and update it as needed to reflect new reports or changes. It should always be maintained to stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Setting up the register from scratch may take about 1.5 to 2 hours for the initial structure and first entry, with each new report row taking around 10-15 minutes to complete.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.6.8:event_report_register -->
| Reg Report Id | Reg Channel | Reg Reporter | Reg Report Timestamp | Reg Summary | Reg Triage Outcome | Reg Closure Date |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.6.8:event_report_register -->

## Column guidance — what to fill in

### Reg Report Id

<<MUST item:A.6.8:reg_report_id>>
_Why: Cross-control coherence_

> _Standard text:_ Per-row report identifier (links to A.5.25 triage record where the report was triaged)

<<GUIDANCE>>

### Reg Channel

<<MUST item:A.6.8:reg_channel>>
_Why: 27002:6.8 — channels effectiveness_

> _Standard text:_ Per-row channel used (drives channel-mix analysis — are some channels under-used?)

<<GUIDANCE>>

### Reg Reporter

<<MUST item:A.6.8:reg_reporter>>
_Why: 27002:6.8 — mechanism_

> _Standard text:_ Per-row reporter identity or 'anonymous' (anonymous reports are first-class; non-attribution is the point of the option)

<<GUIDANCE>>

### Reg Report Timestamp

<<MUST item:A.6.8:reg_report_timestamp>>
_Why: 27002:6.8 — timely_

> _Standard text:_ Per-row report timestamp (drives timeliness analysis — gap between event time and report time)

<<GUIDANCE>>

### Reg Summary

<<MUST item:A.6.8:reg_summary>>
_Why: Operational discipline_

> _Standard text:_ Per-row content summary (one-line headline + classification — observed / suspected / near-miss)

<<GUIDANCE>>

### Reg Triage Outcome

<<MUST item:A.6.8:reg_triage_outcome>>
_Why: 27002:6.8 + A.5.25_

> _Standard text:_ Per-row triage outcome (incident-confirmed → A.5.26 register; false-positive-closed; near-miss-filed-for-trend; pending-investigation)

<<GUIDANCE>>

### Reg Closure Date

<<MUST item:A.6.8:reg_closure_date>>
_Why: Closes the loop_

> _Standard text:_ Per-row closure date (every report reaches a closed state, no open-forever)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Ack Sent

<<SHOULD item:A.6.8:reg_ack_sent>>
_Why: Reporting culture_

> _Standard text:_ Per-row acknowledgment-sent-to-reporter flag (where reporter known + non-anonymous)

<<GUIDANCE>>

### Reg Lessons Feed

<<SHOULD item:A.6.8:reg_lessons_feed>>
_Why: Continual improvement_

> _Standard text:_ Per-row lessons-feed flag where the report surfaced a control gap (feeds back to A.6.3 awareness curriculum or relevant control owner)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
