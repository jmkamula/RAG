---
leaf_id: req:5.3:isms_roles_program_review
control_ref: 5.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# ISMS Roles Program Review

> Annual verification that the matrix reflects current org structure, the RACI framework is being followed, and role changes during the year were captured (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:5.3:rev_date>>
_Why: Clause 5.3 — periodic_

<<TEXT>>

## 2. Reviewer identity (ISMS Manager + HR partner)

<<MUST item:5.3:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Matrix currency check — every role still has an active holder

<<MUST item:5.3:rev_currency>>
_Why: Drift detection_

<<TEXT>>

## 4. Cross-check against change records — every org-chart change touching ISMS roles is logged

<<MUST item:5.3:rev_change_log>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. A.5.2 cross-check — operational role definitions still consistent with management-system roles

<<MUST item:5.3:rev_a52_alignment>>
_Why: Cross-control coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:5.3:rev_next_date>>
_Why: Planning_

<<TEXT>>
