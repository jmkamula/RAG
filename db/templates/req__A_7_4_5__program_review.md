---
leaf_id: req:A.7.4.5:program_review
control_ref: A.7.4.5
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# End-of-Processing Program Review

<<DOC_CONTROL>>

> Annual verification — end-triggers fire reliably, verification passes, no PII lingering past end-of-processing, backup propagation working (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.4.5:program_review -->
<!-- column: item:A.7.4.5:rev_date -->
<!-- column: item:A.7.4.5:rev_reviewer -->
<!-- column: item:A.7.4.5:rev_trigger_health -->
<!-- column: item:A.7.4.5:rev_verification_audit -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you confirm that your end-of-processing steps are working as intended, ensuring no personal data remains and backups are up to date. It supports your compliance with ISO 27701 privacy requirements.

## When to use it

Use this review record whenever your data processing activities reach their end, especially if your operations match certain triggers. Plan to complete it about once a year to stay compliant.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes filling out the required sections from scratch, with additional time if you have multiple processing activities to review.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4.5:program_review -->
| Rev Date | Rev Reviewer | Rev Trigger Health | Rev Verification Audit |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4.5:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.4.5:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.4.5:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Data Ops + Infrastructure)

<<GUIDANCE>>

### Rev Trigger Health

<<MUST item:A.7.4.5:rev_trigger_health>>
_Why: §7.4.5_

> _Standard text:_ Trigger health — end-of-processing detection functioning across activity types

<<GUIDANCE>>

### Rev Verification Audit

<<MUST item:A.7.4.5:rev_verification_audit>>
_Why: Effectiveness_

> _Standard text:_ Verification audit — sampled actions verified to have removed PII across primary + backup

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.4.5:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
