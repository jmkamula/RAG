---
leaf_id: req:Art.28:processor_program_review
control_ref: Art.28
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Processor Program Review

> Annual verification that every active processor has a current DPA, sub-processor authorisations are tracked, Art.32 assurance sources are still valid (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.28:processor_program_review -->
<!-- column: item:Art.28:rev_date -->
<!-- column: item:Art.28:rev_reviewer -->
<!-- column: item:Art.28:rev_dpa_currency -->
<!-- column: item:Art.28:rev_subprocessor_audit -->
<!-- column: item:Art.28:rev_security_currency -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.28:processor_program_review -->
| Rev Date | Rev Reviewer | Rev Dpa Currency | Rev Subprocessor Audit | Rev Security Currency |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.28:processor_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.28:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.28:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + procurement / vendor management lead)

### Rev Dpa Currency

<<MUST item:Art.28:rev_dpa_currency>>
_Why: Art.28.3 — written contract_

> _Standard text:_ DPA currency check — every active processor has a current DPA (no expired or pre-onboarding processors active)

### Rev Subprocessor Audit

<<MUST item:Art.28:rev_subprocessor_audit>>
_Why: Art.28.2_

> _Standard text:_ Sub-processor audit — every active sub-processor authorised; unauthorised additions flagged

### Rev Security Currency

<<MUST item:Art.28:rev_security_currency>>
_Why: Art.28.3c_

> _Standard text:_ Security assurance currency — Art.32-equivalent evidence (cert, audit) refreshed within validity period

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.28:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
