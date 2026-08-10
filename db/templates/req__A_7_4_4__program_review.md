---
leaf_id: req:A.7.4.4:program_review
control_ref: A.7.4.4
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Minimization Program Review

<<DOC_CONTROL>>

> Annual verification — minimisation objectives current, techniques appropriate for risk profile, re-identification risk stable, no drift toward over-collection (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.4.4:program_review -->
<!-- column: item:A.7.4.4:rev_date -->
<!-- column: item:A.7.4.4:rev_reviewer -->
<!-- column: item:A.7.4.4:rev_technique_currency -->
<!-- column: item:A.7.4.4:rev_drift_sweep -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document your annual review of data minimization practices, ensuring your objectives are up to date and your techniques match your current privacy risks.

## When to use it

Use this template once a year, or whenever your risk profile changes significantly, to confirm you’re not collecting more data than needed and your re-identification risks remain stable.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 45 to 60 minutes completing this from scratch, depending on how many items you need to review and record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4.4:program_review -->
| Rev Date | Rev Reviewer | Rev Technique Currency | Rev Drift Sweep |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4.4:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.4.4:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.4.4:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Privacy Engineering)

<<GUIDANCE>>

### Rev Technique Currency

<<MUST item:A.7.4.4:rev_technique_currency>>
_Why: §7.4.4_

> _Standard text:_ Technique currency — techniques still appropriate for risk profile (advances in re-identification research surfaced)

<<GUIDANCE>>

### Rev Drift Sweep

<<MUST item:A.7.4.4:rev_drift_sweep>>
_Why: Continuous improvement_

> _Standard text:_ Drift sweep — new processing activities checked for minimisation opportunity

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.4.4:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
