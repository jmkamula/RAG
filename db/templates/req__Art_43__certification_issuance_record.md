---
leaf_id: req:Art.43:certification_issuance_record
control_ref: Art.43
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Certification Issuance Record

> Per-certificate issuance record. Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row certificate recipient

<<MUST item:Art.43:reg_recipient>>
_Why: Audit_

<<TEXT>>

## 2. Per-row assessment outcome with assessor identity

<<MUST item:Art.43:reg_assessment>>
_Why: Art.43.2.c_

<<TEXT>>

## 3. Per-row decision date + decision (issue / renew / withdraw / refuse)

<<MUST item:Art.43:reg_decision_date>>
_Why: Currency_

<<TEXT>>

## 4. Per-row decision grounds (criteria-mapped)

<<MUST item:Art.43:reg_grounds>>
_Why: Art.43.5_

<<TEXT>>

## 5. Per-row validity period (max 3 years per Art.42.7)

<<MUST item:Art.43:reg_validity>>
_Why: Art.42.7_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row complaint handling where contested

<<SHOULD item:Art.43:reg_complaint>>
_Why: Art.43.2.d_

<<TEXT>>
