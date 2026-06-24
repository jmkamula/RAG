---
leaf_id: req:A.5.36:compliance_review_schedule
control_ref: A.5.36
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
---

# Compliance Review Schedule

> A.5.36 expects regular review — without a schedule, 'regular' becomes 'when something goes wrong'. The schedule register is the calendar: every in-scope policy/rule/standard, the planned cadence per item (proportional to risk and change rate), the last review date and the next review date

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Full catalogue of in-scope items enumerated (InfoSec policy + every topic-specific policy + rules + applicable standards — completeness is the integrity check)

<<MUST item:A.5.36:sch_full_catalogue>>
_Why: 27002:5.36 — InfoSec policy + topic-specific policies + rules + standards_

<<TEXT>>

## 2. Cadence per item (annual baseline; tighter for high-risk or fast-changing items — e.g. acceptable use, access control)

<<MUST item:A.5.36:sch_cadence>>
_Why: 27002:5.36 — regularly_

<<TEXT>>

## 3. Planned method per item (which items use sampling vs audit vs automated check)

<<MUST item:A.5.36:sch_method_planned>>
_Why: 27002:5.36 — reviewed_

<<TEXT>>

## 4. Last review date per item

<<MUST item:A.5.36:sch_last_review>>
_Why: Audit defensibility_

<<TEXT>>

## 5. Next review date per item

<<MUST item:A.5.36:sch_next_review>>
_Why: Planning_

<<TEXT>>

## 6. Named owner per item (reviewer accountable for the next cycle)

<<MUST item:A.5.36:sch_owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc change triggers documented (policy edit, regulator action, incident affecting a policy area) — fires reviews outside the planned cadence

<<SHOULD item:A.5.36:sch_change_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Scheduled-vs-completed delta tracked (so missed reviews surface)

<<SHOULD item:A.5.36:sch_delta>>
_Why: Operational discipline_

<<TEXT>>
