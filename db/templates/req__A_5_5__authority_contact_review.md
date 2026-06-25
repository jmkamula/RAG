---
leaf_id: req:A.5.5:authority_contact_review
control_ref: A.5.5
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Periodic Authority Contact Review

> Periodic verification that the register is still accurate, the scope is still correct, and the maintenance procedure is being followed. ISO 27002:2022 § 5.5 expects contact to be maintained — drift between register and reality is the audit failure mode this leaf catches

<!-- TABLE-COLUMNS leaf:req:A.5.5:authority_contact_review -->
<!-- column: item:A.5.5:rev_date -->
<!-- column: item:A.5.5:rev_reviewer -->
<!-- column: item:A.5.5:rev_per_entry -->
<!-- column: item:A.5.5:rev_scope_check -->
<!-- column: item:A.5.5:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.5:authority_contact_review -->
| Rev Date | Rev Reviewer | Rev Per Entry | Rev Scope Check | Rev Register Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.5:authority_contact_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.5:rev_date>>
_Why: 27002:5.5 — maintained_

> _Standard text:_ Review date within the planned interval (typically within 12 months of last review)

### Rev Reviewer

<<MUST item:A.5.5:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role recorded

### Rev Per Entry

<<MUST item:A.5.5:rev_per_entry>>
_Why: 27002:5.5 — maintained_

> _Standard text:_ Per-entry outcome (verified / amended / removed) and the verification method used

### Rev Scope Check

<<MUST item:A.5.5:rev_scope_check>>
_Why: Cross-leaf coherence_

> _Standard text:_ Cross-check against the applicable-authorities scope (any new jurisdiction or sector that should add an entry)

### Rev Register Update

<<MUST item:A.5.5:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated back to the live register with reference to this review

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Ad Hoc Triggers

<<SHOULD item:A.5.5:rev_ad_hoc_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc review triggers listed (re-org, new geography, new sectoral obligation)

### Rev Next Date

<<SHOULD item:A.5.5:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
