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
---

# RoPA Periodic Review Record

> Even with maintenance triggers in place, drift accumulates between RoPA and reality. An annual (or more frequent) review verifies each activity against current operations, propagates corrections back to the register, and produces auditable evidence that the register is not stale

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval (typically within 12 months of last review)

<<MUST item:Art.30:rev_date>>
_Why: Periodic accuracy_

<<TEXT>>

## 2. Reviewer identity and role (DPO, privacy lead, or delegated equivalent)

<<MUST item:Art.30:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Per-activity outcome (no change / amended / retired) recorded

<<MUST item:Art.30:rev_outcome>>
_Why: Auditable result_

<<TEXT>>

## 4. Changes propagated back to the live register with reference to this review

<<MUST item:Art.30:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

## 5. Gaps identified (missing activity, outdated retention, undocumented transfer) with remediation owner and target date

<<MUST item:Art.30:rev_gaps>>
_Why: Defect tracking_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc review triggers listed (re-org, M&A, new processing line, new processor onboarded)

<<SHOULD item:Art.30:rev_ad_hoc_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:Art.30:rev_next_date>>
_Why: Planning_

<<TEXT>>

### 3. Cross-check against the data flow inventory recorded — both should describe the same reality

<<SHOULD item:Art.30:rev_dfi_alignment>>
_Why: Cross-leaf coherence_

<<TEXT>>
