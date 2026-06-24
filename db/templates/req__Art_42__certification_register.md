---
leaf_id: req:Art.42:certification_register
control_ref: Art.42
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Certification Register

> Per-certification record (active + past). Annual refresh (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row certification identifier

<<MUST item:Art.42:reg_certification_id>>
_Why: Audit_

<<TEXT>>

## 2. Per-row scheme + Art.43 body

<<MUST item:Art.42:reg_scheme>>
_Why: Art.42.5_

<<TEXT>>

## 3. Per-row processing scope covered

<<MUST item:Art.42:reg_scope>>
_Why: Art.42.7_

<<TEXT>>

## 4. Per-row validity end date (max 3 years from issue)

<<MUST item:Art.42:reg_valid_until>>
_Why: Art.42.7_

<<TEXT>>

## 5. Per-row status (active / under renewal / withdrawn)

<<MUST item:Art.42:reg_status>>
_Why: Lifecycle_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row surveillance audit dates

<<SHOULD item:Art.42:reg_surveillance_dates>>
_Why: Cadence_

<<TEXT>>
