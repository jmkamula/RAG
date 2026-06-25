---
leaf_id: req:Art.32:program_review
control_ref: Art.32
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Art.32 Security Program Review

> Annual verification — measures still risk-appropriate, resilience test executed, register reflects all current activities (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.32:program_review -->
<!-- column: item:Art.32:rev_date -->
<!-- column: item:Art.32:rev_reviewer -->
<!-- column: item:Art.32:rev_appropriateness -->
<!-- column: item:Art.32:rev_register_currency -->
<!-- column: item:Art.32:rev_iso_alignment -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.32:program_review -->
| Rev Date | Rev Reviewer | Rev Appropriateness | Rev Register Currency | Rev Iso Alignment |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.32:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.32:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.32:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + CISO + Risk lead)

### Rev Appropriateness

<<MUST item:Art.32:rev_appropriateness>>
_Why: Art.32.1 — state of the art_

> _Standard text:_ Appropriateness re-assessment — measures still proportionate given current threat landscape and tech state-of-art

### Rev Register Currency

<<MUST item:Art.32:rev_register_currency>>
_Why: Cross-leaf coherence_

> _Standard text:_ Register currency — every Art.30 RoPA activity covered with current measures

### Rev Iso Alignment

<<MUST item:Art.32:rev_iso_alignment>>
_Why: Cross-standard_

> _Standard text:_ ISO 27001 alignment — implementing controls (A.5.24/A.8.x) still in force; any reductions challenged for Art.32 impact

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.32:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
