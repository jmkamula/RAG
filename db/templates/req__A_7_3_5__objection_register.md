---
leaf_id: req:A.7.3.5:objection_register
control_ref: A.7.3.5
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Objection Event Register

<<DOC_CONTROL>>

> Per-objection-event row — audit trail of each objection with type, resolution, and downstream propagation. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.3.5:objection_register -->
<!-- column: item:A.7.3.5:reg_event_id -->
<!-- column: item:A.7.3.5:reg_subject_id -->
<!-- column: item:A.7.3.5:reg_objection_type -->
<!-- column: item:A.7.3.5:reg_resolution -->
<!-- column: item:A.7.3.5:reg_propagation_status -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of every privacy objection you receive, including details about the type, how it was resolved, and any follow-up actions. It supports your compliance with privacy standards and provides a reliable audit trail.

## When to use it

Use this register whenever your organization receives a privacy objection that matches specific criteria, and update it at least once a year to ensure your records stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required detail for each objection event; setting up the register from scratch for a single event will likely take around an hour, with more time needed as you add more events.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.5:objection_register -->
| Reg Event Id | Reg Subject Id | Reg Objection Type | Reg Resolution | Reg Propagation Status |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.5:objection_register -->

## Column guidance — what to fill in

### Reg Event Id

<<MUST item:A.7.3.5:reg_event_id>>
_Why: Audit trail_

> _Standard text:_ Unique event identifier per row

<<GUIDANCE>>

### Reg Subject Id

<<MUST item:A.7.3.5:reg_subject_id>>
_Why: Traceability_

> _Standard text:_ Subject identifier per row

<<GUIDANCE>>

### Reg Objection Type

<<MUST item:A.7.3.5:reg_objection_type>>
_Why: GDPR Art.21_

> _Standard text:_ Objection type per row (absolute — marketing/stats; balancing — legitimate interests / public interest)

<<GUIDANCE>>

### Reg Resolution

<<MUST item:A.7.3.5:reg_resolution>>
_Why: Art.21.1 — compelling grounds_

> _Standard text:_ Resolution per row (processing halted / balancing test rejection with justification)

<<GUIDANCE>>

### Reg Propagation Status

<<MUST item:A.7.3.5:reg_propagation_status>>
_Why: Effectiveness_

> _Standard text:_ Downstream propagation status

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Legal Review

<<SHOULD item:A.7.3.5:reg_legal_review>>
_Why: Defensibility_

> _Standard text:_ Legal counsel signoff for balancing-test rejections

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
