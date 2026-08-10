---
leaf_id: req:Art.30:ropa_annual_review
control_ref: Art.30
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 3
table_shape: true
---

# RoPA Periodic Review Record

<<DOC_CONTROL>>

> Even with maintenance triggers in place, drift accumulates between RoPA and reality. An annual (or more frequent) review verifies each activity against current operations, propagates corrections back to the register, and produces auditable evidence that the register is not stale

<!-- TABLE-COLUMNS leaf:req:Art.30:ropa_annual_review -->
<!-- column: item:Art.30:rev_date -->
<!-- column: item:Art.30:rev_reviewer -->
<!-- column: item:Art.30:rev_outcome -->
<!-- column: item:Art.30:rev_register_update -->
<!-- column: item:Art.30:rev_gaps -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep your Record of Processing Activities (RoPA) accurate by guiding you through a structured review and update process, ensuring your records reflect your current operations and are ready for audits.

## When to use it

Use this template at least once a year, or more often if your operations change frequently, to review and update your RoPA and confirm it matches your actual data processing activities.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on the number of activities you need to review and update in your register.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.30:ropa_annual_review -->
| Rev Date | Rev Reviewer | Rev Outcome | Rev Register Update | Rev Gaps |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.30:ropa_annual_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.30:rev_date>>
_Why: Periodic accuracy_

> _Standard text:_ Review date within the planned interval (typically within 12 months of last review)

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.30:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role (DPO, privacy lead, or delegated equivalent)

<<GUIDANCE>>

### Rev Outcome

<<MUST item:Art.30:rev_outcome>>
_Why: Auditable result_

> _Standard text:_ Per-activity outcome (no change / amended / retired) recorded

<<GUIDANCE>>

### Rev Register Update

<<MUST item:Art.30:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated back to the live register with reference to this review

<<GUIDANCE>>

### Rev Gaps

<<MUST item:Art.30:rev_gaps>>
_Why: Defect tracking_

> _Standard text:_ Gaps identified (missing activity, outdated retention, undocumented transfer) with remediation owner and target date

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Ad Hoc Triggers

<<SHOULD item:Art.30:rev_ad_hoc_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc review triggers listed (re-org, M&A, new processing line, new processor onboarded)

<<GUIDANCE>>

### Rev Next Date

<<SHOULD item:Art.30:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

### Rev Dfi Alignment

<<SHOULD item:Art.30:rev_dfi_alignment>>
_Why: Cross-leaf coherence_

> _Standard text:_ Cross-check against the data flow inventory recorded — both should describe the same reality

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
