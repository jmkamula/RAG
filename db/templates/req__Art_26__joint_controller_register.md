---
leaf_id: req:Art.26:joint_controller_register
control_ref: Art.26
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Joint Controller Register

> Per-relationship record for every active joint-controller arrangement. Annual refresh (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row joint-controller counterparty

<<MUST item:Art.26:reg_counterparty>>
_Why: Audit_

<<TEXT>>

## 2. Per-row processing activity (Art.30 RoPA reference)

<<MUST item:Art.26:reg_activity>>
_Why: Cross-article_

<<TEXT>>

## 3. Per-row responsibility split summary

<<MUST item:Art.26:reg_responsibilities>>
_Why: Art.26.1_

<<TEXT>>

## 4. Per-row essence-of-arrangement published location (privacy notice URL)

<<MUST item:Art.26:reg_essence_published>>
_Why: Art.26.2_

<<TEXT>>

## 5. Per-row arrangement signature date

<<MUST item:Art.26:reg_signed_date>>
_Why: Currency_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row next-review date

<<SHOULD item:Art.26:reg_review_date>>
_Why: Planning_

<<TEXT>>
