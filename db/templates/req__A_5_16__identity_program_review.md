---
leaf_id: req:A.5.16:identity_program_review
control_ref: A.5.16
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 7
should_count: 2
---

# Periodic Identity-Management Program Review

> The identity program creates value only if the lifecycle actually closes — orphan accounts, lingering contractor access, stale service credentials, missed termination SLAs all signal the program is leaking. The review captures the planned-interval check: orphan analysis, SLA-miss analysis, service-account hygiene audit, contractor expiry verification, and resulting program adjustments. Cadence tightened to 180 days — identity drift is high-volume

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned 180-day interval

<<MUST item:A.5.16:rev_date>>
_Why: 27002:5.16 — periodic_

<<TEXT>>

## 2. Reviewer identity (IT identity-lead + HR partner + InfoSec lead jointly)

<<MUST item:A.5.16:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Orphan analysis (identities without active HR record / business reason; remediation per orphan)

<<MUST item:A.5.16:rev_orphan_analysis>>
_Why: 27002:5.16 — drift catch_

<<TEXT>>

## 4. Termination-SLA analysis (gap between leaver effective_date and identity_revocation date; outliers investigated)

<<MUST item:A.5.16:rev_termination_sla>>
_Why: 27002:5.16 — timeliness_

<<TEXT>>

## 5. Service-account hygiene audit (sample of service accounts re-validated: owner still employed, scope still appropriate, expiry not lapsed)

<<MUST item:A.5.16:rev_service_hygiene>>
_Why: 27002:5.16 — service-account discipline_

<<TEXT>>

## 6. Contractor-expiry verification (audit that expired contractor identities are actually disabled, not just flagged)

<<MUST item:A.5.16:rev_contractor_expiry>>
_Why: 27002:5.16 — fixed-expiry enforcement_

<<TEXT>>

## 7. Action items captured (e.g. tighten auto-suspend threshold, expand HR-cascade automation, retire shared accounts)

<<MUST item:A.5.16:rev_actions>>
_Why: 27002:5.16 — program adjustments_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. IAM tooling check (vendor releases, new capabilities like just-in-time access; capability gaps to consider)

<<SHOULD item:A.5.16:rev_iam_tooling>>
_Why: Audit defensibility_

<<TEXT>>

### 2. Next planned review date stated (within 180d of this review)

<<SHOULD item:A.5.16:rev_next_date>>
_Why: Planning_

<<TEXT>>
