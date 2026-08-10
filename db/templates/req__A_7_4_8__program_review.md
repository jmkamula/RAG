---
leaf_id: req:A.7.4.8:program_review
control_ref: A.7.4.8
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Disposal Program Review

<<DOC_CONTROL>>

> Annual verification — techniques current, certificates on file for every disposal, media lifecycle coverage complete (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.4.8:program_review -->
<!-- column: item:A.7.4.8:rev_date -->
<!-- column: item:A.7.4.8:rev_reviewer -->
<!-- column: item:A.7.4.8:rev_technique_currency -->
<!-- column: item:A.7.4.8:rev_certificate_audit -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of how your organization disposes of sensitive media, ensuring all disposal methods are up to date and that you have certificates for each disposal event.

## When to use it

Use this review record if your organization needs to regularly verify disposal practices, especially when your activities match certain privacy-related triggers. Plan to complete it about once a year.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes filling this out from scratch, depending on how many disposal events you need to document and how easily you can access the required information.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4.8:program_review -->
| Rev Date | Rev Reviewer | Rev Technique Currency | Rev Certificate Audit |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4.8:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.4.8:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.4.8:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Infrastructure + DPO)

<<GUIDANCE>>

### Rev Technique Currency

<<MUST item:A.7.4.8:rev_technique_currency>>
_Why: §7.4.8_

> _Standard text:_ Technique currency — techniques still appropriate given hardware / cloud evolution

<<GUIDANCE>>

### Rev Certificate Audit

<<MUST item:A.7.4.8:rev_certificate_audit>>
_Why: Audit trail_

> _Standard text:_ Certificate audit — sampled disposals have valid certificates

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.4.8:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
