---
leaf_id: req:Art.39:dpo_tasks_program_review
control_ref: Art.39
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# DPO Tasks Program Review

> Annual verification — DPO actually performing each Art.39.1 task, risk-based priorities being honoured, awareness contribution effective (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.39:dpo_tasks_program_review -->
<!-- column: item:Art.39:rev_date -->
<!-- column: item:Art.39:rev_reviewer -->
<!-- column: item:Art.39:rev_task_coverage -->
<!-- column: item:Art.39:rev_risk_prioritisation_check -->
<!-- column: item:Art.39:rev_quality_signals -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.39:dpo_tasks_program_review -->
| Rev Date | Rev Reviewer | Rev Task Coverage | Rev Risk Prioritisation Check | Rev Quality Signals |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.39:dpo_tasks_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.39:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.39:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (executive sponsor)

### Rev Task Coverage

<<MUST item:Art.39:rev_task_coverage>>
_Why: Art.39.1_

> _Standard text:_ Task coverage audit — every Art.39.1 task has corresponding activity-register entries

### Rev Risk Prioritisation Check

<<MUST item:Art.39:rev_risk_prioritisation_check>>
_Why: Art.39.2_

> _Standard text:_ Risk prioritisation check — DPO attention skewed toward higher-risk processing

### Rev Quality Signals

<<MUST item:Art.39:rev_quality_signals>>
_Why: Effectiveness_

> _Standard text:_ Quality signals — incident-trend reduction, DPIA-handling improvement, SA-interaction outcomes

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.39:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
