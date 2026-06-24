---
leaf_id: req:A.5.22:review_schedule_register
control_ref: A.5.22
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 4
should_count: 2
---

# Supplier Review Schedule Register

> A.5.22 expects the review activity to be regular — without a schedule, 'regular' becomes 'whenever someone remembers'. The schedule register is the calendar: per supplier, the planned cadence (proportional to tier), the last review date, the next review date, and the owner

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Cadence per supplier (proportional to tier — high-tier monthly, low-tier annually, etc.)

<<MUST item:A.5.22:sch_cadence>>
_Why: 27002:5.22 — regularly_

<<TEXT>>

## 2. Last review date per row

<<MUST item:A.5.22:sch_last_review>>
_Why: Audit defensibility_

<<TEXT>>

## 3. Next review date per row

<<MUST item:A.5.22:sch_next_review>>
_Why: Planning_

<<TEXT>>

## 4. Named owner accountable for executing the review per row

<<MUST item:A.5.22:sch_owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Scheduled-vs-completed delta tracked (so missed reviews surface)

<<SHOULD item:A.5.22:sch_delta>>
_Why: Operational discipline_

<<TEXT>>

### 2. Linkage to A.5.19 supplier register tier (drives cadence)

<<SHOULD item:A.5.22:sch_tier_link>>
_Why: Cross-control consistency_

<<TEXT>>
