---
leaf_id: req:6.1.2:risk_assessment_program_review
control_ref: 6.1.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Risk Assessment Program Review

<<DOC_CONTROL>>

> Annual verification that the procedure is being followed, the register is current, and the methodology still fits (freshness=365)

<!-- TABLE-COLUMNS leaf:req:6.1.2:risk_assessment_program_review -->
<!-- column: item:6.1.2:rev_date -->
<!-- column: item:6.1.2:rev_reviewer -->
<!-- column: item:6.1.2:rev_register_currency -->
<!-- column: item:6.1.2:rev_methodology_fit -->
<!-- column: item:6.1.2:rev_significant_change -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you review and confirm that your risk assessment process is up to date, your risk register is accurate, and your approach still fits your organization’s needs.

## When to use it

Use this template once a year to check that your risk assessment program is being followed and remains effective, as it always applies to your environment and should be refreshed annually.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on how many risks you need to review and update in your register.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:6.1.2:risk_assessment_program_review -->
| Rev Date | Rev Reviewer | Rev Register Currency | Rev Methodology Fit | Rev Significant Change |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:6.1.2:risk_assessment_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:6.1.2:rev_date>>
_Why: Clause 6.1.2 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:6.1.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Risk Manager + ISMS Manager)

<<GUIDANCE>>

### Rev Register Currency

<<MUST item:6.1.2:rev_register_currency>>
_Why: Cross-leaf coherence_

> _Standard text:_ Register currency check — every row reviewed for continued relevance

<<GUIDANCE>>

### Rev Methodology Fit

<<MUST item:6.1.2:rev_methodology_fit>>
_Why: Cross-leaf coherence_

> _Standard text:_ Methodology fit check — scoring scale still discriminating, acceptance bands still calibrated

<<GUIDANCE>>

### Rev Significant Change

<<MUST item:6.1.2:rev_significant_change>>
_Why: Cross-clause coherence_

> _Standard text:_ Significant-change trigger sweep — 8.2 ad-hoc assessments captured

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:6.1.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
