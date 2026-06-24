---
leaf_id: req:A.5.18:access_rights_review
control_ref: A.5.18
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 8
should_count: 3
---

# Periodic Access Rights Review

> A.5.18 requires periodic review of access rights. Each review record captures the planned-interval review of subject-asset pairs in the register, the reviewer's identity, the outcome per subject, the orphan-access check, and any resulting modifications or revocations. Review freshness tightened to 180d for Style v2 alignment — access drift is high-volume, matches A.5.16 / A.5.17 / A.5.25 / A.5.26 volatility family

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval (typically within 6 months of last review under the 180d cadence)

<<MUST item:A.5.18:rev_date>>
_Why: 27002:5.18h — periodic_

<<TEXT>>

## 2. Reviewer identity and role recorded (asset owner + InfoSec lead jointly; reviewer must not be the same person who authorised the access)

<<MUST item:A.5.18:rev_reviewer>>
_Why: Accountability + independence_

<<TEXT>>

## 3. Outcome per reviewed subject (no change / amended / revoked) with rationale where amended or revoked

<<MUST item:A.5.18:rev_outcome>>
_Why: 27002:5.18h_

<<TEXT>>

## 4. Action items closed where rights were amended or revoked (each modification or revocation traceable to a register row update + revocation_record where applicable)

<<MUST item:A.5.18:rev_actions>>
_Why: 27002:5.18h_

<<TEXT>>

## 5. Coverage stated — full register reviewed OR risk-tiered sampling with documented selection method; gaps flagged for next cycle

<<MUST item:A.5.18:rev_coverage>>
_Why: 27002:5.18h — completeness_

<<TEXT>>

## 6. Orphan-access check — every register row reconciled against A.5.16 identity register; any rights attaching to disabled/deleted identities surfaced and revoked

<<MUST item:A.5.18:rev_orphan_check>>
_Why: A.5.16 coherence — orphan-prevention_

<<TEXT>>

## 7. Privileged-access subset reviewed with extra scrutiny (cross-link to A.8.2 privileged-access oversight; tighter cadence may apply for this slice)

<<MUST item:A.5.18:rev_privileged_check>>
_Why: A.8.2 linkage_

<<TEXT>>

## 8. Identity-family pair check — A.5.16 identity register reviewed in parallel (or same cycle); pair-confirmation that no identity has stale access AND no access points to stale identity

<<MUST item:A.5.18:rev_identity_pair>>
_Why: A.5.16 + A.5.17 family coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Sampling approach declared if not full coverage of the register (selection method documented — risk-stratified, random, role-targeted)

<<SHOULD item:A.5.18:rev_sampling>>
_Why: Audit defensibility_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.18:rev_next_date>>
_Why: Planning_

<<TEXT>>

### 3. Ad-hoc review triggers listed (org restructure, M&A, major access policy change, security incident affecting access controls)

<<SHOULD item:A.5.18:rev_ad_hoc_triggers>>
_Why: Change-driven review_

<<TEXT>>
