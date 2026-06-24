---
leaf_id: req:A.8.2:privileged_access_recertification
control_ref: A.8.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 7
should_count: 1
---

# Privileged Access Recertification

> A.8.2 calls for periodic review of privileged access — typically more frequent than the general access review at A.5.18 (this curation sets freshness at 180 days; tenants with high-risk processing may run quarterly). The recertification record evidences that each privileged grant was re-confirmed by the asset owner

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Recertification date within the planned interval (≤180 days since last)

<<MUST item:A.8.2:rc_date>>
_Why: 27002:8.2k_

<<TEXT>>

## 2. Reviewer identity (asset owner or delegated authority)

<<MUST item:A.8.2:rc_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Per-privileged-account outcome (re-confirmed / amended / revoked)

<<MUST item:A.8.2:rc_per_account>>
_Why: 27002:8.2k_

<<TEXT>>

## 4. Revocation/modification actions completed for non-reconfirmed access

<<MUST item:A.8.2:rc_actions>>
_Why: 27002:8.2k_

<<TEXT>>

## 5. Revocation-actions-within-SLA flag per row (auditor-critical timeliness proof, parallel to A.5.16 rev_sla_met)

<<MUST item:A.8.2:rc_sla_met>>
_Why: 27002:8.2k modern interpretation (Style v2)_

<<TEXT>>

## 6. Cross-link to A.5.18 general access review — every privileged subject also appears under their general access row (no orphan privileged paths)

<<MUST item:A.8.2:rc_a518_pairing>>
_Why: Cross-control coherence (Style v2)_

<<TEXT>>

## 7. Role-change events trigger ad-hoc recertification outside the interval

<<MUST item:A.8.2:rc_role_change_trigger>>
_Why: 27002:8.2g (Style v2 promotion)_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned recertification date stated

<<SHOULD item:A.8.2:rc_next_date>>
_Why: Planning_

<<TEXT>>
