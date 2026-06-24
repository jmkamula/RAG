---
leaf_id: req:8.3:treatment_execution_program_review
control_ref: 8.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 5
should_count: 1
---

# Treatment Execution Program Review

> Semi-annual verification that the plan is being executed on schedule, slipping items get escalated, completed items had residual risk re-affirmed (freshness=180 — operational tempo)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:8.3:rev_date>>
_Why: Clause 8.3 — periodic_

<<TEXT>>

## 2. Reviewer identity (Risk Manager + ISMS Manager + ops lead)

<<MUST item:8.3:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Progress check — every active plan item status updated; on-track vs slipping called out

<<MUST item:8.3:rev_progress>>
_Why: Effectiveness_

<<TEXT>>

## 4. Residual revisit check — completed items had owner re-affirm residual; divergent residuals escalated

<<MUST item:8.3:rev_residual_revisit>>
_Why: Clause 8.3 — results_

<<TEXT>>

## 5. SoA currency check — newly implemented controls reflected in the SoA (6.1.3 leaf)

<<MUST item:8.3:rev_soa_currency>>
_Why: Cross-clause coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:8.3:rev_next_date>>
_Why: Planning_

<<TEXT>>
