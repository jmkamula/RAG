---
leaf_id: req:A.7.5.2:program_review
control_ref: A.7.5.2
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Destinations Program Review

<<DOC_CONTROL>>

> Annual verification — destinations list current, public notice reflects register, subcontractor destinations captured (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.5.2:program_review -->
<!-- column: item:A.7.5.2:rev_date -->
<!-- column: item:A.7.5.2:rev_reviewer -->
<!-- column: item:A.7.5.2:rev_completeness -->
<!-- column: item:A.7.5.2:rev_public_notice_sync -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep an up-to-date record of all your data destinations, ensuring your public notices and internal registers are accurate and compliant with privacy standards.

## When to use it

Use this template once a year or whenever your organization’s profile changes in a way that affects your data destinations, such as adding new subcontractors or updating public notices.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, depending on how many destinations you need to list and review.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.5.2:program_review -->
| Rev Date | Rev Reviewer | Rev Completeness | Rev Public Notice Sync |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.5.2:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.5.2:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.5.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Trust + Legal)

<<GUIDANCE>>

### Rev Completeness

<<MUST item:A.7.5.2:rev_completeness>>
_Why: §7.5.2 — countries to which PII can be transferred_

> _Standard text:_ Completeness check — actual PII flows reconciled against register

<<GUIDANCE>>

### Rev Public Notice Sync

<<MUST item:A.7.5.2:rev_public_notice_sync>>
_Why: §7.5.2 — available to customers_

> _Standard text:_ Public notice sync — subject-facing destinations list matches register

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.5.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
