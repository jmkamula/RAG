---
leaf_id: req:A.7.3.1:program_review
control_ref: A.7.3.1
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Obligations Program Review

<<DOC_CONTROL>>

> Annual verification — obligations catalog current with regulatory landscape, fulfilment channels healthy, SLAs met, no missing obligations flagged (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.3.1:program_review -->
<!-- column: item:A.7.3.1:rev_date -->
<!-- column: item:A.7.3.1:rev_reviewer -->
<!-- column: item:A.7.3.1:rev_catalog_currency -->
<!-- column: item:A.7.3.1:rev_sla_audit -->
<!-- column: item:A.7.3.1:rev_channel_health -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your privacy-related obligations, making sure your records are up to date and that you’re meeting all necessary requirements under ISO 27701.

## When to use it

Use this review record once a year, or whenever your organization’s profile changes in a way that might affect your privacy obligations, to confirm your obligations catalog is current and nothing important is missing.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on how many obligations you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.1:program_review -->
| Rev Date | Rev Reviewer | Rev Catalog Currency | Rev Sla Audit | Rev Channel Health |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.1:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.3.1:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.3.1:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Legal)

<<GUIDANCE>>

### Rev Catalog Currency

<<MUST item:A.7.3.1:rev_catalog_currency>>
_Why: §7.3.1 — vary from one jurisdiction to another_

> _Standard text:_ Catalog currency — recent regulatory / case-law developments incorporated

<<GUIDANCE>>

### Rev Sla Audit

<<MUST item:A.7.3.1:rev_sla_audit>>
_Why: §7.3.1 — timely manner_

> _Standard text:_ SLA audit — sampled A.7.3.9 request register measured against catalog SLAs

<<GUIDANCE>>

### Rev Channel Health

<<MUST item:A.7.3.1:rev_channel_health>>
_Why: §7.3.1 — accessible_

> _Standard text:_ Channel health — fulfilment channels reachable + functional

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.3.1:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
