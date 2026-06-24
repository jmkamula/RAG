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
---

# Periodic Records Protection Program Review

> Periodic verification that the schedule reflects the scope, the procedure still matches the protection requirements per class, and disposal/legal-hold discipline is being followed. ISO 27002:2022 § 5.33 expects records protection to be maintained — drift between schedule and reality (new classes emerging, retention periods overrun, disposals not happening) is the audit failure mode this leaf catches. Annual cadence (freshness=365) matches the stable doctrine of records-management methodology

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval (typically within 12 months of last review)

<<MUST item:A.5.33:rev_date>>
_Why: 27002:5.33 — maintained_

<<TEXT>>

## 2. Reviewer identity and role recorded (records manager / compliance lead with legal-counsel sign-off where material)

<<MUST item:A.5.33:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Per-class outcome (verified / amended / retired / new added) with retention-still-adequate and protection-class-still-adequate confirmation

<<MUST item:A.5.33:rev_schedule_check>>
_Why: 27002:5.33 — kept current_

<<TEXT>>

## 4. Cross-check against the records-categories scope — any new business activity / legal driver / data category that should add classes

<<MUST item:A.5.33:rev_scope_check>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. Disposal audit — sample of classes past retention end-date confirmed disposed (certificate of destruction present) or held under documented legal hold; overruns flagged for remediation

<<MUST item:A.5.33:rev_disposal_audit>>
_Why: 27002:5.33 — disposal discipline_

<<TEXT>>

## 6. Active legal-hold status reviewed (which classes/rows currently held, by whom, on what basis, expected release trigger) — stale unreleased holds remediated

<<MUST item:A.5.33:rev_legal_hold_status>>
_Why: 27002:5.33 — litigation readiness_

<<TEXT>>

## 7. Changes propagated back to the live schedule with reference to this review

<<MUST item:A.5.33:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc review triggers listed (new regulator action, new sector entry, M&A, legal-hold invocation pattern shift)

<<SHOULD item:A.5.33:rev_ad_hoc_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.33:rev_next_date>>
_Why: Planning_

<<TEXT>>
