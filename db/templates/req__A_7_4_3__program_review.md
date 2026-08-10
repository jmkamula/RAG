---
leaf_id: req:A.7.4.3:program_review
control_ref: A.7.4.3
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Accuracy Program Review

<<DOC_CONTROL>>

> Annual verification — prevention controls working, incident register growing at healthy rate (not stalled = under-detection), root-cause remediations closing (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.4.3:program_review -->
<!-- column: item:A.7.4.3:rev_date -->
<!-- column: item:A.7.4.3:rev_reviewer -->
<!-- column: item:A.7.4.3:rev_prevention_health -->
<!-- column: item:A.7.4.3:rev_detection_rate -->
<!-- column: item:A.7.4.3:rev_root_cause_closure -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of how well your privacy controls are working, making it easier to spot issues and show that you’re addressing root causes over time.

## When to use it

Use this review record whenever your organization’s profile matches certain privacy-related triggers, and plan to update it about once a year to stay compliant with ISO 27701.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on the number of required elements and how much information you need to gather for each.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4.3:program_review -->
| Rev Date | Rev Reviewer | Rev Prevention Health | Rev Detection Rate | Rev Root Cause Closure |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4.3:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.4.3:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.4.3:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Data Ops)

<<GUIDANCE>>

### Rev Prevention Health

<<MUST item:A.7.4.3:rev_prevention_health>>
_Why: §7.4.3_

> _Standard text:_ Prevention controls health (input validation / duplicate detection / reconciliation)

<<GUIDANCE>>

### Rev Detection Rate

<<MUST item:A.7.4.3:rev_detection_rate>>
_Why: Drift detection_

> _Standard text:_ Detection rate check — under-detection surfaces via low incident counts

<<GUIDANCE>>

### Rev Root Cause Closure

<<MUST item:A.7.4.3:rev_root_cause_closure>>
_Why: Continuous improvement_

> _Standard text:_ Root-cause closure — systemic remediations from prior period reviewed for completeness

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.4.3:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
