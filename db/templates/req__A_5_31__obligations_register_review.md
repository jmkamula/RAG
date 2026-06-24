---
leaf_id: req:A.5.31:obligations_register_review
control_ref: A.5.31
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 6
should_count: 2
---

# Periodic Legal/Regulatory Register Review

> Periodic verification that the register still reflects current obligations and that the compliance approach for each is still adequate. The cadence is semi-annual (freshness=180) because regulatory change is faster than annual; this matches the prior single-leaf freshness signal

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval (within 6 months of last review)

<<MUST item:A.5.31:rev_date>>
_Why: 27002:5.31 — kept up to date_

<<TEXT>>

## 2. Reviewer identity and role recorded (compliance lead with legal-counsel sign-off where material)

<<MUST item:A.5.31:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Per-entry outcome (verified / amended / retired / new added) with compliance-approach still-adequate confirmation

<<MUST item:A.5.31:rev_per_entry>>
_Why: 27002:5.31b_

<<TEXT>>

## 4. Cross-check against the applicable-obligations scope — any new applicability that should add entries

<<MUST item:A.5.31:rev_scope_check>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. Forward-looking section — obligations entering force in the next 12-24 months that need preparation

<<MUST item:A.5.31:rev_horizon>>
_Why: Forward-looking compliance_

<<TEXT>>

## 6. Changes propagated back to the live register with reference to this review

<<MUST item:A.5.31:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc review triggers listed (major regulator action, court ruling, customer contract restructure)

<<SHOULD item:A.5.31:rev_ad_hoc_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.31:rev_next_date>>
_Why: Planning_

<<TEXT>>
