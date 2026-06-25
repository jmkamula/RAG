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

> Annual verification that age-verification and parental-consent flows are functioning, the register is current, no in-scope service is operating without the procedure (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.8:child_consent_program_review -->
<!-- column: item:Art.8:rev_date -->
<!-- column: item:Art.8:rev_reviewer -->
<!-- column: item:Art.8:rev_verification_quality -->
<!-- column: item:Art.8:rev_register_coverage -->
<!-- column: item:Art.8:rev_threshold_currency -->
<!-- /TABLE-COLUMNS -->

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

### Rev Reviewer

<<MUST item:Art.8:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + product lead)

### Rev Verification Quality

<<MUST item:Art.8:rev_verification_quality>>
_Why: Art.8.2 — reasonable efforts_

> _Standard text:_ Age-verification sample audit — claimed-age values look plausible vs other signals

### Rev Register Coverage

<<MUST item:Art.8:rev_register_coverage>>
_Why: Cross-leaf coherence_

> _Standard text:_ Register coverage — every in-scope service has consent rows flowing in

### Rev Threshold Currency

<<MUST item:Art.8:rev_threshold_currency>>
_Why: Currency_

> _Standard text:_ Member State threshold currency — any MS that has changed its age threshold reflected

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.8:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
