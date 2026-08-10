---
leaf_id: req:B.8.2.4:program_review
control_ref: B.8.2.4
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Infringing Instruction Program Review

<<DOC_CONTROL>>

> Annual verification — review triggers functional, notifications issued when required, escalation records intact (freshness=365)

<!-- TABLE-COLUMNS leaf:req:B.8.2.4:program_review -->
<!-- column: item:B.8.2.4:rev_date -->
<!-- column: item:B.8.2.4:rev_reviewer -->
<!-- column: item:B.8.2.4:rev_trigger_health -->
<!-- column: item:B.8.2.4:rev_notification_audit -->
<!-- column: item:B.8.2.4:rev_legislation_currency -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of how your organization reviews and manages instructions that could violate privacy requirements, ensuring all notifications and escalations are properly documented for ISO 27701 compliance.

## When to use it

Use this template whenever your organization’s activities match certain privacy-related triggers, and make sure to complete it about once a year to stay current with compliance requirements.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, depending on the number of review records you need to enter.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.2.4:program_review -->
| Rev Date | Rev Reviewer | Rev Trigger Health | Rev Notification Audit | Rev Legislation Currency |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.2.4:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:B.8.2.4:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:B.8.2.4:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Legal)

<<GUIDANCE>>

### Rev Trigger Health

<<MUST item:B.8.2.4:rev_trigger_health>>
_Why: Drift detection_

> _Standard text:_ Trigger health — sample of high-risk instruction categories reviewed for missed infringement flags

<<GUIDANCE>>

### Rev Notification Audit

<<MUST item:B.8.2.4:rev_notification_audit>>
_Why: §8.2.4 — inform the customer_

> _Standard text:_ Notification audit — sampled notifications reviewed for accuracy + timeliness

<<GUIDANCE>>

### Rev Legislation Currency

<<MUST item:B.8.2.4:rev_legislation_currency>>
_Why: Currency_

> _Standard text:_ Legislation currency — cited legislation updated for regulatory changes

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:B.8.2.4:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
