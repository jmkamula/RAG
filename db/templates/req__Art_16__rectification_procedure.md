---
leaf_id: req:Art.16:rectification_procedure
control_ref: Art.16
standard_id: GDPR:2016/679
evidence_type: rectification_procedure
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
---

# Rectification procedure (Art.16)

> Art.16 requires the controller to rectify inaccurate personal data without undue delay and to complete incomplete data. The procedure must cover intake, identity verification (Art.12.6), data location across all systems including replicas, the correction step itself, response to the data subject within one month (Art.12.3), and onward notification to recipients per Art.19. ISO does not require this as a discrete artifact; Art.16 does.

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Intake channel published and accessible to data subjects

<<MUST item:Art.16:intake_channel>>
_Why: Art.12.2 — facilitate exercise of rights_

<<TEXT>>

## 2. Identity verification step (proportionate, not over-collecting)

<<MUST item:Art.16:identity_verification>>
_Why: Art.12.6 — verify identity of requester_

<<TEXT>>

## 3. Data location workflow across all systems including replicas (links to Art.30 RoPA)

<<MUST item:Art.16:data_location>>
_Why: Art.16 — rectification across all instances_

<<TEXT>>

## 4. Correction recorded with what was changed, when, by whom

<<MUST item:Art.16:correction_record>>
_Why: Art.5.2 accountability_

<<TEXT>>

## 5. Response to data subject within one month (extendable by two months for complex requests)

<<MUST item:Art.16:response_deadline>>
_Why: Art.12.3 — one-month deadline_

<<TEXT>>

## 6. Notification to recipients per Art.19 unless impossible or disproportionate

<<MUST item:Art.16:recipient_notification>>
_Why: Art.19 — onward notification obligation_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Mechanism for supplementary statement when correction is contested

<<SHOULD item:Art.16:supplementary_statement>>
_Why: Art.16 — completion via supplementary statement_

<<TEXT>>

### 2. Documented grounds for refusing manifestly unfounded or excessive requests

<<SHOULD item:Art.16:refusal_grounds>>
_Why: Art.12.5 — handling unfounded requests_

<<TEXT>>
