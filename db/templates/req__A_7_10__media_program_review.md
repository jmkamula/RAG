---
leaf_id: req:A.7.10:media_program_review
control_ref: A.7.10
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Storage Media Program Review

<<DOC_CONTROL>>

> Annual verification of register currency, lifecycle compliance, lost-media incidents. Freshness=365

<!-- TABLE-COLUMNS leaf:req:A.7.10:media_program_review -->
<!-- column: item:A.7.10:rev_date -->
<!-- column: item:A.7.10:rev_reviewer -->
<!-- column: item:A.7.10:rev_inventory_audit -->
<!-- column: item:A.7.10:rev_lost_count -->
<!-- column: item:A.7.10:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your storage media, making sure your records are up-to-date and that you’re following proper procedures for handling and reporting lost media.

## When to use it

Use this review record every year to confirm your storage media register is current and compliant. It’s relevant for any environment where storage media is managed or tracked.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, depending on the number of storage media items you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.10:media_program_review -->
| Rev Date | Rev Reviewer | Rev Inventory Audit | Rev Lost Count | Rev Register Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.10:media_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.10:rev_date>>
_Why: 27002:7.10 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.10:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (IT + InfoSec)

<<GUIDANCE>>

### Rev Inventory Audit

<<MUST item:A.7.10:rev_inventory_audit>>
_Why: Loss detection_

> _Standard text:_ Inventory audit — sample-based confirmation of media at stated location

<<GUIDANCE>>

### Rev Lost Count

<<MUST item:A.7.10:rev_lost_count>>
_Why: 27002:7.10 — protected_

> _Standard text:_ Lost-media count for period (every loss has an incident link)

<<GUIDANCE>>

### Rev Register Update

<<MUST item:A.7.10:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the register / procedure

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.10:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
