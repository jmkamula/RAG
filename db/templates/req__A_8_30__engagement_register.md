---
leaf_id: req:A.8.30:engagement_register
control_ref: A.8.30
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 1
---

# Outsourced Development Engagement Register

> Per-engagement catalogue — vendor id, scope, contract reference, maturity-assessment outcome, delivered-code-test status

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-engagement unique identifier

<<MUST item:A.8.30:reg_engagement_id>>
_Why: Identification_

<<TEXT>>

## 2. Per-engagement vendor (cross-link to A.5.19 supplier register)

<<MUST item:A.8.30:reg_vendor>>
_Why: Cross-control coherence_

<<TEXT>>

## 3. Per-engagement scope description (what's being developed; data classes touched)

<<MUST item:A.8.30:reg_scope>>
_Why: 27002:8.30 — direct_

<<TEXT>>

## 4. Per-engagement contract reference (cross-link to A.5.20)

<<MUST item:A.8.30:reg_contract_ref>>
_Why: Cross-control coherence_

<<TEXT>>

## 5. Per-engagement maturity-assessment outcome

<<MUST item:A.8.30:reg_maturity_outcome>>
_Why: Risk-based vendor selection_

<<TEXT>>

## 6. Per-engagement delivered-code-test status (latest review outcome)

<<MUST item:A.8.30:reg_delivered_test_status>>
_Why: 27002:8.30 — review_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-engagement named owner (Engineering sponsor + Procurement partner)

<<SHOULD item:A.8.30:reg_owner>>
_Why: Accountability_

<<TEXT>>
