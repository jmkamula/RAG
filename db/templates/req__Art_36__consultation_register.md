---
leaf_id: req:Art.36:consultation_register
control_ref: Art.36
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# Prior Consultation Register

> Per-consultation record. Annual refresh (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row consultation id

<<MUST item:Art.36:reg_consultation_id>>
_Why: Audit_

<<TEXT>>

## 2. Per-row DPIA cross-reference (Art.35 register entry)

<<MUST item:Art.36:reg_dpia_xref>>
_Why: Cross-article_

<<TEXT>>

## 3. Per-row submission date to SA

<<MUST item:Art.36:reg_submission_date>>
_Why: Currency_

<<TEXT>>

## 4. Per-row supervisory authority engaged

<<MUST item:Art.36:reg_sa>>
_Why: Art.55-56_

<<TEXT>>

## 5. Per-row outcome (approved / approved-with-conditions / advised-against)

<<MUST item:Art.36:reg_outcome>>
_Why: Art.36.2_

<<TEXT>>

## 6. Per-row controller decision after SA advice (proceed / modify / abandon)

<<MUST item:Art.36:reg_decision_to_proceed>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row SA response date

<<SHOULD item:Art.36:reg_response_date>>
_Why: Audit clarity_

<<TEXT>>
