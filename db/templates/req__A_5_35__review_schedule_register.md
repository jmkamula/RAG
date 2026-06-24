---
leaf_id: req:A.5.35:review_schedule_register
control_ref: A.5.35
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
---

# Independent Review Schedule Register

> A.5.35 expects reviews at planned intervals — without a schedule, 'planned' becomes 'when leadership asks for it'. The schedule register is the calendar of upcoming independent reviews: which scope areas, what cadence, which reviewer or selection mechanism, last review date, next review date

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Planned cadence stated (annual is the doctrine baseline; risk-tier or scope-area may drive tighter cadences for hot domains)

<<MUST item:A.5.35:sch_cadence>>
_Why: 27002:5.35 — planned intervals_

<<TEXT>>

## 2. Scope areas planned (the ISMS may be reviewed end-to-end annually OR sliced across cycles — both acceptable; the slicing is documented)

<<MUST item:A.5.35:sch_scope_areas>>
_Why: 27002:5.35 — including people, processes and technologies_

<<TEXT>>

## 3. Reviewer selection mechanism (external rotation, internal independence criteria, audit-firm framework agreement) — drives the independence guarantee

<<MUST item:A.5.35:sch_reviewer_selection>>
_Why: 27002:5.35 — reviewed independently_

<<TEXT>>

## 4. Last review date recorded (proves the schedule is anchored in reality, not aspirational)

<<MUST item:A.5.35:sch_last_review>>
_Why: Audit defensibility_

<<TEXT>>

## 5. Next review date stated (per scope area where sliced)

<<MUST item:A.5.35:sch_next_review>>
_Why: Planning_

<<TEXT>>

## 6. Named owner accountable for executing the schedule (typically CISO / InfoSec lead with management sponsor)

<<MUST item:A.5.35:sch_owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc change triggers documented (M&A, major architectural shift, regulatory upheaval, major breach) — fires reviews outside the planned cadence

<<SHOULD item:A.5.35:sch_change_triggers>>
_Why: 27002:5.35 — on significant change_

<<TEXT>>

### 2. Scheduled-vs-completed delta tracked (so missed reviews surface)

<<SHOULD item:A.5.35:sch_delta>>
_Why: Operational discipline_

<<TEXT>>
