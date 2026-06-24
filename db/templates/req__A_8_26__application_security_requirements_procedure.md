---
leaf_id: req:A.8.26:application_security_requirements_procedure
control_ref: A.8.26
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 1
---

# Application Security Requirements Procedure

> A.8.26 requires security requirements identified, specified, approved during development/acquisition. Procedure documents intake step, requirement categories, approval, traceability. Per-application register, applicable scope, program review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Security-requirements gathering step at project initiation (cross-link to A.5.8 project + A.8.25 SDLC)

<<MUST item:A.8.26:requirements_step>>
_Why: 27002:8.26 — identified, specified_

<<TEXT>>

## 2. Requirement categories (authn / authz / data-protection / logging / error-handling / integrations / privacy)

<<MUST item:A.8.26:requirement_types>>
_Why: 27002:8.26 — information security requirements_

<<TEXT>>

## 3. Approval authority for requirements before development / procurement proceeds (InfoSec + business sponsor)

<<MUST item:A.8.26:approval>>
_Why: 27002:8.26 — approved_

<<TEXT>>

## 4. Traceability from requirements into design / code / test cases (auditor-defensible chain)

<<MUST item:A.8.26:traceability>>
_Why: 27002:8.26 — specified_

<<TEXT>>

## 5. Threat modelling at design phase (modern baseline — STRIDE / LINDDUN / kill-chain analysis as appropriate)

<<MUST item:A.8.26:threat_modeling>>
_Why: Modern baseline (Style v2 promotion)_

<<TEXT>>

## 6. Exception process for requirements that cannot be met (compensating-control + expiry)

<<MUST item:A.8.26:exception>>
_Why: Pragmatic adoption_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Security stories integrated into agile backlog (modern delivery alignment)

<<SHOULD item:A.8.26:security_stories>>
_Why: Modern delivery_

<<TEXT>>
