---
leaf_id: req:A.7.2.1:program_review
control_ref: A.7.2.1
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Purpose Documentation Program Review

<<DOC_CONTROL>>

> Annual verification — every in-scope activity has a documented purpose, purposes remain specific + clear, no undocumented processing has emerged (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.2.1:program_review -->
<!-- column: item:A.7.2.1:rev_date -->
<!-- column: item:A.7.2.1:rev_reviewer -->
<!-- column: item:A.7.2.1:rev_coverage_check -->
<!-- column: item:A.7.2.1:rev_specificity_audit -->
<!-- column: item:A.7.2.1:rev_undocumented_sweep -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of the specific reasons for each activity that involves personal data, ensuring everything is clearly documented and up to date for privacy compliance.

## When to use it

Use this template once a year, or whenever your organization’s activities match certain privacy-related triggers, to confirm that all processing purposes are still accurate and nothing new has been missed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes completing this from scratch, depending on how many activities you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2.1:program_review -->
| Rev Date | Rev Reviewer | Rev Coverage Check | Rev Specificity Audit | Rev Undocumented Sweep |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2.1:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.2.1:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.2.1:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Privacy Office)

<<GUIDANCE>>

### Rev Coverage Check

<<MUST item:A.7.2.1:rev_coverage_check>>
_Why: §7.2.1 — every processing_

> _Standard text:_ Coverage check — every in-scope activity has a purpose registered

<<GUIDANCE>>

### Rev Specificity Audit

<<MUST item:A.7.2.1:rev_specificity_audit>>
_Why: §7.2.1 implementation guidance_

> _Standard text:_ Specificity audit — sampled purposes reviewed for clarity + non-vagueness

<<GUIDANCE>>

### Rev Undocumented Sweep

<<MUST item:A.7.2.1:rev_undocumented_sweep>>
_Why: Drift detection_

> _Standard text:_ Undocumented-processing sweep — new activities emerged since last review flagged for registration

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.2.1:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
