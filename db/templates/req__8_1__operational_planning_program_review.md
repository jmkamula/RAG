---
leaf_id: req:8.1:operational_planning_program_review
control_ref: 8.1
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Operational Planning Program Review

> Annual verification that processes ran per the procedure, the register is current, outsourced processes are being controlled (freshness=365)

<!-- TABLE-COLUMNS leaf:req:8.1:operational_planning_program_review -->
<!-- column: item:8.1:rev_date -->
<!-- column: item:8.1:rev_reviewer -->
<!-- column: item:8.1:rev_execution_completeness -->
<!-- column: item:8.1:rev_outsourced_oversight -->
<!-- column: item:8.1:rev_c6_handoff -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:8.1:operational_planning_program_review -->
| Rev Date | Rev Reviewer | Rev Execution Completeness | Rev Outsourced Oversight | Rev C6 Handoff |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:8.1:operational_planning_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:8.1:rev_date>>
_Why: Clause 8.1 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:8.1:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + ops lead)

### Rev Execution Completeness

<<MUST item:8.1:rev_execution_completeness>>
_Why: Effectiveness_

> _Standard text:_ Execution completeness check — every scheduled process iteration logged

### Rev Outsourced Oversight

<<MUST item:8.1:rev_outsourced_oversight>>
_Why: Clause 8.1 — outsourced_

> _Standard text:_ Outsourced oversight check — every outsourced process has current supplier-side evidence (A.5.19/A.5.20)

### Rev C6 Handoff

<<MUST item:8.1:rev_c6_handoff>>
_Why: Cross-clause coherence_

> _Standard text:_ Clause 6 handoff check — every 6.1.1 planned action reached operational implementation OR was deferred

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:8.1:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
