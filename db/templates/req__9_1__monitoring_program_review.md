---
leaf_id: req:9.1:monitoring_program_review
control_ref: 9.1
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Monitoring Program Review

> Annual verification that measurements are flowing per the procedure, thresholds still discriminate, results actually feed 9.3 management review (freshness=365)

<!-- TABLE-COLUMNS leaf:req:9.1:monitoring_program_review -->
<!-- column: item:9.1:rev_date -->
<!-- column: item:9.1:rev_reviewer -->
<!-- column: item:9.1:rev_flow_check -->
<!-- column: item:9.1:rev_threshold_recalibration -->
<!-- column: item:9.1:rev_mgmt_review_handoff -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:9.1:monitoring_program_review -->
| Rev Date | Rev Reviewer | Rev Flow Check | Rev Threshold Recalibration | Rev Mgmt Review Handoff |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:9.1:monitoring_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:9.1:rev_date>>
_Why: Clause 9.1 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:9.1:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + KPI lead)

### Rev Flow Check

<<MUST item:9.1:rev_flow_check>>
_Why: Effectiveness_

> _Standard text:_ Flow check — every metric in the procedure's catalog has values flowing into the record

### Rev Threshold Recalibration

<<MUST item:9.1:rev_threshold_recalibration>>
_Why: Validity_

> _Standard text:_ Threshold recalibration — targets reviewed for continued relevance and stretch

### Rev Mgmt Review Handoff

<<MUST item:9.1:rev_mgmt_review_handoff>>
_Why: Clause 9.3.2c_

> _Standard text:_ Management review handoff — last cycle's measurement results actually surfaced in 9.3 minutes

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:9.1:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
