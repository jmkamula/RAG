---
leaf_id: req:A.7.13:equipment_maintenance_procedure
control_ref: A.7.13
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# Equipment Maintenance Procedure

> A.7.13 requires equipment to be maintained correctly to ensure availability, integrity, and confidentiality. The procedure documents schedules, authorised providers, supervision, offsite-maintenance controls, post-verification. The maintenance event register, applicable-equipment scope and periodic review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Maintenance schedule per equipment class with intervals

<<MUST item:A.7.13:schedule>>
_Why: 27002:7.13 — maintained correctly_

<<TEXT>>

## 2. Authorised maintenance providers list with security expectations

<<MUST item:A.7.13:authorised_providers>>
_Why: 27002:7.13 — maintained_

<<TEXT>>

## 3. Supervision requirements when maintenance involves access to sensitive information

<<MUST item:A.7.13:supervision>>
_Why: 27002:7.13 — confidentiality_

<<TEXT>>

## 4. Asset-removal controls when equipment goes offsite (data removal, escrow, return verification)

<<MUST item:A.7.13:offsite_maintenance>>
_Why: 27002:7.13 — integrity, confidentiality_

<<TEXT>>

## 5. Post-maintenance verification (functional test, integrity check)

<<MUST item:A.7.13:post_verification>>
_Why: 27002:7.13 — availability, integrity_

<<TEXT>>

## 6. Provider selection criteria documented (security competence, background screening, NDA)

<<MUST item:A.7.13:provider_criteria>>
_Why: Supply chain hygiene_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Predictive maintenance based on monitoring data

<<SHOULD item:A.7.13:predictive_maint>>
_Why: Modern practice_

<<TEXT>>
