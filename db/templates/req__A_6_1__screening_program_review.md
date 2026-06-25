---
leaf_id: req:A.6.1:screening_program_review
control_ref: A.6.1
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Periodic Screening Program Review

> Periodic verification that screening is happening at the right depth for each role tier, that legal/sectoral driver shifts have been incorporated, that re-screening cadence is being met, and that the register has no gaps. Annual cadence (freshness=365) matches the HR-program-review doctrine

<!-- TABLE-COLUMNS leaf:req:A.6.1:screening_program_review -->
<!-- column: item:A.6.1:rev_date -->
<!-- column: item:A.6.1:rev_reviewer -->
<!-- column: item:A.6.1:rev_register_check -->
<!-- column: item:A.6.1:rev_scope_check -->
<!-- column: item:A.6.1:rev_rescreen_status -->
<!-- column: item:A.6.1:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.6.1:screening_program_review -->
| Rev Date | Rev Reviewer | Rev Register Check | Rev Scope Check | Rev Rescreen Status | Rev Register Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.6.1:screening_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.6.1:rev_date>>
_Why: 27002:6.1 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.6.1:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role recorded (HR lead + InfoSec lead jointly; legal-counsel sign-off where jurisdictional shifts material)

### Rev Register Check

<<MUST item:A.6.1:rev_register_check>>
_Why: 27002:6.1 — completeness_

> _Standard text:_ Per-tier outcome (did every new hire in this tier get the right checks? gaps flagged and remediated)

### Rev Scope Check

<<MUST item:A.6.1:rev_scope_check>>
_Why: Cross-leaf coherence_

> _Standard text:_ Cross-check against the applicable-roles scope — any new role tier, new jurisdiction, new sectoral driver?

### Rev Rescreen Status

<<MUST item:A.6.1:rev_rescreen_status>>
_Why: Operational discipline_

> _Standard text:_ Rescreen status — for roles with ongoing-check obligations, what fraction completed on cadence vs aged-overdue

### Rev Register Update

<<MUST item:A.6.1:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated back to the procedure / scope with reference to this review

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Ad Hoc Triggers

<<SHOULD item:A.6.1:rev_ad_hoc_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc review triggers listed (regulator enforcement action in sector, security incident involving inadequately-screened personnel)

### Rev Next Date

<<SHOULD item:A.6.1:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
