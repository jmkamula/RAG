---
leaf_id: req:Art.18:restriction_program_review
control_ref: Art.18
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Restriction Program Review

> Annual verification — restrictions still active are valid, Art.18.2 exceptions enforced, Art.19 notifications fired (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.18:restriction_program_review -->
<!-- column: item:Art.18:rev_date -->
<!-- column: item:Art.18:rev_reviewer -->
<!-- column: item:Art.18:rev_active_restrictions -->
<!-- column: item:Art.18:rev_exception_compliance -->
<!-- column: item:Art.18:rev_art19_compliance -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.18:restriction_program_review -->
| Rev Date | Rev Reviewer | Rev Active Restrictions | Rev Exception Compliance | Rev Art19 Compliance |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.18:restriction_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.18:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.18:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + ops lead)

### Rev Active Restrictions

<<MUST item:Art.18:rev_active_restrictions>>
_Why: Cross-leaf coherence_

> _Standard text:_ Active-restrictions check — every active row still has a valid Art.18.1 ground

### Rev Exception Compliance

<<MUST item:Art.18:rev_exception_compliance>>
_Why: Art.18.2_

> _Standard text:_ Exception compliance — restricted records only used per Art.18.2 exceptions

### Rev Art19 Compliance

<<MUST item:Art.18:rev_art19_compliance>>
_Why: Art.19_

> _Standard text:_ Art.19 notification compliance — recipient notifications fired for new/lifted restrictions

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.18:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
