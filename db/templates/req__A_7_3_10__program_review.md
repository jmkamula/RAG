---
leaf_id: req:A.7.3.10:program_review
control_ref: A.7.3.10
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Automated Decision Subject Obligations Program Review

<<DOC_CONTROL>>

> Annual verification — subject notification working, objection pathway healthy, human-intervention path functional, jurisdiction-prohibition scope current (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.3.10:program_review -->
<!-- column: item:A.7.3.10:rev_date -->
<!-- column: item:A.7.3.10:rev_reviewer -->
<!-- column: item:A.7.3.10:rev_notification_audit -->
<!-- column: item:A.7.3.10:rev_intervention_test -->
<!-- column: item:A.7.3.10:rev_jurisdiction_currency -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you confirm that your automated decision-making processes are transparent and that individuals can exercise their rights, such as being notified, objecting, or requesting human review.

## When to use it

Use this template when your organization uses automated decisions that impact individuals and you need to check these processes at least once a year, or whenever your risk profile changes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, depending on how many automated decision processes you have to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.10:program_review -->
| Rev Date | Rev Reviewer | Rev Notification Audit | Rev Intervention Test | Rev Jurisdiction Currency |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.10:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.3.10:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.3.10:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + ML/Product lead + Legal)

<<GUIDANCE>>

### Rev Notification Audit

<<MUST item:A.7.3.10:rev_notification_audit>>
_Why: §7.3.10 — notifying the existence_

> _Standard text:_ Notification audit — sampled A.22 systems verified to have subject-notification surfaced

<<GUIDANCE>>

### Rev Intervention Test

<<MUST item:A.7.3.10:rev_intervention_test>>
_Why: Art.22.3_

> _Standard text:_ Human-intervention pathway test

<<GUIDANCE>>

### Rev Jurisdiction Currency

<<MUST item:A.7.3.10:rev_jurisdiction_currency>>
_Why: §7.3.10 NOTE_

> _Standard text:_ Jurisdiction-currency check — new full-automation prohibitions surfaced

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.3.10:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
