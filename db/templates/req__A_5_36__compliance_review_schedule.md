---
leaf_id: req:A.5.36:compliance_review_schedule
control_ref: A.5.36
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Compliance Review Schedule

<<DOC_CONTROL>>

> A.5.36 expects regular review — without a schedule, 'regular' becomes 'when something goes wrong'. The schedule register is the calendar: every in-scope policy/rule/standard, the planned cadence per item (proportional to risk and change rate), the last review date and the next review date

<!-- TABLE-COLUMNS leaf:req:A.5.36:compliance_review_schedule -->
<!-- column: item:A.5.36:sch_full_catalogue -->
<!-- column: item:A.5.36:sch_cadence -->
<!-- column: item:A.5.36:sch_method_planned -->
<!-- column: item:A.5.36:sch_last_review -->
<!-- column: item:A.5.36:sch_next_review -->
<!-- column: item:A.5.36:sch_owner -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you organize and track the review schedule for all your key policies, rules, and standards. It ensures you have a clear calendar for compliance reviews, tailored to your organization's needs.

## When to use it

Use this whenever you need to set up or update your compliance review calendar, especially if you want to make sure reviews happen regularly instead of only after issues arise. Update the register as needed to keep it current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element, plus additional time for each policy or standard you include. For a typical organization, initial setup may take 1-2 hours.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.36:compliance_review_schedule -->
| Sch Full Catalogue | Sch Cadence | Sch Method Planned | Sch Last Review | Sch Next Review | Sch Owner |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.36:compliance_review_schedule -->

## Column guidance — what to fill in

### Sch Full Catalogue

<<MUST item:A.5.36:sch_full_catalogue>>
_Why: 27002:5.36 — InfoSec policy + topic-specific policies + rules + standards_

> _Standard text:_ Full catalogue of in-scope items enumerated (InfoSec policy + every topic-specific policy + rules + applicable standards — completeness is the integrity check)

<<GUIDANCE>>

### Sch Cadence

<<MUST item:A.5.36:sch_cadence>>
_Why: 27002:5.36 — regularly_

> _Standard text:_ Cadence per item (annual baseline; tighter for high-risk or fast-changing items — e.g. acceptable use, access control)

<<GUIDANCE>>

### Sch Method Planned

<<MUST item:A.5.36:sch_method_planned>>
_Why: 27002:5.36 — reviewed_

> _Standard text:_ Planned method per item (which items use sampling vs audit vs automated check)

<<GUIDANCE>>

### Sch Last Review

<<MUST item:A.5.36:sch_last_review>>
_Why: Audit defensibility_

> _Standard text:_ Last review date per item

<<GUIDANCE>>

### Sch Next Review

<<MUST item:A.5.36:sch_next_review>>
_Why: Planning_

> _Standard text:_ Next review date per item

<<GUIDANCE>>

### Sch Owner

<<MUST item:A.5.36:sch_owner>>
_Why: Accountability_

> _Standard text:_ Named owner per item (reviewer accountable for the next cycle)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Sch Change Triggers

<<SHOULD item:A.5.36:sch_change_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc change triggers documented (policy edit, regulator action, incident affecting a policy area) — fires reviews outside the planned cadence

<<GUIDANCE>>

### Sch Delta

<<SHOULD item:A.5.36:sch_delta>>
_Why: Operational discipline_

> _Standard text:_ Scheduled-vs-completed delta tracked (so missed reviews surface)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
