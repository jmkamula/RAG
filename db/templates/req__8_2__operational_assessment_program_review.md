---
leaf_id: req:8.2:operational_assessment_program_review
control_ref: 8.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Operational Assessment Program Review

> Annual verification that planned assessments happened, significant-change triggers fired when they should have, results inform the treatment plan (freshness=365)

<!-- TABLE-COLUMNS leaf:req:8.2:operational_assessment_program_review -->
<!-- column: item:8.2:rev_date -->
<!-- column: item:8.2:rev_reviewer -->
<!-- column: item:8.2:rev_cadence_met -->
<!-- column: item:8.2:rev_triggers_fired -->
<!-- column: item:8.2:rev_treatment_handoff -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:8.2:operational_assessment_program_review -->
| Rev Date | Rev Reviewer | Rev Cadence Met | Rev Triggers Fired | Rev Treatment Handoff |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:8.2:operational_assessment_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:8.2:rev_date>>
_Why: Clause 8.2 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:8.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Risk Manager + ISMS Manager)

### Rev Cadence Met

<<MUST item:8.2:rev_cadence_met>>
_Why: Clause 8.2 — planned intervals_

> _Standard text:_ Cadence-met check — every scheduled assessment for each tier happened

### Rev Triggers Fired

<<MUST item:8.2:rev_triggers_fired>>
_Why: Clause 8.2 — significant changes_

> _Standard text:_ Trigger-firing sweep — significant changes during the year that should have triggered ad-hoc assessment all did

### Rev Treatment Handoff

<<MUST item:8.2:rev_treatment_handoff>>
_Why: Cross-clause coherence_

> _Standard text:_ Treatment handoff — every new risk found flows to 6.1.3 / 8.3 treatment

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:8.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
