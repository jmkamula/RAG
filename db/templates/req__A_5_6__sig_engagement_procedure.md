---
leaf_id: req:A.5.6:sig_engagement_procedure
control_ref: A.5.6
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 4
should_count: 2
---

# SIG Engagement Procedure

> A.5.6 expects active engagement, not nominal membership. The procedure documents how SIGs are joined, how value is captured back into the organisation (intel sharing into threat-intelligence A.5.7, runbook updates, training inputs) and how dormant memberships are pruned

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Path to join a new SIG (business case linked to risk-topic scope, approval, budget allocation)

<<MUST item:A.5.6:proc_join_path>>
_Why: Operational sufficiency_

<<TEXT>>

## 2. Attendance/participation expectations per membership (minimum events, working groups, briefings)

<<MUST item:A.5.6:proc_attendance>>
_Why: 27002:5.6 — maintain_

<<TEXT>>

## 3. Value-capture path — how intelligence/insights flow back (cross-link to A.5.7 threat-intel procedure)

<<MUST item:A.5.6:proc_value_capture>>
_Why: 27002:5.6b / A.5.7_

<<TEXT>>

## 4. Disengagement path for dormant or low-value memberships (avoid paying for unused subscriptions)

<<MUST item:A.5.6:proc_disengagement>>
_Why: 27002:5.6 — appropriate_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Confidentiality expectations when sharing internal info to SIGs (TLP labelling, NDA awareness)

<<SHOULD item:A.5.6:proc_confidentiality>>
_Why: Information leakage avoidance_

<<TEXT>>

### 2. Link to training programme (A.6.3) for representatives who attend on behalf of the org

<<SHOULD item:A.5.6:proc_training_link>>
_Why: Effectiveness_

<<TEXT>>
