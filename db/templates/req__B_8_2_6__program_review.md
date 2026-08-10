---
leaf_id: req:B.8.2.6:program_review
control_ref: B.8.2.6
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Processor RoPA Program Review

<<DOC_CONTROL>>

> Annual verification — processor RoPA complete + accurate + current, cross-register reconciliation intact, secure maintenance (freshness=365)

<!-- TABLE-COLUMNS leaf:req:B.8.2.6:program_review -->
<!-- column: item:B.8.2.6:rev_date -->
<!-- column: item:B.8.2.6:rev_reviewer -->
<!-- column: item:B.8.2.6:rev_completeness -->
<!-- column: item:B.8.2.6:rev_accuracy_sample -->
<!-- column: item:B.8.2.6:rev_customer_extract_test -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you review and confirm that your processor records of processing activities (RoPA) are accurate, up-to-date, and securely maintained, supporting your compliance with ISO 27701 privacy requirements.

## When to use it

Use this template if your organization is required to maintain a processor RoPA and your profile matches certain compliance triggers. Plan to complete this review about once a year to ensure records stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes filling out the required elements from scratch, with additional time needed if you have a large number of processing activities to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.2.6:program_review -->
| Rev Date | Rev Reviewer | Rev Completeness | Rev Accuracy Sample | Rev Customer Extract Test |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.2.6:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:B.8.2.6:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:B.8.2.6:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Trust Ops)

<<GUIDANCE>>

### Rev Completeness

<<MUST item:B.8.2.6:rev_completeness>>
_Why: §8.2.6 — necessary records_

> _Standard text:_ Completeness check — one RoPA row per active customer engagement

<<GUIDANCE>>

### Rev Accuracy Sample

<<MUST item:B.8.2.6:rev_accuracy_sample>>
_Why: Drift detection_

> _Standard text:_ Accuracy sample — random rows verified against customer instruction record + subprocessor list

<<GUIDANCE>>

### Rev Customer Extract Test

<<MUST item:B.8.2.6:rev_customer_extract_test>>
_Why: §8.2.5 cross-link_

> _Standard text:_ Customer-extract test — sampled customers requested + received their RoPA row within SLA

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:B.8.2.6:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
