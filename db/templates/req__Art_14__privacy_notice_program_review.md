---
leaf_id: req:Art.14:privacy_notice_program_review
control_ref: Art.14
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Art.14 Privacy Notice Program Review

<<DOC_CONTROL>>

> Annual verification that every third-party source is captured, notice was delivered per Art.14.3 deadlines, Art.14.5 exception claims still hold (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.14:privacy_notice_program_review -->
<!-- column: item:Art.14:rev_date -->
<!-- column: item:Art.14:rev_reviewer -->
<!-- column: item:Art.14:rev_register_currency -->
<!-- column: item:Art.14:rev_deadline_compliance -->
<!-- column: item:Art.14:rev_exception_reassessment -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of all third-party data sources and confirm that privacy notices were sent out on time, as required by GDPR Article 14. It also checks if any exceptions you claimed are still valid.

## When to use it

Use this template once a year to review your privacy notice program, especially if you regularly receive personal data from third parties. It’s designed for environments where Article 14 always applies.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on the number of third-party sources you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.14:privacy_notice_program_review -->
| Rev Date | Rev Reviewer | Rev Register Currency | Rev Deadline Compliance | Rev Exception Reassessment |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.14:privacy_notice_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.14:rev_date>>
_Why: Periodic accountability_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.14:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + procurement / data-acquisition lead)

<<GUIDANCE>>

### Rev Register Currency

<<MUST item:Art.14:rev_register_currency>>
_Why: Cross-leaf coherence_

> _Standard text:_ Register currency check — every active third-party source has a current row

<<GUIDANCE>>

### Rev Deadline Compliance

<<MUST item:Art.14:rev_deadline_compliance>>
_Why: Art.14.3_

> _Standard text:_ Deadline compliance audit — notice deadlines met per Art.14.3

<<GUIDANCE>>

### Rev Exception Reassessment

<<MUST item:Art.14:rev_exception_reassessment>>
_Why: Currency_

> _Standard text:_ Art.14.5 exception re-assessment — exceptions claimed still hold (proportionate-impossibility may change)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.14:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
