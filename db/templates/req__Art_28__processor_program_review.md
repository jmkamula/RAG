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

<<DOC_CONTROL>>

> Annual verification that every active processor has a current DPA, sub-processor authorisations are tracked, Art.32 assurance sources are still valid (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.28:processor_program_review -->
<!-- column: item:Art.28:rev_date -->
<!-- column: item:Art.28:rev_reviewer -->
<!-- column: item:Art.28:rev_dpa_currency -->
<!-- column: item:Art.28:rev_subprocessor_audit -->
<!-- column: item:Art.28:rev_security_currency -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of your data processors, making sure each has a current agreement and that all required GDPR checks are up to date.

## When to use it

Use this template once a year, or whenever you onboard a new processor, to confirm your processor agreements and authorisations are current and compliant with GDPR Article 28.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10 to 15 minutes per required element, plus extra time for each processor you need to review, so a typical review may take 1-2 hours depending on the number of processors.

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

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.28:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + procurement / vendor management lead)

<<GUIDANCE>>

### Rev Dpa Currency

<<MUST item:Art.28:rev_dpa_currency>>
_Why: Art.28.3 — written contract_

> _Standard text:_ DPA currency check — every active processor has a current DPA (no expired or pre-onboarding processors active)

<<GUIDANCE>>

### Rev Subprocessor Audit

<<MUST item:Art.28:rev_subprocessor_audit>>
_Why: Art.28.2_

> _Standard text:_ Sub-processor audit — every active sub-processor authorised; unauthorised additions flagged

<<GUIDANCE>>

### Rev Security Currency

<<MUST item:Art.28:rev_security_currency>>
_Why: Art.28.3c_

> _Standard text:_ Security assurance currency — Art.32-equivalent evidence (cert, audit) refreshed within validity period

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.28:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
