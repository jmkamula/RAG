---
leaf_id: req:Art.6:lawful_basis_program_review
control_ref: Art.6
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Lawful Basis Program Review

<<DOC_CONTROL>>

> Annual verification that every processing activity has a current basis, the procedure is being followed, regulator guidance updates have been swept in (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.6:lawful_basis_program_review -->
<!-- column: item:Art.6:rev_date -->
<!-- column: item:Art.6:rev_reviewer -->
<!-- column: item:Art.6:rev_register_currency -->
<!-- column: item:Art.6:rev_basis_appropriateness -->
<!-- column: item:Art.6:rev_regulator_guidance -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of the legal reasons for all your data processing activities and ensures your procedures stay up to date with the latest regulatory guidance.

## When to use it

Use this review record once a year to confirm that every data processing activity in your organization has a valid legal basis and follows current procedures, as required under GDPR.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes completing this from scratch, depending on the number of processing activities you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.6:lawful_basis_program_review -->
| Rev Date | Rev Reviewer | Rev Register Currency | Rev Basis Appropriateness | Rev Regulator Guidance |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.6:lawful_basis_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.6:rev_date>>
_Why: Art.5.2 — periodic accountability_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.6:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO or Privacy Lead)

<<GUIDANCE>>

### Rev Register Currency

<<MUST item:Art.6:rev_register_currency>>
_Why: Cross-clause coherence_

> _Standard text:_ Register currency check — every Art.30 RoPA activity has a current Art.6 basis assignment

<<GUIDANCE>>

### Rev Basis Appropriateness

<<MUST item:Art.6:rev_basis_appropriateness>>
_Why: Art.5.2 — accountability_

> _Standard text:_ Basis-appropriateness sample — high-volume / high-sensitivity activities re-evaluated for whether the chosen basis still fits

<<GUIDANCE>>

### Rev Regulator Guidance

<<MUST item:Art.6:rev_regulator_guidance>>
_Why: Currency_

> _Standard text:_ Regulator-guidance sweep — EDPB / supervisory authority guidance updates considered for impact

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.6:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
