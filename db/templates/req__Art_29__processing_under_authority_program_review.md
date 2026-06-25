---
leaf_id: req:Art.29:processing_under_authority_program_review
control_ref: Art.29
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Processing Under Authority Program Review

> Annual verification — every person touching personal data has a current authorisation row, training is current, processing stays within documented instructions (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.29:processing_under_authority_program_review -->
<!-- column: item:Art.29:rev_date -->
<!-- column: item:Art.29:rev_reviewer -->
<!-- column: item:Art.29:rev_authorisation_completeness -->
<!-- column: item:Art.29:rev_training_currency -->
<!-- column: item:Art.29:rev_instruction_drift -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.29:processing_under_authority_program_review -->
| Rev Date | Rev Reviewer | Rev Authorisation Completeness | Rev Training Currency | Rev Instruction Drift |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.29:processing_under_authority_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.29:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.29:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + HR + ops lead)

### Rev Authorisation Completeness

<<MUST item:Art.29:rev_authorisation_completeness>>
_Why: Art.29 — under authority_

> _Standard text:_ Authorisation completeness — every person with access has a register row

### Rev Training Currency

<<MUST item:Art.29:rev_training_currency>>
_Why: Cross-control_

> _Standard text:_ Training currency — A.6.3 / 7.3 training current for every authorised person

### Rev Instruction Drift

<<MUST item:Art.29:rev_instruction_drift>>
_Why: Art.29 — only on documented instructions_

> _Standard text:_ Instruction-drift sweep — sample processing activities to verify they stay within documented controller instructions

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.29:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
