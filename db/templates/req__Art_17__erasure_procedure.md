---
leaf_id: req:Art.17:erasure_procedure
control_ref: Art.17
standard_id: GDPR:2016/679
evidence_type: erasure_procedure
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 8
should_count: 2
---

# Erasure procedure (Art.17)

<<DOC_CONTROL>>

> Art.17 requires the controller to erase personal data without undue delay on any of the six grounds, subject to the Art.17.3 exceptions. The procedure must cover intake, identity verification, ground assessment, exception assessment (with documented refusal where applicable), erasure across all systems including backups/replicas (links to A.8.10), Art.17.2 notification of public-disclosure recipients where the controller has made the data public, and Art.19 notification of routine recipients. ISO does not require this combination as a discrete artifact; Art.17 does.

## What this template gives you

This template helps you create a clear, step-by-step process for handling requests to erase personal data, ensuring you meet GDPR requirements and document your actions for compliance.

## When to use it

Use this whenever you receive a request to erase personal data, or when reviewing your data handling practices. Plan to review and update the procedure about once a year to stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours drafting this document from scratch, as you'll need to cover several required steps and ensure all procedures are clearly described.

## 1. Intake channel published and accessible to data subjects

<<MUST item:Art.17:intake_channel>>
_Why: Art.12.2 — facilitate exercise of rights_

<<GUIDANCE>>

<<TEXT>>

## 2. Identity verification step (proportionate, not over-collecting)

<<MUST item:Art.17:identity_verification>>
_Why: Art.12.6 — verify identity of requester_

<<GUIDANCE>>

<<TEXT>>

## 3. Assessment of which Art.17.1 ground applies (a-f) recorded per request

<<MUST item:Art.17:grounds_assessment>>
_Why: Art.17.1 — six grounds for erasure_

<<GUIDANCE>>

<<TEXT>>

## 4. Assessment of Art.17.3 exceptions with documented refusal grounds where applicable

<<MUST item:Art.17:exception_assessment>>
_Why: Art.17.3 — five exception categories_

<<GUIDANCE>>

<<TEXT>>

## 5. Erasure scope covers backups and replicas (links to A.8.10:scope_systems)

<<MUST item:Art.17:erasure_scope_backups>>
_Why: Art.17.1 — without undue delay across all instances_

<<GUIDANCE>>

<<TEXT>>

## 6. Erasure recorded with what was deleted, when, by whom, verification (links to A.8.10:records)

<<MUST item:Art.17:erasure_record>>
_Why: Art.5.2 accountability_

<<GUIDANCE>>

<<TEXT>>

## 7. Response to data subject within one month (extendable by two months for complex requests)

<<MUST item:Art.17:response_deadline>>
_Why: Art.12.3 — one-month deadline_

<<GUIDANCE>>

<<TEXT>>

## 8. Notification to recipients per Art.19 unless impossible or disproportionate

<<MUST item:Art.17:recipient_notification>>
_Why: Art.19 — onward notification obligation_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Step for Art.17.2 public-disclosure cases — reasonable measures to inform controllers processing the public data

<<SHOULD item:Art.17:public_disclosure_step>>
_Why: Art.17.2 — public-disclosure notification_

<<GUIDANCE>>

<<TEXT>>

### 2. Legal-hold check before erasure (links to A.8.10:legal_hold)

<<SHOULD item:Art.17:legal_hold_check>>
_Why: Art.17.3 — legal obligation / claims exception_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
