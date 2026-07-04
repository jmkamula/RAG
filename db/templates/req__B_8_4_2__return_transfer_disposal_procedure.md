---
leaf_id: req:B.8.4.2:return_transfer_disposal_procedure
control_ref: B.8.4.2
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 1
---

# PII Return / Transfer / Disposal Procedure

> §8.4.2 requires the processor to be able to return / transfer / dispose of PII securely at end of service + make the disposal policy available to the customer. Bridges to GDPR Art.28.3.g.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Return capability — export PII to customer in structured format at end of service

<<MUST item:B.8.4.2:proc_return_capability>>
_Why: §8.4.2 — return_

<<TEXT>>

## 2. Transfer capability — hand PII to nominated third party at customer request

<<MUST item:B.8.4.2:proc_transfer_capability>>
_Why: §8.4.2 — transfer_

<<TEXT>>

## 3. Secure disposal capability — including from backups + DR + continuity systems

<<MUST item:B.8.4.2:proc_disposal_capability>>
_Why: §8.4.2 — from wherever stored, including backups_

<<TEXT>>

## 4. Customer visibility — disposal policy made available to customer on request

<<MUST item:B.8.4.2:proc_customer_visibility>>
_Why: §8.4.2 — make policy available_

<<TEXT>>

## 5. Lapse-of-contract protection — retention period defined before disposal after contract termination (accidental lapse protection)

<<MUST item:B.8.4.2:proc_lapse_protection>>
_Why: §8.4.2 — protection from accidental lapse_

<<TEXT>>

## 6. Certification / attestation of completion issued to customer

<<MUST item:B.8.4.2:proc_certification>>
_Why: Art.28.3.g proof_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (Trust + Platform Ops)

<<SHOULD item:B.8.4.2:proc_owner>>
_Why: Accountability_

<<TEXT>>
