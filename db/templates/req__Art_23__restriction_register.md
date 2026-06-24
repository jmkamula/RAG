---
leaf_id: req:Art.23:restriction_register
control_ref: Art.23
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Art.23 Restriction Application Register

> Per-invocation record — every time an Art.23 restriction is applied to deny / limit a subject right. Annual refresh (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Unique invocation identifier per row

<<MUST item:Art.23:reg_invocation_id>>
_Why: Audit_

<<TEXT>>

## 2. Per-row Member State law cited (article + section)

<<MUST item:Art.23:reg_law_citation>>
_Why: Art.23.1_

<<TEXT>>

## 3. Per-row right restricted (Art.12-22 + Art.34)

<<MUST item:Art.23:reg_right_restricted>>
_Why: Art.23.1_

<<TEXT>>

## 4. Per-row Art.23.1 a-j purpose

<<MUST item:Art.23:reg_purpose>>
_Why: Art.23.1_

<<TEXT>>

## 5. Per-row subject notice (where required by Art.23.2.h)

<<MUST item:Art.23:reg_subject_notice>>
_Why: Art.23.2.h_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row legal counsel sign-off

<<SHOULD item:Art.23:reg_legal_review>>
_Why: Defensibility_

<<TEXT>>
