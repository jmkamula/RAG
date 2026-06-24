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
---

# Periodic ICT Readiness Program Review

> The ICT continuity plan creates value only if RTO/RPO commitments actually hold under test — services that fall out of compliance, dependencies that have shifted, backup restores that fail, test scenarios that have gone stale all signal the plan is drifting. The review captures the planned-interval check: RTO/RPO compliance audit, dependency-currency check, restore-success-rate analysis, scenario-coverage audit, and resulting plan adjustments. Cadence tightened to 180 days — ICT landscape shifts continuously

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned 180-day interval

<<MUST item:A.5.30:rev_date>>
_Why: 27002:5.30 — periodic_

<<TEXT>>

## 2. Reviewer identity (CTO/IT-ops head + BCP-program owner + InfoSec lead jointly; CFO sign-off where critical-service RTO has financial impact)

<<MUST item:A.5.30:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. RTO/RPO compliance audit (sample of services re-tested; gap to target per service; root cause per gap)

<<MUST item:A.5.30:rev_rto_compliance>>
_Why: 27002:5.30 — objectives verification_

<<TEXT>>

## 4. Dependency-currency check (sample of services where dependency map re-validated against current reality; shifts flagged for plan update)

<<MUST item:A.5.30:rev_dependency_check>>
_Why: 27002:5.30 — readiness coordination_

<<TEXT>>

## 5. Restore-success-rate analysis (last N restores attempted; success rate; failed restores investigated)

<<MUST item:A.5.30:rev_restore_success>>
_Why: 27002:5.30 — backup verification_

<<TEXT>>

## 6. Scenario-coverage audit (which scenarios from A.5.29 register actually tested via real recovery; which still untested; remediation plan per gap)

<<MUST item:A.5.30:rev_scenario_coverage>>
_Why: 27002:5.30 + cross-link to [[A.5.29]]_

<<TEXT>>

## 7. Action items captured (e.g. add new service, tighten RTO for service that consistently misses, retire stale scenario, refresh test schedule)

<<MUST item:A.5.30:rev_actions>>
_Why: 27002:5.30 — plan adjustments_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Cloud-provider posture noted (where ICT readiness depends on hyperscaler features — AZ failover, region replication; their SLA changes affect ours)

<<SHOULD item:A.5.30:rev_cloud_posture>>
_Why: Cross-link to [[A.5.23]]_

<<TEXT>>

### 2. Next planned review date stated (within 180d of this review)

<<SHOULD item:A.5.30:rev_next_date>>
_Why: Planning_

<<TEXT>>
