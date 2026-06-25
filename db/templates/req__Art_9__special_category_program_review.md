---
leaf_id: req:Art.9:special_category_program_review
control_ref: Art.9
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Special Category Program Review

> Annual verification that every Art.9 processing activity has a current Art.9.2 condition justification, safeguards are in place, no quiet onboarding happened (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.9:special_category_program_review -->
<!-- column: item:Art.9:rev_date -->
<!-- column: item:Art.9:rev_reviewer -->
<!-- column: item:Art.9:rev_register_currency -->
<!-- column: item:Art.9:rev_safeguards_audit -->
<!-- column: item:Art.9:rev_silent_onboarding -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.9:special_category_program_review -->
| Rev Date | Rev Reviewer | Rev Register Currency | Rev Safeguards Audit | Rev Silent Onboarding |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.9:special_category_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.9:rev_date>>
_Why: Periodic accountability_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.9:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + executive sponsor)

### Rev Register Currency

<<MUST item:Art.9:rev_register_currency>>
_Why: Cross-leaf coherence_

> _Standard text:_ Register currency check — every active activity has its Art.9.2 condition still appropriate

### Rev Safeguards Audit

<<MUST item:Art.9:rev_safeguards_audit>>
_Why: Art.9.3_

> _Standard text:_ Safeguards audit — Art.9.3 secrecy obligations being enforced (where Art.9.2.h-i applies)

### Rev Silent Onboarding

<<MUST item:Art.9:rev_silent_onboarding>>
_Why: Art.9.1 — prohibition default_

> _Standard text:_ Silent-onboarding sweep — verify no new special-category data ingested without the procedure being invoked

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.9:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
