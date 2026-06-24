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
---

# Periodic Redundancy Program Review

> Annual verification — critical-service list current, redundancy approach matches availability target, test attainment per service (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.8.14:rev_date>>
_Why: 27002:8.14 — periodic_

<<TEXT>>

## 2. Reviewer identity (Site Reliability + Infrastructure + business-service owners)

<<MUST item:A.8.14:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Critical-service list re-confirmed (new service in scope; retired service removed)

<<MUST item:A.8.14:rev_service_list>>
_Why: 27002:8.14 — availability_

<<TEXT>>

## 4. Failover-test attainment per service (cadence met; targets met)

<<MUST item:A.8.14:rev_test_attainment>>
_Why: 27002:8.14 — sufficient_

<<TEXT>>

## 5. Cross-check with A.5.30 BIA (any availability-tier change → redundancy approach re-evaluation)

<<MUST item:A.8.14:rev_bia_alignment>>
_Why: Cross-control coherence_

<<TEXT>>

## 6. Baseline / runbook updates published from findings

<<MUST item:A.8.14:rev_baseline_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.14:rev_next_date>>
_Why: Planning_

<<TEXT>>
