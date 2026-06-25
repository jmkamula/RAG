---
leaf_id: req:Art.37:dpo_designation_program_review
control_ref: Art.37
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# DPO Designation Program Review

> Annual verification — DPO designation still appropriate (org may have grown into Art.37.1 criteria), qualifications still hold, publication current (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.37:dpo_designation_program_review -->
<!-- column: item:Art.37:rev_date -->
<!-- column: item:Art.37:rev_reviewer -->
<!-- column: item:Art.37:rev_criteria_recheck -->
<!-- column: item:Art.37:rev_qualifications_currency -->
<!-- column: item:Art.37:rev_publication_current -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.37:dpo_designation_program_review -->
| Rev Date | Rev Reviewer | Rev Criteria Recheck | Rev Qualifications Currency | Rev Publication Current |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.37:dpo_designation_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.37:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.37:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (executive sponsor + legal counsel)

### Rev Criteria Recheck

<<MUST item:Art.37:rev_criteria_recheck>>
_Why: Art.37.1_

> _Standard text:_ Criteria recheck — Art.37.1 applicability re-assessed against current processing scope

### Rev Qualifications Currency

<<MUST item:Art.37:rev_qualifications_currency>>
_Why: Art.37.5_

> _Standard text:_ Qualifications currency — DPO continuing-education or certification renewal evidence

### Rev Publication Current

<<MUST item:Art.37:rev_publication_current>>
_Why: Art.37.7_

> _Standard text:_ Publication currency — privacy notice + SA registration still reflect current DPO contact

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.37:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
