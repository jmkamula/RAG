---
leaf_id: req:Art.34:subject_communication_record
control_ref: Art.34
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# Subject Communication Record

> Per-breach communication record — proves Art.34 communication was made (or documented exception applied). Annual refresh (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row breach id (Art.33 register cross-reference)

<<MUST item:Art.34:reg_breach_id>>
_Why: Cross-article_

<<TEXT>>

## 2. Per-row high-risk decision (high risk → communicate / no high risk → no communication, with rationale)

<<MUST item:Art.34:reg_high_risk_decision>>
_Why: Art.34.1_

<<TEXT>>

## 3. Per-row Art.34.3 exception cited (if claimed)

<<MUST item:Art.34:reg_exception_cited>>
_Why: Art.34.3_

<<TEXT>>

## 4. Per-row communication method (email + in-app / public notice / mixed)

<<MUST item:Art.34:reg_communication_method>>
_Why: Art.34.2_

<<TEXT>>

## 5. Per-row communication date

<<MUST item:Art.34:reg_communication_date>>
_Why: Currency_

<<TEXT>>

## 6. Per-row subjects-reached count (or 'unable to calculate, public communication used')

<<MUST item:Art.34:reg_subjects_reached>>
_Why: Effectiveness signal_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row SA concurrence where SA consulted (Art.34.4)

<<SHOULD item:Art.34:reg_sa_concurrence>>
_Why: Art.34.4_

<<TEXT>>
