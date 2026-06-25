---
leaf_id: req:9.3:management_review_program_review
control_ref: 9.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Management Review Program Review

> Annual verification that reviews happened on cadence, all required inputs were considered, decisions are being tracked to closure (freshness=365)

<!-- TABLE-COLUMNS leaf:req:9.3:management_review_program_review -->
<!-- column: item:9.3:rev_date -->
<!-- column: item:9.3:rev_reviewer -->
<!-- column: item:9.3:rev_cadence_met -->
<!-- column: item:9.3:rev_inputs_completeness -->
<!-- column: item:9.3:rev_action_closure -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:9.3:management_review_program_review -->
| Rev Date | Rev Reviewer | Rev Cadence Met | Rev Inputs Completeness | Rev Action Closure |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:9.3:management_review_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:9.3:rev_date>>
_Why: Clause 9.3 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:9.3:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager)

### Rev Cadence Met

<<MUST item:9.3:rev_cadence_met>>
_Why: Clause 9.3.1_

> _Standard text:_ Cadence check — every planned review happened (or was rescheduled with rationale)

### Rev Inputs Completeness

<<MUST item:9.3:rev_inputs_completeness>>
_Why: Clause 9.3.2_

> _Standard text:_ Inputs-completeness check — every 9.3.2 a-g input was present in each review's minutes

### Rev Action Closure

<<MUST item:9.3:rev_action_closure>>
_Why: Clause 9.3.3_

> _Standard text:_ Action-closure check — decisions from prior reviews tracked to 10.1/10.2 closure

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:9.3:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
