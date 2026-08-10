---
leaf_id: req:Art.25:program_review
control_ref: Art.25
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# DPbD Program Review

<<DOC_CONTROL>>

> Annual verification — DPbD reviews happened for every in-scope design, defaults register is current, certification reliance still valid (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.25:program_review -->
<!-- column: item:Art.25:rev_date -->
<!-- column: item:Art.25:rev_reviewer -->
<!-- column: item:Art.25:rev_coverage -->
<!-- column: item:Art.25:rev_defaults_currency -->
<!-- column: item:Art.25:rev_certification_validity -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record that your Data Protection by Design (DPbD) reviews are up to date, your defaults register is current, and any certifications you rely on are still valid.

## When to use it

Use this template every year to confirm that DPbD reviews have been completed for all relevant designs in your environment and to check that your documentation and certifications remain fresh.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes completing this from scratch, depending on the number of items you need to review and record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.25:program_review -->
| Rev Date | Rev Reviewer | Rev Coverage | Rev Defaults Currency | Rev Certification Validity |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.25:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.25:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.25:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + product + engineering)

<<GUIDANCE>>

### Rev Coverage

<<MUST item:Art.25:rev_coverage>>
_Why: Art.25.1_

> _Standard text:_ Design-coverage check — every in-scope design activity had a DPbD review

<<GUIDANCE>>

### Rev Defaults Currency

<<MUST item:Art.25:rev_defaults_currency>>
_Why: Art.25.2_

> _Standard text:_ Defaults register currency check (cross-leaf — defaults still match deployed system state)

<<GUIDANCE>>

### Rev Certification Validity

<<MUST item:Art.25:rev_certification_validity>>
_Why: Art.25.3_

> _Standard text:_ If Art.25.3 certification used — certification still in validity period

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.25:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
