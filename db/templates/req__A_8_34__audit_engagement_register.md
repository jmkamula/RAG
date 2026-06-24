---
leaf_id: req:A.8.34:audit_engagement_register
control_ref: A.8.34
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Audit Testing Engagement Register

> Per-engagement catalogue — engagement id, tester, scope, dates, outcome, evidence-artefact location

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-engagement unique identifier

<<MUST item:A.8.34:reg_engagement_id>>
_Why: Identification_

<<TEXT>>

## 2. Per-engagement tester identity (internal team / external firm)

<<MUST item:A.8.34:reg_tester>>
_Why: Accountability_

<<TEXT>>

## 3. Per-engagement scope description (systems / data / techniques agreed)

<<MUST item:A.8.34:reg_scope>>
_Why: 27002:8.34 — agreed_

<<TEXT>>

## 4. Per-engagement start / end / time-windows

<<MUST item:A.8.34:reg_dates>>
_Why: 27002:8.34 — planned_

<<TEXT>>

## 5. Per-engagement outcome + findings count

<<MUST item:A.8.34:reg_outcome>>
_Why: Continuous evidence_

<<TEXT>>

## 6. Per-engagement evidence-artefact location reference

<<MUST item:A.8.34:reg_evidence_loc>>
_Why: 27002:8.34 — assessment_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-engagement rollback-invoked flag where applicable

<<SHOULD item:A.8.34:reg_rollback_invoked>>
_Why: Operational defensibility_

<<TEXT>>
