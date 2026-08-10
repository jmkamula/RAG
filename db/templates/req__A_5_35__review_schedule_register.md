---
leaf_id: req:A.5.35:review_schedule_register
control_ref: A.5.35
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Independent Review Schedule Register

<<DOC_CONTROL>>

> A.5.35 expects reviews at planned intervals — without a schedule, 'planned' becomes 'when leadership asks for it'. The schedule register is the calendar of upcoming independent reviews: which scope areas, what cadence, which reviewer or selection mechanism, last review date, next review date

<!-- TABLE-COLUMNS leaf:req:A.5.35:review_schedule_register -->
<!-- column: item:A.5.35:sch_cadence -->
<!-- column: item:A.5.35:sch_scope_areas -->
<!-- column: item:A.5.35:sch_reviewer_selection -->
<!-- column: item:A.5.35:sch_last_review -->
<!-- column: item:A.5.35:sch_next_review -->
<!-- column: item:A.5.35:sch_owner -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you organize and track all your independent review activities, making it easy to see what needs to be reviewed, when, and by whom. It ensures your reviews are planned and documented, not just reactive.

## When to use it

Use this register whenever you need to schedule or update independent reviews for your information security program. Review and update it as needed to keep your review schedule current and compliant.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes setting up the initial register, plus additional time for each review area you add. Updates are quick once the structure is in place.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.35:review_schedule_register -->
| Sch Cadence | Sch Scope Areas | Sch Reviewer Selection | Sch Last Review | Sch Next Review | Sch Owner |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.35:review_schedule_register -->

## Column guidance — what to fill in

### Sch Cadence

<<MUST item:A.5.35:sch_cadence>>
_Why: 27002:5.35 — planned intervals_

> _Standard text:_ Planned cadence stated (annual is the doctrine baseline; risk-tier or scope-area may drive tighter cadences for hot domains)

<<GUIDANCE>>

### Sch Scope Areas

<<MUST item:A.5.35:sch_scope_areas>>
_Why: 27002:5.35 — including people, processes and technologies_

> _Standard text:_ Scope areas planned (the ISMS may be reviewed end-to-end annually OR sliced across cycles — both acceptable; the slicing is documented)

<<GUIDANCE>>

### Sch Reviewer Selection

<<MUST item:A.5.35:sch_reviewer_selection>>
_Why: 27002:5.35 — reviewed independently_

> _Standard text:_ Reviewer selection mechanism (external rotation, internal independence criteria, audit-firm framework agreement) — drives the independence guarantee

<<GUIDANCE>>

### Sch Last Review

<<MUST item:A.5.35:sch_last_review>>
_Why: Audit defensibility_

> _Standard text:_ Last review date recorded (proves the schedule is anchored in reality, not aspirational)

<<GUIDANCE>>

### Sch Next Review

<<MUST item:A.5.35:sch_next_review>>
_Why: Planning_

> _Standard text:_ Next review date stated (per scope area where sliced)

<<GUIDANCE>>

### Sch Owner

<<MUST item:A.5.35:sch_owner>>
_Why: Accountability_

> _Standard text:_ Named owner accountable for executing the schedule (typically CISO / InfoSec lead with management sponsor)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Sch Change Triggers

<<SHOULD item:A.5.35:sch_change_triggers>>
_Why: 27002:5.35 — on significant change_

> _Standard text:_ Ad-hoc change triggers documented (M&A, major architectural shift, regulatory upheaval, major breach) — fires reviews outside the planned cadence

<<GUIDANCE>>

### Sch Delta

<<SHOULD item:A.5.35:sch_delta>>
_Why: Operational discipline_

> _Standard text:_ Scheduled-vs-completed delta tracked (so missed reviews surface)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
