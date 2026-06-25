---
leaf_id: req:A.7.1:perimeter_program_review
control_ref: A.7.1
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Perimeter Program Review

> Periodic verification that perimeters still match the classification needs, the register reflects reality, and any site changes have been incorporated. Annual cadence (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.1:perimeter_program_review -->
<!-- column: item:A.7.1:rev_date -->
<!-- column: item:A.7.1:rev_reviewer -->
<!-- column: item:A.7.1:rev_walkthrough -->
<!-- column: item:A.7.1:rev_scope_check -->
<!-- column: item:A.7.1:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.1:perimeter_program_review -->
| Rev Date | Rev Reviewer | Rev Walkthrough | Rev Scope Check | Rev Register Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.1:perimeter_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.1:rev_date>>
_Why: 27002:7.1 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.7.1:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Facilities lead + InfoSec lead jointly)

### Rev Walkthrough

<<MUST item:A.7.1:rev_walkthrough>>
_Why: 27002:7.1 — verified_

> _Standard text:_ Physical walkthrough conducted per site (sample-based for multi-site orgs) — barriers verified present and functional

### Rev Scope Check

<<MUST item:A.7.1:rev_scope_check>>
_Why: Cross-leaf coherence_

> _Standard text:_ Cross-check against the applicable-sites scope — any new site or sub-let that should add a register entry

### Rev Register Update

<<MUST item:A.7.1:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the live register

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.1:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
