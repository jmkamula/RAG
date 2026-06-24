---
leaf_id: req:A.8.30:outsourced_development_procedure
control_ref: A.8.30
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 1
---

# Outsourced Development Governance Procedure

> A.8.30 requires direction, monitoring, review of outsourced development. Procedure documents contractual-security, code controls, delivered-code testing, incident-notification, oversight rhythm. Per-engagement register, applicable scope, program review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Security requirements in development contracts (cross-link to A.5.20 supplier contracts)

<<MUST item:A.8.30:contractual_security>>
_Why: 27002:8.30 — direct_

<<TEXT>>

## 2. Code ownership / escrow / IP terms in contract

<<MUST item:A.8.30:code_ownership>>
_Why: 27002:8.30 — direct_

<<TEXT>>

## 3. Security testing of delivered code (cross-link to A.8.29; vendor cannot be sole tester)

<<MUST item:A.8.30:delivered_code_testing>>
_Why: 27002:8.30 — review_

<<TEXT>>

## 4. Source-code access controls for vendor (cross-link to A.8.4; vendor-account governance)

<<MUST item:A.8.30:source_code_controls>>
_Why: 27002:8.30 — direct_

<<TEXT>>

## 5. Incident-notification obligation in contract (vendor must notify within agreed window; cross-link to A.5.25/A.5.26)

<<MUST item:A.8.30:incident_notification>>
_Why: 27002:8.30 — monitor_

<<TEXT>>

## 6. Vendor security-maturity assessment before engagement (cross-link to A.5.19 supplier risk)

<<MUST item:A.8.30:maturity_assessment>>
_Why: Risk-based vendor selection (Style v2 promotion)_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Regular review-meeting cadence during engagement (cross-link to A.5.22)

<<SHOULD item:A.8.30:review_meetings>>
_Why: Active monitoring_

<<TEXT>>
