---
leaf_id: req:B.8.5.6:program_review
control_ref: B.8.5.6
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Subcontractor Disclosure Program Review

<<DOC_CONTROL>>

> Annual verification — pre-use disclosure honoured, disclosure content complete, NDA path used appropriately (freshness=365)

<!-- TABLE-COLUMNS leaf:req:B.8.5.6:program_review -->
<!-- column: item:B.8.5.6:rev_date -->
<!-- column: item:B.8.5.6:rev_reviewer -->
<!-- column: item:B.8.5.6:rev_pre_use_audit -->
<!-- column: item:B.8.5.6:rev_content_audit -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your subcontractor disclosures, making sure all required information is complete and up to date, and that NDAs are handled properly for privacy compliance.

## When to use it

Use this review record when your business activities involve subcontractors and you need to verify disclosures annually or whenever your profile matches certain privacy-related triggers.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, depending on the number of subcontractors you need to review and the detail required for each entry.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.5.6:program_review -->
| Rev Date | Rev Reviewer | Rev Pre Use Audit | Rev Content Audit |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.5.6:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:B.8.5.6:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:B.8.5.6:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Trust + Legal + DPO)

<<GUIDANCE>>

### Rev Pre Use Audit

<<MUST item:B.8.5.6:rev_pre_use_audit>>
_Why: §8.5.6 — before use_

> _Standard text:_ Pre-use audit — sampled subcontractor onboardings verified against disclosure record

<<GUIDANCE>>

### Rev Content Audit

<<MUST item:B.8.5.6:rev_content_audit>>
_Why: §8.5.6 implementation_

> _Standard text:_ Content audit — sampled disclosures include countries + obligations mechanism

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:B.8.5.6:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
