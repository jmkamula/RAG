---
leaf_id: req:A.7.5.1:program_review
control_ref: A.7.5.1
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Transfer Basis Program Review

> Annual verification — every transfer relationship has valid basis, TIAs current after Schrems II + regulatory updates (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.5.1:program_review -->
<!-- column: item:A.7.5.1:rev_date -->
<!-- column: item:A.7.5.1:rev_reviewer -->
<!-- column: item:A.7.5.1:rev_basis_currency -->
<!-- column: item:A.7.5.1:rev_tia_refresh -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.5.1:program_review -->
| Rev Date | Rev Reviewer | Rev Basis Currency | Rev Tia Refresh |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.5.1:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.5.1:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.7.5.1:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Legal)

### Rev Basis Currency

<<MUST item:A.7.5.1:rev_basis_currency>>
_Why: Post-Schrems_

> _Standard text:_ Basis currency — Art.45 adequacy decisions still in force (Privacy Shield lessons apply)

### Rev Tia Refresh

<<MUST item:A.7.5.1:rev_tia_refresh>>
_Why: EDPB 01/2020_

> _Standard text:_ TIA refresh — recent case law + guidance considered

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.5.1:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
