---
leaf_id: req:A.7.3:rooms_program_review
control_ref: A.7.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Rooms Program Review

<<DOC_CONTROL>>

> Annual verification of room classifications, locking standards in place, and currency of the register (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.3:rooms_program_review -->
<!-- column: item:A.7.3:rev_date -->
<!-- column: item:A.7.3:rev_reviewer -->
<!-- column: item:A.7.3:rev_walkthrough -->
<!-- column: item:A.7.3:rev_register_check -->
<!-- column: item:A.7.3:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep an up-to-date record of all rooms, their classifications, and locking standards, making it easier to demonstrate compliance with ISO 27001 requirements.

## When to use it

Use this template once a year to review and verify your room classifications, locking standards, and ensure your register is current. It applies to all environments where secure rooms are managed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on the number of rooms you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3:rooms_program_review -->
| Rev Date | Rev Reviewer | Rev Walkthrough | Rev Register Check | Rev Register Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3:rooms_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.3:rev_date>>
_Why: 27002:7.3 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.3:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Facilities + InfoSec)

<<GUIDANCE>>

### Rev Walkthrough

<<MUST item:A.7.3:rev_walkthrough>>
_Why: 27002:7.3 — verified_

> _Standard text:_ Physical walkthrough conducted (sample-based) — locking standards verified, signage compliant

<<GUIDANCE>>

### Rev Register Check

<<MUST item:A.7.3:rev_register_check>>
_Why: 27002:7.3 — current_

> _Standard text:_ Per-room outcome (verified / amended / retired / new added)

<<GUIDANCE>>

### Rev Register Update

<<MUST item:A.7.3:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the live register

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.3:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
