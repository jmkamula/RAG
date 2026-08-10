---
leaf_id: req:A.7.2.2:program_review
control_ref: A.7.2.2
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Lawful Basis Program Review

<<DOC_CONTROL>>

> Annual verification — every activity has a valid basis, LIA balancing tests remain defensible, special-category dual-basis coverage intact, no basis-slippage (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.2.2:program_review -->
<!-- column: item:A.7.2.2:rev_date -->
<!-- column: item:A.7.2.2:rev_reviewer -->
<!-- column: item:A.7.2.2:rev_basis_currency -->
<!-- column: item:A.7.2.2:rev_lia_reaffirmation -->
<!-- column: item:A.7.2.2:rev_special_category_audit -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you confirm that every data processing activity has a valid legal basis and that any balancing tests or special-category data are properly documented and up to date. It keeps your compliance records organized and defensible for audits.

## When to use it

Use this review record when your activities or data types match certain privacy triggers, and plan to update it about once a year to ensure your legal bases remain current and accurate.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes completing this from scratch, depending on the number of activities you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2.2:program_review -->
| Rev Date | Rev Reviewer | Rev Basis Currency | Rev Lia Reaffirmation | Rev Special Category Audit |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2.2:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.2.2:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.2.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + legal counsel)

<<GUIDANCE>>

### Rev Basis Currency

<<MUST item:A.7.2.2:rev_basis_currency>>
_Why: §7.2.2 — comply with basis_

> _Standard text:_ Basis currency — every registered activity still has a valid basis in force

<<GUIDANCE>>

### Rev Lia Reaffirmation

<<MUST item:A.7.2.2:rev_lia_reaffirmation>>
_Why: GDPR Art.6.1.f — ongoing balancing_

> _Standard text:_ LIA reaffirmation — sampled legitimate-interests activities reviewed against current subject-rights context

<<GUIDANCE>>

### Rev Special Category Audit

<<MUST item:A.7.2.2:rev_special_category_audit>>
_Why: GDPR Art.9.2_

> _Standard text:_ Special-category audit — dual-basis coverage confirmed where Art.9/10 data processed

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.2.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
