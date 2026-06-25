---
leaf_id: req:A.8.14:redundancy_program_review
control_ref: A.8.14
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Periodic Redundancy Program Review

> Annual verification — critical-service list current, redundancy approach matches availability target, test attainment per service (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.14:redundancy_program_review -->
<!-- column: item:A.8.14:rev_date -->
<!-- column: item:A.8.14:rev_reviewer -->
<!-- column: item:A.8.14:rev_service_list -->
<!-- column: item:A.8.14:rev_test_attainment -->
<!-- column: item:A.8.14:rev_bia_alignment -->
<!-- column: item:A.8.14:rev_baseline_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.14:redundancy_program_review -->
| Rev Date | Rev Reviewer | Rev Service List | Rev Test Attainment | Rev Bia Alignment | Rev Baseline Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.14:redundancy_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.14:rev_date>>
_Why: 27002:8.14 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.8.14:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Site Reliability + Infrastructure + business-service owners)

### Rev Service List

<<MUST item:A.8.14:rev_service_list>>
_Why: 27002:8.14 — availability_

> _Standard text:_ Critical-service list re-confirmed (new service in scope; retired service removed)

### Rev Test Attainment

<<MUST item:A.8.14:rev_test_attainment>>
_Why: 27002:8.14 — sufficient_

> _Standard text:_ Failover-test attainment per service (cadence met; targets met)

### Rev Bia Alignment

<<MUST item:A.8.14:rev_bia_alignment>>
_Why: Cross-control coherence_

> _Standard text:_ Cross-check with A.5.30 BIA (any availability-tier change → redundancy approach re-evaluation)

### Rev Baseline Update

<<MUST item:A.8.14:rev_baseline_update>>
_Why: Closes the loop_

> _Standard text:_ Baseline / runbook updates published from findings

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.14:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
