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

<<DOC_CONTROL>>

> §8.4.2 requires the processor to be able to return / transfer / dispose of PII securely at end of service + make the disposal policy available to the customer. Bridges to GDPR Art.28.3.g.

## What this template gives you

This template helps you create a clear procedure for securely returning, transferring, or disposing of personal data at the end of a service relationship, as required by privacy standards like ISO 27701 and GDPR.

## When to use it

Use this document whenever your organization needs to outline how personal data will be handled at the end of a contract or service, and update it whenever your processes or legal requirements change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 2 hours drafting this procedure from scratch, as each required section will take roughly 10-15 minutes to complete.

## 1. Return capability — export PII to customer in structured format at end of service

<<MUST item:B.8.4.2:proc_return_capability>>
_Why: §8.4.2 — return_

<<GUIDANCE>>

<<TEXT>>

## 2. Transfer capability — hand PII to nominated third party at customer request

<<MUST item:B.8.4.2:proc_transfer_capability>>
_Why: §8.4.2 — transfer_

<<GUIDANCE>>

<<TEXT>>

## 3. Secure disposal capability — including from backups + DR + continuity systems

<<MUST item:B.8.4.2:proc_disposal_capability>>
_Why: §8.4.2 — from wherever stored, including backups_

<<GUIDANCE>>

<<TEXT>>

## 4. Customer visibility — disposal policy made available to customer on request

<<MUST item:B.8.4.2:proc_customer_visibility>>
_Why: §8.4.2 — make policy available_

<<GUIDANCE>>

<<TEXT>>

## 5. Lapse-of-contract protection — retention period defined before disposal after contract termination (accidental lapse protection)

<<MUST item:B.8.4.2:proc_lapse_protection>>
_Why: §8.4.2 — protection from accidental lapse_

<<GUIDANCE>>

<<TEXT>>

## 6. Certification / attestation of completion issued to customer

<<MUST item:B.8.4.2:proc_certification>>
_Why: Art.28.3.g proof_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (Trust + Platform Ops)

<<SHOULD item:B.8.4.2:proc_owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
