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
table_shape: true
---

# Periodic Access Rights Review

<<DOC_CONTROL>>

> A.5.18 requires periodic review of access rights. Each review record captures the planned-interval review of subject-asset pairs in the register, the reviewer's identity, the outcome per subject, the orphan-access check, and any resulting modifications or revocations. Review freshness tightened to 180d for Style v2 alignment — access drift is high-volume, matches A.5.16 / A.5.17 / A.5.25 / A.5.26 volatility family

<!-- TABLE-COLUMNS leaf:req:A.5.18:access_rights_review -->
<!-- column: item:A.5.18:rev_date -->
<!-- column: item:A.5.18:rev_reviewer -->
<!-- column: item:A.5.18:rev_outcome -->
<!-- column: item:A.5.18:rev_actions -->
<!-- column: item:A.5.18:rev_coverage -->
<!-- column: item:A.5.18:rev_orphan_check -->
<!-- column: item:A.5.18:rev_privileged_check -->
<!-- column: item:A.5.18:rev_identity_pair -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you systematically review and document who has access to what in your systems, ensuring you catch outdated or unnecessary permissions and stay compliant with ISO 27001 requirements.

## When to use it

Use this template whenever you need to review access rights for users and assets, which should happen about every six months to keep your records up to date and minimize security risks.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours completing the required sections for a single review, plus additional time for each user or asset you need to check in your register.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.18:access_rights_review -->
| Rev Date | Rev Reviewer | Rev Outcome | Rev Actions | Rev Coverage | Rev Orphan Check | Rev Privileged Check | Rev Identity Pair |
|---|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.18:access_rights_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.18:rev_date>>
_Why: 27002:5.18h — periodic_

> _Standard text:_ Review date within the planned interval (typically within 6 months of last review under the 180d cadence)

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.5.18:rev_reviewer>>
_Why: Accountability + independence_

> _Standard text:_ Reviewer identity and role recorded (asset owner + InfoSec lead jointly; reviewer must not be the same person who authorised the access)

<<GUIDANCE>>

### Rev Outcome

<<MUST item:A.5.18:rev_outcome>>
_Why: 27002:5.18h_

> _Standard text:_ Outcome per reviewed subject (no change / amended / revoked) with rationale where amended or revoked

<<GUIDANCE>>

### Rev Actions

<<MUST item:A.5.18:rev_actions>>
_Why: 27002:5.18h_

> _Standard text:_ Action items closed where rights were amended or revoked (each modification or revocation traceable to a register row update + revocation_record where applicable)

<<GUIDANCE>>

### Rev Coverage

<<MUST item:A.5.18:rev_coverage>>
_Why: 27002:5.18h — completeness_

> _Standard text:_ Coverage stated — full register reviewed OR risk-tiered sampling with documented selection method; gaps flagged for next cycle

<<GUIDANCE>>

### Rev Orphan Check

<<MUST item:A.5.18:rev_orphan_check>>
_Why: A.5.16 coherence — orphan-prevention_

> _Standard text:_ Orphan-access check — every register row reconciled against A.5.16 identity register; any rights attaching to disabled/deleted identities surfaced and revoked

<<GUIDANCE>>

### Rev Privileged Check

<<MUST item:A.5.18:rev_privileged_check>>
_Why: A.8.2 linkage_

> _Standard text:_ Privileged-access subset reviewed with extra scrutiny (cross-link to A.8.2 privileged-access oversight; tighter cadence may apply for this slice)

<<GUIDANCE>>

### Rev Identity Pair

<<MUST item:A.5.18:rev_identity_pair>>
_Why: A.5.16 + A.5.17 family coherence_

> _Standard text:_ Identity-family pair check — A.5.16 identity register reviewed in parallel (or same cycle); pair-confirmation that no identity has stale access AND no access points to stale identity

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Sampling

<<SHOULD item:A.5.18:rev_sampling>>
_Why: Audit defensibility_

> _Standard text:_ Sampling approach declared if not full coverage of the register (selection method documented — risk-stratified, random, role-targeted)

<<GUIDANCE>>

### Rev Next Date

<<SHOULD item:A.5.18:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

### Rev Ad Hoc Triggers

<<SHOULD item:A.5.18:rev_ad_hoc_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc review triggers listed (org restructure, M&A, major access policy change, security incident affecting access controls)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
