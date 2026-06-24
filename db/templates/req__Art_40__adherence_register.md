---
leaf_id: req:Art.40:adherence_register
control_ref: Art.40
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Code Adherence Register

> Per-code register listing adhered codes + status. Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row code identifier (name + association + approval reference)

<<MUST item:Art.40:reg_code_id>>
_Why: Audit_

<<TEXT>>

## 2. Per-row adherence date

<<MUST item:Art.40:reg_adherence_date>>
_Why: Currency_

<<TEXT>>

## 3. Per-row scope of adherence (which processing activities)

<<MUST item:Art.40:reg_scope>>
_Why: Defensibility_

<<TEXT>>

## 4. Per-row monitoring body engaged (Art.41)

<<MUST item:Art.40:reg_monitoring_body>>
_Why: Art.41_

<<TEXT>>

## 5. Per-row status (active / suspended / withdrawn-on-date)

<<MUST item:Art.40:reg_status>>
_Why: Lifecycle_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row last monitoring assessment date

<<SHOULD item:Art.40:reg_last_assessment>>
_Why: Currency_

<<TEXT>>
