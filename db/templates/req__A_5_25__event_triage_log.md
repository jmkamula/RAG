---
leaf_id: req:A.5.25:event_triage_log
control_ref: A.5.25
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Security Event Triage Log

<<DOC_CONTROL>>

> A.5.25 expects records of events, incidents and weaknesses to be maintained and accessible to competent personnel. The triage log is the live source of truth — every triaged event, its classification, decision and owner — feeding the periodic review and the per-event triage-decision records

<!-- TABLE-COLUMNS leaf:req:A.5.25:event_triage_log -->
<!-- column: item:A.5.25:log_event_id -->
<!-- column: item:A.5.25:log_source -->
<!-- column: item:A.5.25:log_classification -->
<!-- column: item:A.5.25:log_decision -->
<!-- column: item:A.5.25:log_owner -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of all security events, incidents, and weaknesses, including how each was handled and by whom. It supports compliance with ISO 27001 by making your triage process transparent and auditable.

## When to use it

Use this log whenever a security event, incident, or weakness occurs in your environment, and update it as needed to reflect new events or changes. It should be maintained continuously as your main source of truth.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Setting up the log for the first time typically takes about 1 to 2 hours, depending on the number of events you need to record. Ongoing updates are quick, usually 10–15 minutes per new event.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.25:event_triage_log -->
| Log Event Id | Log Source | Log Classification | Log Decision | Log Owner |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.25:event_triage_log -->

## Column guidance — what to fill in

### Log Event Id

<<MUST item:A.5.25:log_event_id>>
_Why: 27002:5.25 — records of events_

> _Standard text:_ Each event captured with a unique identifier and detection timestamp

<<GUIDANCE>>

### Log Source

<<MUST item:A.5.25:log_source>>
_Why: 27002:5.25 — events_

> _Standard text:_ Detection source per row (which monitoring system / user / third party reported it)

<<GUIDANCE>>

### Log Classification

<<MUST item:A.5.25:log_classification>>
_Why: 27002:5.25 — categorised_

> _Standard text:_ Classification per row (event / near-miss / incident / false positive) with severity

<<GUIDANCE>>

### Log Decision

<<MUST item:A.5.25:log_decision>>
_Why: 27002:5.25 — decision_

> _Standard text:_ Triage decision per row (close as false positive / file as near-miss / escalate to A.5.26)

<<GUIDANCE>>

### Log Owner

<<MUST item:A.5.25:log_owner>>
_Why: Accountability_

> _Standard text:_ Named triager per row (accountability)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Log Fp Tag

<<SHOULD item:A.5.25:log_fp_tag>>
_Why: Calibration_

> _Standard text:_ False-positive flag tracked separately (drives calibration in the program review)

<<GUIDANCE>>

### Log Trend Tag

<<SHOULD item:A.5.25:log_trend_tag>>
_Why: 27002:5.25 — correlation_

> _Standard text:_ Trend / correlation tag where related events should be grouped

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
