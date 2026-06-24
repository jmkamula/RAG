---
leaf_id: req:A.8.29:test_program_review
control_ref: A.8.29
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 180
template_version: 1
must_count: 6
should_count: 1
---

# Periodic Security Testing Program Review

> Periodic verification — test-coverage gaps, finding-pattern trending, pen-test outcomes feeding back (freshness=180; testing landscape evolves with threats)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval (≤180 days)

<<MUST item:A.8.29:rev_date>>
_Why: 27002:8.29 — periodic_

<<TEXT>>

## 2. Reviewer identity (Security Engineering + Engineering leads)

<<MUST item:A.8.29:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Test-coverage gap check vs applicable scope

<<MUST item:A.8.29:rev_coverage_gaps>>
_Why: 27002:8.29 — coverage_

<<TEXT>>

## 4. Finding-pattern trending (recurring patterns → SDLC / training / tooling action)

<<MUST item:A.8.29:rev_pattern_trending>>
_Why: Continuous improvement_

<<TEXT>>

## 5. Pen-test outcomes feeding back into procedure / scope / training

<<MUST item:A.8.29:rev_pen_test_feedback>>
_Why: Closes the loop_

<<TEXT>>

## 6. Findings propagated to procedure / scope / tooling

<<MUST item:A.8.29:rev_findings_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.29:rev_next_date>>
_Why: Planning_

<<TEXT>>
