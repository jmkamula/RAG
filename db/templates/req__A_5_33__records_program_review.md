---
leaf_id: req:A.5.33:records_program_review
control_ref: A.5.33
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Periodic Records Protection Program Review

<<DOC_CONTROL>>

> Periodic verification that the schedule reflects the scope, the procedure still matches the protection requirements per class, and disposal/legal-hold discipline is being followed. ISO 27002:2022 § 5.33 expects records protection to be maintained — drift between schedule and reality (new classes emerging, retention periods overrun, disposals not happening) is the audit failure mode this leaf catches. Annual cadence (freshness=365) matches the stable doctrine of records-management methodology

<!-- TABLE-COLUMNS leaf:req:A.5.33:records_program_review -->
<!-- column: item:A.5.33:rev_date -->
<!-- column: item:A.5.33:rev_reviewer -->
<!-- column: item:A.5.33:rev_schedule_check -->
<!-- column: item:A.5.33:rev_scope_check -->
<!-- column: item:A.5.33:rev_disposal_audit -->
<!-- column: item:A.5.33:rev_legal_hold_status -->
<!-- column: item:A.5.33:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you regularly check that your records management schedule matches your actual practices, ensuring you’re protecting records properly and following disposal or legal-hold rules. It’s designed to help you stay compliant with ISO 27001 requirements.

## When to use it

Use this template once a year to review your records protection program and confirm that your procedures and schedules are still accurate and up to date. It’s relevant for any environment where records management is required.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours completing this review from scratch, depending on the number of records classes and how much information you need to gather for each required section.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.33:records_program_review -->
| Rev Date | Rev Reviewer | Rev Schedule Check | Rev Scope Check | Rev Disposal Audit | Rev Legal Hold Status | Rev Register Update |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.33:records_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.33:rev_date>>
_Why: 27002:5.33 — maintained_

> _Standard text:_ Review date within the planned interval (typically within 12 months of last review)

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.5.33:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role recorded (records manager / compliance lead with legal-counsel sign-off where material)

<<GUIDANCE>>

### Rev Schedule Check

<<MUST item:A.5.33:rev_schedule_check>>
_Why: 27002:5.33 — kept current_

> _Standard text:_ Per-class outcome (verified / amended / retired / new added) with retention-still-adequate and protection-class-still-adequate confirmation

<<GUIDANCE>>

### Rev Scope Check

<<MUST item:A.5.33:rev_scope_check>>
_Why: Cross-leaf coherence_

> _Standard text:_ Cross-check against the records-categories scope — any new business activity / legal driver / data category that should add classes

<<GUIDANCE>>

### Rev Disposal Audit

<<MUST item:A.5.33:rev_disposal_audit>>
_Why: 27002:5.33 — disposal discipline_

> _Standard text:_ Disposal audit — sample of classes past retention end-date confirmed disposed (certificate of destruction present) or held under documented legal hold; overruns flagged for remediation

<<GUIDANCE>>

### Rev Legal Hold Status

<<MUST item:A.5.33:rev_legal_hold_status>>
_Why: 27002:5.33 — litigation readiness_

> _Standard text:_ Active legal-hold status reviewed (which classes/rows currently held, by whom, on what basis, expected release trigger) — stale unreleased holds remediated

<<GUIDANCE>>

### Rev Register Update

<<MUST item:A.5.33:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated back to the live schedule with reference to this review

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Ad Hoc Triggers

<<SHOULD item:A.5.33:rev_ad_hoc_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc review triggers listed (new regulator action, new sector entry, M&A, legal-hold invocation pattern shift)

<<GUIDANCE>>

### Rev Next Date

<<SHOULD item:A.5.33:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
