---
leaf_id: req:A.5.5:authority_contact_review
control_ref: A.5.5
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 2
---

# Periodic Authority Contact Review

> Periodic verification that the register is still accurate, the scope is still correct, and the maintenance procedure is being followed. ISO 27002:2022 § 5.5 expects contact to be maintained — drift between register and reality is the audit failure mode this leaf catches

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval (typically within 12 months of last review)

<<MUST item:A.5.5:rev_date>>
_Why: 27002:5.5 — maintained_

<<TEXT>>

## 2. Reviewer identity and role recorded

<<MUST item:A.5.5:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Per-entry outcome (verified / amended / removed) and the verification method used

<<MUST item:A.5.5:rev_per_entry>>
_Why: 27002:5.5 — maintained_

<<TEXT>>

## 4. Cross-check against the applicable-authorities scope (any new jurisdiction or sector that should add an entry)

<<MUST item:A.5.5:rev_scope_check>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. Changes propagated back to the live register with reference to this review

<<MUST item:A.5.5:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc review triggers listed (re-org, new geography, new sectoral obligation)

<<SHOULD item:A.5.5:rev_ad_hoc_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.5:rev_next_date>>
_Why: Planning_

<<TEXT>>
