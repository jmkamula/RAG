---
leaf_id: req:Art.13:privacy_notice_program_review
control_ref: Art.13
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Privacy Notice Program Review

<<DOC_CONTROL>>

> Annual verification that the notice content is current with actual processing, the publication record reflects all deployed versions, every collection point still presents the notice (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.13:privacy_notice_program_review -->
<!-- column: item:Art.13:rev_date -->
<!-- column: item:Art.13:rev_reviewer -->
<!-- column: item:Art.13:rev_content_currency -->
<!-- column: item:Art.13:rev_collection_coverage -->
<!-- column: item:Art.13:rev_publication_archive -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your privacy notice reviews, making sure your notices are up to date and accurately reflect your data practices at every collection point.

## When to use it

Use this template whenever you need to confirm that your privacy notice is current and properly displayed, typically once a year as part of your regular compliance checks.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on how many collection points and notice versions you need to review.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.13:privacy_notice_program_review -->
| Rev Date | Rev Reviewer | Rev Content Currency | Rev Collection Coverage | Rev Publication Archive |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.13:privacy_notice_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.13:rev_date>>
_Why: Art.5.2 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.13:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO or Privacy Lead)

<<GUIDANCE>>

### Rev Content Currency

<<MUST item:Art.13:rev_content_currency>>
_Why: Cross-article coherence_

> _Standard text:_ Content currency check — notice reflects current Art.30 RoPA + Art.6 basis register

<<GUIDANCE>>

### Rev Collection Coverage

<<MUST item:Art.13:rev_collection_coverage>>
_Why: Drift detection_

> _Standard text:_ Coverage check — every in-scope collection point still presents the current notice

<<GUIDANCE>>

### Rev Publication Archive

<<MUST item:Art.13:rev_publication_archive>>
_Why: Art.5.2_

> _Standard text:_ Publication archive check — prior versions retained for audit defensibility

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.13:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
