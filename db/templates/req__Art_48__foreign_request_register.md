---
leaf_id: req:Art.48:foreign_request_register
control_ref: Art.48
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Foreign Authority Request Register

> Per-request record (most orgs will have empty register — that's a defensible outcome). Annual refresh (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row request id (or 'no requests this period' affirmative statement)

<<MUST item:Art.48:reg_request_id>>
_Why: Audit_

<<TEXT>>

## 2. Per-row requesting authority + jurisdiction

<<MUST item:Art.48:reg_authority>>
_Why: Defensibility_

<<TEXT>>

## 3. Per-row legal-basis check outcome (international agreement / Art.49 derogation / refused)

<<MUST item:Art.48:reg_legal_basis_check>>
_Why: Art.48_

<<TEXT>>

## 4. Per-row decision (disclosed / partially-disclosed / refused)

<<MUST item:Art.48:reg_decision>>
_Why: Audit clarity_

<<TEXT>>

## 5. Per-row decision date

<<MUST item:Art.48:reg_date>>
_Why: Currency_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row legal counsel review evidence

<<SHOULD item:Art.48:reg_legal_review>>
_Why: Defensibility_

<<TEXT>>
