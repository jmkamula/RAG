---
leaf_id: req:A.7.7:cd_cs_program_review
control_ref: A.7.7
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Clear Desk / Clear Screen Program Review

> Annual review of policy currency, audit findings trend, enforcement consistency. Freshness=365

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.7.7:rev_date>>
_Why: 27002:7.7 — periodic_

<<TEXT>>

## 2. Reviewer identity (Facilities + InfoSec + HR partner)

<<MUST item:A.7.7:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Audit-finding trend (improving / worsening — drives policy/awareness adjustments)

<<MUST item:A.7.7:rev_audit_trend>>
_Why: Continual improvement_

<<TEXT>>

## 4. Policy currency check (referenced policies — A.5.12 classification, A.6.7 remote-work — still aligned)

<<MUST item:A.7.7:rev_policy_drift>>
_Why: Cross-control coherence_

<<TEXT>>

## 5. Changes propagated to the policy

<<MUST item:A.7.7:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.7.7:rev_next_date>>
_Why: Planning_

<<TEXT>>
