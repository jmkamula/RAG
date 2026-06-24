---
leaf_id: req:A.5.29:continuity_program_review
control_ref: A.5.29
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 7
should_count: 2
---

# Periodic Continuity-Security Program Review

> The continuity plan creates value only when actually exercised — scenarios that go stale, fallbacks that wouldn't actually work, communication paths that have changed all signal the plan is drifting. The review captures the planned-interval check: scenario-currency audit, test-result analysis, fallback-validity check, real-disruption divergence analysis, and resulting plan adjustments. Cadence tightened to 180 days — disruption landscape shifts

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned 180-day interval

<<MUST item:A.5.29:rev_date>>
_Why: 27002:5.29 — periodic_

<<TEXT>>

## 2. Reviewer identity (CISO + BCP-program owner + Legal where regulatory comms scope; supplier-management lead where supplier-dep scenarios in scope)

<<MUST item:A.5.29:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Scenario-currency audit (each scenario in the register re-validated: still plausible? still relevant? new scenarios that should be added?)

<<MUST item:A.5.29:rev_scenario_currency>>
_Why: 27002:5.29 — scenario freshness_

<<TEXT>>

## 4. Test-result analysis (last N tests reviewed; gaps surfaced; remediation per gap; ratio of scenarios tested vs total)

<<MUST item:A.5.29:rev_test_results>>
_Why: 27002:5.29 — preparation effectiveness_

<<TEXT>>

## 5. Fallback-validity check (sample of fallbacks re-validated: would they actually work? are dependencies still in place? are owners still in role?)

<<MUST item:A.5.29:rev_fallback_validity>>
_Why: 27002:5.29 — appropriate level verification_

<<TEXT>>

## 6. Real-disruption divergence analysis (where actual disruptions diverged from the plan — what was missing? what assumed? what proved unnecessary?)

<<MUST item:A.5.29:rev_real_divergence>>
_Why: Plan effectiveness_

<<TEXT>>

## 7. Action items captured (e.g. add scenario, retire stale fallback, refresh communication paths, expand test scope)

<<MUST item:A.5.29:rev_actions>>
_Why: 27002:5.29 — plan adjustments_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Industry-practice scan (notable disruptions in the sector; how peers handled; lessons applicable to our plan)

<<SHOULD item:A.5.29:rev_industry_practice>>
_Why: Audit defensibility_

<<TEXT>>

### 2. Next planned review date stated (within 180d of this review)

<<SHOULD item:A.5.29:rev_next_date>>
_Why: Planning_

<<TEXT>>
