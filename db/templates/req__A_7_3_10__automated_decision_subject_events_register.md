---
leaf_id: req:A.7.3.10:automated_decision_subject_events_register
control_ref: A.7.3.10
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Automated Decision Subject Events Register

<<DOC_CONTROL>>

> Per-subject-event row — objections, requests for human intervention, contests. Distinct from the Art.22 system register (which tracks the systems). Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.3.10:automated_decision_subject_events_register -->
<!-- column: item:A.7.3.10:reg_event_id -->
<!-- column: item:A.7.3.10:reg_subject_id -->
<!-- column: item:A.7.3.10:reg_event_type -->
<!-- column: item:A.7.3.10:reg_system -->
<!-- column: item:A.7.3.10:reg_resolution -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of individual objections, requests for human review, and challenges related to automated decisions, making it easier to demonstrate compliance with privacy standards.

## When to use it

Use this register whenever someone objects to, requests human intervention in, or contests an automated decision about them. Review and update the register at least once a year to keep it current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes to set up the required elements for the first subject event, with additional time needed for each new entry as events occur.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.10:automated_decision_subject_events_register -->
| Reg Event Id | Reg Subject Id | Reg Event Type | Reg System | Reg Resolution |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.10:automated_decision_subject_events_register -->

## Column guidance — what to fill in

### Reg Event Id

<<MUST item:A.7.3.10:reg_event_id>>
_Why: Audit trail_

> _Standard text:_ Unique event identifier per row

<<GUIDANCE>>

### Reg Subject Id

<<MUST item:A.7.3.10:reg_subject_id>>
_Why: Traceability_

> _Standard text:_ Subject identifier per row

<<GUIDANCE>>

### Reg Event Type

<<MUST item:A.7.3.10:reg_event_type>>
_Why: Art.22.3_

> _Standard text:_ Event type per row (objection / human-intervention request / contest / expression-of-view)

<<GUIDANCE>>

### Reg System

<<MUST item:A.7.3.10:reg_system>>
_Why: Traceability to Art.22 register_

> _Standard text:_ Automated system involved per row

<<GUIDANCE>>

### Reg Resolution

<<MUST item:A.7.3.10:reg_resolution>>
_Why: Art.22.3_

> _Standard text:_ Resolution per row (human-reviewed decision / procedure applied / dismissed with reason)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Response Time

<<SHOULD item:A.7.3.10:reg_response_time>>
_Why: Effectiveness_

> _Standard text:_ Response time per row

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
