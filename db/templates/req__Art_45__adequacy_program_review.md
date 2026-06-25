---
leaf_id: req:Art.45:adequacy_program_review
control_ref: Art.45
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Adequacy Program Review

> Annual verification — adequacy decisions still in force, recipient eligibility re-checked, invalidation watch maintained (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.45:adequacy_program_review -->
<!-- column: item:Art.45:rev_date -->
<!-- column: item:Art.45:rev_reviewer -->
<!-- column: item:Art.45:rev_decision_currency -->
<!-- column: item:Art.45:rev_recipient_recheck -->
<!-- column: item:Art.45:rev_fallback_readiness -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.45:adequacy_program_review -->
| Rev Date | Rev Reviewer | Rev Decision Currency | Rev Recipient Recheck | Rev Fallback Readiness |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.45:adequacy_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.45:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.45:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + legal counsel)

### Rev Decision Currency

<<MUST item:Art.45:rev_decision_currency>>
_Why: Art.45.5_

> _Standard text:_ Decision currency — every cited adequacy decision still in force (not repealed, suspended, or invalidated)

### Rev Recipient Recheck

<<MUST item:Art.45:rev_recipient_recheck>>
_Why: Defensibility_

> _Standard text:_ Recipient-eligibility recheck — certifications still active (US-DPF, etc.)

### Rev Fallback Readiness

<<MUST item:Art.45:rev_fallback_readiness>>
_Why: Operational resilience_

> _Standard text:_ Fallback readiness — if a decision were invalidated, Art.46 fallback (e.g. SCCs) pre-staged with affected vendors

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.45:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
