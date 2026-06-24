---
leaf_id: req:Art.18:restriction_register
control_ref: Art.18
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Restriction Register

> Per-restriction record proving active restrictions are in place with documented grounds. Annual refresh (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Subject identifier per row

<<MUST item:Art.18:reg_subject_id>>
_Why: Audit_

<<TEXT>>

## 2. Per-row Art.18.1 ground (a-d) cited

<<MUST item:Art.18:reg_ground>>
_Why: Art.18.1_

<<TEXT>>

## 3. Per-row scope (which data, which systems are restricted)

<<MUST item:Art.18:reg_scope>>
_Why: Implementation_

<<TEXT>>

## 4. Per-row restriction start date

<<MUST item:Art.18:reg_start_date>>
_Why: Currency_

<<TEXT>>

## 5. Per-row lift status (active / lifted-on-date with reason)

<<MUST item:Art.18:reg_lift_status>>
_Why: Art.18.3_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row Art.19 notification reference

<<SHOULD item:Art.18:reg_art19_xref>>
_Why: Cross-article coherence_

<<TEXT>>
