---
leaf_id: req:B.8.5.7:program_review
control_ref: B.8.5.7
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Subcontractor Engagement Program Review

<<DOC_CONTROL>>

> Annual verification — every engagement has customer authorisation + Annex B flow-down (freshness=365)

<!-- TABLE-COLUMNS leaf:req:B.8.5.7:program_review -->
<!-- column: item:B.8.5.7:rev_date -->
<!-- column: item:B.8.5.7:rev_reviewer -->
<!-- column: item:B.8.5.7:rev_authorisation_audit -->
<!-- column: item:B.8.5.7:rev_flowdown_audit -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of all subcontractor engagements, ensuring each one has proper customer approval and includes the necessary privacy requirements. It's designed to support your compliance with privacy standards like ISO 27701.

## When to use it

Use this template whenever you engage a new subcontractor or review existing ones, especially if your business activities match specific compliance triggers. Plan to update it about once a year to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, depending on the number of subcontractors you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.5.7:program_review -->
| Rev Date | Rev Reviewer | Rev Authorisation Audit | Rev Flowdown Audit |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.5.7:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:B.8.5.7:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:B.8.5.7:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Procurement + Legal + DPO)

<<GUIDANCE>>

### Rev Authorisation Audit

<<MUST item:B.8.5.7:rev_authorisation_audit>>
_Why: §8.5.7_

> _Standard text:_ Authorisation audit — every engagement traceable to customer authorisation

<<GUIDANCE>>

### Rev Flowdown Audit

<<MUST item:B.8.5.7:rev_flowdown_audit>>
_Why: §8.5.7 — Annex B_

> _Standard text:_ Flow-down audit — sampled contracts verified against Annex B coverage

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:B.8.5.7:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
