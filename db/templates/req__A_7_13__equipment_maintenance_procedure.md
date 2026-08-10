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

<<DOC_CONTROL>>

> A.7.13 requires equipment to be maintained correctly to ensure availability, integrity, and confidentiality. The procedure documents schedules, authorised providers, supervision, offsite-maintenance controls, post-verification. The maintenance event register, applicable-equipment scope and periodic review are sibling leaves

## What this template gives you

This template helps you create a clear, step-by-step procedure for maintaining your equipment, including schedules, approved providers, and checks after maintenance. It ensures your equipment stays reliable and secure, meeting ISO 27001 requirements.

## When to use it

Use this template if you have equipment that needs regular maintenance and you want to document how it's managed. It should be reviewed and updated about once a year, or whenever your equipment or maintenance process changes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 2 hours filling out this template from scratch, depending on how many pieces of equipment and maintenance providers you need to include.

## 1. Maintenance schedule per equipment class with intervals

<<MUST item:A.7.13:schedule>>
_Why: 27002:7.13 — maintained correctly_

<<GUIDANCE>>

<<TEXT>>

## 2. Authorised maintenance providers list with security expectations

<<MUST item:A.7.13:authorised_providers>>
_Why: 27002:7.13 — maintained_

<<GUIDANCE>>

<<TEXT>>

## 3. Supervision requirements when maintenance involves access to sensitive information

<<MUST item:A.7.13:supervision>>
_Why: 27002:7.13 — confidentiality_

<<GUIDANCE>>

<<TEXT>>

## 4. Asset-removal controls when equipment goes offsite (data removal, escrow, return verification)

<<MUST item:A.7.13:offsite_maintenance>>
_Why: 27002:7.13 — integrity, confidentiality_

<<GUIDANCE>>

<<TEXT>>

## 5. Post-maintenance verification (functional test, integrity check)

<<MUST item:A.7.13:post_verification>>
_Why: 27002:7.13 — availability, integrity_

<<GUIDANCE>>

<<TEXT>>

## 6. Provider selection criteria documented (security competence, background screening, NDA)

<<MUST item:A.7.13:provider_criteria>>
_Why: Supply chain hygiene_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Predictive maintenance based on monitoring data

<<SHOULD item:A.7.13:predictive_maint>>
_Why: Modern practice_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
