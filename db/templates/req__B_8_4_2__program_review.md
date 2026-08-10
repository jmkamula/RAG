---
leaf_id: req:B.8.4.2:program_review
control_ref: B.8.4.2
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# End-of-Service Program Review

<<DOC_CONTROL>>

> Annual verification — return / transfer / disposal working end-to-end, backup propagation reliable, certifications issued (freshness=365)

<!-- TABLE-COLUMNS leaf:req:B.8.4.2:program_review -->
<!-- column: item:B.8.4.2:rev_date -->
<!-- column: item:B.8.4.2:rev_reviewer -->
<!-- column: item:B.8.4.2:rev_completion_audit -->
<!-- column: item:B.8.4.2:rev_backup_propagation -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document and review how your organization handles the return, transfer, or disposal of data and equipment, ensuring backup processes work and certifications are up to date for privacy compliance.

## When to use it

Use this template when your organization’s activities match specific privacy-related triggers and you need to verify these processes annually, typically once every 12 months.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, depending on the number of items you need to review and record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.4.2:program_review -->
| Rev Date | Rev Reviewer | Rev Completion Audit | Rev Backup Propagation |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.4.2:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:B.8.4.2:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:B.8.4.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Trust + DPO + Platform Ops)

<<GUIDANCE>>

### Rev Completion Audit

<<MUST item:B.8.4.2:rev_completion_audit>>
_Why: Effectiveness_

> _Standard text:_ Completion audit — sampled terminations verified end-to-end (data returned + disposal certified)

<<GUIDANCE>>

### Rev Backup Propagation

<<MUST item:B.8.4.2:rev_backup_propagation>>
_Why: §8.4.2 — including backup + BC_

> _Standard text:_ Backup propagation audit — sampled disposals verified to have propagated to backup tiers

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:B.8.4.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
