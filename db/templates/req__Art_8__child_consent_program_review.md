---
leaf_id: req:Art.8:child_consent_program_review
control_ref: Art.8
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Child Consent Program Review

<<DOC_CONTROL>>

> Annual verification that age-verification and parental-consent flows are functioning, the register is current, no in-scope service is operating without the procedure (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.8:child_consent_program_review -->
<!-- column: item:Art.8:rev_date -->
<!-- column: item:Art.8:rev_reviewer -->
<!-- column: item:Art.8:rev_verification_quality -->
<!-- column: item:Art.8:rev_register_coverage -->
<!-- column: item:Art.8:rev_threshold_currency -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your age-verification and parental-consent processes, making sure they are up to date and compliant with GDPR requirements for services used by children.

## When to use it

Use this review record if your service involves children and you need to confirm, about once a year, that your consent and age-checking procedures are working and properly documented.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on the number of services or flows you need to review and record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.8:child_consent_program_review -->
| Rev Date | Rev Reviewer | Rev Verification Quality | Rev Register Coverage | Rev Threshold Currency |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.8:child_consent_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.8:rev_date>>
_Why: Periodic accountability_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.8:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + product lead)

<<GUIDANCE>>

### Rev Verification Quality

<<MUST item:Art.8:rev_verification_quality>>
_Why: Art.8.2 — reasonable efforts_

> _Standard text:_ Age-verification sample audit — claimed-age values look plausible vs other signals

<<GUIDANCE>>

### Rev Register Coverage

<<MUST item:Art.8:rev_register_coverage>>
_Why: Cross-leaf coherence_

> _Standard text:_ Register coverage — every in-scope service has consent rows flowing in

<<GUIDANCE>>

### Rev Threshold Currency

<<MUST item:Art.8:rev_threshold_currency>>
_Why: Currency_

> _Standard text:_ Member State threshold currency — any MS that has changed its age threshold reflected

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.8:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
