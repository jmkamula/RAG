---
leaf_id: req:9.2:audit_program_review
control_ref: 9.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Audit Program Review

> Annual verification that the programme is being executed, every planned audit happened (or was deferred with rationale), the cycle stays on track for full coverage (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:9.2:rev_date>>
_Why: Clause 9.2 — periodic_

<<TEXT>>

## 2. Reviewer identity (ISMS Manager + lead auditor)

<<MUST item:9.2:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Completion check — every scheduled audit happened (or deferred with documented reason)

<<MUST item:9.2:rev_completion>>
_Why: Effectiveness_

<<TEXT>>

## 4. Cycle progress check — at end-of-cycle every ISMS process audited at least once

<<MUST item:9.2:rev_cycle_progress>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. Finding-closure check — last cycle's NCs reached 10.2 closure

<<MUST item:9.2:rev_finding_closure>>
_Why: Clause 9.2e_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:9.2:rev_next_date>>
_Why: Planning_

<<TEXT>>
