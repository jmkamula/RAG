---
leaf_id: req:6.1.3:risk_treatment_program_review
control_ref: 6.1.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Risk Treatment Program Review

> Annual verification that the plan is being executed, the SoA is current, residual risks remain accepted (freshness=365)

<!-- TABLE-COLUMNS leaf:req:6.1.3:risk_treatment_program_review -->
<!-- column: item:6.1.3:rev_date -->
<!-- column: item:6.1.3:rev_reviewer -->
<!-- column: item:6.1.3:rev_plan_progress -->
<!-- column: item:6.1.3:rev_soa_currency -->
<!-- column: item:6.1.3:rev_residual_reaffirm -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:6.1.3:risk_treatment_program_review -->
| Rev Date | Rev Reviewer | Rev Plan Progress | Rev Soa Currency | Rev Residual Reaffirm |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:6.1.3:risk_treatment_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:6.1.3:rev_date>>
_Why: Clause 6.1.3 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:6.1.3:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Risk Manager + ISMS Manager + risk owners as needed)

### Rev Plan Progress

<<MUST item:6.1.3:rev_plan_progress>>
_Why: 8.3 link_

> _Standard text:_ Plan progress check — every treatment item status updated

### Rev Soa Currency

<<MUST item:6.1.3:rev_soa_currency>>
_Why: Cross-leaf coherence_

> _Standard text:_ SoA currency check — still matches treatment plan + Annex A version

### Rev Residual Reaffirm

<<MUST item:6.1.3:rev_residual_reaffirm>>
_Why: Clause 6.1.3f_

> _Standard text:_ Residual risks re-affirmed by owners (or re-treatment triggered)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:6.1.3:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
