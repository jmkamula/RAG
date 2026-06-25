---
leaf_id: req:A.5.22:review_schedule_register
control_ref: A.5.22
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 4
should_count: 2
table_shape: true
---

# Supplier Review Schedule Register

> A.5.22 expects the review activity to be regular — without a schedule, 'regular' becomes 'whenever someone remembers'. The schedule register is the calendar: per supplier, the planned cadence (proportional to tier), the last review date, the next review date, and the owner

<!-- TABLE-COLUMNS leaf:req:A.5.22:review_schedule_register -->
<!-- column: item:A.5.22:sch_cadence -->
<!-- column: item:A.5.22:sch_last_review -->
<!-- column: item:A.5.22:sch_next_review -->
<!-- column: item:A.5.22:sch_owner -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.22:review_schedule_register -->
| Sch Cadence | Sch Last Review | Sch Next Review | Sch Owner |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.22:review_schedule_register -->

## Column guidance — what to fill in

### Sch Cadence

<<MUST item:A.5.22:sch_cadence>>
_Why: 27002:5.22 — regularly_

> _Standard text:_ Cadence per supplier (proportional to tier — high-tier monthly, low-tier annually, etc.)

### Sch Last Review

<<MUST item:A.5.22:sch_last_review>>
_Why: Audit defensibility_

> _Standard text:_ Last review date per row

### Sch Next Review

<<MUST item:A.5.22:sch_next_review>>
_Why: Planning_

> _Standard text:_ Next review date per row

### Sch Owner

<<MUST item:A.5.22:sch_owner>>
_Why: Accountability_

> _Standard text:_ Named owner accountable for executing the review per row

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Sch Delta

<<SHOULD item:A.5.22:sch_delta>>
_Why: Operational discipline_

> _Standard text:_ Scheduled-vs-completed delta tracked (so missed reviews surface)

### Sch Tier Link

<<SHOULD item:A.5.22:sch_tier_link>>
_Why: Cross-control consistency_

> _Standard text:_ Linkage to A.5.19 supplier register tier (drives cadence)
