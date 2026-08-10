---
leaf_id: req:A.7.2.8:program_review
control_ref: A.7.2.8
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# RoPA Program Review

<<DOC_CONTROL>>

> Annual verification — RoPA is complete + accurate + current, cross-register integrity holds, owner accountability functional (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.2.8:program_review -->
<!-- column: item:A.7.2.8:rev_date -->
<!-- column: item:A.7.2.8:rev_reviewer -->
<!-- column: item:A.7.2.8:rev_completeness -->
<!-- column: item:A.7.2.8:rev_accuracy_sample -->
<!-- column: item:A.7.2.8:rev_owner_signoff -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you confirm that your Record of Processing Activities (RoPA) is up-to-date, accurate, and meets privacy standards. It also checks that responsibilities and cross-register links are working as intended.

## When to use it

Use this review each year, or whenever your data processing profile changes in a way that requires a fresh look at your RoPA. It's especially important if your activities trigger privacy compliance checks.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, depending on the number of entries in your register and the detail needed for each required section.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2.8:program_review -->
| Rev Date | Rev Reviewer | Rev Completeness | Rev Accuracy Sample | Rev Owner Signoff |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2.8:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.2.8:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.2.8:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Data Protection Council)

<<GUIDANCE>>

### Rev Completeness

<<MUST item:A.7.2.8:rev_completeness>>
_Why: §7.2.8 — accurate + complete_

> _Standard text:_ Completeness check — RoPA rowcount matches A.7.2.1 register + system inventory

<<GUIDANCE>>

### Rev Accuracy Sample

<<MUST item:A.7.2.8:rev_accuracy_sample>>
_Why: Drift detection_

> _Standard text:_ Accuracy sample — random rows verified against source systems

<<GUIDANCE>>

### Rev Owner Signoff

<<MUST item:A.7.2.8:rev_owner_signoff>>
_Why: §7.2.8 — owner responsible_

> _Standard text:_ Owner signoff — designated RoPA owner attests to accuracy + completeness

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.2.8:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
