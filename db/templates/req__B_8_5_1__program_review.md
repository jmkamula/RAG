---
leaf_id: req:B.8.5.1:program_review
control_ref: B.8.5.1
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Processor Transfer Basis Program Review

<<DOC_CONTROL>>

> Annual verification — customer notifications timely, change-advance notification honoured, basis currency intact (freshness=365)

<!-- TABLE-COLUMNS leaf:req:B.8.5.1:program_review -->
<!-- column: item:B.8.5.1:rev_date -->
<!-- column: item:B.8.5.1:rev_reviewer -->
<!-- column: item:B.8.5.1:rev_notification_audit -->
<!-- column: item:B.8.5.1:rev_basis_currency -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of how you notify customers about data transfers and ensures you’re following the right procedures each year. It’s designed to support privacy compliance and keep your records organized.

## When to use it

Use this review record if your organization handles customer data transfers and needs to confirm, once a year, that notifications are timely and changes are communicated in advance. It’s especially relevant if your activities match certain privacy-related triggers.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, as each required section takes around 10-15 minutes. If you have multiple transfers to log, allow extra time for each additional entry.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.5.1:program_review -->
| Rev Date | Rev Reviewer | Rev Notification Audit | Rev Basis Currency |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.5.1:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:B.8.5.1:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:B.8.5.1:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Legal + Trust)

<<GUIDANCE>>

### Rev Notification Audit

<<MUST item:B.8.5.1:rev_notification_audit>>
_Why: §8.5.1 — inform in advance_

> _Standard text:_ Notification audit — advance-notification obligations verified for all changes since last review

<<GUIDANCE>>

### Rev Basis Currency

<<MUST item:B.8.5.1:rev_basis_currency>>
_Why: Post-Schrems compliance_

> _Standard text:_ Basis currency — Art.45 adequacy currency + Art.46 SCC version currency

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:B.8.5.1:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
