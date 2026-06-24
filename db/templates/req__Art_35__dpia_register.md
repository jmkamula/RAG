---
leaf_id: req:Art.35:dpia_register
control_ref: Art.35
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# DPIA Register

> Per-DPIA record — every conducted DPIA with outcome (proceed / mitigate / Art.36 consult / abandon). Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row DPIA identifier

<<MUST item:Art.35:reg_dpia_id>>
_Why: Audit_

<<TEXT>>

## 2. Per-row processing activity (Art.30 RoPA cross-reference)

<<MUST item:Art.35:reg_processing_activity>>
_Why: Cross-article_

<<TEXT>>

## 3. Per-row trigger (Art.35.3.a-c / SA list / sectoral / risk-based)

<<MUST item:Art.35:reg_trigger>>
_Why: Art.35.1+3-4_

<<TEXT>>

## 4. Per-row DPO advice date + summary

<<MUST item:Art.35:reg_dpo_advice_date>>
_Why: Art.35.2_

<<TEXT>>

## 5. Per-row outcome (proceed / mitigate-then-proceed / Art.36 consult / abandon)

<<MUST item:Art.35:reg_outcome>>
_Why: Audit clarity_

<<TEXT>>

## 6. Per-row residual-risk level after mitigations

<<MUST item:Art.35:reg_residual_risk>>
_Why: Art.36 trigger_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row next review date

<<SHOULD item:Art.35:reg_review_date>>
_Why: Art.35.11_

<<TEXT>>
