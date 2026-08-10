---
leaf_id: req:A.5.30:ict_program_review
control_ref: A.5.30
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Periodic ICT Readiness Program Review

<<DOC_CONTROL>>

> The ICT continuity plan creates value only if RTO/RPO commitments actually hold under test — services that fall out of compliance, dependencies that have shifted, backup restores that fail, test scenarios that have gone stale all signal the plan is drifting. The review captures the planned-interval check: RTO/RPO compliance audit, dependency-currency check, restore-success-rate analysis, scenario-coverage audit, and resulting plan adjustments. Cadence tightened to 180 days — ICT landscape shifts continuously

<!-- TABLE-COLUMNS leaf:req:A.5.30:ict_program_review -->
<!-- column: item:A.5.30:rev_date -->
<!-- column: item:A.5.30:rev_reviewer -->
<!-- column: item:A.5.30:rev_rto_compliance -->
<!-- column: item:A.5.30:rev_dependency_check -->
<!-- column: item:A.5.30:rev_restore_success -->
<!-- column: item:A.5.30:rev_scenario_coverage -->
<!-- column: item:A.5.30:rev_actions -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you systematically review your ICT continuity plan, ensuring your recovery objectives and backup processes are still effective and up to date. It highlights any gaps or changes needed to keep your plan reliable.

## When to use it

Use this template every six months to check your ICT readiness, as your environment and dependencies may change over time. It's designed for regular, scheduled reviews to keep your continuity plan in line with current needs.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours completing this review from scratch, as you'll need to address several required elements and gather up-to-date information for each section.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.30:ict_program_review -->
| Rev Date | Rev Reviewer | Rev Rto Compliance | Rev Dependency Check | Rev Restore Success | Rev Scenario Coverage | Rev Actions |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.30:ict_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.30:rev_date>>
_Why: 27002:5.30 — periodic_

> _Standard text:_ Review date within the planned 180-day interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.5.30:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (CTO/IT-ops head + BCP-program owner + InfoSec lead jointly; CFO sign-off where critical-service RTO has financial impact)

<<GUIDANCE>>

### Rev Rto Compliance

<<MUST item:A.5.30:rev_rto_compliance>>
_Why: 27002:5.30 — objectives verification_

> _Standard text:_ RTO/RPO compliance audit (sample of services re-tested; gap to target per service; root cause per gap)

<<GUIDANCE>>

### Rev Dependency Check

<<MUST item:A.5.30:rev_dependency_check>>
_Why: 27002:5.30 — readiness coordination_

> _Standard text:_ Dependency-currency check (sample of services where dependency map re-validated against current reality; shifts flagged for plan update)

<<GUIDANCE>>

### Rev Restore Success

<<MUST item:A.5.30:rev_restore_success>>
_Why: 27002:5.30 — backup verification_

> _Standard text:_ Restore-success-rate analysis (last N restores attempted; success rate; failed restores investigated)

<<GUIDANCE>>

### Rev Scenario Coverage

<<MUST item:A.5.30:rev_scenario_coverage>>
_Why: 27002:5.30 + cross-link to [[A.5.29]]_

> _Standard text:_ Scenario-coverage audit (which scenarios from A.5.29 register actually tested via real recovery; which still untested; remediation plan per gap)

<<GUIDANCE>>

### Rev Actions

<<MUST item:A.5.30:rev_actions>>
_Why: 27002:5.30 — plan adjustments_

> _Standard text:_ Action items captured (e.g. add new service, tighten RTO for service that consistently misses, retire stale scenario, refresh test schedule)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Cloud Posture

<<SHOULD item:A.5.30:rev_cloud_posture>>
_Why: Cross-link to [[A.5.23]]_

> _Standard text:_ Cloud-provider posture noted (where ICT readiness depends on hyperscaler features — AZ failover, region replication; their SLA changes affect ours)

<<GUIDANCE>>

### Rev Next Date

<<SHOULD item:A.5.30:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated (within 180d of this review)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
